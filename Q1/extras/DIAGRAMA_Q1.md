# Instrução — diagrama de design da Questão 1

Roteiro do diagrama. O PDF é gerado por `gerar_anexo.py` (cortes lidos de `LIMIARES`). A fonte é `questao1.md`: se algo mudar lá (cortes, regras, nomes de classes), atualize este roteiro antes de desenhar.

## Objetivo

Um avaliador entende a solução em ~1 minuto, sem ler o texto: **o que acontece com um documento novo, como a classe é decidida e o que o sistema faz com ela.** O diagrama mostra a solução, não o processo de chegar nela.

## Formato

- Uma página, paisagem, três painéis lidos da esquerda para a direita: **A. Fluxo**, **B. Decisão**, **C. Ação**.
- Exportar em PDF/PNG, legível impresso em A4 (texto ≥ 9 pt).
- Ferramenta livre (Excalidraw, draw.io, Figma, Mermaid). Rótulos em português, curtos (≤ 6 palavras por caixa).

## Painel A — Fluxo de um documento novo

Caixas em sequência, com setas:

1. **Extrair e normalizar** — texto por página; cabeçalho, imagens e assinatura à parte. Saída lateral: *página sem texto → pendência de OCR*.
2. **Indexar** — hashes (bytes, texto, texto normalizado), fluxo de palavras com página, shingles de 5 palavras, citações, partes/processo/tipo de peça.
3. **Buscar candidatos no caso** — hashes para cópia; todos os docs do caso (até ~2 milhões de palavras) ou índice de âncoras (casos maiores).
4. **Comparar** — alinhamento (sementes + Greedy String Tiling) → **dois percentuais** + diff + identidade.
5. **Decidir** → seta para o Painel B.

Dois repositórios desenhados como cilindros, ligados à etapa 4:
- **Histórico do cliente** — shingles que aparecem em ≥ 3 outros casos = *texto de modelo* (não conta).
- **Documentos do caso** — índices do caso; a comparação nunca sai do caso.

Uma faixa abaixo do fluxo: *assíncrono · idempotente (`upload_id`) · par único por versão do pipeline*.

## Painel B — Decisão

Duas partes, de cima para baixo:

**B1. Portão de igualdade (antes de qualquer percentual).** Losangos em ordem:
bytes iguais → **cópia exata** · extração incompleta → **em revisão** · texto e cabeçalho iguais → **cópia exata** · igual após normalização / assinatura ou imagem diferente → **cópia com ressalva** · OCR com confusão de letras → **em revisão (provável cópia)**.
Selo ao lado: **"Cópia só sai por igualdade. Nenhum limiar produz cópia."**

**B2. Mapa dos dois percentuais** (é a figura central do diagrama). Gráfico quadrado:
- eixo x: **% de A encontrado em B**; eixo y: **% de B encontrado em A** (0–100%).
- Regiões:
  - os dois < 20% → **diferente** (canto inferior esquerdo);
  - maior ≥ 60% e menor ≥ 50% → **versão** (canto superior direito);
  - maior ≥ 60% e menor < 50% → **trecho** (faixas junto aos eixos, nos extremos), com a nota *só se contíguo*;
  - o resto → **em revisão**.
- Marcar três pontos de exemplo: enunciado (84%, 84%) em *versão*; petição dentro de autos 4× maiores (100%, 25%) em *trecho*; petições independentes do mesmo modelo (0%, 0%) em *diferente*.
- Legenda curta: *texto próprio = sem texto de modelo e sem citações*.

**B3. Atributo de versão** (três chips saindo de "versão"): tipo de peça diferente → *outra peça do caso*; partes ou processo diferentes → *outra instância do modelo*; senão → *mesma peça*.

## Painel C — Ação por resultado

Tabela ou coluna de cartões, um por resultado:

| Resultado | Ação (rótulo curto) |
|---|---|
| Cópia | agrupa · avisa "já existe" · reaproveita análises |
| Versão · mesma peça | liga ao anterior · diff com página · alerta valor/data/CPF |
| Versão · outra peça / outra instância | vínculo · **não substitui** |
| Trecho | "contém, págs. x–y" |
| Diferente | vínculo "cita", se houver |
| Em revisão | **1 item de fila por documento** → decisão do revisor vira rótulo |

Seta de retorno de "Em revisão" até os cortes do Painel B: *rótulos calibram os limiares*.

## Elementos laterais

- **LLM**: caixa pequena, tracejada, ligada só ao diff → revisor. Rótulo: *resume trechos alterados (~1.100 tokens) · pseudonimizado · nunca decide a classe*.
- **Cache por parágrafo**: ligado à análise de nova versão. Rótulo: *nova versão paga só o que mudou*.

## Cores e legenda

- Uma cor por classe, usada igual nos painéis B e C: cópia, versão, trecho, diferente, em revisão (em revisão em cor neutra/âmbar).
- Fluxo em cinza; componentes opcionais (LLM) tracejados.
- Legenda única no canto inferior.

## O que não entra

- Jaccard, MinHash ou cosseno do documento inteiro como medida (nem como contraste). Embedding só como o sinal da faixa de 20–60% (pares de parágrafos).
- Números da avaliação sintética, histórico de rodadas, versões antigas (`_v1`, `_v2`).
- Detalhes de implementação (PyMuPDF, nomes de funções) e a lista de limitações.

## Checklist antes de entregar

- [ ] Os cortes (3 casos, 20%, 50%, 60%) batem com `questao1.md`.
- [ ] "Cópia" só aparece saindo do portão de igualdade, nunca do mapa de percentuais.
- [ ] As três classes do enunciado aparecem com esse nome; "em revisão" aparece como estado temporário.
- [ ] Dá para seguir um documento do upload até a ação sem ler texto fora das caixas.
- [ ] Legível em preto e branco (classes diferenciadas também por rótulo, não só por cor).
