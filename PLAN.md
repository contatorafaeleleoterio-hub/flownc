# Plano de Execução

status: pronto

## Objetivo

Implementar o **novo design já aprovado** (mockup `mockups/painel-final.v2.html`) no app FlowNC, deixando a interface idêntica ao mockup e preservando a lógica atual (perfis, execução de substituições, verificações, biblioteca e o editor por arquivo já existente). O design antigo está **totalmente descartado** e não serve mais de referência.

Forma de execução livre (criar documentos, escrever código novo, reprogramar ou reconstruir do zero) — o foco é colocar o novo design em funcionamento no sistema atual.

## Glossário

- **Modo edição:** estado em que `editor_panel.py` está visível na coluna direita (o usuário clicou em "✎ Editar" em um arquivo). Ao sair do editor (fechar ou voltar), o app retorna ao modo padrão (coluna direita = Resumo).
- **Proporção dinâmica:** as duas colunas ficam lado a lado num `QSplitter(Qt.Horizontal)` (esquerda e direita). No modo padrão ficam 60 % esquerda / 40 % direita; no modo edição ficam 40 % / 60 %. A troca é feita via `QSplitter.setSizes()` com `QPropertyAnimation` ou animação manual no `resizeEvent`. "Vertical/horizontal" aqui sempre se refere à **orientação do QSplitter**: para colunas lado a lado a orientação é **horizontal**.
- **Fundação visual:** aplicar tokens (cores, fontes, espaçamentos, cantos, alturas do mockup) ao app via `theme.py` + QSS. **Não** alterar posição, número ou hierarquia de widgets existentes — só aparência (cores de fundo, bordas, fontes, tamanho de controles).
- **Layout:** posição, número e hierarquia dos widgets (`QVBoxLayout`, `QHBoxLayout`, `QSplitter`, `QStackedWidget`, etc.). Mudanças de layout pertencem à Mudança B, não à A.
- **Rascunho:** a linha de input ainda em construção pelo usuário no compositor de edições — sempre renderizada no fim da lista "Edições montadas" com visual diferenciado (fundo `--color-bg-subtle`, borda tracejada).
- **Bloco "Editados → backup":** área na coluna direita que lista os nomes dos arquivos que foram salvos em lote com o caminho da pasta de backup criada. Aparece só depois de uma execução bem-sucedida; permanece até o app fechar ou uma nova execução começar.
- **Lógica atual:** todo o código em `flownc/core/` (matcher, inplace_save, perfis, verificações) e os sinais/slots que conectam a UI à lógica em `main_window.py`. Nada disso muda de comportamento — só muda de onde é chamado (o "maestro" vira `main_window.py` refatorado, que instancia os componentes novos e repassa os mesmos sinais/slots).
- **Comandos de verificação (lint/testes):** sempre rodar na raiz do projeto — `pytest flownc/tests/` · `mypy flownc/ --ignore-missing-imports` · `ruff check flownc/`.
- **Fluxo OpenSpec por mudança:** cada Mudança (A/B/C) segue três fases. (1) **Propor** com a skill `/opsx:propose` — gera `proposal.md`, `design.md`, `specs/` e `tasks.md` na pasta `openspec/changes/<nome>/`. (2) **Implementar** com a skill `/opsx:apply <nome>` — ela percorre o `tasks.md` gerado; as etapas de implementação deste plano (ex.: 3–7) **são** essas tarefas e são executadas dentro do `/opsx:apply`. (3) **Arquivar** com `/opsx:archive <nome>`. **Validar a proposta** significa conferir que o `/opsx:propose` terminou sem apontar erros e que os artefatos acima existem e estão coerentes; se houver a CLI do OpenSpec instalada, rodar também `openspec validate <nome>` como reforço.

## Etapas

> Convenção: cada etapa = **um verbo de ação** + **um critério de conclusão mensurável** (_itálico_) + **fallback** (`↳ Se falhar:`). Etapas marcadas `[CRÍTICO]` não podem avançar com falha: parar, reportar ao Mestre e só seguir após resolver. Regra geral de parada segura: nenhum `git commit` enquanto a verificação (pytest/mypy/ruff) da mudança não estiver verde; em qualquer falha não prevista, parar e reportar em vez de improvisar.

