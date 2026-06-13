## Purpose

Define a tela Histórico: uma linha por publicação com restauração dos originais a partir do backup.

## ADDED Requirements

### Requirement: Tela Histórico lista publicações passadas

O sistema SHALL implementar a tela Histórico como uma **lista cronológica reversa** (mais recente no topo) de publicações. Cada linha SHALL exibir: **quando** (data/hora), resumo ("2 edições · 11 trocas em 5 programas"), caminho do **backup** criado e qual **configuração** estava ativa.

#### Scenario: Publicação recente aparece no topo

- **WHEN** o usuário clica em "Ver no Histórico" após uma publicação
- **THEN** a publicação recém-feita aparece no topo da lista com data/hora, resumo e caminho do backup

#### Scenario: Tela vazia exibe estado vazio

- **WHEN** nunca houve nenhuma publicação
- **THEN** a tela Histórico exibe ícone + texto-guia (nunca tela morta)

### Requirement: Restaurar originais por publicação

Cada linha do histórico SHALL ter o botão **"↩ Restaurar originais"**. Ao clicar, o sistema SHALL: (1) pedir confirmação, (2) criar um **novo backup dos arquivos atuais** antes de restaurar e (3) restaurar os arquivos da publicação escolhida a partir do backup associado. Restaurar SHALL ter fallback: se o backup não existir, o botão SHALL ser desabilitado com tooltip de aviso.

#### Scenario: Confirmar restauração cria backup dos atuais primeiro

- **WHEN** o usuário confirma a restauração de uma publicação passada
- **THEN** o sistema primeiro cria um backup versionado dos arquivos atuais e depois restaura os originais do backup da publicação escolhida

#### Scenario: Botão desabilitado se backup não encontrado

- **WHEN** o backup associado a uma linha do histórico não existe mais no disco
- **THEN** o botão "↩ Restaurar originais" dessa linha está desabilitado com tooltip "backup não encontrado"

#### Scenario: Restauração aparece no histórico

- **WHEN** uma restauração é concluída com sucesso
- **THEN** uma nova linha é adicionada ao Histórico indicando a restauração (para rastreabilidade completa)