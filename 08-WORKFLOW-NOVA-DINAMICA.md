# 08 — WORKFLOW E DINÂMICA DO SISTEMA (nova dinâmica por código)

**Projeto:** CNC Batch Editor — substituição e remoção de códigos em programas CNC em lote.
**Status:** desenho de produto aprovado (a implementar). Substitui o fluxo anterior "por programa".
**Data:** 2026-06-03
**Base de decisão:** pesquisa de UX/HMI validada (`07-PROMPT-PESQUISA-UI.md` + validação web), análise `06-ANALISE-UX-WORKFLOW.md`, e mockups `mockups\08`, `mockups\09`, `mockups\10`.
**Leitura rápida:** este documento descreve **o que o sistema faz, que problema resolve e como o operador trabalha nele**. Não é o manual de implementação (esse virá depois).

---

## 1. Contexto

### 1.1 O que é
Ferramenta **desktop Windows** (PySide6/Qt — não é site nem app de celular) que **edita programas CNC em lote**: troca um código por outro, ou remove um código, em vários programas de uma vez, com pré-visualização e gravando sempre em pasta nova (os originais nunca são alterados).

> **Código CNC (G-code):** a "receita" que comanda a máquina. Cada linha tem códigos como `M8` (liga fluido), `G54` (referência da peça), `T0101` (ferramenta), `S2000` (rotação). É texto puro.

### 1.2 Quem usa
**Operador técnico de CNC.** Tem alto conhecimento prático de usinagem, mas **não é usuário avançado de computador**. Uso **repetitivo e diário**, no chão de fábrica (pode ter luva, tela suja, iluminação ruim, pressa).

### 1.3 Onde se encaixa
É um projeto **separado** do *ToolOptimizer CNC* (calculadora de parâmetros). Aqui o foco é **editar o texto dos programas**, não calcular usinagem.

### 1.4 Criticidade (por que é levado a sério)
Erro tem **custo físico alto**: código errado pode causar ferramenta errada, colisão, refugo (peça perdida) ou dano à máquina. Por isso o sistema é construído em torno de **prevenção de erro**: pré-visualizar antes de gravar e **nunca tocar no arquivo original**.

---

## 2. Problemas que o sistema resolve

### 2.1 A dor real
Hoje, para trocar/remover um código em muitos programas, o operador faz isso **manualmente, arquivo por arquivo**, em um editor de texto comum. Isso é:
- **Lento** — abrir, achar, trocar, salvar, repetir em dezenas de arquivos.
- **Arriscado** — fácil esquecer um arquivo, trocar errado, ou alterar algo sem querer.
- **Sem rastreio** — não fica registro do que foi mudado.

### 2.2 As duas ações mais frequentes e trabalhosas
1. **Substituir um código por outro** (ex.: `M8` → `M08`, `G54` → `G55`, `S2000` → `S1500`).
2. **Retirar um código pontual** (ex.: remover o `M6` — troca de ferramenta — em casos em que a ferramenta é usada com o eixo-árvore desligado e o `M6` provocaria um giro de posicionamento indesejado).

O sistema foi desenhado para tornar **essas duas ações rápidas, claras e seguras**.

### 2.3 O que muda com o sistema
| Antes (manual) | Com o sistema |
|---|---|
| Edita arquivo por arquivo | Define a regra **uma vez** e aplica em vários programas |
| Risco de alterar o original | **Grava em pasta nova; original intocado** |
| Sem conferência | **Pré-visualização + resumo** antes de gravar; conferência de integridade ao salvar |
| Sem padronização de códigos | **Biblioteca de códigos** com função e variações por máquina |
| Sem registro | **Log** de tudo que foi feito |

---

## 3. Princípios de design (validados por pesquisa)

Estas decisões não são palpite — vieram de normas e estudos (ISA-101 de HMI industrial, ISO 9241-110 de diálogo, Nielsen Norman Group, WCAG), conferidos com pesquisa própria:

