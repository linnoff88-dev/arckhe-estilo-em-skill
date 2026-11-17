# Modelo do pedido de vídeo (motores externos — NÃO TESTADOS NESTE KIT)

O motor local não usa este arquivo. Ele serve para quem quer animar os painéis num motor de IA de vídeo
na própria conta. O `animar.py --motor kling|seedance --so-prompts` escreve os pedidos por você seguindo
esta estrutura; ajuste aqui se quiser mudar o padrão.

## Por cena (Kling, imagem → vídeo)
```
Anime esta ilustração mantendo o estilo exato (sem mudar traço, cores ou texto).
Ação: {acao}. Câmera: {camera}, lenta e suave.
O texto '{texto_tela}' fica parado e legível. Sem música, sem fala, sem texto novo.
```
O Kling gera no mínimo 3 s: corte cada clipe para 2,5 s antes de montar.

## Por storyboard (Seedance / Higgsfield, storyboard → vídeo)
```
Vídeo {formato} de {duracao} segundos feito a partir desta imagem de storyboard ({linhas}×{colunas} painéis,
leitura da esquerda para a direita, de cima para baixo). Cada painel é uma cena de 2,5 s.
Mantenha EXATAMENTE o estilo, as cores e as letras dos painéis.
{t0}–{t1} s | painel {k} | câmera: {camera} | ação: {acao} | texto na tela: "{texto_tela}" entra com leve
escala, fica legível | entrada: {transicao} | fala: "{fala}"
...
Transições suaves (dissolve). Sem música e sem efeitos sonoros (a trilha entra depois). Não invente texto novo.
```
Depois de baixar os clipes, coloque em `saida/clipes/` e siga com `narrar.py` e `montar.py`
(para montar com clipes externos, junte-os em `saida/video-mudo.mp4` com a duração exata do plano).
