# Plano de Conformidade com o Mockup Aprovado v2

Data da revisao: 2026-06-06
Revisao auditada: 2026-06-07 (cada afirmacao cruzada com o codigo real e o mockup)
Referencia aprovada: `mockups/painel-final.v2.html`
Objetivo: garantir que a interface real do FlowNC reflita o design aprovado, sem tratar entregas parciais como finalizadas.

## Diagnostico da revisao

O agente anterior entregou a casca correta do layout: `HeaderBar`, `CompositorPanel`, `ProgramListPanel`, `SummaryPanel`, `QSplitter` em duas colunas e `QStackedWidget` para alternar Resumo/Editor. A divergencia estava na fidelidade do resultado: o resumo era minimo, o CTA ainda dizia "APLICAR SUBSTITUICOES", a lista de programas nao tinha metadados nem editar por linha, o header nao tinha os comandos do mockup e o plano documentava fases futuras sem refletir a tela efetiva.

A auditoria de 2026-06-07 confirmou que a casca e a maior parte do Resumo conferem, mas que parte do que estava marcado como "entregue" so reproduz o mockup parcialmente, e que uma divergencia inteira (o painel 1, CompositorPanel) nao estava documentada.

## Resultado aplicado nesta revisao

### Header

- `flownc/ui/components/header.py` recebeu marca FlowNC, perfil, `Biblioteca de Codigos`, `+ Adicionar codigo` e `Salvar perfil`, alem de dois atalhos extras `Abrir pasta...` e `Abrir programa(s)...`.
- Divergencias de fidelidade ainda abertas: o mockup NAO tem `Abrir pasta...` nem `Abrir programa(s)...` no header (no mockup a adicao de programas e feita pelo botao do painel 2); a marca usa `⚙ FlowNC` + subtitulo `LOCAL · OFFLINE` no codigo, contra `FlowNC` + `Editor de Lotes` no mockup; o seletor e rotulado `Perfil` (QComboBox nativo) contra `Maquina 01` (controle custom) no mockup.
- Divergencias adicionais confirmadas na auditoria de 2026-06-07: a **posicao** de `Salvar perfil` diverge (mockup: a esquerda, antes do spacer; codigo: a direita, depois de `+ Adicionar codigo`); o `+ Adicionar codigo` usa estilo azul-claro (`interactive`: fundo `#E4EEF7`, texto `#1F5F9E`) contra o azul **solido** (`.hbtn.blue` = `#1F5F9E` com texto branco) do mockup.
- `Biblioteca de Codigos` e `+ Adicionar codigo` abrem o mesmo dialogo `LibraryDialog` (ambos disparam `_open_library_dialog`). `+ Adicionar codigo` NAO abre um formulario de cadastro direto; comporta-se identico a `Biblioteca de Codigos`.
- `Salvar perfil` ficou conectado a um aviso transitorio (`_save_profile_stub` -> `QMessageBox`), porque a persistencia completa do perfil foi removida na refatoracao anterior e nao deve ser fingida como entregue.

### Programas

- `flownc/ui/components/program_list.py` renderiza o painel com `+ Adicionar programa(s)...` no cabecalho e o banner `✓ Regra em edicao — marque os programas...` (fiel ao mockup).
- Cada linha mostra checkbox, nome do arquivo, tamanho/data e botao `Editar` por arquivo. O botao por linha e o duplo-clique emitem o mesmo sinal usado pelo editor integrado.
- Divergencias de fidelidade ainda abertas: o titulo e `2  Programas` no codigo contra `2 Selecao de Programas` no mockup; o metadado usa `NN KB · dd/mm/AAAA HH:MM` contra rotulos relativos do mockup (`hoje 08:14`, `ontem`, `30/05`); cada item e ao mesmo tempo `ItemIsUserCheckable` e carrega um `QCheckBox` proprio no row, e **renderiza de fato dois checkboxes por linha** — nao apenas "tende": confirmado em execucao na auditoria de 2026-06-07 (screenshot da `ProgramListPanel`), contra o chip unico do mockup; linha desmarcada nao recebe o tratamento visual atenuado (`.file.off`).
- Divergencia omitida (auditoria 2026-06-07): **falta o CTA `Adicionar edicao ao lote →`** que no mockup fica no rodape do painel 2 (`.addrule`). No codigo nao existe esse botao; o compositor envia a regra direto ao Resumo (ver secao CompositorPanel), entao o passo "montar lista -> enviar ao lote" do mockup nao tem equivalente.

