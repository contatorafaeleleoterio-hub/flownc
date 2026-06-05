## ADDED Requirements

### Requirement: Contagem de ocorrências por arquivo

O sistema SHALL contar, para um código de origem, quantas vezes ele ocorre em cada arquivo de um conjunto, usando o **mesmo boundary CNC** do motor de substituição (via `find_matches`). A contagem MUST ser exposta por uma função pura com leitura de arquivo injetável (`read_fn`), de modo a ser testável sem acesso a disco. O resultado (`ScanResult`) MUST conter a contagem por arquivo e um **agregado** "X de Y arquivos contêm o código".

#### Scenario: Conta ocorrências por arquivo

- **WHEN** a varredura roda para `M8` sobre três arquivos com 2, 0 e 1 ocorrências
- **THEN** o `ScanResult` reporta `{arq1: 2, arq2: 0, arq3: 1}`

#### Scenario: Agregado de cobertura

- **WHEN** a varredura roda para `M8` sobre 6 arquivos e 5 contêm `M8`
- **THEN** o agregado do `ScanResult` indica "5 de 6 arquivos contêm M8"

#### Scenario: Boundary aplicado na contagem

- **WHEN** a varredura conta `M6` num arquivo que contém `M6` e `M60`
- **THEN** apenas o `M6` é contado (o `M60` não entra na contagem)

#### Scenario: Leitura injetável (sem disco)

- **WHEN** a contagem recebe uma `read_fn` que devolve textos em memória
- **THEN** a varredura produz o `ScanResult` sem ler nenhum arquivo do disco

### Requirement: Zero ocorrências é sinal útil

O sistema SHALL tratar "0 ocorrências num arquivo" como um sinal explícito (não erro), de forma que a UI possa marcá-lo em âmbar e desmarcar o arquivo. O `ScanResult` MUST permitir distinguir arquivos com 0 ocorrências dos demais.

#### Scenario: Arquivo sem o código é sinalizável

- **WHEN** um arquivo do conjunto tem 0 ocorrências do código varrido
- **THEN** o `ScanResult` o identifica como zero-ocorrências (insumo para o âmbar/desmarcar na UI)
