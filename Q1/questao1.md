# Questão 1 — Comparação de documentos parecidos

## Resumo

**A ideia central:** comparo quanto do conteúdo próprio de um documento reaparece no outro, nos dois sentidos, sem contar texto de modelo e citações. Muito conteúdo próprio em comum indica que um documento deriva do outro; vocabulário jurídico em comum, não.

**Como a similaridade é calculada.** Cada documento novo é comparado com os outros documentos do mesmo caso. A similaridade são **dois percentuais**: **% de A encontrado em B** e **% de B encontrado em A**, isto é, quanto do texto próprio de cada documento está escrito igual no outro. Texto próprio é o texto sem o texto de modelo (aprendido no que se repete entre os outros casos do mesmo cliente) e sem as citações explícitas. A classe sai de regras curtas sobre esses dois percentuais, sobre igualdade e sobre a identidade da peça (partes, processo e tipo de peça). Quando o texto igual fica entre 20% e 60%, os parágrafos reescritos com outras palavras são reconhecidos por embedding e entram na conta.

**Decisões de desenho:**
1. **Cópia só sai por igualdade:** bytes, texto ou texto normalizado iguais, com a extração conferida contra a página. Nenhum limiar produz "cópia". O erro mais caro (tratar uma versão com valor alterado como cópia) só pode vir da extração ou da normalização, e é ali que concentro os testes.
2. **A resposta muda a ação do advogado.** As três classes do enunciado vêm com atributos:
   - cópia *exata* ou *com ressalva*;
   - versão *da mesma peça* (substitui a anterior), *outra peça do caso* (memoriais ou recurso que reaproveitam o texto da inicial; não substitui) ou *outra instância do modelo* (mesmo texto-base, outra parte ou outro processo);
   - relação de *documento inteiro* ou de *trecho* ("a petição está nas págs. 12–30 destes autos").
3. **Só a incerteza alta vai para revisão:** igualdade não confirmada (OCR, extração incompleta ou não confiável) ou cobertura perto de um corte. O revisor escolhe uma das três classes, e essa escolha vira rótulo para calibrar o sistema. O custo dominante é humano, então o desenho reduz esse trabalho com uma fila por documento e um cache de análise por parágrafo.

O código está em `q1.py`; o caderno `demonstracao_questao1.ipynb` executa as demonstrações com dados sintéticos e verifica cada afirmação com `assert`. "§n" indica a seção do caderno.

## Fluxo para cada novo documento

1. **Extrair e normalizar:** texto por página; cabeçalho, imagens e assinatura à parte. A extração roda num worker isolado (container sem rede, sistema de arquivos só leitura, limites de memória, CPU, tamanho, páginas e tempo, um documento por processo) que devolve só texto, posições e hashes: uma falha no parser derruba o worker, não a fila. Arquivo ilegível vira pendência; página sem texto vira pendência de OCR, e o documento é comparado com as páginas lidas.
2. **Indexar:** hashes, fluxo de palavras com parágrafo e página, shingles e citações. Partes e processo são conferidos com o cadastro do caso.
3. **Buscar candidatos no caso:** índices exatos para cópias. Para o resto, todos os documentos do caso enquanto o caso somar até ~2 milhões de palavras (~2 s de comparação por upload), ou um índice de âncoras acima disso.
4. **Comparar e decidir:** alinhar, calcular os dois percentuais, diff e identidade, e aplicar as regras da seção 2.
5. **Agir:** vincular, alertar ou enfileirar para revisão (seção 5).

O processamento é assíncrono e idempotente: o `upload_id` deduplica reenvios. Os documentos de um mesmo caso são processados **em série** (fila particionada por caso); como os casos são pequenos, a vazão vem do paralelismo entre casos. Assim, cada documento é indexado e vê todos os anteriores do caso, sem depender da consistência do índice. A chave única `(caso, documento menor, documento maior, versão do pipeline)` protege contra reentrega da fila.

