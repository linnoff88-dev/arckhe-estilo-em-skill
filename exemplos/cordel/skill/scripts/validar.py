#!/usr/bin/env python3
"""validar.py — confere de verdade o vídeo final antes de dizer "pronto".

Confere:
  1. final/manifesto.json existe e tem status "completo"
  2. todos os arquivos citados no manifesto existem (storyboards, painéis, clipes, narração, trilha, vídeo)
  3. duração do vídeo = duração pedida ± 0,5 s
  4. resolução do vídeo = a pedida
  5. o vídeo tem trilha de vídeo E de áudio
  6. o áudio do vídeo não é silêncio, e a narração sozinha também não (volumedetect)
  7. tem trilha musical registrada
Sai com código 0 se tudo passou; senão código 1 e a lista do que falta.

Uso: python3 validar.py [--pasta .] [--duracao 30] [--resolucao 1080x1920] [--sem-intermediarios]
  --duracao/--resolucao: compara com o PEDIDO (padrão: o que está no manifesto)
  --sem-intermediarios: não exige clipes, painéis nem o vídeo mudo (ex.: repositório que guarda só o final)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import ffprobe_json, normalizar_duracao, parse_resolucao, precisa, volume  # noqa: E402

SILENCIO_MEDIO_DB = -50.0
SILENCIO_PICO_DB = -40.0


def main():
    ap = argparse.ArgumentParser(description="Valida o vídeo final e o manifesto")
    ap.add_argument("--pasta", default=".")
    ap.add_argument("--duracao", type=float)
    ap.add_argument("--resolucao")
    ap.add_argument("--sem-intermediarios", action="store_true")
    a = ap.parse_args()
    precisa("ffprobe")

    pasta = Path(a.pasta)
    falhas, ok = [], []
    mpath = pasta / "final" / "manifesto.json"
    if not mpath.exists():
        print(f"FALHOU: não existe {mpath}")
        sys.exit(1)
    m = json.loads(mpath.read_text(encoding="utf-8"))

    if m.get("status") == "completo":
        ok.append("manifesto com status completo")
    else:
        falhas.append(f"manifesto com status '{m.get('status')}' (faltando: {', '.join(m.get('faltando', [])) or '?'})")

    arquivos = [("vídeo", m.get("video")), ("narração", m.get("narracao"))]
    arquivos += [("storyboard", s) for s in m.get("storyboards", [])]
    if not a.sem_intermediarios:
        arquivos += [("painel", p) for p in m.get("paineis", [])] + [("clipe", c) for c in m.get("clipes", [])]
        arquivos.append(("vídeo mudo", m.get("video_mudo")))
    if m.get("trilha"):
        arquivos.append(("trilha", m["trilha"]))
    else:
        falhas.append("sem trilha musical no manifesto (coloque uma em assets/trilha/ e rode o montar.py)")
    faltam = [f"{tipo}: {c}" for tipo, c in arquivos if not c or not (pasta / c).exists()]
    if faltam:
        falhas.append("arquivos do manifesto que não existem: " + "; ".join(faltam[:8]) +
                      (f" (+{len(faltam) - 8})" if len(faltam) > 8 else ""))
    else:
        ok.append(f"{len(arquivos)} arquivos do manifesto existem")

    video = pasta / (m.get("video") or "final/video-final.mp4")
    if not video.exists():
        falhas.append(f"vídeo final não existe: {video}")
    else:
        info = ffprobe_json(video)
        vs = [s for s in info["streams"] if s.get("codec_type") == "video"]
        aus = [s for s in info["streams"] if s.get("codec_type") == "audio"]
        dur = float(info["format"].get("duration", 0))
        pedida = normalizar_duracao(a.duracao) if a.duracao else float(m.get("duracao_s", 0))
        if abs(dur - pedida) <= 0.5:
            ok.append(f"duração {dur:.2f} s (pedido {pedida:g} s ± 0,5)")
        else:
            falhas.append(f"duração {dur:.2f} s fora do pedido {pedida:g} s ± 0,5")
        if not vs:
            falhas.append("o arquivo não tem trilha de vídeo")
        else:
            w, h = int(vs[0]["width"]), int(vs[0]["height"])
            alvo = parse_resolucao(a.resolucao or m.get("resolucao", f"{w}x{h}"))
            if (w, h) == alvo:
                ok.append(f"resolução {w}x{h}")
            else:
                falhas.append(f"resolução {w}x{h}, pedido {alvo[0]}x{alvo[1]}")
        if not aus:
            falhas.append("o vídeo não tem áudio")
        else:
            vol = volume(video)
            if vol["mean"] > SILENCIO_MEDIO_DB and vol["max"] > SILENCIO_PICO_DB:
                ok.append(f"áudio do vídeo com som (média {vol['mean']} dB, pico {vol['max']} dB)")
            else:
                falhas.append(f"áudio do vídeo é silêncio (média {vol['mean']} dB, pico {vol['max']} dB)")
    narr = pasta / (m.get("narracao") or "")
    if m.get("narracao") and narr.exists():
        vn = volume(narr)
        if vn["mean"] > SILENCIO_MEDIO_DB and vn["max"] > SILENCIO_PICO_DB:
            ok.append(f"narração com voz (média {vn['mean']} dB)")
        else:
            falhas.append(f"narração muda (média {vn['mean']} dB, pico {vn['max']} dB) — a trilha pode estar escondendo isso")

    for linha in ok:
        print(f"  ok   {linha}")
    for linha in falhas:
        print(f"  FALTA {linha}")
    if falhas:
        print(f"FALHOU: {len(falhas)} problema(s). Não diga 'pronto' ainda.")
        sys.exit(1)
    print("PASSOU: vídeo conferido, pode dizer pronto.")


if __name__ == "__main__":
    main()
