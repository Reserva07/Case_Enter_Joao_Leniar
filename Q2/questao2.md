# Questão 2: extração de argumentos de sentenças jurídicas

## Resumo

**A ideia central:** um argumento só entra na base se aponta para um trecho da fundamentação que o sustenta, e quem confere isso é o código. O LLM lê a sentença e propõe argumentos. Cada proposta precisa citar parágrafos numerados e copiar o trecho literal. O sistema confere de forma determinística que o trecho existe dentro de um dos parágrafos indicados, sem atravessar a borda entre dois, que está na fundamentação e não no relatório, e que não foi recortado logo depois de um "não". O texto gravado é sempre o da sentença, nunca a cópia feita pelo modelo. Um segundo modelo confere se o trecho, lido no seu parágrafo, sustenta o resumo. O que não passa é descartado e não chega à base.

**Decisões de desenho:**
1. **A sentença é lida pela estrutura do art. 489 do CPC.** O relatório traz os argumentos **das partes**, a fundamentação traz os **do juiz** e o dispositivo traz o que foi decidido. Argumento do juiz só sai da fundamentação. Cada argumento é ligado ao pedido que decide e ao resultado no dispositivo. Esse é o critério de "principal": razão de decidir (*ratio decidendi*) de um pedido, diferente de comentário lateral (*obiter dictum*). Por isso o papel não fica só com o extrator: o código procura o marcador de comentário lateral, o verificador diz se o resultado depende do raciocínio, e a decisão combina os três.
2. **Posição e trecho são dados do sistema, não do modelo.** O texto é dividido em parágrafos numerados com página e offsets antes de chegar ao LLM. O modelo devolve ids de parágrafo e citação, e o código converte isso em posição. Lei, súmula ou precedente que não esteja escrito no trecho é removido do argumento.
3. **A confiança é calculada, não declarada.** A nota que o LLM dá a si mesmo é mal calibrada. A confiança é uma probabilidade estimada a partir dos sinais de verificação e calibrada no conjunto de referência. O sistema decide sozinho: publica, descarta ou, numa faixa estreita de incerteza, manda para revisão.
4. **Extração e decisão são versionadas separadamente.** Cada extração é uma execução imutável. A decisão (calibração e cortes) é uma camada por cima, que pode ser recalculada sem chamar o LLM. A revisão humana é outra camada, guardada como eventos, e sobrevive a uma nova extração.

**Demonstração:** `demonstracao_questao2.ipynb` executa o código da solução (`q2.py`) sobre 300 sentenças sintéticas em PDF, com gabarito, e um LLM simulado que erra de propósito. Cada afirmação deste documento marcada com (caderno §n) tem uma célula com `assert`.

## Fluxo para cada nova sentença

| # | Etapa | Ferramenta | Saída |
|---|---|---|---|
| 1 | Extrair texto | PyMuPDF; OCR (Google Document AI) para páginas sem texto (o mesmo extrator da Q1) | texto por página, `texto_hash` |
| 2 | Numerar parágrafos | código (blocos do PyMuPDF, cabeçalho e rodapé fora, hifenização desfeita) | `§1…§n` com página, `char_ini`, `char_fim`, recuo |
| 3 | Segmentar a estrutura | regex sobre marcadores ("RELATÓRIO", "É o relatório. Decido.", "Dispensado o relatório", "FUNDAMENTAÇÃO", "Ante o exposto", "DISPOSITIVO") e títulos de tópico ("Da preliminar de…", "Dos danos morais"); citações pelo recuo e por marcadores | seção, tópico, `e_citacao` e `adotado` de cada parágrafo |
| 4 | Mapa da sentença | Claude Haiku 5.5, saída estruturada; trechos conferidos por código | partes, pedidos, decisão sobre cada pedido e fatos tidos como provados, todos com trecho conferido; parágrafos de fronteira das seções, comparados com a regex |
| 5 | Extrair argumentos | Claude Sonnet 5.5, ferramenta obrigatória com JSON Schema estrito, fundamentação inteira no prefixo em *prompt cache* | argumentos candidatos por tópico da fundamentação |
| 6 | Verificar | código (casamento do trecho, seção, referências, marcador de alegação) + Claude Haiku 5.5 como verificador | sinais por argumento |
| 7 | Consolidar | código + embeddings (BGE-M3) | sem duplicatas; cobertura dos pedidos conferida |
| 8 | Decidir | regressão logística calibrada; tabela de papel; conclusão pelo dispositivo | argumento publicado, descartado ou em revisão, com papel e conclusão finais |
| 9 | Gravar e indexar | PostgreSQL (referências normalizadas) + pgvector (resumo); agrupamento em teses | busca por tese, norma, precedente, juízo |

