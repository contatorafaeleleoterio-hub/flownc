## Purpose

Define o modal de publicação com barra de progresso, backup versionado e dupla conferência SHA-256.

## ADDED Requirements

### Requirement: Modal de Publicação com barra de progresso

O sistema SHALL abrir um modal **"Publicando…"** ao confirmar a publicação na Conferência. O modal SHALL exibir uma **barra de progresso** e etapas sequenciais: "Backup dos originais", "Gravação na pasta original", "Conferência dupla SHA-256". O modal NOT SHALL ser fechado pelo usuário enquanto a publicação estiver em andamento.

#### Scenario: Modal não fecha durante publicação

- **WHEN** a publicação está em andamento
- **THEN** o botão ✕ e o atalho Esc estão desabilitados; o modal permanece aberto

#### Scenario: Etapas avançam conforme publicação progride

- **WHEN** a publicação completa a etapa de backup
- **THEN** a etapa "Backup dos originais" é marcada como concluída e a barra de progresso avança

### Requirement: Tela de resultado da publicação

Ao concluir com sucesso, o modal SHALL exibir: "Publicado ✓", resumo do que foi feito (N trocas em M programas), caminho do backup criado e botões **"Ver no Histórico"** e **"OK — novo lote"**. Clicar em "OK — novo lote" SHALL fechar o modal e limpar a lista de edições na tela Lote.

#### Scenario: Resultado exibe caminho do backup

- **WHEN** a publicação conclui com sucesso
- **THEN** o modal exibe o caminho completo da pasta de backup criada

#### Scenario: "OK — novo lote" limpa a lista de edições

- **WHEN** o usuário clica em "OK — novo lote"
- **THEN** o modal fecha e a lista de edições na tela Lote é limpa (pronta para novo lote)

#### Scenario: "Ver no Histórico" navega para tela Histórico

- **WHEN** o usuário clica em "Ver no Histórico"
- **THEN** o modal fecha e o rail navega para a tela Histórico, que exibe a publicação recém-feita no topo

### Requirement: Falha de publicação não deixa arquivos corrompidos

O sistema SHALL, em caso de falha durante a publicação, garantir que o backup já criado seja preservado e o caminho seja exibido ao usuário. O modal SHALL mostrar mensagem de erro clara ("arquivo em uso", "falha de rede", etc.) e SHALL NOT silenciar a falha.

#### Scenario: Falha exibe mensagem e preserva backup

- **WHEN** um erro de gravação ocorre durante a publicação (ex.: arquivo em uso)
- **THEN** o modal exibe mensagem de erro clara, mostra o caminho do backup já criado e não fecha silenciosamente