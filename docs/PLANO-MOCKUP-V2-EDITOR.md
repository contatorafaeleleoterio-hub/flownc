# Plano — Mockup v2 do FlowNC: refino visual + Editor integrado

> Criado em: 2026-06-05
> Status: **CONCLUÍDO — mockup `mockups/painel-final.v2.html` construído e aprovado por Rafael (2026-06-05). Editor portado para OpenSpec na mudança `editor-integrado-por-arquivo` (proposta+validada) → falta `/opsx:apply`.**
> Evolui o `docs/PLANO-DESIGN-SYSTEM.md`: além de padronizar, adiciona a feature do Editor integrado.
> Próxima sessão: `/opsx:apply` do editor (ou da mudança pendente `motor-retirar-contagem-e-publicacao`).

---

## Contexto

O painel FlowNC (editor de lotes de G-code) já tem layout 2 colunas e funcionalidades aprovados, com folha
de tokens (IBM Carbon + IBM Plex) pronta em `mockups/PROMPT-CLAUDE-DESIGN.md`. Rafael pediu para REFINAR:
além de padronizar o visual, decidir o que fica/sai/muda e — principalmente — **acrescentar uma funcionalidade
nova**: um **editor de arquivo integrado** ao painel, eliminando a necessidade de abrir o `.NC` pelo Windows.

Esta fase entrega um **mockup HTML para aprovação** (`mockups/painel-final.v2.html`); a implementação real no
app Qt é etapa futura (OpenSpec). Método de referência: skill `design-system` (motor IBM Carbon, validado) +
heurísticas de usabilidade (Nielsen).

## Travado (não rediscutir)

- Layout base 2 colunas, hierarquia dos blocos, fluxo de Lote (Compositor → selecionar programas → Executar → backup → publicar).
- Tokens de espaçamento/tipografia/cor/componentes do `PROMPT-CLAUDE-DESIGN.md`.
- Só mexer no mockup HTML; cópia `v2`; original `painel-final.html` intacto; sem screenshot sem "sim".

## Decisões confirmadas (3 rodadas de perguntas)

### Refino visual
1. Padronizar **+ enxugar** (limpar redundância, manter 100% das funções).
2. Conflito: manter **selo "⚠ 1 conflito"** no topo + **destaque âmbar no cartão**; REMOVER a faixa âmbar solta (o cartão já explica o conflito).
3. Cabeçalho: **remover a linha de subtítulo inteira** ("Centro de usinagem · 247 códigos…"); manter logo+"EDITOR DE LOTES", seletor de máquina, status e botões.
4. **Sem varredura/contagem automática** no painel: remover os chips "✓ N ocorr." e o banner "5/6 contêm M8". A contagem vira função sob demanda DENTRO do editor.

### Layout das colunas (dinâmico)
5. Sem editor aberto: **~60% esquerda / ~40% direita**. Ao abrir o editor, a direita expande para **~60%** e a esquerda encolhe (transição suave). Resumo e editor nunca ocupam a tela ao mesmo tempo.

### Editor integrado por arquivo (FEATURE NOVA)
6. Cada arquivo na lista ganha um **botão "Editar"** (à direita, onde estava o chip). Checkbox de seleção em lote continua à esquerda.
7. Clicar "Editar" **substitui o Resumo** pela área do editor na coluna direita; botão **"✕ Voltar ao resumo"** retorna.
8. Editor = **texto simples estilo Bloco de Notas**, com numeração de linha, edição direta em tempo real (fonte IBM Plex Mono).
9. **Salvar = sobrescreve o original na pasta de origem, SEM backup** (proposital). Mostrar aviso discreto "salva direto, sem cópia". Botão Salvar desabilitado quando não há alteração.
10. Trocar para "Editar" de outro arquivo troca a visualização na hora; se houver alteração não salva, **pop-up "salvar antes de trocar?"**.
11. Editor e fluxo de **Lote convivem**: Lote (com backup, para vários arquivos) + editor (sem backup, ajuste manual rápido).