O processamento é assíncrono (fila SQS + workers) e idempotente: a chave `(sentenca_id, texto_hash, versao_extracao)` impede execuções duplicadas (caderno §9). O PDF original fica imutável no S3. Os dados de saída ficam em PostgreSQL: tabelas relacionais para o que é filtrado e JSONB para a resposta bruta do modelo.

**Por que Sonnet na extração e Haiku na verificação.** Extrair exige interpretar a fundamentação inteira de um tópico: separar razão de decidir de comentário, ligar ao pedido e resumir sem distorcer. Verificar é uma tarefa curta e fechada (um trecho, um resumo, três perguntas), que um modelo menor faz bem e barato. O verificador também recebe menos contexto que o extrator: o parágrafo do trecho, com o trecho marcado, e o parágrafo anterior, sem a sentença inteira. Assim ele julga o que está escrito, e não o que o resto do texto sugere.

**Custo por sentença**, em tokens (o preço é o vigente de cada modelo na hora de calcular, não fica no código):

| Chamada | Quantas | Tokens de entrada |
|---|---|---|
| Mapa (Haiku) | 1 | a sentença inteira |
| Extração (Sonnet) | 1 por tópico, mais reextrações e extrações dirigidas | o prefixo (pedidos, fatos provados, fundamentação, dispositivo) é escrito no cache uma vez e lido nas outras chamadas; só o tópico é pago a preço cheio |
| Verificação (Haiku) | 1 por argumento | ~450 (dois parágrafos e o resumo) |

Nas sentenças do caderno, 66% dos tokens de entrada do extrator são leitura de cache (caderno §10). A proporção cresce com o número de tópicos.

## 1. Saída estruturada

**Sentença (uma por documento):**

| Campo | Exemplo |
|---|---|
| `processo`, `tribunal`, `orgao`, `juiz`, `data` | `0801234-56.2025.8.26.0100`, TJSP, 3ª Vara Cível |
| `classe`, `assuntos` | tabelas do CNJ (TPU) |
| `pedidos[]` | `{id: "P2", texto: "danos morais de R$ 20.000", §: [4], trecho: "..."}` |
| `decisoes[]` | `{pedido: "P2", resultado: "procedente_em_parte", valor: "R$ 8.000", §: [41], trecho: "..."}` |
| `fatos_provados[]` | `{fato: "o réu não provou a contratação", §: [20], trecho: "..."}` |
| `segredo_de_justica` | `false` |
| `texto_hash`, `paragrafos[]` | base para todos os offsets |

**Argumento (vários por sentença):**

```json
{
  "id": "arg_8f3c",
  "linhagem_id": "lin_21aa",
  "tese_id": "tese_0412",
  "titulo": "Inscrição indevida em cadastro de inadimplentes gera dano moral presumido",
  "resumo": "O juiz entende que a negativação sem débito comprovado gera dano moral in re ipsa, sem necessidade de prova do abalo.",
  "tipo": "merito_direito",
  "papel": "ratio_decidendi",
  "por_que_papel": "Sem o dano presumido não haveria fundamento para condenar: o autor não provou abalo concreto.",
  "pedidos": ["P2"],
  "conclusao": "acolhe",
  "favorece": "autor",
  "fundamentos_normativos": [{"norma": "CDC", "artigo": "14"}],
  "precedentes": [{"tribunal": "STJ", "tipo": "sumula", "numero": "385", "uso": "distingue"}],
  "trechos": [
    {"papel": "principal", "paragrafo": 33, "pagina": 7, "char_ini": 18420, "char_fim": 18733,
     "texto": "A inscrição indevida do nome do consumidor em cadastros de proteção ao crédito configura dano moral in re ipsa...",
     "e_citacao": false, "adotado": false}
  ],
  "secao": "fundamentacao",
  "topico": "Dos danos morais",
  "paragrafos_apoio": [],
  "sinais": {"casamento": "exato", "sustenta": "sim", "postura": "adota", "necessario": true, "papel_extrator": "ratio_decidendi",
             "marcador_obiter": false, "marcador_alegacao": false, "referencias_removidas": []},
  "confianca": 0.96,
  "status": "publicado",
  "extracao_run_id": "run_5d10",
  "versao_decisao": "dec_7637"
}
```

