## Context

Hoje a `TopBar` mostra `btn_backup` (chip "backup: <caminho> · mudar", sinal `backup_clicado`) e o
`main_window` guarda `_backup_dir` com default **fake** `"D:\\CNC\\backup\\"`. O `ConferenciaModal`
recebe esse caminho e tem uma linha de backup com "trocar". A publicação usa `_backup_dir`. O chip
fica fora do caminho de execução e pode ser ignorado.

## Goals / Non-Goals

**Goals:**
- Tirar o chip de backup do topo.
- Controle de backup **sutil** na tela Lote, **imediatamente antes** do CTA "Conferir lote →".
- Estado real "não configurado" (sem caminho fake).
- Guarda: clicar no CTA sem backup abre o seletor de pasta; escolher → segue; cancelar → não executa.

**Non-Goals:**
- Não mudar o nome do CTA "Conferir lote →" (contrato v4).
- Não remover a linha de backup do `ConferenciaModal` (continua como confirmação no modal).
- Não atualizar mockup/`CONTEXTO-IA` aqui (follow-up).

## Decisions

**1. `_backup_dir` começa não configurado.**
Remover o default `"D:\\CNC\\backup\\"`. Inicial = `""` (ou o que vier de `settings.backup_dir` /
`output_dir`, se existir). O estado "vazio" controla o texto do controle e a guarda.

**2. Controle sutil na `LoteScreen`, antes do CTA.**
No rodapé do painel direito, entre os `_facts` e o `_CtaButton`, inserir uma linha discreta:
- Não configurado → botão/label secundário **"Definir pasta de backup"** (ícone pequeno de pasta).
- Configurado → texto discreto "backup: …\\backup\\" com link "trocar".
Estilo menor/secundário (não o chip grande atual). Sinal `backup_clicado` (ou método) chama o
seletor de pasta no `main_window` (reusa `_escolher_backup`). A `LoteScreen` expõe
`set_backup_path(caminho)` e `backup_solicitado` (sinal).

**3. Guarda no CTA.**
O clique do CTA passa a verificar o backup **antes** de emitir `conferir_solicitado`:
- Se `_backup_dir` vazio → emitir `backup_solicitado` (abre o seletor). Se o operador escolher,
  seguir para a conferência; se cancelar, não executar.
- Implementação: o `main_window` intermedeia — ao receber `conferir_solicitado`, checa `_backup_dir`;
  se vazio, chama `_escolher_backup()`; se retornar `False` (cancelou), aborta; senão abre o modal.
Mantém a regra de habilitação do CTA (≥1 edição / programas) intacta — a guarda do backup é
adicional e só dispara no clique, não desabilita o botão (para não esconder o caminho do operador).

**4. Remover do topo.**
`TopBar` perde `btn_backup`, `set_backup_path`, `backup_clicado`. `main_window` deixa de ligar o
topo ao backup e passa a ligar a `LoteScreen`.

## Risks / Trade-offs

- **Backup só visível na tela Lote** (não mais global) → o operador vê backup no contexto certo (a
  execução). As outras telas não precisam dele. Aceito.
- **Guarda no clique vs. botão desabilitado** → escolhi guarda no clique para *direcionar* (abre o
  seletor) em vez de só bloquear; é o que o Mestre pediu ("aparecer o menu de escolher o local").
- **Conflito de delta no topo com `lote-configuracoes-salvas`** → ambos modificam
  `topo-global-configuracao`. Mitigação: aplicar/arquivar em sequência; o estado final do topo é
  "só marca". Ao arquivar a segunda, conferir que o delta casa com o estado já aplicado.

## Migration Plan

Sem dado persistido novo. Remoção do default fake é segura (a publicação já exigia escolher pasta de
fato no modal). Rollback = reverter o commit.

## Open Questions

- Persistir a última pasta de backup escolhida em `settings` para vir preenchida no próximo uso?
  (Provavelmente sim — bom para o fluxo repetido; tratar junto se o `settings_store` já suportar
  `backup_dir`, que aparenta suportar.)
