## Context

`ui/icons.py` desenha ícones vetoriais via QPainter (`icon_pixmap(kind, size, color)`); `rail.py`
usa `icon_pixmap("dot", 18, theme.COLOR_WHITE)` no topo. A logo tem um símbolo de três linhas
horizontais decrescentes (degradê azul). Lição registrada: ícone no rail deve ser desenhado, não
bitmap (PNG quebra em alguns EXEs).

## Goals / Non-Goals

**Goals:** marca da logo (linhas de flow) no topo do rail, vetorial, na cor azul da identidade.
**Non-Goals:** não trocar o wordmark do topo nem o `.ico`; não criar assets novos.

## Decisions

**1. Novo `kind="flowmark"` em `icon_pixmap`.** Três linhas horizontais arredondadas, larguras
decrescentes (ex.: 100%/70%/45% da largura útil), alinhadas à direita, espaçamento uniforme —
espelhando o símbolo da arte. Usa o `pen` arredondado já existente.

**2. Cor.** Azul da marca (token de identidade; se não houver um específico, usar um `COLOR_*` azul
do tema). O laranja continua reservado a CTA. Como `icon_pixmap` recebe uma cor sólida, a marca no
rail fica numa cor azul sólida (não degradê) — suficiente e coerente no fundo escuro do rail.

**3. Tamanho.** Compatível com a largura do rail (~56px): símbolo ~22–24px, centralizado no topo
como o `dot` é hoje.

## Risks / Trade-offs

- **Sem degradê** (QPainter sólido) → aceitável; o rail é estreito e escuro, o sólido lê bem.
  Degradê via `QLinearGradient` é possível depois se o Mestre quiser.

## Open Questions

- Token de cor azul exato da marca — usar o já existente no tema; confirmar no ajuste fino visual.
