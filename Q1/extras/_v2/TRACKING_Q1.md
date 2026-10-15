# Tracking de correção — Questão 1

**Meta:** fechar a Q1 hoje (13/10/2026) e liberar os próximos dias para a Q2.
**Regra de ouro:** o notebook é a **fonte única dos números**. O texto só cita o que o notebook imprime (checado automaticamente: 21/21 números conferidos).

Legenda: ✅ feito · ⏭️ adiado (com motivo)

---

## Status por problema

| ID | Problema | Status | Onde ficou a correção |
|---|---|---|---|
| G1 | Petição curta com 1 valor trocado e A+anexo → `revisão` | ✅ | Regra nova por **cobertura de massa de texto** em parágrafos alinhados (§3, §4). Casos "(v1)" na tabela de borda |
| G2 | NFD, hifenização, nº de página, reordenação | ✅ | Normalização de lista branca (§1) + alinhamento 1:1 sem ordem (§3) |
| G3 | Filtro IDF nunca exercitado | ✅ | Coleção de referência de 400 docs; demonstração com e sem filtro (0% × 35%) (§2, §5) |
| G4 | Avaliação circular / sem holdout | ✅ | Gerador com seed; calibração (300) e teste (800) gerados depois dos limiares; "revisão" tratada como abstenção (§11) |
| G5 | Texto × PDF × notebook inconsistentes | ✅ texto/notebook · ⏭️ PDF | PDF será refeito à mão (ver "Números para o PDF" abaixo) |
| M1 | Números mágicos sem porquê | ✅ | `Limiares` com uma intuição por linha (§0); texto explica cada regra |
| M2 | "O que fazer depois" fraco | ✅ | §8/§10 + texto §5: avisos, reaproveitamento, alerta crítico, grupos não transitivos, direção, rótulos, reprocessamento |
| M3 | Custo sem R$; escala 1k | ✅ | §12: medição + extrapolação 1k/10k/100k em R$ |
| M4 | Sem monitoramento | ✅ | Texto §4: shadow mode, correção do revisor por classe, kappa, fila, "padrão desconhecido" |
| M5 | "Diff bruto" minúsculo | ✅ | Diff preserva a caixa original; decisão pela chave cosmética |
| M6 | Referências por célula | ✅ | Referências por "§n" (seções numeradas) |
| M7 | Resumo denso | ✅ | Resumo abre com a decisão de design |
| C1–C4 | Qualidade de código | ✅ | Dataclasses `Evidencia`/`Decisao`/`Limiares`, nomes em PT, índice calculado uma vez |
| C5 | Reprodutibilidade | ✅ | `requirements.txt`; Restart & Run All limpo (~22 s, 0 erros) |

## Achado durante a correção

A primeira execução da §11 encontrou 6 "versão → cópia". A causa estava no **gerador** de pares, não no sistema: uma negação caía em parágrafo sem verbo, e a hifenização cortava fora de uma palavra. Corrigido, com `assert B != A`. Isso está registrado no notebook e no texto como evidência de que a avaliação funciona.

## Pendências (fora do escopo de hoje)

- ⏭️ PDF anexo: refazer à mão com os números abaixo.
- Entrega: **não** enviar `.venv/`, `_v1/`, `Parte1–6.md` nem este arquivo. Enviar `questao1.md`, `demonstracao_questao1.ipynb` e `requirements.txt` (e o PDF, quando estiver pronto).

## Números para o PDF (copiar exatamente; atualizados na rodada 5)

