# Modelo do pedido de storyboard

Preencha os campos `{…}` e envie à ferramenta de imagem. Um pedido por storyboard.
`{frase_de_estilo}` = seção 15 de `references/estilo.md`, inteira. `{paineis}` = um item por cena do storyboard.

---

Crie UMA imagem {proporcao_folha} que é um storyboard em grade de {linhas} linha(s) × {colunas} coluna(s),
com {n_paineis} painéis do mesmo tamanho{vazio}. Cada painel tem proporção {formato} ({orientacao}). Entre os painéis e em volta deles,
uma calha lisa de cor única ({cor_calha}), sem nenhum desenho. Leitura: da esquerda para a direita, de cima
para baixo.

ESTILO (vale para todos os painéis, sem exceção): {frase_de_estilo}

TEXTO: em cada painel, só UMA palavra grande em maiúsculas, escrita exatamente como indicada abaixo, sem letras
trocadas. A palavra ocupa NO MÁXIMO 60% da largura do painel, centrada, com margem livre dos dois lados (nunca
de borda a borda). Nenhum outro texto na imagem: sem números de
painel, sem legendas, sem balões, sem assinatura, sem marca d'água.

FIO CONDUTOR: {motivo}. Ele entra por uma borda de cada painel e sai pela borda que leva ao painel seguinte.
{continuidade}

PERSONAGEM (igual em todos os painéis): {personagem}

PAINÉIS:
{paineis}

Assunto e palavras perto do centro de cada painel: o vídeo vai cortar um pouco das bordas e dar zoom.

---

Formato de cada item de `{paineis}`:
`Painel {k} — palavra "{texto_tela}". Cena: {acao}.`

`{continuidade}`:
- storyboard 1: `O fio começa no painel 1 entrando pela borda esquerda.`
- storyboard N>1 (anexe o storyboard anterior como referência): `Use a imagem anexada como referência de
  estilo, cores e personagem. O fio continua de onde parou no último painel da imagem anexada: entra no
  painel 1 pela borda esquerda, na mesma altura.`
