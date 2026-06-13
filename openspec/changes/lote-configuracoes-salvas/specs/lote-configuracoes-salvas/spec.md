## ADDED Requirements

### Requirement: Botões de configuração na linha do título "Lote de edições"

O sistema SHALL exibir, na **mesma linha do título "Lote de edições"** (espelhando o painel
Programas, que tem "Marcar todos"/"+ Adicionar programa(s)…" na linha do título), dois botões:
**"Abrir configuração"** e **"Salvar configuração"**. Os botões SHALL usar o estilo ghost padrão da
tela Lote.

#### Scenario: Botões presentes na linha do título

- **WHEN** a tela Lote é aberta
- **THEN** "Abrir configuração" e "Salvar configuração" aparecem na linha do título "Lote de edições"

### Requirement: Salvar configuração com nome (acesso rápido)

Clicar em **"Salvar configuração"** SHALL abrir um input pedindo o **nome** da configuração, com
botões **Salvar** e **Cancelar**. Salvar SHALL persistir **apenas as edições montadas (regras)** do
lote — trocas e blocos — **sem os programas**. Se já existir uma configuração com o mesmo nome, o
sistema SHALL pedir confirmação antes de sobrescrever. As configurações SHALL ficar num diretório de
dados da aplicação **compartilhado** entre os operadores da mesma instalação.

#### Scenario: Salvar abre input de nome

- **WHEN** o operador clica em "Salvar configuração" com edições no lote
- **THEN** abre um input com campo de nome e botões Salvar/Cancelar

#### Scenario: Salvar guarda só as regras

- **WHEN** o operador salva uma configuração chamada "Mudar ponto zero" com G54→G55 e M8→M9
- **THEN** a configuração guarda as duas edições (regras), sem nenhum programa associado

#### Scenario: Cancelar não salva

- **WHEN** o operador clica em "Salvar configuração" e depois em Cancelar
- **THEN** nenhuma configuração é criada

#### Scenario: Nome repetido pede confirmação

- **WHEN** o operador salva com um nome que já existe
- **THEN** o sistema pede confirmação antes de sobrescrever a configuração existente

### Requirement: Abrir configuração carrega as edições no lote

Clicar em **"Abrir configuração"** SHALL listar as configurações salvas. Ao escolher uma, o sistema
SHALL carregar suas edições **direto no lote como cartões**, já com as regras prontas e com **0
programas**. Se houver lote montado, o sistema SHALL pedir confirmação antes de substituir.

#### Scenario: Abrir lista as configurações salvas

- **WHEN** o operador clica em "Abrir configuração"
- **THEN** uma lista com os nomes das configurações salvas é exibida

#### Scenario: Escolher carrega edições sem programas

- **WHEN** o operador escolhe "Mudar ponto zero"
- **THEN** as edições G54→G55 e M8→M9 viram cartões no lote, cada um com 0 programas

#### Scenario: Carregar com lote montado pede confirmação

- **WHEN** há edições no lote e o operador escolhe abrir uma configuração
- **THEN** o sistema pede confirmação antes de substituir o lote atual

### Requirement: "Aplicar aos marcados" preenche os programas das edições

O sistema SHALL oferecer **"Aplicar aos marcados"** para atribuir os **programas marcados** ao
conjunto das edições carregadas que estão sem programas. O botão SHALL ficar habilitado somente
quando houver ao menos uma edição sem programas **e** ao menos um programa marcado; caso contrário,
o tooltip SHALL explicar o que falta.

#### Scenario: Aplicar preenche edições sem programas

- **WHEN** há edições carregadas com 0 programas e o operador marca 8 programas e clica "Aplicar aos marcados"
- **THEN** essas edições passam a ter os 8 programas no conjunto delas

#### Scenario: Botão desabilitado sem programas marcados

- **WHEN** há edições sem programas mas nenhum programa está marcado
- **THEN** "Aplicar aos marcados" está desabilitado com tooltip "Marque ao menos 1 programa"

### Requirement: Configuração persiste trocas e blocos

O armazenamento de configuração SHALL guardar tanto edições de **troca de código** (`swap`) quanto
de **inserção de bloco** (`ins`), preservando todos os campos da regra (origem/destino/remover;
texto/modo/código/linha) e **omitindo os programas**. Abrir a configuração SHALL reconstruir as
edições com os mesmos campos.

#### Scenario: Bloco sobrevive ao salvar/abrir

- **WHEN** o operador salva uma configuração que contém uma edição de bloco e depois a abre
- **THEN** a edição de bloco é reconstruída com o mesmo texto, modo, código de âncora e linha
