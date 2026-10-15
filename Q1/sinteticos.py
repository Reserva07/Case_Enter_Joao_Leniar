"""Questão 1 — dados sintéticos da demonstração e da avaliação: modelos do escritório, peças, histórico do cliente,
perturbações (OCR, citação, memoriais, reescrita) e PDFs. Não fazem parte da solução (q1.py)."""
import json
import random
import re
from pathlib import Path

import pymupdf

from q1 import *


# ── Modelos do escritório, peças e histórico do cliente ────────────────────
NOMES = ["Maria", "Marina", "Ana", "Beatriz", "Carla", "Daniela", "Eduarda", "Fernanda", "Gabriela", "Helena",
         "João", "Pedro", "Rafael", "Lucas", "Mateus", "Carlos", "Bruno", "Tiago", "André", "Felipe"]
SOBRENOMES = ["Silva", "Souza", "Oliveira", "Santos", "Pereira", "Costa", "Rodrigues", "Almeida", "Nascimento", "Lima",
              "Araújo", "Fernandes", "Carvalho", "Gomes", "Martins", "Rocha", "Ribeiro", "Barbosa", "Teixeira", "Moreira"]
EMPRESAS = ["Alfa", "Atlas", "Horizonte", "Nova Era", "Prisma", "Vértice", "Solaris", "Delta", "Orion", "Aurora"]
RAMOS = ["Serviços Prediais", "Telecomunicações", "Comércio Varejista", "Logística", "Engenharia", "Imóveis", "Saúde"]
CIDADES = ["São Paulo", "Campinas", "Santos", "Curitiba", "Belo Horizonte", "Porto Alegre", "Recife", "Salvador"]
MESES_LISTA = MESES.split("|")

# Modelos do escritório. Cada parágrafo tem trechos alternativos {a|b|c} e trechos opcionais [...]; a cada uso, o advogado
# escolhe uma combinação e ainda mexe em palavras soltas (deriva). Não há lista fixa de textos: cada modelo gera milhares
# de variantes, e o sistema só conhece o modelo pelo que se repete no histórico de casos do cliente.
MODELOS_ESCRITORIO = [
    "{Ante o exposto|Diante do exposto|Pelo exposto}, {requer|pede|postula} {o regular prosseguimento do feito|o prosseguimento regular da ação}"
    "[, com observância das formalidades legais], {e a intimação|com a intimação} das partes para todos os atos processuais.",
    "{Requer|Pede} a citação da {parte ré|requerida|ré}, {por via postal|pelo correio|por meio eletrônico}, para, querendo, apresentar contestação "
    "no prazo legal, sob pena de {revelia e confissão quanto à matéria de fato|revelia|aplicação dos efeitos da revelia}.",
    "{Protesta|Pretende} provar o alegado por todos os meios de prova {em direito admitidos|admitidos em direito|legalmente admitidos}"
    "[, especialmente {prova documental, testemunhal e pericial|a documental e a testemunhal|a prova documental}][, se necessária].",
    "Requer a concessão {dos benefícios|do benefício} da justiça gratuita, nos termos do {artigo|art.} 98 do {Código de Processo Civil|CPC}, "
    "por não possuir condições de arcar com as custas[ sem prejuízo do próprio sustento].",
    "Requer a inversão do ônus da prova, nos termos do {artigo|art.} 6º, inciso VIII, do {Código de Defesa do Consumidor|CDC}, diante da "
    "{verossimilhança das alegações|hipossuficiência da parte autora|verossimilhança das alegações e da hipossuficiência da autora}.",
    "{Manifesta|Declara} {interesse|desinteresse} na realização de audiência de conciliação, nos termos do {artigo|art.} 319, inciso VII, "
    "do {Código de Processo Civil|CPC}.",
    "{Por tais razões|Por todo o exposto|Assim}, requer o {acolhimento integral|acolhimento} dos pedidos {formulados na presente petição inicial|"
    "formulados nesta inicial|aqui formulados}, com a condenação da ré ao pagamento das custas e honorários advocatícios[ de sucumbência].",
    "Requer que todas as intimações sejam {realizadas|feitas|publicadas} exclusivamente em nome do advogado subscritor, sob pena de nulidade, "
    "nos termos do {artigo|art.} 272[, § 5º,] do {Código de Processo Civil|CPC}.",
    "Dá-se à causa o valor {indicado na planilha anexa|constante da planilha anexa|apurado na planilha em anexo}, para {todos os efeitos legais e "
    "fiscais|os efeitos legais|fins de alçada e demais efeitos legais}[, nos termos do {artigo|art.} 292 do {Código de Processo Civil|CPC}].",
    "{Nestes termos|Termos em que}, a parte autora confia no elevado senso de justiça deste juízo para a procedência dos pedidos"
    "[, como medida de inteira e lídima justiça].",
]
# Modelos que o cliente nunca usou antes: usados para medir o limite (um modelo novo só é aprendido depois de aparecer em vários casos).
MODELOS_NOVOS = [
    "{Registra|Consigna}, por oportuno, que a presente demanda observa os princípios da cooperação, da boa-fé processual e da duração "
    "razoável do processo, conforme os {artigos|arts.} 5º e 6º do {Código de Processo Civil|CPC}.",
    "{Esclarece|Informa}, ainda, que os documentos que instruem a inicial são cópias fiéis dos originais, declaradas autênticas pelo "
    "advogado subscritor, sob sua responsabilidade pessoal.",
]
DERIVA_PADRAO = 0.02   # a cada uso, ~2% das palavras do modelo são mexidas (apagadas, trocadas de lugar ou com uma palavra a mais)
RE_OPCIONAL, RE_ALTERNATIVA = re.compile(r"\[([^\[\]]*)\]"), re.compile(r"\{([^{}]*)\}")
PALAVRAS_EXTRA = ["ainda", "também", "expressamente", "desde logo", "igualmente", "respeitosamente"]


