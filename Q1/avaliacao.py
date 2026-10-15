"""Questão 1 — avaliação: conjuntos de calibração e teste, calibração dos cortes semânticos, métricas, baselines por
ablação, custo e latência. Usa a solução (q1.py) e os dados sintéticos (sinteticos.py)."""
import json
import math
import random
import re
import time
import unicodedata
from collections import Counter, defaultdict
from dataclasses import replace
from pathlib import Path

import numpy as np

from q1 import *
from sinteticos import *


# ── Baseline: cosseno de palavras do documento inteiro ────────────────────
def cosseno_palavras(texto_a, texto_b):
    va, vb = Counter(palavras(normalizar(texto_a))), Counter(palavras(normalizar(texto_b)))
    produto = sum(va[t] * vb[t] for t in va)
    return produto / (math.sqrt(sum(x * x for x in va.values())) * math.sqrt(sum(x * x for x in vb.values())))


# ── 5.1 Modelos com variação: quanto o histórico reconhece ────────────────
def reconhecimento(pecas, docs):
    """% das palavras de parágrafos de modelo reconhecidas como modelo, e % das palavras de fatos marcadas como modelo (erro)."""
    contagem = Counter()
    for peca, doc in zip(pecas, docs):
        assert len(doc.paragrafos) == len(peca.paragrafos)
        for origem, indices in (("modelo", peca.modelo), ("fatos", peca.fatos)):
            for k in indices:
                p = doc.paragrafos[k]
                contagem[origem] += p.p1 - p.p0
                contagem[origem + " como modelo"] += sum(not e for e in doc.especifica[p.p0:p.p1])
    return contagem["modelo como modelo"] / contagem["modelo"], contagem["fatos como modelo"] / contagem["fatos"]