- **Similaridade:** cobertura = fração do conteúdo específico (sem texto padrão) de um documento que reaparece, parágrafo a parágrafo, no outro; calculada nos dois sentidos
- **Fluxo por documento novo:** extrair → indexar → candidatos no caso (índices exatos + força bruta ou índice de âncoras) → evidência + regras → ação
- **Taxonomia:** cópia (exata / com ressalva) · versão (mesma peça / outra instância do modelo) · diferente; relação documento / trecho; "em revisão" é temporário
- **Regras (em ordem):** cópia só por igualdade; versão = ≥60% do menor e ≥50% do maior; trecho = ≥60% do menor, <50% do maior, contíguo; diferente <20%; o resto vai para revisão
- **Exemplo trabalhado:** Maria → Marina, R$ 12.500 → 18.900, 10/04 → 22/05/2024: cobertura 84%/84% → versão · outra instância do modelo (Jaccard 0,49 só como contraste)
- **Teste (800 pares):** versão→cópia 0/407 (≤0,73% a 95%); precisão 100% nas 4 classes; recall 77–100%; abstenção 10,1%; baseline: 182 versões→cópia, 47 diferentes→versão
- **Longos:** 286 páginas em ~0,2 s sem LLM; payload ~830 tokens (pseudonimizado) vs ~113 mil
- **Candidatos:** índices exatos + índice de âncoras (contenção ≥ 10%): 2.364 de 44.850 pares comparados, recall 100%; petição dentro de autos: Jaccard 0,07 × contenção 1,0
- **Custo (1k docs/dia):** revisão de 4,9 h (0,2% por par) a 25 h (1,2%); com classificador: 1,1–4,6 h a 5,9–23,8 h; LLM R$ 2–11; CPU centavos
- **Incremental:** 99,7% dos tokens de análise poupados (286 páginas, 5 parágrafos alterados)
- **Latência:** mediana ~0,2 s sem OCR; p95 ~20 s com OCR

---

## Rodada 2 — segunda revisão (13/10)

Seis dos 12 casos adversariais novos rodados contra o código da rodada 1 expuseram falhas reais.

| ID | Problema | Sev. | Status | Correção |
|---|---|---|---|---|
| R1 | Falso "cópia": cabeçalho com outro nº de processo some (dígitos mascarados); imagem de assinatura/carimbo ignorada | 🔴 | ✅ | Cabeçalho fora do corpo mas dentro da igualdade (vira campo); imagens e assinatura entram na condição de cópia; ausência de cabeçalho num lado é só observação (§8.3) |
| R2 | Custo usa "5% dos documentos", mas o sistema abstém por par (30 comparações → 1% por par vira 26% dos docs) | 🔴 | ✅ | Fila agregada por documento (§8); §11.1 por par × por documento (0,029% → 4,3%); custo por cenários 0,2/0,5/1,2% por par (§12) |
| R3 | Re-segmentação de parágrafos + 1 troca → revisão (43%) | 🟠 | ✅ | Grupos 1:1/1:N pelos componentes do grafo de âncoras; 2 casos ★ novos na §4.2 |
| R4 | LSH não acha cópia de documento só de texto padrão | 🟠 | ✅ | Índices exatos (arquivo, texto, chave) antes do LSH; demo com procuração-modelo (§9) |
| R5 | Ingestão quebra: PDF vazio, `.txt` Latin-1; PDF truncado passa sem alerta | 🟠 | ✅ | `Extracao` defensiva: vazio, corrompido, senha e reparado → pendência; `.txt` não UTF-8 convertido e registrado (§8.3) |
| R6 | Coleção de referência × isolamento por cliente | 🟠 | ✅ | Texto §1: origem da coleção, só contagens de hashes, mínimo de clientes distintos, camada por cliente |
| R7 | Texto e notebook citam a "v1" que o avaliador não viu | 🟠 | ✅ | Marcação ★ e "uma regra mais simples falharia"; nenhuma menção à v1 |
| R8 | CPF/CNPJ vão ao LLM sem mascaramento | 🟡 | ✅ | Pseudônimos estáveis (`CPF_1`→`CPF_2`) no payload + `assert` (§7) |
| R9 | Ajuste do cenário "reescrita extensa" não declarado | 🟡 | ✅ | Declarado na §4.2; fronteira impressa (metade reescrita → versão, 60%) |
| R10 | Código morto, parâmetro `campos` sem uso, e5 recarrega o modelo, variáveis sombreadas, gênero fixo no gerador, versão do Python | 🟡 | ✅ | `n_informativos` removido; `campos` sem uso removido; e5 com cache; variáveis renomeadas; gerador neutro; Python 3.14 e `jupyter==1.1.1` fixados |

---

## Rodada 3 — melhorias de desenho (13/10)

Objetivo: manter a invariante "cópia só por igualdade" e atacar o custo dominante (revisão humana) e a utilidade para o advogado.