1. **Fluxo "por código", não "por programa".** O operador pensa primeiro *"qual código vou mexer"* e só depois *"em quais programas"*. O sistema segue esse fluxo. É o padrão consagrado de **construtor de regras** (igual a regras de filtro de e-mail / formatação condicional).
2. **Pré-visualizar antes de gravar (porteiro).** Nenhuma gravação acontece sem o operador ver o resumo do que vai ser feito.
3. **O original nunca é alterado.** Grava sempre em pasta nova, com data. Regra inegociável.
4. **Cor nunca sozinha.** Todo sinal de cor vem com **ícone + texto** (por causa de daltonismo e tela suja). Verde = ok, amarelo = atenção, vermelho = bloqueio/risco.
5. **Alvos grandes e contraste forte** (chão de fábrica): botões e linhas confortáveis de clicar, fonte legível.
6. **Ação destrutiva é controlada.** "Retirar código" é limitado e protegido (ver §6.2).
7. **Feedback sempre visível.** Resumo do lote em tempo real, animações de progresso, mensagens de erro que dizem **o que fazer**.

---

## 4. Funções do sistema

### 4.1 Perfil de máquina
Conjunto salvo de configurações de uma máquina. Guarda as **variações de código** dela e as regras montadas. Ao **carregar um perfil**, as regras e códigos voltam automaticamente — mas a **lista de programas começa vazia** (ver §6.4).

### 4.2 Biblioteca de códigos
Um "dicionário" de códigos CNC. Cada item tem:
- **Código** (ex.: `M8`)
- **Função** (ex.: "liga fluido de corte")
- **Variação por máquina/perfil** (ex.: `M8` na MAZAK vira `M08`) — porque comandos diferentes usam grafias diferentes para a mesma função.

Características:
- Já vem **completa, com os códigos padrão do mercado**. Novos só quando realmente necessário.
- **Totalmente editável** (criar, editar, salvar variações).
- Botão **"Adicionar código" sempre visível**.
- Ao adicionar um código novo durante o fluxo, um **"+"** pergunta se salva **neste perfil** ou **global** — mantendo as variações por máquina organizadas.

> **Por que variações por máquina:** o G-code tem "dialetos". `M8` e `M08` fazem a mesma coisa (liga fluido), mas comandos diferentes esperam grafias diferentes. Guardar isso por perfil evita erro.

### 4.3 Compositor de regras (o coração do sistema)
Onde o operador monta cada regra, da **esquerda para a direita**:
- **① Código de origem** — dropdown rápido com os códigos da biblioteca.
- **② Ação** — **Substituir** ou **Retirar**.
- **③ Alvo** — se *Substituir*, escolhe o **código novo** (da biblioteca, menos o já selecionado). Se *Retirar*, aparece a **trava de segurança** (1 código por execução).
- **Programas** — escolhe em **quais** programas a regra vale (ver §4.5).

### 4.4 Ações: Substituir e Retirar
- **Substituir:** troca o código de origem pelo código novo. Ex.: `G54` → `G55`.
- **Retirar:** remove o código de origem. **Ação controlada** — só **1 código por execução** (ver §6.2). Uso típico: remover um `M6` pontual.

### 4.5 Seleção de programas
A lista de programas **começa vazia** (os programas mudam a cada trabalho). O operador clica em **"Abrir pasta…/Adicionar programa(s)…"** e escolhe os arquivos. Depois:
- Os programas aparecem em uma **lista**.
- A configuração escolhida (ex.: `G54 → G55`) fica **visível e destacada**.
- Um **indicador** mostra **quantos programas** vão receber aquela regra.

### 4.6 Resumo em tempo real (lista de regras)
Conforme o operador adiciona regras, cada uma vira um **cartão** num painel de resumo, mostrando a regra e o escopo (ex.: "`M8` → `M08` · 10 programas"). Cada cartão pode ser **editado, duplicado ou excluído**. Se duas regras mexerem no mesmo código, aparece um **aviso de conflito** (amarelo) para o operador conferir.

### 4.7 Execução e pré-visualização
Ao clicar **Executar**, o sistema processa (com animação "Executando… / Analisando…") e mostra um **pop-up de resumo** com a lista clara das alterações (regra, nº de ocorrências, programas) **antes de gravar qualquer coisa**.

### 4.8 Salvamento
Ao clicar **Salvar** (no pop-up de resumo), o sistema grava (animação "Salvando…") e **abre a pasta** dos arquivos automaticamente. Regras de gravação em §6.3.

### 4.9 Log e conferência
Toda execução gera **registro** do que foi feito, e ao salvar há **conferência de integridade** (uma "impressão digital" SHA-256 de cada arquivo, para provar que saiu certo). *(Recurso já existente no motor atual.)*

