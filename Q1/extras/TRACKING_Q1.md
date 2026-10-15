# Tracking — Questão 1 (o que falta fazer)

Só o que falta fazer. O porquê de cada decisão fica em `DECISOES_Q1.md`.

**Entrega:** `questao1.md`, `demonstracao_questao1.ipynb`, `q1.py` (solução), `sinteticos.py` (dados sintéticos; lê `parafrases_q1.json`), `avaliacao.py`, `parafrases_q1.json`, `parafrases_reais_q1.json` (paráfrases de parágrafos reais), `sentencas_tjsp.json` (texto real pseudonimizado), `coletar_sentencas.py` (como o corpus foi gerado; não roda no caderno), `requirements.txt` e o PDF anexo.
**Organização (2026-10-14):** a pasta `Q1/` tem só os entregáveis. Tudo o que não vai na entrega fica em `Q1/extras/` (`TRACKING_Q1.md`, `DECISOES_Q1.md`, `DIAGRAMA_Q1.md`, `Enunciado_q1.md`, `gerar_anexo.py`, `_v1/`, `_v2/`). O `gerar_anexo.py` roda da pasta `Q1` (`.venv/bin/python extras/gerar_anexo.py`) e grava o PDF em `Q1/`. Não enviar: `.venv/`, `__pycache__/` e `extras/`.

## Correções de funcionalidade

- [x] **T1. Normalização: hifenização só entre letras.** `"10-\n20"` × `"1020"` hoje dá "cópia com ressalva". Adicionar o caso aos testes de diferença material.
- [x] **T2. Normalização: numeração de página só como "Página N de M".** Uma linha `"fls. 120"` × `"fls. 245"` hoje dá "cópia com ressalva". Adicionar o caso aos testes.
- [x] **T3. Alinhamento sobre a sequência de palavras** (sementes de 5 palavras + Greedy String Tiling) no lugar do parágrafo do PDF. Remover union-find de alinhamento, grupos 1:N e fallback N:M. Parágrafo só para exibição, página e cache.
- [x] **T4. Máscara de palavras específicas pela maioria dos shingles que cobrem a palavra.** A coleção de referência passa a usar shingles do texto corrido.
- [x] **T5. Citações dentro do caso.** Detectar blocos citados (aspas, "in verbis", "nos seguintes termos:") e tirá-los da cobertura. Teste: contestação que transcreve parte da inicial → "diferente", com a citação informada.
- [x] **T6. Ruído de OCR.** Documento com OCR: diferenças compatíveis com confusões de OCR mandam o par para "em revisão" como "provável cópia (OCR)", sem alertas de campo. Teste com ruído de OCR simulado.
- [x] **T7. Hash perceptual: aHash → pHash (DCT)**, implementado em numpy. Medir de novo as taxas.
- [x] **T8. Avaliação: baselines por ablação.** Sem filtro de texto padrão; contenção de conjuntos sem alinhamento; cosseno do documento inteiro. Remover o baseline de Jaccard.
- [x] **T9. Tirar o Jaccard de tudo.** `Evidencia.jaccard_especifico`, exemplo trabalhado, §5, §9 e o texto.
- [x] **T10. Tirar do caderno:** o embedding didático (§6), o classificador da §11.3 (e as colunas de custo que dependem dele) e a `Plataforma` com SQLite. Manter extração, ações por classe, grupos e cache como funções.
- [x] **T11. Caderno sem texto narrativo:** só títulos de seção, código e saídas.
- [x] **T12. Novos testes de borda:** os casos de T1, T2, T5 e T6, mais "frases viram linhas" no novo alinhamento.

## Correções no texto (`questao1.md`)

- [x] **T13.** Tirar o Jaccard (5 menções).
- [x] **T14.** Ordem das regras igual à do código: extração falhou antes de texto igual.
- [x] **T15.** Argumento sobre MinHash: escala do caso e posição do trecho, não "MinHash não acha contido".
- [x] **T16.** Afirmações sobre cosseno e texto padrão marcadas como medidas nos dados sintéticos.
- [x] **T17.** Abstenção por par na tabela de custo marcada como cenário (hipótese), não como medida.
- [x] **T18.** Descrever: alinhamento por sequência de palavras, citações, OCR, ablações. Embeddings e fase 2 só como extensão, sem números.
- [x] **T19.** Atualizar todos os números a partir da nova execução do caderno e conferir texto × saída.

## Outros

- [x] **T20.** `requirements.txt`: tirar o comentário do `sentence-transformers`.
- [x] **T21.** Restart & Run All limpo, 0 erros.
- [x] **T22.** (substituída pela T77, feita) PDF anexo: refazer com os números novos e sem Jaccard (manual). Hoje ainda cita Jaccard, MinHash e embeddings no pipeline: não enviar enquanto não for refeito.

## Rodada 8 — revisão de ferramentas (2026-10-13)

### Correções de funcionalidade (risco de erro crítico)

- [x] **T23. OCR não pode esconder mudança material.** `parecidas_ocr` aceita `SequenceMatcher ≥ 0,6`: `12.500,00`→`18.900,00`, `procedente`→`improcedente`, `devido`→`indevido`, `2023`→`2024`, `pagou`→`negou` viram "confusão de OCR". Tirar o fallback de 0,6; usar só o mapa de confusões; nunca tratar como OCR palavra com dígito nem par em que uma palavra contém a outra (in-/im-/des-). Campo crítico alterado tira o par de "provável cópia (OCR)".
- [x] **T24. Sem confirmação em lote quando há campo alterado.** Texto e ações: "provável cópia (OCR)" só é confirmável em lote se nenhum campo (valor, data, CPF, CNPJ, processo) diferir.
- [x] **T25. Testes de OCR:** "novo scan + valor trocado" e "novo scan + procedente→improcedente" nos casos de borda (esperado: versão / em revisão com alerta, nunca "provável cópia (OCR)"); e o tipo "novo scan com alteração" no gerador de avaliação.
- [x] **T26. Tipo de peça na identidade.** Dentro do caso todas as peças têm as mesmas partes e o mesmo processo. Extrair o tipo da peça (inicial, contestação, réplica, memoriais, recurso…) do título/qualificação; "versão · mesma peça" só com o mesmo tipo. Tipo diferente com cobertura alta → nova relação "reaproveita texto" (não substitui). Teste: inicial × memoriais que copiam os fatos.
- [x] **T27. Documento contido em outro: conferir cabeçalho/processo.** Hoje `peca_outro_processo.pdf` sai "cópia com ressalva · trecho" de autos do processo do caso (§9.2). O processo do cabeçalho do menor tem de ser comparado com o do maior; se diferir, vira identidade diferente (versão · outra instância · trecho) com alerta.

### Avaliação

- [x] **T28. Baseline de cosseno calibrado** no conjunto de calibração (melhores cortes), não 0,98/0,80 fixos.
- [x] **T29. Pares difíceis no gerador:** peças diferentes do mesmo caso que reaproveitam fatos sem aspas (esperado: "reaproveita texto"/revisão, nunca "versão · mesma peça").
- [x] **T30. Curva de limiar plana:** dizer no texto que, nos sintéticos, o corte de 60% quase não muda o resultado (as classes ficam separadas); o limiar só é calibrável com pares reais.

### Texto (`questao1.md`)

- [x] **T31.** "Cosseno/embeddings… acima de 0,9" → "cosseno de palavras" (embeddings não foram medidos).
- [x] **T32.** Uma frase simples antes do resumo explicando a ideia central.
- [x] **T33.** Descrever tipo de peça (T26), a relação "reaproveita texto", a regra de OCR (T23/T24) e o trecho com processo (T27). Atualizar números.

### Caderno (legibilidade)

- [x] **T34.** Uma linha "Afirmação:" por seção (o que a seção prova), sem narrativa de processo.
- [x] **T35.** Nomes: `TB`, `P`, `P_`, `Q`, `pa_`, `pb_`, `re_` → nomes descritivos.
- [x] **T36.** `comparar` em funções menores; reescrever a linha do `exigir` em `alinhar_lacuna`.
- [x] **T37.** Geradores de teste (`ruido_ocr`, `peca_que_cita`, `cosseno_palavras`, `SEM_FILTRO`) definidos antes de serem usados fora da seção, num bloco próprio.
- [x] **T38.** Painel final: trocar os ✅ fixos por `assert`.
- [x] **T39.** Inconsistências: título da §9.4 ("até 50" é parâmetro da demonstração; padrão 200); remover a "meta de p95 ≤ 10 min" da §11; `pseudonimizar` sem mutar a entrada.
- [x] **T40.** Restart & Run All limpo e conferir texto × saída.

### Texto de modelo aprendido no histórico do cliente

- [x] **T41.** Trocar a coleção fixa de referência (10 parágrafos padrão sempre iguais) por um índice aprendido nos outros casos do cliente (≥3 casos = modelo).
- [x] **T42.** Gerador com modelos variados: trechos alternativos, partes opcionais, edições soltas a cada uso; modelos novos para medir o limite.
- [x] **T43.** Cliente sem histórico (<20 casos): "versão" automática só com ≥90% nos dois sentidos; o resto vai para revisão.
- [x] **T44.** §5.1: reconhecimento por nível de variação e por tamanho do histórico; avaliação com "mesmos modelos, redigidos de novo" e "modelo novo".
- [x] **T45.** Atualizar `questao1.md` e conferir texto × saída.


## Rodada 9 — avaliação externa (Cursor), filtrada

Verificado no código antes de entrar aqui. O que ficou de fora está no fim, com o motivo.

### Correções (erro real, confirmado)

- [x] **T46. Identidade das partes pelo CPF/CNPJ, não pela semelhança do nome.** Hoje "MARIA SILVA" (CPF 123…) × "MARINA SILVA" (CPF 987…) sai "versão · mesma peça" (substitui), porque os nomes têm 96% de semelhança. Regra nova: mesmo CPF/CNPJ → mesma parte (mesmo com nome digitado errado); CPF/CNPJ diferente e nome diferente (mesmo que parecido) → outra parte; mesmo nome e CPF diferente → mesma parte com alerta "CPF alterado" (correção); sem CPF/CNPJ → semelhança do nome como hoje. Testes: os três casos + os casos de borda atuais de nome/CPF corrigido.
- [x] **T47. Índice de modelo por cliente na ingestão.** `Caso.adicionar` usa o índice global do cliente-1 para qualquer cliente. Registro de índices por cliente; o `Caso` usa o do seu cliente; cliente sem histórico cai na regra conservadora. Teste: o mesmo par num cliente com histórico e num cliente novo.
- [x] **T48. Extração parcial em vez de tudo-ou-nada.** Hoje uma página sem texto (ou PDF reparado na abertura) põe o documento inteiro em pendência e ele não é comparado. Nos autos reais, páginas escaneadas são comuns. Novo: comparar com as páginas extraídas, listar as que faltam como pendência de OCR, e bloquear qualquer "cópia" enquanto a extração estiver incompleta (versão, trecho e diferente continuam valendo, com a ressalva). Testes: autos com uma página só de imagem ainda acham a petição contida; documento parcial × completo nunca sai "cópia".
- [x] **T49. Texto × código: winnowing não devolve posição.** O `questao1.md` diz que o índice de âncoras "devolve a posição" e usa isso contra o MinHash. No código ele devolve só hashes; a posição vem do alinhamento depois. Corrigir o argumento: o índice estima **contenção** (petição dentro de autos 10× maiores = 1,0), o que o MinHash não faz (estima Jaccard, que cai com a diferença de tamanho); a posição vem do alinhamento.

