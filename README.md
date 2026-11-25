# estilo em skill: todo vêÂ­deo seu no mesmo estilo, sêÂ³ trocando o tema

[![estilo em skill: seu estilo vira skill](guia/assets/banner.jpg)](https://linnoff88-dev.github.io/

**ê°Å¸â¡Â§ê°Å¸â¡Â· [PortuguêÂªs](README.md) êÂ· ê°Å¸â¡Âºê°Å¸â¡Â¸ [English](README.en.md) êÂ· ê°Å¸â¡Âªê°Å¸â¡Â¸ [EspaêÂ±ol](README.es.md)**

## O que êÂ©

VocêÂª vêÂª um vêÂ­deo com um estilo visual que adora, tenta repetir e cada vêÂ­deo seu sai com uma cara diferente. O **estilo em skill** êÂ© um kit grêÂ¡tis que estuda a linguagem visual desse vêÂ­deo (cores, letras, composiêÂ§êÂ£o, movimento) e guarda tudo numa skill, um arquivo de instruêÂ§êÂµes que o Claude Code ou o Codex segue. Depois vocêÂª diz sêÂ³ o tema, e a skill faz o vêÂ­deo inteiro com a mesma cara: storyboard, cenas animadas, narraêÂ§êÂ£o numa voz sêÂ³, uma trilha e uma conferêÂªncia antes de dizer "pronto". êâ° para quem cria vêÂ­deo curto e nêÂ£o programa; vocêÂª precisa do Claude Code ou do Codex, de uma ferramenta que gere imagem e de trêÂªs programas grêÂ¡tis no computador.

## ê°Å¸ââ Guia de uso

Guia completo (landing + passo a passo): **https://linnoff88-dev.github.io/

ê°Å¸Å½Â¬ VêÂ­deo: https://www.youtube.com/watch?v=bphIJzdykNU êÂ· Short: https://youtube.com/shorts/mSEYJ8zA-zU

![Demo cordel: um quadro de cada cena do vêÂ­deo final](exemplos/cordel/final/folha-final.jpg)

## Como funciona

Um kit aberto que transforma o **estilo** (nêÂ£o o conteêÂºdo) de um vêÂ­deo de referêÂªncia numa **skill**
reutilizêÂ¡vel. Depois de instalada, vocêÂª dêÂ¡ sêÂ³ cinco dados (tema, formato, duraêÂ§êÂ£o, resoluêÂ§êÂ£o e motor) e a
skill planeja as cenas, desenha o storyboard no estilo, escreve a narraêÂ§êÂ£o, anima, pêÂµe uma trilha êÂºnica e
entrega `final/video-final.mp4` + `final/manifesto.json`, **conferidos por um script** antes de dizer "pronto".

**vêÂ­deo de referêÂªncia ê¢â â quadros escolhidos sozinhos ê¢â â a IA escreve a "bêÂ­blia do estilo" ê¢â â skill instalada
ê¢â â storyboard (atêÂ© 6 cenas de 2,5 s) ê¢â â cenas animadas ê¢â â narraêÂ§êÂ£o numa voz sêÂ³ ê¢â â trilha êÂºnica ê¢â â vêÂ­deo + manifesto + validaêÂ§êÂ£o**

## Para quem

Para quem cria vêÂ­deo (reels, shorts, explicativos), tem 30+ anos, nêÂ£o êÂ© programador e jêÂ¡ usa o
**Claude Code** ou o **Codex**. VocêÂª nêÂ£o precisa escrever cêÂ³digo: copia comandos e conversa com a IA.

## O que vocêÂª precisa

| o quêÂª | para quêÂª | como conferir |
|---|---|---|
| Claude Code **ou** Codex | ver os quadros, escrever a bêÂ­blia, rodar a skill, gerar o storyboard | abrir no terminal |
| ffmpeg (traz o ffprobe) | cortar, animar, juntar, medir o êÂ¡udio | `ffmpeg -version` |
| Python 3 | rodar os scripts | `python3 --version` |
| Pillow | mexer nas imagens | `python3 -c "import PIL"` (instalar no Ubuntu: `sudo apt install python3-pil`; no Mac: `brew install pillow`) |
| uma voz | narraêÂ§êÂ£o | vocêÂª grava, ou um TTS local (opcional: edge-tts) |
| uma mêÂºsica sua ou com licenêÂ§a | trilha | um `.mp3`/`.wav` |

Para o storyboard vocêÂª precisa de uma ferramenta que gere imagem (no Codex, a `image_gen` da assinatura).

## O processo, do inêÂ­cio ao fim

Legenda: ê°Å¸Â§Â  vocêÂª com a IA êÂ· ê¢Å¡â¢ê¯Â¸Â script êÂ· ê°Å¸Â¤â a skill (a IA seguindo o `SKILL.md`)

| # | passo | comando | quem |
|---|---|---|---|
| 1 | Escolha o vêÂ­deo de referêÂªncia (o estilo que vocêÂª quer) | ê¢â¬â | ê°Å¸Â§Â  |
| 2 | Tirar 5ê¢â¬â8 quadros diferentes + folha de contato | `python3 scripts/quadros.py ref.mp4 --n 8 --saida estilo/quadros/` | ê¢Å¡â¢ê¯Â¸Â |
| 3 | A IA olha os quadros e escreve a bêÂ­blia do estilo (paleta em hex, tipografia, composiêÂ§êÂ£o, o que nêÂ£o fazerê¢â¬Â¦) | colar `prompts/criar-skill.md` no Claude Code/Codex | ê°Å¸Â§Â  |
| 4 | Instalar a skill com a bêÂ­blia | `bash scripts/instalar.sh meu-estilo claude --estilo estilo/estilo.md` (ou `codex`) | ê¢Å¡â¢ê¯Â¸Â |
| 5 | Pedir o vêÂ­deo: tema, formato, duraêÂ§êÂ£o, resoluêÂ§êÂ£o, motor | "use a skill meu-estilo para um vêÂ­deo sobre ê¢â¬Â¦" | ê°Å¸Â§Â  |
| 6 | Calcular cenas e storyboards ê¢â â `saida/plano.json` | `cenas.py --tema ê¢â¬Â¦ --duracao 30 --formato 9:16` | ê°Å¸Â¤âê¢Å¡â¢ê¯Â¸Â |
| 7 | Escrever o roteiro (fala de atêÂ© 6 palavras por cena, palavra-chave por cena) | `roteiro.json` + `cenas.py ê¢â¬Â¦ --roteiro roteiro.json` | ê°Å¸Â¤â |
| 8 | Montar o pedido de cada storyboard a partir do molde + bêÂ­blia | `pedido_storyboard.py` | ê¢Å¡â¢ê¯Â¸Â |
| 9 | Gerar os storyboards, um por vez (o 2êÂº recebe o 1êÂº como referêÂªncia), e OLHAR cada um | ferramenta de imagem ê¢â â `saida/storyboards/storyboard-N.png` | ê°Å¸Â¤âê°Å¸Â§Â  |
| 10 | Cortar em painêÂ©is no formato do vêÂ­deo | `recortar.py --plano saida/plano.json` | ê¢Å¡â¢ê¯Â¸Â |
| 11 | Animar (motor local: zoom/pan lento + dissolve) | `animar.py` | ê¢Å¡â¢ê¯Â¸Â |
| 12 | NarraêÂ§êÂ£o numa voz sêÂ³, encaixada nas cenas | `narrar.py --arquivo voz.wav` (ou `--falas-dir`, `--comando`, `--ARCKHêvox`) | ê¢Å¡â¢ê¯Â¸Â |
| 13 | Trilha êÂºnica com ducking + vêÂ­deo final + manifesto | `montar.py` | ê¢Å¡â¢ê¯Â¸Â |
| 14 | Conferir de verdade e olhar a folha final | `validar.py --duracao 30 --resolucao 1080x1920` e `folha.py` | ê¢Å¡â¢ê¯Â¸Âê°Å¸Â§Â  |
| 15 | Melhorar a skill com o que deu errado | anotar em `references/licoes.md` e mudar a regra | ê°Å¸Â§Â  |

Os comandos dos passos 6 a 14 ficam em `<skill>/scripts/` (ex.: `.claude/skills/meu-estilo/scripts/`).
A skill roda tudo isso sozinha; a tabela êÂ© para vocêÂª saber o que acontece e conseguir rodar êÂ  mêÂ£o.

## Cenas e storyboards

Cada cena dura **2,5 s**; cada storyboard tem **atêÂ© 6 cenas** (15 s). Mais longo = vêÂ¡rios storyboards,
gerados um de cada vez para manter a continuidade. DuraêÂ§êÂ£o que nêÂ£o êÂ© mêÂºltiplo de 2,5 vai para o mais
prêÂ³ximo, com aviso (17 s ê¢â â 17,5 s).

| duraêÂ§êÂ£o | cenas | storyboards | grade (9:16) |
|---|---|---|---|
| 10 s | 4 | 1 | 2 êâ 2 |
| 15 s | 6 | 1 | 2 êâ 3 |
| 20 s | 8 | 2 | 2 êâ 2 + 2 êâ 2 |
| 30 s | 12 | 2 | 2 êâ 3 + 2 êâ 3 |
| 45 s | 18 | 3 | 2 êâ 3 êâ 3 |

Em 16:9 a grade cheia êÂ© 3 linhas êâ 2 colunas (a folha fica quase quadrada nos dois casos).

## Motores

| motor | estado | o que faz |
|---|---|---|
| `local` | **testado** | grêÂ¡tis, sem IA de vêÂ­deo: cada painel ganha um movimento de cêÂ¢mera lento (zoom atêÂ© 1,25êâ, pan) e as cenas se ligam por dissolve, na duraêÂ§êÂ£o exata |
| `kling` | **nêÂ£o testado neste kit** | `animar.py --motor kling --so-prompts` escreve os comandos `kling image_to_video` de cada cena para vocêÂª rodar na SUA conta |
| `seedance` / `higgsfield` | **nêÂ£o testado neste kit** | `animar.py --motor seedance --so-prompts` escreve um prompt por storyboard (tempo de cada cena, cêÂ¢mera, texto, transiêÂ§êÂ£o, fala, "sem mêÂºsica") para colar no site |

O kit nêÂ£o chama nenhuma API. Nos motores de IA, quem roda êÂ© vocêÂª, na sua conta.

## O que o kit garante (e testa)

- `quadros.py` escolhe quadros **diferentes** sozinho: troca de cena do ffmpeg + descarte de parecidos
  (desenho e cor); vêÂ­deo com poucas trocas cai para quadros espaêÂ§ados.
- `recortar.py` acha a calha entre os painêÂ©is (clara ou escura, mesmo com o fio condutor cruzando) e, se nêÂ£o
  achar, corta em grade fixa; aceita grade parcial; pêÂµe respiro para o zoom nêÂ£o cortar a palavra.
- `animar.py` nêÂ£o encurta o vêÂ­deo com o dissolve (30 s pedidos = 30 s entregues).
- `narrar.py` corta silêÂªncio das pontas, acelera atêÂ© 15% se precisar, avisa quando a fala nêÂ£o cabe e **recusa voz muda**.
- `montar.py` usa UMA trilha do comeêÂ§o ao fim (nêÂ£o reinicia), volume 0,5, abaixa sob a voz (ducking), fade no fim;
  sem trilha ele para e pergunta; com vêÂ¡rias, pede para escolher.
- `validar.py` confere arquivos do manifesto, duraêÂ§êÂ£o êÂ±0,5 s, resoluêÂ§êÂ£o, vêÂ­deo + êÂ¡udio, êÂ¡udio e narraêÂ§êÂ£o que
  nêÂ£o sêÂ£o silêÂªncio, trilha presente e `status: completo`. Se algo falha, sai com erro e diz o que falta.

Testes: `bash tests/rodar.sh` (sem pytest; imagens sintêÂ©ticas e tons senoidais no lugar de voz e mêÂºsica; 24/24 passando no Ubuntu).

O kit foi feito e testado no Linux (Ubuntu). No Mac nêÂ£o foi testado: o `scripts/instalar.sh` usa o `sed -i` do Linux e o `tests/rodar.sh` usa `timeout`; para instalar a skill no Mac, siga o caminho manual do guia (passo 4).

## A demo: cordel

Para nêÂ£o usar quadro de vêÂ­deo de ninguêÂ©m, o estilo de referêÂªncia da demo êÂ© **prêÂ³prio**: 6 quadros de
xilogravura de cordel (papel creme, preto chapado, ocre e vermelho terroso, letras entalhadas e um fio
amarelo que liga as cenas) gerados para este kit e juntados num vêÂ­deo curto
(`exemplos/cordel/referencia/referencia.mp4`). DaêÂ­ o fluxo inteiro rodou:

- `estilo/quadros/` + `folha.jpg`: os quadros que o `quadros.py` escolheu sozinho
- `estilo/estilo.md`: a bêÂ­blia preenchida com o prompt do kit
- `skill/`: a skill `cordel` instalada
- `saida/storyboards/`: os 2 storyboards (e os pedidos montados pela skill), `saida/paineis/`: os 12 painêÂ©is
- `saida/plano.json`, `final/manifesto.json`, `final/video-final.mp4`, `final/folha-final.jpg`
- `LICOES.md`: o que deu errado entre as tentativas e o que mudou na skill

Tema: "Como um agente de IA tira o trabalho repetido do seu dia" ê¢â¬â 30 s, 9:16, 1080êâ1920, 12 cenas,
2 storyboards, motor local, voz local, trilha prêÂ³pria.

Resultado (conferido pelo `validar.py`):

```
  ok   manifesto com status completo
  ok   30 arquivos do manifesto existem
  ok   duraêÂ§êÂ£o 30.00 s (pedido 30 s êÂ± 0,5)
  ok   resoluêÂ§êÂ£o 1080x1920
  ok   êÂ¡udio do vêÂ­deo com som (mêÂ©dia -20.2 dB, pico -3.9 dB)
  ok   narraêÂ§êÂ£o com voz (mêÂ©dia -18.9 dB)
PASSOU: vêÂ­deo conferido, pode dizer pronto.
```

- MP4: 30,0 s, 1080êâ1920, 30 fps, H.264 + AAC, 23 MB. Render local (motor `local`): 78 s nesta mêÂ¡quina.
- Voz: TTS local (chatterbox, clonando uma voz de referêÂªncia), 12 falas, nenhuma passando da cena. A voz
  local êÂ s vezes inventa um pedaêÂ§o depois da frase: o `narrar.py` refez falas longas demais, cortou caudas
  baixas e a cena 3 foi refeita sozinha com `--refazer 3`. As 12 frases, conferidas com uma transcriêÂ§êÂ£o local
  (Whisper, `saida/voz/transcricao-conferencia.srt`), batem com o roteiro.
- Trilha: `assets/trilha/energia.mp3` (prêÂ³pria), volume 0,5, abaixando sob a voz.
- No repositêÂ³rio ficam os painêÂ©is em JPG (`paineis-jpg/`); os PNG, clipes e o vêÂ­deo mudo sêÂ£o gerados de novo
  ao rodar. Por isso, num clone, confira com `python3 skill/scripts/validar.py --sem-intermediarios`.

## Melhore a skill depois de cada teste

A skill nêÂ£o nasce pronta. Depois de cada vêÂ­deo, olhe a folha final e anote em `references/licoes.md` o que
saiu errado. Se o erro voltar, **mude a regra** (na bêÂ­blia, nas regras do storyboard ou no script), nêÂ£o sêÂ³ o
pedido. Na demo, pedir "palavra com no mêÂ¡ximo 60% da largura" nêÂ£o adiantou duas vezes; a correêÂ§êÂ£o que
funcionou foi no script (`--respiro`). Veja `exemplos/cordel/LICOES.md`.

## Limites honestos

- **ResoluêÂ§êÂ£o do storyboard**: a ferramenta de imagem entrega cerca de 1254êâ1254 por storyboard; cada painel
  sai com uns 370êâ600 px e êÂ© ampliado para 1080êâ1920. Estilos chapados (gravura, recorte, flat) aguentam bem;
  estilos com muito detalhe fino ficam moles.
- **Texto desenhado** depende da ferramenta de imagem: confira cada palavra com zoom. Palavras curtas e sem
  acento erram menos.
- **Motor local nêÂ£o anima o desenho**: êÂ© cêÂ¢mera passeando pela ilustraêÂ§êÂ£o + dissolve. Para personagem se
  mexendo de verdade, use um motor de IA de vêÂ­deo (nêÂ£o testado aqui).
- **edge-tts** usa um serviêÂ§o online e nêÂ£o foi testado neste kit; a demo usou TTS local. O modo `--ARCKHêvox`
  chama o `tts_direct.py` de uma instalaêÂ§êÂ£o local do ARCKHêvox; a API HTTP dele (porta 8010) nêÂ£o estêÂ¡ implementada.
- **Voz local inventa som**: o corte de cauda êÂ© conservador (sêÂ³ tira o que êÂ© bem mais baixo ou muito curto).
  Um "som" alto sem palavra depois da frase sêÂ³ êÂ© pego ouvindo ou transcrevendo; aêÂ­ use `--refazer N`.
- **Continuidade** entre storyboards êÂ© pedida (o anterior vai como referêÂªncia), mas nêÂ£o êÂ© garantida: confira.
- A bêÂ­blia êÂ© escrita pela IA olhando quadros: confira as cores e o "o que nêÂ£o fazer" antes de usar.
- Use sêÂ³ referêÂªncias e mêÂºsicas que vocêÂª pode usar. O mêÂ©todo copia a linguagem visual, nêÂ£o personagens, logos
  ou textos.

## Estrutura

```
scripts/quadros.py, scripts/instalar.sh      ê¢â Â passo 2 e 4
prompts/criar-skill.md                       ê¢â Â passo 3
molde/estilo-em-skill/                       ê¢â Â a skill (SKILL.md, references/, modelos/, scripts/)
tests/rodar.sh                               ê¢â Â testes
exemplos/cordel/                             ê¢â Â a demo completa
```

## LicenêÂ§a

MIT êÂ© 2026 ARCKHê

---

Projeto adaptado da comunidade ARCKHê TDS - ARCKHÉe