# Correções do Mockup FlowNC — Documento Técnico

> ## ✅ CONCLUÍDO — OS 17 ITENS IMPLEMENTADOS NO MOCKUP
> Os 17 itens foram implementados em `mockups/painel-final.v2.html` (protótipo interativo,
> sem backend real). As 2 variantes `painel-final.v2-*-combo-*.html` foram removidas.
> **Próximo passo:** o Mestre revisa o protótipo no navegador; depois de aprovado, portar
> as mudanças para o app Python (etapa posterior, fora deste documento).
>
> **Checklist dos 17 itens** (✅ implementado no mockup):
> - ✅ 1. Placeholders + seta nos menus de código (campos viram dropdown pesquisável; seta inverte)
> - ✅ 2. Contador ao vivo no botão "Adicionar edição ao lote (N)" + sem texto redundante
> - ✅ 3. Selo da Seção 3: "salvos na pasta original · backup em pasta separada" (+ overlays)
> - ✅ 4. "+ Adicionar código" movido para a Seção 1 + modal de cadastro (com bloco opcional)
> - ✅ 5. Botão ✕ único de excluir + tooltips "Remover" nas 3 seções + foco padronizado
> - ✅ 6. Botões/ações padronizados entre Seções 2 e 3 (mesmo anel de foco/altura/raio)
> - ✅ 7. Programas iniciam desmarcados; clique no ✓ marca/desmarca (linha esmaecida)
> - ✅ 8. Lista de programas em colunas: Nome | Data de modificação | Tipo | Tamanho (cabeçalho fixo)
> - ✅ 9. Menu de códigos pesquisável: frequentes no topo + busca por código/descrição
> - ✅ 10. Fluxo explícito: origem→destino→"Adicionar edição"; destino vazio = remover (com aviso)
> - ✅ 11. Lista de edições dinâmica: recolhida quando vazia, cresce e pisca ao incluir
> - ✅ 12. Resumo com estado vazio; cards/contadores/selo/CTA só aparecem com itens
> - ✅ 13. "Perfil" → "Configurações salvas" (seletor + criar/salvar/reutilizar, em memória)
> - ✅ 14. Ações do Resumo funcionais: ✎ devolve ao compositor · ⧉ duplica · ✕ remove
> - ✅ 15. Execução: trava o CTA, pop-up com barra de progresso 0→100%, reabilita ao fim
> - ✅ 16. Narrativa de salvamento na pasta original + backup em pasta escolhida/fixa/trocável
> - ✅ 17. Inserir bloco multi-linha em posição (linha Nº ou código), com prévia (modal ovInsert)

## Contexto
Foram levantados **17 problemas** na interface do FlowNC. A estratégia aprovada é
implementá-los **primeiro no mockup aprovado** (`mockups/painel-final.v2.html`),
transformando-o num **protótipo interativo**: clicar em botões abre modais/painéis,
listas mudam de estado, setas invertem etc. — tudo navegável, **sem lógica real de
backend** (sem ler/gravar arquivo de verdade). Depois de aprovado o protótipo, as
mudanças serão portadas para o app Python (etapa posterior, fora deste documento).

Decisões confirmadas com o Mestre:
1. **Arquivo alvo:** `painel-final.v2.html`. As 2 variantes geradas pelo Codex
   (`painel-final.v2-with-combo-feedback.html` e `painel-final.v2-CODE-COMBO-UPDATED.html`)
   serão **consolidadas/removidas** para não confundir.
2. **Itens 1 e 7** (já feitos no app) **serão replicados** no mockup — ele vira a
   referência visual completa.
3. **Profundidade:** **fluxo visual completo** nos itens pesados (15/16/17) — pop-ups,
   barra de progresso, passos falsos com timers; sem lógica real.
4. **Este documento** é a especificação a ser revisada **antes** de implementar.