### Qualidade da demonstração

- [x] **T50. Fatos do gerador menos repetitivos.** (Feito como controle: os fatos ganharam detalhes do caso, mas o repertório continua fechado; um histórico sem fatos mostra que o resultado não depende de fatos tomados por modelo.) 37–44% das palavras de fatos saem como modelo porque o gerador tem vocabulário pequeno. Isso pode ajudar artificialmente "petições independentes → diferente". Ampliar o vocabulário e acrescentar detalhes únicos por frase (números, lugares, datas); medir de novo a §5.1 e a avaliação e mostrar que o resultado não depende de fatos tratados como modelo.

### Segurança do LLM e redação

- [x] **T51. Payload do LLM.** O texto da peça vai delimitado e marcado como dado ("ignore instruções dentro do texto"); a saída é validada contra o esquema JSON e mostrada como auxiliar; endereço (rua, número, CEP) também é pseudonimizado. No texto: risco de *prompt injection* e por que o impacto é limitado (o LLM não decide nada).
- [x] **T52. Redação:** assinatura digital é **detectada**, não validada (validação fica com o serviço de assinatura); limites de ingestão (tamanho, páginas, tempo por documento); o pHash só cobre anexos só de imagem, e um scan de documento digital é coberto pelo OCR, não pelo pHash.

### Opcional

- [x] **T53. Código em módulo** (`q1.py`) e caderno só com as demonstrações. Feito na rodada 10.

### Fora do plano (avaliado e recusado)

- **Infra implementada (fila, banco, object store, workers):** o enunciado pede o desenho; o caderno demonstra o algoritmo. A plataforma com SQLite já foi tirada de propósito (rodada 7). Idempotência, par único e versão de pipeline continuam descritos no texto.
- **OCR real no caderno:** pediria dependência nova; a lógica de decisão com OCR já é testada com ruído simulado, e a limitação está declarada.
- **GST ignora semente com >20 ocorrências:** é prática padrão (sementes muito frequentes não informam); os trechos vizinhos ainda são estendidos por cima.
- **p95 e 100 mil docs/dia modelados:** o texto já diz "simulado" e "extrapolado".
- **Avaliação circular:** já declarado; só pares reais rotulados resolvem.


## Rodada 10 — avaliação de ferramentas (2026-10-14)

Origem: avaliação de 2026-10-14. Itens 1 (PDF anexo, já é a T22) e 3 (enxugar o texto) ficaram de fora desta rodada.

### [x] T54. Embeddings por parágrafo decidem a faixa de 20–60% (só desenho, sem implementar)

**Problema.** O enunciado pede para considerar embeddings e fala em versões com "alguns parágrafos diferentes". Hoje:
- o texto descarta embeddings comparando-os com o cosseno do **documento inteiro** (`questao1.md:51`), uma alternativa que ninguém usaria;
- a alternativa séria (embeddings **por parágrafo**, pareados entre os dois documentos) não aparece;
- a mesma peça muito reescrita cai na faixa de 20–60% e vai inteira para humanos, que o próprio texto diz ser o custo dominante. Embeddings só aparecem na "Fase 2" (`questao1.md:202`).

**O que fazer em `questao1.md`:**
1. **§1, tabela "Alternativas consideradas" (`:51`).** Trocar a linha "Cosseno de palavras ou embeddings do documento inteiro" por duas linhas:
   - *Cosseno de palavras do documento inteiro*: ganha "barato"; perde "mede tema, não derivação: petições independentes do mesmo modelo têm cosseno > 0,9 nos dados sintéticos"; papel "baseline (§10.3)".
   - *Embeddings por parágrafo*: ganha "capta paráfrase e parágrafo reescrito"; perde "não localiza a mudança palavra a palavra; parágrafos de modelo também ficam parecidos; custo de inferência"; papel "**decide a faixa de 20–60%** (regras 10–12)".
2. **§2, novo bloco logo depois do parágrafo que explica a faixa de 20–60% (depois de `:115`)**, com o título "Faixa ambígua: sinal semântico". Conteúdo:
   - na ingestão, cada parágrafo de exibição ganha um embedding (modelo multilíngue, guardado junto com o documento e calculado uma vez só);
   - só entram os parágrafos que **não** foram alinhados literalmente e que não são de modelo nem citação. O texto de modelo já foi tirado, e é isso que impede o "tema parecido" de voltar;
   - para cada parágrafo restante de A, buscar o parágrafo mais parecido de B com cosseno ≥ **0,85**. É um valor de partida fixo, declarado como não medido nestes dados. Os pares têm de seguir a ordem dos dois documentos (mesma regra de encadeamento das regiões), para não parear parágrafos soltos de mesmo tema. Fazer o mesmo no outro sentido;
   - **cobertura total** = % das palavras do texto próprio de A cobertas por alinhamento literal **ou** por par semântico em B, e o inverso. Mesma regra de massa de texto dos dois percentuais.
3. **§2, tabela de regras (`:99–113`).** A regra 10 ("o resto: 20–60% → em revisão") vira três regras novas, aplicadas só quando o percentual literal maior está entre 20% e 60%:

   | # | Condição | Resultado |
   |---|---|---|
   | 10 | cobertura total ≥65% num sentido **e** ≥50% no outro | aplica a regra 7 com a cobertura total: **versão** (mesma peça, outra peça do caso ou outra instância). Diff nos trechos literais e pares de parágrafos reescritos lado a lado; alertas de campo e de negação como em qualquer versão |
   | 11 | cobertura total <55% nos dois sentidos | **diferente**, com o vínculo "reaproveita trechos de X (x%, págs. …)" quando o literal for ≥20% |
   | 12 | o resto: cobertura total entre 55% e 65% (perto do corte de 60%), ou texto espalhado dentro de um documento maior | em revisão |

   Regras fixas desta mudança:
   - o sinal semântico **nunca produz "cópia"**;
   - ele **não roda fora da faixa** de 20–60% literal: abaixo de 20% o par continua "diferente", senão petições do mesmo tema voltariam a parecer versões.

   A margem de ±5 pontos em volta de 60% é a "incerteza alta": só ela vai para revisão.
4. **§2, texto logo depois da tabela (`:115`).** Trocar a frase "A faixa de 20–60% vai para revisão porque nela dois casos dão o mesmo número… Contando só texto igual, não há como separar os dois" por: "Na faixa de 20–60%, contando só texto igual, dois casos dão o mesmo número: a mesma peça muito reescrita (~50%) e outra peça que copiou alguns parágrafos sem aspas (36%). O pareamento semântico separa os dois. Na peça reescrita, os parágrafos reescritos encontram par e a cobertura total passa de 65%. Na outra peça, o resto do texto não tem par, e ela fica abaixo de 55%."
5. **§3 Documentos longos.** Uma frase: o embedding é por parágrafo, então o tamanho do documento não importa para o contexto do modelo de embedding.
6. **§6 Trade-offs.** Uma linha com o custo como estimativa, marcada como não medida: 1 mil docs/dia × 20 págs. × ~6 parágrafos ≈ 120 mil embeddings/dia, calculados uma vez na ingestão. A busca é dentro do caso (dezenas de documentos), então não precisa de índice vetorial. Latência: desprezível perto do OCR.
7. **§6 Evolução, item 2 (`:202`).** Tirar a frase "Embeddings por parágrafo entram para recuperar paráfrases…", que passou para a §2.
8. **Limitações (`:206`).** Manter "embeddings não foram executados" e acrescentar: "o corte de 0,85 e as margens de 55%/65% não foram medidos; nos números da §4, as reescritas extensas ainda aparecem em revisão porque o caderno não roda embeddings".
9. **Resumo (`:15`).** "Na dúvida, 'em revisão'" → "Só a incerteza alta vai para revisão: igualdade não confirmada (OCR, extração incompleta) ou cobertura perto do corte".

**O que fazer em `DECISOES_Q1.md`:** nova linha na tabela 3 (Decisão): "Faixa de 20–60% decidida pela cobertura total (literal + pares semânticos por parágrafo, cosseno ≥0,85, na ordem): ≥65%/≥50% → versão; <55% → diferente; 55–65% → revisão". Por quê: a faixa é onde a contagem de texto igual não separa "mesma peça reescrita" de "outra peça que reaproveita trechos". Fora dela, embeddings só trariam de volta o tema. Rejeitado: mandar a faixa inteira para revisão (é onde estão as reescritas, e o sistema não decidiria o caso mais comum depois da cópia); embedding do documento inteiro (mede tema); embeddings como sinal principal (não localizam a mudança e não provam igualdade).

**Caderno:** nada (não implementar).

**Pronto quando:** os itens 1–9 estiverem no texto, a tabela de regras tiver as regras 10–12, nenhum número de embedding aparecer como medido, e a palavra "embeddings" não estiver mais só na "Evolução".

### [x] T55. Avaliação como teste de invariantes, não como desempenho

**Problema.** "Acerto nos decididos 100%" e "precisão de 100% nas quatro classes" (`questao1.md:155`, `:159`) estão em destaque, mas o gerador e as regras têm o mesmo autor. Para quem lê, 100% em dados próprios é sinal de teste viciado, não de qualidade.

**O que fazer em `questao1.md`, §4:**
1. **`:148`.** Trocar o título "**Demonstração (dados sintéticos, §10).**" por "**Teste das invariantes (dados sintéticos, §10).**". Começar o parágrafo com: "Os dados sintéticos testam se as garantias do desenho se mantêm sob perturbações conhecidas. Não estimam a precisão em petições reais: o gerador e as regras têm o mesmo autor. A precisão real vem do método acima, com pares rotulados." Depois disso, tirar o último bullet (`:162`), que diz a mesma coisa.
2. **Tabela (`:150–155`).** Tirar a linha "acerto nos decididos" e pôr no lugar "versão → diferente": 0 · 0 · 0 · 18 (valores da §10.3). A tabela fica só com contagens de erro + taxa de revisão.
3. **Bullet "Precisão… Recall…" (`:159`).** Reescrever como: "Nenhum erro de classe nos 800 pares. O que não foi decidido foi para revisão: [a lista atual de motivos com as contagens]." Tirar "precisão de 100%" e os percentuais de recall por classe. A informação de recall fica implícita na lista do que foi para revisão.

**O que fazer no caderno:**
- §10.2 (célula com `"acerto nos decididos"`): trocar o `print` de "acerto nos decididos" por "erros de classe nos decididos: N";
- §10.3: trocar a coluna "acerto decididos" por "erros decididos" (contagem);
- conferir que o painel (§12, item 4) já está em forma de invariante (está);
- não mexer na lógica, só na apresentação.

**Pronto quando:** a palavra "acerto" e o "100%" não aparecerem mais na §4 do texto nem nas saídas da §10, e o texto abrir dizendo o que os sintéticos medem e o que não medem.

### [x] T56. Explicar quando "outra instância do modelo" acontece dentro de um caso

