# Histórico de decisões — Questão 1

O que foi decidido e por quê. Não vai na entrega. O que falta fazer fica em `TRACKING_Q1.md`.

---

## 1. Medida de similaridade

| Decisão | Por quê | Alternativas rejeitadas |
|---|---|---|
| **Cobertura (contenção) nos dois sentidos**: fração do conteúdo específico de A que reaparece alinhada em B, e o inverso | A pergunta jurídica é "quanto de A está em B". Com os dois sentidos dá para separar "B é versão de A", "A está dentro de B" e "B é A abreviado" | **Jaccard** (usado na v1): é simétrico e cai com a diferença de tamanho. Uma petição dentro de autos 10× maiores tem Jaccard perto de zero. Também cai muito em textos curtos quando muda um único valor. Foi retirado de tudo, inclusive como "contraste" e como baseline. **Cosseno de palavras/embeddings do documento inteiro**: mede tema e não derivação. Duas petições independentes do mesmo modelo dão cosseno > 0,9 |
| **Cópia só por igualdade** (bytes, texto, texto normalizado) | Chamar uma versão de "cópia" é o erro mais caro: o advogado ignora um valor alterado. Se nenhum limiar produz "cópia", esse erro só pode nascer na normalização, que é pequena e testável | Limiar alto de similaridade para "cópia": um centavo diferente passaria |
| **Texto padrão filtrado por frequência numa coleção de referência** (shingle em ≥5% dos documentos) | "Ante o exposto…" não é evidência de derivação. É a técnica padrão contra o "vocabulário jurídico parecido" do enunciado | Stopwords ou lista manual: não pega fórmulas de várias palavras |
| **Índice de modelo como snapshot versionado, construído a partir dos conjuntos por caso** (rodada 11) | Conta casos (não documentos), desconta o caso atual, permite excluir um caso e grava a versão em cada decisão, que fica reproduzível e reavaliável | Contador incremental por documento: não sabe se a sequência já foi contada no caso, não decrementa e faz um upsert por shingle |
| **Citações explícitas não contam como derivação** (rodada 7) | Dentro de um caso, as peças se citam o tempo todo (a contestação transcreve a inicial, a sentença reproduz os pedidos). Sem isso, documentos diferentes do mesmo caso caem na faixa de revisão | Filtro de frequência por caso: também apagaria o conteúdo comum entre versões, que é justamente o sinal |

## 2. Unidade de comparação e alinhamento

| Decisão | Por quê | Alternativas rejeitadas |
|---|---|---|
| **Alinhamento sobre a sequência de palavras do documento inteiro** (rodada 7): sementes de 5 palavras iguais, estendidas ao maior trecho igual e escolhidas do maior para o menor, sem sobreposição (variante do *Greedy String Tiling* do JPlag: uma passada coleta todas as corridas máximas a partir das sementes, que depois são escolhidas do maior para o menor; o original repete rodadas) | Não depende de onde o extrator quebra os parágrafos. Lida com trechos movidos, divididos e unidos sem regra especial | **Parágrafo = bloco do PDF** (rodadas 1–6): os blocos do PyMuPDF não são parágrafos (linha, coluna, célula de tabela). Exigia union-find, grupos 1:N e um fallback N:M só para remendar a segmentação. **Diff global (LCS)**: não lida com trechos movidos |
| **Região alinhada mínima de 15 palavras** (rodada 7) | Sem a agregação por parágrafo, frases curtas de 5–10 palavras coincidiam por acaso entre petições independentes do mesmo modelo, e a cobertura de documentos diferentes subia para ~19% (perto do corte de 20%). Com o mínimo, volta a 0–2% | Agregar por parágrafo: devolve a dependência da segmentação |
| **Início e fim do documento como âncoras; lacuna longa entre regiões aceita só com ≥80% de palavras batendo** (rodada 7) | Uma edição nas últimas palavras ou um parágrafo de texto padrão com ruído entre duas regiões (sem sementes, porque texto padrão não é semente) ficava "removido + incluído". O corte de 80% evita contar texto novo como coincidência | Sementes também no texto padrão: faria texto padrão comum ligar documentos independentes |
| **Shingles de 5 palavras** | Curtos o bastante para sobreviver a uma edição local; longos o bastante para serem específicos | — |
| **Palavra específica = a maioria dos shingles que a cobrem é específica** (rodada 7) | No texto corrido, um shingle que atravessa a fronteira entre dois parágrafos padrão é raro, e marcaria texto padrão como específico | Calcular os shingles por parágrafo: devolve a dependência da segmentação |
| **Parágrafo continua existindo para exibição, página e cache** | O revisor lê por parágrafo e página; a análise por LLM em cache também | — |
| **Diff de palavras (com pontuação) só dentro das regiões alinhadas** | Mostra o que mudou e onde, e é barato | LLM comparando os documentos inteiros: caro, não cabe, difícil de auditar |

