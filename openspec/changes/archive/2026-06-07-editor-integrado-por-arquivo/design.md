## Context

O FlowNC (PySide6) hoje só edita programas indiretamente, via tabelas de trocas + Lote, cuja gravação vai sempre para **pasta separada** e mantém o invariante histórico *"o original nunca é sobrescrito"* (afirmado em `core/file_handler.py`). Falta o ajuste manual rápido de **um** arquivo: hoje o operador abre o `.NC` no Bloco de Notas do Windows, perdendo a biblioteca de códigos, a contagem por borda CNC e a gravação segura.

O mockup `mockups/painel-final.v2.html` e `docs/PLANO-MOCKUP-V2-EDITOR.md` (decisões 6–13), aprovados por Rafael, especificam um **editor integrado por arquivo** na própria janela. Esta mudança porta a feature reaproveitando o motor existente, sem mexer no fluxo de Lote.

Primitivas já existentes e reutilizáveis (não reescrever):
- `core/matcher.find_matches(text, rule, case_sensitive)` → intervalos `(start, end)` com **borda CNC** (lookbehind/lookahead). É a fonte da contagem do Lote.
- `core/file_handler.read_file` → `(texto, EncodingInfo)`; `encode_text(text, info)`; `write_atomic(path, text, info)` (= `_write_bytes_atomic` com tmp + `os.replace`).
- `core/conference.integrity_hash(bytes)` → SHA-256.
- `core/library_store.load_library` / `CodeEntry(find, replace, label)`; `ui/library_dialog.LibraryPickerDialog`.

## Goals / Non-Goals

**Goals:**
- Editor de texto embutido por programa (numeração de linha, fonte mono, edição direta) dentro da janela.
- Localizador idêntico ao Lote em contagem (mesma `find_matches`) e gravação que preserva encoding/EOL.
- Gravação **in-place sem backup**, mas **atômica + conferida por SHA + avisada**, com Salvar travado sem alteração e guarda de não-salvo.
- Lógica testável isolada no `core/` (gravação in-place; a contagem/navegação já vêm de `find_matches`).

**Non-Goals:**
- Refino visual por tokens, remoção da contagem automática do painel, colunas dinâmicas, fila de múltiplas edições (mudanças OpenSpec separadas).
- Qualquer alteração no motor de Lote, presets, verificações ou na escrita da biblioteca (aqui a biblioteca é só leitura).

## Decisions

### Decisão 1 — Onde vive a lógica: `core/inplace_save.py` (puro/testável) + `ui/editor_panel.py` (QWidget)
A regra do projeto é `mypy --strict` no `core/` e lógica testável fora da UI. A **gravação in-place** vira `core/inplace_save.py::salvar_no_lugar(path, text, info) -> ResultadoGravacao`, testável com `tmp_path` (sem Qt). O `QWidget` do editor (`ui/editor_panel.py`) cuida só de apresentação/interação e delega.
- **Alternativa descartada:** colocar a gravação dentro do `QWidget`. Rejeitada: não testável sem GUI e fora do padrão do `core/`.

### Decisão 2 — Reusar `find_matches` para varredura/contagem/navegação (não inventar busca)
A varredura do editor cria um `Rule(find=<código>, mode=AUTO)` e chama `matcher.find_matches` sobre o texto do buffer. Isso garante o requisito "contagem idêntica à do Lote" de graça (mesma borda CNC, mesmo tratamento de `M8` vs `M08`). A navegação usa os mesmos intervalos `(start, end)` para posicionar o cursor/seleção. A varredura **não** rola a tela; só as setas rolam (mapeando o intervalo da ocorrência atual para a posição no `QPlainTextEdit`).
- **Alternativa descartada:** `QPlainTextEdit.find()` nativo. Rejeitada: não respeita a borda CNC (casaria `M8` dentro de `M80`) e divergiria do Lote.

