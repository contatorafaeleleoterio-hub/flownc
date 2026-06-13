## Why

O mockup v4 foi aprovado como contrato visual definitivo do FlowNC em 2026-06-11, substituindo o v2. O v4 introduz mudanças estruturais que invalidam o plano anterior: rail de navegação com 4 telas fixas (Lote · Editor · Códigos · Histórico), compositor com duas abas (Trocar código / Inserir bloco), modal de Conferência com contagem honesta, telas dedicadas para Códigos e Histórico, e configuração global por receita. A change `redesign-fase2-fidelidade-visual` foi gerada contra o v2 e não cobre essas mudanças — este plano define a execução completa da FASE 2 (porte visual fiel ao v4, sem lógica nova) e da FASE 3 (ligar backend ao novo layout).

## What Changes

- **Rail de navegação:** substituir a janela de 2 colunas por uma estrutura rail + área de tela ativa; rail escuro com 4 botões-lugar (Lote, Editor, Códigos, Histórico) e filete laranja no ativo; bolinha laranja no botão Editor quando há alteração não salva.
- **Topo global:** barra de topo presente em todas as telas com seletor de configuração/receita (dropdown com "💾 Salvar lote atual como…") e chip de backup (mostra pasta, clica para trocar).
- **Tela Lote — Programas:** painel esquerdo com lista de arquivos, checkbox, botão "✎ Abrir", ✕ por linha, marcação visual (fundo verde / esmaecido), botão "Marcar todos / Desmarcar todos", "chip N de M marcados", "+ Adicionar programa(s)…", arrastar-e-soltar e estado vazio com CTA.
- **Tela Lote — Compositor com abas:** substituir compositor atual por versão com duas abas: aba "Trocar código" (dois dropdowns pesquisáveis com busca + "★ Frequentes", opção "✕ Remover") e aba "➕ Inserir bloco" (textarea, posição ancorada, modelos salvos, prévia real do primeiro programa). Um único botão "+ Adicionar ao lote" abaixo das abas; proteção: só habilita com origem e destino escolhidos.
- **Tela Lote — Lista de edições:** cartões numerados com tipo (troca ou bloco), ações (✎ editar / ⧉ duplicar / ✕ excluir), destaque âmbar para conflitos, chip "⚠ N conflitos". CTA laranja "Conferir lote →" no rodapé com subtítulo explicativo.
- **Modal Conferência:** abre ao clicar "Conferir lote"; mostra total de alterações (faixa verde/âmbar), avisos de conflito/sem-efeito, cartão por edição (total + programas afetados + exemplo real linha original → linha nova), linha de backup, rodapé fixo com botão "Publicar". **BREAKING:** a publicação agora passa obrigatoriamente pela Conferência — o fluxo antigo de publicar direto é removido.
- **Modal Publicação:** barra de progresso com etapas (backup → gravação → conferência SHA-256), resultado com caminho do backup, botões "Ver no Histórico" e "OK — novo lote".
- **Tela Editor:** restruturar como tela cheia com faixa de arquivos à esquerda (todos os programas carregados; bolinha laranja em arquivo com alteração); cabeçalho "Editando `NOME.NC`" + aviso "⚠ salva direto, sem cópia" + botões "Salvar como…" / "Salvar" (verde); toolbar em 3 grupos (localizar com contagem automática / substituir / inserir bloco); toast "Desfazer" após salvar.
- **Tela Códigos:** nova tela (não modal) com lista código + descrição, busca, contador, "+ Adicionar código" (código, descrição, bloco opcional), tag "bloco" nos códigos com bloco.
- **Tela Histórico:** nova tela com uma linha por publicação (quando, resumo, caminho backup, configuração ativa), botão "↩ Restaurar originais" por linha (com confirmação e novo backup dos atuais antes de restaurar).
- **Fundação visual v4:** paleta "Precisão Laranja" — laranja #E85D04 como CTA, fundo cinza-azulado, topo/rail azul-ardósia escuro; sincronizar `theme.py` e `style.qss` com as variáveis CSS do v4.

## Capabilities

### New Capabilities