### Resumo

- `flownc/ui/components/summary.py` foi refeito como painel rico do mockup:
  - titulo `3 Resumo`;
  - chip `✓ Pronto` / `⚠ N conflito`;
  - contadores `Regras`, `Programas`, `Alteracoes`;
  - cards numerados com formula `De -> Para`, selo `✓ Validado`, linha de conflito e meta `X ocorrencias em Y programas`;
  - selo de preservacao/backup;
  - CTA `Executar Lote / Pre-visualizar antes de publicar`.
- `flownc/ui/main_window.py` alimenta esse painel com:
  - `validate_batch()` para conflitos por codigo de origem;
  - `count_occurrences()` para `X ocorrencias em Y programas`;
  - total de alteracoes agregado pelos programas marcados (contagem bruta de `find`, sem descontar supressao por conflito do `build_plan`; pode superestimar em caso de conflito);
  - caminho de backup configurado quando disponivel.
- Divergencias de fidelidade ainda abertas: o escopo do card mostra `todos`/`sel.` em vez de `N programas` do mockup; as acoes `✎ ⧉ 🗑` do card sao um `QLabel` estatico decorativo, sem clique (nao ha editar/duplicar/excluir regra pelo card); o selo de backup foi colapsado para uma unica linha, perdendo o escudo circular e as duas linhas (`t1`/`t2`) do `seal-big` do mockup.

### Editor e preview

- `flownc/ui/editor_panel.py` teve textos aproximados ao mockup: `Localizar` e `✕ Voltar ao resumo` batem; o botao de varredura usa a lupa `🔎` (U+1F50E) enquanto o mockup usa `🔍` (U+1F50D); as setas de navegacao usam `◂`/`▸` contra `↑`/`↓` do mockup; a linha de substituicao usa um unico rotulo `Substituir por` contra `Substituir` + `por` separados no mockup.
- Divergencias omitidas (auditoria 2026-06-07): o botao salvar e `Salvar` sem o glifo `💾 Salvar` do mockup; o editor **nao realca todas as ocorrencias** (`.occ`/`.occ.current` do mockup) — apenas seleciona a ocorrencia atual via cursor (`_navigate`); o `Um a um` usa uma sequencia de `QMessageBox.question` em vez da barra inline `stepbar` do mockup. Tudo isso foi exercitado em execucao e **funciona** (varredura conta com a borda CNC, substituir/salvar in-place ok), so diverge visualmente.
- `flownc/ui/preview_dialog.py` foi renomeado visualmente para o fluxo do mockup: `Resumo do lote — confira antes de publicar` e botao `Publicar na maquina`. As cores internas do dialogo continuam hardcoded, sem usar os tokens `success-bg`/`warning-bg`/`danger-bg` do mockup.

### Estilo visual

- `flownc/ui/style.qss` recebeu estilos para `HeaderBar`, paineis, contadores, chip de estado, cards de regra, conflito, selo de backup, CTA e banner da lista de programas.
- Os tokens principais do mockup foram preservados e os valores hex conferem exatamente: IBM Plex, cinzas industriais, azul interativo `#1F5F9E`, verde de sucesso `#1C8A4D`, ambar de conflito `#A86A07` e CTA escuro `#3A434E`->`#232A33`.
- Limitacao do Qt QSS: nao suporta `box-shadow`, entao os efeitos `--metal` (sombra metalica nos paineis/botoes) e `--focus-ring` do mockup nao sao reproduzidos; o gutter do editor tambem usa cores proprias, fora dos tokens `--color-editor-gutter*`.
- Divergencia omitida (auditoria 2026-06-07): as **fontes IBM Plex nao sao empacotadas** — `flownc/assets/fonts/` contem apenas `.gitkeep`. `_register_fonts` nao encontra nenhum `.ttf`, entao o app SEMPRE cai no fallback Segoe UI / Consolas. Os tokens de `theme.py`/QSS pedem IBM Plex, mas ela nunca e usada de fato. Ou empacotar as fontes, ou assumir Segoe UI e remover a referencia ao IBM Plex.