**Problema.** No mesmo caso, todas as peças têm as mesmas partes e o mesmo processo. Mesmo assim, o exemplo do enunciado (MARIA × MARINA, `questao1.md:124–127`) sai como "versão · outra instância do modelo", sem explicar como duas peças com partes diferentes chegam ao mesmo caso. Quem lê vai achar o subtipo artificial.

**O que fazer em `questao1.md`:**
1. **§2, bullet de "partes/processo" (`:119`).** Acrescentar ao fim: "Dentro de um caso isso é raro e quer dizer uma de três coisas: (a) peça de outro processo juntada aos autos (decisão usada como precedente, petição de litisconsorte); (b) documento enviado para o caso errado, quando o alerta de cadastro do caso também dispara (§5); (c) na extensão entre casos do mesmo cliente (§6), o caso comum."
2. **§2, exemplo do enunciado (`:124`).** Acrescentar uma frase antes da lista: "O enunciado não diz que as duas petições estão no mesmo caso. O exemplo mostra a medida (84% nos dois sentidos). Se estivessem no mesmo caso, a parte fora do cadastro também geraria alerta na ingestão."
3. **§5, linha "Versão · outra instância" (`:175`).** Acrescentar: "No mesmo caso, junto com o alerta de cadastro quando as partes não são as do caso."

**Caderno:** nada. A §4.1 continua igual; o texto só explica o contexto.

**Pronto quando:** os três trechos estiverem no texto e a explicação couber em no máximo 4 frases somadas.

### [x] T57. Corrigir o corte do cosseno calibrado

**Problema.** O texto diz "versão ≥ 0,95", mas a execução de 2026-10-14 imprime `cortes do cosseno calibrados: cópia ≥ 1.00, versão ≥ 0.96` (§10.3).

**O que fazer:**
- `questao1.md:148`: "versão ≥ 0,95" → "versão ≥ 0,96";
- `DECISOES_Q1.md:108`: "versão ≥ 0,95" → "0,96", e "dá 17" → "dá 18" (falsos "cópia" na execução atual).

**Pronto quando:** o `grep "0,95"` nos dois arquivos não achar mais esse corte e os números baterem com a saída da §10.3.

### [x] T58. Greedy String Tiling: dizer que é uma variante

**Problema.** `DECISOES_Q1.md:20` diz "*Greedy String Tiling*, a técnica do JPlag" e `:134` diz "É o algoritmo do JPlag". A implementação (`trechos_iguais`, caderno §3) é uma variante simplificada:
- o GST original repete rodadas, cada uma marcando os maiores trechos ainda livres, com tamanho mínimo decrescente;
- aqui todas as corridas máximas são coletadas numa passada só (sementes com mais de 20 ocorrências ignoradas), depois ordenadas do maior para o menor, e cada uma fica só com as partes ainda livres.

O resultado é parecido, mas não é o mesmo algoritmo.

**O que fazer:**
- `DECISOES_Q1.md:20`: "(*Greedy String Tiling*, a técnica do JPlag)" → "(variante do *Greedy String Tiling* do JPlag: uma passada coleta todas as corridas máximas a partir das sementes, que depois são escolhidas do maior para o menor; o original repete rodadas)";
- `DECISOES_Q1.md:134`: "É o algoritmo do JPlag" → "É a ideia do algoritmo do JPlag; aqui, numa variante de uma passada";
- `questao1.md:62` e `:47`: "*Greedy String Tiling*" → "variante do *Greedy String Tiling*";
- docstring de `trechos_iguais` no caderno: "Greedy String Tiling:" → "Variante do Greedy String Tiling (uma passada):".

**Pronto quando:** nenhum dos arquivos apresentar a implementação como o algoritmo do JPlag sem a palavra "variante".

### [x] T53 (já listado; deixa de ser opcional). Código num módulo, caderno só com as demonstrações

**Problema.** São ~2.600 linhas de código no caderno. O avaliador vai abrir o caderno para ver as demonstrações e encontra definições de 400 linhas (§3) no meio delas.

**O que fazer:**
1. Criar `Enter/q1.py` com todas as constantes, `dataclass`es, classes e funções que hoje estão nas células de código, na ordem das seções e com um comentário `# §n` separando cada uma. Inclui os geradores sintéticos (§2, §2.1, §10.1) e o `Caso`/`CacheDeAnalise` (§9).
2. No caderno, a primeira célula de código passa a ser `from q1 import *` (mais os imports de exibição). Cada seção mantém o título, a linha "Afirmação:" e só o código que **executa** a demonstração: chamadas, `print`, `assert`, gráficos.
3. Nenhuma lógica muda: as saídas da nova execução têm de ser iguais às da execução de 2026-10-14 (mesmas seeds). Comparar §10.2, §10.3, §10.5, §11 e §12.
4. `questao1.md:17`: citar o `q1.py` junto com o caderno ("o código está em `q1.py`; o caderno executa as demonstrações").
5. Topo deste arquivo, linha "**Entrega:**": acrescentar `q1.py`.
6. Restart & Run All limpo, com 0 erros.

**Pronto quando:** o caderno não tiver nenhuma definição de função ou classe com mais de ~10 linhas, rodar limpo, e as saídas forem iguais às de antes.

## Rodada 11 — segurança, consistência, freshness, acurácia, performance e escala (2026-10-14)

Origem: avaliação do desenho nas seis dimensões. O algoritmo de comparação não muda. As lacunas estão na parte com estado (índice de modelo aprendido, reprocessamento, concorrência) e na ingestão de PDF como entrada hostil.

**Critério desta rodada (o mesmo da rodada 9):** infraestrutura (fila, banco, sandbox, KV) fica **descrita no texto**, não implementada. O caderno só muda quando a mudança demonstra uma invariante ou um comportamento do algoritmo: fidelidade da extração (T59), índice de modelo versionado (T62), precedência humana (T63), reavaliação da fila (T64), reprocessamento (T65), contencioso de massa (T66), limite por volume (T70) e custo de OCR (T73). O código vai para onde a implementação estiver na hora (caderno ou `q1.py`, T53).

**Todas as escolhas abaixo já estão decididas.** Nenhuma tarefa deixa decisão para depois da medição: a medição entra na entrega como evidência da escolha.

**Ordem de execução:** T59 → T62 → T63 → T64 → T65 → T66 → o resto. A T59 protege o erro crítico; T62–T65 fecham a maior lacuna (freshness); a T66 é o maior risco para a taxa de revisão no caso de uso da Enter.

**Arquivos afetados em todas:** depois de cada tarefa, conferir texto × saída do caderno e registrar o porquê em `DECISOES_Q1.md` (nova seção "Rodada 11").

---

### Segurança

### [x] T59. Fidelidade da extração antes de afirmar "cópia" por texto igual

**Problema.** As regras 3 e 4 (`questao1.md:106–107`) dão "cópia · exata" ou "com ressalva" quando os **bytes diferem** mas o texto extraído é igual. Em PDF, o texto extraído pode não corresponder ao que está na página:
- fonte com tabela ToUnicode quebrada ou remapeada (comum em PDF gerado por sistema de tribunal): o "7" desenhado é extraído como "1", ou some (vira U+FFFD ou nada);
- texto coberto por um retângulo preenchido pintado depois dele, ou texto invisível (modo de renderização 3, opacidade 0);
- número desenhado como vetor, que não é texto nem imagem.

Nesses casos, dois PDFs com valores **visíveis** diferentes têm o mesmo texto extraído e saem "cópia". É o erro mais caro do desenho, e o próprio texto (`:10`) diz que ele "só pode vir da extração ou da normalização". Hoje nada confere se a extração foi fiel.

**Objetivo.** Fazer com que "cópia" dependa do que o advogado **vê**, não só do que o extrator lê. A invariante "cópia só por igualdade" passa a valer também para PDFs malformados ou adulterados. O custo é baixo: a checagem 1 roda uma vez por documento na ingestão, e a 2 só nos pares que já iam sair cópia.

**Decisão: duas checagens, as duas implementadas.**

1. **Extração confiável, por documento, na ingestão.** Com PyMuPDF, marcar `doc.extracao_confiavel = False` se houver:
   - texto invisível: spans de `page.get_texttrace()` com tipo invisível (modo 3) ou opacidade 0;
   - texto coberto: retângulo ou caminho preenchido de `page.get_drawings()` cujo `seqno` é maior que o do span e cuja área cobre o bbox de uma palavra;
   - fonte sem mapa de caracteres: caractere U+FFFD no texto extraído, ou fonte Type3 ou sem ToUnicode em `page.get_fonts()` usada em algum span.

   Documento não confiável não pode sair "cópia" por texto (só por bytes, regra 1). Ele cai na mesma barreira da extração incompleta (regra 2a): "em revisão", com o motivo e as páginas.
2. **Página renderizada igual quando o layout é o mesmo, por par.** Quando a regra 3 ou 4 vai disparar com bytes diferentes e as caixas das palavras (`page.get_text("words")`, arredondadas a 1 pt) são iguais nos dois documentos, rasterizar as páginas a 72 dpi em tons de cinza, binarizar e exigir igualdade dos rasters. Se as caixas são iguais e o raster difere, algo foi desenhado fora do texto (número em vetor, carimbo): "em revisão", com a página. Quando o layout difere (reexportação com outra fonte), o raster não é comparável e vale só a checagem 1. Uma reexportação legítima continua "cópia com ressalva".

Por que não comparar sempre o raster da página inteira: qualquer reexportação com outra fonte mudaria o raster, e todas as reexportações iriam para revisão sem ganho de segurança. A checagem 1 cobre as formas conhecidas de o texto divergir do que se vê; a 2 cobre o desenho por cima quando o layout permite comparar.

**O que fazer no caderno (§1 / §7):**
1. `extracao_confiavel(pdf) -> (bool, motivos, paginas)` com as três verificações da checagem 1. Guardar no documento em `doc_de_arquivo`.
2. `rasters_iguais(pdf_a, pdf_b, paginas)` com a checagem 2. Chamada só dentro das regras 3 e 4 com bytes diferentes.
3. Em `decidir`: documento não confiável → regra 2a; layout igual e raster diferente → "em revisão" com o motivo "texto igual, página visualmente diferente (págs. x, y): conferir o original". Nunca "versão" automática, porque o diff de texto está vazio.
4. Novos casos de borda na §4.2 (todos esperados **não cópia**, exceto o último):
   - mesmo PDF + retângulo branco sobre o valor (`page.draw_rect(bbox_valor, color=(1,1,1), fill=(1,1,1))`): o texto extraído é igual e o retângulo foi pintado depois do texto;
   - mesmo PDF + outro valor escrito com `render_mode=3` (invisível): checagem 1;
   - mesmo PDF + um traço vetorial desenhado sobre um dígito (`page.draw_line`), mesmo layout: checagem 2;
   - a mesma petição reexportada com outra fonte (`peticao_v1_reexportada.pdf`): continua "cópia com ressalva".
5. §11: medir os ms por página da checagem 1 e do raster a 72 dpi.

**O que fazer em `questao1.md`:**
- tabela da §1 (`:35`): linha "verificação de fidelidade (texto invisível, texto coberto, fonte sem mapa de caracteres) e raster da página quando o layout é igual", com o papel "garante que texto igual é página igual";
- regras 3 e 4 (`:106–107`): acrescentar "com extração confiável e, se o layout for o mesmo, a mesma página renderizada";
- regra 2a: incluir "extração não confiável" junto com "extração incompleta";
- um parágrafo depois da tabela de regras: "A extração pode divergir do que se vê: fonte sem mapa de caracteres, texto coberto ou invisível, número desenhado. Um documento com qualquer um desses sinais não sai 'cópia' por texto. Com o mesmo layout, a página renderizada também tem de ser igual.";
- §6, Latência: o custo medido no item 5.

