# Estudo de Dimensionamento e Responsividade — FlowNC

status: **estratégia decidida (2026-06-08) — pronta para aplicar no protótipo** · largura máx. **1800px** · piso **1280×768**
escopo: contrato visual de tamanho/adaptação da interface (FASE 1 — entra no protótipo antes de virar código)

> 📌 **Nota (2026-06-13):** este estudo foi feito sobre o protótipo v2, mas a estratégia
> (largura fluida ~1180–1800px, rolagem interna nos painéis, compactação abaixo de 1440px) já
> está **incorporada ao mockup v4** (`mockups/painel-final.v4.html`) — o contrato visual vigente.
> As referências a `painel-final.v2.html` abaixo são históricas; valem para o v4.

> ⛳ **REGRA DE OURO.** Nada disto vira código antes de aprovado e refletido no protótipo vigente (`mockups/painel-final.v4.html`). Este documento é o estudo pedido: largura mínima/máxima, grade, espaçamento e estratégia de adaptação — para decisão.

---

## 1. Problema atual (o que está errado hoje)

A interface é uma **carta de largura fixa: `--dim-screen: 1340px`**, centralizada na tela, e **não tem nenhuma regra de adaptação** (`@media`) — conferido no `mockups/painel-final.v2.html` (linha 127 e `body`/`.screen` nas linhas 139–159).

