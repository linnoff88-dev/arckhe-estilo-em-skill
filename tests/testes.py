#!/usr/bin/env python3
"""Testes do kit "estilo em skill" (sem pytest). Rode por tests/rodar.sh.

Tudo é sintético e local: imagens feitas pelo Pillow, voz e trilha = tons senoidais do ffmpeg.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SCRIPTS = RAIZ / "molde" / "estilo-em-skill" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from PIL import Image, ImageDraw  # noqa: E402

import cenas  # noqa: E402

TMP = Path(os.environ.get("TESTE_TMP") or tempfile.mkdtemp(prefix="estilo-em-skill-"))
resultados = []


def caso(nome):
    def deco(f):
        def rodar():
            try:
                f()
                resultados.append((nome, True, ""))
                print(f"  ok    {nome}")
            except Exception as e:  # noqa: BLE001
                resultados.append((nome, False, str(e)))
                print(f"  FALHA {nome}: {e}")
                traceback.print_exc(limit=2)
        rodar.__name__ = f.__name__
        return rodar
    return deco


def py(script, *args, ok=True, cwd=None):
    r = subprocess.run([sys.executable, str(script), *map(str, args)], capture_output=True, text=True,
                       timeout=900, cwd=cwd)
    if ok and r.returncode != 0:
        raise AssertionError(f"{Path(script).name} saiu {r.returncode}: {r.stderr[-600:]}")
    return r


def ff(*args):
    r = subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *map(str, args)],
                       capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stderr[-400:]


def probe(arq):
    r = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(arq)],
                       capture_output=True, text=True)
    return json.loads(r.stdout)


CORES = [(200, 40, 40), (40, 160, 60), (40, 70, 200), (220, 170, 30), (150, 50, 170), (30, 170, 170)]


def painel_textura(w, h, cor, rotulo):
    """Painel com textura (não é 'liso', senão confunde a busca de calha)."""
    im = Image.new("RGB", (w, h), cor)
    d = ImageDraw.Draw(im)
    for i in range(0, w + h, 18):
        d.line([(i, 0), (i - h, h)], fill=tuple(max(0, c - 60) for c in cor), width=5)
    d.rectangle([w * 0.3, h * 0.4, w * 0.7, h * 0.6], fill=(255 - cor[0], 255 - cor[1], 255 - cor[2]))
    d.text((10, 10), rotulo, fill=(0, 0, 0))
    return im


def folha_sintetica(destino, linhas, colunas, pw, ph, calha, cor_calha, n=None, margens=(30, 30, 30, 30)):
    """Folha com painéis de tamanho conhecido; devolve as caixas reais de cada painel."""
    esq, topo, dir_, base = margens
    W = esq + colunas * pw + (colunas - 1) * calha + dir_
    H = topo + linhas * ph + (linhas - 1) * calha + base
    folha = Image.new("RGB", (W, H), cor_calha)
    caixas = []
    k = 0
    for r in range(linhas):
        for c in range(colunas):
            if n is not None and k >= n:
                break
            x, y = esq + c * (pw + calha), topo + r * (ph + calha)
            folha.paste(painel_textura(pw, ph, CORES[k % 6], f"P{k + 1}"), (x, y))
            caixas.append((x, y, x + pw, y + ph))
            k += 1
    folha.save(destino)
    return caixas


# ---------------------------------------------------------------- cenas.py
@caso("cenas: 10/15/20/30/45 s → cenas e storyboards da tabela")
def t_cenas_tabela():
    esperado = {10: (4, 1), 15: (6, 1), 20: (8, 2), 30: (12, 2), 45: (18, 3)}
    for d, (nc, ns) in esperado.items():
        c = cenas.calcular(d)
        assert (c["n_cenas"], c["n_storyboards"]) == (nc, ns), f"{d} s → {c}"
        assert not c["normalizada"]
        assert max(c["cenas_por_storyboard"]) <= 6 and sum(c["cenas_por_storyboard"]) == nc


@caso("cenas: 17 s normaliza para 17,5 s (7 cenas, 2 storyboards) e avisa")
def t_cenas_normaliza():
    c = cenas.calcular(17)
    assert c["duracao_s"] == 17.5 and c["n_cenas"] == 7 and c["n_storyboards"] == 2 and c["normalizada"], c
    r = py(SCRIPTS / "cenas.py", "--so-calcular", "--duracao", 17)
    assert "17.5 s = 7 cenas / 2 storyboard" in r.stdout, r.stdout
    assert "AVISO" in r.stderr and "17,5" not in r.stdout


@caso("cenas: plano.json com tempos, storyboard, grade e campos de cada cena")
def t_cenas_plano():
    p = TMP / "plano-teste"
    py(SCRIPTS / "cenas.py", "--tema", "teste", "--duracao", 20, "--formato", "9:16", "--pasta", p)
    plano = json.loads((p / "saida" / "plano.json").read_text())
    assert plano["n_cenas"] == 8 and plano["cenas_por_storyboard"] == [4, 4]
    assert plano["storyboards"][1]["continua_de"] == 1
    assert (plano["storyboards"][0]["linhas"], plano["storyboards"][0]["colunas"]) == (2, 2)
    c3 = plano["cenas"][2]
    assert (c3["inicio_s"], c3["fim_s"], c3["storyboard"]) == (5.0, 7.5, 1)
    for campo in ("texto_tela", "acao", "camera", "transicao_entrada", "transicao_saida", "fala"):
        assert campo in c3, campo
    plano30 = cenas.montar_plano("x", 30, "9:16", (1080, 1920), "local")
    assert [(s["linhas"], s["colunas"]) for s in plano30["storyboards"]] == [(2, 3), (2, 3)]


# ---------------------------------------------------------------- recortar.py
def confere_recorte(pasta, caixas, info, tol=4):
    assert len(info["paineis"]) == len(caixas), (len(info["paineis"]), len(caixas))
    for i, (p, cx) in enumerate(zip(info["paineis"], caixas)):
        got = p["origem_px"]
        assert all(abs(g - e) <= tol for g, e in zip(got, cx)), f"painel {i + 1}: {got} ≠ {cx}"
        im = Image.open(p["arquivo"])
        assert im.size == (270, 480), im.size
        # canto do painel recortado tem a cor (escurecida ou não) do painel certo, não a da calha
        r, g, b = im.convert("RGB").resize((1, 1), Image.BOX).getpixel((0, 0))
        er, eg, eb = CORES[i % 6]
        assert abs(r - er) + abs(g - eg) + abs(b - eb) < 200, f"painel {i + 1} cor {(r, g, b)} ≠ {CORES[i % 6]}"


@caso("recortar: grade 2×3 com calha clara e margens desiguais (acha a calha)")
def t_recortar_23():
    import recortar
    arq = TMP / "sb-2x3.png"
    caixas = folha_sintetica(arq, 2, 3, 300, 533, 24, (245, 238, 220), margens=(60, 20, 12, 40))
    info = recortar.recortar(arq, 2, 3, 6, (270, 480), TMP / "rec23", respiro=0)
    assert info["metodo"] == "calha", info["metodo"]
    confere_recorte(TMP / "rec23", caixas, info)


@caso("recortar: acha a calha mesmo com o fio condutor cruzando de um painel ao outro")
def t_recortar_fio():
    import recortar
    arq = TMP / "sb-fio.png"
    caixas = folha_sintetica(arq, 2, 3, 300, 533, 20, (248, 216, 160), margens=(40, 30, 25, 35))
    im = Image.open(arq)
    d = ImageDraw.Draw(im)
    d.line([(0, 300), (im.width, 330)], fill=(242, 194, 48), width=16)      # fio na linha de cima
    d.line([(0, 870), (im.width, 840)], fill=(242, 194, 48), width=16)      # e na de baixo
    d.line([(150, 0), (170, im.height)], fill=(242, 194, 48), width=10)     # e um descendo dentro dos painéis
    im.save(arq)
    info = recortar.recortar(arq, 2, 3, 6, (270, 480), TMP / "recfio", respiro=0)
    assert info["metodo"] == "calha", info["metodo"]
    confere_recorte(TMP / "recfio", caixas, info)


@caso("recortar: grade parcial 2×2 com calha escura")
def t_recortar_22():
    import recortar
    arq = TMP / "sb-2x2.png"
    caixas = folha_sintetica(arq, 2, 2, 320, 568, 18, (12, 12, 12))
    info = recortar.recortar(arq, 2, 2, 4, (270, 480), TMP / "rec22", respiro=0)
    assert info["metodo"] == "calha"
    confere_recorte(TMP / "rec22", caixas, info)


@caso("recortar: 5 painéis numa 2×3 (último vazio) e 1×3 pela linha de comando")
def t_recortar_parcial_cli():
    arq = TMP / "sb-5.png"
    folha_sintetica(arq, 2, 3, 300, 533, 20, (250, 250, 250), n=5)
    r = py(SCRIPTS / "recortar.py", arq, "--linhas", 2, "--colunas", 3, "--paineis", 5, "--resolucao", "270x480",
           "--saida", TMP / "rec5")
    assert len(list((TMP / "rec5").glob("painel-*.png"))) == 5, r.stdout
    arq = TMP / "sb-1x3.png"
    folha_sintetica(arq, 1, 3, 300, 533, 20, (250, 250, 250))
    py(SCRIPTS / "recortar.py", arq, "--linhas", 1, "--colunas", 3, "--resolucao", "270x480", "--saida", TMP / "rec13")
    assert len(list((TMP / "rec13").glob("painel-*.png"))) == 3


@caso("recortar: sem calha nenhuma cai para grade fixa")
def t_recortar_fixa():
    import recortar
    arq = TMP / "sb-sem-calha.png"
    caixas = folha_sintetica(arq, 2, 3, 300, 533, 0, (0, 0, 0), margens=(0, 0, 0, 0))
    info = recortar.recortar(arq, 2, 3, 6, (270, 480), TMP / "recfixa", respiro=0)
    assert info["metodo"] == "grade_fixa", info["metodo"]
    confere_recorte(TMP / "recfixa", caixas, info, tol=6)


@caso("recortar: respiro põe o painel sobre a cor da calha (zoom não corta a palavra)")
def t_recortar_respiro():
    import recortar
    arq = TMP / "sb-2x3.png"
    info = recortar.recortar(arq, 2, 3, 6, (270, 480), TMP / "recresp", respiro=0.1)
    assert info["cor_calha"] == "#F5EEDC", info["cor_calha"]
    im = Image.open(info["paineis"][0]["arquivo"]).convert("RGB")
    assert im.size == (270, 480)
    assert im.getpixel((5, 5)) == (245, 238, 220) and im.getpixel((264, 474)) == (245, 238, 220)
    r, g, b = im.getpixel((135, 100))
    assert (r, g, b) != (245, 238, 220), "o miolo deveria ser o painel"


# ---------------------------------------------------------------- fluxo curto: animar → narrar → montar → validar
def projeto_sintetico(nome, duracao=5.0, trilha=True):
    p = TMP / nome
    if p.exists():
        shutil.rmtree(p)
    roteiro = {"cenas": [{"texto_tela": f"CENA {i + 1}", "fala": f"fala {i + 1}", "acao": "teste",
                          "camera": ["zoom_in", "pan_direita", "zoom_out", "pan_cima"][i % 4]}
                         for i in range(int(duracao / 2.5))]}
    p.mkdir(parents=True)
    (p / "roteiro.json").write_text(json.dumps(roteiro))
    py(SCRIPTS / "cenas.py", "--tema", "teste", "--duracao", duracao, "--formato", "9:16", "--resolucao", "360x640",
       "--roteiro", p / "roteiro.json", "--pasta", p)
    plano = json.loads((p / "saida" / "plano.json").read_text())
    for s in plano["storyboards"]:
        arq = p / s["arquivo"]
        arq.parent.mkdir(parents=True, exist_ok=True)
        folha_sintetica(arq, s["linhas"], s["colunas"], 180, 320, 14, (240, 232, 214), n=s["paineis"])
    py(SCRIPTS / "recortar.py", "--plano", p / "saida" / "plano.json", "--pasta", p)
    if trilha:
        (p / "assets" / "trilha").mkdir(parents=True)
        ff("-f", "lavfi", "-i", "sine=frequency=330:duration=3", "-ac", "2", p / "assets" / "trilha" / "tom.wav")
    return p


VOZ_TOM = "ffmpeg -y -loglevel error -f lavfi -i sine=frequency=220:duration=1.4 -af volume=0.6 {saida}/fala.wav"


@caso("fluxo curto: animar + narrar + montar + validar PASSA (5 s, 360×640)")
def t_fluxo_ok():
    p = projeto_sintetico("fluxo-ok")
    py(SCRIPTS / "animar.py", "--pasta", p)
    for i in (1, 2):
        d = float(probe(p / "saida" / "clipes" / f"cena-{i:02d}.mp4")["format"]["duration"])
        assert abs(d - 2.5) < 0.05, f"clipe {i}: {d}"
    mudo = probe(p / "saida" / "video-mudo.mp4")
    assert abs(float(mudo["format"]["duration"]) - 5.0) < 0.05, "dissolve não pode encurtar o vídeo"
    py(SCRIPTS / "narrar.py", "--pasta", p, "--comando", VOZ_TOM)
    enc = json.loads((p / "saida" / "voz" / "encaixe.json").read_text())
    assert len(enc["falas"]) == 2 and enc["falas"][1]["inicio_s"] >= 2.5
    py(SCRIPTS / "montar.py", "--pasta", p)
    m = json.loads((p / "final" / "manifesto.json").read_text())
    assert m["status"] == "completo" and m["trilha"] == "assets/trilha/tom.wav" and m["trilha_volume"] == 0.5
    assert not m["video"].startswith("/"), "manifesto deve ter caminhos relativos"
    r = py(SCRIPTS / "validar.py", "--pasta", p, "--duracao", 5, "--resolucao", "360x640")
    assert "PASSOU" in r.stdout, r.stdout
    info = probe(p / "final" / "video-final.mp4")
    assert {s["codec_type"] for s in info["streams"]} == {"video", "audio"}


@caso("trilha: ducking abaixa a música sob a voz e ela volta na pausa")
def t_ducking():
    import comum
    p = TMP / "fluxo-ok"
    final = p / "final" / "video-final.mp4"
    # sem voz (0,0–0,1 s não tem fala) x com voz: a mistura com voz não pode ser só soma (ducking age)
    # voz (220 Hz) nas cenas 0,12–1,52 s e 2,62–4,02 s; trilha = 330 Hz. Isola só a trilha com passa-faixa
    # estreito e compara: durante a fala x na pausa entre as falas (2,1–2,5 s).
    musica_isolada = TMP / "musica-sob-voz.wav"
    ff("-i", final, "-af", ",".join(["bandpass=f=330:t=q:w=25"] * 3), "-t", "5", musica_isolada)
    durante = comum.volume(musica_isolada, 0.6, 0.6)["mean"]
    fora = comum.volume(musica_isolada, 2.15, 0.35)["mean"]
    assert fora > -45, f"música sumiu na pausa: {fora}"
    assert durante < fora - 3, f"música não abaixou sob a voz (durante {durante} dB, fora {fora} dB)"


@caso("montar: sem trilha para com código 3; com 2 trilhas pede --trilha (código 4)")
def t_montar_trilha():
    p = projeto_sintetico("sem-trilha", trilha=False)
    py(SCRIPTS / "animar.py", "--pasta", p, "--dissolve", 0)
    py(SCRIPTS / "narrar.py", "--pasta", p, "--comando", VOZ_TOM)
    r = py(SCRIPTS / "montar.py", "--pasta", p, ok=False)
    assert r.returncode == 3 and "nenhuma trilha" in r.stderr, (r.returncode, r.stderr)
    (p / "assets" / "trilha").mkdir(parents=True)
    for f in (220, 440):
        ff("-f", "lavfi", "-i", f"sine=frequency={f}:duration=2", p / "assets" / "trilha" / f"t{f}.wav")
    r = py(SCRIPTS / "montar.py", "--pasta", p, ok=False)
    assert r.returncode == 4 and "--trilha" in r.stderr, (r.returncode, r.stderr)
    py(SCRIPTS / "montar.py", "--pasta", p, "--trilha", "t440.wav")
    m = json.loads((p / "final" / "manifesto.json").read_text())
    assert m["trilha"].endswith("t440.wav")


@caso("validar FALHA: sem trilha (montado com --sem-trilha)")
def t_validar_sem_trilha():
    p = TMP / "sem-trilha"
    py(SCRIPTS / "montar.py", "--pasta", p, "--sem-trilha")
    r = py(SCRIPTS / "validar.py", "--pasta", p, ok=False)
    assert r.returncode == 1 and "sem trilha" in r.stdout and "FALHOU" in r.stdout, r.stdout


@caso("validar FALHA: duração errada (pedido 10 s, vídeo de 5 s)")
def t_validar_duracao():
    r = py(SCRIPTS / "validar.py", "--pasta", TMP / "fluxo-ok", "--duracao", 10, ok=False)
    assert r.returncode == 1 and "fora do pedido" in r.stdout, r.stdout
    r = py(SCRIPTS / "validar.py", "--pasta", TMP / "fluxo-ok", "--resolucao", "1080x1920", ok=False)
    assert r.returncode == 1 and "resolução" in r.stdout


@caso("validar FALHA: narração muda (mesmo com a trilha tocando por cima)")
def t_validar_mudo():
    p = TMP / "mudo"
    if p.exists():
        shutil.rmtree(p)
    shutil.copytree(TMP / "fluxo-ok", p)
    ff("-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", 5, p / "saida" / "voz" / "narracao.wav")
    py(SCRIPTS / "montar.py", "--pasta", p)
    r = py(SCRIPTS / "validar.py", "--pasta", p, ok=False)
    assert r.returncode == 1 and "narração muda" in r.stdout, r.stdout


@caso("narrar: fala longa demais para o nº de palavras é gerada de novo (fica a mais curta)")
def t_narrar_tentativas():
    p = TMP / "fluxo-ok"
    cont = TMP / "contador-tts"
    cont.unlink(missing_ok=True)
    tts = TMP / "tts-falso.sh"
    tts.write_text(f"""n=$(cat {cont} 2>/dev/null || echo 0); echo $((n+1)) > {cont}
