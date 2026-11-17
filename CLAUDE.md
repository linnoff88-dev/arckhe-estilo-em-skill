# CLAUDE.md — estilo-em-skill

Kit que transforma o ESTILO de um vídeo de referência numa skill do Claude Code/Codex.
Público: criador de vídeo 30+, não programador. Tudo em português do Brasil.

- Molde da skill: `molde/estilo-em-skill/` (SKILL.md, references/, modelos/, scripts/).
- Scripts do kit: `scripts/quadros.py`, `scripts/instalar.sh`. Prompt: `prompts/criar-skill.md`.
- Testes: `bash tests/rodar.sh` (sem pytest). Todo script novo ganha teste lá.
- Demo: `exemplos/cordel/` (estilo próprio, quadros gerados para o kit; nunca usar quadro de vídeo de terceiro).
- Motores kling e seedance/higgsfield: só geram prompts, **não testados**. Nenhuma API é chamada pelo kit.
- Sem caminhos da máquina dentro do molde (nada de `/home/...`); manifesto e plano com caminhos relativos.
- Commits: autor `inematds <inematds@gmail.com>`.

## Self-learning

When I correct you, or you catch yourself making a mistake: before continuing, add the lesson as a one-line rule at the TOP of [LESSONS.md](LESSONS.md) (not here), so it never happens again.

## Lessons

Lições ficam em [LESSONS.md](LESSONS.md). Antes de mexer em recorte, animação, voz ou trilha, rode `grep -in "<palavra>" LESSONS.md`.