# ── 10.1 Conjuntos de calibração e teste ────────────────────
def gerar_pares(seed, n, n_massa=0):
    """`n` pares com a mistura de classes abaixo, mais `n_massa` pares de petições de massa (gerados com outra seed, depois)."""
    rng = random.Random(seed)
    pares = []
    pesos = {"cópia": 0.10, "cópia com ressalva": 0.15, "versão": 0.50, "diferente": 0.25}
    for _ in range(n):
        verdade = rng.choices(list(pesos), weights=list(pesos.values()))[0]
        peca = gerar_peca(rng, n_fatos=(4, 7))
        paragrafos, fatos = peca.paragrafos, peca.fatos
        A, extra = "\n".join(paragrafos), {}
        if verdade == "cópia":
            tipo = rng.choice(["bytes iguais", "texto igual, outro arquivo", "extração falhou", "embutida (trecho idêntico)", "novo scan (OCR)"])
            B = A
            extra = {"arquivo_a": sha256(A), "arquivo_b": sha256(A) if tipo == "bytes iguais" else sha256(A + "x")}
            if tipo == "extração falhou":
                extra["extra_b"] = {"extracao_ok": False, "motivo_extracao": "OCR com confiança baixa"}
            if tipo == "embutida (trecho idêntico)":
                maior = gerar_peca(rng, peca.area, n_fatos=(20, 25)).paragrafos
                B, extra = "\n".join(maior[:8] + paragrafos + maior[8:]), {"relacao": "trecho"}
            if tipo == "novo scan (OCR)":
                B, extra = ruido_ocr(A, rng), {"extra_b": {"ocr": True}}
        elif verdade == "cópia com ressalva":
            B, tipo = _ruido_cosmetico(rng, paragrafos)
        elif verdade == "versão":
            tipo = rng.choice(["valor", "data", "CPF", "nome", "negação", "frase reescrita", "abreviada", "anexo",
                               "reordenada", "combinada", "reescrita extensa", "embutida com alteração", "frases em linhas + valor",
                               "novo scan com valor trocado", "outra peça do caso (memoriais)"])
            subtipos = {"nome": "outra instância do modelo", "outra peça do caso (memoriais)": "outra peça do caso"}
            extra = {"subtipo": subtipos.get(tipo, "mesma peça")}
            paragrafos_b = list(paragrafos)
            if tipo == "valor":
                paragrafos_b = [p.replace(peca.campos["valor"], _valor(rng)) for p in paragrafos_b]
            elif tipo == "data":
                nova = _data(rng)
                while nova == peca.campos["data"]:
                    nova = _data(rng)
                paragrafos_b = [p.replace(peca.campos["data"], nova) for p in paragrafos_b]
            elif tipo == "CPF":
                paragrafos_b = [PADROES_CAMPOS["cpf"].sub(_cpf(rng), p) for p in paragrafos_b]
            elif tipo == "nome":
                paragrafos_b = [p.replace(peca.campos["autor"], f"{rng.choice(NOMES)} {rng.choice(SOBRENOMES)}") for p in paragrafos_b]
            elif tipo == "negação":
                i = rng.choice([k for k in fatos if RE_VERBO.search(paragrafos_b[k])])
                paragrafos_b[i] = _negar(paragrafos_b[i])
            elif tipo == "frase reescrita":
                i = rng.choice(fatos)
                frases = paragrafos_b[i].split(". ")
                frases[rng.randrange(len(frases))] = _frase(rng, peca.area).rstrip(".")
                paragrafos_b[i] = ". ".join(frases)
            elif tipo == "abreviada":
                remover = set(rng.sample(fatos, max(1, len(fatos) // 4)))
                paragrafos_b = [p for i, p in enumerate(paragrafos_b) if i not in remover]
            elif tipo == "anexo":
                paragrafos_b = paragrafos_b + [paragrafo_de_fatos(rng, peca.area) for _ in range(rng.randint(1, 2))]
            elif tipo == "reordenada":
                i, j = rng.sample(fatos, 2)
                paragrafos_b[i], paragrafos_b[j] = paragrafos_b[j], paragrafos_b[i]
            elif tipo == "combinada":
                paragrafos_b = [p.replace(peca.campos["valor"], _valor(rng)) for p in paragrafos_b]
                i = rng.choice([k for k in fatos if RE_VERBO.search(paragrafos_b[k])])
                paragrafos_b[i] = _negar(paragrafos_b[i])
                paragrafos_b = paragrafos_b + [paragrafo_de_fatos(rng, peca.area)]
            elif tipo == "reescrita extensa":   # 2/3 dos parágrafos de fatos reescritos: mesmos fatos, outras palavras
                trocar = set(rng.sample(fatos, math.ceil(len(fatos) * 2 / 3)))
                paragrafos_b = [reescrever_fatos(peca.area, peca.frases[fatos.index(i)], random.Random(p)) if i in trocar else p
                                for i, p in enumerate(paragrafos_b)]
            elif tipo == "embutida com alteração":
                maior = gerar_peca(rng, peca.area, n_fatos=(20, 25)).paragrafos
                paragrafos_b = maior[:8] + [p.replace(peca.campos["valor"], _valor(rng)) for p in paragrafos_b] + maior[8:]
                extra["relacao"] = "trecho"
            elif tipo == "novo scan com valor trocado":
                paragrafos_b = ruido_ocr("\n".join(p.replace(peca.campos["valor"], _valor(rng)) for p in paragrafos_b), rng).split("\n")
                extra["extra_b"] = {"ocr": True}
            elif tipo == "outra peça do caso (memoriais)":
                paragrafos_b = memoriais_de(rng, peca).paragrafos
            elif tipo == "frases em linhas + valor":
                paragrafos_b = [f for p in paragrafos_b for f in re.split(r"(?<=\.) (?=[A-Z])", p.replace(peca.campos["valor"], _valor(rng)))]
            B = "\n".join(paragrafos_b)
            assert B != A, f"perturbação '{tipo}' não alterou o texto"
        else:
            tipo = rng.choice(["mesma área", "outra área", "mesmos 4 modelos, redigidos de novo", "modelo novo (nunca usado pelo cliente)",
                               "trechos reaproveitados", "cita a inicial (mesmo caso)"])
            if tipo == "mesma área":
                B = gerar_peca(rng, peca.area).texto
            elif tipo == "outra área":
                B = gerar_peca(rng, rng.choice([a for a in AREAS if a != peca.area])).texto
            elif tipo == "mesmos 4 modelos, redigidos de novo":
                A = gerar_peca(rng, peca.area, modelos=MODELOS_ESCRITORIO[:4], n_modelos=(4, 4)).texto
                B = gerar_peca(rng, peca.area, modelos=MODELOS_ESCRITORIO[:4], n_modelos=(4, 4)).texto
            elif tipo == "modelo novo (nunca usado pelo cliente)":
                A = "\n".join(paragrafos + [instanciar(m, rng) for m in MODELOS_NOVOS])
                B = "\n".join(gerar_peca(rng, peca.area).paragrafos + [instanciar(m, rng) for m in MODELOS_NOVOS])
            elif tipo == "trechos reaproveitados":   # outra peça que copia até metade dos parágrafos de fatos de A, sem aspas
                outra = gerar_peca(rng, peca.area, n_fatos=(5, 7))
                outro = outra.paragrafos
                for destino, origem in zip(outra.fatos, rng.sample(fatos, rng.randint(1, len(fatos) // 2))):
                    outro[destino] = paragrafos[origem]
                B = "\n".join(outro)
            else:
                B = peca_que_cita(rng, peca, n_citados=rng.randint(2, 3)).texto
        pares.append({"verdade": verdade, "tipo": tipo, "a": A, "b": B, **extra})
    rng_massa = random.Random(seed + 10_000)
    for k in range(n_massa):
        peca = gerar_peca_massa(rng_massa)
        if k % 2 == 0:
            B = peca.texto.replace(peca.campos["valor"], _valor(rng_massa))
            pares.append({"verdade": "versão", "tipo": "massa: valor corrigido", "a": peca.texto, "b": B, "subtipo": "mesma peça", "cliente": "massa"})
        else:
            pares.append({"verdade": "diferente", "tipo": "massa: independentes, mesmos modelos", "a": peca.texto,
                          "b": gerar_peca_massa(rng_massa).texto, "cliente": "massa"})
    return pares


def amostra_paragrafos(seed, n_pecas=60):
    """Pares de parágrafos de fatos para calibrar os cortes semânticos: paráfrase (mesmos fatos, outras palavras) contra
    outro fato da mesma peça e outro fato de outra peça da mesma área."""
    rng = random.Random(seed)
    parafrase, outro_mesma, outro_outra = [], [], []
    for _ in range(n_pecas):
        p, q = gerar_peca(rng, n_fatos=(4, 6)), None
        q = gerar_peca(rng, p.area, n_fatos=(4, 6))
        for k, i in enumerate(p.fatos):
            parafrase.append((p.paragrafos[i], reescrever_fatos(p.area, p.frases[k], random.Random(p.paragrafos[i]))))
            outro_mesma.append((p.paragrafos[i], p.paragrafos[p.fatos[(k + 1) % len(p.fatos)]]))
            outro_outra.append((p.paragrafos[i], q.paragrafos[q.fatos[k % len(q.fatos)]]))
    return {"paráfrase": parafrase, "outro fato, mesma peça": outro_mesma, "outro fato, outra peça": outro_outra}


def calibrar_cortes_semanticos(amostra, grade, falso_max=0.01, recall_min=0.99):
    """Corte alto (conta para "versão"): o menor com falso par ≤ falso_max, só pelo cosseno.
    Corte mínimo (só impede "diferente"): o maior que ainda acha ≥ recall_min das paráfrases, com um valor em comum."""
    def medir(pares):
        va = EMBEDDINGS.vetores([x for x, _ in pares])
        vb = EMBEDDINGS.vetores([y for _, y in pares])
        comum = np.array([not (vx := valores_do_paragrafo(x)) or not (vy := valores_do_paragrafo(y)) or bool(vx & vy) for x, y in pares])
        return (va * vb).sum(1), comum
    cos_pos, val_pos = medir(amostra["paráfrase"])
    negativos = [medir(amostra[k]) for k in amostra if k != "paráfrase"]
    cos_neg, val_neg = np.concatenate([c for c, _ in negativos]), np.concatenate([v for _, v in negativos])
    tabela = [{"corte": c, "recall": float(np.mean(cos_pos >= c)), "falso par": float(np.mean(cos_neg >= c)),
               "recall com valor": float(np.mean((cos_pos >= c) & val_pos)), "falso par com valor": float(np.mean((cos_neg >= c) & val_neg))}
              for c in grade]
    alto = min(l["corte"] for l in tabela if l["falso par"] <= falso_max)
    minimo = max(l["corte"] for l in tabela if l["recall com valor"] >= recall_min)
    return alto, minimo, tabela, (cos_pos, cos_neg)


def avaliar(pares, indices=None):
    """Cada par usa o índice de modelo do seu cliente (`indices[par["cliente"]]`); por padrão, o do cliente-1."""
    linhas = []
    for par in pares:
        indice = (indices or {}).get(par.get("cliente"), INDICE)
        a = indexar(representar("A", par["a"], par.get("arquivo_a"), **par.get("extra_a", {})), indice)
        b = indexar(representar("B", par["b"], par.get("arquivo_b"), **par.get("extra_b", {})), indice)
        linhas.append({**par, "docs": (a, b), "evidencia": comparar(a, b)})
    return linhas


# ── 10.2 Resultado no teste ───────────────────────────────────────────────
VERDADES = ["cópia", "cópia com ressalva", "versão", "diferente"]


def limite_superior(erros, n, confianca=0.95):
    """Limite superior exato (Clopper-Pearson, unilateral) da taxa de erro, por bisseção na binomial."""
    if n == 0:
        return float("nan")
    if erros >= n:
        return 1.0

    def cdf(p):
        return sum(math.comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(erros + 1))

    baixo, alto = erros / n, 1.0
    for _ in range(60):
        meio = (baixo + alto) / 2
        baixo, alto = (meio, alto) if cdf(meio) > 1 - confianca else (baixo, meio)
    return alto


def metricas(linhas, previsto):
    versoes = [l for l in linhas if l["verdade"] == "versão"]
    prev = [previsto(l) for l in linhas]
    decididos = [(l, p) for l, p in zip(linhas, prev) if p != "revisão necessária"]
    return {
        "versão→cópia": sum(p in ("cópia", "cópia com ressalva") for l, p in zip(linhas, prev) if l["verdade"] == "versão"),
        "n_versoes": len(versoes),
        "falso cópia": sum(p in ("cópia", "cópia com ressalva") and l["verdade"] in ("versão", "diferente") for l, p in zip(linhas, prev)),
        "diferente→versão": sum(p == "versão" for l, p in zip(linhas, prev) if l["verdade"] == "diferente"),
        "versão→diferente": sum(p == "diferente" for l, p in zip(linhas, prev) if l["verdade"] == "versão"),
        "revisão": sum(p == "revisão necessária" for p in prev) / len(prev),
        "erros nos decididos": sum(p != l["verdade"] for l, p in decididos),
        "precisão": {v: (sum(p == v and l["verdade"] == v for l, p in zip(linhas, prev)), sum(p == v for p in prev)) for v in VERDADES},
        "recall": {v: (sum(p == v and l["verdade"] == v for l, p in zip(linhas, prev)), sum(l["verdade"] == v for l in linhas)) for v in VERDADES},
    }


def previsto_sistema(linha, limiares=LIMIARES):
    return decidir(linha["evidencia"], limiares).classe


# ── 10.3 Ablações: o que cada componente acrescenta ───────────────────────
def _classe_cosseno(linha, corte_copia, corte_versao):
    if linha.get("arquivo_a") and linha.get("arquivo_a") == linha.get("arquivo_b"):
        return "cópia"
    c = linha.setdefault("cosseno", cosseno_palavras(linha["a"], linha["b"]))
    return "cópia" if c >= corte_copia else ("versão" if c >= corte_versao else "diferente")


def previsto_sem_filtro(linha):
    a, b = linha["docs"]
    extra_a, extra_b = linha.get("extra_a", {}), linha.get("extra_b", {})
    a2 = indexar(representar("A", linha["a"], linha.get("arquivo_a"), **extra_a), SEM_FILTRO)
    b2 = indexar(representar("B", linha["b"], linha.get("arquivo_b"), **extra_b), SEM_FILTRO)
    return decidir(comparar(a2, b2)).classe


def previsto_conjuntos(linha):
    """Mesmas regras, mas os percentuais vêm da contenção dos conjuntos de shingles específicos, sem alinhamento nem citações."""
    a, b = linha["docs"]
    comum = len(a.informativos & b.informativos)
    ev = replace(linha["evidencia"], pct_a_em_b=comum / max(1, len(a.informativos)), pct_b_em_a=comum / max(1, len(b.informativos)),
                 trecho=None, so_ruido_ocr=False, ocr_numeros=False)
    return decidir(ev).classe


# ── 11. Custo e latência ──────────────────────────────────────────────────
def medir(func, repeticoes=3):
    tempos = []
    for _ in range(repeticoes):
        t0 = time.perf_counter()
        func()
        tempos.append(time.perf_counter() - t0)
    return min(tempos)


PARAGRAFOS_POR_PAGINA = 6


def interpolar(medicoes, paginas, etapa):
    """Tempo de `etapa` para um documento de `paginas`, interpolado nas medições {páginas: {etapa: segundos}}."""
    xs = sorted(medicoes)
    if paginas <= xs[0]:
        return medicoes[xs[0]][etapa] * paginas / xs[0]
    for x0, x1 in zip(xs, xs[1:]):
        if paginas <= x1:
            f = (paginas - x0) / (x1 - x0)
            return medicoes[x0][etapa] * (1 - f) + medicoes[x1][etapa] * f
    return medicoes[xs[-1]][etapa] * paginas / xs[-1]


def taxa_documento(p_par, p):
    return 1 - (1 - p_par) ** p["documentos já no caso (média)"]


def custo_diario(docs_dia, p_par, p, medicoes, extracao_por_pagina):
    """Custo por dia. O OCR gerenciado é cobrado por página e não consome a CPU da plataforma (a CPU de OCR entra só na
    latência). A auditoria revisa às cegas uma fração dos documentos decididos sem revisão."""
    pg = p["páginas por documento (mediana)"]
    cpu_s = docs_dia * (pg * extracao_por_pagina + interpolar(medicoes, pg, "indexar")
                        + p["documentos já no caso (média)"] * interpolar(medicoes, pg, "comparar"))
    ocr = docs_dia * pg * p["fração de páginas que exigem OCR"] * p["US$ por mil páginas de OCR gerenciado"] / 1000 * p["R$ por US$"]
    revisoes = docs_dia * taxa_documento(p_par, p)
    auditorias = (docs_dia - revisoes) * p["fração auditada"]
    llm = revisoes * (p["tokens de entrada por chamada de LLM"] * p["R$ por milhão de tokens de entrada"]
                      + p["tokens de saída por chamada de LLM"] * p["R$ por milhão de tokens de saída"]) / 1e6
    horas = revisoes * p["minutos por revisão"] / 60
    horas_auditoria = auditorias * p["minutos por revisão"] / 60
    return {"vCPU-hora": cpu_s / 3600, "R$ CPU": cpu_s / 3600 * p["R$ por vCPU-hora"], "R$ OCR": ocr, "R$ LLM": llm,
            "revisões": revisoes, "horas de revisão": horas, "R$ revisão": horas * p["R$ por hora de revisor"],
            "auditorias": auditorias, "R$ auditoria": horas_auditoria * p["R$ por hora de revisor"]}



# ── 10.6 Texto real: sentenças de duas magistradas do TJSP ─────────────────
CORPUS_REAL = Path(__file__).with_name("sentencas_tjsp.json")   # gerado por coletar_sentencas.py (pseudonimizado)
MESES_RE = "janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro"


def corpus_real(n_teste=20, seed=0):
    """Por magistrada (o "cliente"): histórico (cada sentença é um caso) e 20 sentenças de teste, fora do histórico."""
    por_magistrada = defaultdict(list)
    for s in json.loads(CORPUS_REAL.read_text(encoding="utf-8"))["sentencas"]:
        por_magistrada[s["magistrada"]].append(s)
    saida = {}
    for magistrada, docs in sorted(por_magistrada.items()):
        docs = sorted(docs, key=lambda d: d["processo"])
        random.Random(seed).shuffle(docs)
        saida[magistrada] = {"teste": docs[:n_teste], "historico": docs[n_teste:],
                             "indice": IndiceDoCliente({d["processo"]: [d["texto"]] for d in docs[n_teste:]})}
    return saida


def fracao_modelo(texto, indice):
    """Fração das palavras reconhecidas como texto de modelo pelo índice."""
    doc = indexar(representar("x", texto), indice)
    return 1 - sum(doc.especifica) / max(1, len(doc.especifica))


def perturbacoes_reais(texto):
    """Alterações conhecidas sobre uma sentença real: a classe certa é sabida por construção."""
    saida = {"mesmo texto, outro arquivo": (texto, "cópia"),
             "cosmético (NFD, maiúsculas, espaços)": (unicodedata.normalize("NFD", texto).upper().replace(" ", "  "), "cópia com ressalva")}
    v = re.search(r"R\$ ?\d{1,3}(?:\.\d{3})*,\d{2}", texto)
    if v:
        saida["valor alterado"] = (texto[:v.end() - 4] + str((int(texto[v.end() - 4]) + 1) % 10) + texto[v.end() - 3:], "versão")
    p = re.search(r"\b(IM)?PROCEDENTES?\b", texto)
    if p:
        saida["procedente ↔ improcedente"] = (texto[:p.start()] + (p.group()[2:] if p.group(1) else "IM" + p.group()) + texto[p.end():], "versão")
    d = re.search(rf"\b(\d{{1,2}}) de ({MESES_RE}) de (\d{{4}})\b", texto)
    if d:
        saida["data alterada"] = (texto[:d.start(1)] + str(int(d.group(1)) % 28 + 1) + texto[d.end(1):], "versão")
    linhas = texto.split("\n")
    longas = [i for i in range(4, len(linhas) - 4) if len(linhas[i].split()) >= 25]
    if longas:
        i = longas[len(longas) // 2]
        saida["parágrafo removido"] = ("\n".join(linhas[:i] + linhas[i + 1:]), "versão")
    return saida


# ── 10.6 Paráfrases reais: cortes de cosseno e regras 10–12 em texto real ──
PARAFRASES_REAIS = Path(__file__).with_name("parafrases_reais_q1.json")   # escritas uma vez por LLM (os mesmos fatos)


def _paragrafos_proprios(doc):
    """Parágrafos de texto próprio (≥70% das palavras fora do modelo), de 20 a 160 palavras."""
    return [p for p in doc.paragrafos if 20 <= p.p1 - p.p0 <= 160 and sum(doc.especifica[p.p0:p.p1]) >= 0.7 * (p.p1 - p.p0)]


def amostra_paragrafos_reais(reais, papel):
    """Paráfrase real (mesmos fatos, outras palavras) contra parágrafos próprios de outros processos da mesma magistrada."""
    itens = [i for i in json.loads(PARAFRASES_REAIS.read_text(encoding="utf-8"))["itens"] if i["papel"] == papel]
    banco = defaultdict(list)
    for mag, v in reais.items():
        for s in v["teste"] + v["historico"][:40]:
            doc = indexar(representar(s["processo"], s["texto"]), v["indice"])
            banco[mag] += [(s["processo"], p.texto) for p in _paragrafos_proprios(doc)]
    return {"paráfrase": [(i["original"], i["parafrase"]) for i in itens],
            "outro fato, outro processo": [(i["original"], t) for i in itens for proc, t in banco[i["magistrada"]] if proc != i["processo"]]}


def reescritas_reais(reais):
    """Sobre as sentenças de teste com paráfrases: (1) reescrita real, 2 de cada 3 parágrafos próprios trocados pela paráfrase
    (esperado: versão · mesma peça, nunca diferente); (2) outra sentença da mesma magistrada (a de mais texto próprio) que copia, sem aspas,
    parágrafos próprios desta até ~1/3 do texto próprio dela (esperado: diferente)."""
    itens = [i for i in json.loads(PARAFRASES_REAIS.read_text(encoding="utf-8"))["itens"] if i["papel"] == "teste"]
    por_processo = defaultdict(dict)
    for i in itens:
        por_processo[i["processo"]][i["paragrafo"]] = i["parafrase"]
    pares = []
    for mag, v in reais.items():
        teste = {s["processo"]: s for s in v["teste"]}
        for proc, trocas in sorted(por_processo.items()):
            if proc not in teste:
                continue
            a = representar(proc, teste[proc]["texto"])
            ordem = sorted(trocas)
            trocar = {k for n, k in enumerate(ordem) if n % 3 != 2}
            texto_b = "\n".join(trocas[p.indice] if p.indice in trocar else p.texto for p in a.paragrafos)
            pares.append({"magistrada": mag, "tipo": "reescrita real (2/3 dos parágrafos próprios)", "verdade": "versão",
                          "a": teste[proc]["texto"], "b": texto_b})
            # a outra sentença precisa ter conteúdo próprio: a de mais parágrafos próprios da mesma magistrada
            candidatas = [indexar(representar(s["processo"], s["texto"]), v["indice"]) for s in v["teste"] if s["processo"] != proc]
            o = max(candidatas, key=lambda d: (len(_paragrafos_proprios(d)), d.doc_id))
            # copia parágrafos próprios de A até ~1/3 do texto próprio dela: com mais, "um saiu do outro" passa a ser defensável
            a_idx = indexar(representar(proc, teste[proc]["texto"]), v["indice"])
            limite, copiados, soma = _proprias(a_idx) / 3, [], 0
            for k in ordem:
                n = sum(1 for i in range(a.paragrafos[k].p0, a.paragrafos[k].p1) if a_idx.especifica[i] and not a_idx.citada[i])
                if copiados and soma + n > limite:
                    break
                copiados.append(a.paragrafos[k].texto)
                soma += n
            meio = len(o.paragrafos) // 2
            texto_o = "\n".join([p.texto for p in o.paragrafos[:meio]] + copiados + [p.texto for p in o.paragrafos[meio:]])
            pares.append({"magistrada": mag, "tipo": "outra sentença com trechos reaproveitados", "verdade": "diferente",
                          "a": teste[proc]["texto"], "b": texto_o})
    return pares

__all__ = [n for n in dir() if not n.startswith("__")]   # o caderno usa também os nomes com "_"
