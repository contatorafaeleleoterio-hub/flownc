# 09 — DESIGN DA INTERFACE (especificação visual)

**Projeto:** CNC Batch Editor — nova interface da dinâmica "por código".
**Status:** especificação visual extraída de mockup aprovado pelo Rafael (a implementar).
**Data:** 2026-06-03 · **atualizado 2026-06-04** (arranjo → **2 colunas**, ver §0)
**Fonte:** `Downloads\A _ Linha de Produ_o _ 3 colunas _substituir _ pronto_.html` (export de design, Claude artifact).
**Relação com docs anteriores:** é a **evolução em 3 colunas** do fluxo decidido no `08-WORKFLOW-NOVA-DINAMICA.md` e dos mockups `mockups\10`. O fluxo "por código" é preservado; o que mudou é a **arrumação espacial** (3 painéis sempre visíveis em vez de um passo de cada vez) e a **reintrodução da varredura** (contar ocorrências por arquivo — ver §7).

> **Leitura:** este documento descreve **como a tela é** (layout, cores, fontes, posições) e **o que cada ação faz** (lógica). O plano de implementação vive no `10-PLANO-EXECUCAO-3-COLUNAS.md`.

---

## 0. ⭐ LAYOUT FINAL (2026-06-04, "design B / Bancada") — substitui o arranjo de 3 colunas

Rafael revisou o arranjo: a tela passou de **3 colunas iguais** para **2 colunas**. Motivo: na versão de 3 colunas, a coluna 1 (compositor) sobrava muito espaço vazio. O novo arranjo resolve isso e dá **destaque ao resumo**.

```
┌──────────────────────────────────┬────────────────────┐
│  ESQUERDA  (~65% · ~836px)       │  DIREITA (~35%)    │
│  ┌────────────────────────────┐  │  ┌──────────────┐  │
│  │ ① COMPOSITOR — faixa BAIXA │  │  │ ③ RESUMO     │  │
│  │   controles na HORIZONTAL: │  │  │  dominante,  │  │
│  │   código·ação·trocar·config │  │  │  altura      │  │
│  ├────────────────────────────┤  │  │  INTEIRA     │  │
│  │ ② PROGRAMAS — bloco GRANDE │  │  │  (conflito   │  │
│  │   match + lista + add regra│  │  │  em destaque)│  │
│  └────────────────────────────┘  │  └──────────────┘  │
└──────────────────────────────────┴────────────────────┘
```

- **2 colunas** (não 3). Largura aprox. de 1340: **esquerda ~65%** (~836 px) · **direita ~35%** (~470 px).
- **Esquerda = 2 andares empilhados:** ① **Compositor** — faixa **baixa**, controles na **horizontal** (código de origem · ação · trocar por · configuração montada, lado a lado); ② **Programas** — bloco **grande**, pega o resto da altura (match-banner + lista + "Adicionar regra ao lote").
- **Direita = ③ Resumo dominante** — coluna única de **altura inteira**, com o **conflito em destaque**: chip "1 conflito", medidor "REVISAR" (âmbar), faixa de atenção, cartões de regra em conflito (amarelos com a explicação dentro). Rodapé: selo + **EXECUTAR LOTE**.
- **Conflito em dois sentidos** (vistos no design B): *"T1 também é alterado pela Regra 04"* (mesmo trecho) e *"mesmo código de origem da Regra 03"* (mesma origem).
- **Tudo o mais deste documento continua válido** — cores (§3), tipografia (§4), componentes (§5), textos (§6), lógica (§7). Mudou só a **disposição** das 3 zonas; o conteúdo de cada uma é o mesmo. As §1/§2 abaixo descrevem o arranjo **anterior** (3 colunas) — mantidas para histórico.
- **Mockup interativo fiel:** `mockups\12-mockup-bancada-resumo-dominante.html`. (`mockups\11` = versão 3 colunas, anterior.)

---

## 1. Visão geral

Tela única, estilo **painel de máquina industrial** (HMI). Os 3 passos do fluxo "por código" viram **3 colunas lado a lado, todas visíveis**, lendo da esquerda para a direita:

