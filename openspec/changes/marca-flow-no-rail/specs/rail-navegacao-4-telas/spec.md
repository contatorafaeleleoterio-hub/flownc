## MODIFIED Requirements

### Requirement: Rail lateral com 4 botões-lugar

O sistema SHALL exibir um rail lateral escuro (cor de fundo `COLOR_RAIL`) fixo à esquerda da janela principal, com 4 botões verticais: **Lote**, **Editor**, **Códigos**, **Histórico**. O botão ativo SHALL ter um filete laranja (`COLOR_CTA`) na borda esquerda. O rail SHALL ter largura fixa (~56px). No topo do rail, acima dos botões, o sistema SHALL exibir a **marca FlowNC** — o símbolo de linhas de "flow" (três linhas horizontais decrescentes), **desenhado via QPainter** (não bitmap), na cor azul da identidade.

#### Scenario: Botão ativo com filete laranja

- **WHEN** a tela Lote está ativa
- **THEN** o botão "Lote" no rail exibe o filete laranja e os demais botões não têm filete

#### Scenario: Clicar em botão muda tela ativa

- **WHEN** o usuário clica em "Histórico" no rail
- **THEN** a área principal exibe a tela Histórico e o filete laranja move para o botão "Histórico"

#### Scenario: Marca FlowNC no topo do rail

- **WHEN** o rail é exibido
- **THEN** o topo mostra a marca de linhas de "flow" (desenhada via QPainter), não um ponto genérico
