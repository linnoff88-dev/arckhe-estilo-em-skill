#!/usr/bin/env bash
# Roda todos os testes do kit (sem pytest). Precisa: python3, ffmpeg/ffprobe, Pillow.
# Uso: bash tests/rodar.sh          (TESTE_TMP=/pasta mantém os arquivos gerados para olhar)
set -u
cd "$(dirname "$0")/.." || exit 1
for p in python3 ffmpeg ffprobe; do
  command -v "$p" >/dev/null || { echo "falta: $p"; exit 2; }
done
python3 -c "import PIL" 2>/dev/null || { echo "falta o Pillow: python3 -m pip install --user Pillow"; exit 2; }
for f in molde/estilo-em-skill/scripts/*.py scripts/quadros.py; do
  python3 -m py_compile "$f" || { echo "erro de sintaxe em $f"; exit 1; }
done
bash -n scripts/instalar.sh || exit 1
timeout 1200 python3 tests/testes.py