### 4.10 Verificações de segurança — **fora por enquanto**
A seção de verificações configuráveis (ex.: "deve existir M30", "não pode existir M6 solto") **não entra neste momento**, por decisão. Fica registrada para retornar depois — o pop-up "Executar → Analisar → Resumo" é o lugar natural dela (ver §8).

---

## 5. Workflow (passo a passo)

> Fluxo principal do dia a dia. A numeração segue a tela, **da esquerda para a direita**.

**Passo 0 — Abrir o app e escolher o perfil**
O operador abre o programa e seleciona o **perfil da máquina** (ex.: MAZAK VTC-530). As regras salvas do perfil carregam; a **lista de programas vem vazia**.

**Passo 1 — Escolher o código de origem**
No primeiro campo, seleciona no dropdown o **código que vai mexer** (ex.: `G54`).

**Passo 2 — Escolher a ação**
- **Substituir** → aparece o campo "Trocar por"; escolhe o código novo (ex.: `G55`).
- **Retirar** → some o "Trocar por" e aparece a **trava**: "🔒 Retirar é controlado: 1 código por execução. Só códigos válidos da biblioteca."

Um **banner destacado** mostra a configuração atual (ex.: `G54 → G55`), e fica visível durante a escolha dos programas.

**Passo 3 — Escolher os programas**
A lista está vazia. O operador clica **"Abrir pasta…"** e seleciona os programas. Eles aparecem na lista, com **indicador de quantos** vão receber a regra (ex.: "10 programas receberão esta regra").

**Passo 4 — Adicionar a regra ao lote**
Clica **"Adicionar regra ao lote"**. A regra vira **cartão** no resumo (à direita). A zona de programas **reseta** para a próxima regra.

**Passo 5 — Repetir para outras regras (opcional)**
Volta ao Passo 1 e monta novas regras (ex.: `M8 → M08`, depois "retirar `M6`"). O resumo cresce em tempo real e avisa **conflitos**.

**Passo 6 — Executar**
Clica **Executar**. Animação "Executando alterações… → Analisando resultado…". Ao fim, abre o **pop-up de resumo** com tudo que será feito (regras, ocorrências, programas) e a confirmação "originais intactos · grava em `…\_processado_PERFIL_data\`".

**Passo 7 — Salvar**
No pop-up, confere e clica **Salvar**. Animação "Salvando programas…". Ao terminar, **a pasta de destino abre automaticamente**. Originais permanecem intactos; conferência de integridade feita.

**Passo 8 — Novo lote**
Pode iniciar outro lote. Se quiser reusar as regras, salva no perfil.

---

## 6. Regras de negócio e invariantes de segurança