d=1.2; [ "$n" -eq 0 ] && d=6
ffmpeg -y -loglevel error -f lavfi -i sine=frequency=220:duration=$d "$1/fala.wav"
""")
    r = py(SCRIPTS / "narrar.py", "--pasta", p, "--comando", f"bash {tts} {{saida}}")
    assert "gerando de novo" in r.stdout, r.stdout
    enc = json.loads((p / "saida" / "voz" / "encaixe.json").read_text())
    assert all(f["duracao_s"] < 1.5 for f in enc["falas"]), enc["falas"]
    py(SCRIPTS / "narrar.py", "--pasta", p, "--comando", VOZ_TOM)      # deixa o projeto como estava


@caso("narrar: corta a cauda baixa que o TTS inventa, mas não a última palavra de verdade")
def t_narrar_cauda():
    p = TMP / "fluxo-ok"

    def tts_com_cauda(nome, vol_cauda, dur_cauda):
        arq = TMP / nome
        arq.write_text(f"""ffmpeg -y -loglevel error -f lavfi -i "sine=frequency=220:duration=1.0" -f lavfi -i "anullsrc=r=48000:cl=mono" \\
  -f lavfi -i "sine=frequency=180:duration={dur_cauda}" -filter_complex \\
  "[0:a]aresample=48000,volume=1.0[a];[1:a]atrim=0:0.3[b];[2:a]aresample=48000,volume={vol_cauda}[c];[a][b][c]concat=n=3:v=0:a=1" \\
  "$1/fala.wav"
