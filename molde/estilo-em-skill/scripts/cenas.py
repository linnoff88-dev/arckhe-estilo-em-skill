#!/usr/bin/env python3
"""cenas.py — calcula cenas e storyboards e grava saida/plano.json.

Regra: cada cena dura 2,5 s; cada storyboard tem até 6 cenas.
  10 s = 4 cenas / 1 storyboard     15 s = 6 / 1     20 s = 8 / 2
  30 s = 12 / 2                     45 s = 18 / 3
Duração que não é múltiplo de 2,5 vai para o múltiplo mais próximo (17 → 17,5) com aviso.

Uso:
  python3 cenas.py --tema "..." --duracao 30 --formato 9:16 [--resolucao 1080x1920]
                   [--motor local|kling|seedance] [--roteiro roteiro.json] [--pasta .]
  python3 cenas.py --so-calcular --duracao 17        (só imprime a conta, não grava nada)

roteiro.json (opcional, escrito pela IA): {"cenas": [{"texto_tela": "...", "fala": "...",
  "acao": "...", "camera": "zoom_in", "transicao_entrada": "dissolve"}, ...]}
Campos que faltarem ficam com o padrão ("PREENCHER" nos textos).
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import (CENA_S, FORMATOS, GRADES_PARCIAIS, aviso, dividir_storyboards, erro,  # noqa: E402
                   gravar_json, ler_json, normalizar_duracao, parse_resolucao)

CAMERAS = ["zoom_in", "pan_direita", "zoom_out", "pan_esquerda", "pan_cima", "zoom_in", "pan_baixo", "zoom_out"]
MOTORES = ["local", "kling", "seedance"]


def calcular(duracao_pedida: float) -> dict:
    dur = normalizar_duracao(duracao_pedida)
    n = int(round(dur / CENA_S))
    sbs = dividir_storyboards(n)
    return {"duracao_pedida_s": duracao_pedida, "duracao_s": dur, "n_cenas": n,
            "n_storyboards": len(sbs), "cenas_por_storyboard": sbs,
            "normalizada": abs(dur - duracao_pedida) > 1e-9}


def montar_plano(tema, duracao_pedida, formato, resolucao, motor, roteiro=None) -> dict:
    conta = calcular(duracao_pedida)
    w, h = resolucao
    cenas_rot = (roteiro or {}).get("cenas", [])
    if cenas_rot and len(cenas_rot) != conta["n_cenas"]:
        erro(f"o roteiro tem {len(cenas_rot)} cenas, mas {conta['duracao_s']:g} s pedem {conta['n_cenas']} cenas")

    storyboards, cenas = [], []
    idx = 0
    for s, k in enumerate(conta["cenas_por_storyboard"], start=1):
        linhas, colunas = GRADES_PARCIAIS[formato][k]
        storyboards.append({"numero": s, "arquivo": f"saida/storyboards/storyboard-{s}.png",
                            "cenas": list(range(idx + 1, idx + k + 1)), "linhas": linhas, "colunas": colunas,
                            "paineis": k, "continua_de": s - 1 if s > 1 else None})
        for p in range(k):
            r = cenas_rot[idx] if idx < len(cenas_rot) else {}
            n = idx + 1
            cenas.append({
                "numero": n,
                "inicio_s": round(idx * CENA_S, 3),
                "fim_s": round(n * CENA_S, 3),
                "storyboard": s,
                "painel": p + 1,
                "texto_tela": r.get("texto_tela", "PREENCHER"),
                "acao": r.get("acao", "PREENCHER"),
                "camera": r.get("camera", CAMERAS[idx % len(CAMERAS)]),
                "transicao_entrada": r.get("transicao_entrada", "corte" if n == 1 else "dissolve"),
                "transicao_saida": r.get("transicao_saida", "fade_final" if n == conta["n_cenas"] else "dissolve"),
                "fala": r.get("fala", "PREENCHER"),
            })
            idx += 1

    return {
        "versao": 1,
        "tema": tema,
        "formato": formato,
        "resolucao": f"{w}x{h}",
        "fps": 30,
        "motor": motor,
        "cena_s": CENA_S,
        **conta,
        "storyboards": storyboards,
        "cenas": cenas,
        "criado_em": datetime.now().isoformat(timespec="seconds"),
    }


def main():
    ap = argparse.ArgumentParser(description="Calcula cenas/storyboards e grava saida/plano.json")
    ap.add_argument("--tema", default="")
    ap.add_argument("--duracao", type=float, required=True, help="segundos")
    ap.add_argument("--formato", choices=list(FORMATOS), default="9:16")
    ap.add_argument("--resolucao", help="LARGURAxALTURA (padrão do formato)")
    ap.add_argument("--motor", choices=MOTORES, default="local")
    ap.add_argument("--roteiro", help="roteiro.json com os textos de cada cena")
    ap.add_argument("--pasta", default=".", help="pasta do projeto de vídeo")
    ap.add_argument("--so-calcular", action="store_true", help="só imprime a conta")
    a = ap.parse_args()

    if a.duracao <= 0:
        erro("a duração precisa ser maior que zero")
    conta = calcular(a.duracao)
    if conta["normalizada"]:
        aviso(f"{a.duracao:g} s não é múltiplo de 2,5 s; usando {conta['duracao_s']:g} s "
              f"({conta['n_cenas']} cenas de 2,5 s)")
    resumo = (f"{conta['duracao_s']:g} s = {conta['n_cenas']} cenas / {conta['n_storyboards']} storyboard(s) "
              f"{conta['cenas_por_storyboard']}")
    if a.so_calcular:
        print(resumo)
        return

    resolucao = parse_resolucao(a.resolucao) if a.resolucao else FORMATOS[a.formato]["resolucao"]
    w, h = resolucao
    alvo = {"9:16": 9 / 16, "16:9": 16 / 9, "1:1": 1.0}[a.formato]
    if abs(w / h - alvo) > 0.02:
        aviso(f"resolução {w}x{h} não bate com o formato {a.formato}")
    roteiro = ler_json(a.roteiro) if a.roteiro else None
    plano = montar_plano(a.tema, a.duracao, a.formato, resolucao, a.motor, roteiro)
    destino = Path(a.pasta) / "saida" / "plano.json"
    gravar_json(destino, plano)
    faltam = sum(1 for c in plano["cenas"] for k in ("texto_tela", "fala", "acao") if c[k] == "PREENCHER")
    print(resumo)
    print(f"plano gravado em {destino}" + (f" ({faltam} campos PREENCHER para a IA completar)" if faltam else ""))


if __name__ == "__main__":
    main()
