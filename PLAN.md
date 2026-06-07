# Plano de Execução

status: pronto

## Estado de execução e ordem recomendada (2026-06-07)

> **Leia primeiro — o ponto de partida.** As Mudanças **A e B já estão IMPLEMENTADAS e ARQUIVADAS** no OpenSpec:
> - A → `openspec/changes/archive/2026-06-06-redesign-fundacao-visual`
> - B → `openspec/changes/archive/2026-06-07-redesign-layout-principal` (atenção ao nome: foi arquivada como **`redesign-layout-principal`**, não `redesign-layout-paineis`).
>
> Por isso as **Etapas 1–21 são registro histórico** — **não repropor nem reimplementar** (rodar `/opsx:propose redesign-fundacao-visual` ou `redesign-layout-paineis` recriaria mudanças já encerradas e geraria conflito). A execução real começa nas **pendências de fidelidade** ao mockup e segue por **C** e **D**.
>
> **Crítico:** o **empacotamento (itens 7a–7e)** e a **Seed Fanuc (itens 9a–9e)** não são opcionais nem "do fim". Têm de estar prontos **antes de qualquer build de entrega** (Etapas 33 **e** 49); caso contrário o EXE sai "pelado" (sem tema, fontes, biblioteca ou perfil em outro PC).

**Ordem recomendada (do estado atual até a entrega):**
1. **Fidelidade ao mockup** — fechar as divergências do que A/B entregaram: Compositor no formato `editlist` (Próximo passo **1**), header (**2**), lista de programas sem checkbox duplo (**3**), orquestrador `publish_batch` + contador `Alterações` (**4**). Esses pendentes pertencem ao que A/B entregaram com divergência; agora estão em formato de etapa (critério + fallback) na seção "Próximos passos".
2. **Mudança C** — Editor, limpeza e entrega (Etapas 22–36): glifos/realce/stepbar do editor (≈ Próximo passo **5**), remoção de redundâncias, smoke. **Não rodar o build da Etapa 33 sem o passo 3 abaixo.**
3. **Empacotamento + Seed** — Próximos passos **7** (7a–7e) e **9** (9a–9e). **Pré-requisito do primeiro build de entrega (Etapa 33).**
4. **Mudança D** — Segurança e polimento (Etapas 37–50): modais dos 4 overlays e dropdowns `libdrop` (≈ Próximo passo **6**), persistência de perfil (**8**), entrega final.

> Cada item acima já tem critério de conclusão e fallback no bloco correspondente (Etapas C/D e Próximos passos 1–9). Esta seção fixa só **o que já está pronto**, **os nomes reais** e **a ordem**.

## Objetivo

Implementar o **novo design já aprovado** (mockup `mockups/painel-final.v2.html`) no app FlowNC, deixando a interface idêntica ao mockup e preservando a lógica atual (perfis, execução de substituições, biblioteca e o editor por arquivo já existente). O design antigo está **totalmente descartado** e não serve mais de referência.

> **Como fica na nova atualização (verificações):** as **verificações automáticas de perfil** (conferir se o programa tem/não tem certo código — `must_exist`/`must_not_exist`) **saem do escopo** e não são mais preservadas. O sistema novo não confere nada sozinho: a biblioteca vira uma lista de **código + descrição curta, totalmente editável**; o operador escolhe um código (vai ao campo de origem) e outro (vai ao campo de destino), montando cada substituição manualmente. Onde este plano ainda citar "verificações" como lógica a manter, vale esta direção.

> **Decisão de modelo de dados da biblioteca (registrada):** o design aprovado fixa o modelo **"código + descrição curta" com montagem manual** (o operador escolhe um código para a origem e outro para o destino). A biblioteca é, na prática, um **dicionário de códigos** — cada código com o que ele significa —, não uma lista de trocas prontas. A **lógica interna não muda**: ao montar origem→destino, a regra continua sendo um par "trocar de X por Y" em tempo de execução.
>
> **Como os dados foram gravados (2026-06-07):** a biblioteca (89 códigos) está no schema `find`=código, `replace`=**vazio**, `label`=descrição, `tags`=categoria. O `replace` fica **vazio de propósito**: quem define o destino é o operador, na hora. Isso é o meio-termo combinado (não quebra o `load_library` atual e já está no formato certo para a tela nova).
>
> ⚠️ **AVISO IMPORTANTE — comportamento transitório (ler antes de usar/mexer):** enquanto o **Compositor não for reescrito** (Próximo passo 1), a tela de montar edição **ainda é a antiga**, que espera um par "de → para" pronto vindo da biblioteca. Como o `replace` está vazio, **escolher um código da biblioteca direto na tela antiga pode virar "trocar o código por nada" (apagar)** em vez de trocar. **Não usar os códigos da biblioteca direto na tela antiga até a reescrita.** A tela nova terá **dois campos separados** (código que sai / código que entra) e elimina o risco. Os dados estão corretos; o que falta é só a tela nova (já prevista no Próximo passo 1). **Não "consertar" isso preenchendo o `replace` na biblioteca** — isso voltaria ao modelo de pares prontos, que foi descartado.

Forma de execução livre (criar documentos, escrever código novo, reprogramar ou reconstruir do zero) — o foco é colocar o novo design em funcionamento no sistema atual.

## Glossário

