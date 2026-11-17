# Regras do storyboard

Um storyboard é UMA imagem com até 6 painéis. Cada painel vira uma cena de 2,5 s.
O `recortar.py` corta a imagem e o `animar.py` dá zoom de até 1,18×, então o que estiver perto da borda some.

## Grade
| formato | storyboard cheio (6 cenas) | 4 cenas | 5 cenas | 2–3 cenas |
|---|---|---|---|---|
| 9:16 (vertical) | 2 linhas × 3 colunas | 2 × 2 | 2 × 3, último vazio | 1 linha × N |
| 16:9 (horizontal) | 3 linhas × 2 colunas | 2 × 2 | 3 × 2, último vazio | N linhas × 1 |
| 1:1 | 2 linhas × 3 colunas | 2 × 2 | 2 × 3, último vazio | 1 linha × N |

A grade de cada storyboard está no `saida/plano.json` (`linhas`, `colunas`, `paineis`). Use exatamente essa.

## O que pedir na imagem
1. **Grade exata**, painéis do mesmo tamanho, cada um na proporção do vídeo (9:16 = alto e estreito).
2. **Calha lisa** de cor única (clara ou escura) entre os painéis e em volta, sem desenho nela. É ela que o `recortar.py` procura.
3. **Ordem de leitura**: esquerda → direita, de cima para baixo. Painel 1 = primeira cena do storyboard.
4. **Uma palavra-chave grande por painel** (1 palavra; no máximo 2 curtas), em MAIÚSCULAS, ≤ 10 letras.
   Prefira palavras sem acento; se tiver acento, confira com zoom depois.
5. **Zona segura**: a palavra ocupa **no máximo 60% da largura do painel**, centrada, com margem livre dos dois
   lados; nunca de borda a borda. O corte para o formato e o zoom de até 1,18× comem uns 25% da largura
   (teste da demo cordel: "REPETIR" de borda a borda perdeu o R e o R no zoom). Assunto principal também no centro.
   A ferramenta de imagem nem sempre obedece (na demo, duas tentativas saíram de borda a borda). Por isso o
   `recortar.py` põe 8% de respiro em volta de cada painel (`--respiro`): a garantia fica no script, não no pedido.
6. **Nenhum outro texto**: sem número de painel, sem legenda, sem balão, sem marca d'água, sem assinatura.
7. **Estilo da bíblia** em todos os painéis: cole a frase de estilo (seção 15 de `estilo.md`) inteira.
8. **Personagem recorrente** descrito com as mesmas palavras em todo pedido (roupa, cor, acessório).
9. **Fio condutor**: o motivo recorrente do estilo entra por uma borda do painel e sai pela borda que leva ao próximo.

## Continuidade entre storyboards
- Gere um de cada vez. Do storyboard 2 em diante, anexe o anterior como **imagem de referência** e diga:
  "mesmo estilo, mesmas cores, mesmo personagem; o fio condutor continua de onde o último painel parou".
- O último painel do storyboard N e o primeiro do N+1 têm o fio condutor no mesmo lado/altura.

## Conferência (abra a imagem antes de recortar)
- [ ] número de painéis e grade iguais ao plano
- [ ] cada palavra está EXATAMENTE como pedida (amplie: letra trocada, letra a mais, acento errado)
- [ ] nenhuma palavra ou rosto cortado pela borda do painel
- [ ] calhas lisas, sem desenho invadindo
- [ ] paleta e técnica iguais à bíblia (nada de foto, 3D, gradiente se a bíblia proíbe)
- [ ] fio condutor presente e contínuo
Falhou algo → refaça o storyboard (até 2 vezes). Se o mesmo erro voltar, mude ESTA regra ou a bíblia,
não só o pedido, e anote em `licoes.md`.