## 3. Decisão

| Decisão | Por quê |
|---|---|
| Regras curtas, em ordem: bytes → extração falhou → texto igual → normalização → texto insuficiente → versão → trecho → diferente → revisão | Explicáveis e auditáveis. A falha de extração vem antes da igualdade de texto, porque um OCR parcial pode produzir textos iguais por acidente |
| Faixa de 20–60% decidida pela **cobertura total** (literal + pares semânticos por parágrafo, cosseno ≥0,85, na ordem): ≥65%/≥50% → versão; <55% → diferente; 55–65% → revisão (rodada 10) | É onde a contagem de texto igual não separa "mesma peça reescrita" de "outra peça que reaproveita trechos". Fora dela, embeddings só trariam de volta o tema. Rejeitado: mandar a faixa inteira para revisão (é onde estão as reescritas); embedding do documento inteiro (mede tema); embeddings como sinal principal (não localizam a mudança nem provam igualdade) |
| Cortes 20% / 60% / 50% | Pontos de partida. Abaixo de 20% sobra só coincidência; acima de 60% do menor há derivação. Precisam de calibração com pares reais rotulados |
| Taxonomia pública: as 3 classes do enunciado + "em revisão" (temporário), com atributos (exata/com ressalva; mesma peça/outra instância; documento/trecho) | O advogado precisa saber se o documento **substitui** o anterior (mesma peça) ou é o mesmo modelo usado para outra parte (outra instância) |
| Identidade = partes da qualificação + processo do cabeçalho/preâmbulo; nomes parecidos não contam como troca | Testemunhas, advogados e precedentes citados não mudam a identidade da peça. Um erro de digitação também não |
| Confusões de OCR reconhecidas por forma canônica (rn→m, 1/i→l, 0→o, c→e, sem acento) ou semelhança de caracteres ≥ 0,6 (rodada 7) | Só a semelhança não pegava "com" × "corn" (0,57), a confusão mais clássica de OCR |
| "Em revisão" quando a diferença pode ser ruído de OCR (rodada 7) | Dois scans do mesmo papel geram textos diferentes. Sem isso, o sistema dispara "valor alterado" por causa de um 5 lido como 6. Ainda assim não vira "cópia", porque um dígito trocado pelo OCR pode ser real |

## 4. Normalização

| Decisão | Por quê |
|---|---|
| Lista branca: NFC, ligaduras, aspas/travessões tipográficos, caixa, espaços, hifenização de quebra de linha, linhas "Página N de M" | São mudanças que nunca alteram o sentido. Todo o resto (vírgula, dígito, espaço dentro de número) é material |
| Hifenização só entre **letras** (rodada 7) | Com `\w`, `"10-\n20"` virava `"1020"`: um intervalo virava outro número, e o par saía como "cópia com ressalva" |
| Numeração de página só no formato **"Página N de M"** (rodada 7) | A versão anterior apagava qualquer linha `"fls. 120"`. Referências a folhas dos autos são comuns em peças, e trocar a folha virava "cópia com ressalva" |
| Cabeçalho/rodapé fora do corpo, mas dentro da igualdade | Um nº de processo trocado no cabeçalho não pode sumir |
| Imagens e assinatura digital entram na igualdade | A peça assinada/carimbada e o rascunho com o mesmo texto não são a mesma coisa |

## 5. Busca de candidatos