- **Modo edição:** estado em que `editor_panel.py` está visível na coluna direita (o usuário clicou em "✎ Editar" em um arquivo). Ao sair do editor (fechar ou voltar), o app retorna ao modo padrão (coluna direita = Resumo).
- **Proporção dinâmica:** as duas colunas ficam lado a lado num `QSplitter(Qt.Horizontal)` (esquerda e direita). No modo padrão ficam 60 % esquerda / 40 % direita; no modo edição ficam 40 % / 60 %. A troca é feita via `QSplitter.setSizes()` com `QPropertyAnimation` ou animação manual no `resizeEvent`. "Vertical/horizontal" aqui sempre se refere à **orientação do QSplitter**: para colunas lado a lado a orientação é **horizontal**.
- **Fundação visual:** aplicar tokens (cores, fontes, espaçamentos, cantos, alturas do mockup) ao app via `theme.py` + QSS. **Não** alterar posição, número ou hierarquia de widgets existentes — só aparência (cores de fundo, bordas, fontes, tamanho de controles).
- **Layout:** posição, número e hierarquia dos widgets (`QVBoxLayout`, `QHBoxLayout`, `QSplitter`, `QStackedWidget`, etc.). Mudanças de layout pertencem à Mudança B, não à A.
- **Rascunho / "em edição":** a linha de input ainda em construção pelo usuário no compositor de edições — sempre renderizada no fim da lista "Edições montadas" com visual diferenciado (fundo `--color-bg-subtle`, borda tracejada). No mockup essa linha é a classe **`em edição`** (o termo "rascunho" é só o apelido interno deste plano).
- **Bloco "Editados → backup":** área na coluna direita que lista os nomes dos arquivos que foram salvos em lote com o caminho da pasta de backup criada. Aparece só depois de uma execução bem-sucedida; permanece até o app fechar ou uma nova execução começar.
- **Lógica atual:** todo o código em `flownc/core/` (matcher, inplace_save, perfis) e os sinais/slots que conectam a UI à lógica em `main_window.py`. Nada disso muda de comportamento — só muda de onde é chamado (o "maestro" vira `main_window.py` refatorado, que instancia os componentes novos e repassa os mesmos sinais/slots). **Como fica na nova atualização (verificações):** o `core/verifier.py` e as verificações automáticas de perfil **não fazem mais parte da lógica a preservar** — saem do escopo. A lógica mantida cobre só busca/substituição (`matcher`), salvamento por arquivo (`inplace_save`) e os perfis como dado de configuração, sem conferência embutida.
- **Comandos de verificação (lint/testes):** sempre rodar na raiz do projeto — `pytest flownc/tests/` · `mypy flownc/ --ignore-missing-imports` · `ruff check flownc/`.
- **Fluxo OpenSpec por mudança:** cada Mudança segue três fases. (1) **Propor** com a skill `/opsx:propose` — gera `proposal.md`, `design.md`, `specs/` e `tasks.md` na pasta `openspec/changes/<nome>/`. (2) **Implementar** com a skill `/opsx:apply <nome>` — ela percorre o `tasks.md` gerado; as etapas de implementação deste plano **são** essas tarefas e são executadas dentro do `/opsx:apply`. (3) **Arquivar** com `/opsx:archive <nome>`. **Validar a proposta** significa conferir que o `/opsx:propose` terminou sem apontar erros e que os artefatos acima existem e estão coerentes; se houver a CLI do OpenSpec instalada, rodar também `openspec validate <nome>` como reforço. **Não existe skill `/opsx:validate`** — a "validação" é essa conferência manual (+ CLI opcional).

## Etapas

> Convenção: cada etapa = **um verbo de ação** + **um critério de conclusão mensurável** (_itálico_) + **fallback** (`↳ Se falhar:`). Etapas marcadas `[CRÍTICO]` não podem avançar com falha: parar, reportar ao Mestre e só seguir após resolver. Regra geral de parada segura: nenhum `git commit` enquanto a verificação (pytest/mypy/ruff) da mudança não estiver verde; em qualquer falha não prevista, parar e reportar em vez de improvisar.

### Mudança A — Fundação visual (`redesign-fundacao-visual`) — ✅ CONCLUÍDA E ARQUIVADA

> Implementada e **arquivada em 2026-06-06** (`openspec/changes/archive/2026-06-06-redesign-fundacao-visual`). As Etapas 1–9 abaixo são **registro histórico** do que foi feito — **não reexecutar**.

1. **Propor a Mudança A** — rodar `/opsx:propose` com o nome `redesign-fundacao-visual`, descrevendo: criar `theme.py`, carregar fontes IBM Plex, gerar QSS central, aplicar sem mudar layout. _Concluído quando: a pasta `openspec/changes/redesign-fundacao-visual/` existe com `proposal.md`, `design.md`, `tasks.md` e `specs/`._
   ↳ Se falhar: revisar a descrição passada ao comando e repropor; não criar a pasta à mão.

2. **Validar a proposta da Mudança A** — conferir que o `/opsx:propose` terminou sem erros e que `proposal.md`, `design.md`, `tasks.md` e `specs/` existem e estão coerentes (se a CLI estiver instalada, rodar `openspec validate redesign-fundacao-visual` como reforço). _Concluído quando: os quatro artefatos existem e nenhuma validação aponta erro._
   ↳ Se falhar: ler o erro, ajustar o artefato apontado (`proposal`/`specs`/`tasks`) e revalidar; não avançar para a implementação (Etapa 3) com a proposta inválida.

> **Etapas 3–7 (implementação) são as tarefas do `tasks.md` desta mudança e foram executadas dentro de `/opsx:apply redesign-fundacao-visual`.**

3. **[CRÍTICO] Criar `flownc/ui/theme.py`** — definir, como constantes Python, todos os tokens do mockup: cores `--color-*`, tipografia `--t-*`, espaçamentos `--sp-*`, raios `--radius-*`, alturas `--h-*`, dimensões `--dim-*`. _Concluído quando: o arquivo `flownc/ui/theme.py` existe e `import flownc.ui.theme` não levanta erro._
   ↳ Se falhar: conferir os valores direto no `<style>` de `mockups/painel-final.v2.html`; faltando algum token, criar mesmo assim com os que existem e anotar o pendente. Base de todo o visual — não prosseguir para o QSS sem os tokens essenciais de cor e tipografia.

4. **Adicionar as fontes IBM Plex ao projeto** — colocar os arquivos `.ttf` de IBM Plex Sans e IBM Plex Mono em `flownc/assets/fonts/`. _Concluído quando: os arquivos `.ttf` das duas famílias existem em `flownc/assets/fonts/`._
   ↳ Se falhar (sem acesso aos `.ttf`): registrar como blocker e seguir usando fallback de fonte do sistema (`Segoe UI` / `Consolas`) nos tokens de tipografia; trocar para IBM Plex quando os arquivos chegarem. **(Estado real: ainda pendente — `assets/fonts/` só tem `.gitkeep`; ver Próximo passo 7d.)**

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

### Mudança B — Layout e painéis (`redesign-layout-principal`) — ✅ CONCLUÍDA E ARQUIVADA

> Implementada e **arquivada em 2026-06-07** sob o nome **`redesign-layout-principal`** (`openspec/changes/archive/2026-06-07-redesign-layout-principal`). Etapas 10–21 = **registro histórico**. As **pendências de fidelidade** desta entrega (Compositor, header, lista com checkbox duplo) estão nos **Próximos passos 1–3**, já em formato de etapa.

