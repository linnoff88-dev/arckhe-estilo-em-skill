#!/usr/bin/env python3
"""pedido_storyboard.py — monta o pedido de imagem de cada storyboard a partir do molde.

Junta: modelos/prompt-storyboard.md (o molde) + references/estilo.md (seção 15, frase de estilo)
+ saida/plano.json (grade e cenas) + roteiro.json (personagem). Assim, quando uma regra muda no molde
ou na bíblia, todos os próximos pedidos mudam junto.

Saída: saida/storyboards/pedido-storyboard-N.txt (um por storyboard)
Uso: python3 pedido_storyboard.py [--pasta .] [--roteiro roteiro.json] [--motivo "..."] [--calha "..."]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import erro, ler_json  # noqa: E402

SKILL_DIR = Path(__file__).resolve().parent.parent
ORIENTACAO = {"9:16": "vertical, alto e estreito", "16:9": "horizontal, largo e baixo", "1:1": "quadrado"}


def secao(md: str, numero: int) -> str:
    m = re.search(rf"^## {numero}\..*?$\n(.*?)(?=^## |\Z)", md, flags=re.S | re.M)
    return m.group(1).strip() if m else ""


def molde(md: str) -> str:
    partes = md.split("\n---\n")
    if len(partes) < 3:
        erro("modelos/prompt-storyboard.md precisa ter o pedido entre duas linhas '---'")
    return partes[1].strip()


def main():
    ap = argparse.ArgumentParser(description="Monta o pedido de imagem de cada storyboard")
    ap.add_argument("--pasta", default=".")
    ap.add_argument("--roteiro", default="roteiro.json")
    ap.add_argument("--estilo", default=str(SKILL_DIR / "references" / "estilo.md"))
    ap.add_argument("--motivo", help="fio condutor (padrão: 1º item da seção 9 da bíblia)")
    ap.add_argument("--calha", default="creme lisa e uniforme, sem textura")
    a = ap.parse_args()

    pasta = Path(a.pasta)
    plano = ler_json(pasta / "saida" / "plano.json")
    estilo = Path(a.estilo).read_text(encoding="utf-8")
    frase = " ".join(secao(estilo, 15).split())
    if not frase or "PREENCHER" in frase:
        erro("a seção 15 (frase de estilo) da bíblia ainda não foi preenchida")
    motivo = a.motivo
    if not motivo:
        m = re.search(r"\*\*Fio condutor\*\*:\s*(.+?)(?:\n- |\n\n|\Z)", secao(estilo, 9), flags=re.S)
        motivo = " ".join(m.group(1).split()).rstrip(".") if m else "o motivo recorrente do estilo"
    rot_arq = pasta / a.roteiro
    personagem = ler_json(rot_arq).get("personagem", "") if rot_arq.exists() else ""
    base = molde((SKILL_DIR / "modelos" / "prompt-storyboard.md").read_text(encoding="utf-8"))

    destino = pasta / "saida" / "storyboards"
    destino.mkdir(parents=True, exist_ok=True)
    for s in plano["storyboards"]:
        cenas = [c for c in plano["cenas"] if c["storyboard"] == s["numero"]]
        for c in cenas:
            if "PREENCHER" in (c["texto_tela"], c["acao"]):
                erro(f"cena {c['numero']} ainda tem PREENCHER no plano (rode cenas.py com --roteiro)")
        paineis = "\n".join(f'Painel {c["painel"]} — palavra "{c["texto_tela"]}". Cena: {c["acao"]}.' for c in cenas)
        celulas = s["linhas"] * s["colunas"]
        vazio = "" if celulas == len(cenas) else \
            f" (a grade tem {celulas} células: as {celulas - len(cenas)} últimas ficam vazias, só com a cor da calha)"
        if s["numero"] == 1:
            cont = "O fio começa no painel 1 entrando pela borda esquerda."
        else:
            cont = ("Use a imagem anexada como referência de estilo, cores e personagem. O fio continua de onde parou "
                    "no último painel da imagem anexada: entra no painel 1 pela borda esquerda, na mesma altura.")
        folha = s["colunas"] * {"9:16": 9, "16:9": 16, "1:1": 1}[plano["formato"]] / \
            (s["linhas"] * {"9:16": 16, "16:9": 9, "1:1": 1}[plano["formato"]])
        prop = "quadrada (1:1)" if 0.75 <= folha <= 1.34 else "vertical (2:3)" if folha < 0.75 else "horizontal (3:2)"
        texto = base
        for k, v in {"linhas": s["linhas"], "colunas": s["colunas"], "n_paineis": len(cenas), "vazio": vazio,
                     "formato": plano["formato"], "orientacao": ORIENTACAO.get(plano["formato"], ""),
                     "proporcao_folha": prop,
                     "cor_calha": a.calha, "frase_de_estilo": frase, "motivo": motivo, "continuidade": cont,
                     "personagem": personagem or "não há personagem fixo", "paineis": paineis}.items():
            texto = texto.replace("{" + k + "}", str(v))
        sobrou = re.findall(r"\{[a-z_]+\}", texto)
        if sobrou:
            erro(f"campos sem preencher no molde: {sobrou}")
        arq = destino / f"pedido-storyboard-{s['numero']}.txt"
        arq.write_text(texto + "\n", encoding="utf-8")
        print(f"pedido do storyboard {s['numero']}: {arq} ({len(cenas)} painéis, grade {s['linhas']}×{s['colunas']})")


if __name__ == "__main__":
    main()