### Mudança A — Fundação visual (`redesign-fundacao-visual`)

1. **Propor a Mudança A** — rodar `/opsx:propose` com o nome `redesign-fundacao-visual`, descrevendo: criar `theme.py`, carregar fontes IBM Plex, gerar QSS central, aplicar sem mudar layout. _Concluído quando: a pasta `openspec/changes/redesign-fundacao-visual/` existe com `proposal.md`, `design.md`, `tasks.md` e `specs/`._
   ↳ Se falhar: revisar a descrição passada ao comando e repropor; não criar a pasta à mão.

2. **Validar a proposta da Mudança A** — conferir que o `/opsx:propose` terminou sem erros e que `proposal.md`, `design.md`, `tasks.md` e `specs/` existem e estão coerentes (se a CLI estiver instalada, rodar `openspec validate redesign-fundacao-visual` como reforço). _Concluído quando: os quatro artefatos existem e nenhuma validação aponta erro._
   ↳ Se falhar: ler o erro, ajustar o artefato apontado (`proposal`/`specs`/`tasks`) e revalidar; não avançar para a implementação (Etapa 3) com a proposta inválida.

> **Etapas 3–7 (implementação) são as tarefas do `tasks.md` desta mudança e são executadas dentro de `/opsx:apply redesign-fundacao-visual`.**

3. **[CRÍTICO] Criar `flownc/ui/theme.py`** — definir, como constantes Python, todos os tokens do mockup: cores `--color-*`, tipografia `--t-*`, espaçamentos `--sp-*`, raios `--radius-*`, alturas `--h-*`, dimensões `--dim-*`. _Concluído quando: o arquivo `flownc/ui/theme.py` existe e `import flownc.ui.theme` não levanta erro._
   ↳ Se falhar: conferir os valores direto no `<style>` de `mockups/painel-final.v2.html`; faltando algum token, criar mesmo assim com os que existem e anotar o pendente. Base de todo o visual — não prosseguir para o QSS sem os tokens essenciais de cor e tipografia.

4. **Adicionar as fontes IBM Plex ao projeto** — colocar os arquivos `.ttf` de IBM Plex Sans e IBM Plex Mono em `flownc/assets/fonts/`. _Concluído quando: os arquivos `.ttf` das duas famílias existem em `flownc/assets/fonts/`._
   ↳ Se falhar (sem acesso aos `.ttf`): registrar como blocker e seguir usando fallback de fonte do sistema (`Segoe UI` / `Consolas`) nos tokens de tipografia; trocar para IBM Plex quando os arquivos chegarem.

5. **Registrar as fontes no app** — chamar `QFontDatabase.addApplicationFont()` para cada `.ttf` na inicialização de `main_window.py`. _Concluído quando: as duas famílias aparecem em `QFontDatabase.families()` após o boot do app._
   ↳ Se falhar (retorno -1 do add): logar o caminho tentado, manter o fallback de fonte do sistema e não bloquear o boot.

6. **Criar `flownc/ui/style.qss`** — escrever a folha QSS usando os tokens de `theme.py`, cobrindo QMainWindow, QPushButton, QComboBox, QListWidget, QLineEdit, QLabel, QCheckBox e QSplitter. _Concluído quando: o arquivo `flownc/ui/style.qss` existe e contém um seletor para cada um desses 8 tipos de widget._
   ↳ Se falhar (token ausente): usar o valor literal do mockup naquele ponto e anotar para tokenizar depois (Etapa 30).

7. **[CRÍTICO] Aplicar o QSS na inicialização** — em `main_window.py`, ler `style.qss` e chamar `app.setStyleSheet()` no boot, sem remover, mover ou criar widgets. _Concluído quando: o app abre com as cores/fontes do mockup e o número/hierarquia de widgets é idêntico ao de antes._
   ↳ Se falhar (app quebra ou widget some): reverter o `setStyleSheet` e aplicar o QSS em partes (por tipo de widget) até isolar o seletor culpado. Não alterar layout para "consertar" — risco de quebrar a lógica.