### Convenções do mockup (a manter)
- Design system 100% por **tokens** no `:root` (zero inline style, zero cor/valor solto).
- Simulação por **JS + `setTimeout`** e classes `.show`/overlays (já existe o padrão:
  `show(id)`/`hide(id)`, overlays `ovRun`/`ovRes`/`ovSave`/`ovSwitch`/`ovSaved`/`ovSaveAs`).
- Fontes IBM Plex locais (offline). Nada de CDN.
- **Cores:** a paleta é a "Precisão Laranja" — ver `docs/PALETA_PRECISAO_LARANJA.md` (fonte da verdade).

---

## Status — JÁ aplicado nesta sessão

**No app (commit `74f899d`, master, sem push — 148 testes verdes):**
- Item 1 (placeholders + seta nos combos de código) e item 7 (programas iniciam desmarcados, ✓).

**No mockup `painel-final.v2.html` (base visual, antes dos sprints):**
- **Paleta "Precisão Laranja"** aplicada: header slate, CTA laranja único ("Executar Lote"),
  painéis L `#EDF0F5` / R `#E5EAF2`, azul eliminado → slate, badges nos novos tons.
  Detalhes em `docs/PALETA_PRECISAO_LARANJA.md`.
- **Polimento visual** (sutil): raios mais fechados/consistentes, tags retangulares, menos brilho
  glossy/sombras sóbrias, emojis decorativos → glifos neutros.
- **Botão ✕ de excluir padronizado** nas 3 seções (igual ao `.filex` dos programas).

**Concluído (sessão 10):**
- Os **17 itens** implementados no mockup (3 sprints — ver fim do documento). Sintaxe JS validada.
- As 2 variantes `painel-final.v2-with-combo-feedback.html` e `…-CODE-COMBO-UPDATED.html` **removidas**.
- **Pendente:** revisão visual do Mestre no navegador → depois, portar ao app Python.

---

## Itens (ordenados do mais simples ao mais complexo)

Legenda do status no mockup: 🟢 já existe parcialmente · 🟡 existe mas diverge · 🔴 não existe.

### 1. Placeholders e indicação dos menus suspensos — Muito baixa · 🟡
- **Problema:** campos de código iniciam vazios/sem pista de que são menu; sem feedback ao abrir.
- **Estado atual:** `.drop#srcDrop`/`#dstDrop` (linhas ~506-511) mostram um código fixo
  (`M8`/`M08`) e a seta `▾`; o clique chama `cycleSrc()` que **cicla** um array fixo
  (`SRC`, ~710) — não é dropdown de verdade nem tem placeholder. A seta não inverte.
- **Mudança:** texto-guia **"Selecione o código"** quando vazio; seta `▾` à direita que
  vira `▴` quando a lista abre. Alinhar com o app (já feito lá).
- **Interação:** clicar abre a lista (ver item 9); ao abrir, `▾→▴`; ao escolher/digitar, o
  guia some e mostra o código; ao limpar, o guia volta.
- **Risco:** baixo. Depende do item 9 (virar dropdown real) para ficar coerente.

### 2. Remover info desnecessária e pôr contador no botão "Adicionar edição ao lote" — Muito baixa · 🟡
- **Problema:** texto informativo ocupa espaço sem valor; falta um contador claro.
- **Estado atual:** botão `.addrule#addRuleBtn` "Adicionar edição ao lote →" (linha ~536),
  **sem contador** e sem texto redundante abaixo (no mockup v2 o texto já não existe; no app
  ainda existe).
- **Mudança:** exibir **contador ao vivo no próprio botão**, ex.: `Adicionar edição ao lote (2) →`
  (ou badge), refletindo `pendingEdits.length` (+ rascunho, conforme item 10). Garantir que
  nenhum texto-ajuda redundante reapareça.
- **Interação:** o número muda em tempo real ao montar/remover edições; botão desabilita
  quando não há nada a enviar.
- **Risco:** baixo. Acoplado ao item 10/11 (o que conta como "edição pronta").