```
┌──────────────────────────── 1340 × 884 px ────────────────────────────┐
│  HEADER (aço escovado, 70px, "parafusos" nos cantos)                   │
│  [◉ CNC Batch Editor] │ [Perfil: Máquina 01 ▾]  [🔒Local·Offline][Biblioteca][+ Adicionar código] │
├────────────────────────────────────────────────────────────────────────┤
│  BODY (814px · 3 colunas · padding 14)                                  │
│  ┌── COL 1 (312) ──┐ ┌──── COL 2 (580, cresce) ────┐ ┌── COL 3 (392) ──┐ │
│  │ ① COMPOSITOR    │ │ ② SELEÇÃO DE PROGRAMAS      │ │ ③ RESUMO EM      │ │
│  │   DE REGRAS     │ │   [Adicionar programa(s)…]  │ │   TEMPO REAL  ✓  │ │
│  │ Código origem   │ │ ┌ match-banner (verde) ────┐│ │ ○ 3│12│28        │ │
│  │ [ M8  ▾ ]       │ │ │✓ 5/6 contêm M8…          ││ │  Reg Prog Alt    │ │
│  │ Ação            │ │ └──────────────────────────┘│ │ ── divisor ──    │ │
│  │ [Substituir|Ret]│ │ ☑ O1001_FLANGE.NC  ✓3 ocor. │ │ 01 M8→M08 ✓ 10p  │ │
│  │ Trocar por      │ │ ☑ O1002_EIXO…      ✓2       │ │    [✎ ⧉ 🗑]       │ │
│  │ [ M08 ▾ ]       │ │ ☑ O1003_TAMPA      ✓5       │ │ 02 G54→G55 ✓ 12p │ │
│  │ ┌ banner azul ─┐│ │ ☑ O1004_SUPORTE    ✓1       │ │ 03 T1→T01  ✓ 6p  │ │
│  │ │CONFIG MONTADA││ │ ☐ O1005_BUCHA_A    ▲0 ocor. │ │ ── selo ──       │ │
│  │ │ M8 → M08     ││ │ ☑ O1006_BUCHA_B    ✓2       │ │ 🛡 Originais      │ │
│  │ └──────────────┘│ │ ┌──────────────────────────┐│ │    intactos…     │ │
│  │                 │ │ │ Adicionar regra ao lote →││ │ ── CTA escuro ── │ │
│  │                 │ │ └──────────────────────────┘│ │ EXECUTAR LOTE    │ │
│  └─────────────────┘ └──────────────────────────────┘ └──────────────────┘│
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Layout e medidas

| Região | Tamanho (px) | Disposição |
|---|---|---|
| Card / tela | 1340 × 884 | coluna; fundo aço `#C2C9D1` |
| Header | 1340 × 70 | linha, centralizado, padding lateral 18; "parafusos" 7×7 nos cantos |
| Body | 1340 × 814 | linha, padding 14 |
| **Coluna 1** | 312 × 786 | painel fixo — Compositor de Regras |
| **Coluna 2** | 580 × 786 | painel central, **cresce** (flex-grow) — Seleção de Programas |
| **Coluna 3** | 392 × 786 | painel fixo — Resumo + Executar |

**Alvos de toque (chão de fábrica):** linhas de arquivo 50px · dropdowns/botões 42–46px · CTA 56px · linhas confortáveis.

---

## 3. Paleta de cores (tokens)

| Papel | RGB | HEX | Onde |
|---|---|---|---|
| Fundo da tela (aço) | 194,201,209 | `#C2C9D1` | chão de fábrica |
| Painel | 248,250,251 | `#F8FAFB` | as 3 colunas |
| Linha / cartão | 236,239,243 | `#ECEFF3` | linhas de arquivo, cartões de regra |
| Trilho de controle | 225,230,236 | `#E1E6EC` | segmentado, badges de zona |
| Texto principal | 27,33,40 | `#1B2128` | grafite escuro |
| Texto secundário | 86,97,109 | `#56616D` | labels |
| Texto terciário | 137,144,153 | `#899099` | metadados, tags |
| **Azul (info/ação)** | 31,95,158 | `#1F5F9E` | setas `→`, banner "config montada" |
| Azul (fundo banner) | 228,238,247 | `#E4EEF7` | banner "configuração montada" |
| **Verde (OK) texto** | 28,138,77 | `#1C8A4D` | chips ✓, selo, medidor |
| Verde (fundo chip) | 225,241,232 | `#E1F1E8` | chip-ok, match-banner |
| **Âmbar (atenção) texto** | 168,106,7 | `#A86A07` | chip `▲ 0 ocorrências` |
| Âmbar (fundo chip) | 250,238,213 | `#FAEED5` | chip-warn |
| Divisor | 205,212,219 | `#CDD4DB` | linhas separadoras |
| CTA escuro (texto) | 244,247,250 | `#F4F7FA` | botão Executar (texto quase branco, MAIÚSCULO) |