- `rail-navegacao-4-telas`: Estrutura de janela com rail lateral e 4 telas fixas (Lote, Editor, Códigos, Histórico) gerenciadas por QStackedWidget; ativa filete laranja no item atual; bolinha de status no botão Editor.
- `topo-global-configuracao`: Barra de topo persistente em todas as telas com seletor de configuração/receita e chip de backup clicável.
- `compositor-v4-abas`: Compositor com duas abas — "Trocar código" (dois dropdowns pesquisáveis com ★ Frequentes e opção ✕ Remover) e "➕ Inserir bloco" (textarea + posição + modelos + prévia real). Botão único "+ Adicionar ao lote".
- `modal-conferencia-numeros-reais`: Modal "Conferência do lote — números reais" que varre os programas e exibe total, avisos, cartões por edição com exemplos reais e rodapé fixo com ação de Publicar.
- `modal-publicacao-progresso`: Modal de publicação com barra de progresso (backup → gravação → SHA-256) e tela de resultado com caminho do backup.
- `tela-codigos-biblioteca`: Tela dedicada de biblioteca de códigos com lista, busca, "+ Adicionar código" e suporte a blocos reutilizáveis (tag "bloco").
- `tela-historico-restauracao`: Tela de Histórico com linha por publicação e botão "↩ Restaurar originais" (com backup dos atuais antes de restaurar).
- `inserir-bloco`: Funcionalidade de inserção de bloco (textarea + posição ancorada + prévia real) disponível no compositor e na toolbar do editor.

### Modified Capabilities

- `fundacao-visual`: Novos tokens da paleta v4 (laranja #E85D04, fundo cinza-azulado, rail azul-ardósia escuro); sincronizar `theme.py` / `style.qss` com variáveis CSS do mockup v4.
- `layout-principal`: Reestruturar de 2 colunas (QSplitter) para rail + QStackedWidget de telas; remover os painéis Compositor e Resumo do layout antigo; tela Lote herda a lógica de 2 colunas internamente.
- `editor-de-arquivo`: Editor vira tela cheia com faixa de arquivos à esquerda; cabeçalho atualizado; toolbar em 3 grupos; toast "Desfazer" após salvar; bolinha de status no rail.
- `localizador-no-editor`: Toolbar do localizador agora tem 3 grupos (localizar com contagem automática / substituir / inserir bloco); contagem recalcula ao trocar arquivo ou escolher código, sem botão manual de varredura.

## Impact

- `flownc/ui/main_window.py` — reestruturar para rail + QStackedWidget de 4 telas; remover QSplitter atual; gerenciar sinais de status entre telas.
- `flownc/ui/components/compositor.py` — reescrever com abas (Trocar código / Inserir bloco), dropdowns pesquisáveis, proteção origem+destino.
- `flownc/ui/components/program_list.py` — adicionar arrastar-e-soltar, estado vazio, chip "N de M", ✕ por linha.
- `flownc/ui/components/summary.py` — substituído pelo Lote de edições (cartões + conflitos + CTA "Conferir lote →").
- `flownc/ui/components/header.py` — substituído por `top_bar.py` (configuração/receita + chip de backup).
- `flownc/ui/components/rail.py` — novo componente (rail lateral com 4 botões).
- `flownc/ui/screens/lote_screen.py` — nova tela Lote (programas + compositor + lista de edições).
- `flownc/ui/screens/codigos_screen.py` — nova tela Códigos.
- `flownc/ui/screens/historico_screen.py` — nova tela Histórico.
- `flownc/ui/modals/conferencia_modal.py` — novo modal de Conferência.
- `flownc/ui/modals/publicacao_modal.py` — novo modal de Publicação.
- `flownc/ui/editor_panel.py` — adaptado para tela cheia, faixa de arquivos, toolbar v4, toast Desfazer.
- `flownc/ui/theme.py` e `flownc/ui/style.qss` — sincronização com tokens do mockup v4.
- `flownc/core/` — sem alterações na FASE 2; na FASE 3: ligar `publish_batch`, `ensure_seed`, `preset_store` ao novo layout.