8. **[CRÍTICO] Verificar a Mudança A** — rodar `pytest flownc/tests/`, `mypy flownc/ --ignore-missing-imports` e `ruff check flownc/`. _Concluído quando: os três comandos terminam sem falhas._
   ↳ Se falhar: corrigir antes de arquivar; gate obrigatório. Não arquivar nem commitar com qualquer um dos três vermelho.

9. **Arquivar a Mudança A** — rodar `/opsx:archive redesign-fundacao-visual`. _Concluído quando: a change sai de `openspec/changes/` e vai para o histórico de arquivadas._
   ↳ Se falhar: não forçar mover pastas à mão; reportar o erro do comando.

### Mudança B — Layout e painéis (`redesign-layout-paineis`)

10. **Propor a Mudança B** — rodar `/opsx:propose` com o nome `redesign-layout-paineis`, descrevendo: criar `flownc/ui/components/` (`header.py`, `compositor.py`, `program_list.py`, `resumo.py`), refatorar `main_window.py` como "maestro", colunas dinâmicas. _Concluído quando: a pasta `openspec/changes/redesign-layout-paineis/` existe com todos os artefatos._
   ↳ Se falhar: revisar a descrição e repropor; não editar artefatos à mão.

11. **Validar a proposta da Mudança B** — conferir que o `/opsx:propose` terminou sem erros e que `proposal.md`, `design.md`, `tasks.md` e `specs/` existem e estão coerentes (reforço opcional: `openspec validate redesign-layout-paineis`). _Concluído quando: os quatro artefatos existem e nenhuma validação aponta erro._
   ↳ Se falhar: ajustar o artefato apontado e revalidar antes de codar (Etapa 12).

> **Etapas 12–19 (implementação) são as tarefas do `tasks.md` desta mudança e são executadas dentro de `/opsx:apply redesign-layout-paineis`.**

12. **Criar `flownc/ui/components/header.py`** — header fixo com logo FlowNC, título "FlowNC", `QComboBox` de máquina e botões de biblioteca. _Concluído quando: o arquivo existe e a classe de header instancia sem erro._
   ↳ Se falhar (logo indisponível): usar placeholder de texto "FlowNC" e seguir; trocar pelo asset depois.

13. **Montar o esqueleto de 2 colunas em `main_window.py`** — adicionar um `QSplitter(Qt.Horizontal)` (colunas lado a lado) com dois painéis filhos (esquerda e direita). _Concluído quando: o app abre exibindo duas colunas lado a lado._
   ↳ Se falhar: commitar/branch de segurança antes de refatorar `main_window.py`; se a janela não abrir, voltar ao estado anterior e mover os widgets em incrementos menores.

14. **Implementar a proporção dinâmica das colunas** — alternar 60/40 ↔ 40/60 via `QSplitter.setSizes()` (com `QPropertyAnimation`), acionada pelos sinais `editor_opened`/`editor_closed` do `EditorPanel`. _Concluído quando: abrir o editor alarga a coluna direita para ~60% e fechá-lo volta a ~40%._
   ↳ Se falhar (animação travada): usar `setSizes()` direto sem animação como fallback funcional; o efeito suave é secundário.

15. **Adicionar o rodapé/status** — incluir `QStatusBar` (ou rodapé equivalente) na janela. _Concluído quando: a barra de status aparece na base da janela._
   ↳ Se falhar: item de menor prioridade; anotar e seguir.

16. **[CRÍTICO] Criar `flownc/ui/components/compositor.py`** — dropdowns origem→destino, lista "Edições montadas", rascunho no fim e botão "+ adicionar outra edição"; emitir os mesmos sinais dos widgets atuais. _Concluído quando: o arquivo existe e o compositor emite os mesmos sinais que o `main_window` atual ao montar uma edição._
   ↳ Se falhar (sinal divergente quebra a lógica): manter a assinatura exata dos sinais/slots atuais; se preciso, adaptar dentro do componente em vez de mudar o `core`. Comparar com os `connect()` atuais de `main_window.py` antes de remover o widget antigo.

