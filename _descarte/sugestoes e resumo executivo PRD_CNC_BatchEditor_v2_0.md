# Revisão Técnica — PRD v2.0 CNC Batch Editor

**Documento revisado:** 02-PRD_CNC_BatchEditor_v2.0.md
**Revisor:** Engenharia de software desktop (Python/PySide6/PyInstaller) + preparação CNC (ISO/Fanuc)
**Data:** 2026-05-29
**Veredito:** SIM COM CONDIÇÕES
**Maturidade:** ~7/10

---

## RESUMO EXECUTIVO

PRD bem estruturado, escopo claro e — ponto forte — desenho seguro por padrão (originais intactos + preview obrigatório). Maturidade ~7/10. Porém há bugs técnicos bloqueadores no motor de substituição (lookbehind, falta de `re.escape`, cascata, decimais) e a afirmação "todas as 10 categorias resolvidas por substituição textual" é falsa: Cat 9 (replicar peças) e a inserção livre da Cat 7 são impossíveis por texto puro. Encoding/BOM/quebra-de-linha sem round-trip definido é o risco de campo mais traiçoeiro (arquivo abre no editor mas o comando rejeita).

---

## ERROS CRÍTICOS (bloqueadores)

1. **Lookbehind `(?<![A-Z0-9])` está errado.** Em blocos concatenados sem espaço (Fanuc real: `M6T1`, `G43H1`, `S3000M3`), o caractere antes do código é um dígito → o `0-9` no lookbehind **bloqueia o match** e a substituição não ocorre. Impacto: regra "T1→T21" silenciosamente não aplica em `M6T1` → ferramenta errada na máquina. **Correção:** usar `(?<![A-Z])` (só letra, para não casar dentro de palavra de comentário). Dígito antes do endereço é normal e deve ser permitido.

2. **Falta `re.escape()` no texto do usuário.** O campo "Procurar" é texto livre e CNC é cheio de metacaracteres regex: `.` (decimais `X1.`), `(` `)` (comentários), `*`, `+`, `?`. Sem escapar, `(FRESA Ø12)` ou `X1.5` quebram ou casam errado. **Correção:** `re.escape(find)` sempre; aplicar word boundary **apenas** quando o find tem forma de código-endereço (`^[A-Z]\d+$`), nunca em texto livre/multi-token.

3. **Cascata / dupla substituição.** Regras aplicadas em sequência sobre o texto já alterado: `G54→G55` + `G55→G56` transforma `G54` em `G56`. O próprio exemplo do PRD tem `G54→G55`. Impacto: corrupção silenciosa. **Correção:** todas as regras casam contra o conteúdo **original** em passe único (não encadear saídas).

4. **Lookahead `(?![0-9])` insuficiente para decimais.** Em F/S, `F1→F2` corrompe `F1.5` em `F2.5` (após o `1` vem `.`, não dígito → casa). **Correção:** `(?![0-9.])` para evitar avanço/rotação com decimal.

5. **Cat 9 e inserção livre da Cat 7 são impossíveis por substituição textual.** Replicar blocos para G55/G56 = copiar região de código (não substituir texto); "adicionar M00 após linha X" só é possível via âncora (find `M30`→`M00\nM30`), não inserção arbitrária. A "Nota técnica" da Seção 4 afirma cobertura total — **incorreto**. **Correção:** declarar Cat 9 e inserção-livre como **limitações explícitas** fora do escopo do MVP.

6. **Round-trip de encoding/BOM/EOL não especificado.** Sem definir codificação de **escrita**, BOM e fim-de-linha, o arquivo pode mudar bytes: `Ø`/`°`/acentos em comentários corrompem, BOM (`\xEF\xBB\xBF`) antes do `%` faz o comando rejeitar, CRLF↔LF quebra drip-feed/DNC antigo. Impacto: arquivo abre no editor mas falha no controle — bug de campo difícil de diagnosticar. **Correção:** ler/escrever em binário, gravar com a **mesma** codificação lida, preservar BOM e EOL exatos; teste de fidelidade de bytes para ASCII/cp1252/utf-8.

---

## LACUNAS IMPORTANTES

1. **Schema JSON incompleto** (Seção 9): só tem `global_rules`, mas a UI tem regras individuais por arquivo; não há tipo "inserção"; `verifications` só checa presença → "checar T duplicado" (Cat 10) exige contagem, não suportado. Adicionar `individual_rules` e definir verificação de duplicidade ou removê-la do escopo.

2. **Conflito global × individual sem regra definida** (Seções 6.1/8). Definir: por arquivo, a regra individual **suprime** a global conflitante (não rodam ambas), e fixar ordem de aplicação. Adicionar em nova Seção "Resolução de conflitos".

3. **Comportamento de erro ausente:** arquivo corrompido, sem permissão de escrita, vazio, disco cheio, falha no meio do lote. Definir: escrita atômica (temp + rename), skip-and-report por arquivo, nunca abortar o lote em silêncio, nunca gravar arquivo parcial. Nova Seção "Tratamento de erros".

