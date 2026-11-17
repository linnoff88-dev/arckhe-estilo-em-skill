# estilo em skill: todo vÃ­deo seu no mesmo estilo, sÃ³ trocando o tema

[![estilo em skill: seu estilo vira skill](guia/assets/banner.jpg)](https://inematds.github.io/estilo-em-skill/guia/)

**ðŸ‡§ðŸ‡· [PortuguÃªs](README.md) Â· ðŸ‡ºðŸ‡¸ [English](README.en.md) Â· ðŸ‡ªðŸ‡¸ [EspaÃ±ol](README.es.md)**

## O que Ã©

VocÃª vÃª um vÃ­deo com um estilo visual que adora, tenta repetir e cada vÃ­deo seu sai com uma cara diferente. O **estilo em skill** Ã© um kit grÃ¡tis que estuda a linguagem visual desse vÃ­deo (cores, letras, composiÃ§Ã£o, movimento) e guarda tudo numa skill, um arquivo de instruÃ§Ãµes que o Claude Code ou o Codex segue. Depois vocÃª diz sÃ³ o tema, e a skill faz o vÃ­deo inteiro com a mesma cara: storyboard, cenas animadas, narraÃ§Ã£o numa voz sÃ³, uma trilha e uma conferÃªncia antes de dizer "pronto". Ã‰ para quem cria vÃ­deo curto e nÃ£o programa; vocÃª precisa do Claude Code ou do Codex, de uma ferramenta que gere imagem e de trÃªs programas grÃ¡tis no computador.

## ðŸ“– Guia de uso

Guia completo (landing + passo a passo): **https://inematds.github.io/estilo-em-skill/guia/**

ðŸŽ¬ VÃ­deo: https://www.youtube.com/watch?v=bphIJzdykNU Â· Short: https://youtube.com/shorts/mSEYJ8zA-zU

![Demo cordel: um quadro de cada cena do vÃ­deo final](exemplos/cordel/final/folha-final.jpg)

## Como funciona

Um kit aberto que transforma o **estilo** (nÃ£o o conteÃºdo) de um vÃ­deo de referÃªncia numa **skill**
reutilizÃ¡vel. Depois de instalada, vocÃª dÃ¡ sÃ³ cinco dados (tema, formato, duraÃ§Ã£o, resoluÃ§Ã£o e motor) e a
skill planeja as cenas, desenha o storyboard no estilo, escreve a narraÃ§Ã£o, anima, pÃµe uma trilha Ãºnica e
entrega `final/video-final.mp4` + `final/manifesto.json`, **conferidos por um script** antes de dizer "pronto".

**vÃ­deo de referÃªncia â†’ quadros escolhidos sozinhos â†’ a IA escreve a "bÃ­blia do estilo" â†’ skill instalada
â†’ storyboard (atÃ© 6 cenas de 2,5 s) â†’ cenas animadas â†’ narraÃ§Ã£o numa voz sÃ³ â†’ trilha Ãºnica â†’ vÃ­deo + manifesto + validaÃ§Ã£o**

## Para quem

Para quem cria vÃ­deo (reels, shorts, explicativos), tem 30+ anos, nÃ£o Ã© programador e jÃ¡ usa o
**Claude Code** ou o **Codex**. VocÃª nÃ£o precisa escrever cÃ³digo: copia comandos e conversa com a IA.

## O que vocÃª precisa

| o quÃª | para quÃª | como conferir |
|---|---|---|
| Claude Code **ou** Codex | ver os quadros, escrever a bÃ­blia, rodar a skill, gerar o storyboard | abrir no terminal |
| ffmpeg (traz o ffprobe) | cortar, animar, juntar, medir o Ã¡udio | `ffmpeg -version` |
| Python 3 | rodar os scripts | `python3 --version` |
| Pillow | mexer nas imagens | `python3 -c "import PIL"` (instalar no Ubuntu: `sudo apt install python3-pil`; no Mac: `brew install pillow`) |
| uma voz | narraÃ§Ã£o | vocÃª grava, ou um TTS local (opcional: edge-tts) |
| uma mÃºsica sua ou com licenÃ§a | trilha | um `.mp3`/`.wav` |

Para o storyboard vocÃª precisa de uma ferramenta que gere imagem (no Codex, a `image_gen` da assinatura).

## O processo, do inÃ­cio ao fim

Legenda: ðŸ§  vocÃª com a IA Â· âš™ï¸ script Â· ðŸ¤– a skill (a IA seguindo o `SKILL.md`)

| # | passo | comando | quem |
|---|---|---|---|
| 1 | Escolha o vÃ­deo de referÃªncia (o estilo que vocÃª quer) | â€” | ðŸ§  |
| 2 | Tirar 5â€“8 quadros diferentes + folha de contato | `python3 scripts/quadros.py ref.mp4 --n 8 --saida estilo/quadros/` | âš™ï¸ |
| 3 | A IA olha os quadros e escreve a bÃ­blia do estilo (paleta em hex, tipografia, composiÃ§Ã£o, o que nÃ£o fazerâ€¦) | colar `prompts/criar-skill.md` no Claude Code/Codex | ðŸ§  |
| 4 | Instalar a skill com a bÃ­blia | `bash scripts/instalar.sh meu-estilo claude --estilo estilo/estilo.md` (ou `codex`) | âš™ï¸ |
| 5 | Pedir o vÃ­deo: tema, formato, duraÃ§Ã£o, resoluÃ§Ã£o, motor | "use a skill meu-estilo para um vÃ­deo sobre â€¦" | ðŸ§  |
| 6 | Calcular cenas e storyboards â†’ `saida/plano.json` | `cenas.py --tema â€¦ --duracao 30 --formato 9:16` | ðŸ¤–âš™ï¸ |
| 7 | Escrever o roteiro (fala de atÃ© 6 palavras por cena, palavra-chave por cena) | `roteiro.json` + `cenas.py â€¦ --roteiro roteiro.json` | ðŸ¤– |
| 8 | Montar o pedido de cada storyboard a partir do molde + bÃ­blia | `pedido_storyboard.py` | âš™ï¸ |
| 9 | Gerar os storyboards, um por vez (o 2Âº recebe o 1Âº como referÃªncia), e OLHAR cada um | ferramenta de imagem â†’ `saida/storyboards/storyboard-N.png` | ðŸ¤–ðŸ§  |
| 10 | Cortar em painÃ©is no formato do vÃ­deo | `recortar.py --plano saida/plano.json` | âš™ï¸ |
| 11 | Animar (motor local: zoom/pan lento + dissolve) | `animar.py` | âš™ï¸ |
| 12 | NarraÃ§Ã£o numa voz sÃ³, encaixada nas cenas | `narrar.py --arquivo voz.wav` (ou `--falas-dir`, `--comando`, `--inemavox`) | âš™ï¸ |
| 13 | Trilha Ãºnica com ducking + vÃ­deo final + manifesto | `montar.py` | âš™ï¸ |
| 14 | Conferir de verdade e olhar a folha final | `validar.py --duracao 30 --resolucao 1080x1920` e `folha.py` | âš™ï¸ðŸ§  |
| 15 | Melhorar a skill com o que deu errado | anotar em `references/licoes.md` e mudar a regra | ðŸ§  |

Os comandos dos passos 6 a 14 ficam em `<skill>/scripts/` (ex.: `.claude/skills/meu-estilo/scripts/`).
A skill roda tudo isso sozinha; a tabela Ã© para vocÃª saber o que acontece e conseguir rodar Ã  mÃ£o.

## Cenas e storyboards

Cada cena dura **2,5 s**; cada storyboard tem **atÃ© 6 cenas** (15 s). Mais longo = vÃ¡rios storyboards,
gerados um de cada vez para manter a continuidade. DuraÃ§Ã£o que nÃ£o Ã© mÃºltiplo de 2,5 vai para o mais
prÃ³ximo, com aviso (17 s â†’ 17,5 s).

| duraÃ§Ã£o | cenas | storyboards | grade (9:16) |
|---|---|---|---|
| 10 s | 4 | 1 | 2 Ã— 2 |
| 15 s | 6 | 1 | 2 Ã— 3 |
| 20 s | 8 | 2 | 2 Ã— 2 + 2 Ã— 2 |
| 30 s | 12 | 2 | 2 Ã— 3 + 2 Ã— 3 |
| 45 s | 18 | 3 | 2 Ã— 3 Ã— 3 |

Em 16:9 a grade cheia Ã© 3 linhas Ã— 2 colunas (a folha fica quase quadrada nos dois casos).

## Motores

| motor | estado | o que faz |
|---|---|---|
| `local` | **testado** | grÃ¡tis, sem IA de vÃ­deo: cada painel ganha um movimento de cÃ¢mera lento (zoom atÃ© 1,25Ã—, pan) e as cenas se ligam por dissolve, na duraÃ§Ã£o exata |
| `kling` | **nÃ£o testado neste kit** | `animar.py --motor kling --so-prompts` escreve os comandos `kling image_to_video` de cada cena para vocÃª rodar na SUA conta |
| `seedance` / `higgsfield` | **nÃ£o testado neste kit** | `animar.py --motor seedance --so-prompts` escreve um prompt por storyboard (tempo de cada cena, cÃ¢mera, texto, transiÃ§Ã£o, fala, "sem mÃºsica") para colar no site |

O kit nÃ£o chama nenhuma API. Nos motores de IA, quem roda Ã© vocÃª, na sua conta.

## O que o kit garante (e testa)

- `quadros.py` escolhe quadros **diferentes** sozinho: troca de cena do ffmpeg + descarte de parecidos
  (desenho e cor); vÃ­deo com poucas trocas cai para quadros espaÃ§ados.
- `recortar.py` acha a calha entre os painÃ©is (clara ou escura, mesmo com o fio condutor cruzando) e, se nÃ£o
  achar, corta em grade fixa; aceita grade parcial; pÃµe respiro para o zoom nÃ£o cortar a palavra.
- `animar.py` nÃ£o encurta o vÃ­deo com o dissolve (30 s pedidos = 30 s entregues).
- `narrar.py` corta silÃªncio das pontas, acelera atÃ© 15% se precisar, avisa quando a fala nÃ£o cabe e **recusa voz muda**.
- `montar.py` usa UMA trilha do comeÃ§o ao fim (nÃ£o reinicia), volume 0,5, abaixa sob a voz (ducking), fade no fim;
  sem trilha ele para e pergunta; com vÃ¡rias, pede para escolher.
- `validar.py` confere arquivos do manifesto, duraÃ§Ã£o Â±0,5 s, resoluÃ§Ã£o, vÃ­deo + Ã¡udio, Ã¡udio e narraÃ§Ã£o que
  nÃ£o sÃ£o silÃªncio, trilha presente e `status: completo`. Se algo falha, sai com erro e diz o que falta.

Testes: `bash tests/rodar.sh` (sem pytest; imagens sintÃ©ticas e tons senoidais no lugar de voz e mÃºsica; 24/24 passando no Ubuntu).

O kit foi feito e testado no Linux (Ubuntu). No Mac nÃ£o foi testado: o `scripts/instalar.sh` usa o `sed -i` do Linux e o `tests/rodar.sh` usa `timeout`; para instalar a skill no Mac, siga o caminho manual do guia (passo 4).

## A demo: cordel

Para nÃ£o usar quadro de vÃ­deo de ninguÃ©m, o estilo de referÃªncia da demo Ã© **prÃ³prio**: 6 quadros de
xilogravura de cordel (papel creme, preto chapado, ocre e vermelho terroso, letras entalhadas e um fio
amarelo que liga as cenas) gerados para este kit e juntados num vÃ­deo curto
(`exemplos/cordel/referencia/referencia.mp4`). DaÃ­ o fluxo inteiro rodou:

- `estilo/quadros/` + `folha.jpg`: os quadros que o `quadros.py` escolheu sozinho
- `estilo/estilo.md`: a bÃ­blia preenchida com o prompt do kit
- `skill/`: a skill `cordel` instalada
- `saida/storyboards/`: os 2 storyboards (e os pedidos montados pela skill), `saida/paineis/`: os 12 painÃ©is
- `saida/plano.json`, `final/manifesto.json`, `final/video-final.mp4`, `final/folha-final.jpg`
- `LICOES.md`: o que deu errado entre as tentativas e o que mudou na skill

Tema: "Como um agente de IA tira o trabalho repetido do seu dia" â€” 30 s, 9:16, 1080Ã—1920, 12 cenas,
2 storyboards, motor local, voz local, trilha prÃ³pria.

Resultado (conferido pelo `validar.py`):

```
  ok   manifesto com status completo
  ok   30 arquivos do manifesto existem
  ok   duraÃ§Ã£o 30.00 s (pedido 30 s Â± 0,5)
  ok   resoluÃ§Ã£o 1080x1920
  ok   Ã¡udio do vÃ­deo com som (mÃ©dia -20.2 dB, pico -3.9 dB)
  ok   narraÃ§Ã£o com voz (mÃ©dia -18.9 dB)
PASSOU: vÃ­deo conferido, pode dizer pronto.
```

- MP4: 30,0 s, 1080Ã—1920, 30 fps, H.264 + AAC, 23 MB. Render local (motor `local`): 78 s nesta mÃ¡quina.
- Voz: TTS local (chatterbox, clonando uma voz de referÃªncia), 12 falas, nenhuma passando da cena. A voz
  local Ã s vezes inventa um pedaÃ§o depois da frase: o `narrar.py` refez falas longas demais, cortou caudas
  baixas e a cena 3 foi refeita sozinha com `--refazer 3`. As 12 frases, conferidas com uma transcriÃ§Ã£o local
  (Whisper, `saida/voz/transcricao-conferencia.srt`), batem com o roteiro.
- Trilha: `assets/trilha/energia.mp3` (prÃ³pria), volume 0,5, abaixando sob a voz.
- No repositÃ³rio ficam os painÃ©is em JPG (`paineis-jpg/`); os PNG, clipes e o vÃ­deo mudo sÃ£o gerados de novo
  ao rodar. Por isso, num clone, confira com `python3 skill/scripts/validar.py --sem-intermediarios`.

## Melhore a skill depois de cada teste

A skill nÃ£o nasce pronta. Depois de cada vÃ­deo, olhe a folha final e anote em `references/licoes.md` o que
saiu errado. Se o erro voltar, **mude a regra** (na bÃ­blia, nas regras do storyboard ou no script), nÃ£o sÃ³ o
pedido. Na demo, pedir "palavra com no mÃ¡ximo 60% da largura" nÃ£o adiantou duas vezes; a correÃ§Ã£o que
funcionou foi no script (`--respiro`). Veja `exemplos/cordel/LICOES.md`.

## Limites honestos

- **ResoluÃ§Ã£o do storyboard**: a ferramenta de imagem entrega cerca de 1254Ã—1254 por storyboard; cada painel
  sai com uns 370Ã—600 px e Ã© ampliado para 1080Ã—1920. Estilos chapados (gravura, recorte, flat) aguentam bem;
  estilos com muito detalhe fino ficam moles.
- **Texto desenhado** depende da ferramenta de imagem: confira cada palavra com zoom. Palavras curtas e sem
  acento erram menos.
- **Motor local nÃ£o anima o desenho**: Ã© cÃ¢mera passeando pela ilustraÃ§Ã£o + dissolve. Para personagem se
  mexendo de verdade, use um motor de IA de vÃ­deo (nÃ£o testado aqui).
- **edge-tts** usa um serviÃ§o online e nÃ£o foi testado neste kit; a demo usou TTS local. O modo `--inemavox`
  chama o `tts_direct.py` de uma instalaÃ§Ã£o local do inemavox; a API HTTP dele (porta 8010) nÃ£o estÃ¡ implementada.
- **Voz local inventa som**: o corte de cauda Ã© conservador (sÃ³ tira o que Ã© bem mais baixo ou muito curto).
  Um "som" alto sem palavra depois da frase sÃ³ Ã© pego ouvindo ou transcrevendo; aÃ­ use `--refazer N`.
- **Continuidade** entre storyboards Ã© pedida (o anterior vai como referÃªncia), mas nÃ£o Ã© garantida: confira.
- A bÃ­blia Ã© escrita pela IA olhando quadros: confira as cores e o "o que nÃ£o fazer" antes de usar.
- Use sÃ³ referÃªncias e mÃºsicas que vocÃª pode usar. O mÃ©todo copia a linguagem visual, nÃ£o personagens, logos
  ou textos.

## Estrutura

```
scripts/quadros.py, scripts/instalar.sh      â† passo 2 e 4
prompts/criar-skill.md                       â† passo 3
molde/estilo-em-skill/                       â† a skill (SKILL.md, references/, modelos/, scripts/)
tests/rodar.sh                               â† testes
exemplos/cordel/                             â† a demo completa
```

## LicenÃ§a

MIT Â© 2026 INEMA

---

Projeto adaptado da comunidade INEMA TDS - Marca Arckhe