**Pronto quando:** os três PDFs adulterados nunca saírem "cópia", a reexportação continuar "cópia com ressalva", a §10 não ganhar falso "cópia" e o custo por página estiver na §11.

### [x] T60. Ingestão isolada e hashes com chave por cliente (só texto)

**Problema.**
1. O PyMuPDF processa PDFs de terceiros (parte contrária, tribunal, cliente). Parsers de PDF têm histórico de vulnerabilidades. Os limites de tamanho, páginas e tempo (`:21`) protegem a fila, mas não isolam o processo.
2. O índice de modelo e o de âncoras guardam hashes de sequências de 5 palavras. Hash sem chave de texto com pouca entropia pode ser revertido por dicionário: quem tem acesso ao índice testa se "Maria da Silva CPF 123.456.789-09" aparece no cliente, montando as 5 palavras e calculando o hash.
3. O `IDENTIFICADORES` do pseudonimizador é uma lista de padrões (regex). Não cobre dado sensível do art. 11 da LGPD (saúde, em trabalhista e previdenciário) nem nomes de terceiros (já declarado em `:212`).
4. O campo `mudanca` da resposta do LLM é texto livre exibido ao revisor. Sem escape, vira vetor de XSS. Uma injeção também pode escrever "sem mudança relevante" e induzir o revisor a confirmar.

**Objetivo.** Fechar as superfícies de ataque que o desenho cria, mostrando que a ingestão de arquivos hostis e os índices derivados foram pensados como dado sensível, e não só o payload do LLM.

**O que fazer em `questao1.md`:**
1. **Fluxo, passo 1 (`:21`).** Acrescentar: "A extração roda num worker isolado (container sem rede, sistema de arquivos só leitura, limite de memória e CPU, um documento por processo), que devolve só texto, posições e hashes. Uma falha ou travamento no parser derruba o worker, não a fila."
2. **§2, item 1 (`:60`), onde diz "guarda só hashes".** Trocar por "guarda só HMACs com chave por cliente (as chaves ficam num KMS), para que o índice não permita testar se uma frase aparece no cliente. O índice de âncoras usa a mesma chave."
3. **§3, lista do LLM (`:133–137`).**
   - pseudonimização: "lista de padrões + NER no envio; categorias sensíveis da LGPD (saúde, biometria) vão mascaradas";
   - nova linha: "a resposta é exibida como texto escapado, ao lado do diff; o resumo nunca substitui o diff e o revisor confirma olhando o diff. A relevância 'baixa' não esconde nem rebaixa um item que tenha campo ou negação alterados (essa marcação vem do diff, não do LLM)."
4. **Limitações (`:212`).** Juntar a frase de nomes de terceiros com a de NER do item 3, para não repetir.

**Caderno:** nada.

**Pronto quando:** sandbox, HMAC por cliente, LGPD sensível e escape estiverem no texto em no máximo uma frase cada, sem seção nova.

### [x] T61. Exclusão de caso compatível com LGPD × "nada é apagado"

**Problema.** `questao1.md:33` diz "nada é apagado" e a §5 (`:168`) repete. Mas:
- pedido do titular ou fim de contrato exigem apagar o caso;
- o índice de modelo é um **contador agregado** de casos por sequência. Sem saber quais sequências o caso trouxe, não dá para decrementar: o caso apagado continua influenciando o que é "modelo" para sempre;
- o cache por parágrafo também guarda análises derivadas do caso.

**Objetivo.** Deixar claro o escopo de "nada é apagado": a **classificação** não apaga documentos. A plataforma, essa sim, apaga quando a lei manda, e o desenho tem como desfazer o efeito de um caso nos índices derivados.

**O que fazer em `questao1.md`:**
1. `:33`: "auditoria; nada é apagado" → "auditoria; a classificação não apaga nada".
2. §5, depois de "Nova versão do pipeline" (`:185`): "**Exclusão (LGPD, fim de contrato):** apagar um caso remove os arquivos, os pares e o cache dele, e o subtrai do índice de modelo do cliente (o índice guarda o conjunto de sequências de cada caso, T62). Os rótulos de revisão viram pares anonimizados ou são apagados junto."

**Caderno:** coberto pela T62 (`remover_caso`).

**Pronto quando:** a frase "nada é apagado" não aparecer mais sem o escopo, e a exclusão estiver descrita em uma linha na §5.

---

### Consistência

### [x] T62. Índice de modelo como snapshot versionado, construído a partir dos conjuntos por caso

**Problema.**
1. O texto diz que o índice "se atualiza a cada documento" (`:60`) e conta **casos**, descontando o caso atual. Com um contador incremental isso não funciona:
   - para saber se uma sequência já foi contada para o caso, é preciso o conjunto do caso;
   - para descontar o caso atual na consulta, é preciso saber se aquela sequência veio dele.

   No caderno isso funciona porque o histórico é montado de uma vez e não contém o caso atual (docstring da `IndiceDoCliente`).
2. Atualizar a cada documento custa caro (um documento de 100 mil palavras gera cerca de 100 mil upserts) e não traz ganho: modelos de escritório mudam devagar.
3. Sem versão, duas comparações do mesmo par em momentos diferentes podem dar resultados diferentes, e não há como saber por quê.

**Objetivo.** Ter um índice que (a) conte casos corretamente, (b) desconte o caso atual, (c) possa subtrair um caso (T61), (d) tenha versão gravada em cada decisão, para que a decisão seja reproduzível e reavaliável (T63).

**O que fazer no caderno (§2):**
1. `IndiceDoCliente` passa a guardar `conjuntos_por_caso: dict[caso_id, frozenset[shingle]]` e a gerar um **snapshot** imutável com `versao` (inteiro crescente) e `casos_com` (Counter).
2. Métodos:
   - `adicionar_caso(caso_id, textos)`: guarda o conjunto e não recalcula o snapshot;
   - `remover_caso(caso_id)`: apaga o conjunto;
   - `publicar()`: reconstrói `casos_com` a partir dos conjuntos, mantendo só as sequências com ≥ `minimo` casos (as outras nunca são modelo), e incrementa `versao`. Na plataforma, roda uma vez por dia por cliente.
3. `eh_padrao(shingle, caso_atual=None)`: `casos_com[s] - (s in conjuntos_por_caso.get(caso_atual, ()))  >= minimo`. O desconto do caso atual vira código, não premissa.
4. `indexar(doc, indice)` grava `doc.indice_versao = indice.versao`.
5. `Decisao` (§4) ganha `indice_versao` e `versao_pipeline` (a constante `VERSAO_PIPELINE` da §0). `decidir` copia os dois da evidência.
6. Testes:
   - uma sequência em 2 outros casos + o caso atual **não** é modelo (desconto funcionando); em 3 outros casos, é;
   - `remover_caso` + `publicar` faz uma sequência que estava em exatamente 3 casos deixar de ser modelo;
   - o mesmo par comparado com o snapshot v1 e com o v2 grava versões diferentes na decisão.
7. Os números da §5.1 e da §10 **não podem mudar**: o histórico continua o mesmo, só a estrutura muda. Se mudarem, investigar antes de seguir.

**O que fazer em `questao1.md`:**
- `:60`: "guarda só hashes com a contagem de casos e se atualiza a cada documento" → "guarda, por caso, o conjunto de sequências (como HMAC, T60). Um job diário publica um snapshot versionado com a contagem de casos das sequências que aparecem em 3 ou mais casos. A consulta desconta o caso atual. Os modelos mudam devagar, e um snapshot por dia basta; o que ficou na fila nesse meio-tempo é reavaliado (T64).";
- §5: "cada decisão grava a versão do pipeline e a do índice de modelo usadas".

**O que fazer em `DECISOES_Q1.md`:** linha nova na tabela 1: "Snapshot versionado do índice, a partir dos conjuntos por caso". Por quê: contar casos, descontar o atual, permitir exclusão e reproduzir decisões. Rejeitado: contador incremental por documento (não sabe se a sequência já foi contada no caso, não decrementa, upsert por shingle).

**Pronto quando:** os três testes passarem, as saídas da §5.1 e da §10 forem idênticas às de antes e o texto não disser mais "se atualiza a cada documento".

### [x] T63. Concorrência, versão de pipeline ativa e precedência da decisão humana

**Problema.**
1. **Corrida.** "Cada documento é indexado antes de ser comparado" (`:27`) só evita que dois uploads simultâneos se percam se o índice tiver read-your-writes. Um índice de busca com consistência eventual (refresh periódico) deixa A e B se perderem. No código acontece o contrário do texto: `Caso.adicionar` insere em `exatos` e `ancoras` **depois** de comparar (só `self.docs` é atualizado antes).
2. **Versão de pipeline.** "Grava novas linhas, mantendo as antigas" (`:185`) não diz qual versão vale. Se um caso tiver pares da v1 e da v2, os grupos misturam critérios (A~B pela v1, B~C pela v2).
3. **Decisão humana × reprocessamento.** "A revisão preserva a decisão do sistema" (`:184`), mas não diz o que acontece quando o pipeline reprocessa o par (OCR concluído, versão nova, índice novo). Sem regra, a máquina pode sobrescrever o revisor, ou o revisor ficar preso a uma evidência que mudou.

**Objetivo.** Garantir que (a) nenhum par se perca em uploads simultâneos, (b) todas as decisões visíveis de um caso tenham o mesmo critério, (c) a decisão humana tenha precedência clara e só seja revista quando a evidência mudar.

**O que fazer em `questao1.md` (§ Fluxo, `:27`, e §5):**
1. **Corrida.** Trocar a frase por: "Os documentos de um mesmo caso são processados **em série** (fila particionada por `caso_id`). Casos são pequenos, então a série não limita a vazão, que vem do paralelismo entre casos. Com isso, todo documento vê os anteriores do caso, sem depender da consistência do índice. A chave única `(caso, doc menor, doc maior, versão do pipeline)` continua como proteção contra reentrega da fila."
2. **Versão ativa** (§5, no lugar de `:185`): "Cada caso tem uma versão de pipeline ativa. Uma versão nova reprocessa o caso inteiro em segundo plano (300 documentos em ~1 s, §9.4) e só então troca o ponteiro. Grupos, fila e alertas leem só a versão ativa. As linhas antigas ficam para auditoria."
3. **Precedência** (§5, no lugar de `:184`): "A decisão do revisor vale sobre a do sistema enquanto a evidência for a mesma (hash do texto dos dois documentos). Se a evidência mudar (OCR concluído, nova extração), o par volta à fila com a decisão anterior visível. Mudança só de versão do pipeline ou do índice **não** reabre um par já decidido por humano; a diferença é registrada para calibração."