| Decisão | Por quê | Alternativas rejeitadas |
|---|---|---|
| Até ~2 milhões de palavras no caso: compara com todos (rodada 11; antes, ~200 documentos) | O custo depende do tamanho: ~1 µs por palavra do documento já no caso, então 2 milhões de palavras ≈ 2 s por upload. 200 autos de 300 páginas custam ~22 s; 200 petições de 2 páginas, 0,2 s | Limite em número de documentos: não controla a latência |
| Snapshot do índice de modelo em memória no worker, mapa exato (rodada 11) | A latência medida (consulta por shingle) só vale com consulta local | KV remoto por sequência (100 mil round-trips por documento longo); filtro de Bloom (falso positivo marca texto próprio como modelo e empurra o par para "diferente", e não dá a contagem para descontar o caso atual) |
| Acima disso: índices exatos + índice de âncoras por *winnowing* (MOSS) sobre os shingles específicos; candidato = contenção estimada ≥ 10% | O winnowing devolve a **posição** do trecho comum e estima contenção nos dois sentidos | **MinHash/LSH**: o MinHash comum estima Jaccard. Dá para estimar contenção com MinHash e indexá-la com LSH Ensemble, mas na escala de um caso não precisa de índice aproximado, e ele não diz onde está o trecho |
| Índices exatos antes das âncoras | Um documento só de texto padrão (procuração-modelo) não tem âncoras; as cópias dele vêm do hash | — |

## 6. Documentos longos e LLM

| Decisão | Por quê |
|---|---|
| A comparação não usa LLM | O alinhamento por sementes compara 300 páginas em fração de segundo |
| O LLM só resume as mudanças, a partir dos trechos alterados, pseudonimizados e dentro de um orçamento de tokens | Custo e privacidade (LGPD). O resumo ajuda o revisor; a classe continua auditável |
| Cache de análise por parágrafo, escopado por cliente | Uma nova versão só paga pelo que mudou. O cache não cruza clientes |

## 7. Documentos escaneados

| Decisão | Por quê | Alternativas rejeitadas |
|---|---|---|
| OCR nas páginas sem texto; em produção, um OCR de qualidade (Document AI, Textract ou Azure) | A igualdade e o diff dependem da qualidade do texto | Tesseract: fraco em documento jurídico digitalizado |
| pHash (DCT) por página para anexos só de imagem (rodada 7), sempre como "provável cópia" para confirmação | O pHash é o padrão para "mesma imagem digitalizada de novo" e é mais robusto que o aHash | aHash 8×8 (rodadas 3–6): não separava petições do mesmo modelo |

## 8. Avaliação

| Decisão | Por quê | Alternativas rejeitadas |
|---|---|---|
| "Em revisão" é abstenção, não classe: medimos abstenção e erro por classe verdadeira | O mundo só tem cópia, versão e diferente | — |
| Limiares fixados antes de gerar o teste; calibração e teste com seeds separadas | Evita ajustar limiares no teste | — |
| Limite superior exato (Clopper-Pearson) para versão → cópia | Com 0 erros em n, o limite é ≈ 3/n; "0 erros" sozinho não diz nada | — |
| Baselines por **ablação** (rodada 7): sem filtro de texto padrão; contenção de conjuntos sem alinhamento; cosseno do documento inteiro | Mostram o que cada componente acrescenta e o que uma equipe ingênua faria | Baseline de Jaccard (rodadas 1–6): espantalho, e mantinha na entrega um método descartado |
| Abstenção agregada por documento | 1% por par com 30 comparações vira 26% dos documentos; o revisor trabalha por documento | — |
| Auditoria aleatória das decisões automáticas (1%, estratificada por classe e faixa) (rodada 11) | Os rótulos da fila só cobrem a faixa ambígua; o erro das classes decididas só é observável por amostra às cegas | Calibrar só com a fila (viés de seleção) |
| Dados sintéticos só como teste de invariantes (rodada 10) | O gerador e as regras são do mesmo autor; o número real exige pares reais rotulados às cegas, com kappa | — |

## 9. O que saiu da entrega (rodada 7)

| Item | Por quê saiu |
|---|---|
| Texto narrativo no caderno ("leitura honesta", "declaração", "o que a avaliação pegou") | O caderno é a solução; o histórico fica aqui |
| Embedding didático (mapa de sinônimos escrito à mão) | Feito para o `assert` passar; não prova nada. No texto, embeddings ficam como extensão (recuperar paráfrase → revisão), sem número |
| Classificador calibrado da fase 2 (logística + Clopper-Pearson/Learn-then-Test) | Nos dados sintéticos as classes são separáveis, então o número não prova nada. Fica como próximo passo no texto: um LLM julgando os trechos alinhados na faixa ambígua, automatizado só depois de medido com rótulos reais |
| `Plataforma` com SQLite (~400 linhas simulando infraestrutura) | Não demonstra o algoritmo. Idempotência, concorrência e isolamento ficam descritos no texto. O caderno mantém o que é algoritmo: extração, ações por classe, grupos e cache |