10. **Propor a Mudança B** — rodar `/opsx:propose` com o nome `redesign-layout-principal`, descrevendo: criar `flownc/ui/components/` (`header.py`, `compositor.py`, `program_list.py`, `summary.py`), refatorar `main_window.py` como "maestro", colunas dinâmicas. _Concluído quando: a pasta `openspec/changes/redesign-layout-principal/` existe com todos os artefatos._
    ↳ Se falhar: revisar a descrição e repropor; não editar artefatos à mão.

11. **Validar a proposta da Mudança B** — conferir que o `/opsx:propose` terminou sem erros e que `proposal.md`, `design.md`, `tasks.md` e `specs/` existem e estão coerentes (reforço opcional: `openspec validate redesign-layout-principal`). _Concluído quando: os quatro artefatos existem e nenhuma validação aponta erro._
    ↳ Se falhar: ajustar o artefato apontado e revalidar antes de codar (Etapa 12).

> **Etapas 12–19 (implementação) são as tarefas do `tasks.md` desta mudança e foram executadas dentro de `/opsx:apply redesign-layout-principal`.**

12. **Criar `flownc/ui/components/header.py`** — header fixo com logo FlowNC, título "FlowNC", `QComboBox` de máquina e botões de biblioteca. _Concluído quando: o arquivo existe e a classe de header instancia sem erro._
    ↳ Se falhar (logo indisponível): usar placeholder de texto "FlowNC" e seguir; trocar pelo asset depois.

13. **Montar o esqueleto de 2 colunas em `main_window.py`** — adicionar um `QSplitter(Qt.Horizontal)` (colunas lado a lado) com dois painéis filhos (esquerda e direita). _Concluído quando: o app abre exibindo duas colunas lado a lado._
    ↳ Se falhar: commitar/branch de segurança antes de refatorar `main_window.py`; se a janela não abrir, voltar ao estado anterior e mover os widgets em incrementos menores.

14. **Implementar a proporção dinâmica das colunas** — alternar 60/40 ↔ 40/60 via `QSplitter.setSizes()` (com `QPropertyAnimation`), acionada pelos sinais `editor_opened`/`editor_closed` do `EditorPanel`. _Concluído quando: abrir o editor alarga a coluna direita para ~60% e fechá-lo volta a ~40%._
    ↳ Se falhar (animação travada): usar `setSizes()` direto sem animação como fallback funcional; o efeito suave é secundário.

15. **Adicionar o rodapé/status** — incluir `QStatusBar` (ou rodapé equivalente) na janela. _Concluído quando: a barra de status aparece na base da janela._
    ↳ Se falhar: item de menor prioridade; anotar e seguir.

16. **[CRÍTICO] Criar `flownc/ui/components/compositor.py`** — dropdowns origem→destino, lista "Edições montadas", rascunho no fim e botão "+ adicionar outra edição"; emitir os mesmos sinais dos widgets atuais. _Concluído quando: o arquivo existe e o compositor emite os mesmos sinais que o `main_window` atual ao montar uma edição._
    ↳ Se falhar (sinal divergente quebra a lógica): manter a assinatura exata dos sinais/slots atuais; se preciso, adaptar dentro do componente em vez de mudar o `core`. Comparar com os `connect()` atuais de `main_window.py` antes de remover o widget antigo. **(Entregue com divergências de fidelidade — ver Próximo passo 1.)**

17. **[CRÍTICO] Criar `flownc/ui/components/program_list.py`** — lista de arquivos com `QCheckBox` e botão "✎ Editar" por linha; emitir os mesmos sinais atuais. _Concluído quando: o arquivo existe e a lista emite o mesmo sinal de "editar arquivo" do código atual ao clicar no botão da linha._
    ↳ Se falhar: igual à 16 — preservar a interface de sinais; testar a seleção de arquivos antes de descartar o widget antigo. **(Entregue com checkbox duplicado — ver Próximo passo 3.)**

18. **Criar `flownc/ui/components/summary.py`** — selo de estado (⚠/✓ via tokens warning/success), contadores Regras/Programas/Alterações, cartões de regra (editar/duplicar/excluir + borda inset âmbar em conflito), bloco "Editados → backup" (visível só após execução bem-sucedida) e botão "Executar Lote" (CTA escuro, altura `--h-cta`). _Concluído quando: o arquivo existe e o painel Resumo renderiza todos esses elementos._
    ↳ Se falhar: implementar os elementos em ordem de importância (botão Executar e contadores primeiro); anotar o que faltar. **(Nome real do arquivo: `summary.py`. Entregue com divergências — ver Próximo passo 2/4.)**

19. **Conectar o `QStackedWidget` Resumo ↔ Editor no maestro** — em `main_window.py`, alternar entre `summary.py` e `editor_panel.py` na coluna direita. _Concluído quando: clicar em "✎ Editar" troca a coluna direita para o editor e fechar volta ao Resumo._
    ↳ Se falhar: validar que o `EditorPanel` ainda recebe o arquivo correto; se a troca não ocorrer, conferir a conexão do sinal de seleção da `program_list`.

20. **[CRÍTICO] Verificar a Mudança B** — rodar `pytest flownc/tests/`, `mypy flownc/ --ignore-missing-imports` e `ruff check flownc/`. _Concluído quando: os três comandos terminam sem falhas._
    ↳ Se falhar: corrigir antes de arquivar; gate obrigatório. Atenção especial a testes de UI (`test_ui_smoke.py`) que dependem dos sinais migrados.

21. **Arquivar a Mudança B** — rodar `/opsx:archive redesign-layout-principal`. _Concluído quando: a change vai para o histórico de arquivadas._
    ↳ Se falhar: reportar o erro do comando; não mover pastas à mão.

### Mudança C — Editor, limpeza e entrega (`redesign-editor-limpeza`)

> **Próxima a executar** (depois de fechar os Próximos passos 1–4 de fidelidade). **Atenção:** o build da Etapa 33 só deve rodar com o **empacotamento (7a–7e) e a Seed Fanuc (9a–9e) já aplicados**, senão o EXE sai "pelado".

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
    ↳ Se falhar (algo deixa de funcionar ao remover): conferir se a contagem alimentava outra lógica antes de apagar; remover só a exibição, não o cálculo se ele for usado em outro lugar. (`count_occurrences` vive em `core/scan.py` e é usado em `main_window.py:276` — manter a função, remover só a exibição fora do editor.)

