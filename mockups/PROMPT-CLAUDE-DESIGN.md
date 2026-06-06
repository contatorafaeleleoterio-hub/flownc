# Prompt para Claude Design — FlowNC Painel v2

> **Como usar:** Abra claude.ai/design → cole este texto no campo de prompt → anexe o screenshot do `painel-final.html` aberto no navegador como imagem de referência → envie.

---

## Contexto do projeto

Estou refinando o mockup HTML de um painel de software industrial chamado **FlowNC** — um editor de lotes de código G-code para máquinas CNC. O painel já tem layout e funcionalidades aprovados. O que precisa é de **padronização visual**: tirar os desalinhamentos, espaçamentos inconsistentes e redundâncias — sem perder nenhuma funcionalidade.

A imagem que estou enviando junto é o **estado atual** do painel (`painel-final.html`). Preciso que você produza um **arquivo HTML standalone** com o mesmo layout 2 colunas, as mesmas funcionalidades, porém com o design system padronizado descrito abaixo.

---

## Layout aprovado (não mudar estrutura)

Layout 2 colunas dentro de uma janela de aplicativo (1340px):

- **Coluna esquerda (~65%)** — empilhados verticalmente:
  - ① **Compositor de Regras** — faixa horizontal com: dropdown "Código de origem", toggle Substituir/Retirar, dropdown "Trocar por" (condicional), banner de configuração montada, aviso de trava (modo Retirar)
  - ② **Seleção de Programas** — bloco grande com lista de arquivos, banner de ocorrências, botões de ação, botão "Adicionar regra ao lote"

- **Coluna direita (~35%, 470px fixo)** — altura inteira:
  - ③ **Resumo em Tempo Real** — gauge circular, contadores, aviso de conflito, lista de cartões de regra (com editar/duplicar/excluir e destaque de conflito), bloco de destino/backup, botão "Executar Lote"

- **Header** — logo FlowNC, dropdown de perfil de máquina, status "Local · Offline", botões de biblioteca

- **Overlays/modais** — processando, resumo com pré-visualização de linhas, publicação concluída

---

## Diagnóstico do estado atual (Etapa 1 — problemas a corrigir)

### Inline styles no HTML (eliminar, mover para CSS)
- `style="display:flex;gap:8px"` no cabeçalho da seção Programas
- `style="margin:0"` no título dentro desse mesmo cabeçalho

### Espaçamentos fora de escala (normalizar para a grade abaixo)
- gap 7px → usar 8px
- gap/padding 9px → usar 8px
- gap/padding 11px → usar 12px
- padding 13px → usar 12px
- gap 18px (body e comp-row) → usar 16px
- padding header 18px → usar 16px

### Border-radius fragmentado (10 valores distintos → reduzir para 4)
- Valores atuais: 4, 5, 6, 7, 8, 9, 10, 11, 14, 20px
- Manter apenas: 4px (badge inline), 8px (componentes interativos), 12px (painéis/modais), 20px (chips de estado)

### Tipografia caótica (18 tamanhos → reduzir para escala de 11 tokens)
- Eliminar: 9.5px, 10.5px, 11px, 11.5px, 12.5px, 13.5px, 14.5px, 17px
- Usar apenas a escala tipográfica definida abaixo

### Alturas de botão sem hierarquia (5 valores → 3)
- `.ghost` 34px → 32px
- `.hbtn`, `.mbtn`, `.addrule` → todos 44px
- `.cta` → 56px

### Classes duplicadas
- `.lab` e `.field-lab` são visualmente idênticos → unificar em uma única classe

### Peso 800 desnecessário
- `.chk` usa font-weight:800 → mudar para 700

### Cores hardcoded fora das variáveis CSS (mover para tokens)
- `#e7ebee` (footer do modal), `#eef1f4` (fundo de code inline), `#fcf2f2` (linha deletada), `#e6eaee` (borda de linha no resumo), `#f0f2f5` (borda pvrow), `#efd6d6` / `#8a2a2a` (tag de linha apagada)

