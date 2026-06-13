## Why

A logo aprovada do FlowNC (`docs/logo/logo FlowNC.jpeg`) é o wordmark "Flow NC" + uma **marca
gráfica**: três linhas horizontais decrescentes em degradê azul (ideia de "flow"). O wordmark já está
no topo (TopBar) e o ícone vira `flownc.ico` (janela/EXE). Mas o **topo do rail mostra um "ponto"
genérico** (`icon_pixmap("dot")`), sem identidade. Falta levar a marca da logo para o rail, fechando
a presença da identidade visual no app.

## What Changes

- **Marca "flow" no topo do rail:** substituir o `dot` pelo símbolo das **três linhas decrescentes**
  da logo, **desenhado via QPainter** em `ui/icons.py` (novo `kind="flowmark"`) — nada de bitmap no
  rail (lição registrada: PNG no rail vira quadradinho em alguns EXEs).
- Cor da marca seguindo o azul da identidade (a marca = azul; o laranja segue só para CTA), com
  tamanho/peso adequados ao rail (~56px de largura).

## Capabilities

### Modified Capabilities
- `rail-navegacao-4-telas`: o topo do rail passa a exibir a **marca FlowNC** (símbolo de linhas de
  flow desenhado), em vez de um ponto genérico.

## Impact

- **Código:** `flownc/ui/icons.py` (novo ícone `flowmark`), `flownc/ui/components/rail.py` (usar
  `icon_pixmap("flowmark", …)` no topo, na cor azul da marca).
- **Sem novos assets/arquivos:** a marca é vetorial (QPainter); a logo bitmap (`docs/logo`,
  `assets/logo`) e o gerador permanecem para o wordmark do topo e o `.ico`.
- **Contrato visual:** pequeno ajuste no rail; refletir no mockup v4/`CONTEXTO-IA` no follow-up
  visual junto das outras changes.
- **Testes:** `flownc/tests/test_ui_smoke.py` (rail instancia com a marca sem erro).