## 1. Representação

| Representação | Para quê |
|---|---|
| Arquivo original, imutável | auditoria; a classificação não apaga nada |
| SHA-256 dos bytes, do texto e do texto normalizado | cópias achadas em O(1) |
| Verificação de fidelidade (texto invisível, texto coberto, fonte sem mapa de caracteres) e raster da página quando o layout é igual | garante que texto igual é página igual |
| Cabeçalho/rodapé (fora do corpo, dentro da igualdade); impressões de imagens e da assinatura | um nº de processo trocado no cabeçalho ou um carimbo a mais não podem sumir |
| **Fluxo de palavras do documento inteiro**, cada palavra com parágrafo e página | unidade de alinhamento; não depende de onde o extrator quebra os parágrafos |
| Sequências de 5 palavras (shingles), marcadas *de modelo* (repetem-se em vários casos do cliente) ou *do caso* | sementes do alinhamento e âncoras da busca |
| Marcação de citação (aspas longas, "in verbis:") | conteúdo citado não conta como derivação |
| Partes da qualificação, processo do cabeçalho e tipo de peça (inicial, contestação, memoriais, recurso…) | identidade da peça |
| Campos: valores, datas, CPF/CNPJ | destacar alterações (não decidem nada) |
| Embedding por parágrafo | pareamento semântico na faixa ambígua |

**Alternativas consideradas:**

| Abordagem | Ganha | Perde | Papel no desenho |
|---|---|---|---|
| Hash exato | custo zero, prova de igualdade | não vê quase-cópias | detecta cópias |
| **Sementes de shingles + variante do Greedy String Tiling + diff** | explicável, acha trechos movidos e documento dentro de documento, localiza a mudança, barato | não vê paráfrase | **núcleo** |
| Alinhamento por parágrafo | simples | o "parágrafo" do PDF é um bloco de layout | descartado |
| MinHash/LSH | barato em escala | estima Jaccard, que cai com a diferença de tamanho (uma petição dentro de autos 10× maiores parece pouco parecida); na escala de um caso não é preciso índice aproximado | não usado |
| Índice de âncoras (*winnowing* dos shingles específicos) | estima **contenção** nos dois sentidos (petição dentro de autos 10× maiores = 1,0) | só escolhe candidatos | busca de candidatos em casos grandes |
| Cosseno de palavras do documento inteiro | barato | mede tema, não derivação: petições independentes do mesmo modelo têm cosseno > 0,9 nos dados sintéticos | baseline (§10.3) |
| Embeddings por parágrafo | captam paráfrase e parágrafo reescrito | não localizam a mudança palavra a palavra; parágrafos de modelo também ficam parecidos; custo de inferência | **decidem a faixa de 20–60%** (regras 10–12) |
| LLM comparando os dois | entende contexto | caro, lento, difícil de auditar, não cabe documento longo | só resume trechos alterados |

**Extração.** PyMuPDF para PDF digital; páginas sem texto vão para OCR gerenciado (Document AI, Textract ou Azure). Anexos só de imagem usam pHash por página (§7.2), que não enxerga um número trocado e por isso gera só "provável cópia por imagem".

## 2. Quase iguais × vocabulário jurídico parecido

Nos dados sintéticos, petições independentes do mesmo modelo têm cosseno de palavras de 0,90–0,94, mas 0% de texto próprio em comum (§5): o que compartilham é o texto do modelo, que não conta. Quatro mecanismos separam derivação de vocabulário:

