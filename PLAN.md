# Plano de Execução — FlowNC (mockup v4)

status: pronto

> **Base deste plano:** o contrato visual é o mockup **`mockups/painel-final.v4.html`** (aprovado
> pelo Mestre em 2026-06-11). A descrição completa de telas, fluxos e regras está em
> **`docs/CONTEXTO-IA.md`** (fonte central). Onde houver dúvida visual/comportamental, vale o
> mockup v4 + o CONTEXTO-IA.
>
> **Decisão do Mestre (2026-06-11):** a interface é **reconstruída do zero** seguindo o v4 (rail +
> 4 telas). O **núcleo (`core/`)** e o motor de edição (`editor_panel.py`) são preservados e
> reaproveitados; a UI que não serve ao v4 foi arquivada em `_descarte/` e não volta ao fluxo.
>
> **Detalhamento executável:** a Fase 2 está atomizada na change OpenSpec
> **`plano-execucao-mockup-v4`** (`openspec/changes/plano-execucao-mockup-v4/`: `proposal.md`,
> `design.md`, `specs/`, `tasks.md`). Este `PLAN.md` é o plano vivo de alto nível; a change é o
> passo-a-passo que o `/opsx:apply` executa.

## ⛳ REGRA DE OURO — protótipo aprovado é o contrato

> **Nenhuma tela, popup, estado ou interação se implementa no app sem estar no protótipo
> aprovado.** O protótipo HTML (`mockups/painel-final.v4.html`) é o **contrato visual único**: o
> código segue cores, fontes, espaçamentos, textos, estados e comportamento. Qualquer mudança
> visual exige **primeiro** alterar o protótipo e obter aprovação do Mestre — só depois o código
> acompanha. Isso inclui **todos** os componentes de sistema/feedback: pop-ups de
> carregamento/salvamento, avisos, modais de confirmação, transições. Nada é decidido ou assumido
> durante o desenvolvimento: o que não estiver no protótipo aprovado não se implementa.

## Objetivo

Reproduzir o mockup **v4** no app FlowNC (PySide6), entregando uma interface fiel ao protótipo e
ligando-a ao núcleo já existente. O v4 organiza o app em **4 telas-lugar** numa barra lateral
(rail): **Lote · Editor · Códigos · Histórico**, com um **topo global** (seletor de configuração +
chip de backup) presente em todas elas. O coração do produto é o fluxo **Conferir → Publicar**:
nada é gravado sem uma conferência com números reais, e toda publicação cria backup versionado.

> **Trilha de negócio (paralela a este plano técnico):** a estratégia de monetização e o roteiro da
> página de vendas vivem em `docs/MONETIZACAO.md` e `docs/PAGINA-DE-VENDAS.md` (BR-first; comprador =
> dono/gestor da oficina; pagamento via Stripe; preço-teste). Este `PLAN.md` cobre só a **execução
> técnica do v4**; as decisões de produto/preço estão naqueles documentos e no `docs/README.md`.

## Estado atual (honesto)

**Pronto e testado (núcleo — preservar):**
- Motor de substituição com **borda CNC** (`core/matcher.py`), contagem (`core/scan.py`),
  planejamento (`core/replacement_plan.py`), substituição (`core/replacer.py`).
- **Conferência** (`core/conference.py`) e **publicação** com backup versionado + SHA-256
  (`core/publisher.py`).
- Gravação in-place atômica preservando codificação/BOM/EOL (`core/inplace_save.py`,
  `core/file_handler.py`).
- Biblioteca de códigos (`core/library_store.py`), perfis/receitas (`core/preset_store.py`),
  configurações (`core/settings_store.py`), semente de fábrica (`core/seed.py`).
- Suíte de testes verde (o número atual e os comandos exatos estão na seção **Tecnologias e
  verificação**; usar sempre o venv `flownc/.venv`, PySide6 6.11.1 — nunca o `pytest` global).

**Em construção (interface — Fase 2):**
- A interface v4 (`main_window.py` como maestro: topo + rail + `QStackedWidget` de 4 telas) está
  sendo montada tela a tela. A UI que não serve ao v4 já foi arquivada em `_descarte/ui_v2/`.

**A ligar/empacotar (Fase 3):**
- Ligar as telas v4 ao núcleo (conferência, publicação, biblioteca, receitas, histórico).
- Empacotar o EXE com tema, fontes IBM Plex e dados de fábrica (PyInstaller).

## Fases

### FASE 1 — Protótipo v4 ✅ CONCLUÍDA (gate cumprido)
Mockup `mockups/painel-final.v4.html` completo, interativo e **aprovado** (2026-06-11) =
contrato visual congelado. Documentado em `docs/CONTEXTO-IA.md`.

