"""Gera sentencas_tjsp.json: sentenças públicas do TJSP (consulta de julgados de 1º grau, e-SAJ) de duas magistradas de
Juizado Especial Cível, pseudonimizadas. Não é executado pelo caderno; o caderno lê o JSON gerado.

Uso: .venv/bin/python coletar_sentencas.py            (coleta e pseudonimiza)
     .venv/bin/python coletar_sentencas.py bruto.json (só pseudonimiza uma coleta já feita)

Pseudonimização: pessoas físicas (partes) viram nomes fictícios, os mesmos em todo o texto; a qualificação (CPF, RG,
endereço) sai; CPF, e-mail e telefone no corpo e os números de processo são trocados por fictícios consistentes; as
magistradas viram "MAGISTRADA A" e "MAGISTRADA B". Empresas ficam: a mesma empresa em vários processos é o contencioso de
massa que o teste precisa enxergar.
"""
import hashlib
import html
import http.cookiejar
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter

BASE = "https://esaj.tjsp.jus.br/cjpg/"
MAGISTRADAS = {"Joanna Terra Sampaio dos Santos": "MAGISTRADA A", "Vivian Novaretti": "MAGISTRADA B"}
PERIODO = ("01/01/2024", "30/06/2024")
CLASSE = "Procedimento do Juizado Especial Cível"
PAGINAS = 15

_jar = http.cookiejar.CookieJar()
_op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(_jar))
_op.addheaders = [("User-Agent", "Mozilla/5.0 (pesquisa academica; case tecnico)")]


def _get(url):
    for tentativa in range(3):
        try:
            with _op.open(url, timeout=60) as r:
                return r.read().decode("utf-8", errors="replace")
        except Exception:
            time.sleep(5 * (tentativa + 1))
    raise RuntimeError(url)


def _limpar(x):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", x))).strip()


def _campo(bloco, nome):
    m = re.search(rf"{nome}:\s*</strong>\s*(.*?)</td>", bloco, re.S)
    return _limpar(m.group(1)) if m else ""


def analisar(pagina):
    total = re.search(r"Resultados\s*<strong>[^<]*</strong>\s*de\s*([\d.]+)", pagina)
    saida = []
    for bloco in pagina.split('<tr class="fundocinza1">')[1:]:
        proc = re.search(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}", bloco)
        divs = re.findall(r'<div[^>]*style="display:\s*none;?"[^>]*>(.*?)</div>', bloco, re.S)
        if not proc or not divs:
            continue
        texto = re.sub(r"<[^>]+>", "", html.unescape(re.sub(r"<br\s*/?>", "\n", divs[-1])))
        texto = re.sub(r"\n{2,}", "\n", "\n".join(re.sub(r"[ \t]+", " ", l).strip() for l in texto.splitlines())).strip()
        saida.append({"processo": proc.group(), "classe": _campo(bloco, "Classe"), "assunto": _campo(bloco, "Assunto"),
                      "magistrado": _campo(bloco, "Magistrado"), "comarca": _campo(bloco, "Comarca"), "vara": _campo(bloco, "Vara"),
                      "data": _campo(bloco, "Data de Disponibilização"), "texto": texto})
    return (int(total.group(1).replace(".", "")) if total else 0), saida


def buscar(pesquisa, inicio, fim, max_paginas, pausa=1.5):
    q = urllib.parse.urlencode({"dadosConsulta.pesquisaLivre": pesquisa, "dadosConsulta.dtInicio": inicio,
                                "dadosConsulta.dtFim": fim, "conversationId": ""})
    total, docs = analisar(_get(BASE + "pesquisar.do?" + q))
    for p in range(2, max_paginas + 1):
        if len(docs) >= total:
            break
        time.sleep(pausa)
        docs += analisar(_get(BASE + f"trocarDePagina.do?pagina={p}&conversationId="))[1]
    return docs


# ── Pseudonimização ──────────────────────────────────────────────────────────
RE_EMPRESA = re.compile(r"\b(ltda|s\.?\s?/?\s?a\b|eireli|epp|banco|bank|cia\b|companhia|sociedade|associa|cooperativa|instituto|"
                        r"universidade|educacional|ensino|seguro|seguradora|telecom|telef|energia|eletr|airlines?|linhas a[ée]reas|"
                        r"a[ée]rea|operadora|com[ée]rcio|servi[çc]os|participa[çc][õo]es|financeira|financiamento|funda[çc][ãa]o|"
                        r"condom[íi]nio|munic[íi]pio|estado|fazenda|viagens|turismo|pagamentos|varejo|magazine|shopping|"
                        r"tecnologia|sistemas|empreendimentos|incorporadora|construtora|log[íi]stica|transportes?|hotel|"
                        r"clube|igreja|hospital|sa[úu]de|consórcio|consorcio|cart[õo]es|card|net|s/a|cr[ée]dito|marketing|caixa|bradesco|ita[úu]|"
                        r"santander|nubank|ifood|uninove|unipab|samedil|air canada|latam|azul|gol linhas|enel|sabesp|claro|vivo|"
                        r"tim\b|oi\b|mercado (livre|pago)|amazon|magalu|americanas|picpay|99|uber)", re.IGNORECASE)