| ID | Melhoria | Status | Onde |
|---|---|---|---|
| D1 | Subtipo de versão: "mesma peça" × "outra instância do modelo" (partes, nomes trocados, nº do processo) | ✅ | Partes da qualificação + troca de nome próprio no diff + nº do processo; exemplo trabalhado agora é "versão · outra instância do modelo"; 374/374 subtipos corretos |
| D2 | Relação por trecho: "B contém A nas páginas x–y" em vez de revisão para documento embutido | ✅ | Regra 7: igualdade aplicada ao trecho contíguo (janela de 90% dos grupos); 59/59 relações "trecho" corretas; abstenção 15,6% → 10,1% |
| D3 | Classificador calibrado na faixa ambígua + abstenção com risco controlado (nunca produz cópia) | ✅ | §11.3: logística + Learn-then-Test sobre o risco da faixa (α = 2%): corta 77% das revisões com rótulos limpos, 6% com 5% de rótulos trocados; nunca produz cópia |
| D4 | Processamento incremental: cache de análise por parágrafo, reaproveitado em versões | ✅ | §10.2: cache por (versão do pipeline, hash do parágrafo): 99,7% dos tokens poupados numa nova versão de 286 páginas |
| D5 | Documentos escaneados: hash perceptual por página (sem OCR) → "provável cópia" para confirmação rápida | ✅ | §8.4: aHash por página. Anexos: 0,03 × 0,44 (separa bem); petições do mesmo modelo: 0,06 × 0,11 (separa mal → OCR). Não vê troca de número → "provável cópia por imagem", nunca "cópia" |
| D6 | Tipo de documento define a política (limiares, se "versão" se aplica, qual hash usar) | ✅ | Texto §1: tipo de documento escolhe caminho e limiares |
| D7 | Taxonomia pública: 3 classes do enunciado + "em revisão", com atributos (exata/ressalva, mesma peça/outra instância, documento/trecho) | ✅ | `rotulo_publico` (§4) usado na tabela de borda, nos alertas e no texto |
| D8 | Extensão: mesma máquina entre casos do mesmo cliente (demandas repetidas, litispendência) | ✅ | Texto §7 (Evolução, fase 3), com a ressalva de isolamento por cliente |

---

## Rodada 4 — revisão do desenho novo (13/10)

| ID | Problema | Sev. | Status | Correção |
|---|---|---|---|---|
| E1 | Subtipo só funciona no formato do gerador: qualificação realista (caixa alta, ", brasileira, …") não extrai partes; testemunha trocada e precedente citado viram "outra instância" | 🔴 | ✅ | Partes só do parágrafo de qualificação (caixa alta e ", brasileira, …" ok); processo só de cabeçalho/preâmbulo; no trecho, a identidade vem do trecho; cadastro do caso confere partes e processo (§10.3); 5 testes negativos/positivos novos (34/34) |
| E2 | Autos que contêm a petição → "este documento já existe" e reaproveitamento da análise inteira | 🔴 | ✅ | Coluna `relacao` nos pares; trecho vira vínculo "contém" (sem "já existe", fora do grupo de cópias); trecho sem o cabeçalho do documento → com ressalva |
| E3 | Hash perceptual quebra com recorte e rotação | 🟠 | ✅ | Recorte ao conteúdo + 4 rotações; taxas medidas em 30 anexos: 90% (ruído), 87% (recorte 8 pt), 67% (recorte 20 pt), 87% (90°), 0% de falso positivo; petições separam mal (dito no texto) |
| E4 | "Garantia" do classificador com Wilson (aproximado); risco na faixa esconde precisão entre os decididos; supõe mesma distribuição | 🟠 | ✅ | Clopper-Pearson exato (bisseção na binomial) em todo o notebook; erro entre os decididos reportado (4,7% a 52,7% de limite superior); hipótese de mesma distribuição explicitada |
| E5 | Plataforma não usa índices exatos, LSH, cache, caminho de imagem nem classificador | 🟠 | ✅ | `Plataforma` com índices exatos, LSH acima de `limite_forca_bruta`, caminho de imagem, cache por parágrafo (por cliente), checagem de cadastro e `decisor` injetável; caso de 300 docs pela plataforma: 1.766 de 44.850 pares, recall 97,7% |
| E6 | Texto longo (~20 mil caracteres) e difícil de defender inteiro | 🟠 | ✅ | Texto de ~20 mil para ~11 mil caracteres; guia de defesa abaixo |
| E7 | Pseudonimização sem nomes/e-mails/telefones; "99,7%" sem premissa; alerta para imagem só recomprimida | 🟡 | ✅ | Pseudonimização de partes, CPF, CNPJ, processo, e-mail, telefone e OAB (assert sem nome nem CPF em claro); premissa dos 99,7% explícita; alerta só para assinatura/quantidade de imagens |

