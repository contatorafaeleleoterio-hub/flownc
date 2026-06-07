## Why

Hoje, para um ajuste manual rápido num único programa, o operador precisa **sair do FlowNC e abrir o `.NC` no Bloco de Notas do Windows** — sem a biblioteca de códigos à mão, sem contagem por borda CNC e sem gravação segura. O mockup `mockups/painel-final.v2.html` (e as decisões 6–13 de `docs/PLANO-MOCKUP-V2-EDITOR.md`), já aprovados por Rafael, definem um **editor integrado por arquivo** dentro da própria janela. Esta mudança porta essa feature para o app PySide6, reaproveitando o motor existente (`matcher`, `file_handler`, `conference`) para que a contagem do editor seja idêntica à do Lote e a gravação preserve encoding/EOL.

## What Changes

- **Editor de texto integrado por arquivo** (`ui/editor_panel.py`, novo) — cada programa da lista ganha a ação **"Editar"**, que abre um editor estilo Bloco de Notas embutido (numeração de linha, fonte monoespaçada, edição direta), sem abrir o arquivo fora do app. Conviver com o fluxo de Lote (abas/área dedicada na janela; a seleção em lote continua intacta).
- **Localizador no cabeçalho do editor** — dropdown **"Código da biblioteca"** (pesquisável, alimentado por `library_store`), botão **Varredura** que conta as ocorrências do código no buffer **sem mover o cursor**, **contador "N encontrados" + posição "i/N"**, e setas **anterior/próximo** que só rolam até a ocorrência quando clicadas. A contagem usa `matcher.find_matches` → **mesma semântica de borda CNC do Lote**.
- **Substituir em massa no editor** — dropdown **"Substituir por"** (biblioteca) + **"Substituir todos"** e **"Um a um"** (passo a passo com confirmação por ocorrência). Opera sobre o buffer em edição (não sobre disco) até o Salvar.
- **Salvar direto, SEM backup** (`core/inplace_save.py`, novo) — `salvar_no_lugar` **sobrescreve o original na pasta de origem**, de forma **atômica** (tmp + `os.replace`), **preservando encoding/BOM/EOL** (reusa `encode_text`/`write_atomic`) e com **conferência SHA-256 pós-escrita** (reusa `integrity_hash`). **Por decisão de produto, não há cópia de backup** — é o atalho de ajuste manual rápido. A UI mostra o aviso permanente **"salva direto, sem cópia"** e o botão **Salvar fica desabilitado enquanto não há alteração**.
- **Guarda de alterações não salvas** — trocar de arquivo (ou voltar ao resumo/lote) com edição pendente abre confirmação **"salvar antes de trocar?"** (Salvar / Descartar / Cancelar).
- **BREAKING (invariante):** o app deixa de garantir, **apenas neste caminho do editor**, o invariante histórico *"o original nunca é sobrescrito"* (hoje afirmado em `core/file_handler.py`). O Lote permanece 100% como é (saída em pasta separada / backup). A gravação in-place é **explícita, atômica, conferida por SHA e avisada ao usuário** — as garantias substitutas que tornam a ausência de backup aceitável.
- **Non-goals:** refino visual por tokens, remoção da contagem automática do painel, colunas dinâmicas e a fila de múltiplas edições (cada um vira mudança OpenSpec separada). Sem alterar o motor de Lote, presets, verificações ou a biblioteca (só leitura da biblioteca aqui).

## Capabilities

### New Capabilities
- `editor-de-arquivo`: editor de texto embutido por programa (abrir via "Editar", numeração de linha, edição direta), **gravação in-place segura sem backup** (atômica, preserva encoding/EOL, dupla conferência SHA-256, aviso explícito, Salvar desabilitado sem alteração) e **guarda de alterações não salvas** ao trocar de arquivo. Convive com o fluxo de Lote sem alterá-lo.
- `localizador-no-editor`: localizar um código da biblioteca no arquivo aberto **sem mover o cursor**, contar ocorrências (com a mesma borda CNC do motor) e posição "i/N", navegar anterior/próximo sob demanda, e **substituir em massa** (todos de uma vez, ou um a um com confirmação) sobre o buffer em edição.

### Modified Capabilities
<!-- Não há specs arquivadas em openspec/specs/; todas as capacidades acima são novas. A tensão com o invariante de Lote é tratada em design.md e nos requisitos de gravação de `editor-de-arquivo`. -->

## Impact

- **Código novo:** `core/inplace_save.py` (gravação in-place atômica + conferência, função testável com `tmp_path`); `ui/editor_panel.py` (o `QWidget` do editor + localizador + substituir).
- **Código modificado:** `flownc/ui/main_window.py` — ação "Editar" por programa na lista (`lst_prog`), abertura/fechamento do editor na janela, guarda de não-salvo; reutiliza `read_file`, `load_library`/`CodeEntry`, `LibraryPickerDialog`.
- **Reaproveitado intacto (não mexer):** `core/matcher.py` (`find_matches`, borda CNC) para varredura/contagem/navegação; `core/file_handler.py` (`read_file`, `encode_text`, `write_atomic`/`_write_bytes_atomic`) para leitura e gravação atômica; `core/conference.py` (`integrity_hash`) para a conferência pós-escrita; `core/library_store.py` (`load_library`, `CodeEntry`).
- **Testes novos:** `tests/test_inplace_save.py` (atômico; preserva encoding/BOM/EOL byte-a-byte quando nada muda; conferência SHA detecta corrupção; falha de codificação não toca o original; sem `.tmp` órfão); `tests/test_editor_localizador.py` (contagem = `find_matches`; navegação i/N circular; substituir todos; substituir um a um); reforço em `tests/test_ui_smoke.py` (abrir editor, editar, Salvar habilita/desabilita, trocar com aviso).
- **Decisão de produto a registrar na spec:** "editor salva sem backup × Lote salva com backup" — formalizada como garantias substitutas (atômica + SHA + aviso + Salvar travado sem mudança), escopadas só ao editor.
- **Compatibilidade:** nenhuma mudança em presets, settings, schema ou motor de Lote. A biblioteca é usada só em leitura.
- **DoD:** testes novos verdes · `mypy --strict` limpo no `core/` · `ruff` (line-length 100) limpo · gravação in-place preserva round-trip e é conferida por SHA · contagem do editor idêntica à do Lote (mesmos vetores de `find_matches`) · Salvar desabilitado sem alteração · troca com pendência pede confirmação · fluxo de Lote inalterado.
