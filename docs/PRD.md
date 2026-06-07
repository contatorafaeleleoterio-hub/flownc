# PRD

## Resumo

FlowNC é um app desktop Windows para edição em lote de programas CNC: substituição de códigos por regras (origem → destino), edição manual por arquivo num editor integrado, preview, verificações fortes e publicação segura com backup versionado dos originais. O design de referência é o mockup aprovado `mockups/painel-final.v2.html`; qualquer layout anterior está descartado.

## Escopo atual validado

- Motor de substituição seguro com testes automatizados (boundary CNC: `M8` ≠ `M80`).
- Leitura e escrita preservando encoding/BOM/EOL e estrutura do arquivo.
- Editor integrado por arquivo (estilo Bloco de Notas): localizador com varredura/contagem, navegação i/N, substituir todos / um a um, salvamento in-place atômico com conferência SHA-256.
- Varredura, validação de lote e publicação segura com backup versionado e troca atômica (`core/scan.py`, `core/batch.py`, `core/publisher.py`).
- Presets, biblioteca e configurações persistidas em JSON.
- GUI PySide6 funcional para operação local; EXE portátil onedir para Windows.

## Requisitos permanentes

- Preservação do original (backup versionado por data/hora; o editor por arquivo salva direto, sem cópia, por design — ajuste manual rápido).
- Operação rastreável por log.
- Validação forte antes de salvar/publicar.
- Comportamento previsível para zero ocorrências, conflitos e batchs mistos.

## Dinâmica de UI (mockup v2)

- **Duas colunas dinâmicas:** ~60/40 no modo padrão; ao abrir o editor a coluna direita expande para ~60% (~40/60), com transição suave.
- **Coluna esquerda:** ① Configurações (compositor origem → destino + lista única "Edições montadas" com rascunho "em edição" e `+ adicionar outra edição`) e ② Seleção de Programas (lista com checkbox e botão `✎ Editar` por linha, CTA `Adicionar edição ao lote →`).
- **Coluna direita:** ③ Resumo (selo de estado, contadores, cartões de regra com ações editar/duplicar/excluir, selo "Editados → backup", CTA "Executar Lote") ↔ Editor integrado.
- **Sem contagem automática no painel principal:** a varredura/contagem de ocorrências passou a ser função exclusiva do editor.

## Decisões funcionais consolidadas

- A ação separada `Retirar` foi **descartada**: remoção de código é feita por substituição-por-vazio dentro do mesmo fluxo de regras.
- Remoção que esvazia a linha apaga a linha; espaços remanescentes são normalizados.

## Em andamento

Redesign visual do app para fidelidade ao mockup v2, via OpenSpec em mudanças sequenciais (fundação visual → layout/painéis → editor/limpeza/entrega). Estado vivo em `PLAN.md` (raiz) e `HANDOFF.md`.
