# Questão 1 — Comparação de documentos

## Resumo executivo

Preservo cada arquivo e comparo documentos somente dentro do mesmo caso.  
O núcleo usa hash, shingles, diff e alinhamento simples para encontrar cópias e candidatos a versão.  
Prioridade: nunca marcar versão como cópia; toda diferença não cosmética bloqueia “cópia”.  
Casos incertos vão para revisão; o LLM só resume evidências de trechos.  
Meço erros com pares rotulados antes de automatizar decisões de maior risco.

## Representação e escopo

Guardo o arquivo original, o texto extraído e parágrafos com página, seção e offsets. A extração usa PyMuPDF para texto digital e OCR Tesseract em português apenas nas páginas sem texto útil. Para cada parágrafo mantenho hash e shingles de palavras. Campos como partes, valores, datas e negações entram como extensão, para destacar alterações na revisão. Cada resultado registra a versão do extrator e das regras.

| Núcleo determinístico | Extensões (entram quando a medição justificar) |
|---|---|
| Hash de arquivo e de texto, shingles de 5 palavras, Jaccard, fila de candidatos, diff literal e alinhamento simples com `difflib` (cobertura e blocos). Regras determinísticas e revisão dos casos incertos. | Busca semântica com embeddings `multilingual-e5-base`, alinhamento de parágrafos por programação dinâmica, extração de campos, LLM para preparar evidência ambígua, MinHash/LSH para casos grandes. Classificador só após obter rótulos suficientes. |

O processamento é assíncrono e idempotente; reenvio não duplica trabalho. Indexo cada documento antes de compará-lo aos já indexados no caso. Uma chave única `(caso_id, min(doc_id), max(doc_id))` evita pares duplicados quando dois uploads chegam juntos. Enquanto o caso é pequeno, comparo o novo documento com todos os já indexados; quando crescer, MinHash/LSH limita os candidatos. O notebook calcula MinHash (0,47) ao lado do Jaccard exato (0,52), sem usá-lo na decisão. Preservo documentos e histórico; a classificação organiza a revisão, não apaga nem interrompe processos.

## Comparação e decisão

Hash idêntico do arquivo prova igualdade de bytes. Para os demais pares, shingles e Jaccard recuperam candidatos; depois verifico o diff bruto. Jaccard alto pode sugerir derivação, mas nunca basta para declarar cópia. Similaridade semântica recupera paráfrases, mas não substitui o diff: embedding pode considerar parecidas petições com valores ou negações opostos, e a célula 15 do notebook mostra o caso da negação.

Para separar versões de textos que só compartilham vocabulário jurídico comum, identifico frases padrão pela frequência numa coleção histórica independente e retiro seus shingles dos sinais de comparação. A regra lexical inicial é Jaccard ≥0,95 e contenção ≥0,98 nas duas direções. A outra evidência é ter pelo menos três blocos alinhados de 30 tokens, com 50% ou mais dos shingles de cada bloco em IDF ≥1,5. Uma versão abreviada perde shingles e o Jaccard cai; ela passa pelo ramo de blocos. Os cortes são exemplos para validar. O notebook mostra os dois ramos: o de blocos nas células 3 e 5, e os dois juntos na tabela da célula 17, que informa o ramo usado em cada par.

**Cópia:** arquivo idêntico ou derivação sustentada com diff bruto limitado a mudanças cosméticas aprovadas. Caixa ou espaço alterado pode ser “cópia com ressalva”, nunca “cópia exata”. Qualquer outra mudança textual bloqueia cópia. Campos extraídos destacam alterações, mas não liberam cópia se a extração falhar.

**Versão:** há evidência de derivação e diferença textual não cosmética, com cobertura de alinhamento ≥60%. Cobertura entre 20% e 60% é possível reescrita extensa e vai à revisão; abaixo disso, sinais conflitantes também vão à revisão. Os cortes são exemplos iniciais para validação.

**Diferente:** após retirar boilerplate, Jaccard <0,20 e cobertura <20%, com pelo menos 10 shingles em cada texto. Texto vazio/curto ou OCR insuficiente vai à revisão, nunca a “diferente”.