**O que fazer no caderno (§9):**
- em `Caso.adicionar`, inserir em `exatos` e `ancoras` **antes** do laço de comparação (o documento não pode ser candidato de si mesmo, porque `_candidatos` já exclui `doc.doc_id`). Assim o texto e o código dizem a mesma coisa;
- `Caso.decisao_humana(par, classe)` grava `{classe, hash_a, hash_b}`, e `pares` passa a devolver a humana quando os hashes batem. Teste: reprocessar o par com o mesmo texto mantém a decisão humana; com texto novo, o par volta para "em revisão" com `decisao_anterior`.

**Pronto quando:** o texto descrever a fila por caso, a versão ativa e a precedência em no máximo 3 frases cada, e a ordem "indexa → compara" for a mesma no texto e no código.

---

### Freshness

### [x] T64. Reavaliar a fila quando o índice de modelo muda

**Problema.** Uma sequência vira modelo quando aparece no 3º caso do cliente. Os pares decididos antes contaram essa sequência como texto próprio:
- os que foram para revisão por causa dela continuam na fila sem necessidade (a §5.1 mostra 19 de 20 em revisão com histórico zero, e 20/20 "diferente" com 20 casos);
- o desenho não diz se essas decisões são revistas.

Para cliente novo (menos de 20 casos, `:84`) isso é o caso normal, não exceção: a fila cresce no começo e nunca esvazia sozinha.

**Objetivo.** Fazer a fila **diminuir sozinha** à medida que o histórico cresce, sem nunca rebaixar silenciosamente uma decisão automática já entregue ao advogado.

**O que fazer no caderno (nova §9.5, "Fila reavaliada com o histórico"):**
1. Cliente novo com 5 casos de histórico. Uma petição e uma petição independente escrita com os mesmos modelos vão para o mesmo caso: esperado "em revisão" (como na §5.1).
2. Acrescentar 20 casos ao histórico e `publicar()` (T62).
3. `Caso.reavaliar_fila(indice)`: recompara **só** os pares em "revisão necessária" cuja `indice_versao` seja menor que a atual e que não tenham decisão humana (T63). Grava a nova decisão com a nova versão e mantém a anterior no histórico.
4. Asserts:
   - o par sai da fila como "diferente";
   - pares já decididos (cópia, versão, diferente) **não** são recomputados nem mudam;
   - o evento registra "saiu da fila por atualização do índice de modelo (v1 → v2)".

**O que fazer em `questao1.md`:**
- §2, bullet "Cliente sem histórico" (`:84`): acrescentar "Quando o índice ganha uma versão nova, os pares em revisão sem decisão humana são recomparados, e os que deixam de ser ambíguos saem da fila. Decisões já entregues não são rebaixadas automaticamente; uma mudança nelas vira alerta para o revisor.";
- §6, Limitações (`:210`): "geram revisões até o histórico crescer" → "geram revisões, que saem da fila sozinhas quando o histórico cresce".

**Por que só a fila:** reavaliar todos os pares mudaria decisões que o advogado já viu ("era versão, virou diferente"). Isso exige um alerta, não uma troca silenciosa. A fila é o que tem custo (horas de revisão), e reavaliá-la é barato: comparação dentro do caso, ~1 s por caso de 300 documentos.

**Pronto quando:** a §9.5 rodar com os três asserts e o texto tiver as duas frases.

### [x] T65. Reprocessamento disparado por mudança de evidência (OCR concluído)

**Problema.** Quando uma página fica sem texto, o documento é comparado com o resto e a página vira "pendência de OCR, reprocessar" (`:21`, §9 do caderno). Não está desenhado:
- quem dispara o reprocessamento;
- o que acontece com os pares já gravados;
- se a decisão humana sobre o par antigo vale (T63).

O mesmo vale para o cadastro do caso corrigido (alertas de identidade antigos) e para a data de protocolo que chega depois (direção A → B).

**Objetivo.** Garantir que todo dado que muda depois da primeira comparação produza decisões novas, substituindo as antigas de forma auditável. Hoje "reprocessar" é só uma palavra no texto.

**O que fazer no caderno (§9, depois do caso com `peticao_v1_escaneada.pdf`):**
1. `Caso.substituir_texto(doc_id, novos_dados)`: reextrai, reindexa e recompara o documento com todos os candidatos do caso. Grava as novas decisões **por cima** em `pares` e mantém a anterior em `historico_pares`.
2. Demonstração: `peticao_v1_escaneada.pdf` (hoje "nunca cópia", com pendência) recebe a versão com a página 2 lida, simulando o OCR concluído com o texto original:
   - o par com `peticao_v1.pdf` passa a "cópia com ressalva" (bytes diferentes) ou ao que a T59 decidir para o render;
   - a pendência é resolvida e a decisão anterior fica no histórico.
3. Assert: nenhum par do documento fica com decisão da extração parcial depois da substituição.

**O que fazer em `questao1.md`, §5 (lista depois da tabela):**
"**Evidência nova:** OCR concluído, cadastro do caso corrigido ou data de protocolo recebida geram um evento que recompara os pares do documento (ou recalcula alertas e direção). As decisões novas substituem as anteriores, que ficam no histórico. A decisão humana segue a regra de precedência (T63)."

**Pronto quando:** a demonstração rodar e a frase estiver na §5.

---

### Acurácia

### [x] T66. Contencioso de massa: medir e tratar documentos quase só de modelo

**Problema.** No caso de uso típico da Enter (empresa ré em litigância de massa), as petições são quase todas modelo do escritório da outra parte somado a fatos que se repetem entre casos. O filtro de modelo tira a maior parte do texto, e sobra pouco texto próprio (nomes, número do processo, valores, datas, um ou dois parágrafos). Consequências prováveis, ainda não medidas:
- regra 5 (`:108`, menos de 10 shingles específicos) → revisão;
- percentuais calculados sobre uma base de 30–80 palavras ficam ruidosos: um parágrafo a mais muda o resultado de faixa;
- duas versões da **mesma** petição (valor corrigido) podem ir para revisão. É o caso mais comum e o mais simples para um humano.

A §5.1 mede o reconhecimento do modelo, mas com petições que têm 6+ parágrafos de fatos próprios. Não mede o cenário em que o texto próprio é mínimo.

**Objetivo.** Decidir a mesma peça com pouco texto próprio sem abrir mão da segurança, no cenário mais comum da Enter. A taxa de revisão real é o maior risco que o próprio texto aponta.

**Decisão:** entra uma regra para texto próprio mínimo com identidade igual (item 2). A §5.2 mostra o cenário com e sem a regra.

**O que fazer no caderno:**
1. **Cenário (nova §5.2, "Petições quase só de modelo").** Gerador de "massa": 1 parágrafo de fatos curto, todos os outros de modelo (com a variação padrão de ~2–5%), em 300 casos de histórico do cliente com os mesmos modelos. Pares:
   - mesma petição com valor corrigido (versão, mesma peça);
   - mesma petição reexportada (cópia com ressalva);
   - duas petições independentes do mesmo modelo, no mesmo caso, de autores diferentes (diferente / outra instância);
   - petição × contestação que cita trechos dela (diferente).

   Imprimir a fração de texto próprio por documento e a classe resultante, sem a regra e com ela.
2. **Regra nova, antes da regra 5:** se o texto próprio for menor que um mínimo (ex.: 10 shingles específicos) **e** tipo de peça, partes (por CPF/CNPJ) e processo forem iguais nos dois documentos, decidir pelo alinhamento do **texto inteiro** (com modelo), usando os mesmos cortes. O diff de campos continua obrigatório. Por que é seguro: dentro do mesmo caso, duas peças do mesmo tipo e das mesmas partes não são "petições independentes do mesmo modelo". O risco que o filtro de modelo evita (vocabulário igual entre documentos sem relação) não existe com essa identidade.
3. **Nunca produz cópia** (cópia continua só por igualdade) e não se aplica a "outra instância" nem a "outra peça".
4. Incluir o tipo "petição quase só de modelo" no gerador da §10 (mesma peça com valor corrigido e duas independentes do mesmo modelo no mesmo caso). O erro crítico continua 0, e as petições independentes, com partes diferentes, nunca passam pela regra nova.
5. Asserts na §5.2: com a regra, a mesma peça com valor corrigido sai "versão · mesma peça" com o alerta de valor; as petições independentes do mesmo modelo continuam fora de "mesma peça"; nada vira cópia.

**O que fazer em `questao1.md`:**
- linha nova na tabela de regras (antes da 5) e uma frase explicando por que é segura (item 2 acima);
- uma linha nos resultados da §2 com os números da §5.2 (sem e com a regra);
- "Qual o maior risco" (guia em DECISOES): citar o cenário de massa e a regra.

**Pronto quando:** a §5.2 rodar com os asserts, a regra estiver no texto e em DECISOES, e a §10 continuar com 0 erro crítico.

### [x] T67. Auditoria aleatória das decisões automáticas (corrigir o viés de seleção dos rótulos)

**Problema.** "A revisão vira rótulo para calibrar" (`:15`, `:184`) e o shadow mode acompanha "a correção do revisor por classe" (`:146`). Mas o revisor só vê os pares da **fila**, ou seja, a faixa ambígua. O erro nos pares decididos automaticamente (cópia, versão, diferente) nunca é observado em produção, que é justamente onde estariam:
- o erro crítico (versão → cópia);
- o erro silencioso: versão muito reescrita que saiu "diferente" (abaixo de 20%) e ninguém revisou.

Calibrar os cortes só com os rótulos da fila desloca os limiares sem medir o efeito fora dela.

**Objetivo.** Ter uma estimativa sem viés do erro por classe na população que **não** passa por humanos, e com isso poder afirmar "erro ≤ x%" sobre o que o sistema decide sozinho, além de calibrar os cortes com dados representativos.

**O que fazer em `questao1.md`, §4 Avaliação:**
1. Novo bullet em "Método": "**Auditoria contínua:** uma amostra aleatória das decisões automáticas (ex.: 1% por classe, estratificada por classe e por faixa de percentual) vai para revisão às cegas. É a única forma de medir o erro onde ninguém olha. Os rótulos da fila servem para a faixa ambígua; os da auditoria, para os cortes e para o erro das classes decididas."
2. Volume: com a regra de três já citada (`:145`), para afirmar versão → cópia ≤ 1% é preciso ~300 cópias auditadas. Dizer em quantos dias isso se acumula a 1 mil docs/dia (calcular com a fração de cópias da §10 e dizer que é estimativa).
3. Custo: uma linha na tabela de trade-offs (§6), "auditoria 1%: +N revisões/dia", com o mesmo cálculo da §11.

**O que fazer no caderno (§11):** acrescentar a auditoria ao `custo_diario` como parâmetro (`"fração auditada": 0.01`) e uma coluna na tabela de revisão. Mudança de poucas linhas.

**O que fazer em `DECISOES_Q1.md` (§8 Avaliação):** linha nova: "Auditoria aleatória das decisões automáticas". Por quê: os rótulos da fila só cobrem a faixa ambígua. Rejeitado: calibrar só com a fila (viés de seleção).

**Pronto quando:** a auditoria estiver no método, no custo e em DECISOES, com o número de dias até ~300 cópias auditadas.

### [x] T68. Rede de recall abaixo de 20% para a mesma peça (complementa a T54)

**Problema.** Abaixo de 20% o par sai "diferente" e é **final**. Uma versão da mesma peça muito reescrita (paráfrase) sai "diferente" sem passar por ninguém. A T54 decidiu que o sinal semântico **não** roda abaixo de 20%, para não trazer de volta o "tema parecido". Isso vale para pares em geral, mas há um subconjunto em que o risco de tema não existe: dentro do caso, **mesmo tipo de peça + mesmas partes + mesmo processo**.