Consequências:
- **Sobra grande nas laterais.** Num monitor de 1920px de largura (o mais comum), a carta ocupa 1340px e deixa **~580px vazios** (≈30% da tela) — exatamente as faixas vermelhas da captura.
- **Só encolhe, nunca cresce.** A regra `max-width:100%` faz a carta diminuir em telas estreitas, mas em telas largas ela **trava em 1340px** e não aproveita o espaço.
- **Altura não se adapta.** A altura é "puxada" pelo conteúdo. Num monitor de 768px de altura (19"/notebook), a tela pode **passar do limite e exigir rolagem vertical**.
- **Sem padrão entre resoluções.** Como não há pontos de adaptação, o layout pode espremer controles ou cortar conteúdo em telas fora do "ponto ideal".

*(Termos: `@media` = regra de CSS que muda o layout conforme o tamanho da tela; "px" = pixel, a unidade de medida da tela.)*

---

## 2. Dados de referência (resoluções reais de desktop — 2025)

Participação mundial de resoluções em **desktop** (Statcounter / Statista, 2024–2025):

| Resolução      | Participação | Observação |
|----------------|--------------|------------|
| **1920×1080**  | ~19–23%      | A mais comum. Nosso **alvo principal**. |
| **1536×864**   | ~8%          | É um monitor 1080p com **zoom de 125%** do Windows (muito comum em notebook). |
| **1366×768**   | ~7–14%       | Notebooks/monitores básicos e 19" econômicos. **Piso de largura.** |
| **1440×900**   | ~3–7%        | 19"/20" widescreen (16:10). |
| **2560×1440**  | ~3–8%        | Monitores grandes, em crescimento. |
| **3840×2160**  | ~3–4%        | 4K. |
| **1280×1024**  | pequena      | 19" antigo (formato 5:4) — largura 1280, mas **bastante altura**. |

**Leitura para o FlowNC:** os operadores usam **19" (faixa 1280–1366 de largura, 768–1024 de altura)** — esse é o **piso** que não pode quebrar. A máquina onde o sistema é montado/usado para configurar aparenta ser **1920×1080** — o **alvo** a otimizar. Telas muito grandes (2560/4K) são minoria, mas o visual não pode "esticar feio" nelas.

---

## 3. Resoluções de referência adotadas (matriz de projeto e teste)

| Papel | Resolução | O que garantir |
|-------|-----------|----------------|
| **Piso (não pode quebrar)** | **1280×768** (cobre 1280×1024, 1366×768 e o efetivo 1536×864) | Nada cortado, sem rolagem horizontal, rolagem vertical só dentro das listas. |
| **Alvo (otimizar)** | **1920×1080** | Aproveitar a largura (margens mínimas), tudo visível sem rolar. |
| **Teto (não esticar feio)** | **2560×1440 e 3840×2160** | Conteúdo limitado a uma largura confortável; margem sobrando é **intencional** (leitura), não desperdício. |

Altura útil real no piso ≈ **700px** (768 menos a barra de tarefas do Windows). É a restrição mais apertada — guia a estratégia de altura abaixo.

---

## 4. Estratégia recomendada

### 4.1 Largura — fluida, com limites (mínimo e máximo)
- Trocar a largura fixa `--dim-screen:1340px` por **largura fluida `100%` com trava**:
  - **`--app-min: 1180px`** (largura mínima do conteúdo; abaixo disto a interface fica genuinamente apertada).
  - **`--app-max: 1800px`** (largura máxima do conteúdo).
- Pequena **folga lateral** (gutter) de ~16–24px para a carta não colar na borda.

Efeito por tela:
- **1366px** → preenche ~1330px (margem some, sem cortar nada).
- **1920px** → cresce até **1800px**, deixando só **~60px de cada lado** (cheio e equilibrado — fim das faixas vazias).
- **2560/4K** → trava em 1800px e centraliza. A margem que sobra é **proposital**: esticar um formulário de 2 colunas para 2560px deixaria os controles largos demais e cansativos de ler.

> 🔧 **Botão de ajuste:** se o Mestre usar principalmente um monitor grande (2560/4K), subimos o `--app-max` (ex.: 2000–2100px) para aproveitar mais. Para 1920, **1800px é o ponto de equilíbrio**.

### 4.2 Altura — ocupar a tela e **eliminar a rolagem da página**
- A interface passa a **preencher a altura da janela** (cabeçalho fixo no topo, corpo ocupando o resto), em vez de "vazar" para baixo.
- A rolagem, quando necessária, acontece **dentro dos painéis** (a lista de "Programas" e o "Resumo"), **nunca na página inteira**. Os botões grandes (`Executar Lote`, `Adicionar edição ao lote →`) ficam **sempre visíveis**, fixos na base de cada coluna.
- Resultado no piso (altura ~700px): o cabeçalho, os títulos e os botões cabem; só a **lista longa rola internamente** (comportamento esperado e familiar). Nada é cortado nem sai da tela.

### 4.3 Grade (as 2 colunas)
- Mantém a proporção dinâmica **60/40 ↔ 40/60** (Configurações+Programas à esquerda / Resumo ou Editor à direita).
- Cada coluna recebe uma **largura mínima** para nunca ser espremida ou cortada no piso:
  - esquerda: **mín. ~620px**; direita: **mín. ~420px** (somando folgas, cabe em 1280px).

### 4.4 Espaçamento
- Espaçamentos (`--sp-*`) **levemente menores** em telas ≤1440px (ganha área útil) e **confortáveis** em ≥1920px — via faixas (breakpoints) abaixo, mantendo os mesmos tokens em todo o sistema (consistência).

### 4.5 Pontos de adaptação (breakpoints) — só 3, para consistência
| Faixa | Largura | Comportamento |
|-------|---------|---------------|
| **Compacto** | ≤ 1440px | Paddings/gaps menores; colunas no mínimo confortável. |
| **Padrão** | 1441–1800px | Layout pleno; cresce com a tela. |
| **Cap** | > 1800px | Trava em `--app-max` e centraliza. |
| **Piso rígido** | < 1280px | Mantém `--app-min`; só aqui se aceita rolagem horizontal (não ocorre em janela maximizada). |

---

## 5. Como cada exigência do Mestre é atendida

| Exigência | Como é garantida |
|-----------|------------------|
| Aproveitar **largura e altura** | Largura fluida até 1800px + altura preenchendo a janela (4.1, 4.2). |
| Sem **áreas vazias** grandes | Margem de ~60px em 1920; no piso, preenche quase tudo (4.1). |
| Componentes **não cortados** | Larguras mínimas por coluna + rolagem interna, não corte (4.2, 4.3). |
| Componentes **não ultrapassam a tela** | Largura/altura presas ao tamanho da janela (4.1, 4.2). |
| Layout **não quebra** entre resoluções | 3 breakpoints definidos e testados na matriz do item 3 (4.5). |
| Sem **rolagem horizontal** | `--app-min` ≤ piso de 1280; conteúdo nunca mais largo que a janela. |
| **Rolagem vertical** minimizada | Página não rola; só a lista interna rola quando há muitos itens (4.2). |
| Visual **eficiente e harmônico** | Largura confortável de leitura + folga proposital em telas enormes (4.1). |

---

## 6. Caminho de implementação (depois de aprovado)

1. **Protótipo primeiro (FASE 1):** aplicar esta estratégia no `mockups/painel-final.v2.html` (trocar `--dim-screen` fixo pelos limites `--app-min`/`--app-max`, altura preenchendo a viewport, rolagem interna nos painéis, 3 `@media`). Conferir nas 4 resoluções da matriz. **Reaprovação do Mestre.**
2. **Código depois (FASE 2):** no PySide6, o equivalente é: janela com `minimumSize ≈ 1180×720`, layouts que expandem (size policies), `QScrollArea` **só** na lista de programas e no resumo, e o DPI/zoom do Windows tratado pelo Qt (high-DPI). Sem largura fixa.

---

## 7. Decisões do Mestre (2026-06-08)

1. **Largura máxima = 1800px** (confirmado — "não sei/varia" → padrão seguro de 1366 a 1920, sem esticar feio em telas maiores).
2. **Piso = 1280×768** (confirmado — operadores em 19" comum, faixa 1280–1366).
3. **Estratégia decidida.** Pronta para ser aplicada ao protótipo `mockups/painel-final.v2.html` (passo 6.1), com reconferência visual nas 4 resoluções da matriz (item 3) antes da reaprovação final.