### 3. Trocar o informativo verde da Seção 3 — Muito baixa · 🟡
- **Problema:** o aviso verde atual não é prático.
- **Estado atual:** `.seal-big` (linhas ~560-563): "Editados → pasta da máquina · originais → backup".
- **Mudança:** novo texto: **"Arquivos editados serão salvos na pasta original. Backups serão
  armazenados em pasta separada."** (alinha com o item 16). Ajustar também os textos dos overlays
  que falam "pasta da máquina"/`\\servidor\cnc\trabalho\` (linhas ~640, ~820-821).
- **Interação:** apenas texto; mantém o selo/ícone 🛡 e o caminho de backup de exemplo.
- **Risco:** baixo (texto). É a face visível do item 16.

### 4. Reposicionar o botão "+ Adicionar código" — Baixa · 🟡
- **Problema:** botão fora do contexto de uso (hoje no cabeçalho global).
- **Estado atual:** `<button class="hbtn blue">+ Adicionar código</button>` no header (linha ~495).
- **Mudança:** **mover para a Seção 1 (Configurações)**, junto dos campos/da lista de edições.
  Manter "Biblioteca de Códigos" no header (não citado). Padronizar o estilo ao da seção.
- **Interação:** clicar abre um modal "Adicionar código à biblioteca" (campos código + descrição
  + opção multi-linha do item 17), simulado.
- **Risco:** baixo (mover + 1 modal simulado).

### 5. Botão de exclusão (✕) e padronização de tamanhos — Baixa · 🟡
- **Problema:** ✕ pouco intuitivo; inconsistência visual entre botões.
- **Estado atual:** três "✕/remover" diferentes: `.el-x` (lista de edições, ~243), `.filex`
  (programas, ~276) e o ✕ dos modais (`.mh .x`). Tamanhos/cores divergem.
- **Mudança (decidido):** **botão ✕ único** para excluir itens em TODAS as listas — quadrado,
  fundo neutro, ✕ vermelho, hover vermelho-claro (padrão da lista de programas, classe `.filex`).
  Aplicado em Configurações montadas, Programas e Resumo, com mesmo tamanho/área de clique/tooltip
  "Remover". ✕ também fecha modais. (Substitui a ideia anterior de usar 🗑.) **Já aplicado no mockup.**
- **Interação:** hover destaca em vermelho; tooltip explica; clique remove a linha
  correspondente (já existe `removePending`/`removeFile`).
- **Risco:** baixo. Toca várias classes CSS — fazer via tokens para não duplicar.

### 6. Padronizar botões e layout entre as Seções 2 e 3 — Baixa · 🟡
- **Problema:** Seções 2 e 3 usam componentes visuais diferentes.
- **Estado atual:** Seção 2 usa `.ghost`, `.editbtn`, `.filex`, `.addrule`; Seção 3 usa ícones
  `.racts` (✎ ⧉ 🗑) e o `.cta`. Sem sistema único.
- **Mudança:** definir **um conjunto único** de botões (primário, secundário/soft, fantasma,
  perigo, ícone) com mesma altura/raio/sombra/tipografia, e aplicar nas duas seções.
- **Interação:** comportamento uniforme (hover/disabled/foco) em ambas.
- **Risco:** médio-baixo (refator CSS amplo). Base já existe (`.btn-soft`, `.ghost`, `.iconbtn`).

### 7. Programas sem seleção automática + visual de check — Baixa · 🟡 (já feito no app)
- **Problema:** programas aparecem já marcados.
- **Estado atual:** cada `.file` tem `.chk` **verde com ✓** (marcado) por padrão (linhas ~529-534);
  só `O1005` está `.file off`/`.chk off`. O visual já é "✓" (não caixa cheia).
- **Mudança:** **iniciar todos desmarcados** (`.file off` + `.chk off`) e marcar só ao clicar.
  Mantém o padrão de **✓** (já é o caso). Espelha o que foi feito no app.
- **Interação:** clicar no `.chk` alterna ✓ (verde) ↔ vazio; linha desmarcada fica levemente
  esmaecida (`.file.off`, opacity .72). Contadores/escopo reagem.
- **Risco:** baixo.

### 8. Organização da lista de programas em colunas — Baixa · 🟡
- **Problema:** informações "soltas" na linha; difícil comparar.
- **Estado atual:** `.file` é flex livre: `chk · fname · fmeta · editbtn · filex` — nome e
  tamanho/data não alinham entre linhas (linhas ~263-274).
- **Mudança (decidido):** layout em **colunas alinhadas estilo Explorador do Windows**:
  **cabeçalho fixo** com exatamente **4 colunas — Nome | Data de modificação | Tipo | Tamanho**,
  células alinhadas (grid), largura por coluna. O **✓ de seleção** (item 7) fica à esquerda e os
  **botões Editar/🗑** à direita, como **controles da linha — fora das 4 colunas**.
  **Sem ordenar por clique agora** (fica como melhoria posterior).
- **Interação:** colunas alinhadas sob o cabeçalho; ✓ e ações por linha.
- **Risco:** médio-baixo (trocar flex por grid + cabeçalho).

### 9. Filtrar os códigos do menu suspenso — Média · 🟡
- **Problema:** lista com muitos códigos pouco usados; busca lenta.
- **Estado atual:** os campos da Seção 1 **não** têm lista pesquisável (apenas `cycleSrc()`).
  O editor **já tem** o componente certo: `.libdrop` pesquisável (`renderLib`/`filterLib`,
  ~990-1014) sobre `LIB` (247 no app; amostra no mockup).
- **Mudança (decidido):** reusar o `.libdrop` (busca por código/descrição) nos campos
  origem/destino da Seção 1, com um grupo curto de **"frequentes/recentes" no topo** e o
  restante acessível pela busca (padrão de editores/IDEs).
- **Interação:** abre → foca a busca → digita filtra → escolhe preenche o campo e fecha.
- **Risco:** médio. Reaproveita componente existente; o "relevante" é decisão de produto.

### 10. Ajustar o fluxo de criação das edições — Média · 🟡
- **Problema:** edições são criadas automaticamente durante a seleção (há sempre uma linha
  "em edição").
- **Estado atual:** `renderEditList()` (~742) **sempre** desenha uma linha `.el-row.draft`
  "em edição"; `addEdit()` (~736) empilha e abre outra. Ou seja, o rascunho é implícito.
- **Mudança:** fluxo explícito → **1) escolher origem · 2) escolher destino · 3) confirmar no
  botão "Adicionar edição"**. Só **após confirmar** a edição entra na lista. Sem linha
  "em edição" automática ocupando a lista.
- **Interação (decidido):** **origem obrigatória** habilita "Adicionar edição"; **destino vazio
  = remover o código** (mostra aviso "vai remover X" antes de incluir, para não errar). Ao
  confirmar, inclui na lista (feedback do item 11) e limpa os campos para a próxima.
- **Risco:** médio. Mexe na lógica central do compositor (`addEdit`/`renderEditList`/`draftEdit`).

### 11. Tornar a lista de edições dinâmica — Média · 🟡
- **Problema:** a área ocupa espaço mesmo vazia.
- **Estado atual:** `.editlist#editlist` (linhas ~516-519) é sempre visível, com título
  "Edições montadas (1)" mesmo sem itens reais (conta o rascunho).
