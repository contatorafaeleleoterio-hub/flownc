## 1. Remover backup do topo

- [ ] 1.1 Remover `btn_backup`, `set_backup_path` e o sinal `backup_clicado` de `top_bar.py` (manter marca)
- [ ] 1.2 Em `main_window.py`, remover a ligação `self._top.backup_clicado` e os usos de `self._top.set_backup_path`

## 2. Estado "não configurado"

- [ ] 2.1 Em `main_window.py`, iniciar `self._backup_dir = ""` (sem caminho fake); preencher só a partir de `settings.backup_dir`/`output_dir` quando existir
- [ ] 2.2 Persistir a última pasta escolhida em `settings` para vir preenchida no próximo uso (se o `settings_store` suportar)

## 3. Controle de backup na tela Lote

- [ ] 3.1 Em `LoteScreen._build_right`, inserir controle sutil de backup no rodapé, entre `_facts` e o `_CtaButton`
- [ ] 3.2 Estados: "Definir pasta de backup" (não configurado) e caminho discreto + "trocar" (configurado)
- [ ] 3.3 Expor `set_backup_path(caminho)` e sinal `backup_solicitado`; ligar no `main_window` ao `_escolher_backup`

## 4. Guarda no CTA

- [ ] 4.1 No `main_window._on_conferir` (ou no clique do CTA), se `_backup_dir` estiver vazio, chamar `_escolher_backup()` antes de abrir o modal
- [ ] 4.2 Se o operador cancelar o seletor, abortar (não abrir a conferência); se escolher, seguir direto
- [ ] 4.3 Garantir que a habilitação do CTA (edições/programas) não muda — a guarda só dispara no clique

## 5. Testes e verificação

- [ ] 5.1 Atualizar `test_ui_smoke.py`: topo sem chip de backup; controle na tela Lote; estado "não configurado"; guarda abre o seletor ao executar sem backup
- [ ] 5.2 Rodar pytest (venv `flownc/.venv`), mypy e ruff — zero regressões
- [ ] 5.3 Smoke manual: abrir sem backup, montar lote, clicar "Conferir lote →" → seletor abre → escolher → conferência segue; reabrir e ver caminho preenchido