17. **[CRÍTICO] Criar `flownc/ui/components/program_list.py`** — lista de arquivos com `QCheckBox` e botão "✎ Editar" por linha; emitir os mesmos sinais atuais. _Concluído quando: o arquivo existe e a lista emite o mesmo sinal de "editar arquivo" do código atual ao clicar no botão da linha._
   ↳ Se falhar: igual à 16 — preservar a interface de sinais; testar a seleção de arquivos antes de descartar o widget antigo.

18. **Criar `flownc/ui/components/resumo.py`** — selo de estado (⚠/✓ via tokens warning/success), contadores Regras/Programas/Alterações, cartões de regra (editar/duplicar/excluir + borda inset âmbar em conflito), bloco "Editados → backup" (visível só após execução bem-sucedida) e botão "Executar Lote" (CTA escuro, altura `--h-cta`). _Concluído quando: o arquivo existe e o painel Resumo renderiza todos esses elementos._
   ↳ Se falhar: implementar os elementos em ordem de importância (botão Executar e contadores primeiro); anotar o que faltar.

19. **Conectar o `QStackedWidget` Resumo ↔ Editor no maestro** — em `main_window.py`, alternar entre `resumo.py` e `editor_panel.py` na coluna direita. _Concluído quando: clicar em "✎ Editar" troca a coluna direita para o editor e fechar volta ao Resumo._
   ↳ Se falhar: validar que o `EditorPanel` ainda recebe o arquivo correto; se a troca não ocorrer, conferir a conexão do sinal de seleção da `program_list`.

20. **[CRÍTICO] Verificar a Mudança B** — rodar `pytest flownc/tests/`, `mypy flownc/ --ignore-missing-imports` e `ruff check flownc/`. _Concluído quando: os três comandos terminam sem falhas._
   ↳ Se falhar: corrigir antes de arquivar; gate obrigatório. Atenção especial a testes de UI (`test_ui_smoke.py`) que dependem dos sinais migrados.

21. **Arquivar a Mudança B** — rodar `/opsx:archive redesign-layout-paineis`. _Concluído quando: a change vai para o histórico de arquivadas._
   ↳ Se falhar: reportar o erro do comando; não mover pastas à mão.

### Mudança C — Editor, limpeza e entrega (`redesign-editor-limpeza`)

22. **Propor a Mudança C** — rodar `/opsx:propose` com o nome `redesign-editor-limpeza`, cobrindo as etapas 24–35. _Concluído quando: a pasta `openspec/changes/redesign-editor-limpeza/` existe com todos os artefatos._
   ↳ Se falhar: revisar a descrição e repropor.

23. **Validar a proposta da Mudança C** — conferir que o `/opsx:propose` terminou sem erros e que `proposal.md`, `design.md`, `tasks.md` e `specs/` existem e estão coerentes (reforço opcional: `openspec validate redesign-editor-limpeza`). _Concluído quando: os quatro artefatos existem e nenhuma validação aponta erro._
   ↳ Se falhar: ajustar o artefato apontado e revalidar antes de codar (Etapa 24).

> **Etapas 24–30 (implementação) são as tarefas do `tasks.md` desta mudança e são executadas dentro de `/opsx:apply redesign-editor-limpeza`.**

24. **Estilizar o cabeçalho do editor** — em `editor_panel.py`, adicionar `QLabel` com nome do arquivo + `QLabel` menor "salva direto, sem cópia" (cor `--color-text-tertiary`). _Concluído quando: o cabeçalho do editor mostra nome do arquivo e o subtítulo._
   ↳ Se falhar: não mexer na lógica de save de `inplace_save.py`; só camada visual.