- **Mudança:** **iniciar recolhida** (oculta ou minimizada quando vazia) e **expandir conforme
  itens entram**; **feedback visual de inclusão** (ex.: highlight rápido na linha recém-adicionada).
  Título reflete a contagem real (sem o rascunho do item 10).
- **Interação:** vazio = sem caixa (ou placeholder discreto); ao adicionar, a caixa surge/cresce
  com leve animação; cada inclusão pisca brevemente.
- **Risco:** médio. Acoplado ao item 10.

### 12. Estado inicial da Seção 3 (Resumo) — Média · 🔴
- **Problema:** o usuário não entende que ainda não há lotes/regras configurados.
- **Estado atual:** o Resumo já vem com 4 `.rcard` fixos + contadores `4/12/34` (linhas ~548-559);
  **não há estado vazio**.
- **Mudança:** **estado vazio** ("Nenhuma edição no lote ainda — monte edições na Seção 1 e
  adicione ao lote") + **mudar a aparência quando houver itens** (contadores zerados → preenchidos;
  selo/CTA só relevantes com itens).
- **Interação:** começa vazio; ao "Adicionar ao lote" (item 2) os cards aparecem e os contadores
  sobem; remover o último volta ao estado vazio.
- **Risco:** médio. Precisa de função de render do Resumo a partir dos dados (hoje é HTML estático).