4. **Mín. de SO/hardware ausente** (Seção 9). PySide6/Qt6 **não roda em Win7/8** — risco real em PC de chão de fábrica. Especificar Win10 x64+, ~4 GB RAM, ~300 MB disco.

5. **CRUD de presets** (Seção 7): há "Novo"/"Salvar", falta editar/renomear/duplicar/excluir-com-confirmação.

6. **Leading-zero** (Seção 6.3): match literal exige formato idêntico — `T1`≠`T01`, `M8`≠`M08`. Fanuc frequentemente zero-padeia. Documentar e mitigar (ver Riscos #2).

7. **Performance em arquivos grandes** (omitida): moldes geram programas de 50k–500k+ linhas. Múltiplos regex + diff em `QTableWidget` congela a UI. Substituição em `QThread` + progress; preview renderiza **só linhas alteradas** (com contexto), não o arquivo inteiro.

8. **Quando a verificação roda:** Seção 8 põe verificação no passo 4 (antes do preview), Seção 7.3 diz "após processar". Definir que avalia o **resultado** (pós-substituição).

---

## INCONSISTÊNCIAS

1. "Todas as categorias resolvidas por substituição textual" (Seção 4) × Cat 9 e inserção da Cat 7 impossíveis (erro #5).

2. Cat 1 listada como **uma** categoria, mas é **três** regras (T+H+D) sem garantia de consistência — substituição textual não vincula nem valida H/D em relação a T.

3. Exemplos usam `M8`/`M9`/`M30` (sem zero), mas Fanuc real costuma usar `M08`/`M09`/`M06` → exemplos podem induzir formato que não casa com os arquivos reais.

4. Schema JSON (Seção 9) só mostra `global_rules`; UI e Seção 6.1 têm regras individuais → schema não reflete a UI.

5. Fluxo (8) vs painel (7.3): momento de execução da verificação contraditório.

---

## RISCOS NÃO MAPEADOS (além da Seção 12)

1. **Perfil errado aplicado silenciosamente** (UX/segurança): carregar MAZAK e estar preparando ROMI → magazine/offset errados → colisão. Mitigação: banner persistente do perfil ativo + confirmar perfil no diálogo de processar + nome do perfil na pasta de saída.

2. **Regra sem efeito = falha SILENCIOSA** (o risco prático nº1): 0 ocorrências e o operador acha que aplicou → roda ferramenta/offset errado. Mitigação: contagem de matches por regra + **alerta vermelho** se qualquer regra ativa casar 0 vezes no lote. Cobre toda a classe leading-zero.

3. **Auto-ingestão de saídas anteriores** (dados): recarregar pasta que contém `_processado_*` reprocessa arquivos já alterados. Excluir pastas de saída do carregamento.

4. **Colisão de pasta** (dados): duas execuções no mesmo segundo → mesmo nome → sobrescreve. Sufixo incremental se existir.

5. **Verificação de estrutura mínima ausente** (segurança — o item mais importante): nada garante que o output mantém `%`, `O####`, `M30`/`M02`, nem alerta se ficou vazio. Uma regra de remoção pode apagar `%`/`M30` por sobreposição. Mitigação: **checagem estrutural obrigatória e independente** das verificações do usuário, que bloqueia/avisa no salvar.

6. **AV corporativo + `--onefile`** (já citado, elevar): preferir `--onedir` (menos falso-positivo) + assinatura de código; `--onefile` ainda inicia lento em HDD (descompacta Qt ~150–250 MB a cada abertura).

7. **Campo "Substituir" vazio acidental:** marcar visualmente regras de remoção e exigir confirmação listando as deleções no processar.

---

## MELHORIAS SUGERIDAS

1. "Grupo de troca de ferramenta": cria T/H/D vinculados de uma vez + verificação opcional de consistência H↔T/D↔T (reduz risco da Cat 1 sem virar parser).

2. `QSplitter` nos 3 painéis (resize + persistência) e regras individuais em aba ou seção colável com badge de contagem — evita truncamento em 1366×768.

3. Confirmação em "Limpar" e em sobrescrever preset; undo de edição de regras (o output em pasta nova já cobre o undo dos arquivos).

4. Trocar `chardet` por **charset-normalizer** (MIT, mais preciso/rápido; chardet é LGPL) ou lista determinística `utf-8-sig → utf-8 → cp1252 → latin-1` (latin-1 nunca falha decode).

5. Dry-run: relatório de contagem por regra **antes** do preview.

6. Critérios de aceitação com vetores de teste: `T1` não casa `T10`; `M6T1` casa `T1`; `F1` não corrompe `F1.5`; round-trip de bytes preservado.

7. Avisar quando o "find" tem formato diferente do encontrado (regra `T1`, arquivo `T01`).

---

## PRD APROVADO PARA DESENVOLVIMENTO?

**SIM COM CONDIÇÕES.** Arquitetura e filosofia de segurança são sólidas e o sistema é construível. Condicionado a: corrigir os 6 erros críticos (boundary, escape, cascata, decimais, encoding round-trip) e **declarar Cat 9 e inserção-livre da Cat 7 como limitações explícitas** — não são realizáveis por substituição textual.