1. **Texto de modelo não é evidência, e o modelo é aprendido no histórico do cliente.** Não há lista de textos padrão: cada escritório tem os seus modelos e os redige de um jeito a cada uso. Uma sequência de 5 palavras que aparece em 3 ou mais **outros casos do mesmo cliente** é modelo; o que só aparece no caso atual é conteúdo do caso. O índice fica dentro do cliente e guarda, por caso, o conjunto de sequências como HMAC com chave por cliente (chaves num KMS; o índice de âncoras usa a mesma), para que não permita testar se uma frase aparece no cliente. Um job diário publica um snapshot versionado com a contagem de casos das sequências em 3 ou mais casos, e a consulta desconta o caso atual; os modelos mudam devagar. Sem esse filtro, duas petições diferentes escritas com os mesmos três modelos chegam a 36% de texto em comum, e só o sinal semântico (abaixo) as separa; com ele, ficam em 0% e saem "diferente" (§5).
2. **Citação não é derivação.** No mesmo caso, as peças se citam (a contestação transcreve a inicial). Palavras citadas explicitamente (entre aspas longas ou depois de "in verbis:") não contam nos percentuais e geram o vínculo "cita". Uma contestação que transcreve 3 parágrafos da inicial sai "diferente" (0%); sem as marcas de citação, daria 30% e sairia "diferente" com o vínculo "reaproveita trechos" (§5).
3. **Alinhamento por sementes.** Shingles específicos comuns são estendidos ao maior trecho igual, e os trechos são escolhidos do maior para o menor, sem sobreposição (variante do *Greedy String Tiling*, numa passada). Trechos em sequência formam regiões, e um diff de palavras cobre as lacunas. Regiões com menos de 15 palavras iguais não contam (frases curtas coincidem por acaso). Funciona igual com parágrafos divididos, unidos ou movidos.
4. **Percentual por massa de texto:** a fração das palavras do texto próprio de cada documento que ficam alinhadas no outro.

**O que o histórico reconhece (§5.1, modelos sintéticos com trechos alternativos, partes opcionais e edições soltas a cada uso).** Com ~2% das palavras do modelo mexidas a cada uso, o histórico de 80 casos reconhece 76% do texto de modelo; com variação de 0% a ~20%, o reconhecimento vai de 86% a 24%, e as petições independentes com os mesmos 4 modelos saem 20/20 "diferente" em todos os níveis. Com 0, 5, 10, 20 e 80 casos no histórico, o reconhecimento é de 0%, 5%, 19%, 44% e 76%, e as independentes saem 20/20 "diferente" em todos os tamanhos: sem histórico, o modelo conta como texto em comum, mas os fatos de uma não têm par semântico na outra.

- O que não é reconhecido sobe o texto em comum e leva o par para a faixa semântica (regras 10–12), nunca para "versão" falsa.
- **Cliente sem histórico** (menos de 20 casos): o modelo ainda conta como texto em comum. "Diferente" continua seguro, mas "versão" automática exige ≥90% nos dois sentidos. Quando o índice ganha um snapshot novo, os pares em revisão sem decisão humana são recomparados, e os que deixam de ser ambíguos saem da fila (§9.5). Decisões já entregues não são rebaixadas automaticamente; uma mudança nelas vira alerta para o revisor.
- **Efeito colateral:** frases de fatos que se repetem entre casos do cliente também contam como modelo (33–42% das palavras de fatos no gerador), e frase repetida em vários casos não prova derivação. **O resultado não depende disso:** com um histórico sem os parágrafos de fatos, as petições independentes continuam 20/20 "diferente", e a avaliação dá 0 erros e 8,0% de revisão (§5.1, §10.3).
- **Contencioso de massa (§5.2):** 300 casos contra o mesmo réu, com os 10 modelos e uma frase de fatos. O texto próprio cai para 11–24% das palavras (nomes, CPF, valores, datas, edições soltas no modelo), 44–84 sequências, e ainda decide: valor corrigido → 20/20 "versão · mesma peça" com alerta de valor; reexportada → 20/20 "cópia com ressalva"; independentes e contestação → 20/20 "diferente". Sem o filtro de modelo, as independentes de massa viram "versão" falsa (14 nos pares de massa da §10.3).

