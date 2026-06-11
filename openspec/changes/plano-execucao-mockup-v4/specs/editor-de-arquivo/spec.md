## MODIFIED Requirements

### Requirement: Editor como tela cheia com faixa de arquivos

O sistema SHALL implementar o editor como a **tela Editor** (índice 1 do QStackedWidget raiz), ocupando toda a área de conteúdo. A tela SHALL ter duas áreas: **faixa de arquivos** (esquerda, ~200px) com todos os programas carregados e o **editor** (restante). Clicar num arquivo na faixa SHALL trocar o arquivo aberto sem sair da tela Editor.

#### Scenario: Abrir editor pela tela Lote

- **WHEN** o usuário clica em "✎ Abrir" num arquivo da tela Lote
- **THEN** o rail navega para a tela Editor e o arquivo clicado é aberto no editor

#### Scenario: Trocar arquivo pela faixa lateral

- **WHEN** o usuário clica em outro arquivo na faixa de arquivos do editor
- **THEN** o arquivo aberto no editor muda para o selecionado; se há alteração pendente, a guarda de alterações é acionada

### Requirement: Cabeçalho do arquivo com aviso e botões de salvar

O sistema SHALL exibir no cabeçalho do editor: "Editando `NOME.NC`" (fonte mono), aviso permanente **"⚠ salva direto, sem cópia"** e botões **"Salvar como…"** e **"Salvar"** (verde) à direita. O botão Salvar SHALL seguir o comportamento do Requirement "Botão Salvar reflete o estado de alteração" (habilita só com edição pendente).

#### Scenario: Cabeçalho exibe nome e aviso

- **WHEN** um arquivo é aberto no editor
- **THEN** o cabeçalho mostra "Editando [nome_do_arquivo]" e o aviso "⚠ salva direto, sem cópia"

### Requirement: Toast "Desfazer" após salvar

O sistema SHALL exibir um **toast** no rodapé após um salvamento bem-sucedido com o botão **"Desfazer"**. Clicar em "Desfazer" SHALL restaurar o conteúdo do buffer ao estado imediatamente anterior ao save e reabilitar o botão Salvar. O toast SHALL desaparecer automaticamente após ~5 segundos se não for usado.

#### Scenario: Toast aparece após salvar

- **WHEN** o usuário salva um arquivo no editor
- **THEN** um toast verde com botão "Desfazer" aparece no rodapé por ~5 segundos

#### Scenario: Desfazer restaura conteúdo anterior

- **WHEN** o usuário clica em "Desfazer" no toast imediatamente após salvar
- **THEN** o conteúdo do buffer volta ao estado antes do save e o botão Salvar fica habilitado novamente

### Requirement: Bolinha de status na faixa e no rail

O sistema SHALL exibir uma **bolinha laranja** ao lado do nome do arquivo na faixa lateral quando houver alteração não salva. A mesma bolinha SHALL aparecer no botão "Editor" do rail. Ambas SHALL desaparecer ao salvar ou descartar.

#### Scenario: Bolinha na faixa e no rail ao editar sem salvar

- **WHEN** o usuário digita no editor sem salvar
- **THEN** o arquivo na faixa exibe bolinha laranja e o botão "Editor" no rail também exibe bolinha

### Requirement: Editor de texto integrado por programa

O sistema SHALL oferecer, para cada programa carregado, a ação **"✎ Abrir"** que abre o arquivo na tela Editor. O editor MUST exibir **numeração de linha** e usar **fonte monoespaçada**, permitindo **edição direta**. O conteúdo MUST ser lido com `read_file`, preservando codificação/EOL do original.

#### Scenario: Abrir um programa no editor

- **WHEN** o usuário clica em "✎ Abrir" num programa da lista na tela Lote
- **THEN** o conteúdo do arquivo é carregado no editor com numeração de linha e fonte monoespaçada

#### Scenario: Edição ocorre em memória até salvar

- **WHEN** o usuário digita no editor
- **THEN** as alterações ficam no buffer; o arquivo em disco NÃO é tocado até um Salvar explícito

### Requirement: Gravação in-place segura, sem backup

O sistema SHALL salvar sobrescrevendo o arquivo original. A gravação MUST ser **atômica** (gravar `.tmp` e renomear), MUST **preservar codificação/BOM/EOL** (`encode_text`/`write_atomic`) e MUST ser conferida por **SHA-256 pós-escrita**. A UI MUST exibir o aviso permanente **"⚠ salva direto, sem cópia"**.

#### Scenario: Salvar sobrescreve o original preservando encoding/EOL

- **WHEN** o usuário edita e salva um arquivo CRLF/cp1252
- **THEN** o arquivo é sobrescrito com a mesma codificação/BOM/EOL, sem gerar backup

#### Scenario: Round-trip fiel sem alteração

- **WHEN** o usuário abre e salva sem mudar nada
- **THEN** os bytes gravados são idênticos aos do original

### Requirement: Botão Salvar reflete o estado de alteração

O botão Salvar SHALL estar **desabilitado** quando não há alteração no buffer e **habilitado** ao primeiro edit. Após salvar com sucesso, volta a desabilitado.

#### Scenario: Salvar começa desabilitado

- **WHEN** um arquivo acaba de ser aberto
- **THEN** o botão Salvar está desabilitado

#### Scenario: Editar habilita Salvar

- **WHEN** o usuário faz a primeira alteração
- **THEN** o botão Salvar fica habilitado

### Requirement: Guarda de alterações não salvas

O sistema SHALL, ao tentar **trocar de arquivo** na faixa ou **sair da tela Editor** com alterações pendentes, apresentar confirmação com opções **Salvar / Descartar / Cancelar**. Cancelar MUST manter o editor sem perda.

#### Scenario: Trocar arquivo com alteração pendente pede confirmação

- **WHEN** há alteração no buffer e o usuário clica em outro arquivo na faixa
- **THEN** um diálogo "salvar antes de trocar?" com Salvar / Descartar / Cancelar é exibido

### Requirement: "Salvar como…" com extensão e codificação

O botão **"Salvar como…"** no cabeçalho SHALL abrir um modal para salvar uma cópia com: **extensão** (.nc/.txt/.tap/.iso/.min/.mpf), **codificação** (UTF-8, UTF-8 c/ BOM, ANSI) e **quebra de linha** (CRLF/LF), com **prévia** do resultado. O default SHALL ser preservar o formato original do arquivo.

#### Scenario: "Salvar como…" oferece escolha de formato

- **WHEN** o usuário clica em "Salvar como…"
- **THEN** o modal exibe opções de extensão, codificação e quebra de linha com o original como default

#### Scenario: "Salvar como…" não afeta o Salvar normal

- **WHEN** o usuário usa "Salvar como…" para salvar uma cópia
- **THEN** o Salvar normal continua salvando no arquivo original com o formato original