## Log

- 13/10: revisão concluída; plano criado.
- 13/10: notebook reescrito (14 seções, 55 células); texto reescrito; consistência texto × notebook verificada.
- 13/10: segunda revisão: R1–R10 abertos.
- 13/10: R1–R10 corrigidos. Os casos adversariais dessa revisão foram rodados de novo e se comportam como esperado. A avaliação ainda achou um defeito real (palavra hifenizada em volta do rodapé), já corrigido e coberto por teste. Notebook com 61 células, 0 erros; 37/37 números do texto conferidos na saída.
- 13/10: rodada 3 (desenho): D1–D8 abertos.
- 13/10: D1–D8 implementados. Achados no caminho:
  - o hash perceptual separa mal páginas de texto do mesmo modelo (escopo restrito a anexos);
  - com poucos pares de calibração, o classificador não certificava nada; o risco passou a ser medido sobre a faixa toda;
  - o teste do caso "espalhado" passava pelo motivo errado (corrigido);
  - a contiguidade era frágil a um parágrafo alinhado por acaso (janela de 90%).

  Comparação 40% mais rápida (chave cosmética por parágrafo pré-calculada). Notebook com 68 células, 0 erros, ~38 s; 51 números do texto conferidos.
- 13/10: rodada 4: E1–E7 abertos.
- 13/10: E1–E7 corrigidos. Achados no caminho:
  - o cache por parágrafo era global, entre clientes (agora é escopado por cliente);
  - no trecho, a identidade vinha da 1ª qualificação dos autos (agora vem do trecho);
  - trecho sem cabeçalho saía como "cópia exata" (agora sai com ressalva).

  Notebook com 73 células, 0 erros; 37/37 números do texto conferidos.
- 13/10: rodada 5 (aderência ao enunciado): F1–F9 aplicados; texto ~13,5 mil caracteres; notebook com 73 células, 0 erros; 35 números do texto conferidos na saída.
- 13/10: rodada 6 (Jaccard × contenção): G1–G5 aplicados. Achado no caminho: com "≥ 3 âncoras" como critério, 11,7% dos pares viravam candidatos; com contenção ≥ 10%, 2,7% e o mesmo recall. Notebook com 73 células, 0 erros.

---

## Rodada 5 — aderência ao enunciado e revisão do texto (13/10)

| ID | Ajuste | Status | Onde |
|---|---|---|---|
| F1 | Resumo abre com **como a similaridade é calculada** (cobertura nos dois sentidos) | ✅ | texto: Resumo |
| F2 | "Fluxo para cada novo documento" em 5 passos (o enunciado pede "para cada novo documento") | ✅ | texto: nova seção |
| F3 | "Em revisão" como estado temporário que termina numa das 3 classes e vira rótulo | ✅ | texto: Resumo e §5 |
| F4 | Por que duas coberturas e não um número único (cosseno/Jaccard) | ✅ | texto §2; notebook §3 |
| F5 | Exemplo trabalhado com **data** alterada, como no enunciado (nomes, valores, datas, parágrafos) | ✅ | notebook §4.1 (cobertura 84%/84%, Jaccard 0,49, campos valor/data/CPF); texto §2 |
| F6 | Tabela "Alternativas consideradas" (hash, MinHash, embeddings, LLM, núcleo) | ✅ | texto §1 |
| F7 | Avaliação começa pelo método (rótulos às cegas por faixa de cobertura, kappa, **precisão e recall por classe**); fase 2 movida para Evolução | ✅ | texto §4 e §6; notebook imprime precisão/recall |
| F8 | Regras numeradas "em ordem", condição completa do trecho, "cortes são pontos de partida" | ✅ | texto §2 |
| F9 | Justificativa dos embeddings corrigida; limitações: terceiros não pseudonimizados e cliente novo sem coleção | ✅ | texto §1 e §6 |

---

## Rodada 6 — Jaccard × contenção (13/10)

**Motivação:** o Jaccard é simétrico e cai com a diferença de tamanho. Ele aparecia no exemplo trabalhado, entre os atributos do classificador e, principalmente, na busca de candidatos (MinHash/LSH estima Jaccard), que **perdia documento contido em outro**, justamente a relação por trecho do desenho.