**Por que dois percentuais.** Um número só não distingue as situações. Uma petição de 10 páginas dentro de autos de 40 dá 100% × 25% (trecho, "contém, págs. x–y"); o exemplo do enunciado, 84% × 84% (versão); o mesmo texto, 100% × 100%. O maior dos dois percentuais diz se um documento saiu do outro (≥60%); o menor diz se é o documento inteiro (≥50%) ou um trecho dentro de um documento maior.

**Regras, aplicadas em ordem (a primeira que vale decide):**

| # | Condição | Resultado |
|---|---|---|
| 1 | bytes iguais | cópia · exata |
| 2 | nenhuma página com texto | em revisão (pendência do documento) |
| 2a | texto lido igual, mas extração incompleta (página sem texto, PDF reparado) ou não confiável; ou layout igual e página renderizada diferente | em revisão: "confirmar depois do OCR" ou "conferir o original" |
| 3 | texto e cabeçalho iguais; mesmas imagens e presença de assinatura; extração confiável e, com o mesmo layout, a mesma página renderizada | cópia · exata |
| 4 | o mesmo que a 3, com imagem/assinatura diferente (a assinatura é detectada, não validada) ou igual após normalização (caixa, espaços, Unicode, hifenização entre letras, linhas "Página N de M") | cópia · com ressalva (+ alerta se mudou assinatura ou carimbo) |
| 4a | menos de 10 shingles específicos, com o mesmo tipo de peça, as mesmas partes por CPF/CNPJ e o mesmo processo | decide pelo **texto inteiro** (com modelo), com os mesmos cortes; nunca cópia |
| 5 | menos de 10 shingles específicos em algum lado | em revisão |
| 6 | texto de OCR e as diferenças são só confusões de letras (rn/m, l/1, o/0, acento) ou número × número | em revisão: "provável cópia (OCR)", em lote só se nenhum número ou campo difere |
| 7 | um dos dois percentuais ≥60% **e** os dois ≥50% | versão · mesma peça, outra peça do caso ou outra instância |
| 8 | um dos dois ≥60%, o outro <50%, o documento maior tem pelo menos o dobro do texto próprio do menor e o texto encontrado está **contíguo** nele | regras 1, 3, 4 e 7 aplicadas ao **trecho**, com as páginas; cópia do trecho só com a mesma identidade. Sem a diferença de tamanho, o percentual baixo vem de reescrita: regras 10–12 |
| 9 | os dois percentuais <20% | diferente (com o vínculo "cita", se houver citação), salvo a exceção da reescrita (abaixo) |
| 10 | literal entre 20% e 60% e cobertura total ≥65% num sentido **e** ≥50% no outro | a regra 7 com a cobertura total: **versão**, com o diff nos trechos literais e os parágrafos reescritos lado a lado |
| 11 | literal entre 20% e 60% e cobertura total <55% nos dois sentidos, mesmo com o corte mínimo | **diferente**, com o vínculo "reaproveita trechos de X (x%, págs. …)" |
| 12 | o resto: cobertura total entre 55% e 65%, ou texto espalhado dentro de um documento maior | em revisão |

A extração pode divergir do que se vê: fonte sem mapa de caracteres, texto coberto ou invisível, número desenhado. Um documento com qualquer um desses sinais não sai "cópia" por texto (um PDF escaneado com camada de OCR invisível também cai aqui), e, com o mesmo layout, a página renderizada também tem de ser igual (§7.3). Na regra 4a, duas peças do mesmo tipo e das mesmas partes no mesmo caso não são "petições independentes do mesmo modelo", então o risco que o filtro evita não existe. Nos dados de massa ela não dispara; num caso montado só com qualificação e modelos, decide a mesma peça e deixa de fora a de outro CPF (§5.2). Na regra 6, número contra número nunca é ruído: "R$ 49.407,65" × "R$ 99.407,65" pode ser OCR ou valor alterado, e só o original decide.

