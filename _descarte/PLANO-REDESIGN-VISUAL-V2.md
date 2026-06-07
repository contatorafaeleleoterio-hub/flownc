# Plano — Redesenho visual do FlowNC conforme o mockup v2

> **ESQUELETO INICIAL.** Só a estrutura (sessões → etapas) em nível básico, com as decisões estruturais já fechadas. Os detalhes de cada etapa serão refinados dentro da proposta OpenSpec de cada mudança.

## Contexto

A função nova de **editar arquivo por arquivo** já está pronta no app (atrás do botão "✎ Editar programa selecionado") e o EXE novo já foi gerado em `flownc/dist/FlowNC/`. O que **falta** é todo o **visual novo**: a tela do app ainda tem a cara antiga, enquanto o desenho aprovado (`mockups/painel-final.v2.html`) traz um layout repaginado em 2 colunas dinâmicas, lista única "Edições montadas", sistema de cores/fontes padronizado e o editor integrado com cara final.

Esse descompasso causou confusão: ao abrir o app "pronto", ele parecia o antigo, porque só a função foi entregue — o visual nunca foi construído.

**Objetivo:** deixar o app **idêntico ao mockup v2**, com a lógica atual (perfis, execução, verificações, biblioteca) preservada.

**Regra de trabalho:** na hora de implementar, sai **pronto conforme o mockup** — sem ir mostrando pedaço por pedaço. O trabalho é dividido em **sessões**; cada sessão é um bloco completo e testável; cada sessão tem **etapas**.

## Referências

- **Alvo (desenho):** `mockups/painel-final.v2.html` + `docs/PLANO-MOCKUP-V2-EDITOR.md` + `docs/PLANO-DESIGN-SYSTEM.md` + `mockups/PROMPT-CLAUDE-DESIGN.md`
- **Código atual:** `flownc/ui/main_window.py` (monolítico, ~968 linhas, sem tema, cores fixas no código) · `flownc/ui/editor_panel.py` (editor já funcional)
- **Já pronto:** editar por arquivo · **Falta:** todo o visual.

## Decisões estruturais (fechadas)

1. **Componentes separados:** quebrar a janela única em arquivos próprios sob `flownc/ui/components/` (ex.: `header.py`, `compositor.py`, `program_list.py`, `resumo.py`, mais o `editor_panel.py` que já existe). A `MainWindow` vira o "maestro" que junta os componentes e segura a lógica.
2. **Fluxo OpenSpec:** antes de codar, criar uma *change* formal (proposta + specs + tarefas), seguindo o padrão do projeto (uma mudança por vez).
3. **Dividido em 3 mudanças OpenSpec sequenciais** (abaixo).

## Divisão em 3 mudanças OpenSpec (sequenciais)

Cada mudança passa pelo fluxo completo (propor → implementar → arquivar) e é testada antes de começar a próxima.

| Mudança | O que entrega | Sessões |
|---|---|---|
| **A — Fundação visual** | Sistema de cores/fontes/tema (tokens do mockup) aplicado ao app, sem mudar o layout ainda | Sessão 1 |
| **B — Layout e painéis** | Header + 2 colunas dinâmicas + coluna esquerda + coluna direita, já com a cara do mockup | Sessões 2, 3, 4 |
| **C — Editor, limpeza e entrega** | Editor com cara final + remoções do v2 + integração + EXE novo na Área de Trabalho | Sessões 5, 6, 7 |

Cada mudança começa pela **Sessão 0 (proposta OpenSpec)**.

---

## Sessões (esqueleto)

### Sessão 0 — Proposta OpenSpec (repete no início de cada mudança A/B/C)
- 0.1 Criar a *change* (proposta + specs do escopo + tarefas)
- 0.2 Validar a proposta antes de implementar

### Sessão 1 — Fundação visual (sistema de cores/fontes em Qt) → Mudança A
- 1.1 Criar módulo de tema com os tokens do mockup (cores, tipografia, espaçamentos, cantos, alturas)
- 1.2 Carregar fontes IBM Plex Sans / IBM Plex Mono
- 1.3 Criar folha de estilo central (QSS) aplicada ao app inteiro
- 1.4 Aplicar a base na janela (fundos em camadas, bordas, sombra)

### Sessão 2 — Esqueleto da janela (estrutura 2 colunas dinâmicas) → Mudança B
- 2.1 Header fixo: logo FlowNC + título + dropdown de máquina + botões de biblioteca
- 2.2 Corpo em 2 colunas (esquerda / direita)
- 2.3 Proporção dinâmica 60/40 ↔ 40/60 ao entrar/sair do modo edição (transição suave)
- 2.4 Rodapé / barra de estado

### Sessão 3 — Coluna esquerda → Mudança B
- 3.1 Painel "Configurações" (compositor): dropdowns de código origem → destino
- 3.2 Lista única "Edições montadas" (empilhada, com a linha em rascunho no fim)
- 3.3 Botão "+ adicionar outra edição"
- 3.4 Painel "Seleção de Programas": lista de arquivos com checkbox + botão "✎ Editar" por arquivo

### Sessão 4 — Coluna direita (Resumo) → Mudança B
- 4.1 Selo de estado (⚠ conflito / ✓ pronto)
- 4.2 Contadores (Regras / Programas / Alterações)
- 4.3 Cartões de regra (editar ⧉ duplicar 🗑 excluir + destaque de conflito)
- 4.4 Bloco "Editados → backup"
- 4.5 Botão principal "Executar Lote"

### Sessão 5 — Editor integrado (cara final do mockup) → Mudança C
- 5.1 Cabeçalho com nome do arquivo + aviso discreto "salva direto, sem cópia"
- 5.2 Toolbar do localizador: dropdown da biblioteca + lupa + contador + setas + "Substituir todos / Um a um"
- 5.3 Editor com numeração de linha + realce de ocorrências (atual vs. demais)
- 5.4 Alternância Resumo ↔ Editor na coluna direita

### Sessão 6 — Limpeza do v2 (remoções) → Mudança C
- 6.1 Remover contagem automática de ocorrências
- 6.2 Remover redundâncias: faixa de conflito extra, subtítulo do header, indicador circular
- 6.3 Padronizar espaçamentos/cantos/fontes (eliminar valores soltos antigos)

### Sessão 7 — Integração, build e entrega → Mudança C
- 7.1 Garantir que a lógica antiga segue intacta (perfis, execução, verificações, biblioteca)
- 7.2 Rodar testes (pytest) + checagens (mypy, ruff)
- 7.3 Smoke test manual comparando lado a lado com o mockup
- 7.4 Rebuild do EXE + cópia limpa na Área de Trabalho + afastar a versão antiga

---

## A refinar na próxima rodada
- Ordem e granularidade das sessões/etapas
- Detalhar cada etapa (o que exatamente muda, em qual arquivo/componente)
- Nomes definitivos dos componentes em `flownc/ui/components/`

## Verificação (preliminar)
- `pytest` (121+ testes) + `mypy` + `ruff` verdes
- Smoke manual: abrir app, conferir cada tela contra o mockup, editar um arquivo, executar um lote
- Rebuild do EXE e abrir pra confirmar
