## 1. Modelo: programas por edição

- [ ] 1.1 Adicionar campo `programas: tuple[str, ...] = ()` à dataclass `Edicao` (`compositor_v4.py`); confirmar que `duplicada()`/`replace` preservam o conjunto
- [ ] 1.2 Em `CompositorV4._montar_edicao`, injetar `programas=tuple(str(p) for p in self._marcados)` nas duas abas (swap e ins)
- [ ] 1.3 Em `CompositorV4._refresh_add`, exigir `len(self._marcados) >= 1` para habilitar "+ Adicionar ao lote"; tooltip "Marque ao menos 1 programa" quando faltar

## 2. Cartão de edição (lote_screen.py)

- [ ] 2.1 Em cartões de troca, substituir a fórmula estática por dois `LibDropdown` pequenos (origem; destino com `com_remover=True`); `alterado` atualiza a edição via `replace` em `self._edicoes[i]` + re-render
- [ ] 2.2 Manter o resumo textual + ✎→compositor apenas para edições de bloco (`ins`)
- [ ] 2.3 Substituir o ✎ separado por um controle **"N programas ▾"** (clicável) na ponta direita; manter ⧉ duplicar e ✕ excluir
- [ ] 2.4 Estado de aviso no cartão quando `programas` ficar vazio

## 3. Dropdown de programas por edição + desfazer

- [ ] 3.1 Criar popup `_ProgramasPopup` (padrão de `LibDropdown._abrir_popup`): uma linha por programa (nome mono + ✕)
- [ ] 3.2 ✕ risca a linha e troca por "desfazer"; "desfazer" restaura
- [ ] 3.3 Ao fechar o popup, remover do conjunto da edição os itens riscados não desfeitos; atualizar a edição via `replace` e a contagem do cartão

## 4. Painel Programas (program_list_v4.py)

- [ ] 4.1 Adicionar botão ghost "Desmarcar selecionados" no cabeçalho, ao lado de "Marcar todos"
- [ ] 4.2 Habilitar só com ≥1 marcado; ao clicar, chamar `desmarcar_todos()`

## 5. CTA Conferir + facts

- [ ] 5.1 `LoteScreen._refresh_cta`: habilitar só com ≥1 edição e toda edição com ≥1 programa; tooltip explica edição sem programas
- [ ] 5.2 Atualizar o texto de facts do rodapé para refletir edições e total de programas por edição

## 6. Conferência por edição (main_window + modal)

- [ ] 6.1 `main_window._on_conferir`: montar, por edição, o mapa nome→texto só dos `ed.programas` (em vez de `get_marcados()` global)
- [ ] 6.2 Ajustar `scan_lote`/`ConferenciaModal` para aplicar cada edição apenas ao conjunto dela; manter `programas_texto` para leitura
- [ ] 6.3 Atualizar os cartões/contagens da conferência para usar o conjunto por edição

## 7. Testes e verificação

- [ ] 7.1 Atualizar `test_ui_smoke.py`: `Edicao` com `programas`, cartões com contagem, "Desmarcar selecionados", habilitação por escopo
- [ ] 7.2 Atualizar testes de conferência para o escopo por edição
- [ ] 7.3 Rodar pytest (venv `flownc/.venv`), mypy e ruff — zero regressões
- [ ] 7.4 Smoke manual na tela Lote (adicionar 2 edições com escopos diferentes, remover programa com desfazer, desmarcar, conferir)
