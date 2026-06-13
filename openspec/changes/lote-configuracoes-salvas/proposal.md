## Why

O operador repete sempre o mesmo conjunto de edições (ex.: "mudar ponto zero" = `G54→G55` +
`M8→M9`, ou um bloco fixo). Hoje ele remonta tudo do zero a cada turno. Existe um seletor de
receita no topo ("Máquina 1"), mas é escondido, confuso e mistura "salvar" dentro de um dropdown —
o operador não o usa. Falta um jeito explícito e rápido de **salvar o conjunto de edições com um
nome** e **reabrir** depois, compartilhado entre todos os operadores da oficina.

## What Changes

- **Salvar configuração (acesso rápido):** botão **"Salvar configuração"** no painel Lote de
  edições que abre um input para o **nome** + **Salvar/Cancelar**. Guarda **apenas as edições
  montadas (regras)** — trocas e blocos — **sem os programas** (os programas variam a cada execução).
- **Abrir configuração salva:** botão **"Abrir configuração"** no mesmo painel, que lista as
  configurações salvas; ao escolher, as edições entram **direto no lote como cartões**, já com as
  regras prontas e **com 0 programas**.
- **Aplicar aos marcados:** depois de abrir uma configuração (cartões sem programas), o operador
  marca os programas e usa **"Aplicar aos marcados"** para preencher o conjunto de programas das
  edições — então confere/publica.
- **BREAKING (topo):** **remover** o seletor de configuração ("Máquina 1") da `TopBar`. Os dois
  botões passam a viver na tela Lote, na **mesma linha do título "Lote de edições"** (espelhando o
  painel Programas, que tem "Marcar todos"/"Adicionar programas" na linha do título).
- **Compartilhado:** as configurações ficam num diretório de dados da aplicação (mesma máquina),
  visíveis a qualquer operador que abrir o app — não são por-usuário.
- Suporte a **edições de bloco** na configuração (o armazenamento atual de receita só guarda
  trocas; passa a guardar trocas + blocos).

## Capabilities

### New Capabilities
- `lote-configuracoes-salvas`: salvar/abrir configurações nomeadas de edições (regras, sem
  programas) a partir da tela Lote, com input de nome rápido, lista de configurações salvas, entrada
  direta no lote e ação "Aplicar aos marcados".

### Modified Capabilities
- `topo-global-configuracao`: remove o seletor de configuração/receita e o item "Salvar lote atual
  como…" da `TopBar` (a função migra para a tela Lote); o topo mantém só marca + chip de backup.

## Impact

- **Código:** `flownc/ui/components/top_bar.py` (remover `cb_receita` e sinais de receita),
  `flownc/ui/screens/lote_screen.py` (2 botões na linha do título + input de nome + lista de
  configs + "Aplicar aos marcados"), `flownc/ui/main_window.py` (religar salvar/abrir à tela Lote
  em vez do topo), `flownc/core/preset_store.py` ou novo `config_store.py` (persistir edições
  swap + ins num diretório compartilhado).
- **Interação com `lote-edicoes-por-programa`:** configurações guardam só regras; "Aplicar aos
  marcados" é o ponto onde os programas entram nas edições carregadas (casa com o modelo de
  programas-por-edição). As duas changes devem ser aplicadas em ordem (programas-por-edição antes).
- **Contrato visual:** evolui o mockup v4 e `docs/CONTEXTO-IA.md` (topo sem seletor; botões de
  config na tela Lote) — atualizar após aprovação visual do Mestre.
- **Testes:** `flownc/tests/test_ui_smoke.py` e testes do store de configuração.