def eh_empresa(nome):
    """Empresa (fica no texto) ou pessoa física (vira nome fictício). Sigla de uma palavra em maiúsculas é empresa."""
    return bool(RE_EMPRESA.search(nome)) or (len(nome.split()) == 1 and nome.isupper())
RE_PARTE = re.compile(r"^(Requerente|Requerido|Requerida|Autora?|R[ée]u|R[ée]|Exequente|Executad[oa]|Reclamante|Reclamad[oa])"
                      r"(s?)\s*:\s*(.+)$", re.MULTILINE | re.IGNORECASE)
RE_PROCESSO = re.compile(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}")
RE_CPF = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")
RE_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
RE_TELEFONE = re.compile(r"\(?\b\d{2}\)?\s?9?\d{4}-?\d{4}\b")
PRENOMES = ["Ana", "Bruno", "Carla", "Diego", "Elaine", "Fábio", "Gisele", "Hugo", "Isabela", "Jonas", "Karina", "Leandro", "Mariana",
            "Nelson", "Olívia", "Paulo", "Renata", "Sérgio", "Tatiane", "Vinícius"]
MEIOS = ["Alves", "Barros", "Campos", "Dias", "Esteves", "Fontes", "Garcia", "Henriques", "Ivo", "Jardim", "Leite", "Matos", "Nogueira",
         "Otero", "Prado", "Queiroz", "Rocha", "Sales", "Teles", "Vidal"]
SOBRENOMES_FICTICIOS = ["Amaral", "Bastos", "Cury", "Duarte", "Falcão", "Gusmão", "Lago", "Meireles", "Neves", "Pacheco", "Quintela",
                        "Reis", "Sampaio", "Tavares", "Uchoa", "Valente", "Xavier", "Zanetti", "Brandão", "Moura"]
# 8 mil nomes: duas pessoas diferentes quase nunca recebem o mesmo nome (o que faria partes diferentes parecerem a mesma)
NOMES_FICTICIOS = [f"{a} {b} {c}" for a in PRENOMES for b in MEIOS for c in SOBRENOMES_FICTICIOS]


VOCABULARIO_JURIDICO = set("""código defesa consumidor processo civil penal tribunal justiça estado lei direito federal superior câmara
apelação juizado especial cível turma recursal súmula constituição república banco comarca vara ministério público nacional
conselho comunicado provimento corregedoria geral seção relator relatora órgão julgador data julgamento registro foro regional
central diário oficial juiz juíza juízo cartório fazenda município secretaria agência anac anatel procon serasa receita
instituto sistema tabela portaria resolução decreto artigo inciso parágrafo capítulo título enunciado fonaje tema recurso
especial extraordinário agravo embargos mandado segurança ação civil coletiva administração pública poder judiciário
assistência judiciária gratuita sentença acórdão documento assinado digitalmente impressão margem direita""".split())
RE_NOME_PROPRIO = re.compile(r"\b[A-ZÀ-Ý][a-zà-ÿ]+(?:[ \t]+(?:d[aeo]s?[ \t]+)?[A-ZÀ-Ý][a-zà-ÿ]+){2,5}\b")
CONECTIVOS = {"de", "da", "do", "das", "dos"}
RE_PROPOSTO_POR = re.compile(r"(?:propost[oa]|ajuizad[oa]|movid[oa]|promovid[oa])\s+por\s+(.+?)\s+em face d", re.IGNORECASE | re.S)


def _escolha(chave, opcoes):
    return opcoes[int(hashlib.sha256(chave.encode()).hexdigest(), 16) % len(opcoes)]


def _processo_ficticio(real):
    h = int(hashlib.sha256(real.encode()).hexdigest(), 16)
    return f"{h % 10**7:07d}-{h // 10**7 % 100:02d}.2024.8.26.{h // 10**9 % 10**4:04d}"