### 6.1 O original NUNCA é alterado *(inegociável)*
A gravação é sempre em **pasta nova** (`_processado_PERFIL_data_hora\`), separada dos originais. A pasta de saída nunca é a pasta de origem.

### 6.2 "Retirar" é uma ação controlada *(anti-erro e anti-abuso)*
Remover código é poderoso e perigoso (pode quebrar a estrutura do bloco). Por isso é cercado de proteções:
- **Limite rígido: 1 código por execução.** Não dá para encadear várias remoções de uma vez.
- **Lista branca (allowlist):** só aceita **código válido da biblioteca** — nada de texto livre arbitrário que possa corromper a linha.
- **Pré-visualização obrigatória:** mostra exatamente as **linhas afetadas** antes de gravar.
- **Bloqueio por conflito:** se a remoção colidir com outra regra, o sistema avisa/bloqueia.
- **Registro em log:** toda remoção fica auditável.

> **Por quê tão restrito:** limitar e validar a ação destrutiva evita que um erro de operação (ou uma tentativa de "forçar" o sistema) gere bug, conflito ou perda de material. É a aplicação prática de **validação de entrada + privilégio mínimo + confirmação explícita**.

### 6.3 Salvamento (mantém o comportamento atual)
- Grava em **pasta nova com data** → não colide com lotes anteriores e **não sobrescreve** nada.
- **Abre a pasta** ao terminar.
- Conferência de integridade (SHA-256) registrada no log.

### 6.4 Perfil salvo carrega regras, mas programas começam vazios
Ao carregar um perfil, as **regras e códigos** voltam automaticamente. A **lista de programas inicia vazia** — o operador escolhe os programas do trabalho atual a cada vez (os arquivos mudam toda hora). Se houver programas previamente associados, é preciso **reconfirmar/reselecionar** antes de executar.

### 6.5 Conflito entre regras
Se duas regras tocarem o mesmo código, o sistema mostra **aviso de conflito** no resumo, para o operador resolver antes de executar.

---

## 7. Estados, cores e feedback

| Estado | Cor | Sempre acompanhado de |
|---|---|---|
| Validado / pronto / sucesso | Verde | ícone ✓ + texto |
| Atenção / revisar / 0 ocorrências | Amarelo | ícone ▲ + texto |
| Bloqueio / falha / ação destrutiva | Vermelho | ícone ■/🔒 + texto |
| Neutro / informativo | Cinza/Azul | texto |

- **0 ocorrências** de uma troca é tratado como **sinal útil** (amarelo): avisa o operador que algo pode estar errado (código não existe naquele programa).
- **Progresso:** animações simples em operações demoradas ("Executando…", "Analisando…", "Salvando…").
- **Mensagens de erro acionáveis:** dizem o que falhou e o que fazer (ex.: "`G54` não encontrado em 3 arquivos — confira a regra ou os programas").

---

## 8. Fora de escopo (por enquanto)

- **Verificações de segurança configuráveis** (deve existir / não pode existir / contagem) — adiadas por decisão. Quando voltarem, entram como **porteiro no pop-up de resumo** (bloqueia o Salvar se uma verificação crítica falhar). A estrutura do fluxo "Executar → Analisar → Resumo → Salvar" já reserva esse lugar.
- **Inserção de novas linhas/blocos** (o sistema mexe em códigos existentes, não cria blocos novos).
- **Edição manual livre** de programa (não é editor de texto; é editor por regras).

---

## 9. Glossário (linguagem simples)

- **G-code / programa CNC:** o texto que comanda a máquina.
- **Código:** um comando do programa (ex.: `M8`, `G54`, `T0101`).
- **Regra:** uma instrução montada pelo operador = código + ação (substituir/retirar) + programas onde vale.
- **Lote:** o conjunto de regras + programas de um trabalho.
- **Perfil:** configurações salvas de uma máquina (regras e variações de código).
- **Biblioteca:** dicionário de códigos com função e variações por máquina.
- **Escopo:** em quais programas uma regra é aplicada.
- **Preview / pré-visualização:** ver o que vai acontecer antes de gravar.
- **SHA-256 / integridade:** "impressão digital" de cada arquivo, para provar que foi salvo corretamente.
- **Allowlist (lista branca):** só permite itens de uma lista aprovada (aqui, códigos válidos da biblioteca).

---

## 10. Rastreabilidade (de onde veio cada decisão)

- **Fluxo por código + ações Substituir/Retirar + biblioteca com variações:** proposta do Rafael (2026-06-03), validada contra padrão "rule builder" (UI-Patterns, Hagan Rivers), regras de e-mail/formatação condicional, CIMCO Edit ("Replace All from File") e dialetos de G-code (CNCCookbook).
- **Tela única + pré-visualizar antes de gravar + cor com ícone + alvos grandes:** pesquisa `07` validada (ISA-101, ISO 9241-110, NN/G, WCAG 2.2).
- **Indicador de escopo por regra (resolve o "qual programa tem troca exclusiva"):** evolução discutida nos mockups `09`/`10` — o escopo virou propriedade da regra, visível no resumo.
- **Mockups de referência:** `mockups\10-mockup-fluxo-codigo.html` (fluxo final interativo), `mockups\08` e `mockups\09` (etapas anteriores).
- **Invariantes herdadas do sistema atual:** original nunca alterado, gravação em pasta com data, conferência SHA-256, log (motor `core/` estável — 106 testes).

---

### Nota de implementação (escopo técnico)
A maioria das mudanças é de **interface** (`ui/`). Porém **"Retirar código"** e detalhes do fluxo de regras podem exigir trabalho no **motor (`core/`)** — que é a parte testada e estável (106 testes). Toda mudança no motor precisa de **testes novos** antes de ser confiável. A regra "original nunca alterado" deve ser preservada em qualquer cenário.