def derivar(texto, rng, taxa):
    """Edições soltas de quem adapta o modelo à mão: apagar uma palavra, trocar duas de lugar, acrescentar uma palavra."""
    palavras_texto, saida, k = texto.split(" "), [], 0
    while k < len(palavras_texto):
        w = palavras_texto[k]
        if rng.random() < taxa:
            edicao = rng.choice(["apagar", "trocar", "acrescentar"])
            if edicao == "trocar" and k + 1 < len(palavras_texto):
                saida += [palavras_texto[k + 1], w]
                k += 2
                continue
            if edicao == "acrescentar":
                saida += [w, rng.choice(PALAVRAS_EXTRA)]
        else:
            saida.append(w)
        k += 1
    return " ".join(saida)


def instanciar(modelo, rng, deriva=DERIVA_PADRAO):
    texto = RE_OPCIONAL.sub(lambda m: m.group(1) if rng.random() < 0.5 else "", modelo)
    texto = RE_ALTERNATIVA.sub(lambda m: rng.choice(m.group(1).split("|")), texto)
    return derivar(re.sub(r"\s+", " ", texto).strip(), rng, deriva)


AREAS = {
    "serviços": {
        "acao": "COBRANÇA",
        "sujeito": ["A autora", "A contratada", "A equipe técnica da autora", "O responsável técnico", "A prestadora", "O encarregado da obra",
                    "O síndico do edifício", "O gerente da ré", "O preposto da ré", "A fiscalização da ré", "O engenheiro responsável", "A coordenação do contrato"],
        "acao_verbo": ["realizou", "concluiu", "comprovou", "apresentou", "enviou", "recebeu", "reconheceu", "registrou", "aprovou", "efetuou", "acompanhou", "validou"],
        "objeto": ["a troca das bombas hidráulicas", "a revisão do quadro elétrico", "a pintura das áreas comuns", "a substituição dos elevadores",
                   "a impermeabilização da cobertura", "o reparo da rede de esgoto", "a manutenção do sistema de incêndio", "a instalação das câmeras",
                   "o relatório de execução", "a medição mensal dos serviços", "a nota fiscal de serviços", "o termo de aceite parcial"],
        "complemento": ["na unidade comercial {n}", "no bloco {letra} do edifício", "conforme ordem de serviço nº {num}", "dentro do prazo do cronograma",
                        "com acompanhamento do síndico", "após a vistoria técnica", "segundo o laudo de {data}", "mediante protocolo nº {num}",
                        "no valor de {valor}", "com prazo de garantia de {n} meses", "sem qualquer ressalva formal", "com registro fotográfico datado"],
    },
    "consumo": {
        "acao": "INDENIZAÇÃO POR DANOS MORAIS E MATERIAIS",
        "sujeito": ["O autor", "A consumidora", "A central de atendimento", "O atendente da ré", "A operadora", "O fornecedor",
                    "O setor de cobrança da ré", "A ouvidoria da ré", "O técnico credenciado", "A instituição financeira", "O vendedor da loja", "A transportadora"],
        "acao_verbo": ["realizou", "cancelou", "cobrou", "comprovou", "recebeu", "registrou", "reconheceu", "enviou", "negou", "efetuou", "apresentou", "estornou"],
        "objeto": ["a cobrança do pacote adicional", "o cancelamento da linha telefônica", "a entrega do produto adquirido", "a troca do aparelho defeituoso",
                   "o estorno das parcelas indevidas", "a reclamação formal da consumidora", "a fatura com lançamentos desconhecidos", "o contrato de adesão",
                   "o pedido de portabilidade", "a negativação do nome do autor", "o reparo em garantia", "a oferta anunciada no site"],
        "complemento": ["no protocolo de atendimento nº {num}", "em {data}", "no valor de {valor}", "após {n} tentativas de contato",
                        "sem autorização expressa", "conforme gravação da ligação", "dentro do prazo de garantia", "segundo a nota fiscal nº {num}",
                        "por meio do aplicativo", "na loja da cidade de {cidade}", "com cobrança de multa de {valor}", "sem resposta da ouvidoria"],
    },
    "trabalhista": {
        "acao": "RECLAMAÇÃO TRABALHISTA",
        "sujeito": ["O reclamante", "A reclamante", "O supervisor imediato", "A empresa reclamada", "O setor de recursos humanos", "O gerente da filial",
                    "A testemunha indicada", "O coordenador de turno", "A empregadora", "O sindicato da categoria", "O médico do trabalho", "O encarregado do setor"],
        "acao_verbo": ["realizou", "cumpriu", "recebeu", "comprovou", "registrou", "exigiu", "pagou", "reconheceu", "apresentou", "assinou", "efetuou", "anotou"],
        "objeto": ["a jornada de doze horas diárias", "as horas extras habituais", "o intervalo intrajornada reduzido", "o adicional de insalubridade",
                   "as verbas rescisórias", "o depósito do FGTS", "o aviso prévio indenizado", "as metas abusivas de vendas",
                   "o controle de ponto britânico", "a dispensa sem justa causa", "o atestado médico", "a transferência de unidade"],
        "complemento": ["entre {data} e {data2}", "na filial de {cidade}", "conforme cartões de ponto", "sem pagamento correspondente",
                        "no valor de {valor}", "durante {n} meses consecutivos", "segundo o contracheque de {data}", "conforme convenção coletiva",
                        "por determinação da gerência", "sem anotação na carteira", "com aviso de {n} dias", "mediante recibo nº {num}"],
    },
    "locação": {
        "acao": "DESPEJO CUMULADA COM COBRANÇA DE ALUGUÉIS",
        "sujeito": ["O locador", "A locatária", "A administradora do imóvel", "O fiador", "O vistoriador", "O corretor responsável",
                    "A imobiliária", "O condomínio", "O inquilino", "A proprietária", "O avaliador contratado", "O síndico"],
        "acao_verbo": ["realizou", "pagou", "recebeu", "comprovou", "devolveu", "enviou", "registrou", "reconheceu", "apresentou", "assinou", "efetuou", "notificou"],
        "objeto": ["o contrato de locação residencial", "os aluguéis vencidos", "a vistoria de entrada", "as chaves do imóvel",
                   "o depósito caução", "a notificação extrajudicial", "o reajuste anual do aluguel", "as cotas condominiais",
                   "o laudo de vistoria de saída", "a multa contratual", "o seguro fiança", "o termo de entrega das chaves"],
        "complemento": ["em {data}", "no valor de {valor}", "referente ao imóvel da rua {num}", "conforme cláusula {n} do contrato",
                        "com prazo de {n} dias", "por meio da administradora", "sem qualquer justificativa", "segundo recibo nº {num}",
                        "na cidade de {cidade}", "após {n} meses de atraso", "com registro em cartório", "acompanhado de fotografias"],
    },
}
DIREITO = {
    "serviços": "Nos termos dos artigos 389 e 395 do Código Civil, o devedor responde por perdas e danos, juros e atualização monetária quando não cumpre a obrigação no tempo e modo devidos.",
    "consumo": "Nos termos do artigo 14 do Código de Defesa do Consumidor, o fornecedor responde, independentemente de culpa, pela reparação dos danos causados aos consumidores por defeitos na prestação dos serviços.",
    "trabalhista": "Nos termos do artigo 7º da Constituição Federal e do artigo 59 da Consolidação das Leis do Trabalho, a jornada excedente deve ser remunerada com adicional mínimo de cinquenta por cento.",
    "locação": "Nos termos do artigo 9º, inciso III, da Lei 8.245 de 1991, a locação pode ser desfeita em decorrência da falta de pagamento do aluguel e demais encargos.",
}
VERBOS_NEGAVEIS = sorted({v for area in AREAS.values() for v in area["acao_verbo"]}, key=len, reverse=True)