def pseudonimizar(doc, rotulo_magistrada, nome_magistrada, minusculas=frozenset()):
    """`minusculas`: palavras que aparecem em minúsculas no corpus. Uma sequência com inicial maiúscula só é nome de pessoa
    se nenhuma das suas palavras aparece em minúsculas ("Responsabilidade do Fornecedor" não é; "Fernanda Campos" é)."""
    texto, nomes = doc["texto"], {}
    for papel, plural, conteudo in RE_PARTE.findall(texto):
        nome = re.split(r",| - ", conteudo)[0].strip()
        if not nome or eh_empresa(nome):
            continue
        nomes[nome] = _escolha(nome.casefold(), NOMES_FICTICIOS)
    for grupo in RE_PROPOSTO_POR.findall(texto):   # coautores que o cabeçalho resume como "e outro"
        for nome in re.split(r",|\s+e/ou\s+|\s+e\s+", grupo):
            nome = nome.strip(" .")
            if len(nome.split()) >= 2 and not eh_empresa(nome):
                nomes.setdefault(nome, _escolha(nome.casefold(), NOMES_FICTICIOS))
    for m in RE_NOME_PROPRIO.finditer(texto):      # outras pessoas citadas (sócios, testemunhas, relatores)
        nome = m.group()
        palavras = {p.casefold() for p in nome.split()} - CONECTIVOS
        if not eh_empresa(nome) and not palavras & VOCABULARIO_JURIDICO and not palavras & minusculas:
            nomes.setdefault(nome, _escolha(nome.casefold(), NOMES_FICTICIOS))
    linhas = []
    for linha in texto.splitlines():
        m = RE_PARTE.match(linha)
        if m:
            nome = re.split(r",| - ", m.group(3))[0].strip()
            linha = f"{m.group(1)}{m.group(2)}: {nomes.get(nome, nome)}"   # a qualificação (CPF, RG, endereço) sai
        linhas.append(linha)
    texto = "\n".join(linhas)
    for real, ficticio in sorted(nomes.items(), key=lambda x: -len(x[0])):
        texto = re.sub(re.escape(real), ficticio, texto, flags=re.IGNORECASE)
        partes = real.split()
        if len(partes) >= 2:   # "primeiro + último nome" também aparece no corpo
            texto = re.sub(rf"\b{re.escape(partes[0])}\s+{re.escape(partes[-1])}\b", ficticio, texto, flags=re.IGNORECASE)
    texto = RE_PROCESSO.sub(lambda m: _processo_ficticio(m.group()), texto)
    texto = RE_CPF.sub("000.000.000-00", texto)
    texto = RE_EMAIL.sub("email@exemplo.com.br", texto)
    texto = RE_TELEFONE.sub("(11) 90000-0000", texto)
    # o nome e, na mesma linha, sobrenomes extras em maiúsculas (a assinatura traz "VIVIAN NOVARETTI HUMES")
    texto = re.sub(rf"(?i:{re.escape(nome_magistrada)})(?:[ \t]+[A-ZÀ-Ý]{{2,}})*", rotulo_magistrada, texto)
    return {"processo": _processo_ficticio(doc["processo"]), "magistrada": rotulo_magistrada, "assunto": doc["assunto"],
            "vara": doc["vara"], "data": doc["data"], "texto": texto}


def montar_corpus(bruto):
    corpus = []
    minusculas = frozenset(re.findall(r"\b[a-zà-ÿ]{3,}\b", "\n".join(d["texto"] for docs in bruto.values() for d in docs)))
    for nome, rotulo in MAGISTRADAS.items():
        vistos = set()
        for doc in bruto[nome]:
            if doc["classe"] != CLASSE or nome.casefold() not in doc["magistrado"].casefold() or doc["processo"] in vistos \
                    or not re.search(r"SENTENÇA|DECISÃO", doc["texto"]):   # a página às vezes devolve um aviso no lugar do texto
                continue
            vistos.add(doc["processo"])
            corpus.append(pseudonimizar(doc, rotulo, nome, minusculas))
    return {"fonte": "TJSP, consulta de julgados de 1º grau (e-SAJ), sentenças públicas", "periodo": "/".join(PERIODO),
            "classe": CLASSE, "pseudonimizacao": __doc__.split("Pseudonimização: ")[1].strip(), "sentencas": corpus}


if __name__ == "__main__":
    if len(sys.argv) > 1:
        bruto = json.load(open(sys.argv[1], encoding="utf-8"))
    else:
        bruto = {nome: buscar(f'"{nome}"', *PERIODO, max_paginas=PAGINAS) for nome in MAGISTRADAS}
    corpus = montar_corpus(bruto)
    json.dump(corpus, open("sentencas_tjsp.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(Counter(d["magistrada"] for d in corpus["sentencas"]))