25. **Montar a toolbar do localizador** — em `editor_panel.py`, adicionar `QComboBox` da biblioteca de termos, `QLineEdit` de busca, `QLabel` contador "N/M", botões anterior/próxima, "Substituir todos" e "Um a um". _Concluído quando: a toolbar exibe todos esses controles._
   ↳ Se falhar: reaproveitar os controles de busca já existentes no `editor_panel.py` antes de criar novos; preservar os handlers atuais.

26. **Destacar ocorrências no editor** — aplicar um `QSyntaxHighlighter` no `QPlainTextEdit` com `--color-occurrence` nas ocorrências e `--color-occurrence-current` na atual. _Concluído quando: ao buscar um termo, as ocorrências ficam realçadas e a navegada com cor distinta._
   ↳ Se falhar (highlight pesado em arquivos grandes): limitar o realce à viewport visível ou desligar acima de N linhas; funcionalidade de busca não pode travar.

27. **Adicionar o gutter de numeração de linha** — implementar `paintEvent` customizado no editor para a régua de números. _Concluído quando: a coluna de números de linha aparece à esquerda do texto._
   ↳ Se falhar: item cosmético; anotar e seguir sem o gutter.

28. **Remover a contagem automática de ocorrências do painel principal** — apagar de `main_window.py`/`compositor.py` as chamadas que contam e exibem ocorrências fora do editor. _Concluído quando: nenhuma contagem de ocorrências aparece fora da toolbar do editor._
   ↳ Se falhar (algo deixa de funcionar ao remover): conferir se a contagem alimentava outra lógica antes de apagar; remover só a exibição, não o cálculo se ele for usado em outro lugar.

29. **Remover os widgets redundantes do v2** — apagar a faixa de conflito extra (mantendo só o cartão com borda inset âmbar), o subtítulo de máquina no header (se existir) e o indicador circular. _Concluído quando: esses widgets não aparecem mais na UI._
   ↳ Se falhar: remover um widget por vez e rodar o app entre cada remoção para isolar quebras.

30. **Substituir valores fixos restantes por tokens** — trocar qualquer cor/fonte/espaçamento hardcoded remanescente pelos tokens de `theme.py`. _Concluído quando: uma busca por hex de cor/px fixos nos arquivos de UI não retorna ocorrências de estilo._
   ↳ Se falhar (token faltando): adicionar o token em `theme.py` em vez de manter o valor fixo.

31. **[CRÍTICO] Verificar a Mudança C** — rodar `pytest flownc/tests/`, `mypy flownc/ --ignore-missing-imports` e `ruff check flownc/`. _Concluído quando: os três comandos terminam sem falhas._
   ↳ Se falhar: corrigir antes de buildar; gate obrigatório. Não gerar EXE com testes vermelhos.

32. **Fazer o smoke test manual** — abrir o app e comparar configuração, edição de arquivo e execução de lote lado a lado com `mockups/painel-final.v2.html`, anotando divergências. _Concluído quando: cada seção foi percorrida e as divergências foram anotadas (ou nenhuma encontrada)._
   ↳ Se falhar (divergência relevante): registrar como ajuste e voltar à etapa visual correspondente antes de buildar.

33. **[CRÍTICO] Rebuildar o EXE** — rodar `pyinstaller flownc/FlowNC.spec` dentro da pasta `flownc/`. _Concluído quando: `flownc/dist/FlowNC/FlowNC.exe` existe com data de modificação atual._
   ↳ Se falhar (erro de build): ler o log do PyInstaller; conferir se as fontes/assets novos estão declarados em `FlowNC.spec` (`datas`). Não entregar EXE que não abre.

34. **[CRÍTICO] Preservar o EXE antigo** — renomear o EXE `CNC_BatchEditor` para `CNC_BatchEditor_OLD.exe` (ou mover para subpasta `antigo/` na Área de Trabalho), sem deletar. _Concluído quando: o EXE antigo existe com o novo nome/local e nada foi apagado._
   ↳ Se falhar: passo irreversível se deletar — em caso de dúvida, só copiar/renomear, nunca remover. Fazer ANTES de copiar o novo (Etapa 35) para não sobrescrever.