**Tipos (enum fechado, pela função do argumento na decisão):**

| Tipo | O que cobre |
|---|---|
| `preliminar_processual` | competência, ilegitimidade, inépcia, interesse de agir, gratuidade |
| `prejudicial_merito` | prescrição, decadência |
| `merito_fato` | valoração da prova, fatos tidos como provados ou não provados |
| `merito_direito` | interpretação e aplicação da norma ao fato |
| `onus_prova` | distribuição e inversão do ônus |
| `quantificacao` | valor do dano, juros, correção, honorários, multa |
| `outro` | o que não cabe nos tipos acima; vai sempre para revisão |

Norma e precedente não são tipos: são atributos, porque um argumento de mérito pode se apoiar em ambos. `papel` separa `ratio_decidendi` de `obiter_dictum`; só o primeiro conta como argumento principal na busca padrão. O extrator escreve `por_que_papel` (de que o resultado depende) antes de dar o papel, e essa frase aparece para o revisor. `e_citacao` marca o trecho em que o juiz transcreve doutrina, jurisprudência ou a peça de uma parte.

**`e_citacao` e `adotado` são marcados pelo código, não pelo modelo,** na etapa 3 (caderno §1 e §3). Um parágrafo é citação quando: tem recuo maior que o do corpo do texto (posição horizontal dada pelo PyMuPDF); está inteiro entre aspas; vem logo depois de um marcador ("nesse sentido:", "in verbis", "confira-se:", "colaciono:"); ou tem formato de ementa (abre em caixa alta e traz relator, órgão ou data). Ementa transcrita é o erro mais comum nessa tarefa, porque o texto parece raciocínio do juiz: citação nunca é trecho principal. A exceção é a fundamentação *per relationem*: quando o parágrafo anterior diz "adoto como razões de decidir", "faço minhas as razões" ou equivalente, o bloco citado é `adotado` e vale como trecho principal, porque o juiz o tornou seu.

**Posição no documento:** `paragrafo`, `pagina` e offsets sobre o texto normalizado identificado por `texto_hash`. Offsets sem o hash não valem nada: um novo OCR muda todos eles.

**Normalização das referências:** "art. 14 do Código de Defesa do Consumidor", "CDC, art. 14" e "art. 14 da Lei 8.078/90" viram `{norma: "CDC", artigo: "14"}` por um dicionário de leis e regex, não pelo LLM. Precedentes viram `{tribunal, tipo, numero}`. É isso que torna a base consultável ("todos os argumentos que afastam a Súmula 385 do STJ no TJSP").

**Tese (o mesmo argumento em sentenças diferentes):** na etapa 9, cada argumento `ratio_decidendi` entra na tese existente que tenha o mesmo `tipo`, pelo menos uma norma ou precedente em comum e cosseno entre o resumo e o centróide da tese acima de um limiar. O limiar não é chutado: é escolhido em pares de argumentos anotados como "mesma tese" e "tese diferente" no conjunto de referência, para precisão de pares ≥ 90%. Se nenhuma tese atende, o argumento cria uma nova. A tese é o que transforma a lista de argumentos numa base: "como os juízes do TJSP decidem a negativação com inscrição preexistente, e com que resultado".

**Dados pessoais e sigilo.** Sentenças trazem nome, CPF e, às vezes, dados de saúde ou de menores. Título e resumo vão para a base e para o embedding sem nome de parte nem identificador: o código troca os nomes das partes (vindos do mapa) por "a parte autora" e "a parte ré" e mascara CPF, CNPJ e e-mail antes de gravar (caderno §3). Os argumentos ficam na conta do cliente que enviou a sentença. As teses, que agregam argumentos de clientes diferentes, só recebem argumentos de sentenças públicas: sentença com `segredo_de_justica` ou com dado sensível (art. 11 da LGPD) não entra em tese. As chamadas ao modelo usam retenção zero de dados.

## 2. Como reduzir argumentos inventados

O risco tem três formas, e cada uma tem um controle próprio:

| Falha | Exemplo | Controle |
|---|---|---|
| **Inventado** | argumento que não está no texto, ou trecho recortado que inverte o sentido | trecho literal obrigatório, conferido por código, inclusive na borda |
| **Atribuído errado** | argumento do réu apresentado como do juiz | só parágrafos da fundamentação; marcador de alegação; o verificador pergunta "o juiz adota isto?" |
| **Detalhe inventado** | trecho certo, mas com um REsp ou artigo que não existe | toda referência precisa aparecer escrita no parágrafo |

