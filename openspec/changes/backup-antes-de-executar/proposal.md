## Why

O chip de backup vive no topo da tela, com um texto vago (`backup: D:\CNC\backup\ · mudar`) que
ainda por cima é um **caminho fake** — dá falsa sensação de "já configurado". Para um operador de
primeira viagem, o fluxo natural é: seleciona programas → monta edições → executa. O backup, que é
**onde os originais serão guardados antes de gravar**, fica fora desse caminho e pode ser pulado —
o sistema deixa seguir e só avisa depois, comprometendo a experiência. A escolha de onde fica o
backup é uma etapa que, por lógica, vem **antes** de executar.

## What Changes

- **BREAKING (topo):** **remover o chip de backup da `TopBar`**. O backup deixa de morar no topo.
- **Controle de backup na tela Lote, antes do CTA:** um controle **sutil** (menor que o chip atual)
  posicionado **imediatamente antes** do botão "Conferir lote →" (executar), seguindo a ordem
  lógica "escolher backup → executar".
- **Estado real "não configurado":** acabar com o caminho fake padrão. Enquanto não houver pasta
  escolhida, o controle mostra algo como **"Definir pasta de backup"**; depois, mostra o caminho de
  forma discreta com opção de trocar.
- **Guarda no executar:** se o operador clicar em "Conferir lote →" **sem backup configurado**, o
  sistema SHALL abrir o **seletor de pasta** primeiro; escolhendo, segue direto para a conferência;
  cancelando, não executa. Cria um caminho intuitivo e direcional, sem aviso solto depois.

## Capabilities

### New Capabilities
- `backup-antes-de-executar`: controle de pasta de backup na tela Lote, sutil e posicionado antes do
  CTA, com estado "não configurado" e guarda que abre o seletor de pasta ao executar sem backup.

### Modified Capabilities
- `topo-global-configuracao`: remover o chip de backup da `TopBar` (o backup migra para a tela Lote).

## Impact

- **Código:** `flownc/ui/components/top_bar.py` (remover `btn_backup`/`set_backup_path` e o sinal
  `backup_clicado`), `flownc/ui/screens/lote_screen.py` (controle sutil de backup antes do CTA +
  guarda no clique do CTA), `flownc/ui/main_window.py` (estado `_backup_dir` começa **não
  configurado**; religar a troca de backup e a guarda à tela Lote em vez do topo;
  `_escolher_backup` reusado).
- **Estado inicial:** remover o default `"D:\\CNC\\backup\\"`; backup começa vazio até o operador
  escolher (ou vir de `settings`/`output_dir`, se houver).
- **Interação com outras changes:** `lote-configuracoes-salvas` também mexe no topo (remove o
  seletor). Após as duas, a `TopBar` fica só com a marca. Ordenar a aplicação/arquivamento para os
  deltas de `topo-global-configuracao` não conflitarem.
- **Contrato visual:** evolui o mockup v4 e `docs/CONTEXTO-IA.md` (topo sem backup; backup antes do
  CTA na tela Lote) — atualizar após aprovação visual do Mestre.
- **Testes:** `flownc/tests/test_ui_smoke.py` (topo sem chip; controle na tela Lote; guarda abre o
  seletor ao executar sem backup).