## 10. Achados que mudaram o desenho

- **Rodada 1:** a avaliação achou 6 "versão → cópia". A causa estava no gerador: uma negação caía em parágrafo sem verbo. O gerador passou a exigir `B != A`.
- **Rodada 2:** palavra hifenizada em volta do rodapé virava "versão". A ordem da normalização foi invertida.
- **Rodada 2:** o cabeçalho com outro processo sumia (dígitos mascarados). Passou a entrar na igualdade.
- **Rodada 4:** o cache por parágrafo cruzava clientes. Passou a ser escopado por cliente.
- **Rodada 6:** o LSH perdia documento contido em outro. Foi trocado pelo índice de âncoras.
- **Rodada 7 (revisão de ferramentas):** duas regex da normalização produziam falso "cópia com ressalva". O parágrafo do PDF não é unidade confiável. Citação dentro do caso e ruído de OCR não estavam cobertos.

- **Rodada 7, na implementação:** a avaliação pegou 5 de 18 "novos scans com OCR" saindo como "versão" (alertas falsos). As causas eram as bordas do documento, um parágrafo padrão entre regiões e a confusão rn/m. Depois da correção, 18/18 vão para revisão como "provável cópia (OCR)".
- **Rodada 7:** o PDF de demonstração gravava "?" no lugar das aspas tipográficas (a fonte base não tem o glifo), e a citação não era detectada. Era artefato do gerador de PDF; as aspas agora são convertidas para ASCII ao gerar.
- **Rodada 7:** shingles que atravessam a fronteira entre dois parágrafos padrão são raros na coleção de referência e viram âncoras. A demonstração da procuração-modelo passou a usar um único parágrafo padrão; a garantia para documentos só de texto padrão continua vindo dos índices exatos.

- **Rodada 8 (revisão de ferramentas):** a tolerância a OCR aceitava qualquer par com `SequenceMatcher ≥ 0,6`; "R$ 49.407,65" × "R$ 99.407,65" e "procedente" × "improcedente" num novo scan saíam como "provável cópia (OCR)", confirmável em lote. Agora só o mapa de confusões de letras conta como ruído; número × número em texto de OCR vai para conferência item a item, nunca em lote.
- **Rodada 8:** dentro de um caso, partes e processo são sempre os mesmos, então a identidade não separava peças. Memoriais que repetiam os fatos da inicial saíam "versão · mesma peça" (substitui). Entrou o tipo de peça; tipo diferente → "outra peça do caso" (reaproveita o texto, não substitui, não entra no grupo).
- **Rodada 8:** num documento contido em outro, o processo do cabeçalho do menor não era comparado com o do maior: uma peça de outro processo saía "cópia com ressalva" do trecho dos autos. Agora o trecho herda o processo dos autos ou do cadastro do caso, e identidade diferente nunca é cópia do trecho. Os campos do trecho passaram a ser comparados com o trecho, não com os autos inteiros.
- **Rodada 8:** o baseline de cosseno usava cortes fixos (0,98/0,80) e dava 354 falsos "cópia": era um espantalho. Com cortes calibrados (cópia ≥ 1,00, versão ≥ 0,96) dá 18 — continua errando a classe crítica, mas a comparação agora é justa.
- **Rodada 8:** a curva do limiar de derivação é quase plana nos sintéticos (0,10–0,90 → 87%–83% das versões). Isso fica declarado no texto: os dados não testam o corte.

- **Rodada 8:** "cobertura do menor/maior" confundia quem lia. Os nomes passaram a ser "% de A encontrado em B" e "% de B encontrado em A", com a regra dita como "o maior dos dois percentuais" (derivação) e "o menor dos dois" (documento inteiro × trecho).

- **Rodada 8:** o filtro de texto padrão usava uma coleção fixa de 400 petições sintéticas com 10 parágrafos padrão sempre iguais. Isso não representa a realidade (cada escritório tem seus modelos e os redige de um jeito a cada uso) e fazia o filtro parecer perfeito. Trocado por um índice aprendido no histórico do cliente: sequência presente em ≥3 outros casos do mesmo cliente é modelo. O gerador passou a ter modelos com trechos alternativos, partes opcionais e edições soltas, e a §5.1 mede o reconhecimento por nível de variação e por tamanho do histórico. Cliente com menos de 20 casos: "versão" automática só com ≥90% nos dois sentidos.