29. **Remover os widgets redundantes do v2** — apagar a faixa de conflito extra (mantendo só o cartão com borda inset âmbar), o subtítulo de máquina no header (se existir) e o indicador circular. _Concluído quando: esses widgets não aparecem mais na UI._
    ↳ Se falhar: remover um widget por vez e rodar o app entre cada remoção para isolar quebras.

30. **Substituir valores fixos restantes por tokens** — trocar qualquer cor/fonte/espaçamento hardcoded remanescente pelos tokens de `theme.py`. _Concluído quando: uma busca por hex de cor/px fixos nos arquivos de UI não retorna ocorrências de estilo._
    ↳ Se falhar (token faltando): adicionar o token em `theme.py` em vez de manter o valor fixo.

31. **[CRÍTICO] Verificar a Mudança C** — rodar `pytest flownc/tests/`, `mypy flownc/ --ignore-missing-imports` e `ruff check flownc/`. _Concluído quando: os três comandos terminam sem falhas._
    ↳ Se falhar: corrigir antes de buildar; gate obrigatório. Não gerar EXE com testes vermelhos.

32. **Fazer o smoke test manual** — abrir o app e comparar configuração, edição de arquivo e execução de lote lado a lado com `mockups/painel-final.v2.html`, anotando divergências. _Concluído quando: cada seção foi percorrida e as divergências foram anotadas (ou nenhuma encontrada)._
    ↳ Se falhar (divergência relevante): registrar como ajuste e voltar à etapa visual correspondente antes de buildar.

33. **[CRÍTICO] Rebuildar o EXE** — rodar `pyinstaller flownc/FlowNC.spec` dentro da pasta `flownc/`. **Pré-requisito: empacotamento (7a–7e) e Seed Fanuc (9a–9e) já aplicados**, senão o EXE sai "pelado" (sem tema/fontes/dados). _Concluído quando: `flownc/dist/FlowNC/FlowNC.exe` existe com data de modificação atual._
    ↳ Se falhar (erro de build): ler o log do PyInstaller; conferir se as fontes/assets novos estão declarados em `FlowNC.spec` (`datas`). Não entregar EXE que não abre.

34. **[CRÍTICO] Preservar o EXE antigo** — renomear o EXE `CNC_BatchEditor` para `CNC_BatchEditor_OLD.exe` (ou mover para subpasta `antigo/` na Área de Trabalho), sem deletar. _Concluído quando: o EXE antigo existe com o novo nome/local e nada foi apagado._
    ↳ Se falhar: passo irreversível se deletar — em caso de dúvida, só copiar/renomear, nunca remover. Fazer ANTES de copiar o novo (Etapa 35) para não sobrescrever.

35. **Entregar o novo EXE** — copiar `flownc/dist/FlowNC/FlowNC.exe` e a pasta `FlowNC/` para a Área de Trabalho, substituindo o atalho anterior. _Concluído quando: o novo `FlowNC.exe` abre a partir da Área de Trabalho._
    ↳ Se falhar (arquivo em uso): fechar o app aberto antes de copiar; confirmar que o antigo já foi preservado (Etapa 34).

36. **Arquivar a Mudança C** — rodar `/opsx:archive redesign-editor-limpeza`. _Concluído quando: a change vai para o histórico de arquivadas._
    ↳ Se falhar: reportar o erro do comando; não mover pastas à mão.

### Mudança D — Segurança e polimento (`redesign-seguranca-polimento`)

> Origem: relatório de revisão técnica (2026-06-07). Cobre as camadas de **segurança de dados** e **polimento de UX** não detalhadas nas Mudanças A–C. É **aditiva**: não altera nenhuma etapa anterior (1–36) nem renumera nada. Onde um item dialoga com os "Próximos passos para fechar 100%" (modais dos 4 overlays, dropdowns pesquisáveis `.libdrop`, publicação real via `publish_batch`), esta mudança **estende** o que já estiver feito — não duplica.

37. **Propor a Mudança D** — rodar `/opsx:propose` com o nome `redesign-seguranca-polimento`, descrevendo as etapas 39–47 (confirmação de save, robustez de gravação, bloqueio de UI na publicação, atalhos, estados vazios, diff colorido, modais estilizados, tooltips, polimentos opcionais). _Concluído quando: a pasta `openspec/changes/redesign-seguranca-polimento/` existe com `proposal.md`, `design.md`, `tasks.md` e `specs/`._
    ↳ Se falhar: revisar a descrição e repropor; não criar a pasta à mão.

38. **Validar a proposta da Mudança D** — conferir que o `/opsx:propose` terminou sem erros e que `proposal.md`, `design.md`, `tasks.md` e `specs/` existem e estão coerentes (reforço opcional: `openspec validate redesign-seguranca-polimento`). _Concluído quando: os quatro artefatos existem e nenhuma validação aponta erro._
    ↳ Se falhar: ajustar o artefato apontado e revalidar antes de codar (Etapa 39).

> **Etapas 39–47 (implementação) são as tarefas do `tasks.md` desta mudança e são executadas dentro de `/opsx:apply redesign-seguranca-polimento`.**

39. **Adicionar confirmação ao primeiro salvamento do editor** — em `editor_panel.py`, antes do save in-place, exibir um modal "Tem certeza? Esta ação sobrescreve o arquivo original, sem cópia." na primeira vez de cada sessão, com opção "não perguntar de novo nesta sessão". _Concluído quando: o primeiro `Salvar` da sessão abre o modal e, confirmado, grava normalmente; o segundo save não repergunta._
    ↳ Se falhar: não tocar na lógica de `inplace_save.py` — o modal é só uma porta antes da chamada de save. Em dúvida, manter o modal sempre (mais seguro que nunca perguntar).

40. **[CRÍTICO] Tratar erros de gravação (arquivo em uso / rede)** — capturar `PermissionError`/`OSError` no save do editor e na publicação do lote; mostrar mensagem clara ("arquivo aberto em outro programa" / "falha de gravação na rede") e, no lote, **parar com segurança preservando o backup já criado** e informando o caminho dele. _Concluído quando: simular um arquivo bloqueado/sem permissão exibe a mensagem (sem travar o app) e, no lote, o backup permanece e o caminho é mostrado._
    ↳ Se falhar: como o save do editor é atômico (temp + rename), um erro não corrompe o original — garantir ao menos a mensagem; o rollback do lote é o ponto crítico, não pode deixar arquivos pela metade sem avisar.

