#!/usr/bin/env python3
"""folha.py — folha de contato do vídeo final: um quadro do meio de cada cena, numerado.

Uso: python3 folha.py [--pasta .] [--video final/video-final.mp4] [--saida final/folha-final.jpg] [--largura 270]
"""
from __future__ import annotations

import argparse
import io
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import erro, ler_json, precisa  # noqa: E402

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover
    erro("Pillow não está instalado. Rode: python3 -m pip install --user Pillow")


def main():
    ap = argparse.ArgumentParser(description="Folha de contato do vídeo final (um quadro por cena)")
    ap.add_argument("--pasta", default=".")
    ap.add_argument("--video", default="final/video-final.mp4")
    ap.add_argument("--saida", default="final/folha-final.jpg")
    ap.add_argument("--largura", type=int, default=270)
    a = ap.parse_args()
    precisa("ffmpeg")
    pasta = Path(a.pasta)
    plano = ler_json(pasta / "saida" / "plano.json")
    video = pasta / a.video
    if not video.exists():
        erro(f"vídeo não encontrado: {video}")
    quadros = []
    for c in plano["cenas"]:
        t = (c["inicio_s"] + c["fim_s"]) / 2
        r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", f"{t:.3f}", "-i", str(video),
                            "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True, timeout=120)
        if r.returncode != 0 or not r.stdout:
            erro(f"não consegui tirar o quadro de {t:.2f} s")
        quadros.append((c["numero"], t, Image.open(io.BytesIO(r.stdout)).convert("RGB")))
    w = a.largura
    h = round(quadros[0][2].height * w / quadros[0][2].width)
    cols = 6 if len(quadros) > 8 else max(1, min(len(quadros), 4))
    linhas = (len(quadros) + cols - 1) // cols
    m, rot = 8, 26
    folha = Image.new("RGB", (cols * (w + m) + m, linhas * (h + rot + m) + m), (20, 20, 20))
    d = ImageDraw.Draw(folha)
    try:
        fonte = ImageFont.truetype("DejaVuSans-Bold.ttf", 16)
    except OSError:
        fonte = ImageFont.load_default()
    for i, (n, t, im) in enumerate(quadros):
        x, y = m + (i % cols) * (w + m), m + (i // cols) * (h + rot + m)
        d.text((x, y + 4), f"cena {n} · {t:.1f} s", fill=(240, 240, 240), font=fonte)
        folha.paste(im.resize((w, h), Image.LANCZOS), (x, y + rot))
    destino = pasta / a.saida
    destino.parent.mkdir(parents=True, exist_ok=True)
    folha.save(destino, quality=88)
    print(f"folha: {destino} ({len(quadros)} cenas) — abra e confira texto e estilo")


if __name__ == "__main__":
    main()
