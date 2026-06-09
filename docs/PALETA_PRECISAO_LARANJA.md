# Paleta "Precisão Laranja" — FlowNC

**Fonte da verdade de cores do FlowNC.** Aplicada ao mockup `mockups/painel-final.v2.html`
e a ser portada ao app na fase de implementação. Filosofia: fundo slate azulado sóbrio
(seriedade técnica) + um laranja industrial de alto contraste **reservado exclusivamente**
para a ação executável de maior impacto por tela. O laranja nunca é decoração.

---

## Tokens de cor (referência)

### Principais
| Token | Hex | Uso |
|---|---|---|
| `--color-bg` | `#F7F9FC` | Fundo geral da janela / canvas |
| `--color-surface` | `#FFFFFF` | Superfície de cards e painéis internos |
| `--color-header` | `#2B3A4A` | Cabeçalho da aplicação e barra lateral |

### Seções e bordas
| Token | Hex | Uso |
|---|---|---|
| `--color-panel-left` | `#EDF0F5` | Painel de configurações (esquerda) |
| `--color-panel-right` | `#E5EAF2` | Painel de resumo/status (direita) |
| `--color-border` | `#CCD4E0` | Divisores entre seções e bordas de card |
| `--color-border-input` | `#B8C6D6` | Borda de campos de entrada |

### Texto
| Token | Hex | Uso |
|---|---|---|
| `--color-text-primary` | `#1A2533` | Texto principal, rótulos, títulos |
| `--color-text-secondary` | `#4E6278` | Suporte, subtítulos, metadados |
| `--color-text-muted` | `#8FA5C2` | Placeholders, desabilitado, dicas |
| `--color-text-on-dark` / `on-orange` | `#FFFFFF` | Texto sobre header / botão laranja |

### Botões
| Token | Hex | Uso |
|---|---|---|
| `--color-btn-secondary-bg` | `#DDE3EE` | Fundo do botão secundário |
| `--color-btn-secondary-border` | `#C0CEDF` | Borda do secundário |
| `--color-btn-secondary-text` | `#2B3A4A` | Rótulo do secundário |
| `--color-btn-outline-border` | `#8FA5C2` | Borda outline/terciário |
| `--color-btn-ghost-text` | `#4E6278` | Texto de ação sem fundo (ghost) |
| `--color-btn-disabled-bg` | `#EEF1F5` | Fundo desabilitado |
| `--color-btn-disabled-text` | `#B0BFD0` | Texto desabilitado |

### Destaque (ações principais)
| Token | Hex | Uso |
|---|---|---|
| `--color-btn-primary-bg` | `#E85D04` | CTA principal ("Executar Lote") |
| `--color-btn-primary-hover` | `#C94E00` | Hover do CTA laranja |
| `--color-btn-primary-active` | `#A83E00` | Pressionado |
| `--color-btn-dark-bg` | `#2B3A4A` | Ação relevante nível 2 ("Biblioteca de Códigos") |
| `--color-btn-dark-hover` | `#1F2C39` | Hover do slate |

### Tags de status (badges)
| Status | Fundo | Texto | Borda |
|---|---|---|---|
| Em edição / ativo | `#FFF3ED` | `#E85D04` | `#F0A87A` |
| Publicado / confirmado | `#EAF5EA` | `#2D6B2D` | `#8FC98F` |
| Alerta / atenção | `#FFF8E1` | `#A16207` | `#D4A840` |
| Erro / falha | `#FEECEB` | `#D93025` | `#F0948D` |

### Outros
- **Scrollbar:** track `#EDF0F5`, thumb `#CCD4E0`, hover `#B8C6D6`, 6px arredondado.
- **Tooltip:** fundo `#2B3A4A`, texto `#FFFFFF`, 11–12px, raio 4px.
- **Divisores:** seções `#CCD4E0`; entre itens de lista `#E5EAF2`. Nunca borda > 1px.

---

## Hierarquia de ação (Regra de Ouro)
1. **Laranja `#E85D04`** → única ação executável de alto impacto por tela. Ex.: "Executar Lote".
2. **Slate `#2B3A4A`** → ações relevantes, não destrutivas. Ex.: "Adicionar código".
3. **Cinza `#DDE3EE`** → auxiliares/configuração. Ex.: "Salvar configuração".
4. **Outline / Ghost** → opcionais ou cancelamento.
5. **Desabilitado `#EEF1F5` / `#B0BFD0`** → indisponível no contexto.

O laranja **nunca** em ícones decorativos, bordas de seção ou texto de instrução.

---

## Como foi aplicado no mockup (painel-final.v2.html)
O mockup já é 100% por tokens no `:root`; os **nomes** dos tokens foram mantidos e os
**valores** trocados pela paleta acima, recolorindo tudo de forma consistente:
- `--color-cta-*` → **laranja** (faz o "Executar Lote" ser o único laranja da tela), com hover/active.
- `--color-interactive*` (antes azul) → **slate** (nível 2 / acento); o azul foi eliminado.
- `--color-head-*` → **slate sólido** (header e cabeçalho dos modais), texto branco.
- Painéis: `.left .panel` → `#EDF0F5`; `.right .panel` → `#E5EAF2`; cards brancos.
- Badge "em edição" (`.el-row.draft` / `.el-tag`) → tom **laranja**; sucesso/aviso/erro nos novos tons.
- Scrollbar fina e anel de foco em **slate** (corrigido azul remanescente).

**Ressalva (slate sobre header escuro):** botões slate sumiriam no header slate. Por isso
"+ Adicionar código" usa um slate mais claro (`--color-slate-2:#3A4F63`) **enquanto estiver no
header**. Quando o item 4 mover esse botão para a Seção 1 (painel claro), ele volta ao slate padrão.

**Pendente de cor:** a hierarquia fina dos botões (cinza nível-3 × slate nível-2 × outline) será
finalizada no **item 6** (padronizar botões). Hoje o que era azul virou slate como base.

---

## Polimento visual aplicado (sutil — sem mexer em layout/fluxo/contraste)
- **Raios** mais fechados e consistentes: cards `6px`, controles `4px`, miúdos `2px`
  (círculos do logo/spinner/selo preservados).
- **Tags** antes "pílula" (status, "✓ Validado", "em edição", "salva direto") → **retangulares**.
- **Menos brilho glossy:** realce branco do relevo (`--metal`) reduzido; sombras de janela/modal
  mais sóbrias; brilho do topo do header atenuado.
- **Emojis decorativos → glifos neutros:** 🛡/✅ → ✓; removidos 💾/📤 dos botões "Salvar"/"Publicar".
- **Botão ✕ de excluir padronizado** (igual ao `.filex` da lista de programas) nas 3 seções.
