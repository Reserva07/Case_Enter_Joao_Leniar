Premissas:
1- Num mesmo tipo de processo, os argumentos dos juízes se repetem. Não são infinitos.
2- A sentença tem três partes: relatório, fundamentação e dispositivo. Os argumentos do juiz estão na fundamentação. Os juízes marcam a passagem entre as partes com frases fixas ("Fundamento e decido", "Ante o exposto").
3- A plataforma já tem sentenças de cada tipo de processo.
4- O Jev decide: recebe um texto e perguntas fechadas e devolve a probabilidade de cada resposta.

A solução: em vez de um LLM escrever os argumentos, montamos uma lista fechada de tipos de argumento para cada tipo de processo. Essa lista é a taxonomia. O Jev classifica os parágrafos da fundamentação nessa lista.

Montagem da taxonomia:
1- Os parágrafos da fundamentação das sentenças que já estão na plataforma, sem as citações, viram embeddings e são agrupados. Para que o agrupamento siga o argumento do juiz, e não os fatos, nomes, valores, datas e empresas são mascarados antes. Um LLM lê exemplos de cada grupo e escreve o nome e a descrição da categoria.
2- Advogados revisam a categoria dos parágrafos de um lote de sentenças e corrigem a lista. Esse lote é o gabarito de ajuste.
3- Teste: o Jev classifica os parágrafos do gabarito usando as descrições como opções. Quando uma categoria erra muito, os advogados reescrevem a descrição dela.

O tipo de processo vem da classe e do assunto da sentença. Argumentos comuns a qualquer processo (prescrição, competência) ficam numa taxonomia geral. Um tipo com poucas sentenças usa só a geral.

A lista de pedidos de cada tipo é montada do mesmo jeito. Pedido é o que o autor pediu ao juiz, como danos morais ou a exclusão do nome do cadastro.

Extração de uma sentença nova:

Uma sentença nova chega ao sistema e o PDF é lido página a página. Página escaneada vai para OCR.

Depois de lida, o código prepara a sentença em três passos:
1- Divide o texto em parágrafos numerados, cada um com a página e a posição no PDF.
2- Separa relatório, fundamentação e dispositivo pelas frases fixas. Se elas não aparecem, o Jev classifica cada parágrafo como relatório, fundamentação ou dispositivo, e só o que fica abaixo da probabilidade mínima (etapa 4) vai para revisão humana.
3- Marca as citações (ementa, trecho entre aspas). Elas não contam como argumento do juiz, mas as súmulas, artigos e precedentes citados vão para o argumento vizinho.

Etapa 1: o dispositivo é onde o juiz decide cada pedido. Para cada pedido da lista, o Jev responde se o dispositivo o decide e com qual resultado: procedente, parcialmente procedente, improcedente ou extinto sem mérito. Uma pergunta a mais, de sim ou não, verifica se o dispositivo decide algum pedido que não está na lista; se sim, a sentença vai para revisão.

Etapa 2: o Jev lê cada parágrafo da fundamentação junto com o parágrafo anterior e o título da seção (por exemplo, "Dos danos morais"). Na primeira chamada, responde se o parágrafo é argumento do juiz e, para cada categoria, se o parágrafo traz aquele argumento (sim ou não). Assim um parágrafo pode ter mais de um argumento. Se nenhuma categoria passa da probabilidade mínima, o argumento é "outro". Na segunda chamada, para cada argumento achado, responde qual pedido ele sustenta (ou nenhum, se for preliminar), se é razão de decidir ou comentário de passagem e se favorece o autor ou o réu.

Etapa 3: o código junta num só argumento os parágrafos vizinhos com a mesma categoria e o mesmo pedido. O argumento juntado fica com a menor confiança entre eles. Se o lado do argumento não bate com o resultado do pedido (procedente ou improcedente), ele vai para revisão.

Etapa 4: cada pergunta do Jev tem a sua probabilidade mínima (e, se preciso, uma por categoria). A resposta só é aceita sem revisão se passar dela. Os mínimos são ajustados só no gabarito de ajuste e recalculados a cada versão. A meta vem do gabarito de avaliação: a concordância entre dois advogados. Escolhemos os menores valores com que os argumentos publicados ainda alcançam essa meta. O acerto é medido no argumento inteiro, e não em cada resposta. Então:
1- Se as cinco respostas (é argumento, categoria, pedido, papel e lado) passam do mínimo, o argumento é publicado.
2- Se o Jev diz com confiança que o parágrafo não é argumento do juiz, ele é descartado. Uma amostra fixa dos descartados vai para revisão.
3- Uma categoria com poucos exemplos no gabarito vai sempre para revisão, até o gabarito ter exemplos dela.
4- O resto, e todo "outro", vai para revisão humana.

Saída estruturada: cada argumento é salvo assim.