### FASE 2 — Porte visual do v4 ao app (em execução)
Reconstruir a interface em PySide6 seguindo o v4 **uma tela de cada vez**, na ordem definida no
`tasks.md` da change `plano-execucao-mockup-v4`. **Conferência lado a lado** = abrir o
`mockups/painel-final.v4.html` no navegador e o app rodando ao lado, comparando cada tela (mesma
largura de janela) antes de marcar a tarefa como concluída. **"Botões respondem visualmente"** =
têm estados de hover/pressionado pelo QSS e as ações de **navegação** (trocar de tela, abrir/fechar
modal, marcar/desmarcar item) funcionam; ações que dependem do núcleo (publicar de verdade, salvar
receita em disco, varrer arquivos) ainda **não** funcionam nesta fase — as telas exibem **dados de
exemplo** (valores fixos escritos no próprio código da UI, não lidos de `core/`). **Regra: nesta
fase só se altera arquivos de UI** (`flownc/ui/**`: layout, estilo, componentes, telas, modais);
o núcleo (`flownc/core/`) **não muda**. Detalhamento tarefa a tarefa na change
`plano-execucao-mockup-v4`.

Alvo de estrutura de arquivos (novos):
- `flownc/ui/components/rail.py` — barra lateral com os 4 botões-lugar.
- `flownc/ui/components/top_bar.py` — topo global (configuração/receita + chip de backup).
- `flownc/ui/components/program_list_v4.py` — lista de programas da tela Lote (Bloco 3).
- `flownc/ui/components/compositor_v4.py` — compositor com 2 abas (Trocar código / Inserir bloco) (Bloco 4).
- `flownc/ui/screens/lote_screen.py` — tela Lote (Programas + Compositor com abas + Lote de edições).
- `flownc/ui/screens/editor_screen.py` — tela Editor (faixa de arquivos + editor tela cheia).
- `flownc/ui/screens/codigos_screen.py` — tela Códigos (biblioteca).
- `flownc/ui/screens/historico_screen.py` — tela Histórico.
- `flownc/ui/modals/conferencia_modal.py` — modal "Conferência do lote — números reais".
- `flownc/ui/modals/publicacao_modal.py` — modal de publicação (progresso + resultado).
- `flownc/ui/theme.py` + `flownc/ui/style.qss` — paleta "Precisão Laranja" do v4 (CTA `#E85D04`).
- `flownc/ui/main_window.py` — vira o maestro: topo + (rail + `QStackedWidget` das 4 telas).

### FASE 3 — Ligar núcleo + empacotamento (só após a Fase 2 ser aprovada pelo Mestre)
**"Fase 2 aprovada"** = o Mestre conferiu o app contra o mockup v4 (smoke visual de todas as telas)
e deu o aval explícito ("é esse"). Só então começa a Fase 3: dar vida às telas aprovadas **sem
alterar o layout congelado** — conferência e publicação reais (`core/conference.py` +
`core/publisher.py`), biblioteca/receitas/histórico lidos e gravados em disco
(`core/library_store.py`, `core/preset_store.py`, `core/session_log.py`), semente de fábrica no
boot (`core/seed.py`), e empacotamento do EXE (tema, fontes IBM Plex, dados de fábrica) via
PyInstaller (`flownc/FlowNC.spec`). **Regra: nesta fase só se altera arquivos de lógica/ligação e
empacotamento**, nunca o layout aprovado. Será proposta como uma ou mais changes OpenSpec próprias
(`/opsx:propose`) quando a Fase 2 estiver aprovada.

## Mapa das telas do v4 (resumo — detalhe em CONTEXTO-IA)

- **Rail (lateral escura):** 4 botões-lugar; ativo com filete laranja; bolinha laranja no Editor
  quando há alteração não salva.
- **Topo global:** seletor de configuração/receita (com "💾 Salvar lote atual como…") + chip de
  backup clicável; visível em todas as telas.
- **Lote:** coluna Programas (lista, marcar/desmarcar, +adicionar, arrastar-e-soltar, estado vazio)
  + Compositor com **2 abas** ("Trocar código" e "➕ Inserir bloco") e botão único "+ Adicionar ao
  lote" + Lote de edições (cartões numerados, conflito âmbar) + CTA laranja "Conferir lote →".
- **Conferência (modal):** total de alterações, avisos, cartão por edição com exemplo real,
  linha de backup, rodapé fixo com "Publicar". **Contagem honesta** = a varredura simula as edições
  em sequência, na mesma ordem em que seriam gravadas (uma troca anterior pode mudar a âncora de um
  bloco posterior), então o número que o operador confere é exatamente o número que será publicado.
- **Publicação (modal):** progresso (backup → gravação → SHA-256) + resultado (caminho do backup,
  "Ver no Histórico" / "OK — novo lote").
- **Editor:** faixa de arquivos + editor tela cheia; cabeçalho com aviso "salva direto, sem cópia"
  + "Salvar"/"Salvar como…"; toolbar em 3 grupos (localizar com contagem automática · substituir ·
  inserir bloco); toast "Desfazer" após salvar.
- **Códigos:** biblioteca (código + descrição), busca, "+ Adicionar código" (com bloco opcional).
- **Histórico:** uma linha por publicação; "↩ Restaurar originais" (com backup dos atuais antes).

## Regras de negócio essenciais (do v4)