## Rodada 9 — avaliação externa (Cursor)

Aceito, depois de verificar no código:
- **Identidade pelo nome:** "Maria Silva" × "Marina Silva" com CPFs diferentes saía "versão · mesma peça" (96% de semelhança no nome). Agora o CPF/CNPJ decide e o nome só desempata.
- **Índice de modelo global na ingestão:** o `Caso` usava o histórico do cliente-1 para qualquer cliente. Agora cada cliente tem o seu; cliente novo cai na regra conservadora.
- **Tudo-ou-nada na extração:** uma página sem texto (ou PDF reparado) tirava o documento da comparação. Agora compara com as páginas lidas; "cópia" fica bloqueada enquanto a extração estiver incompleta (no trecho, só se faltar página no trecho ou no documento contido); valores que só "faltam" no lado incompleto não viram alerta.
- **Winnowing "devolve a posição":** não devolvia. O argumento contra o MinHash passou a ser contenção × Jaccard.
- **Fatos tomados por modelo (33–44% no gerador):** os fatos do gerador ganharam detalhes do caso, mas o repertório continua fechado. Em vez de aumentar o vocabulário sem fim, um controle com histórico sem fatos mostra que o resultado não depende disso (20/20 diferentes; avaliação com 0 erros e 11,4% de revisão).
- **LLM:** texto da peça como dado, resposta validada contra o formato, endereço e CEP pseudonimizados.

Recusado: infra implementada, OCR real no caderno, GST com sementes muito frequentes, p95 e custo modelados, avaliação circular (motivos no tracking).

## Rodada 10 — avaliação de ferramentas

- **Embeddings por parágrafo decidem a faixa de 20–60%** (só desenho; o caderno não roda embeddings). O texto comparava embeddings só com o cosseno do documento inteiro, uma alternativa que ninguém usaria.
- **Saiu a "Evolução" em fases.** A Fase 2 (LLM julgando a faixa ambígua) ficou redundante com a decisão acima, e a entrega não é planejada em fases. O *shadow mode* deu lugar à auditoria contínua (rodada 11).
- **Avaliação apresentada como teste de invariantes:** contagens de erro e taxa de revisão, sem "acerto 100%", que em dados do mesmo autor sugere teste viciado.
- **"Outra instância" dentro de um caso** ganhou contexto: peça de outro processo juntada, documento no caso errado, extensão entre casos.
- **GST:** a implementação é uma variante de uma passada, e o texto diz isso.
- **Código em `q1.py`;** o caderno só executa as demonstrações (mesmas saídas, verificado).

## Rodada 11 — segurança, consistência, freshness, acurácia, performance e escala

| Decisão | Por quê | Rejeitado |
|---|---|---|
| Fidelidade da extração: texto invisível, texto coberto, fonte sem mapa → nunca "cópia" por texto; com o mesmo layout, raster igual | O texto extraído pode não ser o que a página mostra; "cópia" tem de depender do que o advogado vê. Custo: ~4 ms/página na ingestão, ~1 ms/página só nos pares que iam sair cópia | Raster sempre: toda reexportação com outra fonte iria para revisão, sem ganho |
| Ingestão isolada (container sem rede, só leitura, um documento por processo); HMAC com chave por cliente nos índices | Parser de PDF é superfície de ataque; hash sem chave de 5 palavras é reversível por dicionário | — |
| Fila em série por caso | Cada documento vê todos os anteriores sem depender da consistência do índice; a vazão vem do paralelismo entre casos | Confiar em read-your-writes de um índice de busca |
| Decisão do revisor presa à evidência (hash do texto) | Precedência clara: a máquina não sobrescreve o revisor, e o revisor não fica preso a evidência que mudou | Reabrir a cada versão de pipeline ou índice (só a divergência é registrada) |
| Reavaliar só a fila quando o snapshot muda | A fila é o que custa; decisões entregues não são rebaixadas em silêncio | Recomputar todos os pares |
| Evidência nova (OCR concluído) recompara o documento, com histórico | "Reprocessar" precisava de gatilho e destino para as decisões antigas | — |
| Regra do texto próprio mínimo (4a): mesma identidade documentada → texto inteiro, nunca cópia | Proteção para peças quase só de modelo. Medido: nos dados de massa o texto próprio fica em 44–84 sequências e a regra não dispara; o risco previsto (massa → revisão) não apareceu | — |
| Exceção da reescrita abaixo de 20% (mesmo tipo, partes e processo, semântica ≥60%) → revisão | É o falso negativo silencioso de maior risco, e a identidade tira o risco de "tema parecido" | — |
| Auditoria aleatória de 1% | Mede o erro onde ninguém olha | Calibrar só com a fila |
| Limite de força bruta por volume | O custo depende do tamanho dos documentos | Limite em documentos |
| OCR gerenciado no custo (por página) | É o maior custo de máquina (~R$ 16/dia a 1 mil docs) e a tabela tem de bater com a arquitetura | CPU local como proxy do OCR |