### Subtexto do botão CTA confuso
- Atual: "Pré-visualizar e publicar" → corrigir para: "Pré-visualizar antes de publicar"

---

## Design System a aplicar (Etapa 2 — tokens aprovados)

### Espaçamento — grade única (IBM Carbon 2×)
Usar **exclusivamente** estes valores para padding, margin e gap:

| Token | Valor |
|-------|-------|
| `--sp-2` | 2px |
| `--sp-4` | 4px |
| `--sp-8` | 8px |
| `--sp-12` | 12px |
| `--sp-16` | 16px |
| `--sp-24` | 24px |
| `--sp-32` | 32px |
| `--sp-40` | 40px |
| `--sp-48` | 48px |

### Tipografia — IBM Plex Sans (interface) + IBM Plex Mono (código)

| Token | Fonte | Size | Weight | Line-height | Uso |
|-------|-------|------|--------|-------------|-----|
| `--t-label` | Sans | 10px | 700 | 1.4 | Labels uppercase de campo, contador legenda |
| `--t-caption` | Sans | 12px | 600 | 1.4 | Chips, badges, botões ghost, paths |
| `--t-ui` | Sans | 13px | 600 | 1 | Controles (toggle, hbtn) |
| `--t-body` | Sans | 14px | 400 | 1.5 | Corpo padrão |
| `--t-body-strong` | Sans | 14px | 600 | 1.5 | Texto de ação/resultado |
| `--t-heading` | Sans | 15px | 700 | 1.2 | Títulos de modal, brand name |
| `--t-display` | Sans | 16px | 600 | 1 | CTA button, fórmula de regra |
| `--t-mono-sm` | Mono | 12px | 600 | 1.4 | Paths de backup, notas |
| `--t-mono-md` | Mono | 14px | 600 | 1 | Nomes de arquivo (.fname) |
| `--t-mono-lg` | Mono | 16px | 600 | 1 | Pill, fórmula de regra |
| `--t-mono-display` | Mono | 24px | 700 | 1 | Contadores grandes |

### Cor — tokens nomeados

```
/* Fundos em camadas */
--color-bg-base:    #F8FAFB   (painéis internos)
--color-bg-subtle:  #ECEFF3   (linhas de lista, rows)
--color-bg-rail:    #E1E6EC   (trilhos, toggle inativo)
--color-bg-surface: #C2C9D1   (fundo da tela/header)

/* Texto */
--color-text-primary:   #1B2128
--color-text-secondary: #56616D
--color-text-tertiary:  #899099

/* Bordas */
--color-border:       #CDD4DB
--color-border-strong:#aeb6bf

/* Interativo (azul) */
--color-interactive:    #1F5F9E
--color-interactive-hv: #2B76C0
--color-interactive-bg: #E4EEF7

/* Sucesso (verde) */
--color-success:    #1C8A4D
--color-success-bg: #E1F1E8

/* Aviso (âmbar) */
--color-warning:    #A86A07
--color-warning-bg: #FAEED5

/* Perigo/erro (vermelho) */
--color-danger:     #BB3324
--color-danger-bg:  #FAE4E1
--color-danger-deep:#8a2a2a

/* CTA (botão principal escuro) */
--color-cta-start: #3A434E
--color-cta-end:   #232A33
--color-cta-text:  #F4F7FA

/* Utilitários */
--color-overlay:     rgba(15,20,25,.55)
--color-code-bg:     #eef1f4
--color-row-deleted: #fcf2f2
--color-modal-footer:#e7ebee
```

### Componentes — regras fixas

| Componente | Token | Valor |
|-----------|-------|-------|
| Border-radius — badge/code inline | `--radius-xs` | 4px |
| Border-radius — botões, campos, cards | `--radius-sm` | 8px |
| Border-radius — painéis, modais | `--radius-md` | 12px |
| Border-radius — chips de estado | `--radius-pill` | 20px |
| Altura — botão primário (CTA) | `--h-cta` | 56px |
| Altura — botão padrão | `--h-btn` | 44px |
| Altura — botão ghost/secundário | `--h-ghost` | 32px |
| Altura — campos (drop, toggle) | `--h-field` | 44px |
| Espessura de borda | `--border-width` | 1px |
| Anel de foco | `--focus-ring` | 0 0 0 3px rgba(31,95,158,.35) |
| Barra de conflito no cartão | `--conflict-bar` | inset 3px 0 0 var(--color-warning) |

