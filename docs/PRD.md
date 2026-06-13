# PRD

## Resumo

FlowNC é um app desktop Windows para edição em lote de programas CNC: substituição de códigos por regras (origem → destino), inserção de blocos, edição manual por arquivo num editor integrado, conferência com números reais e publicação segura com backup versionado dos originais. O design de referência é o mockup aprovado `mockups/painel-final.v4.html` (aprovado em 2026-06-11); qualquer layout anterior (incluindo o v2) está descartado. A descrição completa de telas, fluxos e regras está em `docs/CONTEXTO-IA.md` (fonte central).

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

## Dinâmica de UI (mockup v4)

- **Navegação por 4 telas fixas** numa barra lateral (rail): **Lote · Editor · Códigos · Histórico**. O item ativo tem filete laranja; o Editor ganha bolinha laranja quando há alteração não salva.
- **Topo global** (visível em todas as telas): seletor de configuração ("receita"), com "💾 Salvar lote atual como…", e chip da pasta de backup (clicável para trocar).
- **Tela Lote (principal):** duas colunas — **Programas** (lista com checkbox, `✎ Abrir`, `✕`, arrastar-e-soltar) e **Lote de edições** (compositor com **abas "Trocar código" / "➕ Inserir bloco"** e um único `+ Adicionar ao lote`; cartões numerados com editar/duplicar/excluir; CTA laranja **"Conferir lote →"**).
- **Conferência → Publicação:** o modal "Conferência do lote — números reais" varre os arquivos e mostra o que mudaria (nada grava); a publicação faz backup versionado + gravação + dupla conferência SHA-256, com barra de progresso.
- **Tela Editor:** ajustes finos por arquivo; localizador com **contagem automática** (sem botão de varredura), substituir todos / um a um, inserir bloco, salvar direto (com Desfazer) e "Salvar como…".
- **Tela Códigos:** biblioteca código + descrição (com bloco opcional = modelo reutilizável), que alimenta todos os dropdowns.
- **Tela Histórico:** uma linha por publicação com "↩ Restaurar originais".

## Decisões funcionais consolidadas

- A ação separada `Retirar` foi **descartada**: remoção de código é feita por substituição-por-vazio dentro do mesmo fluxo de regras.
- Remoção que esvazia a linha apaga a linha; espaços remanescentes são normalizados.

## Estado

Interface v4 portada para o app e **aprovada pelo Mestre (Fase 2, 64/64)** via change OpenSpec `plano-execucao-mockup-v4`; EXE portátil gerado. Estado vivo em `PLAN.md` (raiz) e `HANDOFF.md`. Próxima frente: monetização/distribuição (ver `docs/MONETIZACAO.md` e `docs/PAGINA-DE-VENDAS.md`).
