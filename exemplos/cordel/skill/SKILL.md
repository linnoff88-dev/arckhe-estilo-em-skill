---
name: cordel
description: Faz vídeo explicativo curto (9:16, 16:9 ou 1:1) SEMPRE no estilo visual "cordel" descrito em references/estilo.md. Recebe tema, formato, duração, resolução e motor; planeja as cenas, desenha os storyboards no estilo, escreve a narração, anima, põe uma trilha única e entrega final/video-final.mp4 + final/manifesto.json conferidos. Use quando pedirem "vídeo no estilo cordel", "usa a skill cordel" ou um vídeo explicativo com esta cara.
---

# Skill de estilo: cordel

Esta skill faz vídeos sempre com a mesma cara. O ESTILO está em `references/estilo.md` (a bíblia).
O CONTEÚDO vem do pedido. Nunca copie personagens, logos ou textos do vídeo que inspirou o estilo.

`SKILL_DIR` = a pasta deste arquivo. Os scripts ficam em `SKILL_DIR/scripts/` e rodam com `python3`.
Trabalhe numa pasta de projeto do vídeo (padrão: a pasta atual). Tudo vai para `saida/` e `final/` dela.

## Antes de tudo
1. Leia `references/estilo.md`, `references/regras-storyboard.md`, `references/regras-video.md` e,
   se existir, `references/licoes.md` (o que já deu errado com este estilo).
2. Confira as ferramentas: `ffmpeg -version`, `python3 -c "import PIL"`. Faltou algo → diga o que instalar e pare.

## Passo 1 — os 5 dados (pergunte em texto livre o que faltar, sugerindo o padrão)
| dado | opções | padrão |
|---|---|---|
| tema | uma frase | — (obrigatório) |
| formato | 9:16 · 16:9 · 1:1 | 9:16 |
| duração | segundos; vira múltiplo de 2,5 | 15 |
| resolução | ex.: 1080x1920 | a do formato (9:16 → 1080x1920, 16:9 → 1920x1080, 1:1 → 1080x1080) |
| motor | `local` (grátis, testado) · `kling` · `seedance` (só prompts, **não testados**) | local |

## Passo 2 — plano das cenas
```bash
python3 SKILL_DIR/scripts/cenas.py --tema "<tema>" --duracao <s> --formato <f> --resolucao <WxH> --motor <m>
```
Mostra quantas cenas (2,5 s cada) e storyboards (até 6 cenas cada). Se avisar que normalizou a duração, conte ao usuário.

## Passo 3 — roteiro (você escreve)
Escreva `roteiro.json` seguindo `references/regras-video.md` (fala de até 6 palavras por cena, uma
palavra-chave grande por cena, a 1ª cena abre pela dor ou pelo desejo de quem vê, em "você"):
```json
{"personagem": "quem aparece em várias cenas, descrito sempre igual (roupa, cor, acessório)",
 "cenas": [{"texto_tela": "PALAVRA", "fala": "frase curta falada", "acao": "o que se vê", "camera": "zoom_in"}]}
```
`personagem` vai para todo pedido de storyboard (sem ele, cada storyboard inventa uma pessoa). Depois:
```bash
python3 SKILL_DIR/scripts/cenas.py ... --roteiro roteiro.json     # mesmo comando + o roteiro
```

## Passo 4 — storyboards no estilo
Monte os pedidos (um por storyboard) a partir do molde + bíblia + plano + personagem:
```bash
python3 SKILL_DIR/scripts/pedido_storyboard.py          # → saida/storyboards/pedido-storyboard-N.txt
```
Envie cada pedido, sem reescrever, à sua ferramenta de imagem (Codex: `image_gen`; Claude Code: a ferramenta de
imagem que você tiver, ou peça ao usuário para gerar e salvar). Salve em `saida/storyboards/storyboard-N.png`.
Para mudar o pedido, mude o molde (`modelos/prompt-storyboard.md`) ou a bíblia, não o texto gerado.
- Gere um de cada vez. Do 2º em diante, passe o storyboard anterior como imagem de referência (continuidade).
- **Abra a imagem e confira** com a lista de `regras-storyboard.md` (grade certa, palavra exata letra por letra,
  estilo, continuidade). Amplie as palavras para conferir. Ruim → refaça (até 2 vezes) e anote em `references/licoes.md`.

## Passo 5 — recortar
```bash
python3 SKILL_DIR/scripts/recortar.py --plano saida/plano.json      # --respiro 0.08 (padrão) protege a palavra do zoom
```

## Passo 6 — animar
```bash
python3 SKILL_DIR/scripts/animar.py                      # motor local: zoom/pan lento + dissolve
python3 SKILL_DIR/scripts/animar.py --motor kling --so-prompts      # NÃO TESTADO: só escreve os comandos
python3 SKILL_DIR/scripts/animar.py --motor seedance --so-prompts   # NÃO TESTADO: só escreve os prompts
```
Com kling/seedance, quem roda é o usuário, na conta dele; depois os clipes voltam para `saida/clipes/`.

## Passo 7 — narração (uma voz só)
```bash
python3 SKILL_DIR/scripts/narrar.py --arquivo voz.wav            # o usuário gravou tudo
python3 SKILL_DIR/scripts/narrar.py --falas-dir falas/           # o usuário gravou uma fala por cena
python3 SKILL_DIR/scripts/narrar.py --comando '<tts> {texto} {saida}'   # qualquer TTS local
python3 SKILL_DIR/scripts/narrar.py --inemavox --inemavox-dir <pasta> --ref <voz.wav>
python3 SKILL_DIR/scripts/narrar.py --edge                       # NÃO TESTADO (serviço online)
```
Com TTS, o `narrar.py` corta a "cauda" que a voz às vezes inventa depois da frase e gera de novo a fala longa
demais para o nº de palavras (`--tentativas 3`). Se avisar que uma fala passou da cena, encurte a fala no
roteiro e rode de novo. Se puder, confira a narração com uma transcrição local (as frases batem com o roteiro?);
fala com problema → `narrar.py ... --refazer N` refaz só a cena N.

## Passo 8 — montar com trilha única
```bash
python3 SKILL_DIR/scripts/montar.py [--trilha assets/trilha/x.mp3] [--volume 0.5]
```
Sem trilha em `assets/trilha/` → pergunte ao usuário qual música usar (dele ou com licença). Várias → peça para escolher.

## Passo 9 — conferir (obrigatório)
```bash
python3 SKILL_DIR/scripts/validar.py --duracao <s> --resolucao <WxH>
python3 SKILL_DIR/scripts/folha.py                 # final/folha-final.jpg: um quadro de cada cena
```
Só diga **"pronto"** depois que o `validar.py` imprimir `PASSOU` e você OLHAR a `final/folha-final.jpg`
(texto legível, sem letra trocada, estilo igual em todos os painéis). Se falhar, diga o que falta.

## Passo 10 — melhore a skill
Depois de cada vídeo, escreva em `references/licoes.md` (uma linha por item) o que saiu errado e a regra que
evitaria. Se for regra de estilo ou de storyboard, mude também `estilo.md`/`regras-storyboard.md`, não só o prompt.
