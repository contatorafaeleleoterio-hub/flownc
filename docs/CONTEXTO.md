# Contexto Atual

## Estado confirmado

- Projeto desktop Windows em Python 3.11+, com CLI e GUI PySide6.
- Núcleo `core/` está estável e coberto por testes.
- Baseline verificada em 2026-06-04: `106 passed`.
- Existe EXE funcional antigo preservado em `flownc/dist` até o smoke do novo `FlowNC.exe`.
- O repositório Git foi inicializado em 2026-06-04 com baseline antes do rebrand.

## Situação do produto

O produto já saiu do modelo antigo baseado em abas por programa e convergiu para uma dinâmica "por código", com composição de regras, seleção de programas e resumo dominante. O layout vigente é o de 2 colunas com resumo forte; qualquer referência antiga a 3 colunas vale apenas como histórico de evolução.

## Situação da documentação

Antes desta consolidação, a documentação estava espalhada entre handoff, PRDs, análises, planos intermediários e mockups antigos. A estrutura em `docs/` passa a ser a fonte principal, enquanto o restante vai para `_descarte/` com índice rastreável.

## Próximos passos imediatos

1. Gerar `dist/FlowNC/FlowNC.exe`.
2. Fazer smoke test do novo executável.
3. Após smoke OK, remover o `dist` antigo e fechar o commit final.