@dataclass
class Peca:
    area: str
    paragrafos: list
    campos: dict
    fatos: list = field(default_factory=list)     # índices dos parágrafos de fatos
    modelo: list = field(default_factory=list)    # índices dos parágrafos que vêm dos modelos do escritório
    frases: list = field(default_factory=list)    # peças das frases de cada parágrafo de fatos (para reescrevê-lo com os mesmos fatos)

    @property
    def texto(self):
        return "\n".join(self.paragrafos)


def _valor(rng):
    reais = rng.randint(1_000, 250_000)
    return f"R$ {reais:,}".replace(",", ".") + f",{rng.randint(0, 99):02d}"


def _data(rng):
    return f"{rng.randint(1, 28)} de {rng.choice(MESES_LISTA)} de {rng.randint(2019, 2025)}"


def _cpf(rng):
    d = [rng.randint(0, 9) for _ in range(11)]
    return f"{d[0]}{d[1]}{d[2]}.{d[3]}{d[4]}{d[5]}.{d[6]}{d[7]}{d[8]}-{d[9]}{d[10]}"


def _cnpj(rng):
    d = "".join(str(rng.randint(0, 9)) for _ in range(14))
    return f"{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:]}"


# Detalhes do caso no meio da frase (quando, onde, quem, quanto): é o que torna um fato real único, e não uma combinação
# de frases prontas que se repete entre casos do cliente.
RUAS = ["das Acácias", "Barão de Itapetininga", "Sete de Setembro", "XV de Novembro", "dos Andradas", "Augusta", "da Consolação",
        "Marechal Deodoro", "das Palmeiras", "Voluntários da Pátria", "Tiradentes", "do Comércio", "Santos Dumont", "Rio Branco"]
