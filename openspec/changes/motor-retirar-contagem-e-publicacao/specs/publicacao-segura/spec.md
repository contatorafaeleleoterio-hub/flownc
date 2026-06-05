## ADDED Requirements

### Requirement: Publicação na pasta de trabalho com backup versionado

O sistema SHALL publicar o resultado das edições **diretamente na pasta de trabalho** (a que a máquina lê — fixa, configurável, podendo ser de rede) e MUST preservar cada original movendo-o para um **backup versionado por data/hora** (`_backup_orig_DATA_HORA/`) numa pasta de backup configurável. O sistema MUST tocar **apenas** os arquivos que realmente mudaram. O invariante "o original nunca se perde" MUST ser mantido pelo backup versionado (cada execução gera uma pasta nova).

#### Scenario: Publica apenas arquivos que mudaram

- **WHEN** o lote altera 2 de 5 arquivos da pasta de trabalho
- **THEN** apenas os 2 arquivos alterados são republicados e seus originais vão para o backup; os outros 3 não são tocados

#### Scenario: Backup versionado por execução

- **WHEN** duas execuções publicam sobre a mesma pasta de trabalho
- **THEN** cada execução cria sua própria pasta `_backup_orig_DATA_HORA/`, sem sobrescrever o backup anterior

### Requirement: Troca atômica à prova de falha

O sistema SHALL publicar cada arquivo de forma atômica: gravar um `.tmp` na própria pasta de trabalho (mesmo volume, para `os.replace` ser atômico mesmo em rede) e só então substituir o arquivo final via `os.replace`. A pasta de trabalho MUST NOT ficar, em nenhum instante, sem o programa. Se a publicação falhar no meio, a produção MUST permanecer íntegra (sem arquivo parcial; `.tmp` removido).

#### Scenario: Pasta de trabalho nunca fica sem o arquivo

- **WHEN** a publicação de um arquivo está em andamento
- **THEN** a pasta de trabalho contém ou o original ou o novo conteúdo completo, nunca um arquivo ausente ou parcial

#### Scenario: Falha simulada não corrompe a produção

- **WHEN** a publicação é interrompida (falha simulada) após o backup mas antes da troca atômica
- **THEN** o arquivo na pasta de trabalho permanece com o conteúdo original íntegro e o backup do original existe

### Requirement: Dupla conferência SHA-256

O sistema SHALL conferir a integridade por SHA-256 **duas vezes** por arquivo publicado: (1) após copiar o original para o backup (o backup confere com o original) e (2) após a troca atômica (o publicado confere com o conteúdo editado em memória). Qualquer divergência MUST ser registrada como falha crítica no log de sessão. O SHA-256 MUST reusar a infraestrutura existente (`integrity_hash`/`verify_saved`).

#### Scenario: Conferência do backup

- **WHEN** o original é copiado para o backup
- **THEN** o SHA-256 do backup é comparado ao do original e uma divergência é reportada como falha crítica

#### Scenario: Conferência do publicado

- **WHEN** o arquivo editado é publicado na pasta de trabalho
- **THEN** o SHA-256 do publicado é comparado ao do conteúdo em memória e uma divergência é reportada como falha crítica

### Requirement: Pastas de trabalho e backup configuráveis e persistentes

O sistema SHALL guardar a pasta de trabalho (`working_dir`) e a pasta de backup (`backup_dir`) de forma persistente nas configurações do app, reusando a infraestrutura de settings existente. O carregamento de configurações antigas (sem essas chaves) MUST funcionar sem erro, retornando defaults seguros (migração transparente de schema).

#### Scenario: Pastas persistem entre execuções

- **WHEN** o usuário define `working_dir` e `backup_dir` e reabre o app
- **THEN** as duas pastas continuam configuradas

#### Scenario: Settings antigos carregam sem erro

- **WHEN** o app carrega um arquivo de configurações da versão anterior (sem `working_dir`/`backup_dir`)
- **THEN** o carregamento sucede e as pastas novas assumem defaults seguros (sem quebrar)