> **Regra "cor nunca sozinha":** todo chip de cor vem com ícone + texto (✓ verde / ▲ âmbar / 🔒 vermelho). Daltonismo + tela suja.

---

## 4. Tipografia

- **UI:** `IBM Plex Sans`, system-ui, sans-serif.
- **Códigos:** `IBM Plex Mono`, ui-monospace, monospace.

| Elemento | Tamanho | Peso | Estilo |
|---|---|---|---|
| Label de campo | 10.5px | 700 | MAIÚSCULA, espaçamento 1.3px |
| Título de zona (1/2/3) | 12px | 700 | MAIÚSCULA, espaçamento 1.4px |
| Marca | 15px | 600 | — |
| Submarca ("EDITOR DE LOTES") | 9.5px | 400 | MAIÚSCULA, espaçamento 2px |
| Código na pílula (banner) | 20px mono | 600 | — |
| Código no dropdown | 16px mono | 600 | — |
| Código no cartão de regra | 15px mono | 600 | — |
| Contadores do resumo | 22px mono | 700 | — |
| Chip | 11.5px | 600 | ícone + texto |
| CTA "Executar lote" | 16px | 600 | MAIÚSCULA |

---

## 5. Componentes-assinatura (o que dá o "ar" industrial)

- **Painel "metal repuxado":** sombra `branco 0 1px 0 inset` (brilho no topo) + 2 sombras suaves embaixo (`rgba(20,28,38,.1) 0 1px 2px` e `rgba(20,28,38,.05) 0 2px 6px`). Repetida em todo bloco elevado (painéis, botões, chips, pílulas).
- **Header escovado** com "parafusos" 7×7 nos cantos (decorativo) — cara de painel de máquina.
- **Chip = ícone + texto sempre** (`✓`/`▲`/`🔒`). Verde = ok, âmbar = atenção, vermelho = bloqueio.
- **Controle segmentado** (Substituir | Retirar): trilho `#E1E6EC`, botão ativo "saltado" (branco + sombra).
- **Pílula de código** (banner) e **badges mono** (`1` `2` `3` das zonas; `01` `02` das regras).
- **Medidor circular** (donut) no resumo, com check verde no centro quando "Pronto".
- **CTA escuro** (grafite, MAIÚSCULO, com subtítulo "Pré-visualizar e gravar") — o ato de gravar é separado e destacado.

---

## 6. Inventário por zona (posições e textos)

### Header (esquerda → direita)
1. **Marca:** ícone redondo 38×38 + `CNC Batch Editor` (15/600) / `EDITOR DE LOTES` (9.5 maiúsc.).
2. Divisor vertical 1px.
3. **Perfil de máquina:** label `PERFIL DE MÁQUINA` + controle 42h → `Máquina 01` / `Centro de usinagem · 247 códigos na biblioteca` + caret ▾.
4. (empurra à direita) **Selo** 156×42: ícone verde + `Local · Offline` / `Zero dados enviados`.
5. Botão fantasma **`Biblioteca de Códigos`** (197×42).
6. Botão azul **`Adicionar código`** (165×42).

### Coluna 1 — Compositor de Regras (zona "1")
1. Label `CÓDIGO DE ORIGEM` + dropdown 280×46: `M8` (mono) · `Liga refrigeração` (tag) · ▾.
2. Label `AÇÃO` + segmentado 280×52: **`[Substituir]`** (ativo) | `[Retirar]`.
3. Label `TROCAR POR` + dropdown 280×46: `M08` (mono) · `Forma normalizada` (tag) · ▾.
4. **Banner azul** 280×87 `CONFIGURAÇÃO MONTADA`: pílula `M8` → (seta azul) → pílula `M08`.

### Coluna 2 — Seleção de Programas (zona "2")
1. Cabeçalho: `2 · SELEÇÃO DE PROGRAMAS` + botão fantasma `Adicionar programa(s)…` (190×34).
2. **Match-banner** (verde) 548×49: `✓ Regra em edição` · `5/6` (mono) · `programas contêm M8 — receberão esta regra.`
3. **Lista de arquivos** (linhas 548×50, fundo `#ECEFF3`):
   - `☑/☐` checkbox 20×20 (marcado = verde com ✓ branco; desmarcado = `.off` vazio) + nome (mono 13.5) + `tamanho · data` (11 muted) + (empurra à direita) **chip de ocorrências**.
   - Exemplos: `O1001_FLANGE.NC ✓3` · `O1002_EIXO_REV2.NC ✓2` · `O1003_TAMPA.NC ✓5` · `O1004_SUPORTE.NC ✓1` · `O1005_BUCHA_A.NC ▲0` (desmarcado) · `O1006_BUCHA_B.NC ✓2`.
