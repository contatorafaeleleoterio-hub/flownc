## 1. Ícone da marca

- [ ] 1.1 Adicionar `kind="flowmark"` em `flownc/ui/icons.py`: três linhas horizontais arredondadas, larguras decrescentes (~100%/70%/45%), alinhadas à direita, espaçamento uniforme
- [ ] 1.2 Conferir renderização em tamanhos pequenos (18–24px)

## 2. Aplicar no rail

- [ ] 2.1 Em `flownc/ui/components/rail.py`, trocar `icon_pixmap("dot", 18, …)` por `icon_pixmap("flowmark", …)` na cor azul da identidade
- [ ] 2.2 Ajustar tamanho/centralização no topo do rail

## 3. Verificação

- [ ] 3.1 Smoke `test_ui_smoke.py`: rail instancia com a marca sem erro
- [ ] 3.2 pytest + mypy + ruff (venv `flownc/.venv`) — zero regressões
- [ ] 3.3 Conferência visual: marca aparece no topo do rail, legível no fundo escuro