**Objetivo.** Cobrir o falso negativo silencioso de maior risco (a reescrita da própria peça) sem reabrir o problema do vocabulário parecido.

**Decisão:** a exceção entra. Dentro do caso, dois documentos do mesmo tipo e da mesma identidade quase nunca são independentes. Mandá-los para revisão custa pouco, e chamar uma reescrita da própria peça de "diferente" esconde do advogado que o documento substitui outro.

**O que fazer (só texto; a T54 é a seção que recebe a frase):** na seção "Faixa ambígua: sinal semântico" da T54, acrescentar: "Exceção: dois documentos do mesmo tipo de peça, das mesmas partes e do mesmo processo, com menos de 20% de texto igual **e** cobertura semântica ≥ 60% nos dois sentidos, vão para revisão como 'possível reescrita da mesma peça'. Fora dessa identidade, abaixo de 20% continua 'diferente'." Na tabela de regras, a regra 9 ganha "salvo a exceção da reescrita (§2)".

**Pronto quando:** a exceção estiver na seção da T54 e na regra 9.

### [x] T69. Medir a identidade da peça à parte (só texto)

**Problema.** O tipo de peça (título/qualificação) e as partes (CPF/CNPJ da qualificação) são heurísticas (`:208`, `:211`). Elas decidem entre "mesma peça" (**substitui** o anterior) e "outra peça" ou "outra instância" (não substitui), que é a informação que o advogado usa. A avaliação mede a classe, não a identidade.

**Objetivo.** Tratar a identidade como componente com métrica própria, como já é feito com candidatos, alinhamento e extração (`:144`), para que um erro de regex no título não fique escondido dentro de "acerto de versão".

**O que fazer em `questao1.md`, §4, bullet "Métricas" (`:144`):** acrescentar "**acurácia do subtipo** (mesma peça × outra peça × outra instância) nos pares rotulados 'versão', e acurácia da extração de tipo de peça e de CPF/CNPJ por documento".

**Pronto quando:** a métrica estiver na lista.

---

### Performance

### [x] T70. Limite de força bruta por volume de texto, não por número de documentos

**Problema.** "Até ~200 documentos no caso, compara com todos" (`:23`, `:197`; `limite_forca_bruta=200` no `Caso`). O custo depende do **tamanho** dos documentos: pela §11, um par de 300 páginas custa 113 ms. Então 200 autos de 300 páginas dão ~22 s por upload em um núcleo, enquanto 200 petições de 2 páginas dão ~0,1 s. O limite em documentos não controla a latência que pretende controlar.

**Objetivo.** O critério de troca para o índice de âncoras passa a refletir o custo real, mantendo a latência por documento previsível em casos com autos grandes.

**O que fazer no caderno (§9 e §9.4):**
1. `Caso.__init__`: trocar `limite_forca_bruta=200` (documentos) por `limite_palavras_forca_bruta` (soma das palavras dos documentos do caso). Valor: o que dá ~2 s de comparação por upload, calculado a partir da tabela da §11 (comparar(ms) por palavra). Escrever a conta no comentário.
2. `_candidatos`: força bruta se `sum(len(d.palavras) for d in todos) <= limite`; senão, índices exatos + âncoras.
3. §9.4: o "caso grande" continua passando para o índice (ajustar o parâmetro da demonstração para que isso aconteça, como hoje com 50).
4. Nenhum número da §8/§9.4 pode mudar além do parâmetro.

**O que fazer em `questao1.md`:** `:23` e `:197`: "até ~200 documentos" → "até ~N milhões de palavras no caso (cerca de 2 s de comparação por upload)", com o N calculado. Uma frase: "o limite é por volume porque autos de 300 páginas custam 50× uma petição de 20".

**Pronto quando:** o código e o texto usarem o mesmo critério e o número vier da tabela da §11.

### [x] T71. Consulta ao índice de modelo em memória no worker (só texto)

**Problema.** `indexar` consulta `eh_padrao` uma vez por shingle. Um documento de 100 mil palavras faz ~100 mil consultas. Se o índice estiver num KV remoto, são 100 mil round-trips, e a latência da §11 (0,46 s para indexar dois documentos de 286 páginas) deixa de valer.

**Objetivo.** Mostrar que a latência medida no caderno é alcançável na plataforma e dizer como.

**Decisão:** mapa exato em memória (HMAC → contagem de casos), só com as sequências de 3 ou mais casos (o snapshot da T62), carregado no worker por cliente. Filtro de Bloom foi descartado: um falso positivo marca texto próprio como modelo, baixa os percentuais e empurra o par para "diferente", que é a direção do erro silencioso. Além disso, o desconto do caso atual precisa da contagem exata.

**O que fazer em `questao1.md`, §6, bullet "Latência" (`:198`):** acrescentar "O snapshot do índice de modelo do cliente (só as sequências de 3 ou mais casos, com a contagem) fica em memória no worker e é consultado localmente, sem chamada remota por sequência."

**O que fazer em `DECISOES_Q1.md` (§5):** linha "Snapshot em memória, mapa exato". Rejeitado: KV remoto por sequência (latência) e filtro de Bloom (erro na direção de 'diferente' e sem contagem para o desconto).

**Pronto quando:** a frase estiver no texto e a decisão em DECISOES.

### [x] T72. Dimensionar o índice de modelo por cliente (só texto)

**Problema.** O texto dimensiona CPU (116 vCPU-hora/dia a 100 mil docs) mas não o índice de modelo. Num cliente grande de massa, a ordem de grandeza (estimativa, a recalcular) é:
- 100 mil casos × ~2 documentos × 20 páginas × ~400 palavras ≈ 1,6 bilhão de shingles por cliente;
- distintos: centenas de milhões, porque a maior parte é modelo repetido;
- com HMAC de 8 bytes + contagem: ordem de **GB por cliente** no snapshot, mais os conjuntos por caso (T62), que são maiores.

Carregar isso no worker (T71) e reconstruir o snapshot (T62) têm custo que o desenho não mostra.

**Objetivo.** Mostrar que o componente que mais cresce foi pensado: onde fica, quanto ocupa e como se mantém pequeno.

**O que fazer em `questao1.md`, §6, bullet "Escala" (`:197`):** acrescentar 2–3 frases:
1. "O índice de modelo cresce com o histórico do cliente, não com o caso. Estimativa para um cliente de 100 mil casos: centenas de milhões de sequências distintas, ordem de GB."
2. "Para mantê-lo pequeno: o snapshot em memória guarda só as sequências com 3 ou mais casos, as únicas que a consulta usa (T71). Os conjuntos por caso ficam no armazenamento de objetos e só são lidos para reconstruir o snapshot e para excluir um caso."
3. "A reconstrução é um job em lote por cliente (map-reduce sobre os conjuntos por caso), fora do caminho do upload."

**Caderno:** uma linha na §5.1 com o tamanho real do índice dos 80 casos: sequências distintas e quantas têm 3 ou mais casos (o tamanho do snapshot). A estimativa do texto usa essa fração.

**Pronto quando:** as frases estiverem no texto, com a estimativa rotulada como tal e calculada a partir da fração medida na §5.1.

### [x] T73. OCR pago no modelo de custo

**Problema.** O texto recomenda OCR gerenciado (Document AI, Textract ou Azure, `:54`), cobrado **por página**, mas o modelo de custo da §11 trata o OCR como CPU local (2 s/página × R$ 0,25/vCPU-hora). Com as premissas do caderno (20 páginas, 10% com OCR) e ~US$ 1,50 por mil páginas (preço de tabela a conferir na data):
- 1 mil docs/dia → 2 mil páginas → ~US$ 3/dia (~R$ 16), contra R$ 0,29 de CPU e ~R$ 2 de LLM;
- 100 mil docs/dia → ~R$ 1,6 mil/dia, contra R$ 29 de CPU.

A conclusão "a revisão humana domina" continua valendo (R$ 291/dia no melhor cenário), mas a tabela omite o maior custo de máquina.

**Objetivo.** Fazer a tabela de custo bater com a arquitetura recomendada no texto, para que um avaliador não ache a inconsistência.

**O que fazer no caderno (§11):**
1. `PREMISSAS`: acrescentar `"US$ por mil páginas de OCR gerenciado": 1.5` e `"R$ por US$"`, com comentário "preço de tabela, conferir".
2. `custo_diario`: coluna `"R$ OCR"` = docs × páginas × fração OCR × preço. Manter a CPU de OCR para a latência (p95), mas tirá-la do custo, porque o serviço gerenciado não consome a CPU da plataforma.
3. Tabelas "Máquina" e "Revisão por cenário": coluna R$ OCR.
4. Ajustar o assert final para `R$ revisão > 10 × (CPU + LLM + OCR)`. Com as premissas atuais ele vale: no melhor cenário, R$ 291 de revisão contra ~R$ 19 de CPU + LLM + OCR a 1 mil docs/dia.

**O que fazer em `questao1.md`, §6:** coluna "OCR/dia" na tabela de trade-offs (`:191–194`) e, no bullet "Precisão × custo" (`:196`), "CPU, OCR e LLM somados".

**Pronto quando:** a tabela do texto e a da §11 tiverem a coluna OCR com os mesmos números e o assert refletir a frase do texto.

---

### Fecho da rodada

- [x] **T74.** Restart & Run All limpo, 0 erros; conferir **todos** os números de `questao1.md` contra a nova saída (T59, T62, T63, T64, T65, T66, T70, T72 e T73 mexem em saídas).
- [x] **T75.** `DECISOES_Q1.md`: seção "Rodada 11" com uma linha por decisão (fidelidade da extração, snapshot versionado, fila por caso, precedência humana, reavaliação da fila, regra de massa, exceção da reescrita, mapa em memória, auditoria, limite por volume, OCR no custo) e as entradas novas no "Guia de defesa":
  - "E se o PDF mostrar um número e o texto extraído for outro?" → verificação de fidelidade da extração e raster com o mesmo layout (T59);
  - "O que acontece com decisões antigas quando o índice de modelo muda?" → a fila é reavaliada, as decisões entregues não são rebaixadas sem alerta (T64);
  - "Dois uploads simultâneos no mesmo caso?" → fila em série por caso (T63);
  - "Como vocês sabem o erro do que ninguém revisa?" → auditoria aleatória (T67).
- [x] **T76.** Conferir o tamanho de `questao1.md`: a rodada acrescenta várias frases. Cortar redundância em outros trechos para que o texto final não fique mais de ~10% maior que o de hoje. A entrega continua sendo só a solução, sem narrativa de processo.

### Notas de execução (rodadas 10 e 11, 2026-10-14)