**Na entrada:**
- O texto vai com os parágrafos numerados (`[§33] ...`). O schema obriga cada argumento a ter `paragrafos[]` e `citacao_literal`. Sem trecho, não há argumento.
- A saída é uma ferramenta obrigatória com JSON Schema estrito (decodificação restrita), gerado do modelo Pydantic: enums fechados, nenhum campo fora do schema. Limites de tamanho são conferidos pelo Pydantic na volta (caderno §2).
- O prompt pede só argumentos da fundamentação e aceita lista vazia. Não há meta de quantidade ("extraia 5 argumentos") que force o modelo a completar.
- O texto da sentença vai como dado, delimitado, com a instrução de ignorar qualquer instrução escrita nele.

**Segmentação conferida duas vezes.** Se a fronteira entre relatório e fundamentação sair errada, o sistema publica argumento da parte como se fosse do juiz. Por isso a fronteira é achada de dois jeitos: pela regex da etapa 3 e pelo mapa da sentença (etapa 4), que devolve o parágrafo onde começa a fundamentação e o parágrafo onde começa o dispositivo. Para a regex, o dispositivo é o título DISPOSITIVO ou, sem ele, o **último** "Ante o exposto" com verbo de comando (julgo, condeno, declaro, extingo, homologo). O "Ante o exposto, rejeito a preliminar" que fecha um tópico é comum e, tomado como dispositivo, cortaria todo o mérito. Se os dois coincidem (com tolerância de um parágrafo, o do título), a fronteira vale. Se só um achou, vale o que achou. Se divergem, a sentença vai para revisão como "segmentação incerta" antes da extração, porque todo o resto depende disso (caderno §4). Sentença de Juizado Especial dispensa o relatório (art. 38 da Lei 9.099/95): o marcador "dispensado o relatório" é detectado, e os pedidos passam a vir da fundamentação e do dispositivo. Pedidos, decisões e fatos do mapa também trazem trecho literal, conferido pela mesma regra dos argumentos. O que não tem trecho conferido não entra no mapa.

**Verificação determinística (código, sem LLM; caderno §3):**
1. **O trecho existe:** `citacao_literal` é procurada dentro de cada parágrafo citado, um de cada vez, palavra por palavra (pontuação e aspas não contam). Um trecho nunca atravessa a borda de um parágrafo: o fim do §16 colado ao começo do §20 forma uma frase que o juiz não escreveu. Os outros parágrafos citados ficam como `paragrafos_apoio`. Primeiro por casamento exato. Se falhar, as duas versões são alinhadas palavra a palavra, e só são aceitas trocas de caractere do mapa de confusões de OCR (`rn`↔`m`, `l`↔`1`, `o`↔`0`…). Palavra inserida, removida ou trocada, dígito diferente ou prefixo de negação (não, in-, im-, des-) reprova: "configura" → "não configura" muda poucos caracteres, mas inverte o argumento. Também reprova o trecho que começa logo depois de um "não", "nem" ou "nunca" da fonte: "configura dano moral" copiado de "não configura dano moral" é substring literal e tem o sentido oposto. **O texto gravado e o enviado ao verificador são os da sentença, recortados pelos offsets encontrados, nunca a cópia do modelo.**
2. **Está na seção certa:** parágrafo no relatório ou citação não adotada não pode ser trecho principal.
3. **Referências conferem:** cada norma e precedente do argumento precisa ser encontrado pela regex num parágrafo citado que seja do juiz: fundamentação, fora de citação não adotada. A Súmula que só o réu invoca no relatório não entra no argumento do juiz, mesmo que o modelo cite o parágrafo do relatório. O que não for encontrado é removido do argumento (o argumento continua; a referência inventada sai). As referências escritas no próprio trecho entram mesmo que o modelo não as tenha listado.
4. **Pedido existe:** `pedidos[]` precisa apontar para um pedido do mapa da sentença.
5. **Marcador de alegação:** o código marca o trecho que começa atribuindo a fala a uma parte ("Sustenta o réu que…", "A ré alega…"). É um sinal, não um descarte: o juiz às vezes recita a alegação para rebatê-la no mesmo parágrafo.
6. **Marcador de comentário lateral:** "Registro, apenas para esclarecimento…", "Anoto que…", "ainda que assim não fosse", "a título de argumentação", do início do parágrafo até o fim do trecho. É um dos três sinais do papel.
7. **Conclusão pelo dispositivo:** para uma razão de mérito ligada a pedidos com o mesmo resultado, o dispositivo impõe a conclusão e o lado favorecido (procedente → acolhe, a favor do autor; improcedente → rejeita, a favor do réu). Pedido procedente em parte, preliminar, prejudicial e ônus da prova ficam com o que o extrator disse, porque o dispositivo não decide sozinho.