1. **Borda CNC:** um código só casa isolado (`M8` ≠ `M80`/`T1.0`). Segurança nº 1.
2. **Conferir ≠ Publicar:** conferir nunca grava; publicar sempre faz backup antes e confere por SHA-256.
3. **Edições rodam em cadeia, na ordem do lote** — a conferência conta nessa mesma ordem.
4. **Remover = trocar por vazio**, sempre por escolha explícita ("✕ Remover"); destino vazio **não**
   vira remoção.
5. **Lote** = edições + programas marcados; **Configuração/receita** = lote + preferências salvos.
6. **Editor salva sem backup** (decisão consciente, com Desfazer); **o Lote nunca grava sem backup**.

## Etapas atômicas da Fase 2

> Convenção: cada etapa tem **um verbo de ação** + **um critério de conclusão mensurável**
> (_em itálico_). Estas etapas são a versão refinada do `tasks.md` da change
> `plano-execucao-mockup-v4` — **manter PLAN.md e tasks.md em sincronia** (ao reaplicar a change,
> regenerar o `tasks.md` a partir daqui). Os números abaixo são a ordem de execução.

> Convenção de resiliência: `↳ Se falhar:` = o que fazer quando a etapa não atinge o critério.
> `[CRÍTICO]` = não pode avançar com falha: **parar, reportar ao Mestre e só seguir após resolver.**
> Regra geral de parada segura: nenhum `git commit` enquanto pytest/mypy/ruff da mudança não
> estiverem verdes; em qualquer falha não prevista, parar e reportar em vez de improvisar.

### Gate 0 — Quadro limpo ✅ (2026-06-12)

> A **única** change ativa é `plano-execucao-mockup-v4`. Todo material de versões antigas (changes,
> componentes de UI, mockups e docs) foi arquivado em `_descarte/` / `openspec/changes/archive/` e
> **não volta a entrar no fluxo** — nada de versão antiga interrompe o desenvolvimento do v4. Gate
> liberado.

### Bloco 1 — Fundação visual v4 (tokens + QSS)

1.1 **[CRÍTICO] Atualizar** `flownc/ui/theme.py` com os tokens da paleta v4 (valores do `<style>` do
   `painel-final.v4.html` + seção 4 do CONTEXTO-IA) — _Concluído quando: `COLOR_CTA == "#E85D04"`,
   existem `COLOR_RAIL` e `COLOR_TOP`, e `import flownc.ui.theme` não levanta erro._
   ↳ Se falhar: conferir os valores direto no `<style>` do mockup v4; faltando um token, criar com o
   que houver e anotar o pendente. É a base de todo o visual — não seguir pro QSS sem as cores e a
   tipografia essenciais.
1.2 **Atualizar** `flownc/ui/style.qss` com seletores para `QTabWidget` e `QDialog` usando tokens —
   _Concluído quando: o arquivo tem blocos para QTabWidget e QDialog e nenhuma cor hexadecimal
   literal (todos os valores vêm de tokens)._
   ↳ Se falhar (token ausente): usar o valor literal do mockup naquele ponto e anotar para
   tokenizar depois.
1.3 **[CRÍTICO] Verificar** a fundação — _Concluído quando: pytest, mypy e ruff (comandos da seção
   Verificação) ficam verdes._
   ↳ Se falhar: corrigir antes de avançar; gate obrigatório — não iniciar o Bloco 2 com qualquer um
   dos três vermelho.

### Bloco 2 — Estrutura raiz (rail + topo + pilha de telas)

2.1 **Criar** `flownc/ui/components/rail.py` com a classe `RailWidget` (4 botões + sinal
   `tela_mudou(int)`) — _Concluído quando: o arquivo existe, instancia sem erro e expõe o sinal._
   ↳ Se falhar: componente novo e isolado; se o sinal não emitir, conferir a declaração
   `Signal(int)` antes de integrar no maestro.
2.2 **Adicionar** o filete laranja no botão ativo do rail — _Concluído quando: só o botão da tela
   ativa exibe o filete._
   ↳ Se falhar: cosmético; usar uma cor de fundo distinta no botão ativo como meio-termo e anotar.
2.3 **Adicionar** a bolinha de status no botão Editor do rail — _Concluído quando: existe um método
   para ligar/desligar a bolinha e ela aparece quando ligada._
   ↳ Se falhar: cosmético; deixar o método pronto (mesmo sem o desenho final) e anotar.
2.4 **Criar** `flownc/ui/components/top_bar.py` com a classe `TopBar` — _Concluído quando: o arquivo
   existe e instancia com o `QComboBox` de receitas (item "💾 Salvar lote atual como…") e o chip de
   backup._
   ↳ Se falhar: componente isolado; se o combo/chip não montar, entregar o mínimo (logo + combo) e
   anotar o resto.
2.5 **Criar** o pacote `flownc/ui/screens/` (com `__init__.py`) e os 4 stubs de tela — _Concluído
   quando: `flownc/ui/screens/__init__.py` existe e `lote_screen.py` (classe `LoteScreen`),
   `editor_screen.py` (`EditorScreen`), `codigos_screen.py` (`CodigosScreen`) e `historico_screen.py`
   (`HistoricoScreen`) existem, cada um com a classe nomeada herdando de `QWidget`._
   ↳ Se falhar: trivial; cada stub é uma classe `QWidget` com um `QLabel` de título. Atenção: sem o
   `__init__.py` os imports do maestro falham.
