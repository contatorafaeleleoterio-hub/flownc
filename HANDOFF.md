# Handoff — redesign-fundacao-visual (2026-06-06)

Status: 22/24 tarefas (2 bloqueadas por TTFs IBM Plex)

Feito nesta sessão:
- `/opsx:archive motor-contagem-e-publicacao` — change arquivada
- `/opsx:propose redesign-fundacao-visual` — proposal + design + spec + tasks criados
- `/opsx:apply redesign-fundacao-visual` — implementação parcial:
  - `flownc/ui/theme.py` — todos os tokens do mockup
  - `flownc/assets/fonts/` — pasta criada (TTFs pendentes)
  - `flownc/ui/style.qss` — 8 seletores obrigatórios
  - `flownc/ui/main_window.py` — `_register_fonts()` + `_apply_stylesheet()` no boot
  - `flownc/app_paths.py` — `fonts_dir()` + `qss_path()`
  - Smoke: app abre, sem widget quebrado; QTableWidget dark = comportamento nativo (não causado pelo QSS)

Onde parou:
- Mudança A 22/24 (tarefas 2.2 e 2.3 bloqueadas: TTFs IBM Plex não encontrados)
- Change ainda NÃO arquivada (aguarda decisão do Mestre)

Próximo passo:
- Decidir: arquivar Mudança A e seguir para Mudança B (layout novo — onde o design do mockup aparece de verdade)
- Mudança B = criar `flownc/ui/components/` (header, compositor, program_list, resumo) + 2 colunas + `main_window.py` como maestro

Blockers:
- TTFs IBM Plex Sans / Mono não encontrados no sistema (fallback Segoe UI ativo)
- Rafael ficou surpreso que Mudança A não muda o layout — esclarecer que o design visível do mockup só aparece na Mudança B

Arquivos tocados:
- flownc/ui/theme.py (novo)
- flownc/ui/style.qss (novo)
- flownc/assets/fonts/.gitkeep (novo)
- flownc/app_paths.py (fonts_dir + qss_path)
- flownc/ui/main_window.py (_register_fonts + _apply_stylesheet)
- openspec/changes/redesign-fundacao-visual/ (todos os artefatos)
- openspec/changes/archive/2026-06-06-motor-contagem-e-publicacao/ (arquivado)

Retomar com: "continuar"