DETALHES = ["em {data}", "no dia {data}", "por volta das {h}h{m:02d} de {data}", "na Rua {rua}, nº {n}", "conforme e-mail de {data}",
            "na presença de {pessoa}", "segundo relato de {pessoa}", "pelo protocolo {num}", "após {n} dias de espera", "na unidade {num}"]


def _valores(rng):
    return dict(n=rng.randint(2, 900), num=rng.randint(1000, 99999), letra=rng.choice("ABCDEF"), data=_data(rng), data2=_data(rng),
                valor=_valor(rng), cidade=rng.choice(CIDADES), h=rng.randint(7, 19), m=rng.randint(0, 59), rua=rng.choice(RUAS),
                pessoa=f"{rng.choice(NOMES)} {rng.choice(SOBRENOMES)}")


def _preencher(rng, molde):
    return molde.format(**_valores(rng))


def _frase(rng, area, registro=None):
    """Uma frase de fato. Com `registro`, guarda as peças da frase, para reescrevê-la depois com os mesmos fatos."""
    g = AREAS[area]
    detalhe, valores_detalhe = rng.choice(DETALHES), _valores(rng)
    complemento, valores_complemento = rng.choice(g["complemento"]), _valores(rng)
    sujeito, verbo, objeto = rng.choice(g["sujeito"]), rng.choice(g["acao_verbo"]), rng.choice(g["objeto"])
    if registro is not None:
        registro.append((detalhe, valores_detalhe, complemento, valores_complemento, sujeito, verbo, objeto))
    return f"{sujeito}, {detalhe.format(**valores_detalhe)}, {verbo} {objeto} {complemento.format(**valores_complemento)}."