""")
        py(SCRIPTS / "narrar.py", "--pasta", p, "--comando", f"bash {arq} {{saida}}")
        return json.loads((p / "saida" / "voz" / "encaixe.json").read_text())["falas"]

    # murmúrio 12 dB mais baixo depois da frase → cortado
    falas = tts_com_cauda("tts-cauda.sh", 0.25, 0.8)
    assert all(0.9 < f["duracao_s"] < 1.15 and f["cauda_cortada_s"] > 0.9 for f in falas), falas
    # palavra final de verdade, no mesmo volume, depois de uma pausa (o "de novo") → fica
    falas = tts_com_cauda("tts-palavra.sh", 0.9, 0.5)
    assert all(f["duracao_s"] > 1.7 and f["cauda_cortada_s"] == 0 for f in falas), falas
    py(SCRIPTS / "narrar.py", "--pasta", p, "--comando", VOZ_TOM)      # deixa o projeto como estava


@caso("narrar --refazer: refaz só a cena pedida e reaproveita as outras falas")
def t_narrar_refazer():
    p = TMP / "fluxo-ok"
    py(SCRIPTS / "narrar.py", "--pasta", p, "--comando", VOZ_TOM)
    antes = json.loads((p / "saida" / "voz" / "encaixe.json").read_text())["falas"]
    outro = VOZ_TOM.replace("frequency=220", "frequency=260")
    r = py(SCRIPTS / "narrar.py", "--pasta", p, "--comando", outro, "--refazer", "2")
    depois = json.loads((p / "saida" / "voz" / "encaixe.json").read_text())["falas"]
    assert depois[0]["arquivo"] == antes[0]["arquivo"] and depois[1]["arquivo"] != antes[1]["arquivo"], depois
    assert r.stdout.count("voz da cena") == 1, r.stdout
    assert Path(depois[0]["arquivo"]).exists() and Path(depois[1]["arquivo"]).exists()


@caso("narrar RECUSA voz muda (TTS que grava silêncio)")
def t_narrar_mudo():
    p = TMP / "fluxo-ok"
    r = py(SCRIPTS / "narrar.py", "--pasta", p, "--comando",
           "ffmpeg -y -loglevel error -f lavfi -i anullsrc=r=24000:cl=mono -t 1 {saida}/fala.wav", ok=False)
    assert r.returncode != 0 and "MUDA" in r.stderr, r.stderr[-300:]


@caso("animar: motores kling/seedance só geram prompts (não testados) e exigem --so-prompts")
def t_motores_prompts():
    p = TMP / "fluxo-ok"
    r = py(SCRIPTS / "animar.py", "--pasta", p, "--motor", "kling", ok=False)
    assert r.returncode != 0 and "--so-prompts" in r.stderr
    py(SCRIPTS / "animar.py", "--pasta", p, "--motor", "kling", "--so-prompts")
    txt = (p / "saida" / "prompts-kling.sh").read_text()
    assert "kling image_to_video" in txt and "NÃO TESTADO" in txt and txt.count("image_to_video") == 2
    py(SCRIPTS / "animar.py", "--pasta", p, "--motor", "seedance", "--so-prompts")
    md = (p / "saida" / "prompts-seedance.md").read_text()
    assert "Sem música" in md and "0.0–2.5 s" in md


@caso("pedido_storyboard: monta o pedido do molde com grade, frase de estilo e palavras de cada painel")
def t_pedido_storyboard():
    p = TMP / "fluxo-ok"
    est = TMP / "estilo-teste.md"
    est.write_text("# Bíblia\n\n## 9. Motivos recorrentes\n- **Fio condutor**: uma fita azul.\n\n"
                   "## 15. Frase de estilo para colar em todo pedido de imagem\nRecorte de papel azul (#0000FF).\n")
    r = py(SCRIPTS / "pedido_storyboard.py", "--pasta", p, "--estilo", est)
    txt = (p / "saida" / "storyboards" / "pedido-storyboard-1.txt").read_text()
    assert "Recorte de papel azul (#0000FF)." in txt and "uma fita azul. Ele entra" in txt, txt[:400]
    assert 'Painel 2 — palavra "CENA 2"' in txt and "1 linha(s) × 2 coluna(s)" in txt and "{" not in txt, r.stdout
    est.write_text("## 15. Frase de estilo\nPREENCHER\n")
    r = py(SCRIPTS / "pedido_storyboard.py", "--pasta", p, "--estilo", est, ok=False)
    assert r.returncode != 0 and "não foi preenchida" in r.stderr


# ---------------------------------------------------------------- instalar.sh
@caso("instalar: Claude Code em .claude/skills/<nome>, Codex em .agents/skills/<nome>, nome no SKILL.md")
def t_instalar():
    proj = TMP / "proj-instalar"
    proj.mkdir(exist_ok=True)
    estilo = proj / "estilo.md"
    estilo.write_text("# Bíblia do estilo: teste\n\n## 15. Frase de estilo\nTudo azul.\n")
    for alvo, pasta in (("claude", ".claude"), ("codex", ".agents")):
        r = subprocess.run(["bash", str(RAIZ / "scripts" / "instalar.sh"), "Meu Estilo!", alvo, "--estilo", str(estilo),
                            "--projeto", str(proj)], capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr
        dest = proj / pasta / "skills" / "meu-estilo"
        assert (dest / "SKILL.md").read_text().splitlines()[1] == "name: meu-estilo"
        assert (dest / "references" / "estilo.md").read_text() == estilo.read_text()
        assert (dest / "scripts" / "validar.py").exists()
    r = subprocess.run(["bash", str(RAIZ / "scripts" / "instalar.sh"), "meu-estilo", "--projeto", str(proj)],
                       capture_output=True, text=True)
    assert r.returncode != 0 and "--forcar" in r.stdout, "não pode sobrescrever sem --forcar"


# ---------------------------------------------------------------- quadros.py
@caso("quadros: vídeo com 6 cortes → 6 quadros diferentes + folha.jpg")
def t_quadros_cortes():
    pasta = TMP / "ref"
    pasta.mkdir(exist_ok=True)
    lista = []
    for i in range(6):
        im = painel_textura(360, 640, CORES[i], f"REF {i}")
        d = ImageDraw.Draw(im)
        d.ellipse([40 + i * 40, 60, 200 + i * 20, 260], fill=(255, 255, 255))
        arq = pasta / f"r{i}.png"
        im.save(arq)
        lista.append(f"file '{arq}'\nduration 1.5\n")
    lista.append(f"file '{pasta / 'r5.png'}'\n")
    (pasta / "lista.txt").write_text("".join(lista))
    ff("-f", "concat", "-safe", "0", "-i", pasta / "lista.txt", "-vf", "fps=30,format=yuv420p", pasta / "ref.mp4")
    out = TMP / "quadros-cortes"
    r = py(RAIZ / "scripts" / "quadros.py", pasta / "ref.mp4", "--n", 8, "--saida", out)
    q = json.loads((out / "quadros.json").read_text())
    assert len(q["quadros"]) == 6, (len(q["quadros"]), r.stdout)
    assert (out / "folha.jpg").exists()
    assert q["quadros"][0]["origem"] == "abertura"


@caso("quadros: vídeo quase sem cortes cai para quadros espaçados (≥5)")
def t_quadros_espacados():
    # um pan lento por uma imagem larga: o visual muda, mas sem nenhum corte
    larga = Image.new("RGB", (2600, 640), (230, 225, 210))
    d = ImageDraw.Draw(larga)
    for i in range(13):
        d.rectangle([i * 200 + 20, 80 + (i % 3) * 120, i * 200 + 180, 560 - (i % 2) * 150], fill=CORES[i % 6])
        d.ellipse([i * 200 + 60, 40, i * 200 + 140, 120], fill=(20, 20, 20))
    larga.save(TMP / "larga.png")
    v = TMP / "lento.mp4"
    ff("-loop", "1", "-i", TMP / "larga.png", "-vf", "crop=360:640:'t*270':0,fps=30,format=yuv420p", "-t", 8, v)
    out = TMP / "quadros-lento"
    r = py(RAIZ / "scripts" / "quadros.py", v, "--n", 8, "--min", 5, "--saida", out)
    q = json.loads((out / "quadros.json").read_text())
    assert 5 <= len(q["quadros"]) <= 8, (len(q["quadros"]), r.stdout)
    assert any(x["origem"] == "espacado" for x in q["quadros"]), r.stdout


if __name__ == "__main__":
    print(f"pasta temporária: {TMP}")
    testes = [v for k, v in list(globals().items()) if k.startswith("t_") and callable(v)]
    for t in testes:
        t()
    falhas = [r for r in resultados if not r[1]]
    print(f"\n{len(resultados) - len(falhas)}/{len(resultados)} testes passaram")
    if not os.environ.get("TESTE_TMP") and not falhas:
        shutil.rmtree(TMP, ignore_errors=True)
    sys.exit(1 if falhas else 0)