4. Botão azul largo 548×50: **`Adicionar regra ao lote →`**.

### Coluna 3 — Resumo em Tempo Real (zona "3")
1. Cabeçalho: `3 · RESUMO EM TEMPO REAL` + chip `✓ Pronto`.
2. **Medidor** circular 78×78 (✓ verde / `PRONTO`) + 3 contadores: `3 Regras` · `12 Programas` · `28 Alterações`.
3. Divisor.
4. **Cartões de regra** 360×61 (fundo `#ECEFF3`): `idx 01` + fórmula mono `M8 → M08` + escopo `10 programas` + chip `✓ Validado` + ações `✎` (editar) `⧉` (duplicar) `🗑` (excluir, vermelho).
   - Cartões exemplo: `01 M8→M08 · 10 prog` · `02 G54→G55 · 12 prog` · `03 T1→T01 · 6 prog`.
5. **Selo** 360×72: disco verde 🛡 + `Originais intactos` / `Gravação em pasta nova: …\_processado_Máquina01_data\`.
6. **CTA escuro** 360×56: `EXECUTAR LOTE` / `Pré-visualizar e gravar`.

---

## 7. Lógica de execução (o que cada ação dispara)

| Gatilho | Efeito |
|---|---|
| Escolher **código de origem** (`M8`) | atualiza o banner "config montada"; **recalcula as ocorrências de `M8` por arquivo** na lista da col 2 (ver §8) |
| Alternar **Substituir / Retirar** | *Substituir* mostra "Trocar por"; *Retirar* **esconde** "Trocar por" e mostra a trava (1 código por execução, allowlist) |
| Escolher **trocar por** (`M08`) | puxa a **variação normalizada da biblioteca** (M8→M08 do perfil) |
| **Adicionar programa(s)…** | popula a lista; cada arquivo ganha chip `✓ N ocorrências` (verde) ou `▲ 0` (âmbar) |
| Arquivo com **0 ocorrências** | chip âmbar **e checkbox desmarcado** (não recebe a regra) |
| **Adicionar regra ao lote →** | cria cartão na col 3; soma contadores (regras / programas / alterações); **reseta** a col 2 para a próxima regra |
| `✎` / `⧉` / `🗑` no cartão | editar / duplicar / excluir regra |
| Duas regras no mesmo código | **aviso de conflito** (âmbar) no resumo |
| **Executar lote** | porteiro: pré-visualiza → grava em pasta nova (`_processado_PERFIL_data\`) → conferência SHA-256 → abre a pasta |

**Invariantes herdadas (inegociáveis):** original nunca alterado · gravação em pasta nova com data · conferência SHA-256 · log. (motor `core/` estável — 106 testes)

---

## 8. ⚠ Decisão em aberto: VARREDURA prévia

Este modelo mostra **`5/6 programas contêm M8`** e **`N ocorrências` por arquivo**. Isso exige **ler e contar** cada programa assim que o código é escolhido (varredura prévia).

No `08`/handoff ficou registrado o **contrário**: *"Sem varredura de códigos nos programas (rejeitado por complexidade)."* Portanto este design **reabre essa decisão**. Tecnicamente é viável (`core/matcher.find_matches` já conta); o custo é ler todos os arquivos ao escolher o código. Para lotes típicos (≤50) roda rápido e síncrono; lotes grandes pedem processamento em segundo plano (QThread).

**→ Esta decisão é do Rafael e está registrada no `10-PLANO-EXECUCAO-3-COLUNAS.md`.**

---

## 9. Diferenças vs. mockups anteriores

- vs. `mockups\10` (fluxo "por código", passo a passo): mesmo fluxo, mas em **3 colunas simultâneas** + resumo/Executar **sempre visíveis** à direita.
- **Novo:** varredura prévia (contagem por arquivo) — ver §8.
- **Mantido:** fluxo por código, Substituir/Retirar, biblioteca com variações, selo "originais intactos", pré-visualizar antes de gravar.
