Considere que a plataforma processa um grande número de documentos jurídicos por dia.
Um cliente possui múltiplos casos jurídicos.
Um caso jurídico contém múltiplos documentos.
Para simplificar, considere que cada caso jurídico está vinculado a exatamente um cliente.
Todo documento está vinculado a exatamente um caso.
Questão 1 — Comparação de Documentos Parecidos

Na Enter, queremos identificar quando dois documentos jurídicos são muito parecidos, mesmo que não sejam idênticos. Por exemplo: duas petições podem ter a mesma tese principal, mas nomes, valores, datas e alguns parágrafos diferentes.

Para cada novo documento inserido na plataforma, queremos calcular sua similaridade com outros documentos do mesmo caso e decidir se ele parece ser uma cópia, uma versão modificada ou um documento diferente.

Desenhe uma solução para calcular e usar essa similaridade entre documentos.  
*
Sua resposta deve cobrir:

Como você representaria cada documento para comparação: texto bruto, trechos, embeddings, hashes, MinHash, ou outra abordagem.
Como diferenciaria documentos quase iguais de documentos que apenas usam vocabulário jurídico parecido.
Como lidaria com documentos longos que não cabem inteiros no contexto de um LLM.
Como avaliaria se a solução está funcionando bem.
O que faria quando um novo documento fosse identificado como provável cópia ou versão de um documento já existente.
Quais trade-offs sua solução faz em termos de custo, latência e precisão.