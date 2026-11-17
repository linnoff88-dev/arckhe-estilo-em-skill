"""Funções em comum dos scripts da skill "estilo em skill".

Só usa a biblioteca padrão do Python + ffmpeg/ffprobe no PATH.
"""
from __future__ import annotations

import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

CENA_S = 2.5            # duração fixa de cada cena
MAX_CENAS_SB = 6        # máximo de cenas por storyboard
FPS = 30

FORMATOS = {
    "9:16": {"resolucao": (1080, 1920), "grade": (2, 3)},   # (linhas, colunas) de um storyboard cheio
    "16:9": {"resolucao": (1920, 1080), "grade": (3, 2)},
    "1:1": {"resolucao": (1080, 1080), "grade": (2, 3)},
}

# grade (linhas, colunas) para k painéis, por formato. Leitura: esquerda→direita, cima→baixo.
GRADES_PARCIAIS = {
    "9:16": {1: (1, 1), 2: (1, 2), 3: (1, 3), 4: (2, 2), 5: (2, 3), 6: (2, 3)},
    "16:9": {1: (1, 1), 2: (2, 1), 3: (3, 1), 4: (2, 2), 5: (3, 2), 6: (3, 2)},
    "1:1": {1: (1, 1), 2: (1, 2), 3: (1, 3), 4: (2, 2), 5: (2, 3), 6: (2, 3)},
}


def erro(msg: str, codigo: int = 1):
    print(f"ERRO: {msg}", file=sys.stderr)
    sys.exit(codigo)


def aviso(msg: str):
    print(f"AVISO: {msg}", file=sys.stderr)


def precisa(programa: str):
    if shutil.which(programa) is None:
        erro(f"'{programa}' não encontrado no PATH. Instale o ffmpeg (que traz o ffprobe) e tente de novo.")


def rodar(cmd: list[str], timeout: int = 1800) -> subprocess.CompletedProcess:
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        cauda = "\n".join(r.stderr.strip().splitlines()[-12:])
        erro(f"comando falhou ({r.returncode}): {' '.join(cmd[:6])} ...\n{cauda}")
    return r


def parse_resolucao(txt: str) -> tuple[int, int]:
    m = re.fullmatch(r"\s*(\d+)\s*[xX×]\s*(\d+)\s*", str(txt))
    if not m:
        erro(f"resolução inválida: {txt!r} (use LARGURAxALTURA, ex.: 1080x1920)")
    w, h = int(m.group(1)), int(m.group(2))
    if w % 2 or h % 2:
        erro(f"resolução {w}x{h}: largura e altura precisam ser pares (exigência do H.264)")
    return w, h


def normalizar_duracao(pedida: float) -> float:
    """Arredonda para o múltiplo de 2,5 s mais próximo (meio sobe), mínimo 2,5 s."""
    n = math.floor(pedida / CENA_S + 0.5)
    return max(1, n) * CENA_S


def dividir_storyboards(n_cenas: int) -> list[int]:
    """Quantas cenas vai em cada storyboard, equilibrado (8 → [4, 4], 12 → [6, 6], 10 → [5, 5])."""
    n_sb = math.ceil(n_cenas / MAX_CENAS_SB)
    base, resto = divmod(n_cenas, n_sb)
    return [base + (1 if i < resto else 0) for i in range(n_sb)]


def ffprobe_json(arquivo: str | Path) -> dict:
    precisa("ffprobe")
    r = rodar(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(arquivo)], 120)
    return json.loads(r.stdout)


def duracao(arquivo: str | Path) -> float:
    info = ffprobe_json(arquivo)
    return float(info["format"].get("duration", 0.0))


def volume(arquivo: str | Path, inicio: float | None = None, dur: float | None = None) -> dict:
    """Retorna {'mean': dB, 'max': dB} do áudio (ffmpeg volumedetect)."""
    precisa("ffmpeg")
    cmd = ["ffmpeg", "-hide_banner", "-nostats"]
    if inicio is not None:
        cmd += ["-ss", f"{inicio:.3f}"]
    if dur is not None:
        cmd += ["-t", f"{dur:.3f}"]
    cmd += ["-i", str(arquivo), "-vn", "-af", "volumedetect", "-f", "null", "-"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    mean = re.search(r"mean_volume:\s*(-?[\d.inf]+) dB", r.stderr)
    mx = re.search(r"max_volume:\s*(-?[\d.inf]+) dB", r.stderr)

    def num(m):
        if not m:
            return -math.inf
        try:
            return float(m.group(1))
        except ValueError:
            return -math.inf
    return {"mean": num(mean), "max": num(mx)}


def ler_json(caminho: str | Path) -> dict:
    p = Path(caminho)
    if not p.exists():
        erro(f"arquivo não encontrado: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def gravar_json(caminho: str | Path, dados: dict):
    p = Path(caminho)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def relativo(caminho: str | Path, base: str | Path) -> str:
    """Caminho relativo à pasta do projeto (manifesto portátil)."""
    try:
        return str(Path(caminho).resolve().relative_to(Path(base).resolve()))
    except ValueError:
        return str(Path(caminho).resolve())