**Faixa ambígua: sinal semântico.** Na faixa de 20–60%, contando só texto igual, dois casos dão o mesmo número: a mesma peça muito reescrita e outra peça que copiou alguns parágrafos sem aspas. O pareamento semântico separa os dois:
- entram só os parágrafos com texto próprio que **não** foi alinhado literalmente (sem modelo nem citação). Como o modelo já saiu, o "tema parecido" não volta;
- cada um ganha um embedding (`paraphrase-multilingual-mpnet-base-v2`), calculado uma vez por parágrafo e guardado, só para os pares que caem na faixa;
- os parágrafos de A e de B são pareados na ordem dos dois documentos (o mesmo encadeamento das regiões), cobrindo o máximo de palavras;
- **um par não contradiz os valores do caso:** se os dois parágrafos têm datas, valores, CPF/CNPJ ou números, precisam ter pelo menos um em comum. A qualificação de outra parte e o pedido de outro valor têm a mesma estrutura e cosseno de até 0,97, com outros fatos; quem reescreve os mesmos fatos mantém os valores;
- **cobertura total** = % das palavras do texto próprio cobertas por alinhamento literal **ou** por par semântico, nos dois sentidos.

**Dois cortes de cosseno, um para cada erro**, calibrados numa amostra de 305 paráfrases e 610 pares de outro fato (§10.1). Fatos diferentes da mesma área chegam a 0,9 de cosseno, então um corte só não separa:
- **0,875** para o par que conta para "versão": o menor corte com ≤1% de falso par só pelo cosseno (a 0,85, 3,1%);
- **0,725** para o par *possível*, que só impede "diferente": o maior corte que ainda acha ≥99% das paráfrases. Uma paráfrase que o embedding não reconhece com o corte alto vai para revisão, nunca para "diferente" em silêncio.

Na peça reescrita, os parágrafos reescritos encontram par e a cobertura passa de 65%; na outra peça, o resto não tem par nem com o corte mínimo e ela fica abaixo de 55%. No teste (§10.2), 13 das 19 reescritas extensas saem "versão" e 6 vão para revisão; os 37 pares com trechos reaproveitados sem aspas saem "diferente". O sinal semântico nunca produz "cópia" e não roda abaixo de 20% literal. Exceção: dois documentos do mesmo tipo de peça, das mesmas partes e do mesmo processo, com menos de 20% literal e cobertura semântica ≥60% nos dois sentidos, vão para revisão como "possível reescrita da mesma peça"; fora dessa identidade, abaixo de 20% continua "diferente". Na faixa, só a margem de ±5 pontos em volta de 60% de cobertura total vai para revisão. Os cortes de cobertura (3 casos, 20%, 50%, 60%, 55%, 65%) são pontos de partida, a calibrar com pares rotulados (§10.5).

**Mesma peça × outra peça × outra instância.** No mesmo caso, as peças têm as mesmas partes e o mesmo processo, e é comum uma repetir o texto de outra. Por isso a identidade tem três partes:
- **tipo de peça**, lido no título ("AÇÃO DE…", "CONTESTAÇÃO", "MEMORIAIS", "APELAÇÃO") ou no metadado do protocolo. Tipo diferente → *outra peça do caso*: memoriais que repetem os fatos da inicial (81% da inicial está nos memoriais) não a substituem;
- **partes**, do parágrafo de qualificação, e **processo**, do cabeçalho. Diferentes → *outra instância do modelo*. A parte é identificada pelo **CPF/CNPJ**, e o nome só desempata: mesmo CPF com o nome digitado errado é a mesma parte; "Maria da Silva Souza" × "Marina da Silva Souza" com CPFs diferentes são duas pessoas. Testemunhas, advogados e precedentes não contam. Dentro de um caso isso é raro e quer dizer: (a) peça de outro processo juntada aos autos (precedente, petição de litisconsorte); (b) documento no caso errado, com o alerta de cadastro (§5); (c) na extensão entre casos do mesmo cliente (§6), o caso comum;
- num **trecho** (peça dentro dos autos), vale o processo do trecho ou, se ele não traz nenhum, o dos autos ou o do cadastro do caso. Uma peça de outro processo dentro dos autos nunca é "cópia" do trecho.