def paragrafo_de_fatos(rng, area, frases=(2, 4), registro=None):
    return " ".join(_frase(rng, area, registro) for _ in range(rng.randint(*frases)))


# Paráfrases fixas (escritas uma vez por um LLM): a mesma frase de fato com outras palavras e outra ordem.
PARAFRASES = json.loads(Path(__file__).with_name("parafrases_q1.json").read_text(encoding="utf-8"))


def reescrever_fatos(area, registro, rng):
    """Reescreve um parágrafo de fatos: mesmos fatos (datas, valores, nomes, números), outras palavras e outra ordem."""
    g, frases = PARAFRASES["areas"][area], []
    for detalhe, valores_detalhe, complemento, valores_complemento, sujeito, verbo, objeto in registro:
        d = PARAFRASES["detalhes"][detalhe].format(**valores_detalhe)
        sj = g["sujeito"][sujeito]
        frases.append(rng.choice(PARAFRASES["estruturas"]).format(
            Detalhe=d[0].upper() + d[1:], detalhe=d, Sujeito=sj, sujeito=sj[0].lower() + sj[1:], verbo=PARAFRASES["verbos"][verbo],
            objeto=g["objeto"][objeto], complemento=g["complemento"][complemento].format(**valores_complemento)))
    return " ".join(frases)


def gerar_peca(rng, area=None, n_fatos=(3, 7), modelos=MODELOS_ESCRITORIO, n_modelos=(2, 4), deriva=DERIVA_PADRAO, reu=None, cnpj=None,
               frases_fato=(2, 4)):
    """`reu`/`cnpj` fixos e `frases_fato` curtas: contencioso de massa (o mesmo réu em todos os casos do cliente)."""
    area = area or rng.choice(list(AREAS))
    autor = f"{rng.choice(NOMES)} {rng.choice(SOBRENOMES)} {rng.choice(SOBRENOMES)}"
    reu = reu or f"{rng.choice(EMPRESAS)} {rng.choice(RAMOS)} Ltda."
    campos = {"autor": autor, "re": reu, "cidade": rng.choice(CIDADES), "valor": _valor(rng), "data": _data(rng)}
    abertura = instanciar("{EXCELENTÍSSIMO SENHOR DOUTOR JUIZ|EXMO. SR. DR. JUIZ|AO JUÍZO} DE DIREITO DA", rng, 0)
    paragrafos = [
        f"{abertura} {rng.randint(1, 40)}ª VARA CÍVEL DA COMARCA DE {campos['cidade'].upper()}",
        f"{autor}, CPF nº {_cpf(rng)}, com endereço em {campos['cidade']}, "
        + instanciar("{vem|vem respeitosamente}, {por seu advogado|por intermédio de seu advogado|por sua advogada}, {propor a presente|ajuizar a presente}", rng, 0)
        + f" AÇÃO DE {AREAS[area]['acao']} em face de {reu}, CNPJ nº {cnpj or _cnpj(rng)}, pelos fatos e fundamentos a seguir expostos.",
        "DOS FATOS",
    ]
    fatos = list(range(len(paragrafos), len(paragrafos) + rng.randint(*n_fatos)))
    frases = [[] for _ in fatos]
    paragrafos += [paragrafo_de_fatos(rng, area, frases_fato, registro) for registro in frases]
    paragrafos += ["DO DIREITO", DIREITO[area], "DOS PEDIDOS",
                   f"Requer a condenação de {reu} ao pagamento de {campos['valor']}, acrescido de correção monetária desde {campos['data']} e juros de mora desde a citação."]
    escolhidos = rng.sample(modelos, rng.randint(*n_modelos))
    modelo = list(range(len(paragrafos), len(paragrafos) + len(escolhidos)))
    paragrafos += [instanciar(m, rng, deriva) for m in escolhidos]
    paragrafos += [instanciar("{Termos em que|Nestes termos,} pede deferimento.", rng, 0), f"{campos['cidade']}, {_data(rng)}.",
                   f"{rng.choice(NOMES)} {rng.choice(SOBRENOMES)} - OAB/SP {rng.randint(100000, 499999)}"]
    return Peca(area, paragrafos, campos, fatos, modelo, frases)