35. **Entregar o novo EXE** — copiar `flownc/dist/FlowNC/FlowNC.exe` e a pasta `FlowNC/` para a Área de Trabalho, substituindo o atalho anterior. _Concluído quando: o novo `FlowNC.exe` abre a partir da Área de Trabalho._
   ↳ Se falhar (arquivo em uso): fechar o app aberto antes de copiar; confirmar que o antigo já foi preservado (Etapa 34).

36. **Arquivar a Mudança C** — rodar `/opsx:archive redesign-editor-limpeza`. _Concluído quando: a change vai para o histórico de arquivadas._
   ↳ Se falhar: reportar o erro do comando; não mover pastas à mão.

## Dependências

- **Mudança A (Etapas 1–9):** Etapa 1 não depende de nada. Etapas 3–7 dependem da proposta validada (Etapas 1–2). A Etapa 3 (`theme.py`) é a base de **todo** o visual: as Etapas 6–7 e todas as etapas das Mudanças B e C consomem os tokens criados nela. As fontes (Etapa 4) precisam existir antes de registrá-las (Etapa 5). O QSS (Etapa 6) precisa de `theme.py` (Etapa 3). Verificação (8) e arquivamento (9) fecham a mudança.
- **Mudança B (Etapas 10–21):** depende da Mudança A arquivada (Etapa 9). O esqueleto de colunas (Etapa 13) é pré-requisito da proporção dinâmica (14), dos componentes de coluna (16–18) e do stacked widget (19). O header (12), o compositor (16), a lista (17) e o resumo (18) podem ser feitos em sequência. Verificação (20) e arquivamento (21) fecham a mudança.
- **Mudança C (Etapas 22–36):** depende da Mudança B arquivada (Etapa 21). A estilização do editor (24–27) depende da alternância Resumo ↔ Editor já existir (Etapa 19). A limpeza (28–30) depende das telas já montadas (Etapas 16–18, 24–27). O build/entrega (33–35) depende de todas as anteriores; preservar o EXE antigo (34) precede entregar o novo (35).
- **Regra OpenSpec:** cada mudança (A → B → C) é **proposta + validada** (`/opsx:propose` → `/opsx:validate`) antes de implementar e **arquivada** (`/opsx:archive`) antes de começar a próxima. Uma mudança por vez.

## Tecnologias

- **Linguagem/UI:** Python 3.11+, PySide6 (Qt Widgets).
- **Estilo:** folha QSS central (`flownc/ui/style.qss`) + módulo de tema/tokens (`flownc/ui/theme.py`, novo); fontes IBM Plex Sans / IBM Plex Mono (carregadas via `QFontDatabase`).
- **Arquitetura:** componentes separados em `flownc/ui/components/` (novos: `header.py`, `compositor.py`, `program_list.py`, `resumo.py`); `flownc/ui/main_window.py` vira o "maestro" (instancia componentes, conecta sinais/slots, gerencia o `QStackedWidget` Resumo ↔ Editor e o `QSplitter` de proporção dinâmica).
- **Editor:** `flownc/ui/editor_panel.py` (já existe, será estilizado na Mudança C) + `core/inplace_save.py` (já existe, não muda).
- **Build:** PyInstaller (`flownc/FlowNC.spec`) → `flownc/dist/FlowNC/FlowNC.exe`.
- **Verificação:** `pytest flownc/tests/` (121+ testes) + `mypy flownc/ --ignore-missing-imports` + `ruff check flownc/`; todos devem passar antes de arquivar cada mudança.
- **Processo:** OpenSpec (propose → apply → archive), 3 mudanças sequenciais (`redesign-fundacao-visual` → `redesign-layout-paineis` → `redesign-editor-limpeza`).
- **Referência de design:** `mockups/painel-final.v2.html` (único modelo válido; design antigo descartado).
- **Plano detalhado (companheiro):** `docs/PLANO-REDESIGN-VISUAL-V2.md`.
