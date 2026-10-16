"""Gera anexo_visual_questao2.pdf: o caminho de uma sentença nova, exatamente como descrito em questao2.md.

Uso, na pasta Q2: .venv/bin/python extras/gerar_anexo.py [png_de_conferencia]
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
X0, X1 = 0, 180
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


def tabela(ax, topo, titulo, linhas):
    """Título e linhas (cor, rótulo, textos), como o registro no caso da Q1; devolve o y de baixo."""
    ax.text(10, topo + 3, titulo, ha="left", va="center", fontsize=11.5, weight="bold", color=TINTA)
    xl, wl, wt = 10, 22, 166 - 32
    y = topo
    for cor, classe, textos in linhas:
        h = 3.6 + LINHA * len(textos)
        caixa(ax, xl + wl / 2, y - h / 2, wl, h, cor, classe, 10.5, "bold")
        ax.add_patch(Rectangle((xl + wl, y - h), wt, h, facecolor=BRANCO, edgecolor=TINTA, lw=1.6, zorder=2))
        for k, t in enumerate(textos):
            ax.text(xl + wl + 2, y - 3.3 - LINHA * k, t, ha="left", va="center", fontsize=10, color=TINTA, zorder=3)
        y -= h + 1.5
    return y


def secao(ax, y, texto):
    ax.text(10, y, texto, ha="left", va="center", fontsize=13, weight="bold", color=TINTA)


def cartao(ax, topo):
    """Saída estruturada: o trecho destacado na página e os campos do JSON que apontam para ele."""
    secao(ax, topo, "Saída estruturada: um argumento gravado (o trecho é o texto do parágrafo, nunca reescrito)")
    # página do PDF
    px, pw, ptopo, ph = 10, 58, topo - 6, 74
    ax.add_patch(Rectangle((px, ptopo - ph), pw, ph, facecolor=BRANCO, edgecolor=TINTA, lw=1.6, zorder=2))
    ax.text(px + pw - 2, ptopo - 3, "pág. 7", ha="right", va="center", fontsize=9, color=NOTA, zorder=3)
    y = ptopo - 9
    destaque = None
    for par, n, marca in [(31, 4, None), (32, 3, "Dos danos morais"), (33, 5, "trecho"), (34, 4, None)]:
        ax.text(px + 2, y, f"§{par}", ha="left", va="center", fontsize=9, weight="bold", color=NOTA, zorder=3)
        if marca == "Dos danos morais":
            ax.text(px + 9, y, "Dos danos morais", ha="left", va="center", fontsize=9, weight="bold", color=TINTA, zorder=3)
            y -= 6
            n -= 1
        for k in range(n):
            fim = px + pw - 4 - (12 if k == n - 1 else 0)
            if marca == "trecho":
                if destaque is None:
                    destaque = y + 1.6
                ax.add_patch(Rectangle((px + 8.5, y - 1.6), fim - px - 8.5, 3.2, facecolor=AMARELO, edgecolor="none", zorder=2.5))
            ax.plot([px + 9, fim], [y, y], color="#9A9A9A", lw=2.2, zorder=3, solid_capstyle="round")
            y -= 3.4
        y -= 3.5
    ax.add_patch(Rectangle((px + 8, destaque - 5 * 3.4 - 0.2), pw - 11, 5 * 3.4 + 0.4, facecolor="none", edgecolor=TINTA, lw=1.2,
                           ls=(0, (3, 2)), zorder=3))
    campos = [
        ("tipo", "categoria dano_moral_presumido_negativacao (só valores da taxonomia)"),
        ("título", "Dano moral presumido na negativação indevida"),
        ("resumo", "descrição da categoria: \"a inscrição indevida gera dano moral sem prova do abalo\""),
        ("fundamentos", "art. 14 do CDC · art. 43 do CDC (extraídos por regra no código, sem modelo)"),
        ("pedido", "danos morais (da lista de pedidos) · procedente · os dois null se for preliminar"),
        ("papel · lado", "razão de decidir (os principais argumentos) · favorece o autor (listas fixas)"),
        ("trecho", "§33, pág. 7, caracteres 18420–18733, retângulos e o texto do parágrafo"),
        ("confiança", "argumento 0,99 · categoria 0,96 · pedido 0,98 · papel 0,91 · favorece 0,97"),
        ("status", "publicado · origem: jev"),
        ("versões", "schema · taxonomia · classificador · limiares · OCR · código"),
        ("documento", "cliente, caso e documento · hash (evita processar duas vezes) · juiz · vara · data"),
    ]
    cx0, yc = 76, topo - 9
    for nome, valor in campos:
        ax.text(cx0, yc, nome, ha="left", va="center", fontsize=10, weight="bold", color=TINTA)
        ax.text(cx0 + 21, yc, valor, ha="left", va="center", fontsize=9.5, color=TINTA)
        if nome == "trecho":
            meio = destaque - 2.5 * 3.4
            seta(ax, [(cx0 - 1, yc), (px + pw + 3, yc), (px + pw + 3, meio), (px + pw - 3, meio)])
        yc -= 6.6
    return min(ptopo - ph, yc)


def main():
    pdf = ENTREGA / "anexo_visual_questao2.pdf"
    png = sys.argv[1] if len(sys.argv) > 1 else None
    fig = plt.figure()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    TOPO = 700
    xa, wa = 30, 80               # coluna principal: x de 30 a 110
    cx = xa + wa / 2
    xb, wb = 118, 58              # coluna da direita
    cxb = xb + wb / 2

    # Premissas e ideia
    fim = passo(ax, 10, TOPO - 4, 166, "Premissas", [
        "1- num mesmo tipo de processo, os argumentos dos juízes se repetem: não são infinitos",
        "2- a sentença tem relatório, fundamentação (onde estão os argumentos do juiz) e dispositivo, separados por frases fixas",
        "3- a plataforma já tem sentenças de cada tipo de processo",
        "4- o Jev decide: recebe um texto e perguntas fechadas e devolve a probabilidade de cada resposta"])
    rotulo(ax, 10, fim - 4, "A solução: em vez de um LLM escrever os argumentos, o Jev classifica os parágrafos da fundamentação "
                            "numa lista fechada de tipos de argumento (a taxonomia)")

    # Montagem da taxonomia
    y = fim - 13
    secao(ax, y, "Montagem da taxonomia (por tipo de processo)")
    ysrc = y - 8
    caixa(ax, cx, ysrc, 56, 6.5, AZUL, "Sentenças já na plataforma", 11, "bold")
    seta(ax, [(cx, ysrc - 3.25), (cx, ysrc - 7.25)])
    topo_m1 = ysrc - 7.25
    fim = passo(ax, xa, topo_m1, wa, "1- Agrupar os parágrafos e nomear os grupos", [
        "parágrafos da fundamentação, sem as citações",
        "nomes, valores, datas e empresas mascarados, para agrupar pelo",
        "    argumento do juiz, e não pelos fatos do caso",
        "os parágrafos viram embeddings e são agrupados",
        "um LLM lê exemplos de cada grupo e escreve o nome e a descrição",
        "    da categoria"])
    passo(ax, xb, topo_m1, wb, "De onde vem cada lista", [
        "tipo de processo: classe + assunto da sentença",
        "taxonomia geral: argumentos de qualquer",
        "    processo (prescrição, competência)",
        "tipo com poucas sentenças: usa só a geral",
        "lista de pedidos: montada do mesmo jeito",
        "    pedido = o que o autor pediu ao juiz",
        "    (danos morais, exclusão do cadastro)"])
    seta(ax, [(cx, fim), (cx, fim - 4)])
    fim = passo(ax, xa, fim - 4, wa, "2- Advogados revisam", [
        "revisam a categoria dos parágrafos de um lote de sentenças",
        "    e corrigem a lista: tudo o que o LLM escreveu é revisado",
        "esse lote é o gabarito de ajuste"])
    seta(ax, [(cx, fim), (cx, fim - 4)])
    topo_m3 = fim - 4
    fim_m3 = passo(ax, xa, topo_m3, wa, "3- Teste: o Jev classifica o gabarito", [
        "usa as descrições das categorias como opções"])
    seta(ax, [(cx, fim_m3), (cx, fim_m3 - 3)])
    yl = fim_m3 - 3 - 7
    losango(ax, cx, yl, 50, 14, "uma categoria erra\nmuito no gabarito?")
    seta(ax, [(cx + 25, yl), (xb, yl)])
    rotulo(ax, cx + 27, yl + 1.8, "sim")
    caixa(ax, cxb, yl, wb, 9, AMARELO, "os advogados reescrevem\na descrição dela", 9.5)
    seta(ax, [(cxb, yl + 4.5), (cxb, (topo_m3 + fim_m3) / 2), (xa + wa, (topo_m3 + fim_m3) / 2)], tracejada=True)
    rotulo(ax, cxb + 1.5, yl + 8, "testa de novo")
    seta(ax, [(cx, yl - 7), (cx, yl - 11)])
    rotulo(ax, cx + 1.5, yl - 9, "não")
    ytax = yl - 11 - 4
    caixa(ax, cx, ytax, 64, 8, VERDE, "Taxonomia do tipo + taxonomia geral\n+ lista de pedidos", 10.5, "bold")
    rotulo(ax, cx + 34, ytax, "→ são as opções do Jev nas etapas 1 e 2")

    # Extração
    y = ytax - 13
    secao(ax, y, "Extração de uma sentença nova")
    ys = y - 8
    caixa(ax, cx, ys, 40, 6.5, AZUL, "Sentença nova", 12, "bold")
    seta(ax, [(cx, ys - 3.25), (cx, ys - 7.25)])
    fim = passo(ax, xa, ys - 7.25, wa, "Ler o PDF página a página", ["página escaneada vai para OCR"])
    passo(ax, xb, ys - 7.25, wb, "Sentenças longas (etapas 1 e 2)", [
        "a sentença nunca vai inteira ao Jev",
        "cada chamada: um parágrafo, o anterior",
        "    e o título da seção",
        "sentença longa = só mais chamadas",
        "argumento espalhado → remontado na etapa 3"])
    seta(ax, [(cx, fim), (cx, fim - 4)])
    fim = passo(ax, xa, fim - 4, wa, "Preparar a sentença (código)", [
        "1- divide em parágrafos numerados, com página e posição no PDF",
        "2- separa relatório, fundamentação e dispositivo pelas frases fixas",
        "    (\"Fundamento e decido\", \"Ante o exposto\")",
        "3- marca as citações (ementa, trecho entre aspas): não são do juiz;",
        "    súmulas, artigos e precedentes vão para o argumento vizinho"])
    seta(ax, [(cx, fim), (cx, fim - 3)])
    yf = fim - 3 - 7
    losango(ax, cx, yf, 50, 14, "as frases fixas\naparecem?")
    seta(ax, [(cx + 25, yf), (xb, yf)])
    rotulo(ax, cx + 27, yf + 1.8, "não")
    topo_j = yf + 7
    fim_j = passo(ax, xb, topo_j, wb, "O Jev separa as partes", [
        "classifica cada parágrafo: relatório,",
        "    fundamentação ou dispositivo",
        "abaixo da probabilidade mínima → revisão"], LARANJA)
    yj = yf - 11
    seta(ax, [(cx, yf - 7), (cx, yj)])
    rotulo(ax, cx + 1.5, yf - 9, "sim")
    seta(ax, [(xb + 8, fim_j), (xb + 8, yj), (cx + 1, yj)], tracejada=True)
    rotulo(ax, xb + 9.5, (fim_j + yj) / 2, "acima do mínimo")

    # Relatório, fundamentação, dispositivo
    yp = yj - 12
    partes = [(30, ROSA, "Relatório"), (cx, VERDE, "Fundamentação"), (cxb, LILAS, "Dispositivo")]
    for x, cor, nome in partes:
        caixa(ax, x, yp, 30, 6, cor, nome)
        ramo(ax, (cx, yj), (x, yp + 3))
    rotulo(ax, 30, yp - 6, "argumentos das partes:", ha="center")
    rotulo(ax, 30, yp - 9, "não é classificado", ha="center")
    rotulo(ax, cx + 2, yp - 6, "argumentos do juiz")
    rotulo(ax, cxb + 2, yp - 6, "onde o juiz decide cada pedido")

    # Etapas 1 e 2
    topo_e = yp - 3 - 9
    seta(ax, [(cx, yp - 3), (cx, topo_e)])
    seta(ax, [(cxb, yp - 3), (cxb, topo_e)])
    fim2 = passo(ax, xa, topo_e, wa, "Etapa 2: argumentos (Jev), um parágrafo por vez", [
        "entrada: o parágrafo + o anterior + o título da seção",
        "    (\"Dos danos morais\"); opções: as categorias da taxonomia",
        "1ª chamada: é argumento do juiz? e, para cada categoria, sim ou não:",
        "    o parágrafo traz este argumento? (pode trazer mais de um)",
        "    nenhuma categoria passa da probabilidade mínima → \"outro\"",
        "2ª chamada, para cada argumento achado:",
        "    qual pedido sustenta (ou nenhum, se for preliminar)?",
        "    razão de decidir ou comentário de passagem?",
        "    favorece o autor ou o réu?"])
    fim1 = passo(ax, xb, topo_e, wb, "Etapa 1: pedidos (Jev)", [
        "para cada pedido da lista de pedidos:",
        "    o dispositivo o decide? com qual resultado?",
        "    procedente · parcialmente procedente ·",
        "    improcedente · extinto sem mérito",
        "+ sim ou não: decide pedido fora da lista?",
        "    sim → revisão"])

    # Etapa 3
    seta(ax, [(cx, fim2), (cx, fim2 - 4)])
    topo3 = fim2 - 4
    fim3 = passo(ax, xa, topo3, wa, "Etapa 3: juntar (código)", [
        "junta parágrafos vizinhos com a mesma categoria e o mesmo pedido",
        "o argumento juntado fica com a menor confiança entre eles",
        "lado ≠ resultado do pedido (procedente ou improcedente) → revisão"])
    yr = topo3 - 6
    seta(ax, [(cxb, fim1), (cxb, yr), (xa + wa, yr)])
    rotulo(ax, cxb + 1.5, (fim1 + yr) / 2, "resultado de cada pedido")

    # Etapa 4
    seta(ax, [(cx, fim3), (cx, fim3 - 4)])
    topo4 = fim3 - 4
    fim4 = passo(ax, xa, topo4, wa, "Etapa 4: decidir pela probabilidade mínima", [
        "cada pergunta tem a sua probabilidade mínima (se preciso, por categoria)",
        "as 5 respostas passam (é argumento, categoria, pedido, papel, lado)",
        "    → publicado",
        "\"não é argumento do juiz\" com confiança → descartado",
        "    (uma amostra fixa dos descartados vai para revisão)",
        "categoria com poucos exemplos no gabarito → revisão, até ter exemplos",
        "o resto, e todo \"outro\" → revisão"])
    topo_p = topo4
    fim_p = passo(ax, xb, topo_p, wb, "Como a probabilidade mínima é escolhida", [
        "ajuste: só no gabarito de ajuste,",
        "    de novo a cada versão",
        "meta: vem do gabarito de avaliação, a",
        "    concordância entre 2 advogados",
        "escolhe a menor que ainda alcança a meta",
        "acerto medido no argumento inteiro,",
        "    e não em cada resposta"], AMARELO)
    seta(ax, [(xb, (topo_p + fim_p) / 2), (xa + wa, (topo_p + fim_p) / 2)], tracejada=True)

    # Registro
    topo_r = min(fim4, fim_p) - 15
    barra = topo_r + 7
    ax.plot([10, 166], [barra, barra], color=SETA, lw=2.2, zorder=1)
    seta(ax, [(cx, fim4), (cx, barra)])
    y = tabela(ax, topo_r, "Registro na base (nada é apagado)", [
        (VERDE, "Publicado", ["entra na base com o trecho destacado no PDF · status publicado · origem jev"]),
        (LARANJA, "Revisão", ["chega de: partes não separadas · pedido fora da lista · lado ≠ resultado · abaixo do mínimo ·",
                              "    \"outro\" · categoria com poucos exemplos · amostra dos descartados",
                              "o revisor vê o trecho destacado no PDF e aceita · corrige · rejeita · marca um trecho que faltou",
                              "cada ação é um registro novo, sem apagar o original, e muda o status (em revisão, publicado,",
                              "    rejeitado ou corrigido) e a origem (jev ou advogado)",
                              "\"outro\" acumulados voltam aos passos 1 e 2 da montagem e viram categorias novas, com gabarito próprio"]),
        (CINZA, "Descartado", ["não é argumento do juiz: não chega à base"]),
    ])
    y_rev = topo_r - 4.9 - 1.5 - (3.6 + LINHA * 6) / 2
    seta(ax, [(166, y_rev), (178, y_rev), (178, ysrc), (cx + 28, ysrc)], tracejada=True)
    rotulo(ax, cx + 31, ysrc + 1.8, "\"outro\" acumulados voltam à montagem (passos 1 e 2)")

    y = tabela(ax, y - 9, "Qualidade: gabarito de avaliação, todo mês em produção", [
        (AZUL, "Gabarito", ["sentenças sorteadas: dois advogados marcam os argumentos sem ver o sistema e um terceiro desempata",
                            "acerto: mesma categoria e mesmo pedido de um argumento do gabarito, com um parágrafo em comum"]),
        (VERDE, "Medidas", ["precisão e recall por categoria · o publicado acerta tanto quanto os advogados concordam?",
                            "quanto vai para revisão · erros na separação de relatório, fundamentação e dispositivo"]),
    ])
    y = tabela(ax, y - 9, "Versionamento: quando o prompt, o modelo ou o schema muda (nada é apagado)", [
        (LILAS, "Versão", ["cada argumento grava a versão do schema, da taxonomia, do classificador, das probabilidades",
                           "mínimas, do OCR e do código; as descrições da taxonomia fazem o papel do prompt do Jev"]),
        (AMARELO, "Taxonomia", ["mudança reclassifica só as categorias afetadas",
                                "troca do LLM ou do prompt da montagem → versão nova da taxonomia, revisada pelos advogados"]),
        (AZUL, "Classificador", ["troca reclassifica tudo, desde que a versão nova não fique pior no gabarito"]),
        (CINZA, "Schema", ["campo novo fica vazio nos registros antigos · campo que muda de sentido gera migração"]),
        (ROSA, "OCR", ["mudança no OCR ou na divisão em parágrafos reprocessa a sentença: a posição dos trechos muda"]),
        (VERDE, "Correções", ["a correção de um advogado prevalece sobre a reclassificação e vai para a versão nova",
                              "pelo mapeamento das categorias"]),
    ])
    y = tabela(ax, y - 9, "Argumentos inventados e trade-offs", [
        (AMARELO, "Inventados", ["o LLM só escreve na montagem (nomes e descrições), e tudo é revisado pelos advogados",
                                 "na extração nenhum modelo escreve texto; o risco que sobra, classificar errado, cai com a regra",
                                 "do JSON, a probabilidade mínima, a pergunta \"é argumento do juiz?\" e o \"outro\"",
                                 "se o classificador for um LLM (plano B): responde só números de parágrafo e opções, em saída",
                                 "    restrita; o código descarta o que não existe e recorta o trecho do documento; a confiança",
                                 "    vem da concordância entre várias respostas dele à mesma pergunta"]),
        (CINZA, "Trade-offs", ["lista fechada: base comparável e barata · argumento novo fica como \"outro\" até a revisão",
                               "fundamentos diferentes na mesma categoria têm o mesmo resumo (distinguem-se pelo trecho",
                               "    e pelos fundamentos citados) · a qualidade depende dos advogados",
                               "Jev em acesso antecipado: o versionamento permite trocá-lo (ex.: LLM com saída restrita às opções)",
                               "serviço externo: contrato de tratamento de dados com a TypeSafe; segredo de justiça não é enviado"]),
    ])

    fundo = cartao(ax, y - 8)
    Y0, Y1 = fundo - 6, TOPO
    fig.set_size_inches(13, 13 * (Y1 - Y0) / (X1 - X0))
    ax.set_xlim(X0, X1)
    ax.set_ylim(Y0, Y1)
    ax.add_patch(Rectangle((X0, Y0), X1 - X0, Y1 - Y0, facecolor=FUNDO, zorder=-2))
    for x in range(X0, X1 + 1, 10):
        ax.plot([x, x], [Y0, Y1], color=GRADE, lw=0.8, zorder=-1)
    for yy in range(int(Y0) // 10 * 10 + 8, Y1 + 1, 10):
        ax.plot([X0, X1], [yy, yy], color=GRADE, lw=0.8, zorder=-1)
    fig.savefig(pdf, facecolor=FUNDO)
    if png:
        fig.savefig(png, dpi=100, facecolor=FUNDO)
    print("gerado:", pdf)


if __name__ == "__main__":
    main()
