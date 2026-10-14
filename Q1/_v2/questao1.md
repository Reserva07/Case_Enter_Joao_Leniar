# Questão 1 — Comparação de documentos parecidos

## Resumo

**Como a similaridade é calculada.** Para cada documento novo, comparo com os outros documentos do mesmo caso. A similaridade é a **cobertura**: a fração do conteúdo *específico* de um documento (sem o texto padrão jurídico) que reaparece, parágrafo a parágrafo, no outro. Ela é calculada nos dois sentidos. A classe sai de regras curtas sobre a cobertura, sobre igualdade e sobre a identidade da peça (partes e processo).

**Decisões de desenho:**
1. **Cópia só sai por igualdade:** bytes, texto ou texto normalizado iguais. Nenhum limiar produz “cópia”. Assim, o erro mais caro, tratar uma versão com valor alterado como cópia, só pode vir da extração ou da normalização, e é ali que concentro os testes.
2. **A resposta muda a ação do advogado.** As três classes do enunciado vêm com atributos:
   - cópia *exata* ou *com ressalva*;
   - versão *da mesma peça* (substitui a anterior) ou *outra instância do modelo* (mesmo texto-base, outra parte ou outro processo);
   - relação de *documento inteiro* ou de *trecho* (“a petição está nas págs. 12–30 destes autos”).
3. **Na dúvida, “em revisão”.** É um estado temporário: o revisor escolhe uma das três classes, e essa escolha vira rótulo para calibrar o sistema. Como o custo dominante é humano, o desenho reduz esse trabalho com uma fila por documento, um cache de análise por parágrafo e, numa segunda fase, um classificador que só automatiza o que consegue certificar.

O caderno `demonstracao_questao1.ipynb` implementa tudo com dados sintéticos e verifica cada afirmação com `assert` (§n = seção do caderno).

## Fluxo para cada novo documento

1. **Extrair e normalizar:** texto por página; cabeçalho, imagens e assinatura guardados à parte. Arquivo ilegível vira pendência, não erro.
2. **Indexar:** hashes, parágrafos e shingles; conferência das partes e do processo com o cadastro do caso.
3. **Buscar candidatos no caso:** índices exatos (cópias) e, para o resto, todos os documentos do caso (até ~200) ou um índice de âncoras por contenção (casos maiores).
4. **Comparar e decidir:** para cada candidato, calcular a evidência (coberturas, diff, campos, identidade) e aplicar as regras da seção 2.
5. **Agir:** vincular, alertar ou enfileirar para revisão (seção 5).

O processamento é assíncrono e idempotente. Cada documento é indexado antes de ser comparado, e uma chave única impede pares duplicados em uploads simultâneos.

## 1. Representação

| Representação | Para quê |
|---|---|
| Arquivo original, imutável | auditoria; nada é apagado |
| SHA-256 dos bytes, do texto e do texto normalizado | cópias achadas em O(1) |
| Cabeçalho/rodapé (fora do corpo, dentro da igualdade) e impressões de imagens e assinatura | um nº de processo trocado no cabeçalho ou um carimbo a mais não podem sumir |
| Partes da qualificação e processo do cabeçalho | identidade da peça |
| Parágrafos (trechos) com página e offsets | unidade de alinhamento, de evidência e de cache |
| Shingles de 5 palavras, marcados *padrão* ou *específicos* | âncoras do alinhamento e da busca de candidatos |
| Campos: valores, datas, CPF/CNPJ | destacar alterações (não decidem nada) |

**Alternativas consideradas:**

| Abordagem | Ganha | Perde | Papel no desenho |
|---|---|---|---|
| Hash exato | custo zero, prova de igualdade | não vê quase-cópias | detecta cópias |
| MinHash/LSH | barato, escala | estima Jaccard, que é simétrico e cai com a diferença de tamanho: não acha documento contido em outro (petição dentro dos autos) | não usado |
| Índice de âncoras (*winnowing* dos shingles específicos) | estima **contenção** nos dois sentidos; acha trechos | índice maior que uma assinatura fixa | busca de candidatos em casos grandes |
| Embeddings | captam paráfrases | medem semelhança de sentido, não diferença material (um “não”, um valor); custo de ingestão | extensão: só recuperam paráfrases |
| LLM comparando os dois | entende contexto | caro, lento, difícil de auditar, não cabe documento longo | só resume trechos alterados |
| **Shingles + alinhamento por parágrafo** | explicável, localiza a mudança, barato | não vê paráfrase | **núcleo** |

**Extração.** PyMuPDF; OCR só em páginas sem texto. Anexos digitalizados sem texto (RG, comprovantes) usam um hash perceptual por página (§8.4). Como ele não enxerga um número trocado, só gera “provável cópia por imagem” para confirmação.

## 2. Quase iguais × vocabulário jurídico parecido

Petições independentes da mesma área têm cosseno de palavras de 0,91–0,94 e **0%** de conteúdo específico alinhado (§5). Três mecanismos separam as duas coisas:

1. **Texto padrão não é evidência.** Um shingle presente em ≥5% de uma coleção de referência (“Ante o exposto…”) não conta. A coleção vem de modelos públicos e do próprio escritório e guarda só contagens de hashes.
2. **Alinhamento por parágrafo.** Shingles específicos ligam parágrafos de A e B. Grupos 1:1 ou 1:N (parágrafo dividido por outro extrator) são aceitos, e a ordem não importa.
3. **Cobertura por massa de texto:** dentro de cada grupo alinhado, um diff conta as palavras específicas que se mantiveram.

**Por que duas coberturas, e não Jaccard ou cosseno.** O Jaccard (`|A∩B| / |A∪B|`) responde “quanto os dois são o mesmo conjunto”. Num documento jurídico, a pergunta certa é **contenção**: quanto de A está em B, e quanto de B está em A. O Jaccard é simétrico e cai com a diferença de tamanho: uma petição inteira dentro de autos de 200 parágrafos tem Jaccard 0,07 e contenção 1,0 (§9). Ele também depende do tamanho absoluto (numa petição curta, trocar só o valor já o derruba). E um número só não distingue “B é versão de A” de “A está dentro de B” nem de “B é A abreviado”, nem diz o que mudou. A cobertura do documento menor diz se ele foi derivado; a do maior diz se o resto do maior também vem dele.

**Regras, aplicadas em ordem (a primeira que vale decide):**

| # | Condição | Resultado |
|---|---|---|
| 1 | bytes iguais; ou texto, cabeçalho e imagens iguais | cópia · exata |
| 2 | texto igual mas imagem/assinatura diferente; ou igual após normalização (caixa, espaços, Unicode, hifenização, paginação) | cópia · com ressalva (+ alerta se mudou assinatura ou carimbo) |
| 3 | extração falhou ou texto específico insuficiente | em revisão |
| 4 | ≥60% do menor reaparece no maior **e** ≥50% do maior é coberto | versão · mesma peça ou outra instância |
| 5 | ≥60% do menor reaparece no maior, mas <50% do maior, de forma **contígua** | regras 1, 2 e 4 aplicadas ao **trecho**, com as páginas |
| 6 | <20% em comum | diferente |
| 7 | o resto (20–60%: reescrita extensa, trechos reaproveitados; ou menor espalhado no maior) | em revisão |

Os cortes (5%, 20%, 50%, 60%) são pontos de partida, a calibrar com pares rotulados (§11.2).

**Mesma peça × outra instância.** A identidade vem do parágrafo de qualificação (partes) e do cabeçalho (processo). Nomes de testemunhas, advogados e processos citados como precedente não contam, e um nome com erro de digitação continua sendo a mesma parte. São 34 casos de borda, incluindo esses negativos (§4.2).

**Exemplo trabalhado (§4.1).** O caso do enunciado: mesma tese, com nome, valor, data e parágrafos diferentes. “MARIA SILVA… R$ 12.500,00… 10 de abril de 2024” × “MARINA SOUZA… R$ 18.900,00… 22 de maio de 2024”:
1. Os 5 parágrafos se alinham, com cobertura de **84%** nos dois sentidos: há derivação. Para contraste, o Jaccard seria 0,49, um “meio parecido” que não diz se há derivação nem o que mudou.
2. O diff destaca valor, data e CPF, com a página.
3. A parte da qualificação mudou. Resultado: **versão · outra instância do modelo**. O sistema avisa que um documento não substitui o outro.

## 3. Documentos longos

A comparação não usa LLM: o índice invertido só compara parágrafos com âncoras em comum, e o diff roda dentro dos grupos. Dois documentos de **286 páginas** são comparados em **~0,2 s**, com as seis alterações localizadas por página (§7). Um documento **dentro** de outro (autos, peça com anexos) vira uma relação por trecho.

O LLM é opcional e só resume as mudanças para o revisor:
- recebe os trechos alterados (**~830 tokens**, contra **~113 mil** do documento);
- partes, CPF, CNPJ, processo, e-mail e telefone vão pseudonimizados;
- nunca decide a classe.

## 4. Avaliação

**Método (dados reais):**
- Dois revisores rotulam pares às cegas, sem ver a saída do sistema. Os pares são amostrados por faixa de cobertura, para garantir casos difíceis, e a concordância entre eles é medida (kappa).
- Calibração e teste ficam separados por caso.
- Métricas: **precisão e recall por classe**, com atenção especial a versão → cópia (o erro crítico); diferente ↔ versão; abstenção **por documento**; e recall de candidatos, alinhamento e extração medidos à parte.
- Para certificar 1% de erro com zero erros observados, são precisos ~300 pares por classe (regra de três).
- Em produção, começo em *shadow mode* e acompanho a correção do revisor por classe.

**Demonstração (dados sintéticos, §11).** Os limiares foram fixados antes de gerar o conjunto de teste de 800 pares:

| | Sistema | Baseline hash + Jaccard |
|---|---|---|
| versão → cópia | **0 / 407** (limite superior exato 95%: 0,73%) | 182 / 407 |
| diferente → versão | 0 | 47 |
| precisão por classe | 100% nas quatro classes | 16% (cópia) a 100% |
| recall por classe | 77% (cópia) a 100%; o resto vai para revisão | 0% (com ressalva) a 75% |
| abstenção por par | 10,1% | — |

O que falta para 100% de recall foi para revisão: extração falha, reescrita extensa, texto padrão desconhecido e trechos reaproveitados. O gerador e as regras são meus, então isso mede robustez a perturbações conhecidas, não desempenho real.

**Por par × por documento.** Um documento novo é comparado com todos os do caso, então uma abstenção por par `p` vira `1 − (1 − p)ⁿ`: com 30 comparações, 1% por par já vira 26% dos documentos. Por isso a fila agrega por documento.

## 5. Depois da classificação

A classificação organiza o caso: não apaga nem substitui documentos (§8, §10).

| Resultado | Ação |
|---|---|
| Cópia | Agrupa as instâncias e avisa que o documento já existe no caso (evita protocolar duas vezes). Reaproveita as análises. |
| Versão · mesma peça | Liga ao anterior, mostra o diff com a página e alerta mudanças em valor, data, CPF, cabeçalho ou negação. |
| Versão · outra instância | Liga como “mesmo modelo” e avisa que **não substitui** o anterior. |
| Trecho | Vínculo “contém, págs. x–y”. Não diz “já existe” e não junta os dois no mesmo grupo. |
| Em revisão | **Um** item de fila por documento, com os pares ambíguos, os motivos e o resumo do LLM. O revisor decide entre as três classes. |

- **Cadastro do caso:** um documento com partes ou processo fora do cadastro gera alerta logo na ingestão.
- **Cache por parágrafo**, escopado por cliente: uma nova versão só paga pelo que mudou (99,7% dos tokens de análise poupados num documento de 286 páginas com 5 parágrafos alterados). Análises globais, como o resumo, são refeitas a partir do diff.
- **Direção** (A → B) só com metadado confiável (data de protocolo).
- **Revisão** preserva a decisão do sistema e vira rótulo.
- **Nova versão do pipeline** grava novas linhas, mantendo as antigas.

## 6. Trade-offs

Tempos medidos e extrapolados para 1 mil documentos/dia, com 30 documentos por caso e 5 min por revisão (§12). A máquina custa centavos por dia; a revisão domina:

| Abstenção por par | Docs com revisão | Revisão/dia | Com classificador (fase 2) | LLM/dia |
|---|---|---|---|---|
| 0,2% | 5,8% | 4,9 h | 1,1–4,6 h | ~R$ 2 |
| 1,2% | 30% | 25 h | 5,9–23,8 h | ~R$ 11 |

- **Precisão × custo:** a invariante da cópia e a abstenção custam revisões. A revisão humana custa mais de dez vezes CPU e LLM somados, então a alavanca é rotular bem e calibrar, não relaxar regras. O desenho escolhe precisão (nenhuma versão chamada de cópia) e paga com recall (casos ambíguos para humanos).
- **Escala:** a comparação só dentro do caso cresce linear com o volume (100 mil docs/dia ≈ 120 vCPU-hora/dia). Até ~200 documentos por caso, comparo com todos (barato e exato). Acima disso, índices exatos e um índice de âncoras escolhem os candidatos. As âncoras são as impressões dos shingles específicos, por *winnowing*. Vira candidato quem tem contenção estimada ≥ 10%, metade do corte de “diferente”. Num caso de 300 documentos, a plataforma compara 2.364 de 44.850 pares, com **100% de recall** (§9). O índice também acha documento dentro de autos, que uma busca por Jaccard (MinHash/LSH) perderia.
- **Latência:** documento mediano em ~0,2 s sem OCR; p95 simulado ≈ 20 s com OCR. O risco é a fila em picos, não a comparação.

**Evolução:**
1. **Fase 1:** regras + atributos + cache, em *shadow mode*.
2. **Fase 2:** na faixa ambígua, um classificador calibrado (regressão logística sobre as evidências e, em produção, o veredito de um LLM) decide só quando o limite superior exato do risco fica ≤ 2%. Ele nunca produz “cópia”. No caderno (§11.3), corta 77% das revisões com rótulos limpos e só 6% com 5% de rótulos trocados: a automação depende da qualidade dos rótulos e supõe que calibração e produção venham da mesma distribuição.
3. **Fora do escopo do enunciado:** a mesma máquina entre casos do mesmo cliente, para demandas repetidas e possível litispendência.

**Limitações:**
- Dados sintéticos; OCR, embeddings e LLM foram simulados.
- A extração de partes é heurística (em produção, NER ou LLM conferido com o cadastro).
- Nomes de terceiros fora da qualificação não são pseudonimizados.
- Cliente novo começa só com o texto padrão de modelos públicos e tem mais revisões até acumular histórico.
- O hash perceptual perde parte dos scans com recorte grande.
- A pontuação é tratada como material, uma escolha conservadora.