## Estado de conformidade

Entregue e fiel ao mockup nesta revisao:

- Layout aprovado em duas colunas com alternancia Resumo/Editor (`QSplitter` + `QStackedWidget`).
- Lista de programas com metadados, banner de regra e editar por linha convergindo no mesmo sinal do editor.
- Resumo com chip de estado, contadores, cards `De -> Para`, selo `✓ Validado`, linha de conflito, meta de ocorrencias e CTA correto, alimentados por `validate_batch()` e `count_occurrences()`.
- Preview com nomenclatura de publicacao (titulo e botao).
- QSS com os tokens/hex do mockup.

Entregue apenas parcialmente (divergencias de fidelidade a fechar):

- Header: contem as acoes do mockup (Biblioteca, + Adicionar codigo, Salvar perfil, perfil), mas adiciona dois botoes fora do mockup (`Abrir pasta...`/`Abrir programa(s)...`), diverge na marca/subtitulo, e `+ Adicionar codigo` nao tem comportamento proprio.
- Lista de programas: titulo (`Programas` vs `Selecao de Programas`), formato de metadados, possivel checkbox duplicado e estado visual de linha desmarcada divergem do mockup.
- Resumo: escopo do card (`todos/sel.` vs `N programas`), acoes do card decorativas (nao clicaveis) e selo de backup simplificado para uma linha.
- Editor: glifos (lupa/setas) e o layout `Substituir`/`por` ainda divergem do HTML.

## Ainda nao deve ser chamado de concluido

- **CompositorPanel (painel 1) diverge fortemente do mockup e ainda nao foi reescrito.** Mockup: titulo numerado `1 Configuracoes`, dropdowns `De`/`Para` com tag descritiva e uma lista empilhada `Edicoes montadas (N)` com linha `em edicao` (rascunho) sempre presente, `✕` por linha e botao tracejado `+ adicionar outra edicao`. Codigo (`compositor.py`): titulo `Montar edicao` sem numero, `QComboBox` editaveis sem busca, `QListWidget` plano sem rascunho, sem `✕` por linha (apenas um botao global de remocao) e o botao adicionar comete a regra na hora em vez de empilhar um rascunho. Alem disso (auditoria 2026-06-07), o compositor tem um seletor `Escopo` (`Todos os programas`/`So este programa`) que **nao existe no mockup** — no mockup o escopo nasce de marcar os programas no painel 2, nao de um dropdown.
- Fluxo de 3 modais exatamente igual ao HTML (`processando -> resumo/preview -> publicando/publicado`) ainda usa o `PreviewDialog` Qt estatico existente.
- Publicacao real via `core/publisher.py::publish_batch` ainda nao substituiu o caminho legado `_save()`/pasta processada (o CTA `Executar Lote` ainda desemboca no fluxo antigo).
- `Salvar perfil` completo nao foi reimplementado depois da refatoracao para componentes; o botao existe visualmente, mas avisa que a persistencia sera consolidada.
- Dropdown pesquisavel com popup customizado (`.libdrop`) igual ao HTML nao existe em ponto algum: editor, compositor e perfil do header usam `QComboBox` nativo, sem campo de busca.
- Colunas dinamicas com transicao suave (~60/40 <-> ~40/60) do mockup sao aproximadas por `setSizes` fixos sem animacao.

## Validacao executada

**Atualizado na auditoria de 2026-06-07.** O ambiente TEM `flownc/.venv` com **PySide6 6.11.1** (Python 3.13.1). A afirmacao anterior de que "PySide6 nao esta instalado / a UI esta nao verificada" estava **incorreta** — bastava usar o venv do projeto.

- `python -m ruff check ...` -> `All checks passed!`.
- `QT_QPA_PLATFORM=offscreen .venv/Scripts/python.exe -m pytest tests/test_ui_smoke.py tests/test_editor_localizador.py -q` -> **20 passed**.
- `QT_QPA_PLATFORM=offscreen .venv/Scripts/python.exe -m pytest -q` (suite completa) -> **146 passed** (nao 42).