2.6 **[CRÍTICO] Reestruturar** `flownc/ui/main_window.py` para topo + (rail + `QStackedWidget`),
   inserindo as telas na ordem fixa **índice 0 = Lote, 1 = Editor, 2 = Códigos, 3 = Histórico**
   (mesma ordem dos botões do rail) — _Concluído quando: não há mais `QSplitter` raiz e o app abre
   mostrando o rail à esquerda e a tela Lote (índice 0)._
   ↳ Se falhar (app não abre): **fazer commit/branch de segurança antes de mexer**; se a janela não
   subir, voltar ao estado anterior e migrar em incrementos menores (primeiro empilhar as telas no
   `QStackedWidget`, depois remover o `QSplitter`). Não alterar a lógica de `core/` para "consertar".
2.7 **Conectar** `RailWidget.tela_mudou` ao `QStackedWidget.setCurrentIndex` — _Concluído quando:
   clicar em cada um dos 4 botões troca o widget central._
   ↳ Se falhar: conferir o `connect()`; como fallback, trocar a tela direto no handler do clique de
   cada botão.
2.8 **[CRÍTICO] Verificar** a estrutura raiz — _Concluído quando: o app abre, os 4 botões trocam de
   tela e o pytest fica verde._
   ↳ Se falhar: corrigir antes de seguir; é a base de todas as telas — não avançar com o app sem
   abrir ou com o pytest vermelho.

### Bloco 3 — Tela Lote · painel Programas

3.1 **Criar** `flownc/ui/components/program_list_v4.py` — _Concluído quando: a lista renderiza
   linhas com checkbox, nome (mono), data, tamanho, botão "✎ Abrir" e "✕"._
   ↳ Se falhar: componente novo; renderizar primeiro a linha mínima (checkbox + nome) e somar as
   colunas (data, tamanho, botões) depois.
3.2 **Implementar** marcar/desmarcar com destaque visual e o chip "N de M marcados" — _Concluído
   quando: clicar na linha alterna o destaque e o chip atualiza a contagem._
   ↳ Se falhar: garantir ao menos o checkbox funcional alimentando a seleção; o destaque visual é
   secundário.
3.3 **Adicionar** o botão "Marcar todos / Desmarcar todos" — _Concluído quando: o botão marca e
   desmarca todas as linhas._
   ↳ Se falhar: item secundário; anotar e seguir.
3.4 **Adicionar** arrastar-e-soltar de arquivos na lista — _Concluído quando: soltar arquivos do
   Windows na área adiciona as linhas correspondentes._
   ↳ Se falhar (drag&drop trabalhoso no Qt): manter o botão "+ Adicionar programa(s)…" como caminho
   principal e anotar o D&D como ajuste posterior.
3.5 **Implementar** o estado vazio com botão "+ Adicionar programa(s)…" — _Concluído quando: sem
   arquivos a área mostra ícone + texto-guia + botão grande._
   ↳ Se falhar: cosmético; ao menos exibir o botão de adicionar quando a lista estiver vazia.
3.6 **Integrar** `program_list_v4` na coluna esquerda da `LoteScreen` — _Concluído quando: a tela
   Lote exibe a lista de programas à esquerda._
   ↳ Se falhar: testar o componente isolado antes de integrar; conferir o layout da coluna esquerda.

### Bloco 4 — Tela Lote · Compositor com abas e Lote de edições

4.1 **Criar** `flownc/ui/components/compositor_v4.py` com `QTabWidget` de 2 abas — _Concluído quando:
   o arquivo existe e mostra as abas "Trocar código" e "➕ Inserir bloco" com um único botão
   "+ Adicionar ao lote" abaixo._
   ↳ Se falhar: começar com uma aba funcional e adicionar a segunda depois.
4.2 **Montar** a aba "Trocar código" com dois dropdowns pesquisáveis — _Concluído quando: os dois
   `QComboBox` abrem com busca + seção "★ Frequentes" e mostram só o código (descrição no tooltip)._
   ↳ Se falhar (dropdown pesquisável difícil): usar `QComboBox` editável simples como meio-termo e
   anotar "★ Frequentes"/tooltip como ajuste.
4.3 **Adicionar** a opção "✕ Remover (sem código)" no dropdown de destino — _Concluído quando:
   selecioná-la deixa o destino vermelho "✕ remover"._
   ↳ Se falhar: garantir ao menos um item "Remover" selecionável; o estilo vermelho é secundário.
