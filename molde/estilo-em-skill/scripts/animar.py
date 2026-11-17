#!/usr/bin/env python3
"""animar.py — transforma os painéis em vídeo.

MOTOR LOCAL (padrão, grátis, testado): sem IA de vídeo. Cada painel vira um clipe de 2,5 s com
movimento de câmera lento (zoom in/out ou pan, zoom máx. 1,25×), e as cenas se ligam por dissolve.
O resultado tem a duração exata do plano (dissolve não encurta o vídeo: cada cena "sobra" metade do
dissolve para os dois lados). Quadro a quadro com Pillow, codificado pelo ffmpeg, 30 fps, determinístico.

Saídas: saida/clipes/cena-NN.mp4 (2,5 s cada, sem transição) e saida/video-mudo.mp4 (tudo junto).

MOTORES OPCIONAIS — NÃO TESTADOS NESTE KIT (só geram texto para você usar na sua conta):
  --motor kling --so-prompts     → saida/prompts-kling.sh   (comandos da CLI oficial `kling`)
  --motor seedance --so-prompts  → saida/prompts-seedance.md (um prompt por storyboard para colar no site)

Uso:
  python3 animar.py [--pasta .] [--dissolve 0.5] [--zoom-max 1.18] [--crf 20]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import CENA_S, aviso, erro, ler_json, parse_resolucao, precisa  # noqa: E402

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    erro("Pillow não está instalado. Rode: python3 -m pip install --user Pillow")

ZOOM_TETO = 1.25
CAMERAS = {"zoom_in", "zoom_out", "pan_direita", "pan_esquerda", "pan_cima", "pan_baixo", "parado"}


def janela(camera: str, p: float, zmax: float):
    """Devolve (zoom, cx, cy) normalizados (0..1) para o progresso p∈[0,1] da cena."""
    p = min(1.0, max(0.0, p))
    zpan = min(zmax, 1.12)
    if camera == "zoom_in":
        return 1.0 + (zmax - 1.0) * p, 0.5, 0.5
    if camera == "zoom_out":
        return zmax - (zmax - 1.0) * p, 0.5, 0.5
    if camera == "parado":
        return 1.04, 0.5, 0.5
    folga = (1 - 1 / zpan) / 2          # quanto o centro pode andar sem sair da imagem
    ida = -folga + 2 * folga * p
    if camera == "pan_direita":
        return zpan, 0.5 + ida, 0.5
    if camera == "pan_esquerda":
        return zpan, 0.5 - ida, 0.5
    if camera == "pan_baixo":
        return zpan, 0.5, 0.5 + ida
    if camera == "pan_cima":
        return zpan, 0.5, 0.5 - ida
    return 1.0 + (zmax - 1.0) * p, 0.5, 0.5


def quadro(base: Image.Image, camera: str, p: float, zmax: float) -> Image.Image:
    w, h = base.size
    z, cx, cy = janela(camera, p, zmax)
    x0 = cx * w - w / (2 * z)
    y0 = cy * h - h / (2 * z)
    # afim com amostragem sub-pixel: movimento liso, sem "degrau" de pixel
    return base.transform((w, h), Image.AFFINE, (1 / z, 0, x0, 0, 1 / z, y0), resample=Image.BICUBIC)


def abrir_ffmpeg(destino: Path, w: int, h: int, fps: int, crf: int) -> subprocess.Popen:
    destino.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{w}x{h}", "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", "medium",
           "-crf", str(crf), "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(destino)]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE)


def fechar(proc: subprocess.Popen, nome: str):
    proc.stdin.close()
    if proc.wait(timeout=600) != 0:
        erro(f"ffmpeg falhou ao gravar {nome}")


def animar_local(pasta: Path, plano: dict, dissolve: float, zmax: float, crf: int, fade_final: float):
    precisa("ffmpeg")
    w, h = parse_resolucao(plano["resolucao"])
    fps = int(plano.get("fps", 30))
    cenas = plano["cenas"]
    n = len(cenas)
    total = n * CENA_S
    bases = []
    for c in cenas:
        arq = pasta / "saida" / "paineis" / f"cena-{c['numero']:02d}.png"
        if not arq.exists():
            erro(f"painel não encontrado: {arq} (rode o recortar.py antes)")
        img = Image.open(arq).convert("RGB")
        if img.size != (w, h):
            aviso(f"{arq.name} tem {img.size[0]}x{img.size[1]}; ajustando para {w}x{h}")
            img = img.resize((w, h), Image.LANCZOS)
        cam = c.get("camera", "zoom_in")
        if cam not in CAMERAS:
            aviso(f"câmera '{cam}' desconhecida na cena {c['numero']}; usando zoom_in")
            cam = "zoom_in"
        bases.append((img, cam))

    meio = dissolve / 2
    dur_mov = CENA_S + dissolve           # cada cena se move também durante as duas metades de dissolve

    def puro(k: int, t_local: float) -> Image.Image:
        img, cam = bases[k]
        return quadro(img, cam, (t_local + meio) / dur_mov, zmax)

    n_quadros = round(total * fps)
    q_cena = round(CENA_S * fps)
    principal = abrir_ffmpeg(pasta / "saida" / "video-mudo.mp4", w, h, fps, crf)
    clipe, clipe_k = None, -1
    for f in range(n_quadros):
        t = f / fps
        k = min(n - 1, f // q_cena)
        tl = t - k * CENA_S
        atual = puro(k, tl)
        if k != clipe_k:
            if clipe:
                fechar(clipe, f"cena {clipe_k + 1}")
            clipe = abrir_ffmpeg(pasta / "saida" / "clipes" / f"cena-{k + 1:02d}.mp4", w, h, fps, crf)
            clipe_k = k
        clipe.stdin.write(atual.tobytes())
        saida = atual
        if dissolve > 0:
            if tl < meio and k > 0:                       # começo da cena: ainda misturando com a anterior
                a = 0.5 + tl / dissolve
                saida = Image.blend(puro(k - 1, tl + CENA_S), atual, a)
            elif tl > CENA_S - meio and k < n - 1:        # fim da cena: já misturando com a próxima
                a = 0.5 - (CENA_S - tl) / dissolve
                saida = Image.blend(atual, puro(k + 1, tl - CENA_S), a)
        if fade_final > 0 and t > total - fade_final:
            escuro = Image.new("RGB", (w, h), (0, 0, 0))
            saida = Image.blend(saida, escuro, min(1.0, (t - (total - fade_final)) / fade_final))
        principal.stdin.write(saida.tobytes())
        if f % (fps * 5) == 0:
            print(f"  animando: {t:5.1f}/{total:.1f} s", flush=True)
    fechar(clipe, f"cena {clipe_k + 1}")
    fechar(principal, "video-mudo.mp4")
    print(f"pronto: {n} clipes em saida/clipes/ e saida/video-mudo.mp4 ({total:g} s, {w}x{h}, {fps} fps)")


def prompts_kling(pasta: Path, plano: dict):
    """NÃO TESTADO: só escreve os comandos. Nada é enviado."""
    linhas = ["#!/usr/bin/env bash",
              "# NÃO TESTADO NESTE KIT. Gasta créditos da SUA conta Kling. Confira cada prompt antes de rodar.",
              "# O Kling gera no mínimo 3 s: depois corte cada clipe para 2,5 s, ex.:",
              "#   ffmpeg -i in.mp4 -t 2.5 -c:v libx264 -an saida/clipes/cena-01.mp4",
              "set -e", ""]
    for c in plano["cenas"]:
        prompt = (f"Anime esta ilustração mantendo o estilo exato (sem mudar traço, cores ou texto). "
                  f"Ação: {c['acao']}. Câmera: {c['camera'].replace('_', ' ')}, lenta e suave. "
                  f"O texto '{c['texto_tela']}' fica parado e legível. Sem música, sem fala, sem texto novo.")
        prompt = prompt.replace('"', "'")
        linhas.append(f"# cena {c['numero']} ({c['inicio_s']}–{c['fim_s']} s)")
        linhas.append(f'kling image_to_video --model kling-video-v3_0_turbo '
                      f'--image saida/paineis/cena-{c["numero"]:02d}.png "{prompt}" --poll 300')
        linhas.append("")
    destino = pasta / "saida" / "prompts-kling.sh"
    destino.write_text("\n".join(linhas), encoding="utf-8")
    print(f"comandos gravados em {destino} (NÃO TESTADO; nada foi enviado)")


def prompts_seedance(pasta: Path, plano: dict):
    """NÃO TESTADO: um prompt por storyboard para colar no site do motor."""
    partes = ["# Prompts de vídeo por storyboard (Seedance / Higgsfield)", "",
              "> NÃO TESTADO NESTE KIT. Cole cada bloco no site junto com a imagem do storyboard.", ""]
    for s in plano["storyboards"]:
        cenas = [c for c in plano["cenas"] if c["storyboard"] == s["numero"]]
        dur = len(cenas) * CENA_S
        partes += [f"## Storyboard {s['numero']} — {s['arquivo']} ({dur:g} s, {plano['formato']})", "",
                   "```",
                   f"Vídeo {plano['formato']} de {dur:g} segundos feito a partir desta imagem de storyboard "
                   f"({s['linhas']}×{s['colunas']} painéis, leitura da esquerda para a direita, de cima para baixo). "
                   "Cada painel é uma cena de 2,5 s. Mantenha EXATAMENTE o estilo, as cores e as letras dos painéis.",
                   ""]
        for c in cenas:
            t0 = c["inicio_s"] - cenas[0]["inicio_s"]
            partes.append(f"{t0:.1f}–{t0 + CENA_S:.1f} s | painel {c['painel']} | câmera: {c['camera'].replace('_', ' ')} "
                          f"| ação: {c['acao']} | texto na tela: \"{c['texto_tela']}\" entra com leve escala, "
                          f"fica legível | entrada: {c['transicao_entrada']} | fala: \"{c['fala']}\"")
        partes += ["", "Transições suaves (dissolve). Sem música e sem efeitos sonoros (a trilha entra depois). "
                   "Não invente texto novo.", "```", ""]
    destino = pasta / "saida" / "prompts-seedance.md"
    destino.write_text("\n".join(partes), encoding="utf-8")
    print(f"prompts gravados em {destino} (NÃO TESTADO; nada foi enviado)")


def main():
    ap = argparse.ArgumentParser(description="Anima os painéis (motor local) ou gera prompts de motores externos")
    ap.add_argument("--pasta", default=".")
    ap.add_argument("--plano", default="saida/plano.json")
    ap.add_argument("--motor", choices=["local", "kling", "seedance"], help="padrão: o do plano")
    ap.add_argument("--so-prompts", action="store_true", help="kling/seedance: só escreve os prompts")
    ap.add_argument("--dissolve", type=float, default=0.5, help="segundos de dissolve entre cenas (0 = corte)")
    ap.add_argument("--zoom-max", type=float, default=1.18)
    ap.add_argument("--fade-final", type=float, default=0.4)
    ap.add_argument("--crf", type=int, default=20)
    a = ap.parse_args()

    pasta = Path(a.pasta)
    plano = ler_json(pasta / a.plano)
    motor = a.motor or plano.get("motor", "local")
    if a.zoom_max > ZOOM_TETO:
        aviso(f"zoom {a.zoom_max} passa do teto {ZOOM_TETO}; usando {ZOOM_TETO}")
        a.zoom_max = ZOOM_TETO
    if not 0 <= a.dissolve <= 1.2:
        erro("dissolve precisa estar entre 0 e 1,2 s")
    if motor == "local":
        animar_local(pasta, plano, a.dissolve, max(1.0, a.zoom_max), a.crf, a.fade_final)
    elif not a.so_prompts:
        erro(f"o motor '{motor}' não é testado neste kit; use --so-prompts para gerar os prompts e rodar na sua conta")
    elif motor == "kling":
        prompts_kling(pasta, plano)
    else:
        prompts_seedance(pasta, plano)


if __name__ == "__main__":
    main()