{
  "id": "arg_8f3c", "cliente_id": "cli_77", "caso_id": "caso_903", "documento_id": "doc_5521",
  "hash_documento": "sha256:9c1e...", "juiz": "jui_41", "vara": "1ª Vara do JEC", "data_sentenca": "2024-06-28",
  "tipo_processo": "negativacao_indevida",
  "categoria": "dano_moral_presumido_negativacao",
  "titulo": "Dano moral presumido na negativação indevida",
  "descricao": "A inscrição indevida em cadastro de inadimplentes gera dano moral sem prova do abalo.",
  "pedido": "danos_morais", "resultado_pedido": "procedente",
  "papel": "razao_de_decidir", "favorece": "autor",
  "fundamentos_citados": ["art. 14 do CDC", "art. 43 do CDC"],
  "trechos": [{"paragrafo": 33, "pagina": 7, "char_ini": 18420, "char_fim": 18733,
               "retangulos": [[60.0, 534.3, 507.6, 549.4]], "texto": "A inscrição indevida do nome do consumidor..."}],
  "confianca": {"argumento": 0.99, "categoria": 0.96, "pedido": 0.98, "papel": 0.91, "favorece": 0.97},
  "status": "publicado", "origem": "jev",
  "versoes": {"schema": "1.2", "taxonomia": "neg_v3", "classificador": "jev-2026-09", "limiares": "neg_v3_l2", "ocr": "ocr-2026-08", "codigo": "c41a"}
}

Regra do JSON: a categoria só aceita valores da taxonomia. O pedido vem da lista de pedidos; se o argumento for preliminar, pedido e resultado_pedido ficam null. Papel e favorece vêm de listas fixas. O trecho é o texto do próprio parágrafo, nunca reescrito.

O tipo do argumento é a categoria. Título e descrição vêm da taxonomia e fazem o papel do resumo. O que é específico do caso fica em fundamentos_citados (súmulas, artigos e precedentes do parágrafo e das citações vizinhas), extraídos por regra no código, sem modelo. Os principais argumentos são os de papel "razão de decidir". O hash do documento evita processar a mesma sentença duas vezes.

Argumentos inventados: o LLM só escreve texto na montagem da taxonomia, nos nomes e descrições das categorias. Tudo o que ele escreve é revisado pelos advogados antes de ser usado. Na extração, nenhum modelo escreve texto, então o único risco é classificar errado. Esse risco é reduzido pela regra do JSON, pela probabilidade mínima, pela pergunta "é argumento do juiz?" e pelo "outro".

Se o classificador for um LLM (o plano B dos trade-offs), as mesmas regras valem. Ele responde só com números de parágrafo e opções da lista, em saída restrita, nunca com texto livre. O código descarta número ou opção que não existe e recorta o trecho do próprio documento. Como o LLM não dá uma probabilidade confiável, a confiança vem da concordância entre várias respostas dele à mesma pergunta.

Sentenças longas: a sentença nunca vai inteira ao modelo. Cada chamada leva só um parágrafo, o anterior e o título da seção, então uma sentença longa só gera mais chamadas. Um argumento espalhado em vários parágrafos é remontado na etapa 3.

Revisão humana: o revisor vê o trecho destacado no PDF. Ele aceita, corrige ou rejeita o argumento, ou marca um trecho que faltou. Cada ação é um registro novo, e o original não é apagado. A ação muda o status do argumento (em revisão, publicado, rejeitado ou corrigido) e a origem (jev ou advogado). Quando os "outro" se acumulam, voltam aos passos 1 e 2 da montagem e viram categorias novas, com gabarito próprio.

Qualidade: sorteamos sentenças, e dois advogados marcam os argumentos sem ver a resposta do sistema. Um terceiro desempata. Esse é o gabarito de avaliação. Um argumento do sistema acerta quando tem a mesma categoria e o mesmo pedido de um argumento do gabarito e pelo menos um parágrafo em comum. Nele medimos, todo mês em produção:
1- a precisão e o recall por categoria;
2- se os argumentos publicados acertam tanto quanto os advogados concordam entre si;
3- quanto vai para revisão;
4- os erros na separação de relatório, fundamentação e dispositivo.

Versionamento: cada argumento grava a versão do schema, da taxonomia, do classificador, das probabilidades mínimas, do OCR e do código. As descrições da taxonomia definem as perguntas do Jev e fazem o papel do prompt.
1- Mudança na taxonomia reclassifica só as categorias afetadas.
2- Troca de classificador reclassifica tudo, desde que a versão nova não fique pior no gabarito.
3- Troca do LLM ou do prompt da montagem gera uma versão nova da taxonomia, que passa de novo pelos advogados.
4- Campo novo no schema fica vazio nos registros antigos. Campo que muda de sentido gera migração.
5- Mudança no OCR ou na divisão em parágrafos reprocessa a sentença, porque a posição dos trechos muda.
Nada é apagado. A correção de um advogado prevalece sobre a reclassificação e é levada para a versão nova pelo mapeamento das categorias.

Trade-offs: a lista fechada deixa a base comparável e barata. Em troca:
1- argumento novo fica como "outro" até a revisão;
2- dois fundamentos diferentes na mesma categoria ganham o mesmo resumo e só se distinguem pelo trecho e pelos fundamentos citados;
3- a qualidade depende dos advogados;
4- o Jev está em acesso antecipado, mas o versionamento permite trocá-lo por outro classificador, como um LLM com saída restrita às opções;
5- a sentença vai para um serviço externo, o que exige contrato de tratamento de dados com a TypeSafe, e processos em segredo de justiça não são enviados.