- **T53:** saídas iguais às da execução anterior (comparadas célula a célula), exceto tempos e a §11, que mudou pela T73/T67.
- **T54:** a "Evolução" em fases saiu do texto: a Fase 2 (LLM na faixa ambígua) ficou redundante com as regras 10–12, e a entrega não é planejada em fases. O *shadow mode* deu lugar à auditoria (T67).
- **T59:** os PDFs adulterados ficaram na nova §7.3 (precisam de PDF; a §4.2 compara texto). O teste de "texto invisível" usa uma camada de texto invisível sobre a imagem de outro valor, porque só inserir texto invisível muda o texto extraído. O raster ignora a área das imagens (o carimbo já é diferença não textual e continua "cópia com ressalva").
- **T62:** §5.1 e os 800 pares originais da §10 idênticos ao antes.
- **T63–T65:** demonstrados na §9 (decisão do revisor, OCR concluído) e na nova §9.5 (fila reavaliada).
- **T66:** medido, e o risco previsto não apareceu. Em 300 casos de massa (mesmo réu, 10 modelos, uma frase de fatos) o texto próprio fica em 11–24% das palavras, 44–84 sequências; os quatro tipos de par saem certos sem a regra nova, que não dispara. A regra entrou como decidido e é exercida num caso montado (§5.2). A §10 ganhou 60 pares de massa (860 no total), avaliados com o índice do cliente de massa: com o índice de outro cliente, 26 de 30 independentes iam para revisão.
- **T70:** a razão real de custo 300 × 20 páginas é ~24× (o "50×" do plano vinha de números antigos); o texto usa os tempos medidos (22 s × 0,2 s).
- **T76:** o texto ficou ~12% maior que antes (28,5 KB × 25,5 KB), depois de quatro passadas de corte; o que sobrou é o que as tarefas pedem.
- **T22:** resolvida na rodada 12 pela T77 (PDF gerado por `gerar_anexo.py`).

## Rodada 12 — revisão adversarial (2026-10-14)

Ordem de execução: T79 → T77 → T78; depois T80–T84.

### [x] T77. PDF anexo gerado por código, coerente com `questao1.md` (substitui a T22)

**Problema.** `anexo_visual_questao1.pdf` ainda diz "Jaccard indica derivação", "shingles/IDF/MinHash", "Regras no MVP; modelo após rótulos", "Evolução: busca semântica" e "20–60% revisão". Contradiz o texto e mistura fases.

**Decisão.** Gerar o PDF por código (`gerar_anexo.py`, matplotlib, não vai na entrega), seguindo `DIAGRAMA_Q1.md`, com o mapa dos dois percentuais como figura central (regiões: diferente, versão, trecho, faixa decidida pela cobertura total, revisão; portão de igualdade à parte). Números e cortes lidos de `LIMIARES`.

**Pronto quando:** o PDF não citar Jaccard/MinHash/fases, os cortes baterem com `questao1.md` e o arquivo antigo tiver sido substituído.

### [x] T78. Embeddings executados de verdade na faixa de 20–60% (regras 10–12)

**Problema.** As regras 10–12 dependem de pares semânticos por parágrafo (cosseno ≥ 0,85), mas o código não implementa a cobertura total e o caderno não roda embeddings: as reescritas extensas vão para revisão e o corte de 0,85 não tem medida.

**Decisão.** Implementar a cobertura total em `q1.py` (parágrafos não alinhados, sem modelo nem citação, pareados na ordem com cosseno ≥ corte) com um modelo multilíngue real (`sentence-transformers`). Paráfrases fixas num JSON versionado (escritas uma vez por LLM), para o caderno não depender de API. Medir a distribuição do cosseno (paráfrase × outro parágrafo do mesmo caso), fixar o corte na calibração e mostrar no teste as reescritas saindo da revisão.

**Pronto quando:** as regras 10–12 rodarem no código, o corte vier da calibração e os números do texto forem os da nova execução.

### [x] T79. Corte de ocorrências das sementes sem degrau (`q1.py`, `trechos_iguais`)

**Problema.** Uma semente com mais de 20 ocorrências em B é descartada inteira. A contra "A repetido 20×" dá "cópia · trecho"; com 21×, "diferente" (erro silencioso).

**Decisão.** Limitar pelo produto das ocorrências em A e em B, não só em B.

**Pronto quando:** o teste "A repetido 21×" estiver nos casos de borda e as saídas do caderno não mudarem nos demais casos.

### Notas de execução (rodada 12, 2026-10-14)

- **T79:** saídas do caderno iguais, exceto o caso novo de borda (50/50 na época).
- **T77:** `gerar_anexo.py` gera o PDF a partir de `LIMIARES`; mapa dos dois percentuais como figura central. O PDF antigo está só no histórico.
- **T78:** o teste honesto com paráfrases achou três problemas, todos corrigidos e registrados em `DECISOES_Q1.md` (rodada 12): (1) a regra 8 chamava de "trecho" uma versão reescrita (agora exige tamanho 2×); (2) um corte único transformava paráfrase não reconhecida em "diferente" (agora dois cortes, calibrados em parágrafos); (3) qualificação e pedido de outro caso pareavam por estrutura (agora o par não contradiz os valores). Resultado no teste: 0 erros, revisão 10,9% → 7,9%; 13/19 reescritas → versão, 6 → revisão; 37/37 trechos reaproveitados → diferente. Modelo `paraphrase-multilingual-mpnet-base-v2` (20 ms/parágrafo em CPU). O conjunto de avaliação mudou de composição (o gerador consome o `rng` de outro jeito), então todos os números de `questao1.md` foram refeitos.
- A pasta foi movida para `Claudio/Q1` durante a rodada; o caderno rodou limpo (34 células) antes da mudança e não depende do caminho.

- **T81:** divisão pela árvore sintática (cada bloco de nível superior vai inteiro para um módulo). `q1.py` (solução, ~1.700 linhas) não tem nenhum nome indefinido sem os outros dois módulos (`pyflakes`): a solução não depende dos dados sintéticos. O índice padrão começa vazio, num registro por cliente (`INDICES_POR_CLIENTE`); `sinteticos.py` registra o cliente-1 ao ser importado. Saídas do caderno idênticas, exceto tempos.

### [x] T80. Avaliação com texto real: sentenças públicas de uma mesma vara

**Problema.** O filtro de modelo só foi testado com modelos sintéticos do mesmo autor das regras.

**Decisão.** 50–100 sentenças públicas de uma mesma vara (o juiz reaproveita modelos, como um cliente): medir o texto de modelo reconhecido e a classe dos pares independentes.

### [x] T81. Separar `q1.py` em solução, geradores sintéticos e avaliação

### [x] T82. Tabela de cortes: estruturais × calibráveis (no texto, curta)

### [x] T83. `DECISOES_Q1.md`: corrigir as linhas antigas (coleção de referência ≥ 5%, OCR com semelhança ≥ 0,6)

### [x] T84. Restart & Run All e conferência de todos os números de `questao1.md`

- **T80:** §10.6 com 226 sentenças reais (2 magistradas). Resultados: identidade 226/226; modelo reconhecido 39%/84% com o histórico próprio × 6%/25% com o da outra; 380 pares de processos diferentes sem nenhum "cópia"/"mesma peça" (359 diferente, 2 outra instância, 19 revisão de uma só homologação); cosseno calibrado chamaria 14 de "versão"; alterações controladas 193/195 certas, 2 revisão, 0 erros. O texto real revelou que a identidade não lia sentenças (corrigido em `q1.py`; saídas sintéticas iguais). Tempos no texto passaram a aproximados (±30% entre execuções); a asserção de tempo da §11 virou ordem de grandeza (≤ 10 s), para não quebrar em máquina carregada.

## Rodada 13 — revisão de engenharia: ferramentas, hipóteses e implementação (2026-10-14)

Tudo abaixo foi verificado com código antes de entrar aqui (comando e saída nas notas de cada tarefa). Ordem de execução: T85 → T86 → T87 → T88 → T89 → T90 → T91 → T92.

### Implementação (erro real, confirmado)

### [x] T85. O tipo de peça vira "inicial" em qualquer peça com abertura real ("nos autos da AÇÃO DE…")

**Problema.** `extrair_tipo` (`q1.py:248`) fica com o padrão que aparece **primeiro** na abertura, e "AÇÃO DE" faz parte da fórmula de quase toda peça que não é a inicial ("nos autos da AÇÃO DE INDENIZAÇÃO que lhe move…, vem apresentar CONTESTAÇÃO"). Testado:

| Abertura | Tipo lido |
|---|---|
| "…nos autos da AÇÃO DE INDENIZAÇÃO… vem apresentar CONTESTAÇÃO" | `inicial` |
| "…nos autos da AÇÃO DE INDENIZAÇÃO… vem apresentar MEMORIAIS" | `inicial` |
| "…nos autos da AÇÃO DE INDENIZAÇÃO… vem apresentar RÉPLICA" | `inicial` |
| "…inconformado com a r. SENTENÇA, vem interpor RECURSO DE APELAÇÃO" | `inicial` |
| "…vem propor a presente AÇÃO INDENIZATÓRIA em face de…" | `""` |
| título "PETIÇÃO INICIAL" | `""` |

De ponta a ponta: inicial × memoriais que repetem os fatos, com a abertura realista, sai **"versão · mesma peça"** (substitui a inicial). Com a abertura do gerador ("nos autos da ação", em minúsculas) sai "outra peça do caso". É o erro que a T26 dizia ter resolvido; só passou porque o gerador e a regra são do mesmo autor. E, com o tipo de um lado vazio, `_subtipo_versao` cai em "mesma peça" por omissão.

**Decisão.**
- O tipo é o **objeto do verbo da peça**: "apresentar/oferecer CONTESTAÇÃO|RÉPLICA|MEMORIAIS|CONTRARRAZÕES", "interpor|opor RECURSO|APELAÇÃO|AGRAVO|EMBARGOS", "propor|ajuizar (a presente) AÇÃO …". O título isolado ("CONTESTAÇÃO", "SENTENÇA") continua valendo. "AÇÃO DE" depois de "autos da/do" nunca define tipo.
- Precedência: qualquer tipo específico vence "inicial".
- "Mesma peça" (substitui) só com os **dois** tipos lidos e iguais. Com um tipo não lido, o resultado é "versão · peça não identificada": liga, mostra o diff e **não** substitui. Não é revisão: é uma versão decidida, só sem a afirmação de substituição.
- Gerador: memoriais, contestação e recurso passam a usar a abertura realista ("nos autos da AÇÃO DE … que lhe move …").

**Pronto quando:** as 6 aberturas acima estiverem nos casos de borda (§4.2) com o tipo certo; inicial × memoriais com abertura realista sair "outra peça do caso"; a §10 rodar com o gerador novo, com os números de `questao1.md` refeitos.

### [x] T86. Número de lei vira "valor em comum" e abre a trava do par semântico

**Problema.** `valores_do_paragrafo` (`q1.py:530`) conta como valor qualquer número com 3+ dígitos. Testado: "Lei nº 8.078/90", "art. 186" e "Súmula 479" saem como valores. Dois parágrafos de fatos **diferentes** que citam o CDC têm "valor em comum" e a trava ("um par não contradiz os valores do caso") deixa de valer justamente no caso mais comum do contencioso de consumo. Nos sintéticos isso não aparece porque os fatos do gerador não citam lei.

**Decisão.** Tirar de `valores_do_paragrafo` os números precedidos de "art.", "artigo", "lei", "nº" de lei, "súmula", "decreto", "inciso", "§" e os números no formato de lei (`\d{1,2}\.\d{3}/\d{2,4}`). Valor continua sendo data, R$, CPF/CNPJ, processo e número solto do caso (protocolo, contrato, quantidade).