`test_ui_smoke.py` **instancia a UI de verdade**: cria `MainWindow` + os 4 componentes (`HeaderBar`, `CompositorPanel`, `ProgramListPanel`, `SummaryPanel`), e exercita compositor->summary (montar/remover edicao, sinal emitido), troca de stack resumo<->editor, abrir editor, habilitar/gravar in-place e preservacao de CRLF. `test_editor_localizador.py` cobre a logica pura do localizador (contagem == Lote, borda CNC, substituir todos/um a um). Ambos **passam**.

Smoke manual executado (MainWindow real, offscreen, com screenshots): abrir pasta -> programas marcados -> 3 edicoes no compositor (incluindo conflito) -> Resumo recalcula (chip `⚠ 1 conflito`, contadores 3/3/10, cards, selo, CTA) -> abrir editor por caminho -> varredura (`M8`=2, ignora `M80`) -> substituir todos + salvar in-place (arquivo sobrescrito, SHA conferido) -> voltar ao resumo -> CTA -> `PreviewDialog` (`Resumo do lote — confira antes de publicar` / `Publicar na maquina`). **Tudo funcionou.** O contador `Alteracoes` exibiu 10 com a contagem bruta vs. ~6 reais sob conflito — confirma a ressalva da secao Resumo. Decorativos confirmados: acoes `✎ ⧉ 🗑` do card e `Salvar perfil`. Divergencia visual confirmada em render: dois checkboxes por linha.

## Biblioteca de Codigos e Perfil padrao (Fanuc) — lacunas confirmadas (2026-06-07)

- `data/library.json` **nao existe**; `load_library` devolve `[]`. O app inicia com a **biblioteca vazia**, sem nenhum codigo Fanuc seed — dropdowns De/Para e do editor nascem vazios.
- O unico preset e `MAZAK_VTC530.json` (Mazak, exemplo). **Nao ha perfil Fanuc padrao**, entao o app nao inicia com itens de comando Fanuc.
- Onde semear: criar `flownc/data/library.json` (Fanuc: M03/M04/M05/M06/M08/M09/M00/M01/M30, G00–G03, G17–G19, G20/G21, G28, G40–G43, G49, G54–G59, G90/G91, G94/G95, normalizacoes M3->M03 / M8->M08 / G0->G00 / T1->T01) e `flownc/data/presets/FANUC_PADRAO.json` (ordena antes de MAZAK -> vira o default). Para robustez, adicionar `core/seed.py` com `ensure_seed()` chamado em `MainWindow.__init__`/`main()` para regenerar na 1a execucao.

## Empacotamento (EXE) — lacuna confirmada (2026-06-07)

`flownc/FlowNC.spec` tem `datas=[]`: o EXE **nao inclui** `ui/style.qss`, `data/presets`, `data/library.json` nem `assets/fonts`. No executavel, `_apply_stylesheet` cai no `except` e o app roda **sem tema**, sem perfil e sem biblioteca. Corrigir `datas` para empacotar esses recursos (ou documentar que o operador copia `data/` e `ui/style.qss` ao lado do EXE — o que nao resolve o QSS/fontes).

## Proximo passo obrigatorio para fechar 100%

Para declarar o design aprovado como completamente entregue, as proximas mudancas devem cobrir:

1. reescrever o `CompositorPanel` para o formato `editlist`/rascunho do mockup (titulo `1 Configuracoes`, lista `Edicoes montadas (N)`, linha `em edicao`, `✕` por linha, botao tracejado `+ adicionar outra edicao`);
2. corrigir a fidelidade do header (marca/subtitulo, remover ou realocar os botoes `Abrir pasta`/`Abrir programa(s)`) e o escopo/acoes do card de Resumo;
3. orquestrador fino de publicacao usando `build_plan`, `apply_edits` e `publish_batch`, substituindo o `_save()` legado;
4. modais Qt equivalentes ao fluxo de 4 overlays do mockup v2;
5. dropdowns pesquisaveis (`.libdrop`) no editor, compositor e perfil do header;
6. persistencia completa do perfil no novo `CompositorPanel`/header;
7. validacao em ambiente com `PySide6` instalado (smoke automatizado + conferencia visual contra o mockup).