Uma falha em 1 ou 2 descarta o argumento. Se algum argumento do tópico for descartado, o tópico é reextraído uma vez, com o erro na mensagem; se falhar de novo, o descarte fica registrado e conta como falha na métrica de qualidade.

**Verificação semântica (Claude Haiku 5.5, por argumento):** recebe o parágrafo do trecho, com o trecho marcado, o parágrafo anterior, o resumo e o resultado, no dispositivo, do pedido ligado. O parágrafo inteiro importa porque uma negação ou ressalva fora do trecho ("Não é verdade que…") muda o sentido dele. Responde com saída estruturada, escrevendo a justificativa antes do veredito: (a) o trecho sustenta o resumo? (`sim`/`parcial`/`não`); (b) o juiz adota o raciocínio ou o relata? (c) o resultado do pedido depende deste raciocínio, ou é observação de passagem? (d) o tipo está correto?

**Decisão (o sistema decide; a revisão é a exceção):**
- falhou na verificação determinística, ou verificador = `não`, ou "relata" → **descartado**;
- tipo `outro`, ou marcador de alegação com verificador dizendo "adota" (código e verificador discordam) → **em revisão**;
- confiança ≥ corte de publicação → **publicado**;
- confiança < corte de descarte → **descartado**;
- entre os dois → **em revisão**.

A confiança é a saída de uma regressão logística sobre os sinais (veredito do verificador, casamento exato ou por OCR, referências removidas, tipo contestado, tópico sem título, reextração, citação adotada, fusão de candidatos, marcador de alegação), treinada nas sentenças de calibração do conjunto de referência (seção 5). O rótulo que ela prevê é **correto**: o argumento corresponde a um argumento de referência e o trecho o sustenta.

Os cortes saem das probabilidades fora da amostra (validação cruzada por sentença), nunca das que a própria regressão ajustou:
- **Publicação:** o menor corte em que a precisão esperada dos publicados (a média das probabilidades calibradas) é ≥ 95%, sem publicar nenhum argumento com probabilidade abaixo de 0,80. Procurar o corte direto nos rótulos o faz saltar entre rodadas, porque cada combinação de sinais entra ou sai inteira. E só a precisão acumulada deixaria publicar uma faixa ruim, que passa por estar misturada à massa de alta confiança.
- **Descarte:** o maior corte em que os argumentos corretos esperados abaixo dele são no máximo 2% do total.

**Papel e conclusão finais.** O papel sai de uma tabela com as oito combinações de três sinais (marcador de comentário lateral, papel dado pelo extrator, "necessário?" do verificador), cada uma levada ao papel que os anotadores deram à maioria dos argumentos dela nas sentenças de calibração. Quem vence quando extrator e verificador discordam sai dos dados, não de uma regra escolhida à mão. Combinação com menos de 5 exemplos: o marcador decide; sem ele, obiter só se extrator e verificador concordarem. Depois do papel, uma razão de mérito recebe a conclusão que o dispositivo impõe (verificação 7). Os dois ficam na camada de decisão, junto com a regressão: saem dos sinais gravados e são recalculados sem chamar o LLM. O sistema regrava o rótulo; nada disso vai para a fila.

No caderno, os cortes saíram 0,85 e 0,75, com precisão de 97% nos publicados das sentenças de teste (97% também na busca padrão, só *ratio*), papel certo em 100% dos publicados casados e erro de calibração de 0,02 (caderno §6).

**Cobertura (contra o erro oposto, o argumento esquecido):** cada decisão do dispositivo precisa ter pelo menos um argumento `ratio_decidendi` ligado ao seu pedido. Um pedido decidido sem argumento dispara uma extração dirigida ("quais fundamentos o juiz usa para decidir P3?") em cada tópico da fundamentação; o prefixo já está em cache, então isso custa pouco. Se continuar sem argumento, a sentença vai para revisão marcada como "pedido sem fundamento extraído".