### 13. "Perfis" → "Configurações salvas" (criar/salvar/reutilizar) — Média · 🔴
- **Problema:** botão não funciona; não cria novos perfis; o nome "Perfil" não representa a função.
- **Estado atual:** header tem o seletor `.profile .ctl` "Máquina 01 ▾" (linha ~490) e o botão
  `Salvar perfil` (~492) — ambos **sem ação**.
- **Mudança (decidido):** renomear para **"Configurações salvas"** (seletor) + **"Salvar
  configuração"** (botão); permitir **criar, salvar e reutilizar** configurações = **regras +
  preferências de salvamento** (pasta de backup, máquina ativa). O seletor lista as
  configurações salvas + "Nova…".
- **Interação:** abrir o seletor mostra configs salvas; "Salvar configuração" abre modal (nome +
  confirmar) que adiciona à lista (simulado, em memória do mockup).
- **Risco:** médio. Novo modal + estado em memória; sem persistência real.

### 14. Botões laterais (ações) da Seção 3 — Média · 🔴
- **Problema:** os botões de ação do resumo não funcionam.
- **Estado atual:** cada `.rcard` tem `.racts` com **✎ ⧉ 🗑** (linhas ~555-558) **sem handlers**.
- **Mudança:** torná-los funcionais (simulado) e no novo padrão visual (item 6):
  **🗑** remove o card (e recalcula contadores/estado vazio do item 12); **✎** devolve a edição
  ao compositor (Seção 1) para ajuste; **⧉** duplica o card.
- **Interação:** clicar age na hora, com feedback; mantém conflitos coerentes (`setConflict`).
- **Risco:** médio. Depende do item 12 (Resumo orientado a dados).

### 15. Feedback durante a execução do lote — Média/Alta · 🟡
- **Problema:** o usuário não sabe se o processo começou.
- **Estado atual:** `execLote()` (~811) já abre `ovRun` (spinner) → `ovRes`; **mas** não bloqueia
  o botão, não tem **barra de progresso** e permite re-clique.
- **Mudança:** **bloquear/desabilitar** "Executar Lote" durante a execução (evita múltiplos
  cliques); **pop-up de processamento** com **barra de progresso** (0→100% simulada) e passos;
  reabilitar ao fim.
- **Interação:** clique → botão vira "Processando…" desabilitado → modal com barra avança em
  etapas (timers) → resumo. Re-clique ignorado enquanto roda.
- **Risco:** médio. Em cima do fluxo existente; adicionar componente de barra + guarda de estado.