41. **Bloquear a UI durante a publicação** — enquanto o lote grava, desabilitar a janela principal (`setEnabled(False)`) com overlay/spinner de "Processando", reabilitando ao terminar (sucesso ou erro). _Concluído quando: durante a publicação a janela fica inerte a cliques e volta ao normal ao fim._
    ↳ Se falhar: no mínimo desabilitar o botão "Executar Lote" durante a operação para evitar duplo-clique. Complementa (não duplica) os overlays previstos nos "Próximos passos".

42. **Implementar atalhos de teclado** — registrar `QShortcut` para `Ctrl+S` (salvar no editor), `Ctrl+F` (focar busca), `Ctrl+H` (substituir), `Esc` (fechar modal/editor) e `F3` (próxima ocorrência). _Concluído quando: cada atalho dispara a ação correspondente com o editor aberto._
    ↳ Se falhar: priorizar `Ctrl+S` e `Esc` (os mais usados) e anotar os demais.

43. **Tratar estados vazios** — exibir mensagem de orientação quando não há programas carregados (área da lista), a biblioteca está vazia (dropdowns) e a busca do editor não retorna ocorrências (toolbar). _Concluído quando: cada um dos três casos mostra um texto de orientação em vez de área em branco._
    ↳ Se falhar: cobrir ao menos "nenhum programa carregado" (o mais visível ao abrir o app). A biblioteca vazia é mitigada pela Seed Fanuc (Próximo passo 9), mas a mensagem vale como rede de segurança.

44. **Destacar diferenças no preview do lote** — na pré-visualização, realçar em verde o conteúdo adicionado e em vermelho o removido na linha (tokens `--color-success`/`--color-danger`), em vez de só exibir a linha nova. _Concluído quando: o preview mostra a diferença colorida por linha alterada._
    ↳ Se falhar (diff por caractere pesado): cair para realce da linha inteira (verde = nova, vermelho = antiga); o objetivo é a conferência rápida.

45. **Padronizar avisos e erros no estilo do app** — substituir os `QMessageBox` padrão do Windows remanescentes por modais estilizados com o QSS/tokens do mockup (mesma linguagem visual dos overlays). _Concluído quando: os diálogos de erro/aviso seguem o visual do app, sem caixas cinza padrão do sistema._
    ↳ Se falhar: estilizar via QSS o próprio `QMessageBox` como meio-termo; o essencial é a consistência visual.

46. **Adicionar tooltips na biblioteca** — exibir a descrição do código ao passar o mouse nos itens dos dropdowns origem/destino e nos cartões de regra. _Concluído quando: o tooltip aparece com a descrição cadastrada do código._
    ↳ Se falhar: item de menor prioridade; anotar e seguir.

47. **(Opcional / baixa prioridade) Polimentos finos** — avaliar e, se couber, aplicar: bloqueio de caracteres inválidos nos campos do compositor que possam corromper o `.NC`; revisão de contraste dos tokens para fábrica com alta luminosidade; micro-animações de `hover/active` nos botões via QSS. _Concluído quando: os três foram avaliados e aplicados ou registrados como dispensáveis._
    ↳ Se falhar/sem tempo: pular sem bloquear a entrega; nenhum é essencial.

48. **[CRÍTICO] Verificar a Mudança D** — rodar `pytest flownc/tests/`, `mypy flownc/ --ignore-missing-imports` e `ruff check flownc/`. _Concluído quando: os três comandos terminam sem falhas._
    ↳ Se falhar: corrigir antes de buildar; gate obrigatório. Não gerar EXE com testes vermelhos.

49. **[CRÍTICO] Rebuildar e entregar o EXE final** — rodar `pyinstaller flownc/FlowNC.spec`, conferir que o `.exe` abre e copiá-lo para a Área de Trabalho substituindo o anterior. **O EXE antigo `CNC_BatchEditor` já foi preservado na Etapa 34 — não repetir.** **Pré-requisito:** empacotamento (7a–7e) e Seed Fanuc (9a–9e) já aplicados, senão o EXE sai "pelado" (sem tema/dados). _Concluído quando: o novo `FlowNC.exe` (com segurança e polimento) abre a partir da Área de Trabalho._
    ↳ Se falhar (arquivo em uso): fechar o app antes de copiar. Se C e D forem executadas em sequência, pode-se buildar só uma vez aqui, no fim da D.

50. **Arquivar a Mudança D** — rodar `/opsx:archive redesign-seguranca-polimento`. _Concluído quando: a change vai para o histórico de arquivadas._
    ↳ Se falhar: reportar o erro do comando; não mover pastas à mão.

## Dependências

- **Mudança A (Etapas 1–9):** ✅ concluída/arquivada — não é mais dependência ativa. (Histórico: a Etapa 3 `theme.py` é a base de todo o visual; as fontes (4) precisam existir antes de registrá-las (5); o QSS (6) precisa de `theme.py` (3).)
- **Mudança B (Etapas 10–21):** ✅ concluída/arquivada (nome real `redesign-layout-principal`) — não é mais dependência ativa. Suas **pendências de fidelidade** (Compositor, header, lista) viraram os Próximos passos 1–3.
- **Pendências de fidelidade (Próximos passos 1–4):** dependem de A e B já entregues (estão). São o **primeiro bloco a executar** e antecedem a entrada formal na Mudança C.
- **Mudança C (Etapas 22–36):** depende das Mudanças A e B arquivadas (têm). Recomenda-se fechar os Próximos passos 1–4 antes. A estilização do editor (24–27) depende da alternância Resumo ↔ Editor já existir (Etapa 19, feita). A limpeza (28–30) depende das telas montadas. **O build (33) depende do empacotamento (7a–7e) e da Seed (9a–9e)**; preservar o EXE antigo (34) precede entregar o novo (35).
- **Mudança D (Etapas 37–50):** depende da Mudança C arquivada (Etapa 36). Aditiva e de baixo acoplamento. O rebuild/entrega final (49) reaproveita a preservação do EXE antigo já feita na Etapa 34 (não repetir) e **pressupõe o empacotamento (7a–7e) e a Seed Fanuc (9a–9e) já aplicados**.
- **Empacotamento (7a–7e) + Seed (9a–9e):** independentes entre si na maior parte, mas **ambos pré-requisitos de qualquer build de entrega (Etapas 33 e 49)**. O 7c (semear `data/` ao lado do `.exe`) e o 9b/9c se complementam.
- **Regra OpenSpec:** cada mudança nova (C, depois D) é **proposta + validada** (`/opsx:propose` + conferência manual; **não existe `/opsx:validate`**) antes de implementar e **arquivada** (`/opsx:archive`) antes de começar a próxima. Uma mudança por vez. A e B já cumpriram esse ciclo.

