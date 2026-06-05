## ADDED Requirements

### Requirement: Retirar um código é troca-por-vazio sobre o motor existente

O sistema SHALL modelar a ação "Retirar X" como uma regra de substituição por texto vazio (`Rule(find="X", replace="", action=RETIRAR)`), reusando o motor de plano/composição já existente (`build_plan`/`apply_edits`). O sistema MUST NOT criar um motor de remoção paralelo. A localização do código a retirar MUST usar o mesmo boundary CNC das substituições, de modo que retirar `M6` não atinja `M60`, `M6.5` nem `M6` colado a uma palavra.

#### Scenario: Retira código no meio de um bloco

- **WHEN** o usuário retira `M6` da linha `N50 M6 T0101`
- **THEN** o resultado é `N50 T0101` (o `M6` sai e os espaços ao redor são normalizados)

#### Scenario: Retira código concatenado (Fanuc)

- **WHEN** o usuário retira `M6` da linha `M6T1`
- **THEN** o resultado é `T1`

#### Scenario: Boundary protege código de valor maior

- **WHEN** o usuário retira `M6` de um arquivo que contém `M60`
- **THEN** `M60` permanece intacto (o boundary CNC impede o casamento parcial)

#### Scenario: Retira mantendo os demais códigos da linha

- **WHEN** o usuário retira `M6` da linha `M8 M6 M9`
- **THEN** o resultado é `M8 M9`

### Requirement: Faxina de linha após remoção

O sistema SHALL aplicar uma faxina de linha **apenas** nas linhas do resultado que tiveram remoção por uma ação RETIRAR. A faxina MUST: (1) colapsar 2 ou mais espaços/tabs consecutivos em um único espaço; (2) remover espaço sobrando no início e no fim da linha; (3) se a linha ficou **vazia por causa** da remoção, apagar a linha inteira incluindo sua quebra. A faxina MUST NOT alterar linhas que não receberam remoção, e MUST NOT apagar linhas que já eram vazias antes da remoção. O EOL original do arquivo (`\r\n`, `\n` ou `\r`, conforme `EncodingInfo.eol`) MUST ser preservado.

#### Scenario: Linha que sobra vazia é apagada

- **WHEN** o usuário retira `M6` de uma linha que continha apenas `M6`
- **THEN** a linha inteira (e sua quebra) é removida do arquivo

#### Scenario: Linha vazia pré-existente é preservada

- **WHEN** o arquivo já tinha uma linha em branco e o usuário retira um código de outra linha
- **THEN** a linha em branco pré-existente permanece no resultado

#### Scenario: EOL preservado

- **WHEN** o arquivo usa `\r\n` e o usuário retira um código
- **THEN** todas as quebras de linha do resultado continuam `\r\n`

#### Scenario: Faxina não afeta linhas vizinhas

- **WHEN** uma linha tem espaços duplos mas não recebeu remoção
- **THEN** seus espaços permanecem inalterados (a faxina é escopada às linhas tocadas por RETIRAR)

### Requirement: Lote misto compõe substituições e remoções

O sistema SHALL compor, num único passe, regras de Substituir e regras de Retirar sobre o mesmo arquivo, reusando a composição não-cascata existente. Conflitos de **pedaço** (sobreposição de bytes entre uma regra de Substituir e uma de Retirar no mesmo trecho) MUST ser resolvidos pelo mecanismo de `Suppression` já existente (vencedor por escopo → priority → ordem de declaração).

#### Scenario: Substituir e Retirar no mesmo arquivo

- **WHEN** o lote tem `M8 → M08` e `retirar M6`, aplicados ao mesmo arquivo
- **THEN** o resultado contém `M08` e não contém mais `M6`, sem perda de outros códigos

#### Scenario: Conflito de pedaço entre Substituir e Retirar

- **WHEN** uma regra de Substituir e uma de Retirar disputam exatamente o mesmo trecho
- **THEN** o conflito é resolvido por `Suppression` e o trecho recebe apenas a ação vencedora, registrada no plano
