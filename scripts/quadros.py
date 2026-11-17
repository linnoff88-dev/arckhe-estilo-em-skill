#!/usr/bin/env python3
"""quadros.py — escolhe sozinho de 5 a 8 quadros DIFERENTES de um vídeo de referência e faz a folha.

Como escolhe:
  1. procura trocas de cena com o ffmpeg (select='gt(scene,LIMIAR)'), mais o primeiro trecho do vídeo
     (a detecção nunca marca a abertura);
  2. descarta quadros parecidos: mesmo desenho (hash de diferença 9×8 com distância de Hamming pequena)
     E mesmas cores (miniatura 8×8 colorida quase igual). Mesmo layout com outra paleta conta como diferente;
  3. se sobrar menos que o mínimo (vídeo com poucas trocas), completa com quadros espaçados no tempo,
     afrouxando o filtro de parecidos só o necessário;
  4. se sobrar mais que --n, fica com os mais espalhados no tempo.
Saída: quadro-01.jpg ... + folha.jpg (contact sheet com o tempo de cada quadro) + quadros.json

Uso: python3 scripts/quadros.py video.mp4 [--n 8] [--min 5] [--saida estilo/quadros/] [--limiar 0.3]
Precisa: Python 3, ffmpeg/ffprobe e Pillow (python3 -m pip install --user Pillow).
"""
from __future__ import annotations

import argparse
import io
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("ERRO: Pillow não está instalado. Rode: python3 -m pip install --user Pillow", file=sys.stderr)
    sys.exit(2)


def erro(msg):
    print(f"ERRO: {msg}", file=sys.stderr)
    sys.exit(1)


def duracao(video: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
                       capture_output=True, text=True, timeout=120)
    try:
        return float(r.stdout.strip())
    except ValueError:
        erro(f"não consegui ler a duração de {video}")


def trocas_de_cena(video: Path, limiar: float) -> list[float]:
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(video), "-vf",
                        f"select='gt(scene,{limiar})',showinfo", "-an", "-f", "null", "-"],
                       capture_output=True, text=True, timeout=1800)
    return [float(x) for x in re.findall(r"pts_time:([\d.]+)", r.stderr)]


def pegar_quadro(video: Path, t: float) -> Image.Image | None:
    r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", f"{t:.3f}", "-i", str(video),
                        "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"],
                       capture_output=True, timeout=120)
    if r.returncode != 0 or not r.stdout:
        return None
    return Image.open(io.BytesIO(r.stdout)).convert("RGB")


def dhash(img: Image.Image) -> int:
    p = img.convert("L").resize((9, 8), Image.LANCZOS)
    px = list(p.getdata())
    bits = 0
    for y in range(8):
        for x in range(8):
            bits = (bits << 1) | (1 if px[y * 9 + x] > px[y * 9 + x + 1] else 0)
    return bits


def cores(img: Image.Image) -> list[int]:
    return list(img.convert("RGB").resize((8, 8), Image.BOX).tobytes())


def dif_cor(a: list[int], b: list[int]) -> float:
    return sum(abs(x - y) for x, y in zip(a, b)) / len(a)


def hamming(a: int, b: int) -> int:
    return bin(a ^ b).count("1")


def espalhar(itens: list, n: int) -> list:
    if len(itens) <= n:
        return itens
    passo = (len(itens) - 1) / (n - 1)
    return [itens[round(i * passo)] for i in range(n)]


