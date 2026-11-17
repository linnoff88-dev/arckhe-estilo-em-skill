#!/usr/bin/env python3
"""recortar.py — corta um storyboard em painéis e deixa cada um no formato do vídeo.

- Grade padrão 2 linhas × 3 colunas (9:16). Aceita 1×N e grades parciais (ex.: 5 painéis numa 2×3).
- Procura a calha (faixa clara ou escura e lisa) entre os painéis perto de onde ela deveria estar;
  se não achar, corta em grade fixa.
- Cada painel é redimensionado em "cover" (preenche sem distorcer, corta a sobra no centro).
- Respiro (padrão 8% de cada lado): o painel fica um pouco menor, sobre a cor da calha, como uma gravura
  impressa no papel. Assim o zoom/pan da animação não corta a palavra, mesmo quando a ferramenta de imagem
  desenha a palavra de borda a borda (aconteceu na demo cordel). --respiro 0 desliga.

Uso:
  python3 recortar.py storyboard.png --linhas 2 --colunas 3 [--paineis 6] --resolucao 1080x1920 \
                      --saida saida/paineis --inicio 1
  python3 recortar.py --plano saida/plano.json --storyboard 1 [--pasta .]   (lê grade e nomes do plano)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import aviso, erro, gravar_json, ler_json, parse_resolucao  # noqa: E402

try:
    from PIL import Image, ImageFilter, ImageStat
except ImportError:  # pragma: no cover
    erro("Pillow não está instalado. Rode: python3 -m pip install --user Pillow")


def _perfil(img_l: Image.Image, eixo: str):
    """Para cada coluna (eixo='x') ou linha (eixo='y'): (mediana, fração de pixels perto da mediana).

    Mediana + fração (e não média + desvio) para tolerar um detalhe que cruza a calha, como o fio
    condutor passando de um painel para o outro (aconteceu na demo cordel)."""
    w, h = img_l.size
    # reduz o outro eixo para acelerar sem perder a posição exata no eixo medido
    if eixo == "x":
        pequena = img_l.resize((w, max(1, min(h, 400))))
        W, H = pequena.size
        px = pequena.load()
        linhas = ([px[x, y] for y in range(H)] for x in range(W))
    else:
        pequena = img_l.resize((max(1, min(w, 400)), h))
        W, H = pequena.size
        px = pequena.load()
        linhas = ([px[x, y] for x in range(W)] for y in range(H))
    for vals in linhas:
        med = sorted(vals)[len(vals) // 2]
        perto = sum(1 for v in vals if abs(v - med) <= 18) / len(vals)
        yield med, perto


def _lisa(med, perto, fracao_min=0.85):
    return perto >= fracao_min and (med >= 185 or med <= 60)


def achar_cortes(img_l: Image.Image, partes: int, eixo: str) -> tuple[list[tuple[int, int]], bool]:
    """Devolve os intervalos [ini, fim) de cada parte no eixo e se achou calhas de verdade."""
    total = img_l.size[0] if eixo == "x" else img_l.size[1]
    if partes == 1:
        perfil = list(_perfil(img_l, eixo))
        ini, fim = _margens(perfil)
        return [(ini, fim)], False
    perfil = list(_perfil(img_l, eixo))
    lisas = [_lisa(m, d) for m, d in perfil]
    ini_borda, fim_borda = _margens(perfil)
    util = fim_borda - ini_borda
    passo = util / partes
    janela = max(4, int(passo * 0.12))
    calhas = []
    for j in range(1, partes):
        esperado = int(ini_borda + j * passo)
        corridas, x, a, b = [], esperado - janela, None, None
        while x <= esperado + janela:
            if 0 <= x < total and lisas[x]:
                a = x if a is None else a
                b = x
            elif a is not None:
                corridas.append((a, b))
                a = None
            x += 1
        if a is not None:
            corridas.append((a, b))
        if not corridas:
            calhas.append(None)
            continue
        # a corrida mais perto do lugar esperado (desempate: a mais larga)
        corridas.sort(key=lambda c: (abs((c[0] + c[1]) / 2 - esperado), -(c[1] - c[0])))
        calhas.append(corridas[0])
    achou = all(c is not None for c in calhas)
    if not achou:
        cortes = [int(ini_borda + j * passo) for j in range(partes + 1)]
        return [(cortes[i], cortes[i + 1]) for i in range(partes)], False
    intervalos, ini = [], ini_borda
    for a, b in calhas:
        intervalos.append((ini, a))
        ini = b + 1
    intervalos.append((ini, fim_borda))
    return intervalos, True


def _margens(perfil) -> tuple[int, int]:
    """Pula a margem lisa das bordas da folha (no máximo 8% de cada lado)."""
    n = len(perfil)
    lim = int(n * 0.08)
    ini = 0
    while ini < lim and _lisa(*perfil[ini]):
        ini += 1
    fim = n
    while fim > n - lim and _lisa(*perfil[fim - 1]):
        fim -= 1
    return ini, fim


def cover(img: Image.Image, w: int, h: int) -> Image.Image:
    sw, sh = img.size
    esc = max(w / sw, h / sh)
    nw, nh = max(w, round(sw * esc)), max(h, round(sh * esc))
    grande = img.resize((nw, nh), Image.LANCZOS)
    x, y = (nw - w) // 2, (nh - h) // 2
    out = grande.crop((x, y, x + w, y + h))
    if esc > 1.5:  # painel ampliado: devolve um pouco de nitidez
        out = out.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
    return out


def cor_da_calha(img: Image.Image) -> tuple[int, int, int]:
    """Mediana das bordas externas da folha (onde fica a calha)."""
    w, h = img.size
    tiras = [img.crop((0, 0, w, 3)), img.crop((0, h - 3, w, h)), img.crop((0, 0, 3, h)), img.crop((w - 3, 0, w, h))]
    canais = [[], [], []]
    for t in tiras:
        for px in t.resize((max(1, t.width // 4), max(1, t.height // 4))).getdata():
            for i in range(3):
                canais[i].append(px[i])
    return tuple(sorted(c)[len(c) // 2] for c in canais)


def com_respiro(painel: Image.Image, w: int, h: int, respiro: float, fundo) -> Image.Image:
    if respiro <= 0:
        return cover(painel, w, h)
    iw, ih = round(w * (1 - 2 * respiro)) // 2 * 2, round(h * (1 - 2 * respiro)) // 2 * 2
    tela = Image.new("RGB", (w, h), fundo)
    tela.paste(cover(painel, iw, ih), ((w - iw) // 2, (h - ih) // 2))
    return tela


def recortar(arquivo, linhas, colunas, paineis, resolucao, saida, inicio=1, prefixo="painel",
             respiro=0.08) -> dict:
    img = Image.open(arquivo).convert("RGB")
    fundo = cor_da_calha(img)
    lum = img.convert("L")
    w, h = resolucao
    linhas_iv, achou_y = achar_cortes(lum, linhas, "y")
    # colunas medidas em cada faixa de linha (a calha vertical pode não atravessar a folha toda)
    saida = Path(saida)
    saida.mkdir(parents=True, exist_ok=True)
    gerados, n, metodo = [], 0, []
    for r, (y0, y1) in enumerate(linhas_iv):
        faixa = lum.crop((0, y0, lum.size[0], y1))
        cols_iv, achou_x = achar_cortes(faixa, colunas, "x")
        metodo.append("calha" if (achou_x or colunas == 1) and (achou_y or linhas == 1) else "grade_fixa")
        for c, (x0, x1) in enumerate(cols_iv):
            if n >= paineis:
                break
            painel = img.crop((x0, y0, x1, y1))
            if ImageStat.Stat(painel.convert("L")).stddev[0] < 3:
                aviso(f"painel {n + 1} parece vazio (cor lisa) em {arquivo}")
            destino = saida / f"{prefixo}-{inicio + n:02d}.png"
            com_respiro(painel, w, h, respiro, fundo).save(destino)
            gerados.append({"arquivo": str(destino), "origem_px": [x0, y0, x1, y1]})
            n += 1
    if n < paineis:
        erro(f"pedi {paineis} painéis mas a grade {linhas}×{colunas} só tem {n}")
    modo = "calha" if all(m == "calha" for m in metodo) else "grade_fixa"
    return {"storyboard": str(arquivo), "linhas": linhas, "colunas": colunas, "paineis": gerados,
            "respiro": respiro, "cor_calha": "#%02X%02X%02X" % fundo,
            "metodo": modo, "tamanho_storyboard": list(img.size),
            "tamanho_painel_origem": [gerados[0]["origem_px"][2] - gerados[0]["origem_px"][0],
                                      gerados[0]["origem_px"][3] - gerados[0]["origem_px"][1]]}


def main():
    ap = argparse.ArgumentParser(description="Corta um storyboard em painéis no formato do vídeo")
    ap.add_argument("storyboard", nargs="?")
    ap.add_argument("--linhas", type=int, default=2)
    ap.add_argument("--colunas", type=int, default=3)
    ap.add_argument("--paineis", type=int, help="quantos painéis usar (padrão: linhas×colunas)")
    ap.add_argument("--resolucao", default="1080x1920")
    ap.add_argument("--saida", default="saida/paineis")
    ap.add_argument("--inicio", type=int, default=1, help="número do primeiro painel (cena)")
    ap.add_argument("--respiro", type=float, default=0.08, help="margem de cada lado, 0–0.2 (0 = cover puro)")
    ap.add_argument("--plano", help="plano.json (lê grade, nomes e resolução de lá)")
    ap.add_argument("--storyboard", dest="sb", type=int, help="número do storyboard no plano")
    ap.add_argument("--pasta", default=".")
    a = ap.parse_args()

    if a.plano:
        plano = ler_json(a.plano)
        pasta = Path(a.pasta)
        alvo = [s for s in plano["storyboards"] if a.sb in (None, s["numero"])]
        if not alvo:
            erro(f"storyboard {a.sb} não existe no plano")
        res = parse_resolucao(plano["resolucao"])
        for s in alvo:
            arq = pasta / s["arquivo"]
            if not arq.exists():
                erro(f"storyboard não encontrado: {arq}")
            info = recortar(arq, s["linhas"], s["colunas"], s["paineis"], res, pasta / "saida" / "paineis",
                            inicio=s["cenas"][0], prefixo="cena", respiro=a.respiro)
            gravar_json(pasta / "saida" / "paineis" / f"recorte-storyboard-{s['numero']}.json", info)
            print(f"storyboard {s['numero']}: {len(info['paineis'])} painéis ({info['metodo']}), "
                  f"painel de origem {info['tamanho_painel_origem'][0]}x{info['tamanho_painel_origem'][1]} px")
        return

    if not a.storyboard:
        erro("informe o arquivo do storyboard ou --plano")
    paineis = a.paineis or a.linhas * a.colunas
    if paineis > a.linhas * a.colunas:
        erro(f"{paineis} painéis não cabem numa grade {a.linhas}×{a.colunas}")
    info = recortar(a.storyboard, a.linhas, a.colunas, paineis, parse_resolucao(a.resolucao), a.saida, a.inicio,
                    respiro=a.respiro)
    print(json.dumps({"paineis": len(info["paineis"]), "metodo": info["metodo"],
                      "painel_origem": info["tamanho_painel_origem"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
