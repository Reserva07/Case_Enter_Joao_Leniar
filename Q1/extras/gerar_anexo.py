"""Gera anexo_visual_questao1.pdf: o fluxo de um documento novo, exatamente como descrito em questao1.md.

Uso, na pasta Q1: .venv/bin/python extras/gerar_anexo.py [png_de_conferencia]
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Polygon, Rectangle
from matplotlib.path import Path as Path_

ENTREGA = Path(__file__).resolve().parent.parent

FUNDO, GRADE, TINTA, SETA, NOTA = "#F2F2F2", "#E3E3E3", "#1A1A1A", "#333333", "#555555"
LILAS, ROSA, VERDE, AZUL = "#DCD9FA", "#F6C9C9", "#BDEBCB", "#C9DAF8"
BRANCO, CINZA, LARANJA, AMARELO = "#FFFFFF", "#E0E0E0", "#F9D7B8", "#FBEFC4"
LINHA = 3.0   # altura de uma linha de texto, em unidades do desenho
plt.rcParams["font.family"] = ["Helvetica Neue", "Arial", "DejaVu Sans"]


def caixa(ax, cx, cy, w, h, cor, texto="", tam=11, peso="normal"):
    ax.add_patch(Rectangle((cx - w / 2, cy - h / 2), w, h, facecolor=cor, edgecolor=TINTA, lw=1.6, zorder=2))
    if texto:
        ax.text(cx, cy, texto, ha="center", va="center", fontsize=tam, color=TINTA, weight=peso, zorder=3,
                linespacing=1.2)


def passo(ax, x0, topo, w, titulo, linhas, cor=BRANCO):
    """Caixa com título em negrito e uma linha por item; devolve o y de baixo."""
    h = 5.2 + LINHA * len(linhas)
    ax.add_patch(Rectangle((x0, topo - h), w, h, facecolor=cor, edgecolor=TINTA, lw=1.6, zorder=2))
    ax.text(x0 + 2, topo - 2.8, titulo, ha="left", va="center", fontsize=11.5, weight="bold", color=TINTA, zorder=3)
    for k, linha in enumerate(linhas):
        ax.text(x0 + 2, topo - 6.0 - LINHA * k, linha, ha="left", va="center", fontsize=10, color=TINTA, zorder=3)
    return topo - h


def losango(ax, cx, cy, w, h, texto):
    ax.add_patch(Polygon([(cx, cy + h / 2), (cx + w / 2, cy), (cx, cy - h / 2), (cx - w / 2, cy)],
                         facecolor=AMARELO, edgecolor=TINTA, lw=1.6, zorder=2))
    ax.text(cx, cy, texto, ha="center", va="center", fontsize=10, color=TINTA, zorder=3, linespacing=1.15)


def seta(ax, pontos, tracejada=False):
    """Seta por uma polilinha (cotovelos retos)."""
    caminho = Path_(pontos, [Path_.MOVETO] + [Path_.LINETO] * (len(pontos) - 1))
    ax.add_patch(FancyArrowPatch(path=caminho, arrowstyle="-|>,head_length=7,head_width=4.5", color=SETA, lw=1.6,
                                 linestyle=(0, (4, 3)) if tracejada else "-", zorder=1, shrinkA=0, shrinkB=0))


def ramo(ax, a, b):
    """Seta curva que sai para baixo e chega para baixo (como as do esboço)."""
    d = (a[1] - b[1]) * 0.75
    caminho = Path_([a, (a[0], a[1] - d), (b[0], b[1] + d), b], [Path_.MOVETO, Path_.CURVE4, Path_.CURVE4, Path_.CURVE4])
    ax.add_patch(FancyArrowPatch(path=caminho, arrowstyle="-|>,head_length=7,head_width=4.5", color=SETA, lw=1.6,
                                 zorder=1, shrinkA=0, shrinkB=0))


def rotulo(ax, x, y, texto, ha="left", rot=0):
    ax.text(x, y, texto, ha=ha, va="center", fontsize=10, style="italic", color=NOTA, rotation=rot, zorder=3)


def mapa(ax, fig, topo, limites):
    """Onde cada par cai: % do novo no outro × % do outro no novo, com as regiões da etapa 3."""
    X0, X1, Y0, Y1 = limites
    ax.text(10, topo - 2, "Onde cada par cai pelos dois percentuais (a cópia sai antes, pelo hash)", ha="left", va="center",
            fontsize=11.5, weight="bold", color=TINTA)
    lado, x_m, y_m = 58, 22, topo - 8 - 58          # quadrado do gráfico, em unidades do desenho
    m = fig.add_axes([(x_m - X0) / (X1 - X0), (y_m - Y0) / (Y1 - Y0), lado / (X1 - X0), lado / (Y1 - Y0)])
    m.set_facecolor(BRANCO)
    dif, inteiro, d = 20, 50, 60
    regioes = [
        (CINZA, None, [(0, 0), (dif, 0), (dif, dif), (0, dif)]),
        ("#DCE8FA", "//", [(dif, 0), (d, 0), (d, d), (0, d), (0, dif), (dif, dif)]),
        (VERDE, None, [(inteiro, d), (inteiro, 100), (100, 100), (100, inteiro), (d, inteiro), (d, d)]),
        (ROSA, None, [(d, 0), (100, 0), (100, inteiro), (d, inteiro)]),
        (ROSA, None, [(0, d), (inteiro, d), (inteiro, 100), (0, 100)]),
    ]
    for cor, hachura, pts in regioes:
        m.add_patch(Polygon(pts, closed=True, facecolor=cor, edgecolor=TINTA, lw=1.0, hatch=hachura))
    caixa_txt = dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85)
    for xx, yy, t in [(10, 13, "diferente"), (40, 40, "etapa 2\n(embedding)"), (76, 70, "versão"),
                      (80, 32, "um dentro\ndo outro"), (25, 85, "um dentro\ndo outro")]:
        m.text(xx, yy, t, ha="center", va="center", fontsize=9.5, weight="bold", color=TINTA, bbox=caixa_txt, zorder=4)
    for xx, yy, letra in [(85, 85, "a"), (100, 25, "b"), (3, 3, "c")]:
        m.plot(xx, yy, "o", color=TINTA, ms=6, clip_on=False, zorder=5)
        m.annotate(letra, (xx, yy), (xx - 5 if xx > 50 else xx + 3, yy + 3 if xx > 50 else yy - 1), fontsize=10, weight="bold", color=TINTA,
                   annotation_clip=False, zorder=5)
    ticks = [0, dif, inteiro, d, 100]
    m.set_xlim(0, 100)
    m.set_ylim(0, 100)
    m.set_xticks(ticks, [f"{t}%" for t in ticks], fontsize=9)
    m.set_yticks(ticks, [f"{t}%" for t in ticks], fontsize=9)
    m.set_xlabel("% do texto \"caso\" do novo que está no outro", fontsize=10)
    m.set_ylabel("% do texto \"caso\" do outro que está no novo", fontsize=10)

    xr, yy = 92, topo - 9
    legenda = [
        (VERDE, None, "versão", ["um ≥ 60% e o outro ≥ 50%"]),
        (ROSA, None, "um dentro do outro", ["um ≥ 60% e o outro < 50%, com um documento", "pelo menos 2× maior que o outro",
                                            "(maior < 2× o menor → etapa 2)",
                                            "é cópia se o menor estiver inteiro no maior; senão, versão"]),
        ("#DCE8FA", "//", "etapa 2 (embedding)", ["maior de 20% até < 60%: soma os parágrafos",
                                                  "reescritos aos dois percentuais",
                                                  "≥ 65% e ≥ 50% → versão",
                                                  "os dois < 55% → diferente",
                                                  "o resto → juiz LLM"]),
        (CINZA, None, "diferente", ["os dois < 20%"]),
    ]
    for cor, hachura, titulo, linhas in legenda:
        ax.add_patch(Rectangle((xr, yy - 1.6), 4, 3.2, facecolor=cor, edgecolor=TINTA, lw=1.0, hatch=hachura, zorder=2))
        ax.text(xr + 6, yy, titulo, ha="left", va="center", fontsize=10.5, weight="bold", color=TINTA)
        for k, t in enumerate(linhas):
            ax.text(xr + 6, yy - LINHA * (k + 1), t, ha="left", va="center", fontsize=10, color=TINTA)
        yy -= LINHA * (len(linhas) + 1) + 3
    for k, t in enumerate(["a: petição com 3 de 20 parágrafos trocados e o valor alterado (≈ 85% × 85%)",
                           "b: petição juntada dentro de autos 4× maiores (100% × 25%)",
                           "c: contestação × inicial do mesmo caso (perto de 0% × 0%)"]):
        ax.text(10, y_m - 14 - LINHA * k, t, ha="left", va="center", fontsize=10, color=TINTA)


def main():
    pdf = ENTREGA / "anexo_visual_questao1.pdf"
    png = sys.argv[1] if len(sys.argv) > 1 else None
    X0, X1, Y0, Y1 = 0, 180, -120, 262
    fig = plt.figure(figsize=(13, 13 * (Y1 - Y0) / (X1 - X0)))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(X0, X1)
    ax.set_ylim(Y0, Y1)
    ax.axis("off")
    ax.add_patch(Rectangle((X0, Y0), X1 - X0, Y1 - Y0, facecolor=FUNDO, zorder=-2))
    for x in range(X0, X1 + 1, 10):
        ax.plot([x, x], [Y0, Y1], color=GRADE, lw=0.8, zorder=-1)
    for y in range(Y0 + 8, Y1 + 1, 10):
        ax.plot([X0, X1], [y, y], color=GRADE, lw=0.8, zorder=-1)

    # Cliente → casos → documentos do caso + documento novo
    caixa(ax, 48, 254, 20, 6.5, LILAS, "Cliente", 12)
    casos = [18, 38, 58, 78, 98]
    for k, x in enumerate(casos, 1):
        caixa(ax, x, 238, 15, 6, ROSA, f"Caso {k}")
        ramo(ax, (48, 250.75), (x, 241))
    docs = [98, 116, 134]
    for k, x in enumerate(docs, 1):
        caixa(ax, x, 222, 14, 6, VERDE, f"Doc {k}")
        ramo(ax, (98, 235), (x, 225))
    ax.text(146, 222, "···", ha="center", va="center", fontsize=20, color=TINTA, weight="bold")
    ax.text(155, 222.3, "+", ha="center", va="center", fontsize=26, color=TINTA)
    caixa(ax, 168, 222, 18, 6, AZUL, "Doc Novo", 11, "bold")
    ax.plot([10.5, 85.5], [233.5, 233.5], color=SETA, lw=1.2, zorder=1)
    for x in (10.5, 85.5):
        ax.plot([x, x], [233.5, 234.8], color=SETA, lw=1.2, zorder=1)
    rotulo(ax, 48, 231, "outros casos do cliente", ha="center")

    # Coluna principal
    xa, wa = 30, 80               # caixas da coluna principal: x de 30 a 110
    cx = xa + wa / 2
    seta(ax, [(168, 219), (168, 214), (cx, 214), (cx, 210)])
    fim = passo(ax, xa, 210, wa, "Ler o PDF página a página", ["página escaneada vai para OCR"])
    seta(ax, [(xa + wa, (210 + fim) / 2), (120, (210 + fim) / 2)])
    caixa(ax, 148, (210 + fim) / 2, 56, 7, LARANJA, "página que não pôde ser lida → revisão humana", 9.5)
    seta(ax, [(cx, fim), (cx, fim - 4)])
    fim = passo(ax, xa, fim - 4, wa, "Extrair três coisas", [
        "1- hashes: arquivo, texto, texto normalizado, imagens, assinatura",
        "2- palavras em grupos de 5 seguidas, com a página",
        "3- partes (CPF/CNPJ), processo e tipo de peça"])
    seta(ax, [(cx, fim), (cx, fim - 4)])
    topo_et = fim - 4
    fim = passo(ax, xa, topo_et, wa, "Etiquetar cada grupo de 5 palavras", [
        "modelo: igual em ≥ 5 outros casos do cliente",
        "citação: entre aspas ou depois de \"in verbis\"",
        "caso: o resto; é o que conta na comparação"])
    meio_et = (topo_et + fim) / 2
    seta(ax, [(15, 233.5), (15, meio_et), (xa, meio_et)], tracejada=True)
    rotulo(ax, 12.5, (233.5 + meio_et) / 2, "grupos de palavras dos outros casos (só para etiquetar)", ha="center", rot=90)
    seta(ax, [(cx, fim), (cx, fim - 4)])
    topo_cmp = fim - 4
    fim = passo(ax, xa, topo_cmp, wa, "Comparar com cada doc do mesmo caso", [])
    meio_cmp = (topo_cmp + fim) / 2
    seta(ax, [(116, 219), (116, meio_cmp), (xa + wa, meio_cmp)], tracejada=True)
    rotulo(ax, 118.5, (219 + meio_cmp) / 2 + 6, "um de cada vez", rot=90)

    # Hashes iguais?
    seta(ax, [(cx, fim), (cx, fim - 3)])
    yh = fim - 3 - 6
    losango(ax, cx, yh, 44, 12, "hashes\niguais?")
    seta(ax, [(cx + 22, yh), (123, yh)])
    rotulo(ax, cx + 24, yh + 1.8, "sim")
    caixa(ax, 150, yh, 54, 16, AZUL, "Cópia; a comparação com esse doc termina\narquivo igual, ou texto, imagens e\nassinatura iguais → exata\ntexto igual com imagem ou assinatura diferente,\nou só o normalizado igual → com ressalva", 9.5)

    # Etapa 1
    seta(ax, [(cx, yh - 6), (cx, yh - 10)])
    rotulo(ax, cx + 1.5, yh - 8, "não")
    topo1 = yh - 10
    fim = passo(ax, xa, topo1, wa, "Etapa 1: semelhança de texto", [
        "trecho igual: palavras seguidas idênticas, na mesma ordem",
        "conta só texto \"caso\"; trecho vale com ≥ 15 palavras",
        "dois percentuais: % do novo no outro e % do outro no novo"])
    seta(ax, [(xa + wa, (topo1 + fim) / 2), (120, (topo1 + fim) / 2)])
    caixa(ax, 148, (topo1 + fim) / 2, 56, 10, LARANJA, "texto de OCR com só trocas de leitura\nou número divergente → revisão humana", 9.5)

    # Maior percentual entre 20% e 60%?
    seta(ax, [(cx, fim), (cx, fim - 3)])
    yd = fim - 3 - 10
    losango(ax, cx, yd, 64, 20, "maior % de 20% até < 60%,\nou um ≥ 60% e o outro < 50%\ncom o maior < 2× o menor?")
    # não → decide pelos percentuais da etapa 1
    seta(ax, [(cx, yd - 10), (cx, yd - 14)])
    rotulo(ax, cx + 1.5, yd - 12, "não")
    topo3a = yd - 14
    fim3a = passo(ax, xa, topo3a, wa, "Etapa 3: decidir pelos dois percentuais", [
        "um ≥ 60% e o outro ≥ 50% → versão",
        "um ≥ 60%, o outro < 50% e um doc ≥ 2× o outro",
        "    → um dentro do outro (espalhado → juiz)",
        "os dois < 20% → diferente",
        "cliente com < 20 casos: versão só com os dois ≥ 90%",
        "< 10 grupos \"caso\": texto inteiro, se mesma peça",
        "o resto → juiz LLM"])
    # sim → etapa 2 → decide pelos percentuais somados
    xb, wb = 118, 58
    seta(ax, [(cx + 32, yd), (xb, yd)])
    rotulo(ax, cx + 33, yd + 1.8, "sim")
    topo2 = yd + 9
    fim2 = passo(ax, xb, topo2, wb, "Etapa 2: semelhança de sentido", [
        "embedding nos parágrafos sem trecho igual",
        "reescrito = cosseno ≥ 0,875",
        "    e mesmos valores e datas",
        "soma aos dois percentuais"])
    seta(ax, [(xb + wb / 2, fim2), (xb + wb / 2, fim2 - 4)])
    fim3b = passo(ax, xb, fim2 - 4, wb, "Etapa 3: decidir (% somados)", [
        "um ≥ 65% e o outro ≥ 50% → versão",
        "os dois < 55%, mesmo com cosseno ≥ 0,725",
        "    → diferente",
        "cliente com < 20 casos: versão → juiz LLM",
        "qualquer outra combinação → juiz LLM"])
    seta(ax, [(xb + wb / 2, fim3b), (xb + wb / 2, fim3b - 4)])
    topo_juiz = fim3b - 4
    fim3b = passo(ax, xb, topo_juiz, wb, "Juiz LLM", [
        "recebe os parágrafos sem trecho igual (nomes",
        "    e CPF mascarados), os dois % e onde ficam",
        "    os trechos iguais",
        "\"B é A editado ou outro documento?\"",
        "3 respostas iguais → versão ou diferente",
        "divergência ou \"incerto\" → revisão"], AMARELO)

    # Etapa 3 da esquerda: o resto vai ao juiz
    meio_juiz = (topo_juiz + fim3b) / 2
    seta(ax, [(xa + wa, fim3a + 3.5), (114, fim3a + 3.5), (114, meio_juiz), (xb, meio_juiz)])

    # Registro no caso: as setas chegam numa barra acima da tabela
    topo_r = min(fim3a, fim3b) - 13
    barra = topo_r + 7
    ax.plot([10, 166], [barra, barra], color=SETA, lw=2.2, zorder=1)
    seta(ax, [(cx, fim3a), (cx, barra)])
    seta(ax, [(xb + wb / 2, fim3b), (xb + wb / 2, barra)])
    seta(ax, [(176, yh), (178, yh), (178, barra), (166, barra)])
    ax.text(10, topo_r + 3, "Registro no caso (nada é apagado)", ha="left", va="center", fontsize=11.5, weight="bold",
            color=TINTA)
    linhas = [
        (AZUL, "Cópia", ["exata ou com ressalva; marcada como cópia e ligada à original"]),
        (VERDE, "Versão", ["tipo de peça, partes e processo iguais → mesma peça: as duas no mesmo grupo de versões",
                           "tipo de peça diferente → versão de outra peça do caso: as duas só ficam ligadas",
                           "partes ou processo diferentes → mesmo modelo em outro processo: só ligadas, com aviso",
                           "tipo de peça não lido → ligada como versão, sem afirmar que substitui",
                           "versão de mais de um doc → ligada a todos; atual = a mais recente pela data de protocolo (sem data, não se afirma)",
                           "registra onde estão as diferenças: parágrafos novos, removidos e palavras trocadas, com a página"]),
        (ROSA, "Um dentro\ndo outro", ["cópia, se o menor estiver inteiro, palavra por palavra (todo o texto), no maior; senão, versão", "ligado ao outro, com as páginas onde está"]),
        (CINZA, "Diferente", ["sem ligação"]),
        (LARANJA, "Revisão", ["juiz LLM sem 3 respostas iguais ou \"incerto\"; OCR com só trocas de leitura (provável cópia) ou com número", "diferente; página que não pôde ser lida → fila de um revisor, que escolhe uma das três classes"]),
    ]
    xl, wl, wt = 10, 22, 166 - 32
    y = topo_r
    for cor, classe, textos in linhas:
        h = 3.6 + LINHA * len(textos)
        caixa(ax, xl + wl / 2, y - h / 2, wl, h, cor, classe, 10.5, "bold")
        ax.add_patch(Rectangle((xl + wl, y - h), wt, h, facecolor=BRANCO, edgecolor=TINTA, lw=1.6, zorder=2))
        for k, t in enumerate(textos):
            ax.text(xl + wl + 2, y - 3.3 - LINHA * k, t, ha="left", va="center", fontsize=10, color=TINTA, zorder=3)
        y -= h + 1.5

    mapa(ax, fig, y - 4, (X0, X1, Y0, Y1))
    fig.savefig(pdf, facecolor=FUNDO)
    if png:
        fig.savefig(png, dpi=100, facecolor=FUNDO)
    print("gerado:", pdf)


if __name__ == "__main__":
    main()
