#!/usr/bin/env python3
"""montar.py — junta vídeo + narração + UMA trilha contínua e escreve o vídeo final e o manifesto.

Trilha: procura em <pasta>/assets/trilha/ (e depois em assets/trilha/ da skill).
  - nenhuma trilha → para (código 3) e pede uma: coloque um .mp3/.wav lá ou use --trilha arquivo
  - mais de uma   → para (código 4) e lista: escolha com --trilha
A trilha toca do começo ao fim sem reiniciar (loop se for curta, corte se for longa), volume 0,5 por
padrão, ABAIXA sob a voz (sidechain/ducking), entra com fade de 0,5 s e sai com fade de 2 s.

Saída: final/video-final.mp4 + final/manifesto.json
Uso:  python3 montar.py [--pasta .] [--trilha arquivo] [--volume 0.5] [--sem-trilha]
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import duracao, erro, gravar_json, ler_json, precisa, relativo, rodar  # noqa: E402

AUDIO = (".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac")
SKILL_DIR = Path(__file__).resolve().parent.parent


def achar_trilha(pasta: Path, pedida: str | None) -> Path:
    if pedida:
        p = Path(pedida)
        if not p.exists():
            p = pasta / "assets" / "trilha" / pedida
        if not p.exists():
            erro(f"trilha não encontrada: {pedida}", 3)
        return p
    for d in (pasta / "assets" / "trilha", SKILL_DIR / "assets" / "trilha"):
        achadas = sorted(x for x in d.glob("*") if x.suffix.lower() in AUDIO) if d.is_dir() else []
        if len(achadas) == 1:
            return achadas[0]
        if len(achadas) > 1:
            lista = "\n".join(f"  --trilha {x}" for x in achadas)
            erro(f"há {len(achadas)} trilhas em {d}; escolha uma:\n{lista}", 4)
    erro("nenhuma trilha encontrada. Coloque UM arquivo .mp3/.wav em assets/trilha/ (música sua ou com "
         "licença de uso) ou passe --trilha arquivo. Pergunte ao usuário qual trilha usar.", 3)


def main():
    ap = argparse.ArgumentParser(description="Monta o vídeo final com narração e trilha única")
    ap.add_argument("--pasta", default=".")
    ap.add_argument("--plano", default="saida/plano.json")
    ap.add_argument("--trilha")
    ap.add_argument("--volume", type=float, default=0.5, help="volume da trilha (0–1), antes do ducking")
    ap.add_argument("--sem-trilha", action="store_true", help="monta só com a voz (o manifesto fica incompleto)")
    ap.add_argument("--crf", type=int, default=21)
    a = ap.parse_args()

    precisa("ffmpeg")
    pasta = Path(a.pasta)
    plano = ler_json(pasta / a.plano)
    T = float(plano["duracao_s"])
    video = pasta / "saida" / "video-mudo.mp4"
    voz = pasta / "saida" / "voz" / "narracao.wav"
    for f in (video, voz):
        if not f.exists():
            erro(f"falta {f} (rode animar.py e narrar.py antes)")
    trilha = None if a.sem_trilha else achar_trilha(pasta, a.trilha)
    if not 0 < a.volume <= 1:
        erro("--volume precisa estar entre 0 e 1")

    final = pasta / "final"
    final.mkdir(parents=True, exist_ok=True)
    saida = final / "video-final.mp4"
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(video), "-i", str(voz)]
    if trilha:
        cmd += ["-stream_loop", "-1", "-i", str(trilha)]
        fade = max(0.5, min(2.0, T / 6))
        grafo = (
            f"[2:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:{T},asetpts=PTS-STARTPTS,"
            f"volume={a.volume},afade=t=in:d=0.5,afade=t=out:st={T - fade:.3f}:d={fade:.3f}[musica];"
            "[1:a]aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[voz][chave];"
            "[musica][chave]sidechaincompress=threshold=0.015:ratio=8:attack=20:release=400[abaixada];"
            "[voz][abaixada]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[a]"
        )
    else:
        grafo = "[1:a]aformat=sample_rates=48000:channel_layouts=stereo[a]"
    cmd += ["-filter_complex", grafo, "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-preset", "medium",
            "-crf", str(a.crf), "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-t", f"{T}",
            "-movflags", "+faststart", str(saida)]
    rodar(cmd, 3600)

    def rel(p):
        return relativo(p, pasta)

    paineis = [rel(pasta / "saida" / "paineis" / f"cena-{c['numero']:02d}.png") for c in plano["cenas"]]
    clipes = [rel(pasta / "saida" / "clipes" / f"cena-{c['numero']:02d}.mp4") for c in plano["cenas"]]
    faltando = [] if trilha else ["trilha"]
    manifesto = {
        "tema": plano.get("tema", ""),
        "duracao_s": T,
        "duracao_pedida_s": plano.get("duracao_pedida_s", T),
        "duracao_real_s": round(duracao(saida), 3),
        "formato": plano["formato"],
        "resolucao": plano["resolucao"],
        "fps": plano.get("fps", 30),
        "motor": plano.get("motor", "local"),
        "n_cenas": plano["n_cenas"],
        "n_storyboards": plano["n_storyboards"],
        "storyboards": [s["arquivo"] for s in plano["storyboards"]],
        "paineis": paineis,
        "clipes": clipes,
        "video_mudo": rel(video),
        "narracao": rel(voz),
        "trilha": rel(trilha) if trilha else None,
        "trilha_volume": a.volume if trilha else None,
        "trilha_ducking": bool(trilha),
        "video": rel(saida),
        "status": "completo" if not faltando else "incompleto",
        "faltando": faltando,
        "gerado_em": datetime.now().isoformat(timespec="seconds"),
    }
    gravar_json(final / "manifesto.json", manifesto)
    print(f"vídeo: {saida} ({manifesto['duracao_real_s']} s) | trilha: {manifesto['trilha']} | "
          f"status: {manifesto['status']}")
    print("agora rode: python3 validar.py --pasta", a.pasta)


if __name__ == "__main__":
    main()