## Documentos longos

- Segmento o arquivo em parágrafos e seções, guardando página e offsets para localizar evidências.
- Comparo trechos correspondentes, não um único vetor do documento inteiro.
- Uso shingles raros como âncoras e alinho parágrafos por seção; no notebook, `SequenceMatcher` é apenas um proxy simples desse alinhamento.
- O LLM recebe somente pequenos trechos ambíguos já alinhados para organizar evidências.
- O documento inteiro nunca entra no contexto do LLM.

## Exemplo trabalhado

1. **Petição A:** Maria Silva pede pagamento de R$ 12.500,00 por serviço entregue e não pago.
2. **Petição B:** Marina Souza pede pagamento de R$ 18.900,00 pelo mesmo tipo de serviço e alega entrega comprovada.
3. Shingles de cinco palavras dão Jaccard aproximado de **0,52** no par sintético da célula 3 do notebook.
4. Esse valor encontra o par como candidato; sozinho não decide a classe.
5. O diff bruto aponta mudança de nome, valor e alguns detalhes da execução.
6. A checagem de campos (extensão) destaca nome e valor, sem ser a única proteção.
7. Três blocos específicos alinhados sustentam derivação; as mudanças não são cosméticas.
8. Resultado: **versão modificada**, com diff e campos destacados para revisão.

## Depois da classificação

Agrupo documentos relacionados por componentes conexos. Só indico ordem A→B→C quando metadados ou histórico sustentam a direção; caso contrário, mostro “relacionado, sem direção”. Cópias mantêm todas as instâncias e podem compartilhar resultado apenas quando arquivo e versão do pipeline coincidem. Reclassificações preservam a decisão anterior e notificam o responsável.

## Operação, segurança e avaliação

Como hipótese de capacidade para a extensão semântica: 1.000 documentos/dia × 20 páginas × 6 parágrafos por página geram cerca de **120 mil embeddings/dia**, ou **1,4 por segundo** em 24 horas. Meço o processamento em lote na CPU; p95 automático de até 10 minutos é uma meta inicial, não SLA. Com cinco minutos por revisão, encaminhar 5% gera 50 revisões/dia (**4,2 horas**) e 10% gera 100 (**8,3 horas**). Acompanho volume e idade da fila; fila alta não relaxa regras de cópia.

Dados e índices ficam isolados por cliente e caso; acesso e envio externo são autorizados e auditados. Registro versões, evidências, diffs e decisões. OCR ruim, conflito entre sinais ou baixa cobertura seguem para revisão humana.

- **Notebook (célula 17):** 27 pares sintéticos, 19 cenários distintos (cópias e cosméticos repetem o mesmo par). O sistema acerta todos, com zero erros versão→cópia, e cobre as cinco classes, incluindo três casos de revisão. O baseline hash + Jaccard comete seis erros versão→cópia e 19 no total; ele não tem as classes “cópia com ressalva” e “revisão necessária”. A matriz demonstra o fluxo, não prevê desempenho em petições reais, e as regras foram escritas junto com os pares.
- **Dados reais:** dois revisores rotulam pares às cegas, sem ver a saída do sistema. Comparo as regras com o baseline e meço matriz de confusão, precisão e recall por classe, recall de candidatos e taxa de revisão, separando calibração e teste por caso. Avalio extração e alinhamento separadamente antes de ampliar automação.
- **Limite estatístico:** a meta inicial é erro versão→cópia ≤1%. Com 20–30 pares só detecto falhas grosseiras; sustentar 1% exige centenas de pares de versão (zero erros em n versões dá limite superior de cerca de 3/n).

## Trade-offs

| Eixo | Escolha inicial | Custo / limite |
|---|---|---|
| Custo | Hash e busca lexical no núcleo; embeddings como extensão. | Embeddings aumentam custo de ingestão. |
| Latência | Fila assíncrona; embeddings pré-calculados quando adicionados. | LLM e revisão aumentam o tempo dos casos ambíguos. |
| Precisão | Diff bruto protege contra falso “cópia”; casos incertos vão a humano. | Mais revisões enquanto a automação é restrita; reduzo apenas após auditoria por classe. |