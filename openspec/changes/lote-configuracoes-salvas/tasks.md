## 1. Armazenamento de configurações

- [ ] 1.1 Adicionar `configs_dir()` em `app_paths.py` (diretório de dados compartilhado da aplicação)
- [ ] 1.2 Criar `core/config_store.py`: `save_config(nome, edicoes)`, `load_config(nome)`, `list_configs()`, `config_exists(nome)` — serializa `Edicao` (swap + ins) em JSON via `json_store`, **omitindo `programas`**
- [ ] 1.3 Testes do `config_store` (round-trip swap + ins; lista; sobrescrever)

## 2. Remover seletor do topo

- [ ] 2.1 Remover `cb_receita`, `ITEM_SALVAR`, `set_receitas`, sinais `receita_alterada`/`salvar_receita_solicitado` de `top_bar.py` (manter marca + chip de backup)
- [ ] 2.2 Em `main_window.py`, remover as ligações e os métodos `_on_receita_alterada`/`_on_salvar_receita` ligados ao topo (migram para a tela Lote)

## 3. Botões de configuração na tela Lote

- [ ] 3.1 Em `LoteScreen._build_right`, adicionar "Abrir configuração" e "Salvar configuração" (ghost) na linha do título "Lote de edições"
- [ ] 3.2 "Salvar configuração": input de nome + Salvar/Cancelar; chama `config_store.save_config` com `self._edicoes` sem programas; confirma sobrescrever se nome existe
- [ ] 3.3 "Abrir configuração": lista os nomes salvos; ao escolher, `set_edicoes` com as edições carregadas (0 programas); confirma se já há lote montado

## 4. Aplicar aos marcados

- [ ] 4.1 Adicionar botão "Aplicar aos marcados" na tela Lote (perto do CTA ou do título)
- [ ] 4.2 Habilitar só com ≥1 edição sem programas e ≥1 programa marcado; tooltip explica o que falta
- [ ] 4.3 Ao clicar, preencher `programas` das edições sem programas com os marcados atuais (via `replace`); re-render e refresh do CTA

## 5. Testes e verificação

- [ ] 5.1 Atualizar `test_ui_smoke.py`: topo sem seletor; botões na tela Lote; salvar/abrir; "Aplicar aos marcados"
- [ ] 5.2 Rodar pytest (venv `flownc/.venv`), mypy e ruff — zero regressões
- [ ] 5.3 Smoke manual: salvar "Mudar ponto zero" (G54→G55 + M8→M9), limpar, abrir, marcar programas, aplicar aos marcados, conferir
