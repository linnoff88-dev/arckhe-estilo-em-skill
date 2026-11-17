# Lições deste estilo

Uma linha por lição, a mais nova no topo: `data | o que saiu errado | regra que mudou (arquivo)`.

- 2026-11-13 | TTS deixou som alto sem palavra depois da frase (cena 3) | --refazer N + conferir por transcrição (scripts/narrar.py, SKILL.md)
- 2026-11-13 | corte de cauda 3 dB cortou "de novo" | cauda só ≥ 8 dB mais baixa ou < 0,25 s (scripts/narrar.py)
- 2026-11-13 | TTS local inventou pedaço em frase curta (4 palavras = 4,6 s) | refaz fala acima de 0,42 s/palavra + 0,9 s (scripts/narrar.py)
- 2026-11-13 | fio amarelo cruzando a calha fazia o recorte cair para grade fixa | busca de calha por mediana + fração (scripts/recortar.py)
- 2026-11-13 | image_gen ignorou "palavra ≤ 60% da largura" na 2ª tentativa | respiro de 8% no recorte; a garantia fica no script (scripts/recortar.py, regras-video.md)
- 2026-11-13 | palavra de borda a borda perdeu letras no zoom; gravura clara demais | bíblia: palavra ≤ 60% da largura e preto sólido ≥ 1/3 do painel (estilo.md, regras-storyboard.md, modelos/prompt-storyboard.md)