## Tecnologias

- **Linguagem/UI:** Python 3.11+, PySide6 (Qt Widgets).
- **Estilo:** folha QSS central (`flownc/ui/style.qss`) + módulo de tema/tokens (`flownc/ui/theme.py`); fontes IBM Plex Sans / IBM Plex Mono (carregadas via `QFontDatabase`; `.ttf` ainda pendentes — ver Próximo passo 7d).
- **Arquitetura:** componentes separados em `flownc/ui/components/` (`header.py`, `compositor.py`, `program_list.py`, `summary.py`); `flownc/ui/main_window.py` é o "maestro" (instancia componentes, conecta sinais/slots, gerencia o `QStackedWidget` Resumo ↔ Editor e o `QSplitter` de proporção dinâmica).
- **Editor:** `flownc/ui/editor_panel.py` (existe, será estilizado na Mudança C) + `core/inplace_save.py` (existe, não muda).
- **Build:** PyInstaller (`flownc/FlowNC.spec`) → `flownc/dist/FlowNC/FlowNC.exe`.
- **Verificação:** `pytest flownc/tests/` + `mypy flownc/ --ignore-missing-imports` + `ruff check flownc/`; todos devem passar antes de arquivar cada mudança. Usar o venv `flownc/.venv` (PySide6 6.11.1). _Nota: a auditoria de 2026-06-07 contou **123 funções `def test_`** em 17 arquivos; a contagem de **146** citada antes inclui casos parametrizados — **revalidar rodando o `pytest`** em vez de fixar o número._
- **Processo:** OpenSpec (propose → apply → archive). 4 mudanças: A (`redesign-fundacao-visual`, ✅) → B (`redesign-layout-principal`, ✅) → C (`redesign-editor-limpeza`) → D (`redesign-seguranca-polimento`).
- **Referência de design:** `mockups/painel-final.v2.html` (único modelo válido; o v1 `painel-final.html` foi deletado — deleção ainda não commitada). Tokens citados neste plano (`--color-occurrence`, `--h-cta`, `--color-success`, `--t-*`, `--sp-*`, `--radius-*`, etc.) e classes (`editlist`, `libdrop`, `em edição`, "Edições montadas", "Adicionar edição ao lote →") foram conferidos e **existem** no mockup.

> **Plano único.** Este `PLAN.md` é o único plano vivo. Os planos antigos/superados e o relatório item-a-item de conformidade foram arquivados em `_descarte/` (recuperáveis, fora do caminho). A seção abaixo consolida o estado real auditado.

## Estado real auditado (2026-06-07)

> Auditoria independente cruzando o app real, o mockup `mockups/painel-final.v2.html` e o código (venv `flownc/.venv` com PySide6 6.11.1). Consolida o antigo `docs/PLANO-CONFORMIDADE-MOCKUP-V2.md` (agora em `_descarte/`, com o detalhe item-a-item).

### Entregue e verificado em execução
- Mudanças A (fundação visual) e B (layout 2 colunas + 4 componentes + `QStackedWidget` Resumo↔Editor) entregues, **arquivadas** e **verificadas em execução** — `test_ui_smoke.py` instancia `MainWindow` + componentes e passa.
- Resumo recalcula de verdade: chip de estado (`validate_batch` em `core/batch.py:16`), contadores, cards `De→Para`, selo `✓ Validado`, meta de ocorrências (`count_occurrences` em `core/scan.py:16`).
  - → **Como fica na nova atualização (verificações):** o `selo ✓ Validado`/`validate_batch` deixa de representar verificação de perfil — não há mais conferência automática (`must_exist`/`must_not_exist`). O Resumo passa a refletir só o que o operador montou manualmente (contadores e cards `De→Para` das substituições origem→destino vindas da biblioteca editável); o chip de estado, se mantido, indica apenas se há edições prontas para publicar, não "programa aprovado".
- Editor por arquivo: varredura com borda CNC (`M8`≠`M80`), substituir todos/um a um, **salvar in-place atômico com conferência SHA** (CRLF preservado). Botão `✎ Editar` e duplo-clique abrem o editor correto.
- Preview com nomenclatura de publicação; QSS com tokens/hex do mockup.

### Divergências de fidelidade abertas (a fechar — viram os Próximos passos 1–6)
- **Header:** marca `⚙ FlowNC`/`LOCAL · OFFLINE` (vs `FlowNC`/`Editor de Lotes`); 2 botões fora do mockup (`Abrir pasta`/`Abrir programa(s)`); `Salvar perfil` à direita (mockup: à esquerda) e só avisa (stub `_save_profile_stub` em `main_window.py:550`); `+ Adicionar código` azul-claro (mockup: azul sólido) e sem comportamento próprio (abre a Biblioteca).
- **Compositor (painel 1):** título `Montar edição` sem número; `QComboBox` sem busca; lista plana sem rascunho/`✕` por linha; o botão adicionar **comete a regra na hora**; tem seletor `Escopo` **inexistente no mockup**; falta o CTA `Adicionar edição ao lote →` do painel 2.
- **Lista de programas:** **dois checkboxes por linha** (confirmado em render); título `Programas` (vs `Seleção de Programas`); metadados absolutos (vs relativos); sem `.file.off` na linha desmarcada.
- **Resumo:** escopo `todos/sel.` (vs `N programas`); ações `✎ ⧉ 🗑` decorativas (QLabel sem clique); selo de backup em 1 linha (vs escudo + 2 linhas); contador `Alterações` **superestima sob conflito** (contagem bruta, sem descontar supressão — 10 vs ~6 reais).
- **Editor:** glifos `🔎`/`◂▸` (vs `🔍`/`↑↓`); `Substituir por` único (vs `Substituir`+`por`); `Salvar` sem `💾`; **não realça todas as ocorrências**; `Um a um` por `QMessageBox` (vs stepbar inline).
- **Preview/publicação:** cores hardcoded (fora dos tokens); fluxo de 4 overlays do mockup ausente; o CTA ainda usa `_save()` legado (`main_window.py:466`, chamado em `:418`) em vez de `publish_batch` (`core/publisher.py:56`, backup versionado + SHA já prontos e testados, mas órfãos da UI). _Obs.: a UI já usa `build_plan`/`apply_edits` (`main_window.py:328`/`:329`); falta só trocar o salvamento final._