def gerar_historico(seed, n_casos=80, deriva=DERIVA_PADRAO, modelos=MODELOS_ESCRITORIO, sem_fatos=False):
    """Casos anteriores de um cliente: 1 a 3 peças por caso, todas escritas a partir dos modelos do escritório, com variação.
    Com `sem_fatos`, o histórico não leva os parágrafos de fatos: controle em que nenhum fato pode virar modelo."""
    rng = random.Random(seed)

    def texto(peca):
        return "\n".join(p for k, p in enumerate(peca.paragrafos) if not (sem_fatos and k in peca.fatos))
    return [[texto(gerar_peca(rng, modelos=modelos, deriva=deriva)) for _ in range(rng.randint(1, 3))] for _ in range(n_casos)]
INDICE = IndiceDoCliente(gerar_historico(seed=0))   # cliente-1: o cliente dos exemplos e da avaliação
INDICES_POR_CLIENTE[CLIENTE_PADRAO] = INDICE


# ── Perturbações: OCR, citação, memoriais ────────────────────
CONFUSOES_OCR = [("rn", "m"), ("m", "rn"), ("l", "1"), ("i", "l"), ("o", "0"), ("e", "c"), ("ç", "c"), ("ã", "a"), ("é", "e"),
                 ("5", "6"), ("0", "8"), ("1", "7")]
CONFUSOES_SO_LETRAS = [(x, y) for x, y in CONFUSOES_OCR if not (x.isdigit() and y.isdigit())]


def ruido_ocr(texto, rng, taxa=0.03, confusoes=CONFUSOES_OCR, poupar_campos=False):
    """Simula outro OCR do mesmo papel: confusões de caracteres dentro de palavras (nunca na 1ª letra, nunca cria ou junta palavras).
    Com `poupar_campos`, valores, datas, CPF, CNPJ e processo saem intactos."""
    protegidos = [m.span() for padrao in PADROES_CAMPOS.values() for m in re.finditer(padrao.pattern, texto, re.IGNORECASE)] if poupar_campos else []

    def trocar(m):
        w = m.group(0)
        if rng.random() >= taxa or any(a <= m.start() < b for a, b in protegidos):
            return w
        opcoes = [(x, y, k) for x, y in confusoes for k in range(1, len(w)) if w.startswith(x, k)]
        if not opcoes:
            return w
        x, y, k = rng.choice(opcoes)
        return w[:k] + y + w[k + len(x):]
    novo = texto
    while novo == texto:
        novo = re.sub(r"\w{3,}", trocar, texto)
    return novo


def peca_que_cita(rng, origem, n_citados=3):
    """Contestação do mesmo caso: outra peça que transcreve parágrafos de fatos da inicial, 'in verbis', entre aspas. Abertura real:
    "nos autos da AÇÃO DE … que lhe move …, vem apresentar CONTESTAÇÃO"."""
    fatos = origem.paragrafos[3:origem.paragrafos.index("DO DIREITO")][:n_citados]
    propria = gerar_peca(rng, origem.area, n_fatos=(4, 6)).paragrafos
    propria[1] = (f"{origem.campos['re']}, já qualificada nos autos da AÇÃO DE {AREAS[origem.area]['acao']} que lhe move "
                  f"{origem.campos['autor']}, vem apresentar CONTESTAÇÃO, pelos fatos e fundamentos a seguir expostos.")
    return Peca(origem.area, propria[:3] + ["Alega a parte autora, in verbis:"] + [f"“{p}”" for p in fatos] + propria[3:], {})


def memoriais_de(rng, origem, n_novos=(1, 2)):
    """Memoriais do mesmo caso: outra peça, mesmas partes e processo, que repete os fatos da inicial sem marca de citação."""
    fatos = origem.paragrafos[3:origem.paragrafos.index("DO DIREITO")]
    return Peca(origem.area, [origem.paragrafos[0],
                              f"{origem.campos['autor']}, já qualificada nos autos da AÇÃO DE {AREAS[origem.area]['acao']} que move em face "
                              f"de {origem.campos['re']}, vem apresentar MEMORIAIS, nos termos a seguir.", "DOS FATOS"] + fatos
                + ["DA INSTRUÇÃO"] + [paragrafo_de_fatos(rng, origem.area) for _ in range(rng.randint(*n_novos))]
                + ["Termos em que pede deferimento."], {})