**Pronto quando:** os dois parágrafos do teste acima não tiverem valor em comum; um caso de borda com dois fatos diferentes que citam a mesma lei, na faixa de 20–60%, não sair "versão".

### [x] T87. Embedding trunca parágrafos longos em 128 tokens

**Problema.** `paraphrase-multilingual-mpnet-base-v2` vem com `max_seq_length = 128`. Medido: **13%** dos parágrafos das sentenças reais (≥ 8 palavras) passam de 128 tokens (p90 = 156), e 11% dos parágrafos de fatos sintéticos (p90 = 129). O que passa do limite é cortado em silêncio; numa reescrita que muda a ordem das frases, o par é julgado pela metade. Petições têm parágrafos de fatos mais longos que sentenças.

**Decisão.** `max_seq_length = 512` (o modelo aceita; medido nos sintéticos: mesmos cortes, recall no corte alto 71,3% → 72,0%). Parágrafo acima de 512 tokens é dividido em janelas de frases, e o cosseno do par é o da melhor janela.

**Pronto quando:** a configuração estiver em `Embeddings` e a §10.1 refeita.

### Ferramentas e hipóteses

### [x] T88. Os cortes de cosseno foram "medidos" em paráfrases sintéticas, e o modelo separa mal

**Problema.**
1. A tabela de cortes chama 0,875/0,725 de "medidos", mas foram medidos em paráfrases de um gabarito fixo (`parafrases_q1.json`) sobre fatos de vocabulário fechado. O teste (§10.2) usa **o mesmo gabarito**: as 13/19 reescritas que saem "versão" estão na mesma distribuição da calibração.
2. Medido na amostra de calibração: no corte alto, o modelo acha só **71%** das paráfrases; no corte mínimo, **41%** dos pares de outro fato também passam. A separação vem quase toda da trava do valor (que a T86 mostra ser frágil), não do embedding. As 6 reescritas em revisão são consequência disso.
3. O modelo é de 2019 e treinado em paráfrase genérica. Há modelos multilíngues melhores para português na mesma faixa de custo.

**Decisão.**
- **Calibrar em texto real.** Paráfrases de parágrafos **das sentenças TJSP** (os mesmos fatos com outras palavras), escritas uma vez por LLM e versionadas em JSON, como já é feito com `parafrases_q1.json`. Negativos difíceis reais: parágrafos de outras sentenças **da mesma magistrada** (mesmo vocabulário, outros fatos). Calibração e teste separados por sentença.
- **Escolher o modelo pela medida**, não por default: comparar o mpnet atual com `intfloat/multilingual-e5-base` e `BAAI/bge-m3` nessa amostra real (AUC, recall no corte de falso par ≤ 1%, falso par no corte de recall ≥ 99%, ms por parágrafo em CPU) e ficar com o melhor. (Resultado nas notas de execução.)
- Na tabela de cortes, "medidos" passa a dizer onde: "em paráfrases reais de sentenças".

**Pronto quando:** o JSON de paráfrases reais existir; os dois cortes e o modelo saírem da amostra real; a §10.2 mostrar as reescritas sintéticas **e** as reais com os cortes novos.

### [x] T89. Os cortes de 20% e 60% têm evidência real e o texto diz que não têm

**Problema.** A tabela de cortes põe 20/50/60% em "a calibrar… só pares reais rotulados os calibram". Mas os 380 pares reais de processos diferentes já medem o lado do corte de 20%. Medido (`pct_alto`): Magistrada A, p99 = 7%, máximo 12%; Magistrada B, p99 = 28%, com 1 par em 23% (sai "diferente" pela cobertura total) e 2 acima de 60% (as duas sentenças-modelo de desistência/ausência, que saem "versão · outra instância", a resposta certa). As alterações reais ficam todas acima de 90%.

**Decisão.** A linha "A calibrar" vira "Verificados em texto real": 20% (99% dos pares de processos diferentes ficam abaixo; os que passam, a cobertura total decide) e 60% (nenhuma alteração real abaixo de 90%). 50%, 55%/65% e os cortes de cliente sem histórico continuam declarados como escolhidos, com o motivo de cada um em uma linha. Uma figura na §10.6: histograma de `pct_alto` dos pares reais com os cortes marcados.

**Pronto quando:** a §10.6 imprimir esses percentis e `questao1.md` usar esses números.

### Texto (`questao1.md`)

### [x] T90. "±5 pontos em volta de 60%" não é o que o código faz

**Problema.** O texto diz que, na faixa, só a margem de ±5 pontos em volta de 60% de cobertura total vai para revisão. No código (`q1.py:1109–1122`), a revisão é decidida por **dois cortes de cosseno diferentes**: um par com 40% de cobertura no corte alto e 70% no corte mínimo vai para revisão, e isso não é "±5 pontos". A regra 12 da tabela tem o mesmo problema.

**Decisão.** Reescrever a frase e a regra 12 como o código decide: "versão" se a cobertura com o corte alto passa de 65%/50%; "diferente" se nem com o corte mínimo passa de 55%; revisão no resto.

### [x] T91. Respostas curtas às seis perguntas do enunciado, no topo

**Problema.** O resumo explica a ideia e as decisões, mas quem corrige procura as seis perguntas do enunciado e tem de achá-las em 220 linhas densas (12 regras com 2a e 4a, exceções, tabelas).

**Decisão.** Logo depois da ideia central, uma tabela de seis linhas: pergunta do enunciado → resposta em uma frase → seção. As regras da seção 2 são renumeradas de 1 a N, sem "2a"/"4a" (mesma numeração nos comentários de `q1.py`).

### Fecho da rodada

### [x] T92. Restart & Run All, conferência de todos os números e `DECISOES_Q1.md`

`DECISOES_Q1.md`: seção "Rodada 13" (tipo pelo objeto do verbo e "peça não identificada"; números de lei fora dos valores; 512 tokens; cortes e modelo calibrados em paráfrases reais; cortes de 20%/60% verificados em texto real). Guia de defesa: "Como o sistema sabe que é memoriais e não a inicial?" e "Por que esse modelo de embedding?".

### Notas de verificação (rodada 13)

- **T85:** `extrair_tipo` nas 6 aberturas da tabela; `classificar(inicial, memoriais)` com a abertura do gerador → "versão · outra peça do caso" (`tipos = ('inicial', 'memoriais')`); com a abertura realista → "versão · mesma peça" (`('inicial', 'inicial')`).
- **T86:** `valores_do_paragrafo("…Lei nº 8.078/90 e do art. 186 do Código Civil…")` → `{('número', '186'), ('número', '8.078/90')}`.
- **T87:** `SentenceTransformer(...).max_seq_length == 128`; tokens por parágrafo: sentenças reais mediana 54, p90 156, 13,2% > 128; fatos sintéticos mediana 91, p90 129, 10,7% > 128. Com 512: recall no corte alto 0,713 → 0,720; falso par no corte alto 0,007 nos dois casos.
- **T88:** na amostra de calibração (seed 1), mpnet: recall no corte alto 0,71, falso par no corte mínimo 0,41; medianas do cosseno 0,90 (paráfrase) × 0,70 (outro fato).
- **T89:** `pct_alto` nos 190 pares de cada magistrada: A p50 0 / p99 0,071 / máx. 0,116; B p50 0 / p99 0,281 / máx. 0,864 (2 pares ≥ 0,60, ambos "outra instância"; 1 par em 0,231, "diferente"). Os 19 em revisão da B têm `pct_alto` = 0 (texto próprio insuficiente).

### Notas de execução (rodada 13, 2026-10-14)

- **T85:** `extrair_tipo` lê o objeto do verbo da peça (verbo depois de "vem/vêm", ou nome da peça em maiúsculas: "Requer a citação para apresentar contestação" continua sem tipo); depois o título isolado; depois maiúsculas; "inicial" por último. A abertura passou a ir até ~60 palavras, porque um extrator que quebra "EXMO. / SR. / DR." em linhas empurrava a qualificação para fora (achado pela §10: 14 "frases em linhas + valor" saíam "peça não identificada"; o código antigo também não lia o tipo ali, só o escondia com o padrão "mesma peça"). Gerador: contestação e memoriais com a abertura real. Novo subtipo "peça não identificada" (não substitui, fora dos grupos). §4.2: 7 aberturas com `assert` e o caso novo "tipo não lido num dos lados" → "versão · peça não identificada". 226/226 sentenças continuam com tipo.
- **T86:** `RE_NORMA` tira art./lei/súmula/decreto/inciso/§/"8.078/90" antes de procurar valores. §4.2: "outra petição copia 2 fatos; todos os fatos citam o CDC" → "diferente".
- **T87:** `max_seq_length = 512`; acima disso, média das janelas de frases. Efeito no teste: reescritas extensas 13 → 14 de 19 "versão" (5 em revisão).
- **T88:** comparação de modelos em 57 paráfrases reais × 24.386 pares de outros processos da mesma magistrada: mpnet AUC 0,9992, 18 ms/parágrafo; e5-base AUC 0,9990, cossenos comprimidos (corte de 1% de falso par em 0,965); bge-m3 AUC 0,9994, 60 ms/parágrafo. Fica o mpnet. Nos sintéticos, o mpnet tem AUC 0,977 (os negativos sintéticos são mais difíceis). Cortes mantidos: no real, alto 94,7%/96,2% de recall (calibração/teste) com 0,12%/0,06% de falso par; mínimo 100% de recall com 1,1%/0,8% de falso par. §10.1 imprime e verifica. `parafrases_reais_q1.json`: 109 paráfrases de 18 sentenças (57 calibração, 52 teste, separadas por sentença; ementas e transcrições não parafraseadas). §10.6: reescritas reais 6/6 "versão · mesma peça"; trechos reaproveitados reais 5 "diferente" + 1 revisão, 0 erros. A revisão vem de parágrafos genéricos que passam o corte mínimo (limitação no texto); o melhor par recíproco foi testado e não ajuda.
- **T89:** a afirmação do plano "nenhuma alteração real abaixo de 90%" estava errada: medido, edições pontuais ≥95% e parágrafo removido ≥72% (menor dos dois percentuais); o texto usa esses números. §10.6 imprime p99/máximo do maior percentual por magistrada (A: 7%/12%; B: 28%/86%) e o histograma com os cortes. Tabela de cortes: "Verificados em texto real" (20%, 60%) e "Escolhidos" (50%, 55/65%, 60% abaixo de 20%, cliente sem histórico).
- **T90/T91:** regra 14 e a frase da faixa descrevem os dois cortes; regras 1–14 sem "2a"/"4a" (texto e comentários de `q1.py`); tabela de respostas curtas no topo de `questao1.md`.
- **T92:** Restart & Run All limpo (68 células, 0 erros). Números que mudaram e foram atualizados em `questao1.md`: casos de borda 53 → 55; revisão 7,9% → 7,8%; histórico sem fatos 8,0% → 7,9%; cosseno do documento inteiro dif.→versão 52 → 53 e versão→dif. 27 → 26; contenção de conjuntos 12,7% → 12,6%; reescritas 13/6 → 14/5. PDF anexo regenerado. `DECISOES_Q1.md`: seção "Rodada 13" e 2 perguntas no guia de defesa. `questao1.md` cresceu ~4 KB (tabela de respostas curtas e evidência real).
