# Produto

## Direção atual

FlowNC é uma ferramenta para preparar lotes de programas CNC com segurança operacional. O fluxo é orientado por códigos e regras (origem → destino), complementado por um editor integrado por arquivo para ajustes manuais pontuais — não por edição dispersa arquivo a arquivo.

## Núcleo da dinâmica (tela Lote)

1. Carregar os programas NC (botão ou arrastar-e-soltar) e **marcar** os que vão receber as edições.
2. No compositor, montar a edição numa das **abas**: "Trocar código" (origem → destino, ou remover) ou "➕ Inserir bloco"; mandar ao lote com `+ Adicionar ao lote`.
3. Empilhar quantas edições precisar — cada uma vira um **cartão numerado** (com editar/duplicar/excluir); conflitos aparecem em âmbar.
4. **Conferir lote →**: o modal mostra os **números reais** (o que muda, onde, quantas vezes) — nada é gravado.
5. **Publicar:** backup versionado dos originais → gravação na pasta original → dupla conferência SHA-256, com barra de progresso e resumo final.

Para ajustes pontuais fora das regras, o operador abre o **editor por arquivo** (`✎ Abrir` ou a tela Editor): localizador com **contagem automática**, navegação i/N, substituir todos / um a um, inserir bloco e salvamento direto (com Desfazer).

## Princípios de produto

- O original nunca pode se perder (backup versionado no lote; o editor por arquivo salva direto, sem cópia, por escolha consciente para ajuste rápido).
- O operador precisa entender o impacto antes de executar.
- Regras de substituição são operações explícitas; remoção é substituição-por-vazio (a ação separada `Retirar` foi descartada).
- Conflitos e zero-ocorrências precisam aparecer como feedback útil, não como surpresa tardia.

## Interface vigente

O mockup vigente e **único válido** é `mockups/painel-final.v4.html` (aprovado em 2026-06-11). A descrição detalhada de telas, fluxos e regras está em `docs/CONTEXTO-IA.md` (fonte central). O v4 organiza o app em **4 telas fixas num rail**:

- **Lote** (principal): Programas + Lote de edições (compositor com abas, conferência com números reais, publicação segura);
- **Editor:** ajustes finos por arquivo, com contagem automática;
- **Códigos:** biblioteca código + descrição que alimenta todos os dropdowns;
- **Histórico:** publicações com "↩ Restaurar originais".

## Layout

Rail (barra lateral escura) + topo global (seletor de configuração + chip de backup) + área da tela ativa. O v2 (2 colunas dinâmicas), o conceito de 3 colunas e o `painel-final.html` estão **descartados** — só histórico em `_descarte/`, nunca referência de implementação.