# ── 5.1 Petições independentes com os mesmos modelos ────────────────────
def pares_independentes(indice, deriva, n=20, seed=7000):
    """Petições independentes do mesmo cliente, todas com os mesmos 4 modelos (cada uma com a sua redação), fatos diferentes."""
    rng = random.Random(seed)
    pecas = [gerar_peca(rng, "consumo", modelos=MODELOS_ESCRITORIO[:4], n_modelos=(4, 4), deriva=deriva) for _ in range(2 * n)]
    docs = [indexar(representar(f"p{k}", p.texto), indice) for k, p in enumerate(pecas)]
    classes = Counter(decidir(comparar(docs[2 * k], docs[2 * k + 1])).classe for k in range(n))
    return pecas, docs, classes


# ── 5.2 Petições quase só de modelo (contencioso de massa) ─────────────────────
REU_MASSA, CNPJ_MASSA = "Operadora Exemplo S.A.", "11.222.333/0001-81"   # o mesmo réu em todos os casos do cliente


def gerar_peca_massa(rng):
    """Petição de massa: os 10 modelos do escritório, uma frase de fatos, o mesmo réu de todos os casos."""
    return gerar_peca(rng, "consumo", n_fatos=(1, 1), n_modelos=(len(MODELOS_ESCRITORIO),) * 2, reu=REU_MASSA, cnpj=CNPJ_MASSA, frases_fato=(1, 1))


def historico_massa(seed, n_casos=300, sem_fatos=False):
    """Histórico de um cliente de massa: 1 a 2 petições por caso, todas contra o mesmo réu (`sem_fatos`: controle da §10.3)."""
    rng = random.Random(seed)

    def texto(peca):
        return "\n".join(p for k, p in enumerate(peca.paragrafos) if not (sem_fatos and k in peca.fatos))
    return [[texto(gerar_peca_massa(rng)) for _ in range(rng.randint(1, 2))] for _ in range(n_casos)]


def peca_minima(rng, autor=None, cpf=None, deriva=0.0):
    """Caso extremo: qualificação + modelos sem edição, sem fatos, valor nem data. Texto próprio = nome e CPF."""
    autor = autor or f"{rng.choice(NOMES)} {rng.choice(SOBRENOMES)} {rng.choice(SOBRENOMES)}"
    return [f"{autor.upper()}, CPF nº {cpf or _cpf(rng)}, já qualificado nos autos, vem, por seu advogado, propor a presente AÇÃO DE "
            f"INDENIZAÇÃO POR DANOS MORAIS E MATERIAIS em face de {REU_MASSA}, CNPJ nº {CNPJ_MASSA}, pelos fatos e fundamentos a seguir expostos.",
            "DOS PEDIDOS"] + [instanciar(m, rng, deriva) for m in MODELOS_ESCRITORIO] + ["Termos em que pede deferimento."]


# ── 6. LLM simulado (o caderno não chama API) ────────────────────
def llm_simulado(payload):
    """Substitui a chamada real: devolve o formato esperado, sem classificar."""
    saida = []
    for item in payload["itens"]:
        partes, negacoes = diff_palavras(item.get("antes", ""), item.get("depois", ""))
        relevancia = "alta" if negacoes or any(re.search(r"\d", p) for p in partes) else "media"
        saida.append({"id": item["id"], "mudanca": f"{item['tipo']}: {' '.join(partes)[:120]}", "relevancia": relevancia})
    return {"itens": saida}
# ── 7. PDFs e anexos de imagem ────────────────────
A4_LARGURA, A4_ALTURA = pymupdf.paper_size("a4")
MARGEM = 60