## 3. Sentenças longas

A maioria das sentenças tem de 5 a 30 páginas e cabe no contexto do modelo. Mesmo assim, a extração não pede todos os argumentos numa chamada só. A unidade de trabalho é o **tópico da fundamentação**, por dois motivos: uma chamada com uma tarefa estreita ("os argumentos do tópico Dos danos morais") deixa menos argumento para trás do que "todos os argumentos da sentença", e uma falha na verificação reextrai só o tópico, não a sentença.

1. **Corte do relatório.** O relatório costuma ser de 20% a 40% do texto e não tem argumento do juiz. Ele não entra na extração; entra só a lista de pedidos do mapa da sentença.
2. **Divisão por tópico.** A fundamentação é dividida pelos títulos do próprio juiz ("Da prescrição", "Do mérito", "Dos danos morais"). Sem títulos, ou com um tópico grande demais, a divisão é por blocos de até ~8 mil tokens, cortados só entre parágrafos. Não há sobreposição entre blocos: o contexto global já vai em cada chamada (caderno §5).
3. **Contexto global em cada chamada.** Cada chamada recebe os pedidos, os fatos tidos como provados, a fundamentação inteira e o dispositivo, e a instrução de extrair só do tópico X. Isso importa porque o juiz fixa um fato num tópico ("restou provado que não havia débito") e o usa em outro ("Dos danos morais"). Esse prefixo é igual para todos os tópicos da sentença e fica em *prompt cache*, então só a instrução do tópico é paga a preço cheio. Quando a fundamentação passa de ~150 mil tokens, o prefixo troca a fundamentação pelo título e pelo primeiro e último parágrafo de cada tópico, mas mantém os fatos provados inteiros. É por eles que um tópico continua enxergando o fato que outro fixou.
4. **Ids globais.** Os parágrafos mantêm a numeração da sentença inteira, então as posições não precisam ser remapeadas.
5. **Consolidação.** O mesmo argumento pode sair duas vezes: em dois tópicos, ou citado por duas frases diferentes do mesmo parágrafo. Dois candidatos são o mesmo argumento quando os trechos se sobrepõem (IoU dos caracteres ≥ 0,5); quando citam o mesmo parágrafo principal, com o mesmo tipo, um pedido em comum e resumos com cosseno ≥ 0,80; ou quando estão em parágrafos diferentes com o mesmo pedido, o mesmo tipo e resumos com cosseno ≥ 0,85 (BGE-M3). O mesmo parágrafo sozinho não basta: um parágrafo pode trazer duas razões para o mesmo pedido ("o dano é presumido" e "a Súmula 385 não incide porque as inscrições anteriores foram canceladas"), e fundi-las apagaria uma (caderno §5). Os limiares são escolhidos nos pares anotados, como o da tese. A fusão junta os trechos e mantém o resumo do candidato que o verificador melhor avaliou.

Sentenças muito longas (ação civil pública ou recuperação judicial, com centenas de páginas) seguem o mesmo caminho: só aumenta o número de tópicos. Como o prefixo fica em cache, o custo cresce quase linear com a fundamentação, não com o documento.

## 4. Revisão humana

**Tela de revisão na própria plataforma**, porque quem revisa são advogados que já trabalham nela. É uma tela de duas colunas: à esquerda a sentença, com os trechos de cada argumento destacados e as seções (relatório, fundamentação, dispositivo) marcadas; à direita os cartões dos argumentos, agrupados por pedido. Clicar num cartão rola o texto até o trecho.

| Ação | Como funciona |
|---|---|
| **Aceitar** | um clique; muda o status para `aprovado` |
| **Editar** | campos editáveis (título, resumo, tipo, papel, pedido, referências). O trecho é trocado selecionando texto na sentença, então continua sendo um trecho real, com offsets do sistema. A edição passa pela mesma checagem de referências: norma ou precedente que não está escrito no parágrafo gera um aviso na tela (não bloqueia, porque o revisor pode saber o que o texto não diz) |
| **Rejeitar** | motivo obrigatório: `nao_esta_no_texto`, `argumento_da_parte`, `obiter_nao_principal`, `duplicado`, `resumo_distorce`, `irrelevante` |
| **Adicionar** | o revisor seleciona um trecho e preenche o cartão; nasce com `origem = humano` |
| **Juntar / dividir** | une dois cartões ou separa um em dois |

