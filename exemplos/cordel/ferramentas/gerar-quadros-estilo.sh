#!/usr/bin/env bash
# Gera os 6 "quadros de estilo" ORIGINAIS da demo cordel pelo Codex image_gen (assinatura).
# Eles fazem o papel do "vídeo de referência" — nenhum quadro de terceiro é usado.
# Os PNG gerados foram convertidos para JPG (qualidade 90) para o repositório ficar leve.
# Uso: bash exemplos/cordel/ferramentas/gerar-quadros-estilo.sh [n1 n2 ...]   (padrão: 1..6, 3 em paralelo)
set -u
RAIZ="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$RAIZ" || exit 1
DEST="exemplos/cordel/referencia/quadros-estilo"
LOG="exemplos/cordel/logs"
mkdir -p "$DEST" "$LOG"

ESTILO="Estilo: xilogravura de cordel nordestino brasileiro. Papel creme envelhecido com fibras visíveis (#EFE3C8), tinta preta chapada (#151210) com traço de goiva irregular e áreas grandes de preto sólido, cores só em poucas áreas chapadas: ocre (#C8902E) e vermelho terroso (#A3402A). Um FIO AMARELO grosso (#F2C230), como uma linha de costura/cordão, atravessa a cena de uma borda à outra e liga os elementos. Letras grossas entalhadas em madeira, maiúsculas, pretas, com pequenas imperfeições de impressão. Moldura de filete preto irregular. Sem gradiente, sem 3D, sem brilho, sem fotografia, sem marca d'água, sem assinatura."

declare -A CENA
CENA[1]="Cena: um pescador numa jangada no mar ao amanhecer, sol grande de raios entalhados; o fio amarelo sai da vela e vai até a borda direita. Palavra grande entalhada no topo: MAR"
CENA[2]="Cena: uma feira de rua com barracas, balaios de frutas e um vendedor de chapéu de couro gritando; o fio amarelo passa por dentro dos balaios. Palavra grande entalhada no topo: FEIRA"
CENA[3]="Cena: uma casa de taipa com um mandacaru ao lado e um jumento; o fio amarelo sai da janela da casa. Palavra grande entalhada embaixo: CASA"
CENA[4]="Cena: close de duas mãos tecendo uma rede numa grade de madeira; o fio amarelo é o fio que está sendo tecido. Palavra grande entalhada no topo: TEAR"
CENA[5]="Cena: um violeiro sentado num banquinho cantando, notas musicais entalhadas saindo da viola; o fio amarelo sai das cordas da viola. Palavra grande entalhada embaixo: CANTO"
CENA[6]="Cena: um caminhão pau-de-arara numa estrada de terra indo em direção ao horizonte com lua; o fio amarelo segue a estrada até sumir. Palavra grande entalhada no topo: ESTRADA"

gera() {
  local n="$1"
  local saida="$DEST/estilo-$n.png"
  local pedido="Use sua ferramenta de geração de imagem (image_gen) para criar UMA imagem vertical (retrato, proporção 2:3) e salve o PNG em $saida dentro deste diretório. Não edite nenhum outro arquivo. ${CENA[$n]}. $ESTILO A palavra deve estar escrita exatamente como indicado, em português, sem letras trocadas, sem nenhum outro texto na imagem."
  printf '%s' "$pedido" | timeout 900 codex exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox - >"$LOG/estilo-$n.log" 2>&1
  if [ -s "$saida" ]; then echo "ok estilo-$n"; else echo "FALHOU estilo-$n (ver $LOG/estilo-$n.log)"; fi
}

LISTA=("$@"); [ ${#LISTA[@]} -eq 0 ] && LISTA=(1 2 3 4 5 6)
ativos=0
for n in "${LISTA[@]}"; do
  gera "$n" &
  ativos=$((ativos+1))
  if [ "$ativos" -ge 3 ]; then wait -n; ativos=$((ativos-1)); fi
done
wait