def gerar_pdf(paragrafos, cabecalho, fonte=11, titulo="Petição", autor="Escritório Exemplo", paginas_escaneadas=(), modo_texto=0):
    """`modo_texto=3`: corpo em texto invisível (como a camada de OCR de um PDF escaneado)."""
    pdf = pymupdf.open()
    topo, base_pagina = MARGEM + 30, A4_ALTURA - MARGEM - 20
    pagina, y = pdf.new_page(width=A4_LARGURA, height=A4_ALTURA), topo
    for texto in paragrafos:
        for _ in range(2):
            if base_pagina - y < fonte * 3:
                pagina, y = pdf.new_page(width=A4_LARGURA, height=A4_ALTURA), topo
            caixa = pymupdf.Rect(MARGEM, y, A4_LARGURA - MARGEM, base_pagina)
            sobra = pagina.insert_textbox(caixa, texto.translate(TIPOGRAFIA), fontsize=fonte, fontname="helv", render_mode=modo_texto)   # a fonte base não tem aspas tipográficas
            if sobra >= 0:
                y += caixa.height - sobra + fonte * 0.8
                break
            pagina, y = pdf.new_page(width=A4_LARGURA, height=A4_ALTURA), topo
        else:
            raise ValueError("parágrafo maior que uma página")
    total = pdf.page_count
    for numero, pagina in enumerate(pdf, start=1):
        pagina.insert_text((MARGEM, MARGEM), cabecalho, fontsize=8, fontname="helv")
        pagina.insert_text((A4_LARGURA / 2 - 30, A4_ALTURA - MARGEM + 20), f"Página {numero} de {total}", fontsize=8, fontname="helv")
    for numero in paginas_escaneadas:
        imagem = pdf[numero - 1].get_pixmap(dpi=90)
        pdf.delete_page(numero - 1)
        nova = pdf.new_page(pno=numero - 1, width=A4_LARGURA, height=A4_ALTURA)
        nova.insert_image(nova.rect, pixmap=imagem)
    pdf.set_metadata({"title": titulo, "author": autor})
    return pdf.tobytes()


def anexo_imagem(seed):
    r = random.Random(seed)
    pdf = pymupdf.open()
    pagina = pdf.new_page(width=420, height=280)
    for _ in range(14):
        x, y = r.uniform(0, 380), r.uniform(0, 240)
        cor = (r.random(), r.random(), r.random())
        pagina.draw_rect(pymupdf.Rect(x, y, x + r.uniform(30, 160), y + r.uniform(20, 120)), color=cor, fill=cor)
    return pdf.tobytes()


def reescanear(dados, graus=0, recorte=0):
    origem = pymupdf.open(stream=dados, filetype="pdf")
    saida = pymupdf.open()
    for pagina in origem:
        pix = pagina.get_pixmap(dpi=90)
        nova = saida.new_page(width=pagina.rect.width, height=pagina.rect.height)
        r = nova.rect
        nova.insert_image(pymupdf.Rect(r.x0 - recorte, r.y0 - recorte, r.x1 + recorte, r.y1 + recorte), pixmap=pix, rotate=graus)
    return saida.tobytes()


# ── Perturbações dos pares de avaliação ────────────────────
def _ruido_cosmetico(rng, paragrafos):
    texto = "\n".join(paragrafos)

    def hifenizar(t):
        longas = list(re.finditer(r"\b[a-z]{9,}\b", t))
        if not longas:
            return t
        m = rng.choice(longas)
        return t[:m.start() + 4] + "-\n" + t[m.start() + 4:]

    opcoes = {
        "NFD": lambda t: unicodedata.normalize("NFD", t),
        "maiúsculas": str.upper,
        "espaços": lambda t: t.replace(". ", ".   "),
        "hifenização": hifenizar,
        "numeração de página": lambda t: "\n".join(p + (f"\nPágina {k // 5 + 1} de 9" if k % 5 == 4 else "") for k, p in enumerate(t.split("\n"))),
        "travessão": lambda t: t.replace(" - ", " — "),
        "parágrafo quebrado": lambda t: re.sub(r"(\. )(?=[A-Z])", ".\n", t, count=1),
    }
    escolhidas = rng.sample(sorted(opcoes), rng.randint(1, 3))
    novo = texto
    for nome in escolhidas:
        novo = opcoes[nome](novo)
    if novo == texto:
        novo, escolhidas = texto.replace(". ", ".  "), ["espaços"]
    return novo, f"{len(escolhidas)} ruído(s): " + "+".join(sorted(escolhidas))


RE_VERBO = re.compile(rf"\b({'|'.join(VERBOS_NEGAVEIS)})\b")


def _negar(paragrafo):
    return RE_VERBO.sub(r"não \1", paragrafo, count=1)


__all__ = [n for n in dir() if not n.startswith("__")]   # o caderno usa também os nomes com "_"