---

## Mapa — cada problema → token que resolve

| Problema | Correção |
|---------|---------|
| inline `gap:8px` no HTML | mover para CSS com `gap: var(--sp-8)` |
| inline `margin:0` no HTML | mover para CSS com regra de escopo |
| espaçamentos 7/9/11/13px | → `--sp-8` ou `--sp-12` |
| espaçamentos 18px | → `--sp-16` |
| 10 border-radius distintos | → 4 tokens `--radius-*` |
| 18 tamanhos de fonte | → 11 tokens `--t-*` |
| peso 800 no chk | → 700 |
| 5 alturas de botão | → 3 tokens `--h-*` |
| `.lab` e `.field-lab` duplicados | → unificar em `.label-caps` |
| 14+ cores hardcoded | → `--color-*` tokens |
| subtexto CTA confuso | → "Pré-visualizar antes de publicar" |
| `align-items:flex-end` no .comp-row | → `align-items:flex-start` |

---

## Funcionalidades obrigatórias (todas devem continuar funcionando)

1. Dropdown de código de origem (clicável, cicla entre M8/M6/G54/T1)
2. Toggle Substituir / Retirar (segmented control)
3. Dropdown "Trocar por" (some no modo Retirar)
4. Aviso de trava Retirar (aparece no modo Retirar)
5. Banner de configuração montada (azul=substituir, vermelho=retirar)
6. Botão "varredura" (anima os chips para loading e restaura)
7. Botão "Adicionar programa(s)…"
8. Banner de contagem de ocorrências (estados: substituir, retirar, scan)
9. Lista de arquivos com checkbox, nome, metadados e chip de ocorrências
10. Botão "Adicionar regra ao lote →" (com estado disabled durante scan)
11. Chip de estado global (✓ Pronto / ⚠ conflito) no painel Resumo
12. Gauge SVG circular (muda cor e ícone conforme estado)
13. Contadores: Regras / Programas / Alterações
14. Banner de aviso de conflito (âmbar, ocultável)
15. Lista de cartões de regra com editar (✎), duplicar (⧉), excluir (🗑)
16. Destaque de conflito nos cartões (borda âmbar + texto de aviso)
17. Bloco de destino/backup (seal-big) com ícone + caminho
18. Botão "Executar Lote" (abre modal)
19. Modal de resumo com pré-visualização de linhas (substituir/retirar/linha apagada)
20. Botão "Publicar na máquina" dentro do modal
21. Modal de progresso (processando) e modal de publicação concluída
22. Dropdown de perfil de máquina no header
23. Status "Local · Offline" no header
24. Botões "Biblioteca de Códigos" e "+ Adicionar código" no header
25. Barra de demonstração (5 botões de estado + hint) — manter para navegação do mockup

---

## O que entregar

Um **arquivo HTML standalone** (`painel-final.v2.html`) com:

1. Um único bloco `<style>` no `<head>` contendo um `:root {}` com **todos os tokens** listados acima como variáveis CSS
2. Todas as regras de estilo usando os tokens (zero valores hardcoded fora do `:root`)
3. Zero inline styles no HTML — tudo no CSS
4. Todos os 25 itens funcionais acima preservados e operáveis
5. JavaScript interativo mantido (os botões da barra demo devem funcionar)
6. Fonte IBM Plex Sans e IBM Plex Mono carregadas via Google Fonts (igual ao original)

**Não mudar:** estrutura de 2 colunas, hierarquia dos blocos, lógica JavaScript, conteúdo textual dos elementos (exceto o subtexto do CTA corrigido).

---

## Referência visual

A imagem anexada mostra o estado atual do painel no navegador. Use como referência de layout — o objetivo é manter o mesmo visual geral, apenas mais limpo, alinhado e consistente.