4.4 **Habilitar** "+ Adicionar ao lote" só com origem e destino preenchidos — _Concluído quando: o
   botão fica desabilitado faltando qualquer um dos dois._
   ↳ Se falhar: na dúvida **manter o botão desabilitado** (mais seguro — evita edição "trocar por
   nada") e conferir os sinais de mudança dos combos.
4.5 **Montar** a aba "➕ Inserir bloco" — _Concluído quando: a aba mostra textarea, seletor de
   posição (com aviso na opção por número de linha), chips de modelos e a prévia do primeiro
   programa marcado._
   ↳ Se falhar: entregar textarea + seletor de posição primeiro; prévia e chips de modelo depois.
4.6 **Implementar** a lista de edições (cartões numerados) na `LoteScreen` — _Concluído quando:
   adicionar uma edição cria um cartão numerado com as ações ✎/⧉/✕._
   ↳ Se falhar: renderizar uma lista de texto simples antes dos cartões estilizados.
4.7 **Implementar** editar/duplicar/excluir do cartão — _Concluído quando: ✎ recarrega a edição no
   compositor na aba certa, ⧉ duplica e ✕ remove e renumera os cartões._
   ↳ Se falhar: priorizar o excluir (✕); editar e duplicar podem vir depois.
4.8 **Detectar** conflito (mesma origem) com destaque âmbar + chip — _Concluído quando: dois cartões
   de mesma origem ficam âmbar e o chip mostra "⚠ N conflitos"._
   ↳ Se falhar: a detecção é por código de origem repetido; se o destaque âmbar falhar, ao menos
   mostrar o chip "⚠ N conflitos".
4.9 **Implementar** o CTA "Conferir lote →" com a regra de habilitação — _Concluído quando: fica
   desabilitado sem edições ou sem programas marcados (tooltip explica o que falta) e habilitado
   com ambos._
   ↳ Se falhar: na dúvida manter desabilitado; conferir as duas condições (tem edição? tem programa
   marcado?).

### Bloco 5 — Modal Conferência

5.1 **Criar** o pacote `flownc/ui/modals/` (com `__init__.py`) e `conferencia_modal.py` (`QDialog`
   bloqueante) — _Concluído quando: `flownc/ui/modals/__init__.py` existe e o modal abre exibindo
   faixa de total, avisos, cartões por edição, linha de backup e rodapé fixo._
   ↳ Se falhar: modal novo isolado; montar as seções de cima pra baixo (faixa → avisos → cartões →
   backup → rodapé), validando uma de cada vez.
5.2 **Preencher** o modal com dados de exemplo — _Concluído quando: a faixa mostra um total e os
   cartões listam programas afetados com exemplo real (valores fixos no código da UI)._
   ↳ Se falhar: usar um conjunto mínimo fixo (1 edição, 2 programas) só para validar o visual.
5.3 **Implementar** o rodapé conforme o estado — _Concluído quando: botão laranja sem conflito,
   âmbar com conflito, desabilitado com total 0._
   ↳ Se falhar: na dúvida desabilitar o botão (mais seguro) e conferir a lógica de conflito/total.
5.4 **Ligar** o CTA "Conferir lote →" para abrir o modal — _Concluído quando: clicar no CTA abre o
   modal de Conferência._
   ↳ Se falhar: conferir o sinal do CTA; como fallback, abrir o modal direto no handler do clique.

### Bloco 6 — Modal Publicação

6.1 **Criar** `flownc/ui/modals/publicacao_modal.py` com barra de progresso — _Concluído quando: o
   modal mostra as etapas backup → gravação → SHA-256 e não fecha durante o progresso._
   ↳ Se falhar: começar com a barra estática; o ponto-chave é **impedir o fechar durante o
   progresso** (desabilitar ✕ e Esc).
6.2 **Implementar** a tela de resultado — _Concluído quando: ao concluir mostra "Publicado ✓", o
   caminho do backup e os botões "Ver no Histórico" e "OK — novo lote"._
   ↳ Se falhar: ao menos exibir "Publicado ✓" e o caminho do backup.
6.3 **Ligar** "OK — novo lote" para limpar a lista de edições — _Concluído quando: clicar remove
   todos os cartões da `LoteScreen`._
   ↳ Se falhar: conferir o método de limpar a lista de edições da `LoteScreen`.
6.4 **Ligar** "Ver no Histórico" para navegar à tela Histórico — _Concluído quando: clicar fecha o
   modal e ativa a tela Histórico no rail._
   ↳ Se falhar: reusar o caminho do rail (`setCurrentIndex` da tela Histórico) no handler.
6.5 **Encadear** Conferência → Publicação — _Concluído quando: clicar "Publicar" na Conferência
   fecha-a e abre o modal de Publicação._
   ↳ Se falhar: fechar a Conferência e abrir a Publicação no mesmo handler do botão "Publicar".

### Bloco 7 — Tela Editor

7.1 **Criar** `flownc/ui/screens/editor_screen.py` reaproveitando o motor de edição existente —
   _Concluído quando: a tela abre um arquivo em tela cheia com numeração de linha e fonte mono._
   ↳ Se falhar: **não alterar `core/inplace_save.py` nem `core/file_handler.py`** (lógica de save
   testada); embrulhar o `editor_panel` existente como widget interno da tela em vez de reescrever.
7.2 **Implementar** a faixa de arquivos à esquerda — _Concluído quando: a faixa lista os programas
   carregados e clicar troca o arquivo aberto._
   ↳ Se falhar: começar com uma lista simples de nomes; clicar carrega o arquivo no editor.
7.3 **[CRÍTICO] Implementar** a guarda de alterações ao trocar/sair — _Concluído quando: com edição
   pendente, trocar de arquivo abre o diálogo Salvar / Descartar / Cancelar._
   ↳ Se falhar: na dúvida **sempre perguntar** antes de trocar/sair (perder edição do operador é
   inaceitável); Cancelar deve manter o editor exatamente como estava.
7.4 **Montar** o cabeçalho do editor — _Concluído quando: mostra "Editando NOME.NC", o aviso
   "⚠ salva direto, sem cópia" e os botões "Salvar como…" e "Salvar"._
   ↳ Se falhar: cosmético; garantir ao menos o aviso "salva direto, sem cópia" e o botão Salvar.
7.5 **Implementar** o toast "Desfazer" após salvar — _Concluído quando: salvar mostra um toast com
   "Desfazer" que restaura o conteúdo anterior ao save._
   ↳ Se falhar: guardar o conteúdo pré-save em memória; se o toast falhar, manter ao menos o Ctrl+Z
   do editor como rede de segurança.
7.6 **Implementar** a bolinha de alteração na faixa e no rail — _Concluído quando: editar sem salvar
   mostra a bolinha laranja na faixa e no botão Editor; salvar a remove._
   ↳ Se falhar: cosmético; anotar e seguir.

### Bloco 8 — Toolbar do Editor (3 grupos)

8.1 **Organizar** a toolbar em 3 grupos com separadores — _Concluído quando: a toolbar mostra
   Localizar | Substituir | Inserir bloco separados._
   ↳ Se falhar: reaproveitar os controles de busca já existentes no editor; o agrupamento visual é
   secundário.
8.2 **Implementar** a contagem automática de ocorrências — _Concluído quando: trocar código, trocar
   arquivo ou editar o texto recalcula "N encontrados" sem botão manual._
   ↳ Se falhar: usar `core/matcher.py` (`find_matches`) / `core/scan.py` (`count_occurrences`) já
   prontos; se recalcular a cada tecla pesar, recalcular ao trocar código/arquivo primeiro.
8.3 **Implementar** a navegação ↑/↓ circular com realce da corrente — _Concluído quando: as setas
   rolam até a ocorrência, "i/N" atualiza e a corrente fica com realce mais forte._
   ↳ Se falhar: garantir próximo/anterior não-circular antes de fechar o ciclo.
8.4 **Implementar** o realce de todas as ocorrências (`QSyntaxHighlighter`) — _Concluído quando:
   escolher um código realça todas as ocorrências no texto._
   ↳ Se falhar (lento em arquivo grande): limitar o realce à área visível ou desligar acima de N
   linhas; a busca não pode travar.
8.5 **Implementar** "Substituir todos" — _Concluído quando: o botão substitui todas as ocorrências
   no buffer de uma vez._
   ↳ Se falhar: reaproveitar a substituição já existente no editor atual.
8.6 **Implementar** "Um a um" como stepbar inline — _Concluído quando: clicar abre a barra inferior
   com Substituir / Pular → / Concluir, sem usar `QMessageBox`._
   ↳ Se falhar: manter o fluxo um-a-um atual como meio-termo até a stepbar inline ficar pronta.
8.7 **[CRÍTICO] Implementar** "➕ Inserir bloco" no editor com proteção de âncora — _Concluído
   quando: o modal mostra a prévia e bloqueia o botão se a âncora não existe no arquivo._
   ↳ Se falhar: priorizar a **proteção** (âncora inexistente bloqueia a inserção) — é segurança
   contra inserir no lugar errado; a prévia visual pode vir depois.

### Bloco 9 — Tela Códigos

9.1 **Criar** `flownc/ui/screens/codigos_screen.py` com lista + busca + contador — _Concluído quando:
   a tela lista código+descrição, filtra pela busca e mostra "N cadastrados"._
   ↳ Se falhar: entregar a lista simples + busca primeiro; o contador depois.
9.2 **Implementar** "+ Adicionar código" (com bloco opcional) — _Concluído quando: o formulário cria
   um código novo que aparece na lista._
   ↳ Se falhar: salvar via `core/library_store.py` já existente; conferir o schema (`find`=código,
   `label`=descrição, `replace`="").
9.3 **Marcar** com a tag "bloco" os códigos com bloco e expô-los como modelos — _Concluído quando:
   códigos com bloco mostram a tag e aparecem como chips nos inseridores de bloco._
   ↳ Se falhar: o campo bloco é opcional; entregar código+descrição primeiro e o bloco depois.

### Bloco 10 — Tela Histórico

10.1 **Criar** `flownc/ui/screens/historico_screen.py` com lista cronológica reversa — _Concluído
   quando: a tela lista publicações (quando/resumo/backup/configuração), mais recente no topo._
   ↳ Se falhar: lista simples de linhas com dados de exemplo; a leitura real de `core/session_log.py`
   é da Fase 3.
10.2 **Implementar** o estado vazio do Histórico — _Concluído quando: sem publicações a tela mostra
   ícone + texto-guia._
   ↳ Se falhar: cosmético; anotar e seguir.
10.3 **Implementar** "↩ Restaurar originais" por linha — _Concluído quando: o botão pede confirmação
   e fica desabilitado se o backup não existir._
   ↳ Se falhar: na Fase 2 basta o botão + diálogo de confirmação (visual). A restauração real (criar
   backup dos atuais **antes** de devolver os originais) é da Fase 3 e é **[CRÍTICO]** lá — mexe em
   arquivos do operador.

### Bloco 11 — Topo global (receitas + backup)

11.1 **Implementar** a seleção de receita no `QComboBox` — _Concluído quando: selecionar com lote
   vazio carrega direto e com lote preenchido pede confirmação._
   ↳ Se falhar: na dúvida **sempre pedir confirmação** antes de substituir (não perder o lote
   montado pelo operador).
11.2 **Implementar** "💾 Salvar lote atual como…" — _Concluído quando: o item abre um diálogo para
   nomear e a receita passa a aparecer na lista._
   ↳ Se falhar: na Fase 2 basta o diálogo de nome; a gravação real via `core/preset_store.py` é da
   Fase 3.
11.3 **Implementar** o chip de backup clicável — _Concluído quando: clicar abre o seletor de pasta e
   o chip passa a mostrar o novo caminho._
   ↳ Se falhar: usar o `QFileDialog` nativo do Qt para escolher a pasta; conferir o caminho
   retornado antes de atualizar o chip.

### Bloco 12 — Verificação da Fase 2

12.1 **[CRÍTICO] Rodar** o pytest — _Concluído quando: zero regressões frente ao baseline._
   ↳ Se falhar: corrigir antes de pedir o aval do Mestre; não aprovar nem commitar com teste vermelho.
12.2 **[CRÍTICO] Rodar** o mypy — _Concluído quando: sem novos erros de tipo._
   ↳ Se falhar: corrigir os tipos dos arquivos novos da UI; não silenciar com `type: ignore` sem motivo.
12.3 **[CRÍTICO] Rodar** o ruff — _Concluído quando: sem violações._
   ↳ Se falhar: rodar `ruff check --fix` para o trivial e ajustar o resto à mão.
12.4 **Fazer** o smoke visual de todas as telas — _Concluído quando: cada tela foi comparada ao
   mockup v4 e as divergências anotadas (ou nenhuma encontrada)._
   ↳ Se falhar (divergência relevante): anotar e voltar ao bloco da tela correspondente antes de
   pedir o aval do Mestre — é o gate da Fase 2.
12.5 **Pedir** a aprovação explícita do Mestre ("é esse") — _Concluído quando: o Mestre conferiu o
   smoke visual de todas as telas e deu o aval; é o **gate de saída da Fase 2** que libera a Fase 3._
   ↳ Se falhar (Mestre aponta divergência): anotar, voltar ao bloco da tela correspondente e
   reapresentar; não iniciar a Fase 3 sem o "é esse".

## Etapas da Fase 3 (alto nível — atomizar na proposta da change da Fase 3)

> Só começam após o gate "Fase 2 aprovada pelo Mestre". Serão **atomizadas com fallback próprio na
> proposta da change da Fase 3** (`/opsx:propose`). Aqui valem o critério mensurável e a marcação de
> criticidade; o fallback fino entra na proposta. Regra geral até lá: em falha de gravação, **parar
> preservando o backup já criado** e reportar, nunca deixar arquivos pela metade em silêncio.

- **Ligar** a biblioteca real aos dropdowns (`core/library_store.py`) — _Concluído quando: os
  dropdowns mostram os códigos do disco, não dados de exemplo._
- **Ligar** a varredura/conferência real (`core/conference.py` + `core/scan.py` +
  `core/replacement_plan.py`) ao modal de Conferência — _Concluído quando: o modal mostra números
  reais dos arquivos marcados._
- **[CRÍTICO] Ligar** a publicação real (`core/publisher.py`) ao botão Publicar — _Concluído quando:
  publicar grava com backup versionado + SHA-256._ (Crítico: grava nos arquivos do operador.)
- **Ligar** as receitas (`core/preset_store.py`) ao seletor de configuração — _Concluído quando:
  salvar e carregar receita persiste em disco._
- **[CRÍTICO] Ligar** o histórico (`core/session_log.py`) e a restauração à tela Histórico —
  _Concluído quando: cada publicação aparece no Histórico e "Restaurar" devolve os originais do
  backup, criando antes um backup dos arquivos atuais._ (Crítico: restaurar mexe nos arquivos atuais.)
- **Chamar** `core/seed.py` (`ensure_seed`) no boot — _Concluído quando: abrir numa pasta `data/`
  vazia repõe biblioteca + receitas de fábrica._
- **[CRÍTICO] Configurar** `flownc/FlowNC.spec` (`datas` com QSS, fontes e `data_default`) —
  _Concluído quando: o build inclui tema, fontes e dados de fábrica._ (Crítico: sem isso o EXE sai
  "pelado" na entrega.)
- **[CRÍTICO] Empacotar e verificar** o EXE numa pasta limpa — _Concluído quando: `FlowNC.exe` abre
  com tema, fontes e biblioteca/receitas carregados (não "pelado")._

## Dependências e ordem

- **Sequência de fases:** Fase 1 ✅ → Fase 2 (atual) → Fase 3 (só após a Fase 2 ser aprovada pelo Mestre).
- **Dentro da Fase 2:** o Gate 0 precede tudo; depois os blocos seguem a ordem numérica
  (1 → 12). O Bloco 2 (estrutura raiz) é pré-requisito de todos os blocos de tela (3–11). Os modais
  (5, 6) dependem da tela Lote (3, 4). A toolbar do Editor (8) depende da tela Editor (7).
- **Núcleo é pré-requisito de ligação (Fase 3), não de layout (Fase 2):** a Fase 2 usa dados de
  exemplo; a Fase 3 conecta o `core/`.

## Tecnologias e verificação

- **Linguagem/UI:** Python 3.11+, PySide6 (Qt Widgets).
- **Estilo:** `flownc/ui/theme.py` (tokens) + `flownc/ui/style.qss`; fontes IBM Plex Sans/Mono
  (empacotar na Fase 3).
- **Arquitetura:** rail + topo + `QStackedWidget` de 4 telas em `main_window.py` (maestro);
  telas em `flownc/ui/screens/`; modais em `flownc/ui/modals/`; componentes compartilhados em
  `flownc/ui/components/`.
- **Núcleo:** `flownc/core/` (preservado, não muda na Fase 2).
- **Build:** PyInstaller (`flownc/FlowNC.spec`) → `flownc/dist/FlowNC/FlowNC.exe` (Fase 3).
- **Verificação (sempre a partir da raiz do projeto, com o Python do venv `flownc/.venv`):** no
  Windows/PowerShell, `flownc\.venv\Scripts\python.exe -m pytest flownc/tests/`,
  `flownc\.venv\Scripts\python.exe -m mypy flownc/ --ignore-missing-imports` e
  `flownc\.venv\Scripts\python.exe -m ruff check flownc/`. **"Verde"** = todos os testes que já
  passavam continuam passando (zero regressões frente ao estado atual — não fixar um número
  absoluto, comparar com o baseline rodando antes da mudança). Os três verdes são pré-requisito
  para arquivar qualquer change.
- **Processo OpenSpec:** propose → apply → archive, **uma mudança por vez**. Fase 2 =
  `plano-execucao-mockup-v4`; Fase 3 = change(s) futura(s). "Validar" = conferir que os artefatos
  existem e estão coerentes (+ `openspec validate <nome>` opcional). Não existe `/opsx:validate`.

## Glossário rápido

**Termos do produto/v4**
- **Rail:** barra lateral escura com os 4 botões-lugar (Lote/Editor/Códigos/Histórico).
- **Topo global:** faixa no alto, visível em todas as telas, com o seletor de configuração/receita
  e o chip de backup.
- **Chip de backup:** botão pequeno no topo que mostra o caminho da pasta de backup atual; clicar
  abre um seletor para trocar a pasta.
- **Receita/Configuração:** lote de edições + preferências salvos com um nome, para reutilizar.
- **Lote:** conjunto de edições a aplicar nos programas marcados.
- **Edição:** uma troca de código (origem → destino/remover) **ou** uma inserção de bloco.
- **Conferir:** varredura real que mostra o que mudaria, sem gravar.
- **Publicar:** gravar as edições com backup versionado e conferência dupla (SHA-256).
- **Borda CNC:** regra que impede `M8` de casar dentro de `M80`/`T1.0`.

**Termos de interface (UX)**
- **Estado vazio:** o que uma lista/tela mostra quando ainda não tem dados — ícone + texto-guia +
  botão de ação, nunca uma área em branco.
- **Toast:** aviso passageiro que aparece no rodapé e some sozinho após alguns segundos (pode
  trazer um botão, ex.: "Desfazer").
- **Smoke (teste de fumaça) visual:** abrir o app de verdade e conferir cada tela a olho contra o
  mockup v4, anotando divergências — não é teste automatizado.

**Termos técnicos (Python/Qt)**
- **Maestro:** `flownc/ui/main_window.py` — instancia rail/topo/telas/modais, conecta os sinais e
  troca a tela ativa. Não contém lógica de conteúdo de tela.
- **QStackedWidget:** empilhador de telas do Qt em que **só uma** fica visível por vez; o rail
  escolhe qual mostrar. É o que troca entre Lote/Editor/Códigos/Histórico.
- **Sinais/slots (Qt):** mecanismo do Qt em que um widget "emite um sinal" (ex.: botão clicado) e
  um método conectado ("slot") responde. As telas avisam o maestro por sinais; o maestro reage.
- **Tokens:** constantes de estilo (cores, fontes, espaçamentos) definidas em `flownc/ui/theme.py`
  e usadas no `flownc/ui/style.qss`, para não espalhar valores fixos pelo código.
