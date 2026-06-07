> Grupo 1 = `core/` puro (gravação in-place) — nada no `core/` sem teste novo. Grupos 2–4 = UI (editor + localizador + integração). Grupo 5 = QA. Regra de ouro: rodar a suíte inteira ao final, sem regredir os 106 testes existentes; `mypy --strict` no `core/` e `ruff` (line-length 100) limpos.

## 1. Gravação in-place segura (`core/inplace_save.py`, novo, puro/sensível)

- [x] 1.1 Criar dataclass `ResultadoGravacao` (ok: bool, mensagem: str, sha_conferido: bool) para reportar sucesso/falha sem exceção silenciosa.
- [x] 1.2 Criar `salvar_no_lugar(path, text, info) -> ResultadoGravacao`: (1) preflight `encode_text(text, info)` — se `UnicodeEncodeError`/`LookupError`, abortar **antes** de tocar o disco; (2) `write_atomic(path, text, info)` (tmp no mesmo diretório + `os.replace`); (3) reler bytes e comparar `integrity_hash` com os bytes esperados; divergência → `ok=False`.
- [x] 1.3 Garantir: NÃO cria backup (proposital); NÃO deixa `.tmp` órfão em caso de falha; preserva encoding/BOM/EOL via `info`.
- [x] 1.4 `tests/test_inplace_save.py`: sobrescreve no lugar preservando encoding/EOL (CRLF/cp1252) · round-trip byte-a-byte quando nada muda · conferência SHA detecta corrupção (mock/patch) · falha de codificação não toca o original e não deixa `.tmp` · sem pasta de backup criada.
- [x] 1.5 `mypy --strict` e `ruff` limpos no módulo novo.

## 2. Widget do editor (`ui/editor_panel.py`, novo)

- [x] 2.1 Criar `EditorPanel(QWidget)` com `QPlainTextEdit` em fonte monoespaçada + **numeração de linha** (gutter sincronizado com o scroll).
- [x] 2.2 `abrir(path)`: ler com `read_file`, popular o buffer, guardar baseline (texto + `EncodingInfo`); cabeçalho mostra o nome do arquivo.
- [x] 2.3 Estado **dirty**: comparar buffer com baseline; sinal `dirtyChanged` para habilitar/desabilitar Salvar; após salvar, baseline := buffer.
- [x] 2.4 Botão **Salvar** delega a `core.inplace_save.salvar_no_lugar`; sucesso → `QMessageBox` discreto e baseline atualizado; falha → `QMessageBox` de erro (original intacto).
- [x] 2.5 Exibir aviso permanente **"salva direto, sem cópia"** e botão **"✕ Voltar ao resumo/lote"**.
- [x] 2.6 `tem_alteracao() -> bool` para a guarda de não-salvo (usado pela `main_window`).

## 3. Localizador e substituir no editor (`ui/editor_panel.py`)

- [x] 3.1 Dropdown **"Código da biblioteca"** pesquisável, alimentado pela biblioteca injetada (`CodeEntry`); filtro por digitação.
- [x] 3.2 **Varredura**: montar `Rule(find=<código>, mode=AUTO)` e chamar `matcher.find_matches(buffer, rule, case_sensitive)`; guardar os intervalos. NÃO mover o cursor nem rolar; exibir **"N encontrados"** e **"i/N"**.
- [x] 3.3 Marcar a contagem como **desatualizada** a cada edição do buffer (até nova varredura).
- [x] 3.4 Setas **anterior/próximo**: navegação **circular** que rola/seleciona a ocorrência atual (mapear span→cursor no `QPlainTextEdit`) e atualiza "i/N"; só navega quando clicada.
- [x] 3.5 Dropdown **"Substituir por"** + **"Substituir todos"**: trocar todas as ocorrências (via spans de `find_matches`, de trás p/ frente p/ não invalidar offsets) no buffer; marca dirty; recontar.
- [x] 3.6 **"Um a um"**: navegar até a ocorrência atual e oferecer substituir / pular / concluir, repetindo; trocas no buffer; marca dirty.
- [x] 3.7 `tests/test_editor_localizador.py` (lógica pura, sem GUI): contagem == `find_matches` no mesmo texto · substituir todos confere com a troca esperada · um a um (substituir vs. pular) · borda CNC (`M8` não conta dentro de `M80`).

## 4. Integração na janela (`flownc/ui/main_window.py`)

- [x] 4.1 Adicionar ação **"Editar"** por programa na lista `lst_prog` (botão por linha ou menu de contexto), abrindo o `EditorPanel` numa área dedicada da janela sem remover a marcação em lote.
- [x] 4.2 Injetar no editor a biblioteca já carregada (`self._library`) e usar `read_file` existente; nada do fluxo de Lote é alterado.
- [x] 4.3 **Guarda de não-salvo**: ao trocar de arquivo no editor ou fechá-lo com `tem_alteracao()`, abrir `QMessageBox` "salvar antes de trocar?" (Salvar/Descartar/Cancelar); Cancelar preserva a edição.
- [x] 4.4 Garantir que abrir/fechar o editor não interfere em presets, verificações nem na execução do Lote.

## 5. QA e fechamento

- [x] 5.1 Reforçar `tests/test_ui_smoke.py`: abrir editor, editar, Salvar habilita/desabilita, trocar com aviso (sem travar a suíte headless).
- [x] 5.2 Rodar a suíte completa (`pytest`) — todos verdes, sem regressão dos 106 existentes.
- [x] 5.3 `mypy --strict` limpo no `core/`; `ruff` (line-length 100) limpo nos arquivos novos/alterados.
- [x] 5.4 Conferir DoD: gravação in-place atômica + conferida por SHA + preserva round-trip · contagem do editor idêntica ao Lote · Salvar travado sem alteração · guarda de não-salvo · fluxo de Lote inalterado.
- [x] 5.5 Smoke manual: rodar o app, "Editar" um `.NC`, localizar/contar/navegar, substituir todos e um a um, Salvar (conferir que o original foi sobrescrito sem backup). *(Rafael optou por pular o smoke manual; boot do EXE verificado automaticamente.)*
- [x] 5.6 Atualizar `docs/CONTEXTO.md` e a memória ao concluir; preparar para `/opsx:archive`.
