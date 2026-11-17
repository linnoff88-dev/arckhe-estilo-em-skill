# Regras do vídeo

## Tempo
- Cena = 2,5 s. Storyboard = até 6 cenas (15 s). Duração vira múltiplo de 2,5 (17 s → 17,5 s, com aviso).

| duração | cenas | storyboards |
|---|---|---|
| 10 s | 4 | 1 |
| 15 s | 6 | 1 |
| 20 s | 8 | 2 (4 + 4) |
| 30 s | 12 | 2 (6 + 6) |
| 45 s | 18 | 3 (6 + 6 + 6) |

## Roteiro (roteiro.json)
- **personagem** (no topo do arquivo): quem aparece em várias cenas, descrito sempre com as mesmas palavras.
- **Fala**: até 6 palavras por cena (2,5 s ≈ 6 palavras faladas sem correr). Frase completa, como se fala com alguém.
- **1ª cena**: abre pela dor ou pelo desejo de quem assiste, em "você". Nada de "Neste vídeo…" ou "Imagina…".
- **Última cena**: fecha com o ganho (o que a pessoa leva) ou uma pergunta de verdade.
- **texto_tela**: a palavra-chave desenhada no painel (1 palavra, ≤ 10 letras, maiúsculas). Ela resume a fala.
- **acao**: o que se vê no painel, concreto (quem, fazendo o quê, onde).
- **camera**: alterne (`zoom_in`, `pan_direita`, `zoom_out`, `pan_esquerda`, `pan_cima`, `pan_baixo`, `parado`).
  Não repita o mesmo movimento em duas cenas seguidas.

## Animação (motor local)
- Movimento lento e contínuo; zoom máximo 1,25× (padrão 1,18×). Nada de tremida, chicote ou zoom rápido.
- O painel entra com 8% de respiro sobre a cor da calha (como gravura no papel): o zoom não corta a palavra.
- Dissolve de 0,5 s entre cenas; o vídeo mantém a duração exata. Fade curto no fim.
- 30 fps, na resolução pedida.

## Voz
- Uma voz só no vídeo todo. Cada fala começa logo depois do início da sua cena.
- Fala que não cabe: o `narrar.py` acelera até 15%; passou disso, encurte a fala.
- Nunca entregue com voz muda: o `narrar.py` e o `validar.py` conferem.

## Trilha
- UMA trilha do começo ao fim, sem reiniciar entre storyboards. Volume 0,5; abaixa sob a voz; fade no fim.
- Só música sua ou com licença de uso.

## Motores
| motor | estado | o que faz |
|---|---|---|
| local | **testado** | Pillow + ffmpeg, grátis, sem IA de vídeo |
| kling | **não testado neste kit** | `--so-prompts` escreve os comandos `kling image_to_video` (mínimo 3 s: corte para 2,5 s) |
| seedance / higgsfield | **não testado neste kit** | `--so-prompts` escreve um prompt por storyboard para colar no site |
