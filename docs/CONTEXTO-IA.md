# FlowNC — Documento Central de Contexto (para qualquer agente de IA)

> **Para que serve este documento:** entregue este arquivo a qualquer ferramenta/agente de IA
> (pesquisa, análise de mercado, copywriting, ideação de funções, UX, aprimoramentos em geral)
> como base única e suficiente sobre o produto. Ele reflete **exatamente o design aprovado**:
> o mockup `mockups/painel-final.v4.html` (aprovado pelo dono do projeto em 2026-06-11).
> Atualizado por último em: 2026-06-13.

---

## 1. O que é o FlowNC (resumo de 1 parágrafo)

O **FlowNC** é um aplicativo desktop para Windows que permite a operadores de máquinas CNC
**corrigir e padronizar códigos G/M em dezenas de programas NC de uma vez**, com segurança:
nada é gravado sem antes uma **conferência com números reais** ("o que vai mudar, onde, quantas
vezes"), toda publicação cria **backup automático versionado** e qualquer publicação pode ser
**restaurada com 1 clique**. Ele substitui o processo manual de abrir arquivo por arquivo no
bloco de notas — lento, repetitivo e sujeito a erro humano que pode quebrar ferramenta ou peça.

## 2. Público e problema

- **Usuário-alvo:** operador/programador de CNC em oficinas e usinagens (chão de fábrica),
  **não-técnico em informática**. Idioma do produto: **português do Brasil**.
- **Cenário típico:** a oficina troca um padrão (ex.: todo `M8` deve virar `M08`; todo programa
  precisa de um bloco de rotação depois do `G54`) e isso precisa ser aplicado em 10, 50, 200
  programas `.NC` espalhados numa pasta.
- **Dores que o produto ataca:**
  1. Editar em massa no "localizar e substituir" comum é perigoso: `M8` casa dentro de `M80`,
     `T1` dentro de `T1.0` — o FlowNC usa **borda CNC** (regra de fronteira que impede isso).
  2. Medo de gravar errado: o FlowNC **nunca grava no lote sem conferência prévia** e sempre
     guarda os originais em backup datado.
  3. Falta de rastro: o **Histórico** mostra cada publicação e permite **restaurar originais**.

## 3. Princípios de design (a "constituição" do produto)

Estes 5 princípios guiam toda decisão de interface (herdados do redesign v3 e mantidos no v4):

1. **Uma verdade por número** — nenhum contador estimado/inventado. Números só aparecem após
   varredura real dos arquivos. (No v4 isso foi reforçado: a contagem da conferência simula
   exatamente o mesmo encadeamento da publicação — número conferido = número gravado.)
2. **Um caminho, uma lista** — a edição montada cai direto no lote; não há estágios
   intermediários nem botões duplicados.
3. **Nome do botão = efeito do botão** — "Conferir lote" só confere (nada grava);
   "Publicar" grava com backup.
4. **Lugares, não modos** — navegação por 4 telas fixas (Lote · Editor · Códigos · Histórico)
   numa barra lateral, em vez de janelas/modos que se sobrepõem.
5. **Toda gravação tem volta** — backup versionado + "Restaurar originais" no Histórico;
   no editor (que salva direto, sem cópia), há "Desfazer" imediato após salvar.

## 4. Estrutura geral da interface (mockup v4)

```
┌──────┬──────────────────────────────────────────────────────┐
│ RAIL │ TOPO: FlowNC · [Configuração ▾] · backup: D:\..\ ·🛈  │
│ Lote ├──────────────────────────────────────────────────────┤
│ Edit │                                                      │
│ Cód. │                ÁREA DA TELA ATIVA                    │
│ Hist │                                                      │
└──────┴──────────────────────────────────────────────────────┘
```

- **Rail (barra lateral escura):** 4 botões-lugar — **Lote** (tela principal), **Editor**,
  **Códigos** (biblioteca), **Histórico**. O item ativo tem filete laranja; o item Editor
  ganha **bolinha laranja** quando há alteração não salva.
- **Topo (verdades globais, visível em todas as telas):**
  - **Seletor de configuração ("receita")** — um dropdown com configurações salvas
    (ex.: "Máquina 01"). Carregar uma receita preenche o lote inteiro de edições.
    O menu tem o item **"💾 Salvar lote atual como…"** (guarda lote + preferências com um nome).
    **Proteção:** carregar uma receita com lote já montado pede confirmação antes de substituir.
  - **Chip de backup** — mostra a pasta de backup atual (ex.: `D:\CNC\backup\`) o tempo todo;
    clicar troca a pasta.
- **Paleta visual:** "Precisão Laranja" — fundo claro acinzentado, painéis em cinza-azulado,
  topo/rail em azul-ardósia escuro, **laranja (#E85D04) como cor de ação principal (CTA)**,
  verde para sucesso/confirmação, âmbar para avisos, vermelho para perigo/remoção.
  Tipografia: **IBM Plex Sans** (interface) e **IBM Plex Mono** (códigos, nomes de arquivo,
  números) — fontes embutidas localmente, app 100% offline.

## 5. Tela LOTE (principal) — dinâmica completa

Duas colunas: **Programas** (esquerda) e **Lote de edições** (direita).

### 5.1 Painel Programas
- Lista de arquivos NC carregados, em linhas com: checkbox, nome (fonte mono), data de
  modificação, tamanho, botão **"✎ Abrir"** (abre o arquivo na tela Editor) e **✕** (remove da lista).
- **Marcar/desmarcar:** clique em qualquer ponto da linha alterna a marcação; linha marcada fica
  com fundo verde-claro e filete verde; desmarcada fica esmaecida. Botão **"Marcar todos /
  Desmarcar todos"** no cabeçalho. Chip mostra "N de M marcados".
- **Adicionar programas:** botão "+ Adicionar programa(s)…" ou **arrastar-e-soltar** arquivos
  na lista (a área ganha contorno tracejado ao arrastar por cima). Estado vazio tem ícone,
  texto-guia e botão grande de adicionar.

### 5.2 Compositor de edições (com abas — novidade do v4)
Um único compositor com **duas abas** e **um único botão "+ Adicionar ao lote"**:

- **Aba "Trocar código":** dois dropdowns pesquisáveis — **Código de origem** e **Trocar por**.
  - Os dropdowns abrem com campo de busca, seção **"★ Frequentes"** e a lista completa da
    biblioteca; mostram **só o código** (a descrição aparece em tooltip ao passar o mouse).
  - **Remover código:** no dropdown de destino existe a opção explícita
    **"✕ Remover (sem código)"** — escolhida, o botão de destino fica vermelho ("✕ remover").
  - **Proteção (v4):** o botão "+ Adicionar ao lote" só habilita com origem **e** destino
    escolhidos. Esquecer o destino **não** cai no fluxo de remoção (no passado, vazio = remover
    por padrão — perigoso). Não há modal de confirmação para remover: a escolha explícita +
    o cartão vermelho "→ remover" + a Conferência são as travas.
- **Aba "➕ Inserir bloco":** monta a inserção de um bloco de linhas em todos os programas
  marcados, **inline** (sem modal):
  - Textarea "Bloco a inserir (uma instrução por linha)";
  - **Posição em cada programa:** "Abaixo da 1ª ocorrência de [código ▾]" (recomendado) ou
    "Abaixo da linha Nº [n]" (com aviso de que a linha pode variar entre programas);
  - **Modelos salvos:** chips com blocos reutilizáveis vindos da biblioteca de códigos;
  - **Prévia real:** mostra o trecho exato do primeiro programa marcado que receberia o bloco,
    com as linhas novas destacadas (`+ ▶`).

### 5.3 Lote de edições (a lista única)
- Cada edição vira um **cartão numerado**: `M8 → M08`, `G54 → remover` (vermelho) ou
  `➕ bloco · 2 linhas após G54`.
- Ações por cartão: **✎ editar** (volta a edição para o compositor, na aba certa),
  **⧉ duplicar**, **✕ excluir**.
- **Conflito:** se duas edições alteram o mesmo código de origem, os cartões ficam âmbar com
  aviso "▲ Conflito" e o chip do painel mostra "⚠ N conflitos".
- Rodapé com o **CTA laranja grande**: **"Conferir lote →"** com subtítulo
  "varre os programas e mostra os números reais — nada é gravado".
  Desabilitado se não houver edições ou programas marcados (tooltip explica o que falta).

## 6. Conferência e Publicação — o coração do produto

### 6.1 Modal "Conferência do lote — números reais"
Abre ao clicar em "Conferir lote". Conteúdo, de cima para baixo:

1. **Resumo da decisão (v4):** faixa verde com **número grande** — total de alterações — e
   o texto "alterações em **X de Y** programas marcados · N trocas · bloco em M programas ·
   nada foi gravado ainda". Se total = 0, a faixa fica âmbar ("nenhuma alteração encontrada").
2. **Avisos:** conflitos ("▲ Conflito: M8 é alterado por mais de uma edição") e edições sem
   efeito ("⚠ M5 não aparece em nenhum programa marcado").
3. **Um cartão por edição:** fórmula no cabeçalho + total ("11 trocas em 4 programas"),
   lista **apenas dos programas afetados** com a contagem de cada um; os programas com zero
   ocorrência ficam **recolhidos numa única linha** ("+ 2 programas sem M8 — nada muda").
   Cada cartão de troca mostra um **exemplo real**: a linha original riscada → a linha nova,
   com arquivo e número da linha.
4. **Linha de backup:** "🛡 Ao publicar: originais vão para `D:\CNC\backup\` (versionado por
   data/hora) · gravação com conferência dupla", com botão para trocar a pasta.
5. **Rodapé fixo (não rola — v4):** repete o veredito. Sem problemas → botão laranja
   **"Publicar — 11 trocas · bloco em 4 programas"**. Com conflito → o aviso aparece no rodapé
   e o botão vira âmbar **"Publicar mesmo assim — …"**. Total 0 → botão desabilitado
   ("Nada a publicar").

**Honestidade da contagem (v4):** a varredura simula **exatamente o mesmo encadeamento** da
publicação (as edições rodam em sequência, por programa — uma troca anterior pode mudar a
âncora de um bloco posterior). O número que o operador confere é o número que será gravado.

### 6.2 Publicação
- Modal "Publicando…" com barra de progresso e etapas: **backup dos originais → gravação na
  pasta original → conferência dupla SHA-256**.
- Ao concluir: "Publicado ✓", resumo do que foi feito, caminho do backup criado, e botões
  **"Ver no Histórico"** e **"OK — novo lote"** (limpa o lote para a próxima tarefa).

## 7. Tela EDITOR — dinâmica completa

Para ajustes finos num arquivo individual. Duas áreas: **faixa de arquivos** (esquerda, estreita)
e o **editor** (restante da tela — linhas de NC são longas, o editor é tela cheia).

- **Faixa de arquivos:** todos os programas carregados; clicar troca o arquivo aberto sem sair
  da tela. Arquivo com alteração não salva ganha **bolinha laranja** (a mesma aparece no item
  "Editor" do rail). Trocar de arquivo com alteração pendente abre confirmação:
  **Cancelar / Descartar / Salvar e continuar**.
- **Cabeçalho do arquivo (v4):** "Editando `O1001_FLANGE.NC`" + aviso permanente
  **"⚠ salva direto, sem cópia"** + botões **"Salvar como…"** e **"Salvar"** (verde) à direita —
  salvar é decisão sobre o arquivo, por isso mora no cabeçalho, não na barra de ferramentas.
- **Toolbar em 3 grupos** (localizar · substituir · inserir):
  - **Localizar:** dropdown de código (mesma biblioteca pesquisável) + contador
    **"N encontrados"** + posição "i/N" + setas ↑ ↓ para navegar entre ocorrências
    (a atual fica com realce mais forte).
  - **Contagem automática (v4):** escolher o código, abrir o arquivo ou digitar **já reconta**
    as ocorrências — não existe botão de varredura nem estado "— encontrados" parado.
  - **Substituir:** "por [código ▾]" + **"Substituir todos"** + **"Um a um"** (abre barra
    inferior com "Ocorrência i/N — substituir M8 → M08?" e botões Substituir / Pular → / Concluir).
  - **➕ Inserir bloco:** modal com modelos salvos, textarea, posição (abaixo da linha Nº /
    abaixo da 1ª ocorrência de um código) e prévia do resultado.
    **Proteção (v4):** se o código-âncora não existe no arquivo, a prévia avisa
    ("não aparece neste arquivo — nada será inserido") e o botão fica bloqueado
    (antes inseria silenciosamente no fim do arquivo).
- **Área de edição:** numeração de linhas, fonte mono, realce amarelo das ocorrências.
- **Salvar:** grava direto na pasta de origem, sem cópia (decisão de produto, para não poluir
  as pastas das máquinas) — compensado por **toast com botão "Desfazer"** logo após salvar
  (1 clique restaura o conteúdo anterior).
- **"Salvar como…":** modal para salvar uma cópia escolhendo **extensão** (.nc/.txt/.tap/.iso/
  .min/.mpf), **codificação** (UTF-8, UTF-8 c/ BOM, ANSI) e **quebra de linha** (CRLF/LF),
  com prévia do resultado. O Salvar normal sempre **preserva** o formato original do arquivo.

## 8. Tela CÓDIGOS (biblioteca)

- Página (não modal) com a biblioteca de códigos: **código + descrição** (ex.: `M8 — Liga
  refrigeração`). Busca por código ou descrição; contador de cadastrados.
- **"+ Adicionar código":** código, descrição e — opcional — um **bloco de linhas**; com bloco,
  o código vira **modelo reutilizável** nos "Inserir bloco" (tela Lote e Editor), marcado com
  a tag "bloco" na lista.
- Os códigos alimentam **todos os dropdowns** do app (origem, destino, localizar, substituir,
  âncoras de bloco). No app real a biblioteca tem ~250 códigos.

## 9. Tela HISTÓRICO

- Uma linha por publicação: **quando**, resumo ("2 edições · 11 trocas em 5 programas"),
  caminho do **backup** criado e qual **configuração** estava ativa.
- Botão **"↩ Restaurar originais"** por linha: confirma e devolve os arquivos da publicação
  escolhida a partir do backup — e os arquivos atuais são preservados num **novo** backup antes
  da troca (restaurar também tem volta).

## 10. Comportamentos transversais de interação

- **Modais:** fecham com ✕, clique fora ou tecla **Esc** (exceto o modal de publicação em
  andamento, que não fecha). Botão primário à direita; perigo em âmbar/vermelho.
- **Dropdowns pesquisáveis:** abrem com a busca focada; clique fora fecha; seleção fecha.
- **Toasts (avisos passageiros):** confirmações curtas no rodapé ("Edição adicionada ao lote"),
  verde para sucesso, âmbar para alerta; podem carregar **um botão de ação** (ex.: "Desfazer").
- **Feedback de inclusão:** ao adicionar uma edição, o cartão novo pisca brevemente e a lista
  rola até ele.
- **Estados vazios:** toda lista vazia tem ícone + título + texto-guia + ação (nunca tela morta).
- **Responsividade:** janela fluida de ~1180 a 1800 px de largura; painéis com rolagem interna;
  abaixo de 1440 px os espaçamentos compactam.

## 11. Regras de negócio essenciais (para qualquer análise/ideação)

1. **Borda CNC:** um código só casa quando isolado — `M8` **não** casa em `M80`, `M81`, `T1.0`.
   É a regra de segurança nº 1 de qualquer substituição.
2. **Conferir ≠ Publicar:** conferir nunca grava; publicar sempre faz backup antes de gravar
   e verifica a gravação com soma de verificação (SHA-256) dupla.
3. **Edições rodam em cadeia, na ordem do lote** — e a conferência conta nessa mesma ordem.
4. **Remover = trocar por vazio**, sempre por escolha explícita; linhas que ficarem vazias após
   a remoção são apagadas.
5. **Lote** = lista de edições + programas marcados; **Configuração/receita** = lote + preferências
   salvos com nome para reutilizar (ex.: rotina mensal de padronização da "Máquina 03").
6. **Editor salva sem backup** (decisão consciente, com Desfazer); **o Lote nunca grava sem backup**.

## 12. Glossário rápido

| Termo | Significado |
|---|---|
| Programa NC | Arquivo de texto com instruções para máquina CNC (`.NC`, `.tap`, `.iso`…) |
| Código G/M | Instruções padrão CNC (`G54` origem de peça, `M8` liga refrigeração, `M30` fim) |
| Lote | Conjunto de edições a aplicar nos programas marcados |
| Edição | Uma troca de código (origem → destino/remover) **ou** uma inserção de bloco |
| Bloco | Grupo de linhas de instrução inserido numa posição ancorada |
| Conferir | Varredura real que mostra o que mudaria, sem gravar |
| Publicar | Gravar as edições com backup versionado e conferência dupla |
| Receita/Configuração | Lote + preferências salvos com nome, reutilizáveis |
| Borda CNC | Regra que impede `M8` de casar dentro de `M80`/`T1.0` |

## 13. Estado do projeto e stack (resumo técnico honesto)

- **Design:** mockup **v4 aprovado** (`mockups/painel-final.v4.html`) = **contrato visual**.
  É um HTML interativo autocontido (abre no navegador, offline) com anotações explicativas
  embutidas: ✦ azuis = mudanças do v4 · 🛈 laranja = decisões herdadas do v3 (botão "🛈
  Anotações" liga/desliga). A interatividade do mockup é real: a conferência varre arquivos
  de exemplo de verdade.
- **App:** Python 3.11+ / PySide6 (Qt), desktop Windows, com CLI auxiliar. O **núcleo está
  pronto e testado**: motor de substituição com borda CNC, contagem, publicação com backup
  versionado + SHA-256, gravação in-place preservando codificação/BOM/quebra de linha,
  biblioteca de códigos.
- **Interface v4:** **portada e aprovada pelo Mestre (Fase 2, 64/64 tarefas)** via change
  OpenSpec `plano-execucao-mockup-v4` — rail + 4 telas, compositor com abas, conferência com
  números reais, publicação com progresso, editor com contagem automática.
- **Distribuição:** **EXE portátil para Windows já gerado** (PyInstaller, onedir); sem
  instalador, sem internet. Próxima frente é a monetização/distribuição
  (ver `docs/MONETIZACAO.md` e `docs/PAGINA-DE-VENDAS.md`).

## 14. O que o FlowNC NÃO é (limites de escopo)

- Não é CAM/CAD: não gera nem simula trajetórias, não desenha peças.
- Não transmite programas para a máquina (sem DNC/rede industrial).
- Não interpreta a semântica completa do G-code: trabalha com **texto estruturado + borda CNC**.
- Não é multiusuário/nuvem: é local, offline, um operador por vez.

## 15. Direções já aventadas para evolução (insumo para ideação — não compromissos)

- Semear a biblioteca com códigos padrão Fanuc (e depois outros controles: Siemens, Haas…).
- Perfis por máquina/controle, com receitas associadas.
- Mais validações pré-publicação (ex.: detectar programas sem `M30`).
- Relatório/etiqueta de publicação para rastreabilidade da qualidade.
