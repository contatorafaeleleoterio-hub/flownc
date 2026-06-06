## ADDED Requirements

### Requirement: Editor de texto integrado por programa

O sistema SHALL oferecer, para cada programa da lista, a ação **"Editar"** que abre um editor de texto **embutido na própria janela** (sem abrir o arquivo fora do app). O editor MUST exibir **numeração de linha** e usar **fonte monoespaçada**, permitindo **edição direta** do conteúdo. O conteúdo aberto MUST ser lido com `read_file`, preservando o texto e os metadados de codificação/EOL do original.

#### Scenario: Abrir um programa no editor

- **WHEN** o usuário clica em "Editar" num programa da lista
- **THEN** o conteúdo do arquivo é carregado no editor embutido, com numeração de linha e fonte monoespaçada, pronto para edição

#### Scenario: Edição ocorre em memória até salvar

- **WHEN** o usuário digita ou apaga texto no editor
- **THEN** as alterações ficam apenas no buffer em memória e o arquivo em disco NÃO é tocado até um Salvar explícito

### Requirement: Gravação in-place segura, sem backup

O sistema SHALL salvar **sobrescrevendo o arquivo original na pasta de origem**, **sem criar cópia de backup** (decisão de produto: atalho de ajuste manual rápido). A gravação MUST ser **atômica** (gravar `.tmp` no mesmo volume e então `os.replace`), MUST **preservar a codificação/BOM/EOL** detectados na leitura (reusar `encode_text`/`write_atomic`) e MUST ser **conferida por SHA-256 após a escrita** (reusar `integrity_hash`), reportando qualquer divergência como falha. Como o invariante histórico "o original nunca é sobrescrito" não se aplica a este caminho, a ausência de backup MUST ser compensada por essas garantias (atômica + dupla conferência + aviso explícito) e a UI MUST exibir o aviso permanente **"salva direto, sem cópia"**.

#### Scenario: Salvar sobrescreve o original preservando encoding/EOL

- **WHEN** o usuário edita e clica em Salvar num arquivo CRLF/cp1252
- **THEN** o arquivo original é sobrescrito no lugar, com a mesma codificação/BOM e o mesmo EOL, sem gerar arquivo de backup

#### Scenario: Round-trip fiel quando nada muda

- **WHEN** o usuário abre um arquivo e salva sem alterar nada
- **THEN** os bytes gravados são idênticos aos do original (byte-a-byte)

#### Scenario: Conferência SHA detecta corrupção

- **WHEN** a conferência SHA-256 pós-escrita não bate com o conteúdo editado
- **THEN** a operação é reportada como falha ao usuário (e registrada), não como sucesso

#### Scenario: Falha de codificação não corrompe o original

- **WHEN** o conteúdo editado não pode ser codificado na codificação do arquivo
- **THEN** o salvamento é abortado antes de qualquer escrita, o original permanece íntegro e nenhum `.tmp` órfão é deixado

### Requirement: Botão Salvar reflete o estado de alteração

O sistema SHALL manter o botão **Salvar desabilitado enquanto não houver alteração** no buffer em relação ao conteúdo carregado, e habilitá-lo assim que houver qualquer edição. Após um Salvar bem-sucedido, o estado MUST voltar a "sem alteração" (Salvar desabilitado).

#### Scenario: Salvar começa desabilitado

- **WHEN** um arquivo acaba de ser aberto no editor
- **THEN** o botão Salvar está desabilitado

#### Scenario: Editar habilita Salvar

- **WHEN** o usuário faz a primeira alteração no buffer
- **THEN** o botão Salvar fica habilitado

#### Scenario: Salvar volta ao estado limpo

- **WHEN** o usuário salva com sucesso
- **THEN** o botão Salvar fica desabilitado novamente até a próxima alteração

### Requirement: Guarda de alterações não salvas

O sistema SHALL, ao tentar **trocar de arquivo** ou **fechar o editor** com alterações pendentes, apresentar uma confirmação **"salvar antes de trocar?"** com as opções **Salvar**, **Descartar** e **Cancelar**. Cancelar MUST manter o editor no estado atual sem perder a edição.

#### Scenario: Trocar de arquivo com pendência pede confirmação

- **WHEN** o usuário tem alteração não salva e clica em "Editar" de outro programa
- **THEN** aparece a confirmação "salvar antes de trocar?" com Salvar / Descartar / Cancelar

#### Scenario: Cancelar preserva a edição

- **WHEN** o usuário escolhe Cancelar na confirmação
- **THEN** o editor permanece no arquivo atual com a alteração pendente intacta

### Requirement: Convivência com o fluxo de Lote

O sistema SHALL manter o fluxo de Lote inalterado quando o editor existe. A seleção de programas em lote (marcação) e a gravação de Lote (saída em pasta separada / backup) MUST continuar funcionando como antes; o editor é um caminho **independente** para ajuste de um único arquivo.

#### Scenario: Lote permanece intacto

- **WHEN** o usuário usa o editor para ajustar um arquivo e depois executa o Lote
- **THEN** o Lote opera normalmente sobre os programas marcados, com seu próprio fluxo de saída/backup, sem interferência do editor