def folha(quadros: list[dict], destino: Path):
    larg = 360
    imgs = [Image.open(q["arquivo"]) for q in quadros]
    alturas = [round(im.height * larg / im.width) for im in imgs]
    alt = max(alturas)
    cols = 4 if len(imgs) > 6 else 3
    linhas = (len(imgs) + cols - 1) // cols
    m, rotulo = 12, 30
    s = Image.new("RGB", (cols * (larg + m) + m, linhas * (alt + rotulo + m) + m), (24, 24, 24))
    d = ImageDraw.Draw(s)
    try:
        fonte = ImageFont.truetype("DejaVuSans-Bold.ttf", 18)
    except OSError:
        fonte = ImageFont.load_default()
    for i, (im, q) in enumerate(zip(imgs, quadros)):
        x = m + (i % cols) * (larg + m)
        y = m + (i // cols) * (alt + rotulo + m)
        s.paste(im.resize((larg, alturas[i])), (x, y + rotulo))
        d.text((x, y + 4), f"{i + 1}  ·  {q['tempo_s']:.1f} s  ·  {q['origem']}", fill=(240, 240, 240), font=fonte)
    s.save(destino, quality=88)


def main():
    ap = argparse.ArgumentParser(description="Escolhe quadros diferentes de um vídeo e monta a folha")
    ap.add_argument("video")
    ap.add_argument("--n", type=int, default=8, help="máximo de quadros (padrão 8)")
    ap.add_argument("--min", type=int, default=5, help="mínimo de quadros (padrão 5)")
    ap.add_argument("--saida", default="estilo/quadros")
    ap.add_argument("--limiar", type=float, default=0.3, help="sensibilidade da troca de cena (0–1)")
    ap.add_argument("--parecido", type=int, default=12, help="distância de hash abaixo da qual é 'parecido'")
    a = ap.parse_args()

    for prog in ("ffmpeg", "ffprobe"):
        if shutil.which(prog) is None:
            erro(f"'{prog}' não encontrado. Instale o ffmpeg.")
    video = Path(a.video)
    if not video.exists():
        erro(f"vídeo não encontrado: {video}")
    a.min = max(1, min(a.min, a.n))
    dur = duracao(video)
    saida = Path(a.saida)
    saida.mkdir(parents=True, exist_ok=True)
    for velho in saida.glob("quadro-*.jpg"):
        velho.unlink()

    # candidatos: abertura + logo depois de cada troca (0,25 s depois, para fugir do quadro de transição)
    trocas = trocas_de_cena(video, a.limiar)
    cand = [(min(0.3, dur / 4), "abertura")] + [(min(t + 0.25, max(0.0, dur - 0.05)), "troca") for t in trocas]
    escolhidos: list[dict] = []

    def tentar(t, origem, limite):
        img = pegar_quadro(video, t)
        if img is None:
            return
        h = dhash(img)
        cor = cores(img)
        if all(hamming(h, e["hash"]) >= limite or dif_cor(cor, e["cor"]) >= limite * 2 for e in escolhidos):
            escolhidos.append({"tempo_s": round(t, 2), "origem": origem, "hash": h, "cor": cor, "img": img})

    for t, origem in cand:
        tentar(t, origem, a.parecido)
    print(f"trocas de cena achadas: {len(trocas)} → {len(escolhidos)} quadros diferentes")

    if len(escolhidos) < a.n:
        # completa com quadros espaçados que sejam realmente diferentes (filtro normal)
        antes = len(escolhidos)
        k = a.n * 3
        for i in range(k):
            if len(escolhidos) >= a.n:
                break
            tentar(dur * (i + 0.5) / k, "espacado", a.parecido)
        if len(escolhidos) > antes:
            print(f"quadros espaçados diferentes acrescentados: {len(escolhidos) - antes}")

    if len(escolhidos) < a.min:
        print(f"poucas trocas: completando com quadros espaçados (mínimo {a.min})")
        limite = a.parecido // 2
        while len(escolhidos) < a.min and limite >= 1:
            k = a.n * 3
            for i in range(k):
                if len(escolhidos) >= a.n:
                    break
                tentar(dur * (i + 0.5) / k, "espacado", limite)
            if len(escolhidos) < a.min:
                limite //= 2
                if limite >= 1:
                    print(f"  afrouxando o filtro de parecidos para {limite}")
        if len(escolhidos) < a.min:
            print(f"AVISO: só consegui {len(escolhidos)} quadros diferentes; o vídeo é quase estático", file=sys.stderr)

    escolhidos.sort(key=lambda e: e["tempo_s"])
    escolhidos = espalhar(escolhidos, a.n)
    lista = []
    for i, e in enumerate(escolhidos, start=1):
        arq = saida / f"quadro-{i:02d}.jpg"
        e["img"].save(arq, quality=92)
        lista.append({"arquivo": str(arq), "tempo_s": e["tempo_s"], "origem": e["origem"], "hash": f"{e['hash']:016x}"})
    folha(lista, saida / "folha.jpg")
    (saida / "quadros.json").write_text(json.dumps({"video": str(video), "duracao_s": round(dur, 2),
                                                    "trocas_de_cena": len(trocas), "quadros": lista},
                                                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(lista)} quadros em {saida}/ + folha.jpg")


if __name__ == "__main__":
    main()