Achados: sem o filtro de modelo, petições de massa independentes viram "versão" falsa (14 de 30); com o histórico do próprio cliente de massa, 30/30 "diferente". Avaliadas com o histórico de outro cliente (sem o réu fixo), 26 de 30 iam para revisão: o índice de modelo precisa ser do cliente certo.

## Rodada 12 — revisão adversarial (2026-10-14)

| Decisão | Por quê | Rejeitado |
|---|---|---|
| Semente repetida só é descartada se repetir nos **dois** lados (mais de 20 vezes em A e em B) | Uma petição contra autos que a juntam 21 vezes saía "diferente": todas as sementes eram descartadas porque repetiam em B | Limite só em B (degrau para o erro silencioso) |
| Anexo visual gerado por código (`gerar_anexo.py`) a partir de `LIMIARES` | O PDF antigo citava Jaccard, MinHash e fases; gerado do código, não diverge | Desenho manual |
| Embeddings executados de verdade: `paraphrase-multilingual-mpnet-base-v2`, por parágrafo, só nos parágrafos próprios não alinhados | As regras 10–12 dependiam de um sinal nunca medido. Medido: o mpnet acha 85% das paráfrases a 0,85 contra 53% do MiniLM, com falso par parecido | MiniLM (separa pior); embedding do documento inteiro (mede tema) |
| Reescrita no gerador = **os mesmos fatos com outras palavras** (`parafrases_q1.json`, escrito uma vez por LLM) | A "reescrita extensa" antiga trocava 2/3 dos fatos por fatos novos: não era paráfrase, e o rótulo "versão" era discutível | Gerar paráfrases com API no caderno (não reproduzível sem chave) |
| **Dois cortes semânticos**: alto 0,875 (par que conta para "versão": falso par ≤ 1%) e mínimo 0,725 (par possível: acha ≥ 99% das paráfrases), calibrados numa amostra de parágrafos | Com um corte só, uma paráfrase que o embedding não reconhece vira "diferente" em silêncio (2–6 erros no teste). Calibrar só por pares levava a um corte único: a calibração tem poucos pares na faixa e nenhum em que o corte mínimo evite um erro (sobreajuste) | Corte único 0,85 ou 0,90; cortes escolhidos pelo par |
| **Par semântico não contradiz os valores do caso**: com valores (datas, valores, CPF/CNPJ, números de 3+ dígitos, sem anos) nos dois parágrafos, precisa de um em comum | Os parágrafos de outros fatos da mesma área chegam a 0,9 de cosseno (falso par de 38% no corte mínimo, só pelo cosseno). Qualificação de outras partes e pedido de outro valor pareavam (0,88 e 0,97) e geraram uma "versão" falsa no controle sem fatos no histórico. Com o valor em comum, o falso par cai para ~0,3% | Só cosseno; lista de parágrafos estruturais a ignorar (frágil) |
| **Regra 8 exige tamanho**: trecho só quando o maior tem pelo menos o dobro do texto próprio do menor | Uma versão com 2/3 dos fatos reescritos dava 65% × 43% e saía "trecho" (o percentual baixo vinha de reescrita, não de tamanho). Agora vai para a faixa semântica | — |
| "Trechos reaproveitados" no gerador copiam até metade dos fatos de A | Com 3 de 4 fatos copiados, 66% do texto de A está em B: "versão · outra instância" é defensável e o rótulo "diferente" estava errado | — |

Achados: a premissa do valor em comum não é validada pelos sintéticos (o gerador mantém os valores na paráfrase por construção); vai como limitação. O sinal semântico também decide os pares sem histórico: as independentes com 0–10 casos de histórico passaram de revisão para 20/20 "diferente" (§5.1).

