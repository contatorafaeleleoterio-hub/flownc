# STATUS — FlowNC

> Para retomar o projeto, leia primeiro `..\docs\README.md`. Este arquivo é o
> detalhe por fase.

**Baseline:** `..\docs\PRD.md`
**Última atualização:** 2026-06-02

## Onde estamos no roadmap (PRD §19)

| Fase | Descrição | Status |
|------|-----------|--------|
| 1 | Núcleo de matching e plano (sem UI) | ✅ Concluída e validada |
| 2 | File handling e verificações | ✅ Concluída e validada |
| 3 | Preset store | 🟡 Parcial (carga/validação/salvar ok; falta CRUD criar/duplicar/renomear/excluir + backup) |
| 4 | UI esqueleto (PySide6) | ✅ Feita |
| 5 | UI de regras (editar/criar trocas na tela) | ✅ Feita (modelo POR PROGRAMA: comuns + específicas) |
| 6 | Dry-run/preview/verificações na UI | ✅ Feita (preview em diálogo + aba Verificações separada) |
| 7 | Salvamento e log na UI | ✅ Feita (pasta separada + log) |
| 8 | Threading e performance | ⬜ (hoje síncrono; ok p/ poucos/médios) |
| 9 | Empacotamento (EXE onedir portátil) | ✅ EXE regenerado com conferência (Sessão D) |
| 10 | Hardening | ✅ Stage 0 completo (H0.1–H0.6) |

## Sessão 2026-06-02 — entrega verificada + análise de UX (sem mudança de código)