### 16. Lógica de salvamento do lote (com backup) — Alta · 🟡
- **Problema:** comportamento atual diverge do requisito (salvar fora da pasta original).
- **Estado atual (mockup):** overlays `ovRes`/`ovSave` falam em publicar em
  `\\servidor\cnc\trabalho\` (pasta da máquina) com backup (linhas ~640, ~816-823).
- **Mudança (decidido):** editados vão **para a pasta de cada arquivo** (de onde vieram);
  **backup numa pasta escolhida pelo usuário**, que fica **lembrada e fixa** (sempre a mesma)
  até ele trocar quando quiser — guardada nas "Configurações salvas" (item 13). O fluxo
  `ovRes`/`ovSave` e o selo (item 3) mostram isso e incluem um seletor "Pasta de backup: …
  [Mudar]". Mantém compatibilidade com "Editar Programas". *A lógica real é do app (etapa
  posterior); aqui é só a narrativa visual.*
- **Interação:** modal mostra etapas "Backup → grava na pasta original → conferência" e final
  "Concluído · originais no backup".
- **Risco:** no mockup, baixo (texto/fluxo). No app (depois), **alto** — é mudança de
  comportamento de gravação.

### 17. Inserir múltiplas linhas em posição específica — Muito alta · 🔴
- **Problema:** a funcionalidade não existe.
- **Estado atual:** o editor substitui código (localizar/substituir) e a biblioteca guarda
  **código + descrição** de 1 linha (`LIB`, ~828). Não há inserção de bloco multi-linha nem
  posicionamento por linha/ref.
- **Mudança (protótipo interativo):**
  - **Modelos multi-linha:** biblioteca passa a aceitar um "bloco" com várias linhas (novo campo;
    no modal do item 4).
  - **Inserção posicionada:** no editor, novo botão **"➕ Inserir bloco"** abre modal `ovInsert`
    com: textarea do bloco + escolha de **posição** — (a) **abaixo da linha Nº [campo]** ou
    (b) **abaixo do código [libdrop]** — + **prévia** do resultado.
  - **Processamento (simulado):** ao confirmar, o bloco é "inserido" no texto do editor (splice
    no `edInput`), só para demonstrar; sem gravar.
- **Interação:** abrir modal → digitar/escolher bloco → escolher posição → ver prévia → inserir;
  o editor mostra o resultado.
- **Risco:** no mockup, médio (novo modal + splice de texto). No app (depois), **muito alto**
  (nova lógica de processamento + biblioteca + casamento por linha/código).

---

## Ordem recomendada de implementação (sprints)
**Sprint 1 — UI rápida (1,2,3,4,5,6,7,8):** placeholders/seta; contador no botão; texto do selo;
mover "+ Adicionar código"; padronizar ✕ e botões; checkboxes desmarcados; lista em colunas.
**Sprint 2 — Usabilidade (9,10,11,12,13,14):** filtrar códigos; fluxo de adicionar edição;
lista de edições dinâmica; estado vazio da Seção 3; configurações salvas; ações do resumo.
**Sprint 3 — Fluxos críticos (15,16,17):** feedback de execução com barra; narrativa de
salvamento na pasta original + backup; inserção de bloco multi-linha.

Cada item será aplicado e validado abrindo o mockup no navegador (sem gerar `.exe`).

---

## Decisões tomadas (2026-06-09)
- **Item 8 — colunas:** 4 colunas **Nome | Data de modificação | Tipo | Tamanho** (Explorador), cabeçalho fixo, ✓ e ações como controles da linha; **sem ordenar por clique** por enquanto.
- **Item 9 — códigos relevantes:** **frequentes/recentes no topo** + resto na busca.
- **Item 10 — destino vazio:** **vazio = remover o código** (com aviso antes de incluir); origem obrigatória.
- **Itens 5/6 — botões:** excluir em listas = **botão ✕ único** (igual ao `.filex` da lista de programas), mesmo tamanho/estilo nas Seções 1/2/3; ✕ também fecha modais.
- **Item 13 — Perfis:** renomear para **"Configurações salvas"**; guarda **regras + preferências** (backup/máquina); criar/salvar/reutilizar.
- **Item 16 — salvamento:** editados na **pasta de cada arquivo**; **backup em pasta escolhida pelo usuário, lembrada/fixa e trocável** (guardada na configuração).
- **Variantes:** **remover** `painel-final.v2-with-combo-feedback.html` e `painel-final.v2-CODE-COMBO-UPDATED.html` (consolidar no v2).

---

## Resumo
| Dificuldade | Itens |
|---|---|
| Muito baixa | 1, 2, 3 |
| Baixa | 4, 5, 6, 7, 8 |
| Média | 9, 10, 11, 12, 13, 14 |
| Média/Alta | 15 |
| Alta | 16 |
| Muito alta | 17 |
