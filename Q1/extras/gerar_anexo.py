"""Gera anexo_visual_questao1.pdf (e .png): fluxo, decisão e ação numa página A4 paisagem.

Os cortes vêm de LIMIARES (q1.py), para o anexo nunca divergir do código. Fica em extras/ e grava o PDF na pasta da entrega.
Uso, na pasta Q1: .venv/bin/python extras/gerar_anexo.py
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, FancyBboxPatch, Polygon, Rectangle

ENTREGA = Path(__file__).resolve().parent.parent   # pasta Q1: q1.py e o PDF anexo
sys.path.insert(0, str(ENTREGA))
from q1 import LIMIARES as L  # noqa: E402

COR = {"cópia": "#0072B2", "versão": "#009E73", "trecho": "#CC79A7", "diferente": "#7F7F7F",
       "revisão": "#D55E00", "faixa": "#56B4E9", "fluxo": "#4D4D4D"}
FUNDO = {k: v + "2E" for k, v in COR.items()}   # mesma cor, translúcida
TINTA = "#1A1A1A"
LINHA = 0.0215                                  # altura de uma linha de corpo (fração da página)


def pct(x):
    return f"{x * 100:.0f}%"


def num(x):
    return f"{x:g}".replace(".", ",")


def caixa(ax, x, topo, w, titulo, corpo="", cor=COR["fluxo"], tracejada=False, fundo=None, tam=8.4):
    """Caixa com título e corpo; a altura sai do número de linhas. Devolve a base."""
    h = 0.040 + LINHA * (corpo.count("\n") + 1 if corpo else 0)
    ax.add_patch(FancyBboxPatch((x, topo - h), w, h, boxstyle="round,pad=0.003,rounding_size=0.006", transform=ax.transAxes,
                                facecolor=fundo or "white", edgecolor=cor, lw=1.3, ls="--" if tracejada else "-"))
    ax.text(x + 0.007, topo - 0.010, titulo, transform=ax.transAxes, fontsize=tam + 0.6, fontweight="bold", color=TINTA, va="top")
    if corpo:
        ax.text(x + 0.007, topo - 0.035, corpo, transform=ax.transAxes, fontsize=tam - 0.4, color=TINTA, va="top", linespacing=1.32)
    return topo - h


def seta(ax, x0, y0, x1, y1, cor=COR["fluxo"]):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0), xycoords="axes fraction",
                arrowprops=dict(arrowstyle="-|>", color=cor, lw=1.2, shrinkA=0, shrinkB=0))


def cilindro(ax, x, y, w, h, titulo, corpo):
    ax.add_patch(Rectangle((x, y), w, h, transform=ax.transAxes, facecolor="#F2F2F2", edgecolor=COR["fluxo"], lw=1.1))
    for yy in (y, y + h):
        ax.add_patch(Ellipse((x + w / 2, yy), w, 0.018, transform=ax.transAxes, facecolor="#F2F2F2", edgecolor=COR["fluxo"], lw=1.1))
    ax.text(x + 0.006, y + h - 0.018, titulo, transform=ax.transAxes, fontsize=8.6, fontweight="bold", va="top", color=TINTA)
    ax.text(x + 0.006, y + h - 0.060, corpo, transform=ax.transAxes, fontsize=7.8, va="top", color=TINTA, linespacing=1.3)


def titulo_painel(ax, x, texto):
    ax.text(x, 0.885, texto, transform=ax.transAxes, fontsize=11.5, fontweight="bold", color=TINTA)


# ── A. Fluxo ─────────────────────────────────────────────────────────────────
def painel_fluxo(ax, x=0.012, w=0.218):
    titulo_painel(ax, x, "A. Fluxo por documento")
    etapas = [
        ("1. Extrair e normalizar", "texto por página; cabeçalho, imagens\ne assinatura à parte; worker isolado"),
        ("2. Indexar", "hashes (bytes, texto, normalizado);\npalavras com página; sequências de\n5 palavras; citações; partes e tipo"),
        ("3. Candidatos no caso", f"hashes para cópia; todos os docs\naté ~2 mi de palavras no caso;\nacima, índice de âncoras"),
        ("4. Comparar", "alinhamento por sementes →\ndois percentuais + diff + identidade"),
        ("5. Decidir", "portão de igualdade e mapa (B)"),
    ]
    topo = 0.860
    for k, (titulo, corpo) in enumerate(etapas):
        base = caixa(ax, x, topo, w, titulo, corpo)
        if k == 0:
            ax.text(x + w / 2 + 0.008, base - 0.014, "página sem texto → OCR", transform=ax.transAxes,
                    fontsize=7.4, color=COR["revisão"], style="italic", va="center")
        if k < len(etapas) - 1:
            seta(ax, x + w / 2, base, x + w / 2, base - 0.028)
        topo = base - 0.028
    cilindro(ax, x, 0.105, 0.105, 0.135, "Histórico do\ncliente", f"≥{L.padrao_min_casos} outros casos\n= texto de modelo\n(não conta)")
    cilindro(ax, x + 0.113, 0.105, 0.105, 0.135, "Documentos\ndo caso", "a comparação\nnunca sai\ndo caso")
    ax.text(x, 0.072, "usados nas etapas 2–4", transform=ax.transAxes, fontsize=7.4, color=COR["fluxo"], style="italic")
    ax.text(x, 0.040, "assíncrono · idempotente (upload_id) ·\nem série por caso · decisão grava as versões",
            transform=ax.transAxes, fontsize=7.4, color=COR["fluxo"], va="center")


# ── B. Decisão ───────────────────────────────────────────────────────────────
def painel_decisao(ax, fig, x0=0.258, x1=0.722):
    titulo_painel(ax, x0, "B. Decisão")
    ax.text(x0, 0.852, "B1. Portão de igualdade (antes dos percentuais; vale a primeira)",
            transform=ax.transAxes, fontsize=9, fontweight="bold")
    portao = [
        ("bytes iguais", "cópia · exata", "cópia"),
        ("extração incompleta ou não confiável; página renderizada diferente", "em revisão", "revisão"),
        ("texto, cabeçalho, imagens e assinatura iguais", "cópia · exata", "cópia"),
        ("igual após normalização, ou imagem/assinatura diferente", "cópia · com ressalva", "cópia"),
        ("texto de OCR e só confusões de letras (número divergente: item a item)", "em revisão", "revisão"),
        (f"texto próprio < {L.min_shingles} sequências (mesma peça e partes: decide pelo texto inteiro)", "em revisão", "revisão"),
    ]
    for k, (cond, res, cls) in enumerate(portao):
        yy = 0.822 - k * 0.027
        ax.text(x0 + 0.004, yy, f"{k + 1}. {cond}", transform=ax.transAxes, fontsize=7.9, va="center", color=TINTA)
        ax.text(x1, yy, res, transform=ax.transAxes, fontsize=7.9, va="center", ha="right", fontweight="bold", color=COR[cls])
    ax.add_patch(FancyBboxPatch((x0 + 0.002, 0.633), x1 - x0 - 0.004, 0.030, boxstyle="round,pad=0.003", transform=ax.transAxes,
                                facecolor=FUNDO["cópia"], edgecolor=COR["cópia"], lw=1.2))
    ax.text((x0 + x1) / 2, 0.648, "Cópia só sai por igualdade. Nenhum limiar produz cópia.", transform=ax.transAxes,
            fontsize=9, fontweight="bold", ha="center", va="center", color=COR["cópia"])

    ax.text(x0, 0.600, "B2. Os dois percentuais (texto próprio = sem modelo e sem citações)",
            transform=ax.transAxes, fontsize=9, fontweight="bold")
    m = fig.add_axes([0.292, 0.135, 0.255, 0.42])
    d, inteiro, dif = L.derivacao, L.documento_inteiro, L.diferente
    regioes = [
        ("diferente", [(0, 0), (dif, 0), (dif, dif), (0, dif)]),
        ("faixa", [(dif, 0), (d, 0), (d, d), (0, d), (0, dif), (dif, dif)]),
        ("versão", [(inteiro, d), (inteiro, 1), (1, 1), (1, inteiro), (d, inteiro), (d, d)]),
        ("trecho", [(d, 0), (1, 0), (1, inteiro), (d, inteiro)]),
        ("trecho", [(0, d), (inteiro, d), (inteiro, 1), (0, 1)]),
    ]
    for cls, pts in regioes:
        m.add_patch(Polygon(pts, closed=True, facecolor=FUNDO[cls], edgecolor=COR[cls], lw=1.0, hatch="//" if cls == "faixa" else None))
    for xx, yy, t, cls in [(dif / 2, dif / 2 + 0.03, "dife-\nrente", "diferente"), ((d + dif) / 2, (d + dif) / 2 + 0.02, "faixa\nsemântica", "faixa"),
                           ((1 + d) / 2, 0.93, "versão", "versão"), ((1 + d) / 2, inteiro / 2 + 0.10, "trecho", "trecho"),
                           (inteiro / 2, (1 + d) / 2, "trecho", "trecho")]:
        m.text(xx, yy, t, ha="center", va="center", fontsize=8.8, fontweight="bold", color=COR[cls],
               bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.75))
    for xx, yy, rot in [(0.84, 0.84, "a"), (1.0, 0.25, "b"), (0.0, 0.0, "c")]:
        m.plot(xx, yy, "o", color=TINTA, ms=5, clip_on=False, zorder=5)
        m.annotate(rot, (xx, yy), (xx - 0.045 if xx > 0.5 else xx + 0.03, yy + 0.03), fontsize=8.6, fontweight="bold",
                   color=TINTA, annotation_clip=False)
    for v in sorted({dif, inteiro, d}):
        m.axvline(v, color="#BBBBBB", lw=0.5, zorder=0)
        m.axhline(v, color="#BBBBBB", lw=0.5, zorder=0)
    ticks = [0, dif, inteiro, d, 1]
    m.set_xlim(0, 1)
    m.set_ylim(0, 1)
    m.set_xticks(ticks, [pct(t) for t in ticks], fontsize=7.4)
    m.set_yticks(ticks, [pct(t) for t in ticks], fontsize=7.4)
    m.set_xlabel("% de A encontrado em B", fontsize=8.2)
    m.set_ylabel("% de B encontrado em A", fontsize=8.2)
    m.set_aspect("equal")
    ax.text(0.292, 0.060, "a: exemplo do enunciado (84% × 84%)\nb: petição dentro de autos 4× maiores (100% × 25%)\n"
                          "c: petições independentes do mesmo modelo (0% × 0%)",
            transform=ax.transAxes, fontsize=7.4, color=TINTA, va="center", linespacing=1.35)

    xr = 0.562
    legenda = [
        ("versão", f"maior ≥ {pct(d)} e menor ≥ {pct(inteiro)}:\num documento saiu do outro"),
        ("trecho", f"maior ≥ {pct(d)}, menor < {pct(inteiro)},\num documento ≥ 2× o outro:\ntrecho, se contíguo (senão,\nrevisão)"),
        ("faixa", f"maior entre {pct(dif)} e {pct(d)}: decide a\ncobertura total = literal + pará-\ngrafos reescritos (embedding,\n"
                  f"cosseno ≥ {num(L.cosseno_par)}, valor comum)\n"
                  f"≥ {pct(L.cobertura_versao)} e ≥ {pct(inteiro)} → versão\n"
                  f"< {pct(L.cobertura_diferente)} mesmo com {num(L.cosseno_par_minimo)}\n  → diferente\n"
                  f"{pct(L.cobertura_diferente)}–{pct(L.cobertura_versao)} → em revisão"),
        ("diferente", f"os dois < {pct(dif)}: só vocabulário\nou modelo em comum (citação\nexplícita vira o vínculo \"cita\")"),
    ]
    yy = 0.585
    for cls, texto in legenda:
        ax.add_patch(Rectangle((xr, yy - 0.015), 0.009, 0.015, transform=ax.transAxes, facecolor=COR[cls], edgecolor="none"))
        ax.text(xr + 0.014, yy, texto, transform=ax.transAxes, fontsize=7.6, va="top", color=TINTA, linespacing=1.3)
        yy -= 0.012 + 0.0205 * (texto.count("\n") + 1)
    ax.text(xr, yy - 0.004, "B3. Versão de quê?", transform=ax.transAxes, fontsize=9, fontweight="bold")
    for k, (cond, res) in enumerate([("tipo de peça diferente", "outra peça do caso"),
                                     ("outras partes (CPF) ou processo", "outra instância do modelo"),
                                     ("mesmo tipo, partes e processo", "mesma peça (substitui)")]):
        base = yy - 0.030 - k * 0.037
        ax.text(xr, base, cond, transform=ax.transAxes, fontsize=7.6, va="center", color=TINTA)
        ax.text(xr + 0.008, base - 0.018, "→ " + res, transform=ax.transAxes, fontsize=7.6, va="center", fontweight="bold", color=COR["versão"])


# ── C. Ação ──────────────────────────────────────────────────────────────────
def painel_acao(ax, x0=0.744, w=0.246):
    titulo_painel(ax, x0, "C. Ação por resultado")
    cartoes = [
        ("cópia", "Cópia", "agrupa · avisa \"já existe\" · reaproveita\nas análises · não apaga nada"),
        ("versão", "Versão · mesma peça", "liga à anterior · diff com página ·\nalerta de valor, data, CPF, negação"),
        ("versão", "Versão · outra peça ou instância", "vínculo · não substitui"),
        ("trecho", "Trecho", "\"contém, págs. x–y\""),
        ("diferente", "Diferente", "vínculo \"cita\" ou \"reaproveita trechos\""),
        ("revisão", "Em revisão", "1 item de fila por documento, com\nos motivos · o revisor escolhe a classe"),
    ]
    topo = 0.860
    for cls, titulo, corpo in cartoes:
        topo = caixa(ax, x0, topo, w, titulo, corpo, cor=COR[cls], fundo=FUNDO[cls]) - 0.011
    seta(ax, x0 + w / 2, topo + 0.011, x0 + w / 2, topo - 0.014, cor=COR["revisão"])
    caixa(ax, x0, topo - 0.014, w, "Calibração", "decisões do revisor + auditoria aleatória\nde 1% das automáticas → rótulos → cortes",
          cor=COR["revisão"])
    caixa(ax, x0, 0.205, 0.119, "LLM (opcional)", "resume os trechos\nalterados · pseudo-\nnimizado · nunca\ndecide a classe",
          tracejada=True, tam=8.0)
    caixa(ax, x0 + 0.127, 0.205, 0.119, "Cache", "por parágrafo: uma\nnova versão paga\nsó o que mudou", tam=8.0)


def main(caminho=ENTREGA / "anexo_visual_questao1.pdf", png=None):
    fig = plt.figure(figsize=(11.69, 8.27))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    fig.text(0.012, 0.962, "Questão 1 — Comparação de documentos parecidos", fontsize=15, fontweight="bold", color=TINTA)
    fig.text(0.012, 0.930, "Cada documento novo é comparado com os do mesmo caso: quanto do texto próprio de cada um está escrito igual "
                           "no outro, nos dois sentidos.\nVocabulário jurídico, texto de modelo do escritório e citações não contam.",
             fontsize=9.2, color=COR["fluxo"], va="center", linespacing=1.35)
    for x in (0.243, 0.735):
        ax.plot([x, x], [0.03, 0.90], color="#DDDDDD", lw=1, transform=ax.transAxes)
    painel_fluxo(ax)
    painel_decisao(ax, fig)
    painel_acao(ax)
    fig.savefig(caminho)
    if png:
        fig.savefig(png, dpi=110)
    print("gerado:", caminho)


if __name__ == "__main__":
    main()