- **Reverificação do sistema atual:** `pytest tests -q` → **106/106 verdes** (~3,4s; inclui
  `test_ui_smoke.py`). **EXE antigo em `dist` abre** sem erro
  (título de janela correto, encerrado limpo). Pacote conferido: EXE + `_internal\` +
  `data\presets\MAZAK_VTC530.json` + `GUIA-DE-USO.txt` (idêntico ao `.md`) + `LEIA-ME.txt`.
  **Entregue como pasta pronta para pendrive** (sem ZIP, por opção do Rafael). Nenhuma linha
  de código alterada.
- **Análise de UX (workflow devolvido pelo Rafael):** produzidos na raiz do projeto —
  `06-ANALISE-UX-WORKFLOW.md` (relatório: 12 problemas + 7 achados extras + **novo workflow
  de 5 passos + novo layout** + roadmap P0→P3), `mockups\06-mockup-ux.html` e
  `mockups\06-prototipo-navegavel.html`, e `07-PROMPT-PESQUISA-UI.md` (prompt de pesquisa
  para decidir tela-única-vs-wizard com base em normas + benchmark).
- **Achado técnico p/ implementação futura:** verificações configuráveis hoje rodam sobre o
  **original** (`_on_execute_verifs` → `read_file`); para virarem porteiro no preview, rodar
  sobre o **resultado** (sem tocar no `core/`; `run_configurable` já existe).

## Correções de campo — botão Executar + extensões (2026-06-01, 106 testes verdes)

Reportado pelo Rafael: "botão Executar não faz nada, sem feedback". Dois bugs:

1. **Crash silencioso (enum→string):** `OnZeroMatches` herda de `str`; o Qt devolvia
   string pura ao ler de `QTableWidgetItem` (UserRole), e `.value` (add. na Sessão D)
   crashava. Em EXE `--windowed` o erro sumia. **Fix:** `_read_subs_table` reconstrói o
   enum; `_build_outcomes` defensivo; `sys.excepthook` global em `main.py` mostra erro
   em diálogo (nunca mais "mudo"). Regressão: `tests/test_ui_smoke.py` (GUI offscreen).
2. **Arquivos sem extensão ignorados:** programas Fanuc reais (`O2169`...) não têm
   extensão; `list_input_files` filtrava por `.nc/.txt/.iso` → 0 arquivos. **Fix:** aceita
   curinga `"*"`, sempre inclui sem-extensão (binário rejeitado por `read_file`). Preset
   MAZAK → `extensions: ["*"]`; "Abrir programa(s)" abre em "Todos os arquivos".
   Regressão: `tests/test_list_input_files.py`.

EXE regenerado com os fixes. Guia do operador: `..\GUIA-DE-USO.md` (cópia `.txt` no dist).

## Sessão D — Conferência forte pós-salvamento (2026-06-01, 95 testes verdes)

- `core/conference.py` (novo) — `integrity_hash` (SHA-256), `verify_saved` (relê cada
  arquivo gravado e compara hash), `format_integrity_report`, dataclass `IntegrityResult`
- `ui/main_window.py`:
  - `FileOutcome.checklist` — lista `(find, replace, count, on_zero_label)` por regra
  - `_build_outcomes` popula o checklist (inclusive trocas com 0 ocorrências)
  - `_detail` mostra **CHECKLIST DE TROCAS PLANEJADAS** no preview (OK / aviso / ERRO)
  - `_save` faz **conferência pós-salvamento**: relê arquivos, confere SHA-256,
    grava relatório de integridade + contagem por regra no log; alerta se divergir
- `tests/test_conference.py` — 10 testes (hash, verify ok/divergência/ausente/múltiplos, relatório)
- **mypy --strict no core: limpo** (corrigidos 9 erros de tipagem pré-existentes em
  `preset_store.py`: genéricos `dict`/`list` sem args, `_as_int`, `_enum` com TypeVar)

## Sessão C — Pasta de saída configurável (2026-06-01, 84 testes verdes)

- `core/settings_store.py` — `AppSettings` (output_mode/output_dir), `load_settings` (fallback seguro), `save_settings` (atômico)
- `app_paths.settings_path()` — caminho portátil para `data/settings.json`
- `core/file_handler.make_output_dir` — parâmetro `base_dir=None` preserva comportamento legado
- `ui/main_window.py` — linha "Destino:" com radio `Ao lado dos originais` / `Pasta fixa` + `Escolher...`; persiste entre execuções; `_save` usa `base_dir` e bloqueia se pasta fixa não configurada
- `tests/test_settings_store.py` — 7 testes; `test_file_roundtrip.py` — 2 novos casos `base_dir`

## Sessão B — CRUD de perfis (2026-06-01, 75 testes verdes)

- `core/preset_store.py` — `create_preset`, `duplicate_preset`, `rename_preset`, `delete_preset`, `backup_before_write` (retain 10), `_validate_name` (charset + Windows reserved + traversal)
- `ui/main_window.py` — botões `Novo`, `Duplicar`, `Renomear`, `Excluir` na barra do topo; exclusão com dupla confirmação + backup automático
- `tests/test_preset_crud.py` — 16 testes

## Sessão A — Biblioteca de códigos (2026-06-01, 59 testes verdes)

- `core/library_store.py` — `CodeEntry`, `load_library`, `save_library` (JSON atômico, dedup, sort)
- `app_paths.library_path()` — caminho portátil para `data/library.json`
- `ui/library_dialog.py` — `LibraryDialog` (gerenciar) + `LibraryPickerDialog` (filtrar e inserir)
- `ui/main_window.py` — botões `+ da lista` (comum e por-arquivo) + `Gerenciar codigos...`
- `tests/test_library_store.py` — 8 testes (ausente, rejeição, roundtrip, dedup, sort, erros)

## Stage 0 — Hardening (sessão 2026-06-01, 51 testes verdes)

| Item | Arquivo | Estado |
|------|---------|--------|
| H0.1 — preset malformado nunca derruba a GUI | `core/preset_store.py` | ✅ |
| H0.2 — verificação estrutural por token CNC (M300 ≠ M30) | `core/verifier.py` | ✅ |
| H0.3 — lote tudo-ou-nada (preflight + helpers) | `core/file_handler.py` + `ui/main_window.py` | ✅ |
| H0.4 — colisão de nomes / multi-pasta | `ui/main_window.py` | ✅ chave interna→resolve(); bloqueia dupes + multi-pasta |
| H0.5 — JSON atômico reutilizável | `core/json_store.py` (novo) | ✅ |
| H0.6 — paridade OnZeroMatches GUI↔CLI | `ui/main_window.py` | ✅ tupla 5 campos; IGNORE/WARN/ERROR enforçados |

Novos testes: `tests/test_json_store.py` (4), `tests/test_preset_store.py` (12), `tests/test_verifier.py` (+1 TV-STR-07).

## O que já funciona (verificado)

- Motor seguro (boundary §8.2 corrigido, sem cascata, conflitos com log) — **33 testes pytest verdes**.
- Leitura/escrita preservando encoding/BOM/EOL; escrita atômica; original nunca alterado; ignora `_processado_*`.
- Verificações estruturais (bloqueiam no salvar) e configuráveis (aba Verificações).
- **GUI por programa** (abas Substituições/Verificações; comuns + específicas; preview antes de salvar). Funciona com 1 ou vários programas.
- **EXE portátil antigo** em `dist` (~115 MB), preservado ate o smoke do novo `FlowNC.exe`.

## Como rodar

```powershell
cd C:\Users\USUARIO\Desktop\Projetos\Sistema_verificador_codigos_cnc\flownc
.\.venv\Scripts\python.exe main.py            # GUI (dev)
.\.venv\Scripts\python.exe -m pytest tests -q # 33 testes
powershell -ExecutionPolicy Bypass -File build_exe.ps1   # regenerar EXE
```

EXE portátil: depois do build do rebrand, copiar `dist\FlowNC\` p/ pen drive e rodar `FlowNC.exe`.

## Próximo passo (retomar)

Plano `04-PLANO-MELHORIAS` concluído em código (Stage 0 + Sessões A–E). Sistema **entregue e
verificado** (pacote antigo preservado em `dist` ate o smoke de `FlowNC.exe`).

**Duas frentes em aberto:**
1. **Validação operacional (só o Rafael):** rodar o EXE no chão de fábrica com **arquivos
   reais**, conferir o `_log.txt` (`=== CONFERENCIA POS-SALVAMENTO ===`).
2. **Redesenho de UI/UX (planejado, não implementado):** rodar a pesquisa do
   `..\07-PROMPT-PESQUISA-UI.md` → decidir tela-única-vs-wizard → implementar o **P0** do
   `..\06-ANALISE-UX-WORKFLOW.md` (só QSS + rótulos + fiação leve; **não tocar no `core/`**).
   Ver detalhe em `..\00-HANDOFF.md` §9 (bloco FOCO ATUAL).

**Regenerar EXE:** `python -m PyInstaller` (NÃO o `pyinstaller.exe` — wrapper quebrado
após mover o venv). O `build_exe.ps1` já foi corrigido para isso.

## Regras do usuário

- **Screenshot proibido sem autorização explícita** (ver `Desktop\CLAUDE.md` + `~/.claude/settings.json`).
- Exclusão/mover/renomear pasta do desktop: só com dupla confirmação.
