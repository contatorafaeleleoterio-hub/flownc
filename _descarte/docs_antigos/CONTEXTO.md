# Contexto Atual

> 🟠 **ATUALIZAÇÃO 2026-06-11 — DESIGN ALVO MUDOU PARA O MOCKUP v4.**
> O Mestre aprovou `mockups/painel-final.v4.html` como **contrato visual** do app.
> Linhagem: v2 (aprovado 2026-06-05) → v3 (redesign 2026-06-10: rail com 4 telas
> Lote/Editor/Códigos/Histórico, "Conferir lote" com varredura real, Histórico com restaurar,
> inserir bloco em lote) → **v4 (refinamento aprovado 2026-06-11)**: compositor único com abas
> (trocar código / inserir bloco, um só botão "+ Adicionar ao lote"), Salvar no cabeçalho do
> editor, conferência com total em destaque + zeros recolhidos + "Publicar mesmo assim" em
> conflito, topo sem ação duplicada + confirmação ao carregar receita com lote montado,
> contagem automática no editor; mais 3 correções de honestidade (conferência simula o pipeline
> encadeado da publicação; duplicar clona a edição inteira; bloco sem âncora não insere no fim
> do arquivo). **Referências a v2/v3 como "alvo" neste documento e no PLAN.md valem só como
> histórico.** Descrição completa do v4 (telas, fluxos, interatividade, regras de negócio):
> **`docs/CONTEXTO-IA.md`** — documento central, autossuficiente, para qualquer agente/IA.

## Termos adotados (2026-06-06)

- **Plano de execução / plano de implementação:** criação de um documento com as etapas necessárias para executar uma solução já decidida. Vale para qualquer pedido de "plano", seja qual for o nome usado (stack, roteiro, documento etc.).
- **Implementação:** colocar a solução em funcionamento, executando o plano definido (por documentos, código, reprogramação ou reconstrução do zero — a forma não importa).
- **"Implementar o design":** refere-se **exclusivamente ao novo design aprovado** (`mockups/painel-final.v2.html`).
- **Design antigo: descartado.** Não é mais referência para nada. Menções a layouts antigos (incl. `painel-final.html` e o conceito de 3 colunas) valem só como histórico.
- Plano de execução vigente: **`PLAN.md`** (raiz do projeto). Estado entre sessões: **`HANDOFF.md`** (raiz).

## Estado confirmado

- Projeto desktop Windows em Python 3.11+, com CLI e GUI PySide6.
- Núcleo `core/` está estável e coberto por testes.
- Baseline: `106 passed` (2026-06-04) → `121 passed` (2026-06-05, após `editor-integrado-por-arquivo`) → **`146 passed` (2026-06-07)** após `motor-contagem-e-publicacao` + `redesign-fundacao-visual`. Usar o venv `flownc/.venv` (PySide6 6.11.1).
- Existe EXE funcional antigo preservado até o smoke do novo `FlowNC.exe`.
- Repositório Git inicializado em 2026-06-04 com baseline antes do rebrand.

## Editor integrado por arquivo — IMPLEMENTADO E ARQUIVADO (2026-06-05)

Mudança OpenSpec `editor-integrado-por-arquivo` implementada:

- **`core/inplace_save.py`** — `salvar_no_lugar`: gravação in-place sem backup, atômica, com preflight de codificação e conferência SHA-256. Preserva encoding/BOM/EOL.
- **`ui/editor_panel.py`** — `EditorPanel` (editor mono com numeração de linha) + localizador que reusa `matcher.find_matches` (mesma borda CNC do Lote): varredura/contagem sem mover cursor, navegação i/N circular, substituir todos / um a um. Lógica de busca/substituição em funções puras testáveis.
- **`ui/main_window.py`** — botão "✎ Editar" por programa; área da direita virou `QStackedWidget` (Resumo ↔ editor); guarda de não-salvo.
- O `QPlainTextEdit` usa `\n` interno; o EOL real (CRLF) é reaplicado só na gravação, preservando byte-a-byte (travado por teste de regressão).

## Motor de contagem e publicação — IMPLEMENTADO E ARQUIVADO (2026-06-06)

Mudança OpenSpec `motor-contagem-e-publicacao` (a parte "Retirar" foi removida do plano — remoção já funciona via substituição-por-vazio):

- **`core/models.py`, `core/scan.py`:** `ScanResult`, `Issue`, `count_occurrences` com boundary CNC.
- **`core/batch.py`:** `validate_batch` — detecta conflito de regra (≥2 regras no mesmo código de origem).
- **`core/publisher.py`, `core/settings_store.py` v2:** `publish_batch` — backup versionado por data/hora, troca atômica, dupla conferência SHA-256; settings migrado v1→v2 com `working_dir`/`backup_dir`.

## Situação do produto

O produto convergiu para a dinâmica "por código" (composição de edições em lote, seleção de programas, conferência real antes de publicar) + editor integrado por arquivo. O **design alvo é exclusivamente o mockup v4** (`mockups/painel-final.v4.html`, aprovado 2026-06-11); v2/v3 e qualquer layout anterior estão **descartados como alvo** (ver atualização no topo).

## Situação da documentação

A estrutura em `docs/` é a fonte principal; planos intermediários e mockups antigos foram movidos para `_descarte/` com índice rastreável. O plano de execução único e vivo é `PLAN.md` (raiz).

## Próximos passos imediatos

### Prioridade 1 — Redesign visual conforme o mockup v2 (plano ativo)

O mockup v2 está aprovado e o editor integrado já existe. Falta **portar o visual v2 para o app Qt** e fechar as divergências de fidelidade. Plano vivo: **`PLAN.md`** (raiz).

OpenSpec em **3 mudanças sequenciais**:
- **A — `redesign-fundacao-visual`:** tokens (cores/fontes/espaçamentos) + tema/QSS. **Arquivada (2026-06-06).**
- **B — `redesign-layout-principal`:** header + 2 colunas dinâmicas (60/40 ↔ 40/60) + coluna esquerda (Configurações + Edições montadas) + coluna direita (Resumo). **Em implementação (37/38 tarefas).**
- **C — editor/limpeza/entrega:** editor com cara final + remoções do v2 (contagem automática fora do editor, redundâncias) + EXE novo. **A propor.**

### Prioridade 2 — Gate do executável (não bloqueante)

`dist/FlowNC/FlowNC.exe` existe mas ainda com pendências de empacotamento (ver lacunas no `PLAN.md`: `FlowNC.spec datas=[]`, fontes IBM Plex, seed Fanuc). Smoke manual, entrega de cópia limpa na Área de Trabalho e afastamento da versão antiga ficam para o **fim do redesign**.