### Lacunas confirmadas (fora do mockup, mas bloqueiam a entrega)
- **Biblioteca de códigos:** ✅ **populada (2026-06-07)** — `data/library.json` e `data_default/library.json` têm **89 códigos** (53 G + 14 M + 6 eixos + 11 parâmetros + 2 variáveis + 3 fluxo), no schema `find`=código / `replace`="" / `label`=descrição / `tags`=categoria (meio-termo do modelo "código + descrição"). _Resta: o `ensure_seed` em runtime (9b/9c) caso `data/` seja apagada._
- **Perfis iniciais:** ✅ **criados (2026-06-07)** — `MAQ01`, `MAQ02`, `MAQ03` (apenas esses 3, sem regras nem verificações) em `data/presets/` e `data_default/presets/`. O exemplo `MAZAK_VTC530.json` foi removido (recuperável no git).
- **`FlowNC.spec datas=[]`** (linha 8): o EXE não inclui `ui/style.qss`, `data/` nem fontes → roda sem tema/perfil/biblioteca. **(Ainda pendente — Próximo passo 7.)**
- **Fontes IBM Plex não empacotadas** (`assets/fonts/` só tem `.gitkeep`) → fallback Segoe UI/Consolas. **(Ainda pendente — Próximo passo 7d.)**

### Próximos passos para fechar 100%

> Reformatados em etapa (verbo + critério _itálico_ + fallback `↳`). Os passos 1–4 são o **primeiro bloco de execução** (fidelidade do que A/B entregaram); 5–6 dialogam com C/D; 7 e 9 são pré-requisitos de build; 8 fecha a persistência.

1. **Reescrever o `CompositorPanel` no formato `editlist`/rascunho do mockup** — painel 1 com `1 Configurações`, lista `Edições montadas (N)`, linha `em edição` com `✕` por linha, botão `+ adicionar outra edição` e o CTA `Adicionar edição ao lote →` no painel 2. **Requisito do modelo aprovado:** a tela deve ter **dois campos separados** — "código que sai" (origem) e "código que entra" (destino) — e o operador escolhe cada um da biblioteca; a biblioteca é **dicionário** (código + descrição), não fornece o par pronto (ver "Decisão de modelo de dados da biblioteca" no Objetivo). _Concluído quando: o painel 1 bate visualmente com o mockup (lista empilhada + rascunho + `✕` + CTA), tem os dois campos origem/destino e montar/remover edição funciona._
   ↳ Se falhar: **preservar os sinais/slots atuais** (a lógica core não muda); reescrever só a camada visual/UX, comparando com os `connect()` atuais antes de remover widgets.
   ⚠️ **Atenção (transitório):** a biblioteca tem `replace` **vazio** de propósito. Até esta reescrita, a tela antiga pode tratar um código escolhido como "trocar por nada" (apagar) — ver AVISO no Objetivo. A correção é **esta tela nova com dois campos**; **não** preencher o `replace` da biblioteca para "resolver" (volta ao modelo de pares prontos, descartado). O destino só existe quando o operador escolhe o segundo código.

2. **Corrigir a fidelidade do header e do Resumo** — header com marca `FlowNC`/subtítulo do mockup, realocar/remover `Abrir pasta`/`Abrir programa(s)`, `Salvar perfil` à esquerda, `+ Adicionar código` azul sólido; Resumo com escopo `N programas`, ações do card clicáveis (`✎ ⧉ 🗑`) e selo de backup em escudo + 2 linhas. _Concluído quando: header e Resumo batem com o mockup nesses pontos._
   ↳ Se falhar: aplicar um controle por vez rodando o app entre cada mudança para isolar quebras.

3. **Remover o checkbox duplicado da lista de programas e aplicar `.file.off`** — deixar **um** checkbox por linha; aplicar o estilo `.file.off` na linha desmarcada; título `Seleção de Programas`; metadados relativos. _Concluído quando: cada linha tem só um checkbox e a linha desmarcada fica esmaecida (`.file.off`)._
   ↳ Se falhar: identificar qual checkbox alimenta a seleção real antes de remover o outro; não quebrar o sinal de seleção.

4. **Trocar o `_save()` legado pelo orquestrador `publish_batch` e corrigir o contador `Alterações`** — o CTA `Executar Lote` deve publicar via `build_plan` + `apply_edits` + `publish_batch` (`core/publisher.py`, backup versionado + SHA); o contador `Alterações` deve descontar supressões (não superestimar sob conflito). _Concluído quando: a publicação roda pelo `publish_batch` (não pelo `_save()` de `main_window.py:466`) e o contador mostra o número real de alterações._
   ↳ Se falhar: manter `_save()` como fallback funcional até o `publish_batch` estar testado na UI; corrigir o contador isoladamente, conferindo a lógica de supressão no `build_plan`.

5. **Acertar o editor (glifos, labels, realce, stepbar, `💾`)** — usar `🔍`/`↑↓`, separar `Substituir`+`por`, `💾 Salvar`, realçar **todas** as ocorrências e trocar o `Um a um` por stepbar inline. _Concluído quando: o editor bate com o mockup nesses pontos e realça todas as ocorrências da busca._
   ↳ Se falhar: priorizar o realce de todas as ocorrências (maior valor de uso). Boa parte está nas **Etapas 24–27 (Mudança C)** — executar lá.

6. **Modais Qt dos 4 overlays + dropdowns pesquisáveis (`libdrop`)** — transformar os 4 overlays de publicação do mockup em modais Qt estilizados e tornar os dropdowns origem/destino pesquisáveis (`libdrop`). _Concluído quando: os 4 overlays existem como modais estilizados e os dropdowns filtram por digitação._
   ↳ Se falhar: estilizar `QMessageBox` como meio-termo; isto se estende nas **Etapas 41/45 (Mudança D)**.

