# Produto

## Direção atual

FlowNC é uma ferramenta para preparar lotes de programas CNC com segurança operacional. O fluxo é orientado por códigos e regras (origem → destino), complementado por um editor integrado por arquivo para ajustes manuais pontuais — não por edição dispersa arquivo a arquivo.

## Núcleo da dinâmica

1. Escolher ou montar regras por código (compositor origem → destino).
2. Empilhar as edições na lista "Edições montadas" (com rascunho "em edição" e `+ adicionar outra edição`).
3. Selecionar os programas que receberão as regras e mandar ao lote (`Adicionar edição ao lote →`).
4. Revisar um resumo dominante (selo de estado, contadores, cartões de regra, conflitos).
5. Publicar com segurança e manter backup versionado dos originais (troca atômica + conferência SHA-256).

Para ajustes pontuais fora das regras, o operador abre o **editor integrado por arquivo** (`✎ Editar`): localizador com varredura/contagem, navegação i/N, substituir todos / um a um e salvamento direto.

## Princípios de produto

- O original nunca pode se perder (backup versionado no lote; o editor por arquivo salva direto, sem cópia, por escolha consciente para ajuste rápido).
- O operador precisa entender o impacto antes de executar.
- Regras de substituição são operações explícitas; remoção é substituição-por-vazio (a ação separada `Retirar` foi descartada).
- Conflitos e zero-ocorrências precisam aparecer como feedback útil, não como surpresa tardia.

## Interface vigente

O mockup vigente e **único válido** é `mockups/painel-final.v2.html` (design aprovado). Ele privilegia:

- composição de regras na coluna esquerda (Configurações + Edições montadas);
- seleção de programas com editor por arquivo acessível por linha;
- resumo forte do lote na coluna direita, que dá lugar ao editor integrado quando acionado.

A contagem de ocorrências **não** aparece no painel principal: é função do editor (varredura sob demanda).

## Layout

Duas colunas dinâmicas: ~60/40 no modo padrão e ~40/60 quando o editor está aberto (a coluna direita expande), com transição suave. O conceito antigo de 3 colunas e o mockup `painel-final.html` estão **descartados** — permanecem apenas como histórico de evolução, nunca como referência de implementação.