**Quem chega na fila:** os argumentos na faixa entre os dois cortes, os casos em que código e verificador discordam, os de tipo `outro`, e as sentenças com segmentação incerta ou pedido sem argumento. A fila é **por sentença**, não por argumento: o revisor abre a sentença uma vez e vê os itens incertos destacados, com os publicados logo ao lado como contexto.

**Modelo de dados da revisão** (caderno §9):
- `argumento` (o que o modelo extraiu) é imutável;
- `revisao` é uma tabela de eventos, só com inserções: `{argumento_id, linhagem_id, revisor, acao, campos_antes, campos_depois, motivo, ts}`;
- a base consulta a visão `argumento_atual`, que aplica a última revisão sobre a extração. A decisão do modelo nunca é apagada: ela e a correção juntas são o rótulo usado na avaliação;
- dois revisores na mesma sentença não sobrescrevem um ao outro: cada revisão informa quantos eventos a linhagem tinha quando a tela abriu, e é recusada se outro evento entrou nesse meio-tempo.

## 5. Qualidade da extração

**Conjunto de referência:** 300 sentenças estratificadas por área (cível, consumidor, trabalhista, tributário), tribunal, tamanho e resultado. Dois advogados anotam cada sentença às cegas, sem ver a saída do sistema, e um terceiro resolve as divergências. Cada anotador marca todos os argumentos do juiz, *ratio* e *obiter*, com trecho, pedido, tipo, papel e conclusão; e, entre argumentos de sentenças diferentes, quais são a mesma tese. A concordância entre os dois anotadores é medida: é o teto realista do sistema.

O conjunto é dividido em **100 sentenças de calibração e 200 de teste**. Nas de calibração se ajusta o prompt, a regressão e os cortes. As de teste só medem e decidem a troca de versão (seção 6). O teste é maior porque é ele que precisa de poder estatístico.

**Casamento entre extraído e referência:** um argumento extraído corresponde a um de referência quando pelo menos metade do trecho menor está dentro do outro e eles têm um pedido em comum. Contenção, e não IoU, porque o anotador costuma marcar o parágrafo inteiro e o modelo cita uma ou duas frases dele: o IoU daria a uma citação correta um valor baixo. O casamento é um-para-um, pelo algoritmo húngaro.

| Métrica | O que mede | Meta |
|---|---|---|
| **Taxa de inventados** | publicados sem trecho que os sustente ou atribuídos ao juiz quando são de uma parte | ≤ 1% |
| **Precisão** | publicados corretos (correspondem a um argumento de referência, *ratio* ou *obiter*, e o trecho o sustenta) | ≥ 95% |
| **Precisão da busca padrão** | publicados como `ratio_decidendi` que são corretos e *ratio* na referência: o que o usuário vê quando pede os argumentos principais | ≥ 95% |
| **Recall** | argumentos `ratio_decidendi` de referência que foram publicados | ≥ 85% |
| **Acerto por campo** | tipo, papel, pedido, conclusão; normas e precedentes (precisão e recall exatos após normalização) | por campo |
| **Fidelidade do resumo** | nota de 1 a 5 por advogado numa amostra; um juiz LLM com rubrica só é usado depois de concordar com essa nota | ≥ 4 |
| **Cobertura dos pedidos** | decisões do dispositivo com pelo menos um argumento | ≥ 98% |
| **Calibração** | curva de confiabilidade da confiança | erro de calibração ≤ 0,05 |
| **Teses** | precisão dos pares de argumentos postos na mesma tese | ≥ 90% |
| **Fila** | sentenças com algum item em revisão | menor possível, dada a precisão |

"Inventado" e "irrelevante" são contados separados. O primeiro corrompe a base; o segundo é ruído que um filtro por `papel` resolve.

**Acompanhamento contínuo:**
- **Amostra aleatória de 2% dos publicados** vai para revisão às cegas (o revisor não vê a confiança). Só essa amostra estima a precisão real sem viés; a fila de incertos, por construção, não serve para isso.
- Taxa de rejeição por motivo e de edição por campo, segmentadas por tribunal, área e tamanho. Uma alta em `argumento_da_parte` num tribunal aponta para uma segmentação que falhou com o formato dele.
- A confiança é recalibrada só com rótulos sem viés: o conjunto de referência e a amostra aleatória de 2%. Os rótulos da fila de incertos não entram na calibração, porque só contêm casos difíceis. Eles servem para a análise de erro e como exemplos no prompt.

## 6. Versionamento