### Localizador/Verificação no cabeçalho do editor (UI = melhores práticas, delegada por Rafael)
12. Barra de ferramentas do editor, da esquerda p/ direita:
    - **Dropdown "Código da biblioteca"** (lista pesquisável dos 247 códigos) — escolhe o código a procurar.
    - Botão **Varredura** (lupa) — procura no arquivo aberto **sem mover o cursor**.
    - **Contador inline** "N encontrados" + indicador de posição "1/N".
    - Setas **↑ / ↓** (anterior/próximo) que navegam até a ocorrência só quando clicadas (= o "ir até").
    - Bloco **Substituir em massa**: dropdown "Substituir por" (biblioteca) + **"Substituir todos"** e **"Um a um"** (passo a passo com confirmação).
    - Botão **Salvar**.
13. Caso de uso central atendido: ver "N encontrados" sem descer no arquivo; só navega se quiser.

### Texto/limpeza
14. Banner verde "Regra em edição" perde o número: vira "Regra em edição — marque os programas que vão receber esta regra."
15. Subtexto do CTA corrigido para "Pré-visualizar antes de publicar".
16. Aplicar todos os tokens do `PROMPT-CLAUDE-DESIGN.md` (zero inline style, zero cor/valor fora do `:root`).

### Ajustes finais confirmados
17. Remover o bloco destacado em vermelho no topo do painel.
18. No topo, remover o texto acima do dropdown de máquina, deixando apenas o seletor "Máquina 01" e adicionando o botão "Salvar perfil" ao lado.
19. Na sessão 1, trocar o título "Compositor de regras" por "Configurações" e adicionar o botão "+ Adicionar edição".
20. Na sessão 3, trocar "Resumo em tempo real" por "Resumo".
21. Remover o indicador circular da sessão 3 para reduzir poluição visual.

## Arquivos

| Ação | Arquivo |
|------|---------|
| Lê | `mockups/painel-final.html` (estado atual) e `mockups/PROMPT-CLAUDE-DESIGN.md` (tokens) |
| Cria | `mockups/painel-final.v2.html` ← novo; original preservado |
| Não toca | `flownc/` (app Qt), `core/`, `.qss`, OpenSpec |

## Implementação do mockup (após aprovação)

1. Copiar a estrutura do `painel-final.html` e refatorar o CSS para um único `:root` com os tokens aprovados (+ 3 tokens novos: gutter de linha, realce de ocorrência, ocorrência atual).
2. Aplicar refinos 1–4, 14–16 (enxugar conflito/cabeçalho/contagem, normalizar espaços/raios/fontes).
3. Tornar as colunas dinâmicas (refino 5) e adicionar botão "Editar" por linha (refino 6).
4. Construir o **painel do editor** na coluna direita (refinos 7–13) com JS: alternância Resumo↔Editor, pop-up de salvar-ao-trocar, localizador (dropdown+varredura+contador+setas) e substituir em massa (todos/um a um) — funcionando em modo demonstração sobre um arquivo de exemplo.
5. Manter a barra demo (navegação dos estados do mockup) e a interatividade JS existente.

## Verificação

- Abrir `painel-final.v2.html` no navegador e comparar lado a lado com `painel-final.html`.
- Checklist funcional: confirmar que as 25 funções originais seguem presentes + as novas do editor operam (abrir/voltar, trocar com aviso, localizar+contador+navegar, substituir todos/um a um, salvar).
- Conferir: sem contagem automática, sem faixa de conflito redundante, cabeçalho sem subtítulo, espaços só na escala de tokens, colunas expandindo ao editar.

## Fora de escopo (futuro)

- Portar tokens + editor para o app Qt (`flownc/ui/`) → mudança(s) OpenSpec.
- Resolver formalmente a tensão "editor salva sem backup × Lote salva com backup" na spec do app.
