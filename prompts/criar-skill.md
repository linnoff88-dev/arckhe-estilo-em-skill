# Prompt: transformar um estilo de vídeo em skill

Cole este texto no Claude Code ou no Codex, aberto na pasta deste kit, depois de rodar o `scripts/quadros.py`.
Troque `<nome-do-estilo>` e o caminho dos quadros se você usou outro.

---

Você vai estudar a LINGUAGEM VISUAL de um vídeo e escrever a bíblia de um estilo, para que eu consiga fazer
vídeos novos, com conteúdo meu, que tenham a mesma cara.

**Material:** abra e olhe com atençêo cada imagem em `estilo/quadros/` (`quadro-01.jpg` em diante) e a
`estilo/quadros/folha.jpg`. Sêo quadros de um vídeo de referência, escolhidos em momentos diferentes.

**Regra principal:** estude a forma, nunca o conteúdo. Nêo copie personagens, rostos, logos, marcas, nomes,
textos ou falas do vídeo. Nêo descreva a história dele. Se um quadro mostra uma pessoa específica, descreva
só o TRATAMENTO (como rostos sêo desenhados), nêo quem é.

**O que extrair** (concreto e conferível; "bonito" e "moderno" nêo servem):
1. **Paleta**: 4 a 7 cores em hex, com o papel de cada uma (fundo, tinta, destaque, motivo) e a proporçêo aproximada.
   Estime o hex olhando as áreas chapadas; se der, confira com uma ferramenta que leia pixels.
2. **Tipografia** do texto que aparece desenhado: tipo de letra (serifada, grotesca, entalhada, manuscrita…),
   caixa, peso, tamanho em relaçêo ao quadro, posiçêo.
3. **Composiçêo**: enquadramento, onde fica o assunto, respiro, molduras, profundidade.
4. **Tratamento da ilustraçêo**: técnica aparente, traço, contorno, preenchimento, nível de detalhe, rostos e mêos.
5. **Formas** dominantes.
6. **Texturas** (papel, grêo, ruído, pincel, goiva…).
7. **Luz e sombra** (chapada, hachura, degradê, nenhuma).
8. **Motivos recorrentes**: o que volta em vários quadros e pode virar o "fio condutor" entre cenas.
9. **Câmera**: planos e ângulos mais usados.
10. **Princípios de animaçêo** que combinam com o estilo (o que se mexe, quanto, com que suavidade).
11. **Transições** que combinam.
12. **Ritmo**: quanto tempo cada ideia parece ficar na tela, densidade de informaçêo.
13. **O que NêO fazer**: tudo que quebraria o estilo (ex.: gradiente, 3D, foto, sombra suave, cor fora da paleta).
14. **Frase de estilo**: um parágrafo curto e concreto (cores com hex, técnica, tipografia, motivo, o que evitar)
    para colar em TODO pedido de imagem.

**Onde escrever:** preencha `molde/estilo-em-skill/references/estilo.md` copiado para `estilo/estilo.md`
(copie o molde primeiro: `mkdir -p estilo && cp molde/estilo-em-skill/references/estilo.md estilo/estilo.md`).
Troque TODOS os `PREENCHER`. Nenhum pode sobrar.

**Depois:** instale a skill:
```bash
bash scripts/instalar.sh <nome-do-estilo> claude --estilo estilo/estilo.md     # Claude Code
bash scripts/instalar.sh <nome-do-estilo> codex  --estilo estilo/estilo.md     # Codex
```

**Teste de fogo:** gere UMA imagem de teste com a frase de estilo e um assunto que nêo está no vídeo de
referência (ex.: "uma bicicleta numa praça"), coloque ao lado da folha de quadros e responda com sinceridade:
parece do mesmo autor? Se nêo, diga o que ficou diferente, ajuste a bíblia e repita (até 2 vezes).