**Cada execução grava a versão completa do que a produziu:**

| Componente | Como é versionado |
|---|---|
| Prompt (mapa, extrator, verificador) | arquivos no git; versão = hash do conteúdo junto com o schema |
| Modelo | id fixo do modelo (`claude-sonnet-5-5`), nunca um alias que muda sozinho |
| Schema | semver (`2.1.0`), com o JSON Schema guardado no repositório |
| Código | hash do código de segmentação, verificação, normalização de referências e consolidação |
| Embeddings | modelo e versão do BGE-M3 |
| Decisão | pesos da regressão e cortes; versão própria (`versao_decisao`) |

`versao_extracao` é o hash dos cinco primeiros, os que mudam a saída do LLM ou a verificação. A calibração fica fora de propósito: os sinais de verificação ficam gravados com cada argumento, então recalibrar reaplica a decisão sobre eles, sem chamar o LLM e sem mudar a chave de idempotência (caderno §8). A tabela `extracao_run` guarda a versão, a resposta bruta do modelo, os tokens e o custo. Os argumentos pertencem a uma execução e nunca são sobrescritos. Cada sentença tem um ponteiro `run_ativo`, e a base consulta só ele.

**Quando algo muda** (caderno §7):
1. **Calibração própria.** Um prompt ou modelo novo muda a distribuição dos sinais. A candidata roda nas 100 sentenças de calibração, ajusta a própria regressão e os próprios cortes e só então é comparada.
2. **Avaliação antes de trocar.** A candidata e a ativa rodam nas 200 sentenças de teste. A diferença é medida por *bootstrap* pareado por sentença (as mesmas sentenças reamostradas para as duas versões), como teste de não inferioridade. A candidata só vira ativa se o limite inferior do intervalo de 95% da diferença de F1 for ≥ −3 pontos e o limite superior do intervalo da diferença de inventados for ≤ +2 pontos. As margens são do tamanho que 200 sentenças conseguem distinguir. Para conferir isso, a própria versão ativa é rodada de novo (teste A/A) e precisa passar no gate. Com margens de 1 ponto, ela mesma seria reprovada: o extrator não é determinístico e o intervalo de F1 tem ±3 pontos. Os números das duas versões ficam gravados lado a lado.
3. **Reprocessamento.** As sentenças são reextraídas com a nova versão pela Batch API (assíncrona e mais barata), e o ponteiro `run_ativo` é trocado sentença por sentença. A execução antiga continua consultável, então dá para comparar as duas e voltar.
4. **Mudança de schema.** Campo opcional novo (versão *minor*): as execuções antigas ficam com o campo nulo e só são reextraídas se a consulta precisar dele. Mudança que quebra o schema (*major*), como dividir um tipo em dois: um script de migração converte o que é dedutível e reextrai o resto. A versão do schema vai em cada linha, então a leitura nunca mistura formatos sem saber.
5. **A sentença muda.** Embargos de declaração com efeito modificativo alteram a sentença. A decisão dos embargos entra como documento vinculado, o texto integrado ganha um novo `texto_hash`, e a extração roda de novo sobre ele. A linhagem liga os argumentos que continuam iguais.

**O trabalho humano sobrevive à reextração.** `linhagem_id` liga o mesmo argumento entre execuções, pela mesma regra de "mesmo argumento" da consolidação (seção 3, item 5), um para um (algoritmo húngaro). Sem isso, dois argumentos novos podiam herdar a mesma linhagem, e a rejeição de um suprimiria o outro (caderno §9).
- Linhagem **aprovada ou editada** por humano: a versão humana continua valendo. Se a nova extração discordar dela em tipo, papel, pedido ou conclusão, a diferença é registrada como possível regressão.
- Linhagem **rejeitada** por `nao_esta_no_texto`, `argumento_da_parte`, `duplicado` ou `irrelevante`: o argumento equivalente da nova extração é suprimido, porque o problema está no trecho, e o trecho é o mesmo.
- Linhagem **rejeitada** por `resumo_distorce` ou `obiter_nao_principal`: o argumento equivalente volta para revisão, com a rejeição anterior ao lado, porque a nova extração pode ter corrigido o resumo ou o papel.
- Argumento **adicionado** por humano: é mantido, porque não depende de execução.

Assim, trocar o prompt, o modelo ou o schema não apaga revisões já feitas, e cada argumento da base pode ser rastreado até a sentença, o trecho, a execução e a pessoa que o confirmou.