Os 53 casos de borda da §4.2 incluem esses negativos.

**Exemplo do enunciado (§4.1):** "MARIA SILVA… R$ 12.500,00… 10 de abril de 2024" × "MARINA SOUZA… R$ 18.900,00… 22 de maio de 2024". O enunciado não diz que as duas estão no mesmo caso; se estivessem, a parte fora do cadastro também geraria alerta na ingestão.
1. **84%** de cada um encontrado no outro: um saiu do outro.
2. O diff destaca valor, data e CPF, com a página.
3. A parte da qualificação mudou. Resultado: **versão · outra instância do modelo**, e o aviso de que um documento não substitui o outro.

## 3. Documentos longos

A comparação não usa LLM. Dois documentos de **286 páginas** (105 mil palavras) são comparados em **0,13 s**, com as seis alterações localizadas por página (§6). Um documento **dentro** de outro (autos, peça com anexos) vira uma relação por trecho. O embedding é por parágrafo, então o tamanho do documento não esbarra no contexto do modelo.

O LLM é opcional e só resume as mudanças para o revisor:
- recebe os trechos alterados (**~1.100 tokens**, contra **~152 mil** do documento);
- partes, CPF, CNPJ, processo, endereço, CEP, e-mail, telefone e OAB vão pseudonimizados por lista de padrões + NER (que pega nomes de terceiros); categorias sensíveis da LGPD (saúde, biometria) vão mascaradas;
- o texto da peça vai como dado, com a instrução de ignorar instruções escritas nele (*prompt injection*); a resposta só é aceita no formato combinado (id, frase curta, relevância), e qualquer outra chave, como uma "classe", descarta o item;
- a resposta é exibida como texto escapado, ao lado do diff, que ela nunca substitui; "relevância baixa" não esconde um item com campo ou negação alterados (essa marcação vem do diff);
- nunca decide a classe: o pior efeito de uma injeção é um resumo errado.

## 4. Avaliação

**Método (dados reais):**
- Dois revisores rotulam pares às cegas, amostrados por faixa de similaridade, com concordância medida (kappa).
- Calibração e teste ficam separados por caso.
- Métricas: **precisão e recall por classe**, com atenção especial a versão → cópia (o erro crítico); diferente ↔ versão; abstenção **por documento**; **acurácia do subtipo** (mesma peça × outra peça × outra instância) nos pares "versão" e da extração de tipo de peça e de CPF/CNPJ por documento; recall de candidatos, alinhamento e extração, à parte.
- Para afirmar erro ≤ 1% com zero erros observados, são precisos ~300 pares por classe (regra de três).
- **Auditoria contínua:** uma amostra aleatória de 1% das decisões automáticas, estratificada por classe e faixa de percentual, vai para revisão às cegas. É a única forma de medir o erro onde ninguém olha; os rótulos da fila só cobrem a faixa ambígua. A 1 mil docs/dia são ~9 documentos auditados por dia, ~2 com cópia: ~300 cópias auditadas em ~150 dias (estimativa com a fração de cópias da §10).

**Teste das invariantes (dados sintéticos, §10).** Os dados sintéticos testam se as garantias do desenho se mantêm sob perturbações conhecidas. Não estimam a precisão em petições reais (o gerador e as regras têm o mesmo autor); isso vem do método acima. Limiares fixados antes de gerar o teste de 860 pares (com novo scan com valor trocado, memoriais que repetem os fatos e 60 pares de massa). Baselines por ablação; os cortes do cosseno foram escolhidos no conjunto de calibração (cópia ≥ 1,00, versão ≥ 0,96):

