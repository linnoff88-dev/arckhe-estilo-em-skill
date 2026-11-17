#!/usr/bin/env bash
# instalar.sh — instala a skill de um estilo no seu projeto (Claude Code ou Codex).
#
# Uso:
#   bash scripts/instalar.sh <nome-do-estilo> [claude|codex] [--estilo estilo.md] [--projeto PASTA]
#                            [--destino PASTA] [--forcar]
#
#   claude (padrão) → <projeto>/.claude/skills/<nome>/
#   codex           → <projeto>/.agents/skills/<nome>/
#   --estilo        → copia a sua bíblia do estilo para references/estilo.md
#   --destino       → instala exatamente nesta pasta (ex.: exemplos/cordel/skill)
#   --forcar        → sobrescreve uma instalação existente
set -euo pipefail
KIT="$(cd "$(dirname "$0")/.." && pwd)"
MOLDE="$KIT/molde/estilo-em-skill"

[ $# -ge 1 ] || { sed -n '2,13p' "$0"; exit 2; }
NOME="$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]/-/g; s/--*/-/g; s/^-//; s/-$//')"
shift
ALVO="claude"; ESTILO=""; PROJETO="."; DESTINO=""; FORCAR=0
while [ $# -gt 0 ]; do
  case "$1" in
    claude|codex) ALVO="$1" ;;
    --estilo) ESTILO="$2"; shift ;;
    --projeto) PROJETO="$2"; shift ;;
    --destino) DESTINO="$2"; shift ;;
    --forcar) FORCAR=1 ;;
    *) echo "opção desconhecida: $1"; exit 2 ;;
  esac
  shift
done
[ -n "$NOME" ] || { echo "nome do estilo vazio"; exit 2; }

if [ -z "$DESTINO" ]; then
  if [ "$ALVO" = "codex" ]; then DESTINO="$PROJETO/.agents/skills/$NOME"; else DESTINO="$PROJETO/.claude/skills/$NOME"; fi
fi
if [ -e "$DESTINO" ] && [ "$FORCAR" -ne 1 ]; then
  echo "já existe: $DESTINO (use --forcar para sobrescrever)"; exit 1
fi
mkdir -p "$DESTINO"
cp -r "$MOLDE/." "$DESTINO/"
find "$DESTINO" -name '__pycache__' -type d -prune -exec rm -rf {} +

# nome da skill no cabeçalho do SKILL.md
sed -i "s/^name: .*/name: $NOME/" "$DESTINO/SKILL.md"
sed -i "s/{{NOME_DO_ESTILO}}/$NOME/g" "$DESTINO/SKILL.md"

if [ -n "$ESTILO" ]; then
  [ -f "$ESTILO" ] || { echo "bíblia do estilo não encontrada: $ESTILO"; exit 1; }
  cp "$ESTILO" "$DESTINO/references/estilo.md"
fi
if grep -q "PREENCHER" "$DESTINO/references/estilo.md"; then
  echo "AVISO: references/estilo.md ainda tem marcadores PREENCHER — rode o prompts/criar-skill.md antes de usar."
fi
echo "skill '$NOME' instalada em $DESTINO ($ALVO)"
echo "Para usar: abra o $([ "$ALVO" = codex ] && echo Codex || echo Claude Code) nesse projeto e peça: \"use a skill $NOME para um vídeo sobre <tema>\""
