#!/usr/bin/env bash
# Gera UM storyboard da demo pelo Codex image_gen (assinatura), com o pedido montado pela skill
# (skill/scripts/pedido_storyboard.py → saida/storyboards/pedido-storyboard-N.txt).
# Do 2º em diante, anexa o storyboard anterior como referência (continuidade).
# Uso: bash exemplos/cordel/ferramentas/gerar-storyboard.sh <N> [tentativa]
set -u
N="$1"; TENT="${2:-1}"
RAIZ="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$RAIZ" || exit 1
SB="exemplos/cordel/saida/storyboards"
PEDIDO="$SB/pedido-storyboard-$N.txt"
SAIDA="$SB/storyboard-$N.png"
LOG="exemplos/cordel/logs/storyboard-$N-t$TENT.log"
mkdir -p exemplos/cordel/logs
[ -f "$PEDIDO" ] || { echo "falta $PEDIDO"; exit 1; }
[ -f "$SAIDA" ] && mv "$SAIDA" "$SB/storyboard-$N-anterior-$(date +%H%M%S).png"
REF=()
if [ "$N" -gt 1 ]; then REF=(-i "$SB/storyboard-$((N-1)).png"); fi
TEXTO="Use sua ferramenta de geração de imagem (image_gen) para criar UMA imagem e salve o PNG em $SAIDA dentro deste diretório. Não edite nenhum outro arquivo. Pedido da imagem:

$(cat "$PEDIDO")"
printf '%s' "$TEXTO" | timeout 900 codex exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox "${REF[@]}" - >"$LOG" 2>&1
if [ -s "$SAIDA" ]; then echo "ok storyboard-$N"; else echo "FALHOU storyboard-$N (ver $LOG)"; exit 1; fi
