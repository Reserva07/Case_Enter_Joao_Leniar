# Questão 1: comparação de documentos parecidos

## Arquivos

- **`anexo_visual_questao1.pdf`**: o fluxo da solução numa página. Mostra o caminho de um documento novo, da leitura do PDF até o registro no caso, e um gráfico com os dois percentuais que mostra onde cai cada tipo de par (versão, um documento dentro do outro, etapa 2 e diferente).
- **`demonstracao_questao1.ipynb`**: o caderno com o código da solução e a prova de cada número do texto. A seção "Código", no início, tem três células:
  - **Solução:** a comparação e a decisão;
  - **Dados sintéticos:** o gerador de documentos de teste;
  - **Avaliação:** métricas, custo e latência.

  As seções seguintes rodam as demonstrações e conferem cada afirmação com `assert`. Cada seção citada no texto tem uma nota "Números do `questao1.md`", que aponta de onde sai o número. As saídas estão salvas, então dá para ler o caderno sem rodar.
- **`sentencas_tjsp.json`**: 226 sentenças públicas de Juizado Especial Cível do TJSP (1º semestre de 2024), de duas magistradas, com as partes pseudonimizadas. É o teste com texto real (seções 10.6 e 10.7).
- **`parafrases_reais_q1.json`**: paráfrases de parágrafos dessas sentenças, escritas uma vez por um LLM. Servem para conferir os cortes de cosseno em texto real (seção 10.1).

## Como rodar o caderno

1. Python 3.14 com `pymupdf`, `numpy`, `matplotlib`, `sentence-transformers` e `torch`.
2. Os dois arquivos `.json` na mesma pasta do caderno.
3. *Restart & Run All*. Leva cerca de 6 minutos. Na primeira execução, o caderno baixa o modelo de embedding (`paraphrase-multilingual-mpnet-base-v2`, cerca de 1 GB).

O tempo vem da demonstração, não da solução. O caderno gera cerca de 1.200 pares de documentos sintéticos, PDFs e documentos de 286 páginas, roda o embedding na CPU e simula custo e latência. A comparação em si leva cerca de 0,5 s por documento (seções 6 e 11).

O caderno não chama nenhum LLM. O juiz LLM é testado só na montagem da pergunta e na regra que aceita as respostas (seção 4.3).