### Decisão 3 — Gravação in-place SEM backup, com garantias substitutas (o cerne da mudança)
Por decisão de produto, o editor é o atalho de ajuste manual rápido e **não** cria backup (diferente do Lote). Para que isso seja seguro, `salvar_no_lugar` faz, nesta ordem:
1. **Preflight de codificação:** `encode_text(text, info)`; se falhar (`UnicodeEncodeError`/`LookupError`), aborta **antes de tocar o disco** — original intacto.
2. **Escrita atômica:** `write_atomic(path, text, info)` (grava `path.tmp` no mesmo volume + `os.replace`) — a pasta de origem nunca fica sem o arquivo.
3. **Conferência pós-escrita:** relê os bytes do `path` e compara `integrity_hash` com o dos bytes que deveriam ter sido gravados; divergência → resultado de falha (não "salvo").
4. Sem cópia de backup; a UI exibe o aviso permanente "salva direto, sem cópia".
- **Por que aceitável sem backup:** atômico (sem estado parcial), conferido por SHA (sem corrupção silenciosa), explícito (aviso + Salvar só quando há mudança), e escopado a um único arquivo. O invariante do Lote ("o original nunca se perde") **não** é enfraquecido — o Lote continua com pasta separada/backup; só o editor abre esse caminho, conscientemente.
- **Alternativa descartada:** criar backup também no editor. Rejeitada por decisão de produto (poluiria a pasta de origem no ajuste rápido); a segurança vem das garantias acima.

### Decisão 4 — Estado de "sujo" (dirty) e guarda de não-salvo na UI
O editor guarda o texto carregado (baseline) e compara com o buffer para o estado dirty: Salvar habilita só quando `buffer != baseline`; após salvar, baseline := buffer. Trocar de arquivo/fechar com dirty dispara `QMessageBox` "salvar antes de trocar?" (Salvar/Descartar/Cancelar). A contagem da varredura é marcada como **desatualizada** a cada edição (espelha o mockup), evitando número mentiroso.

### Decisão 5 — Acoplamento mínimo na `main_window`
A ação "Editar" entra por item da lista `lst_prog` (botão por linha ou ação contextual), abrindo o `editor_panel` numa área dedicada da janela (a seleção/marcação em lote permanece). A `main_window` injeta a biblioteca já carregada (`self._library`) e o `read_file` no editor; nada do fluxo de Lote muda.

## Risks / Trade-offs

- **[Sem backup: edição destrutiva]** → Mitigado por escrita atômica + dupla conferência SHA + aviso explícito + Salvar travado sem alteração + guarda de não-salvo. Escopo limitado a um arquivo por vez.
- **[`os.replace` em pasta de rede]** → O `.tmp` é criado no **mesmo diretório** do alvo (mesmo volume), condição para `os.replace` ser atômico mesmo em rede (mesma técnica já usada no Lote).
- **[Divergência de contagem editor × Lote]** → Eliminada por construção: ambos usam `find_matches`. Teste compara os dois caminhos no mesmo vetor.
- **[Codificação: caractere novo fora do cp1252]** → Preflight `encode_text` aborta antes de escrever; mensagem cita o problema; original intacto.
- **[Perda de edição ao trocar de arquivo]** → Guarda de não-salvo com Cancelar que preserva o buffer.
- **[Arquivo grande no `QPlainTextEdit`]** → Programas CNC são pequenos/médios; `QPlainTextEdit` aguenta. Sem virtualização nesta mudança (Non-Goal).

## Migration Plan

Sem migração de dados: nenhuma mudança em presets, settings, schema ou biblioteca. É feature aditiva.
- **Rollback:** remover a ação "Editar" e os módulos novos (`core/inplace_save.py`, `ui/editor_panel.py`) restaura o comportamento anterior; o motor de Lote nunca foi tocado.

## Open Questions

- Layout do editor na janela: aba dedicada vs. área que substitui o painel à direita (o mockup usa "substitui o resumo"). Decidir na implementação da UI; não afeta os requisitos nem o `core/`.
- Mostrar no editor o caminho/encoding/EOL detectados (rótulo informativo)? Desejável, não obrigatório nesta mudança.