## Guia de defesa

| Pergunta | Resposta curta |
|---|---|
| Por que nenhum limiar produz "cópia"? | Porque "cópia" autoriza tratar dois documentos como um só; esse erro só pode vir de igualdade mal definida, que é testável caso a caso |
| Por que contenção e não Jaccard? | A pergunta é "quanto de A está em B". O Jaccard é simétrico, cai com a diferença de tamanho e não diz o que mudou |
| Por que alinhar a sequência de palavras e não parágrafos? | O parágrafo depende do extrator. Sementes de 5 palavras estendidas ao maior trecho igual não dependem |
| O que é Greedy String Tiling? | Acha os maiores trechos iguais entre dois textos, do maior para o menor, sem sobreposição. É a ideia do algoritmo do JPlag; aqui, numa variante de uma passada. Lida com trechos movidos |
| Por que não MinHash/LSH? | O MinHash estima Jaccard, que cai com a diferença de tamanho; o winnowing estima contenção (petição dentro de autos 10× maiores = 1,0). Na escala de um caso não é preciso índice aproximado. O índice só escolhe candidatos; a posição do trecho vem do alinhamento |
| O que é winnowing? | De cada janela de 4 hashes de shingles consecutivos, guarda o menor; garante uma âncora para todo trecho comum de ≥ 8 palavras |
| E citações entre peças do mesmo caso? | Blocos citados ("in verbis", entre aspas, "nos seguintes termos:") não contam como derivação; a relação "cita" aparece como informação |
| E scans? | O ruído de OCR não vira "valor alterado": o par vai para revisão como "provável cópia (OCR)" |
| Por que agregar a revisão por documento? | 1% por par com 30 comparações vira 26% dos documentos |
| Memoriais que copiam a inicial não viram "versão"? | Viram "versão · outra peça do caso": o texto deriva, mas é outro documento. O tipo de peça (título/qualificação, em produção o metadado do protocolo) separa a nova versão da inicial dos memoriais |
| E um novo scan com o valor diferente? | Número contra número em texto de OCR nunca é ruído: vai para conferência item a item contra o original, nunca em lote |
| Como o sistema sabe o que é texto de modelo? | Aprende no histórico do cliente: o que se repete em 3 ou mais outros casos dele é modelo; o que só aparece neste caso é conteúdo. Não há lista fixa. Cliente novo ou modelo novo: mais revisão até o histórico crescer, nunca "versão" falsa |
| Como o sistema separa duas pessoas de nome parecido? | Pelo CPF/CNPJ da qualificação. O nome só desempata: mesmo CPF com nome digitado errado é a mesma parte; CPF diferente e nome diferente é outra pessoa |
| E se uma página não tiver texto? | O documento é comparado com o resto, a página vira pendência de OCR, e nenhuma "cópia" é afirmada até ela ser lida |
| Qual o maior risco? | A taxa de revisão real é desconhecida: citação, OCR e reescrita em pares reais. Só se mede com rótulos reais. O contencioso de massa (petições quase só de modelo) foi medido: o texto próprio que sobra (nomes, CPF, valores) ainda decide, e a regra 4a cobre o que ficar abaixo de 10 sequências |
| E se o PDF mostrar um número e o texto extraído for outro? | Verificação de fidelidade (texto invisível, coberto, fonte sem mapa) e, com o mesmo layout, raster igual: sem isso, nunca "cópia" |
| O que acontece com decisões antigas quando o índice de modelo muda? | A fila é reavaliada; decisões entregues não são rebaixadas sem alerta |
| Dois uploads simultâneos no mesmo caso? | Fila em série por caso: o segundo vê o primeiro |
| Como vocês sabem o erro do que ninguém revisa? | Auditoria aleatória de 1% das decisões automáticas, às cegas |
| Embeddings não trazem o "tema" de volta? | Só entram parágrafos próprios não alinhados (sem modelo e sem citação), na ordem, e o par não pode contradizer os valores do caso. Sem a regra do valor, qualificação de outra parte e pedido de outro valor pareavam |
| E se o embedding não reconhecer uma paráfrase? | O corte mínimo (acha ≥ 99% das paráfrases) impede "diferente": o par vai para revisão, nunca para "diferente" em silêncio |
