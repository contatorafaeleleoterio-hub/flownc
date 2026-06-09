# Handoff — FlowNC — 2026-06-08 (sessão 8)
Status: EXE entregue na Área de Trabalho (pasta FlowNC/ no Desktop).

Feito nesta sessão:
- app_paths.py: resource_dir() via sys._MEIPASS (EXE) ou pasta do projeto (dev).
- core/seed.py: ensure_seed() — semeia data/ na 1ª execução, preserva corrompidos.
- main.py: ensure_seed() chamado antes de _load_library/_load_presets.
- FlowNC.spec: datas preenchidos (ui/style.qss, assets/fonts, data_default).
- dist/FlowNC/data/ copiado ao lado do EXE (editável pelo operador).
- EXE buildado: FlowNC.exe 1.8 MB, _internal/ com data_default/ui/assets.
- Pasta FlowNC/ entregue no Desktop; 146 testes verdes.

Onde parou: EXE funcional pronto para pen drive.
Próximos passos (opcionais — FASE 3 ainda incompleta):
  - Mudança C (editor: glifos, realce, stepbar) — Etapas 22–36.
  - Mudança D (modais, atalhos, confirmações) — Etapas 37–50.
  - Passo 8: persistência real de perfil (hoje é stub).
  - Passo 4: trocar _save() legado por publish_batch.
Blockers: nenhum.
Retomar com: "continuar mudança C" ou "entregar EXE com polimento".