| ID | Mudança | Status | Onde |
|---|---|---|---|
| G1 | MinHash/LSH substituído por **índice de âncoras**: *winnowing* (janela 4) dos shingles específicos; candidato = contenção estimada ≥ 10% (metade do corte de "diferente") | ✅ | notebook §8 (`IndiceAncoras`, `impressoes`) e §9 |
| G2 | Medido: 300 docs → 1.193 candidatos (2,7% dos pares), **recall 100%** (o LSH dava 97,3%); pares relevantes têm contenção ≥ 0,93, os demais no máximo 0,20; "petição dentro dos autos" achada com contenção 1,0 enquanto o Jaccard cai para 0,07 | ✅ | notebook §9 |
| G3 | `Plataforma` usa o índice de âncoras: 300 docs em 0,8 s (antes 8 s), 2.364 de 44.850 pares comparados, recall 100% | ✅ | notebook §8/§9 |
| G4 | Jaccard fora do classificador; no exemplo trabalhado só como contraste ("meio parecido" que não diz nada) | ✅ | notebook §4.1 e §11.3 |
| G5 | Texto: alternativas (MinHash/LSH "não usado"; índice de âncoras na busca), "por que contenção e não Jaccard" com o número dos autos, escala com recall 100% | ✅ | texto §1, §2, §6 |

---

## Guia de defesa (o que um avaliador pode perguntar e a resposta curta)

| Pergunta | Resposta em uma frase |
|---|---|
| Por que nenhum limiar produz "cópia"? | Porque "cópia" autoriza tratar dois documentos como um só; esse erro só pode vir de igualdade mal definida (extração/normalização), que é testável caso a caso. |
| Por que shingles de 5 palavras? | Curtos o bastante para sobreviver a uma edição local e longos o bastante para serem específicos; uma troca destrói no máximo 5. |
| Por que cobertura e não Jaccard? | A pergunta jurídica é contenção ("quanto de A está em B"), não igualdade de conjuntos; o Jaccard é simétrico, cai com a diferença de tamanho (petição dentro de autos: 0,07 × contenção 1,0) e não diz o que mudou. |
| O que é "texto padrão" e de onde vem? | Shingle presente em ≥5% de uma coleção de referência (modelos públicos e do escritório), guardada só como contagem de hashes. |
| Como lida com documento de 300 páginas? | Índice invertido por âncoras + diff só dentro dos grupos alinhados; o LLM só vê trechos alterados e pseudonimizados. |
| Por que índice de âncoras e não MinHash/LSH? | O MinHash estima Jaccard, então o LSH perde documento contido em outro; o índice de âncoras estima contenção nos dois sentidos e acha trechos. |
| O que é *winnowing*? | De cada janela de 4 hashes de shingles consecutivos, guarda o menor; garante uma âncora em comum para todo trecho comum de ≥ 8 palavras, guardando ~1/3 dos shingles (técnica do MOSS, detector de plágio). |
| Por que contenção ≥ 10% para candidato? | É metade do corte de "diferente" (20%): margem para não perder nada que a comparação completa classificaria como versão; medido: relevantes ≥ 0,93, demais ≤ 0,20. |
| E documentos só de texto padrão? | Não têm âncoras; cópias vêm dos índices exatos (hash do arquivo, do texto e do texto normalizado). |
| O que é Clopper-Pearson? | Limite exato do intervalo de confiança de uma proporção binomial; com 0 erros em n, ≈ 3/n (regra de três). |
| O que o classificador garante? | Que, na calibração, o erro sobre a faixa ambígua fica ≤ 2% com 95% de confiança; não garante precisão entre os poucos decididos nem vale sob mudança de distribuição. |
| Por que agregar a revisão por documento? | 1% de abstenção por par com 30 comparações vira 26% dos documentos; o revisor trabalha por documento. |
| "Mesma peça" × "outra instância"? | Mesma qualificação (partes) e processo = mesma peça; outra parte ou processo = mesmo modelo usado para outro caso: não substitui. |
| Por que o hash perceptual não decide? | Ele não vê a troca de um número; serve para propor "provável cópia" de anexos sem texto. |
| Qual o maior risco do desenho? | Rótulos reais ruidosos: sem kappa alto, a fase 2 automatiza pouco e o custo humano continua dominante. |