| | Sistema | Sem filtro de modelo | Contenção de conjuntos, sem alinhamento | Hash + cosseno do documento inteiro (calibrado) |
|---|---|---|---|---|
| falso "cópia" | **0** | 0 | 0 | 18 |
| diferente → versão | **0** | 14 | 0 | 39 |
| versão → diferente | **0** | 0 | 0 | 18 |
| erros de classe (total) | **0** | 14 | 11 | 234 |
| em revisão (por par) | **10,9%** | 26,4% | 13,8% | 0% |

- **Versão → cópia: 0/432**, com limite superior exato de 0,69% a 95%. Nenhuma versão saiu como "provável cópia (OCR)", e nenhum dos 21 memoriais como "mesma peça".
- Nenhum erro de classe nos 860 pares. O que não foi decidido foi para revisão: novo scan com valor trocado (30), reescrita extensa (24), extração falha (15), novo scan com OCR (11), modelo que o cliente nunca usou (9), trechos reaproveitados sem marca de citação (5). As 41 petições independentes escritas com os mesmos 4 modelos e as 30 de massa saíram todas como "diferente".
- **Os limiares são pouco testados por estes dados:** com o corte de derivação de 0,10 a 0,90, as versões reconhecidas vão de 86% a 80% (§10.5).

**Por par × por documento.** Uma abstenção por par `p` vira `1 − (1 − p)ⁿ` por documento (30 comparações: 1% por par → 26% dos documentos); por isso a fila agrega por documento.

## 5. Depois da classificação

A classificação organiza o caso: não apaga nem substitui documentos (§9).

| Resultado | Ação |
|---|---|
| Cópia | Agrupa as instâncias, avisa que o documento já existe no caso e reaproveita as análises. |
| Versão · mesma peça | Liga ao anterior e mostra o diff com a página. Alerta mudanças em valor, data, CPF, cabeçalho ou negação. |
| Versão · outra peça do caso | Vínculo "reaproveita x% do texto de", com o diff; **não substitui** a anterior nem entra no grupo. |
| Versão · outra instância | Liga como "mesmo modelo" e avisa que **não substitui** o anterior. No mesmo caso, vem junto com o alerta de cadastro quando as partes não são as do caso. |
| Trecho | Vínculo "contém, págs. x–y", fora do grupo. Trecho de outra peça ou de outro processo gera aviso. |
| Diferente com citação ou reaproveitamento | Vínculo informativo "cita" ou "reaproveita trechos de". |
| Em revisão | **Um** item de fila por documento, com os pares ambíguos, os motivos e o resumo do LLM. "Provável cópia (OCR)" sem número ou campo divergente e "provável cópia por imagem" são confirmadas em lote. |

- **Cadastro do caso:** um documento com partes ou processo fora do cadastro gera alerta logo na ingestão.
- **Cache por parágrafo**, escopado por cliente: uma nova versão só paga pelo que mudou (99,7% dos tokens poupados num documento de 286 páginas com 5 parágrafos alterados).
- **Direção** (A → B) só com metadado confiável (data de protocolo).
- **Grupos** podem não ser transitivos (A~B, B~C, A≁C), e a interface mostra isso.
- **Rastreabilidade:** cada decisão grava a versão do pipeline e a do snapshot do índice de modelo usadas.
- **Decisão do revisor:** vale sobre a do sistema enquanto a evidência for a mesma (hash do texto dos dois documentos) e vira rótulo. Se a evidência mudar, o par volta à fila com a decisão anterior visível; mudança só de versão do pipeline ou do índice não o reabre, e a divergência fica registrada (§9).
- **Evidência nova:** OCR concluído, cadastro do caso corrigido ou data de protocolo recebida geram um evento que recompara os pares do documento (ou recalcula alertas e direção). As decisões novas substituem as anteriores, que ficam no histórico (§9).
- **Nova versão do pipeline:** cada caso tem uma versão ativa. A nova reprocessa o caso em segundo plano (300 documentos em ~1 s, §9.4) e só então troca o ponteiro; grupos, fila e alertas leem só a versão ativa.
- **Exclusão (LGPD, fim de contrato):** apagar um caso remove os arquivos, os pares e o cache dele e o tira do índice de modelo no próximo snapshot (o índice guarda o conjunto de cada caso); os rótulos são anonimizados ou apagados.