7. **Corrigir o empacotamento do EXE.** Hoje `FlowNC.spec datas=[]` → o EXE abre "pelado" em outro PC. **Atenção:** só preencher `datas` **não basta** — no PyInstaller 6.x os arquivos de `datas` caem na subpasta `_internal/` (= `sys._MEIPASS`), mas o `app_paths.base_dir()` atual procura ao lado do `.exe` (`Path(sys.executable).parent`); sem ajustar isso o app continua pelado. São 3 sub-passos + decisão das fontes:
   - **7a. `app_paths.py` — dois "baldes" de caminho.** Criar `resource_dir()` que usa `sys._MEIPASS` quando empacotado (lê **recurso fixo**: `ui/style.qss` e `assets/fonts/*.ttf` de dentro do `_internal/`); manter os **dados editáveis** (`presets/`, `library.json`, `settings.json`) saindo da pasta do `.exe`, pra o operador continuar editando no pen drive. _Concluído quando: `qss_path()`/`fonts_dir()` apontam pro bundle e `presets_dir()`/`library_path()`/`settings_path()` apontam pra pasta do `.exe`._ ↳ Se falhar: o `app_paths.py` atual já tem `base_dir()`/`presets_dir()`/`library_path()`/`settings_path()`/`fonts_dir()`/`qss_path()`, mas **sem** `resource_dir()` nem `_MEIPASS` — adicionar sem quebrar as funções existentes.
   - **7b. `FlowNC.spec` — `datas` só do recurso fixo.** Declarar em `datas` apenas `('ui/style.qss', 'ui')` e `('assets/fonts/*.ttf', 'assets/fonts')`. **Não** pôr `data/` aqui (senão vira só-leitura escondido no `_internal/`). _Concluído quando: o build gera `_internal/ui/style.qss` e `_internal/assets/fonts/*.ttf`._
   - **7c. Semente de `data/` ao lado do `.exe`.** Passo de build (script pós-PyInstaller ou cópia no `.spec`) que copia `data/` (presets + `library.json`) pra `dist/FlowNC/data/`, editável. _Concluído quando: `dist/FlowNC/data/presets/*.json` e `dist/FlowNC/data/library.json` existem ao lado do `.exe`._
   - **7d. Fontes (na execução).** Baixar IBM Plex Sans + IBM Plex Mono `.ttf` reais (gratuitas, OFL — Google Fonts/GitHub) e colocar em `flownc/assets/fonts/` (hoje só tem `.gitkeep`). Fallback automático Segoe UI/Consolas já existe no `theme.py` se faltar. _Concluído quando: os `.ttf` das duas famílias existem em `assets/fonts/` e são empacotados (7b)._
   - **7e. Verificar.** Buildar e abrir o `.exe` numa pasta limpa (idealmente outro PC): conferir que o visual (QSS), as fontes e os presets/biblioteca carregam. _Concluído quando: o app não abre "pelado"._

8. **Persistência completa do perfil + conferência visual final** — implementar a gravação real de perfil (hoje `Salvar perfil` é stub `_save_profile_stub` em `main_window.py:550`): salvar grava em disco via `preset_store` e o perfil reaparece ao reabrir; ao fim, conferência visual completa contra o mockup. _Concluído quando: salvar um perfil e reabrir o app mantém o perfil; a conferência final foi feita._
   ↳ Se falhar: implementar primeiro só a gravação/leitura (o essencial) e deixar a conferência visual como passo final separado.

9. **Semear na primeira execução (Seed).** Os dados de fábrica **já existem** (ver 9a/9e), mas falta a cópia automática em runtime: hoje, se a pasta `data/` for apagada, o FlowNC abre **pelado** porque `_load_library` ([main_window.py:529](flownc/ui/main_window.py:529)) devolve lista vazia sem reclamar e `_load_presets` ([main_window.py:177](flownc/ui/main_window.py:177)) não acha presets. Falta `core/seed.py`/`ensure_seed` para repor a fábrica. A biblioteca é uma lista de **código + descrição curta, totalmente editável** (modelo aprovado — ver "Decisão de modelo de dados da biblioteca" no Objetivo). Decisão de design: **dado de fábrica como arquivo** (não string em Python), separado do dado editável, reaproveitando o caminho de empacotamento dos itens 7a–7c. Sub-passos:
   - **9a. ✅ Defaults de fábrica em `flownc/data_default/` (feito 2026-06-07).** Criados `data_default/library.json` (**89 códigos**) e `data_default/presets/MAQ01.json`/`MAQ02.json`/`MAQ03.json`, versionados no repo e validados via `load_library`/`load_preset`. Schema único entre `data/` e `data_default/`: biblioteca = `find`=código / `replace`="" / `label`=descrição / `tags`=categoria (meio-termo do modelo "código + descrição", sem quebrar o `load_library` atual).
   - **9b. `core/seed.py` com `ensure_seed(data_dir)`.** No boot, se `library.json` ou a pasta `presets/` não existirem (ou estiverem vazias), copiar os defaults de `data_default/` para a pasta editável ao lado do `.exe`. **Idempotente:** se já houver conteúdo do operador, não sobrescrever. _Concluído quando: rodar `ensure_seed` numa pasta `data/` vazia gera `library.json` + `presets/MAQ01.json`/`MAQ02`/`MAQ03`, e rodar de novo não altera nada._ ↳ Se falhar (erro de cópia/permissão): logar e seguir com biblioteca/perfil vazios, sem travar o boot.
   - **9c. Chamar `ensure_seed` no boot.** Invocar em `main.py` (ou no `__init__` da `MainWindow`) **antes** de `_load_library`/`_load_presets`, usando `app_paths` (pasta editável do item 7a). _Concluído quando: app aberto numa pasta limpa já mostra a biblioteca (89 códigos) e um dos perfis MAQ0X selecionado._ ↳ Se falhar: conferir a ordem de inicialização; a semente tem de ocorrer antes do load.
   - **9d. Empacotar os defaults no EXE.** Garantir que `data_default/` seja recurso fixo no bundle (junto do item 7b), para o `ensure_seed` encontrar a fábrica mesmo no EXE. _Concluído quando: o EXE recém-buildado em pasta limpa semeia a biblioteca + perfis sozinho._ ↳ Se falhar: conferir `datas` do `FlowNC.spec` e o caminho de recurso (`resource_dir`/`_MEIPASS` do item 7a).
   - **9e. ✅ Conteúdo da biblioteca (lista do Mestre) — fornecida 2026-06-07.** 89 códigos G/M/eixos/parâmetros/variáveis/fluxo, cada um como `código` + `descrição curta`. _Já em `data/library.json` e `data_default/library.json`._ ↳ Pendente só a conferência visual de que aparecem nos dois campos (origem/destino) ao abrir o app (smoke).

> **Nota de ligação:** o passo 7 (empacotamento) cita "Seed Fanuc" de passagem — o detalhamento atômico é **este item 9**. O 7c (semear `data/` ao lado do `.exe`) e o 9b/9c se complementam: 7c garante o arquivo na entrega; 9b/9c garantem a semente também em runtime se a pasta for apagada.
