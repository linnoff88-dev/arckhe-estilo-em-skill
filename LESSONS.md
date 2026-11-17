# LESSONS — estilo-em-skill

Uma linha por lição, a mais nova no topo: `data — o que aconteceu → regra`.

- 2026-11-13 — corte de "cauda" do TTS com 3 dB/0,5 s cortou palavra real ("de novo") → corte só ≥ 8 dB mais baixo ou < 0,25 s, teste dos dois lados, e conferir a narração com transcrição local.
- 2026-11-13 — `.gitignore` com `saida/clipes/` (barra no meio) só vale na raiz; clipes da demo entraram no commit → usar `**/saida/clipes/` e conferir `git show --stat` antes de dar o commit por bom.