## 6. Trade-offs

Tempos medidos e extrapolados para 1 mil documentos/dia, 30 documentos por caso, 5 min por revisão e OCR gerenciado a ~US$ 1,50 por mil páginas em 10% delas (preço a conferir) (§11). A abstenção por par em produção é desconhecida: os cenários são hipóteses (no caso sintético de 300 documentos, 0,02% por par).

| Abstenção por par (hipótese) | Docs com revisão | Revisão/dia | LLM/dia | OCR/dia | CPU/dia |
|---|---|---|---|---|---|
| 0,2% | 5,8% | 4,9 h | ~R$ 2 | ~R$ 16 | ~R$ 0,03 |
| 1,2% | 30% | 25 h | ~R$ 12 | ~R$ 16 | ~R$ 0,03 |

- **Precisão × custo:** a revisão humana custa mais de dez vezes CPU, OCR e LLM somados, então a alavanca é rotular bem e calibrar, não relaxar regras. A auditoria de 1% acrescenta ~9 revisões/dia (~0,8 h). Embeddings (estimativa): ~120 mil parágrafos/dia, calculados uma vez na ingestão; a busca é dentro do caso, sem índice vetorial.
- **Escala:** a comparação só dentro do caso cresce linear com o volume (100 mil docs/dia ≈ 10 vCPU-hora/dia, mais ~R$ 1,6 mil/dia de OCR). Até ~2 milhões de palavras no caso, comparo com todos; o limite é por volume porque 200 autos de 300 páginas custam ~22 s por upload e 200 petições de 2 páginas, 0,2 s. Acima disso, índices exatos e o índice de âncoras escolhem os candidatos (contenção estimada ≥ 10%). Num caso de 300 documentos, a plataforma compara 1.780 de 44.850 pares, com **100% de recall** dos pares relevantes (§8, §9.4). O índice de modelo cresce com o histórico do cliente, não com o caso. Estimativa para um cliente de 100 mil casos: centenas de milhões de sequências distintas; o snapshot guarda só as de 3 ou mais casos (14% na §5.1), ~1 GB. Os conjuntos por caso ficam no armazenamento de objetos, lidos só pelo job em lote que reconstrói o snapshot e na exclusão de um caso.
- **Latência:** documento mediano em ~0,4 s sem OCR; p95 simulado ≈ 20 s com OCR. A verificação de fidelidade custa ~4 ms por página e o raster ~1 ms por página, só nos pares que iam sair cópia. O snapshot do índice de modelo fica em memória no worker (mapa exato, com a contagem), sem chamada remota por sequência.

**Fora do escopo do enunciado:** a mesma máquina entre casos do mesmo cliente, para demandas repetidas e possível litispendência.

**Limitações:**
- Dados sintéticos; OCR, LLM e embeddings não foram executados. O corte de 0,85 e as margens de 55%/65% não foram medidos; na §4, as reescritas extensas aparecem em revisão porque o caderno não roda embeddings.
- Citação só é detectada quando marcada (aspas longas, "in verbis:"); o recuo do bloco no PDF seria um sinal a mais.
- O tipo de peça e as partes vêm do título e da qualificação (heurística); em produção, o metadado do protocolo e o cadastro do caso.
- Um novo scan com número mal lido vai para conferência item a item: sem o original, erro de OCR e valor alterado são indistinguíveis.
- Cliente novo (menos de 20 casos) e modelo novo (menos de 3 casos, 0% reconhecido antes disso) geram revisões, que saem da fila sozinhas quando o histórico cresce.
- O pHash só cobre anexos só de imagem entre si (um scan de documento digital é coberto pelo OCR) e perde parte dos scans com recorte grande.
- A pontuação é tratada como material, uma escolha conservadora.
