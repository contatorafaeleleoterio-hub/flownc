# 06 — ANÁLISE DE UX / WORKFLOW — CNC Batch Editor

> **Origem deste documento:** o [05-PLANO-UI-UX.md](05-PLANO-UI-UX.md) §4 estava
> aguardando o Rafael devolver a análise do workflow atual com correções/incômodos.
> O Rafael devolveu essa análise (os 12 problemas abaixo). Este arquivo é a **resposta
> técnica fundamentada no código real** (`ui/main_window.py`, `ui/preview_dialog.py`,
> `ui/library_dialog.py`) + a proposta consolidada do redesenho.
>
> **Data:** 2026-06-02
> **Status:** relatório documentado. Visualização criada em `mockups\06-mockup-ux.html`
> (anotado) e `mockups\06-prototipo-navegavel.html` (clicável). A decisão de **tela única vs
> wizard** será confirmada pela pesquisa do `07-PROMPT-PESQUISA-UI.md` antes de implementar.
> O sistema atual já foi **entregue verificado** (pacote portátil; 106 testes verdes; EXE
> abre). **Nada de código do app foi alterado.**

---

## 0. Restrições que governam toda recomendação (do próprio projeto)

- **Não tocar no `core/`** — só `ui/` + `main.py` + QSS ([05-PLANO §3](05-PLANO-UI-UX.md)).
  O motor é seguro: 106 testes verdes.
- **Ferramenta de chão de fábrica:** sóbria, legível, operacional — **não** o visual
  "bold/maximalista" que skills web sugerem ([05-PLANO §2](05-PLANO-UI-UX.md)).
- **Sistema é síncrono** (threading é Fase 8, ⬜ não feita — [STATUS.md](cnc_batch_editor/STATUS.md)).
  Isso limita o que "barra de progresso real" pode ser hoje.
- **Princípios diretores:** ambiente industrial, operadores técnicos, uso repetitivo,
  segurança operacional, redução de erro humano, velocidade, baixa curva de aprendizado,
  compatibilidade com o existente, mínimo retrabalho, máximo ganho de usabilidade.

---

## 1. Estado atual do sistema (o que o código realmente faz)

Mapeamento fiel da interface, com referências ao código:

- **Janela única** `QMainWindow` 1180×720 ([main_window.py:125-142](cnc_batch_editor/ui/main_window.py)).
- **Barra superior** ([main_window.py:149-177](cnc_batch_editor/ui/main_window.py)):
  `Perfil ▾` + botões **Novo / Duplicar / Renomear / Excluir** + `addSpacing(12)` +
  **Abrir pasta… / Abrir programa(s)…** + rótulo de origem. Todos `QPushButton` padrão,
  mesmo peso visual.
- **Linha Destino** ([main_window.py:179-198](cnc_batch_editor/ui/main_window.py)):
  rádio `Ao lado dos originais` / `Pasta fixa:` + `QLineEdit` readonly + `Escolher…`.
- **`QTabWidget` com 2 abas** ([main_window.py:200-203](cnc_batch_editor/ui/main_window.py)):
  "Substituições" e "Verificações" — **separadas**.
- **Aba Substituições** ([main_window.py:208-275](cnc_batch_editor/ui/main_window.py)):
  `QSplitter` [ esquerda: lista de PROGRAMAS com checkbox | direita: tabela **Trocas COMUNS**
  + botões (`+ troca comum` / `- remover` / `+ da lista`) ; tabela **Trocas SÓ DESTE**
  + botões (`+ troca só deste` / `- remover` / `+ da lista` / `Gerenciar codigos…` / `Salvar perfil`) ;
  botão **Executar substituições (preview)** + `addStretch` ].
- **Aba Verificações** ([main_window.py:277-307](cnc_batch_editor/ui/main_window.py)):
  tabela (Aplicar/Tipo/Codigo/Valor/Obs) + `Executar verificações` + área de texto de resultado.
- **As duas tabelas de troca são idênticas** — mesma função `_make_subs_table`
  ([main_window.py:310-319](cnc_batch_editor/ui/main_window.py)).
- **PreviewDialog** ([preview_dialog.py](cnc_batch_editor/ui/preview_dialog.py)):
  lista lateral (RESUMO + cada programa colorido por severidade) + painel de detalhe +
  **Confirmar e salvar** (desabilita se houver erro crítico) / **Cancelar**.
- **Salvar** ([main_window.py:654-710](cnc_batch_editor/ui/main_window.py)): grava em pasta
  nova `_processado_PERFIL_data`, faz **conferência SHA-256** relendo os arquivos, gera log,
  e mostra `QMessageBox` final com contagem + `[INTEGRIDADE OK]`.
- **Cores de severidade** verde/amarelo/vermelho já existem no domínio
  ([main_window.py:84-86](cnc_batch_editor/ui/main_window.py)).
- **Sem barras de progresso** em lugar nenhum — tudo síncrono.

---

## 2. Avaliação crítica de cada problema (concordo / discordo / ajusto)

### Problema 1 — Verificações fora do fluxo principal — **CONCORDO, com correção técnica**

Existem **duas** classes de verificação, e não são a mesma coisa:

- **Estruturais** (automáticas, `run_structural`) — **já estão no fluxo** e **bloqueiam o
  salvar** (vermelho). [main_window.py:548,563](cnc_batch_editor/ui/main_window.py). Correto.
- **Configuráveis** (aba Verificações: "Deve existir", "Não pode existir", etc.) — são um
  relatório **paralelo e opcional**, não gatilham aprovação.
  [main_window.py:713-737](cnc_batch_editor/ui/main_window.py).

A percepção do Rafael vale para as **configuráveis**.

**Pegadinha técnica importante:** hoje elas rodam sobre o **arquivo original**
(`read_file(p)` na [linha 726](cnc_batch_editor/ui/main_window.py)), **não** sobre o
**resultado** das trocas. Se viram "porteiro final antes de salvar", precisam rodar sobre o
**resultado processado** — senão validam o texto errado. Integrar é certo, mas é uma
**mudança de semântica deliberada**, não só mover botão. Risco baixo: `run_configurable` já
existe; é fiação na UI, **sem mexer no core**.

Fluxo proposto pelo Rafael: `Perfil → Programas → Substituições → Preview → Verificações →
Salvar`. **Aceito**, com a verificação rodando dentro do preview, sobre o resultado.

### Problema 2 — Ausência de hierarquia visual — **CONCORDO totalmente**

Todos são `QPushButton` no estilo padrão, mesmo peso
([main_window.py:155-173](cnc_batch_editor/ui/main_window.py)). Novo/Duplicar/Renomear/
Excluir/Abrir têm o mesmo destaque que a ação que faz o trabalho. Único agrupamento: um
`addSpacing(12)` ([linha 167](cnc_batch_editor/ui/main_window.py)). Resolvível 100% por
QSS + `objectName`, **sem lógica**.

### Problema 3 — Botão principal escondido — **CONCORDO**

"Executar substituições (preview)" fica embaixo à esquerda do painel direito, estilo padrão,
com `addStretch` **depois** dele ([main_window.py:265-270](cnc_batch_editor/ui/main_window.py)).
É a ação central e não se distingue de "- remover". O nome atrapalha: "(preview)" entre
parênteses esconde que **este é o passo que avança o processo**.

### Problema 4 — Ausência de feedback de progresso — **CONCORDO, com limite técnico**

Não há nenhuma barra. Como tudo é síncrono, em lotes grandes a janela **congela** sem sinal.
**Mas:** progresso *real* (barra que anda) exige threading (Fase 8). Hoje dá pra entregar
barato: cursor "ocupado" + status "Processando N de M…" com `processEvents`. Barra threaded
fica para depois. **Honestidade:** não prometer barra real sem o trabalho de thread.

### Problema 5 — Ausência de feedback de conclusão — **DISCORDO PARCIALMENTE**

O **salvar já tem bom feedback**: `QMessageBox` "Salvo" com contagem + caminho +
`[INTEGRIDADE OK]` (confere SHA-256 relendo os arquivos)
([main_window.py:700-710](cnc_batch_editor/ui/main_window.py)). Isso é melhor que a maioria
dos apps. O que **falta** é feedback nos **passos intermediários** (executar trocas,
verificações) e confirmação **visual inline** em vez de só modal. **Ajuste do problema:** não
é "ausência", é "feedback concentrado só no fim e sempre em pop-up".

### Problema 6 — Trocas comuns vs específicas confundem — **CONCORDO**

Duas `QTableWidget` **idênticas** (mesma função `_make_subs_table`,
[linha 310](cnc_batch_editor/ui/main_window.py)) empilhadas; a diferença vive só no texto do
rótulo. Visualmente gêmeas → exige leitura atenta, exatamente como o Rafael disse.

### Problema 7 — Biblioteca com baixa descoberta — **CONCORDO**

"+ da lista" é críptico (o próprio Rafael citou "da lista" como confuso) e "Gerenciar
codigos…" está perdido no canto ([main_window.py:234,253](cnc_batch_editor/ui/main_window.py)).
A palavra "biblioteca" nem aparece nos botões.

### Problema 8 — Lista de programas subaproveita espaço — **CONCORDO, com cautela**

Mostra só nome + check ([main_window.py:473-477](cnc_batch_editor/ui/main_window.py)). Dá pra
enriquecer, **mas** contagem de trocas/alertas só é conhecida **após** executar (vem do
`build_plan`). Solução sem recomputar caro: **colorir e anotar a lista depois do preview**
(verde/amarelo/vermelho + "N trocas"). Antes de executar, no máximo info estática. **Não
inventar números** que o sistema ainda não tem.

### Problema 9 — Destino pouco explícito — **CONCORDO PARCIALMENTE**

A linha já tem rádio + caminho + "Escolher"
([main_window.py:179-197](cnc_batch_editor/ui/main_window.py)). O buraco real: no modo "Ao
lado dos originais" o operador **não vê onde** vai cair (é calculado:
`_processado_PERFIL_data` na pasta de origem). Falta **mostrar o caminho final resolvido**. O
`QLineEdit` fica readonly mas não claramente desabilitado nesse modo.

### Problema 10 — Ausência de visão geral do lote — **CONCORDO**

Só existe "N programa(s)" no rótulo ([linha 469](cnc_batch_editor/ui/main_window.py)). Um
painel-resumo agrega. Cautela igual ao item 8: pré-execução só dá pra mostrar
total/marcados/trocas configuradas; válidos/alertas/erros só pós-preview.

### Problema 11 — Preview e verificações fragmentados — **CONCORDO** (é o item 1 pelo outro lado)

O `PreviewDialog` já reúne: alterações + conflitos + alertas + checklist
([preview_dialog.py](cnc_batch_editor/ui/preview_dialog.py)). **Só falta a seção de
verificações configuráveis.** Unificar = adicionar uma seção no preview + deixar verificação
reprovada desabilitar "Confirmar". Reaproveita o diálogo existente; **risco baixo**.

### Problema 12 — Indicador global de progresso (stepper) — **DISCORDO da forma proposta**

Um **wizard de 6 passos que obriga navegação** brigaria com o ponto forte atual: tela única
que o operador experiente usa repetidamente, rápido. Para uso repetitivo de produção, wizard
forçado **atrasa o expert**. Além disso, os 6 passos propostos misturam configuração
(Perfil/Programas/Substituições) com ações (Revisão/Verificações/Concluir).

**Contraproposta:** uma **faixa de etapas passiva** (não-bloqueante) no topo, que **destaca
onde você está** mas não trava navegação — orienta o iniciante sem frear o experiente. E
**fundir** Revisão+Verificações (item 11): `Perfil → Programas → Trocas → Revisar &
Verificar → Salvar` (5 passos).

---

## 3. Melhorias adicionais (não citadas pelo Rafael)

| # | Achado | Por quê importa |
|---|--------|-----------------|
| A | **Risco de perda de dados no perfil.** Editar trocas e trocar de perfil/fechar **descarta tudo** sem aviso — só persiste em "Salvar perfil" ([main_window.py:740](cnc_batch_editor/ui/main_window.py)). | Operador perde configuração silenciosamente. Precisa de indicador "perfil modificado *" + aviso ao sair. **Alto valor.** |
| B | **Sem atalhos de teclado.** Nenhum F5/Ctrl+S/Del. | Uso repetitivo de produção pede teclado. Ganho grande, custo baixo. |
| C | **Verificações rodam no ORIGINAL, não no resultado** ([linha 726](cnc_batch_editor/ui/main_window.py)). | Já citado no item 1 — é também um achado independente: hoje a verificação configurável não vê o efeito das trocas. |
| D | **Sinalização só por cor** (verde/amarelo/vermelho). | Chão de fábrica tem operadores com daltonismo/visão cansada. Adicionar **ícone + palavra** junto da cor. Acessibilidade. |
| E | **Fricção invertida.** Excluir perfil tem **dupla** confirmação ([linhas 867-880](cnc_batch_editor/ui/main_window.py)) embora já faça backup; salvar trocas não tem proteção nenhuma. | Equilibrar: um confirm bom basta para excluir; proteger o que realmente perde dado (item A). |
| F | **Restrição "mesma pasta" só aparece ao executar** ([linha 587](cnc_batch_editor/ui/main_window.py)). | Operador descobre tarde. Sinalizar ao carregar. |
| G | **Sem estado vazio orientado.** App abre "(nenhum perfil)" + lista vazia sem dizer o que fazer. | Iniciante fica perdido — bate na dor nº1 do plano ("não sei por onde começar"). |

---

## 4. Novo workflow recomendado

O fluxo **lógico** atual está correto; o problema é **apresentação e o ponto da
verificação**. Recomendado:

```
1. PERFIL        → escolhe a máquina (trocas pré-carregam)
2. PROGRAMAS     → abre pasta/arquivos + define DESTINO (com caminho final visível)
3. TROCAS        → comuns (todos) + extras (só do selecionado)
4. REVISAR & VERIFICAR  → 1 tela: alterações + verificações + conflitos + alertas
                          (verificação reprovada de bloqueio = trava "Confirmar")
5. SALVAR        → grava + conferência SHA-256 + log + confirmação
```

**Mudança-chave:** verificações configuráveis entram **dentro do passo 4** (rodando sobre o
resultado), virando porteiro de aprovação — não uma aba paralela. A aba Verificações
**permanece** como ferramenta avulsa "avançada" para quem quer só checar sem trocar nada
(compatibilidade preservada).

---

## 5. Novo layout recomendado (mantém janela única e o `QSplitter`)

```
┌───────────────────────────────────────────────────────────────┐
│  [① Perfil] → [② Programas] → [③ Trocas] → [④ Revisar] → [⑤ Salvar]   ← faixa passiva
├───────────────────────────────────────────────────────────────┤
│ Perfil: [MAZAK ▾]  ·perfil modificado*·   | Códigos ▸ Gerenciar │  ← grupo config
│ Programas: [Abrir pasta] [Abrir arquivos]   12 carregados       │
│ Destino:  (•)Ao lado  ( )Pasta fixa [____]   → cairá em: ...\_processado_MAZAK_… │
├───────────── RESUMO DO LOTE: 12 prog · 10 marcados · 3 trocas · — alertas ──────┤
│ PROGRAMAS            │  TROCAS PARA TODOS OS PROGRAMAS                          │
│ ☑ O2169  ●2 trocas   │  [tabela comum]      [+ troca] [+ da biblioteca] [−]     │
│ ☑ O2170  ●ok         │ ───────────────────────────────────────────────────────│
│ ☑ O2171  ▲0 trocas   │  TROCAS EXTRAS — só de O2169                             │
│ ☐ O2172              │  [tabela específica] [+ troca] [+ da biblioteca] [−]     │
│                      │                                                         │
│                      │              ┌───────────────────────────────┐         │
│                      │              │  REVISAR ALTERAÇÕES  →         │ ← primária│
│                      │              └───────────────────────────────┘         │
└───────────────────────────────────────────────────────────────┘
   status: pronto.                                          [Salvar perfil]
```

- **Faixa de etapas** = `QHBoxLayout` de `QLabel`s; a atual em negrito/cor. **Não
  navega/bloqueia** — só informa.
- **Resumo do lote** = tira fina, preenche números pós-preview.
- Duas tabelas **visualmente distintas** (faixa de cor/título forte/recuo), não gêmeas.

---

## 6. Hierarquia visual recomendada (via QSS + `objectName`, zero lógica)

| Nível | Botões | Estilo |
|-------|--------|--------|
| **Primário** (avança o processo) | Revisar alterações → / Confirmar e salvar | Fundo de cor (verde sóbrio), negrito, padding maior, maior |
| **Secundário** (ação de apoio) | Abrir pasta/arquivos, + troca, + da biblioteca, Salvar perfil | Estilo padrão, neutro |
| **Terciário/administrativo** | Novo, Duplicar, Renomear | Discreto, menor, agrupado sob "Perfil" |
| **Destrutivo** | Excluir, − remover | Texto/borda avermelhada sutil; nunca primário |

---

## 7. Organização dos botões

- **Agrupar por função** com separadores visuais:
  `[Perfil: Novo·Duplicar·Renomear·Excluir]` | `[Programas: Abrir pasta·Abrir arquivos]` |
  `[Biblioteca: Gerenciar]`.
- CRUD de perfil pode ir para um menu "⋯" ou `QToolButton` — são ações raras, não merecem 4
  botões de mesmo peso na barra principal.
- "Gerenciar codigos…" → renomear **"Biblioteca de códigos…"** e tirar do meio dos botões de
  linha.

---

## 8. Organização das tabelas

- **Comuns:** título forte "TROCAS PARA TODOS OS PROGRAMAS"; faixa/cor de cabeçalho neutra.
- **Específicas:** título "TROCAS EXTRAS — só de `<nome>`" com o nome do programa em destaque
  (já existe `lbl_prog`, [linha 497](cnc_batch_editor/ui/main_window.py)); cor de cabeçalho
  diferente + leve recuo, comunicando "subconjunto".
- Quando a tabela específica está vazia, **recolher/atenuar** para reduzir ruído.
- "+ da lista" → **"+ da biblioteca"** em ambas.

---

## 9. Estratégia de feedback visual

- **Inline + cor + ícone + palavra** (não só cor — item D): `● OK`, `▲ atenção`, `■ erro`.
- Lista de programas pintada **após** o preview, com contagem de trocas.
- Tira-resumo do lote atualizada a cada ação.
- Manter os `QMessageBox` finais (já bons), mas adicionar status inline nos passos
  intermediários.

---

## 10. Estratégia de validação

- **Estruturais** (automáticas): mantêm bloqueio de salvar — já correto.
- **Configuráveis**: migram para dentro do preview, **rodando sobre o resultado**; tipo de
  severidade decide se **bloqueia** "Confirmar". Aba avulsa permanece para checagem
  independente.
- Preview vira a **única tela de aprovação**: alterações + verificações + conflitos + alertas
  juntos.

---

## 11. Estratégia de progresso (honesta ao sistema síncrono)

- **Fase imediata (barato):** cursor "ocupado" + status "Processando N de M…" com
  `processEvents` antes do laço de `_build_outcomes`.
- **Fase 2 (quando fizerem Fase 8/threading):** `QThread` worker + barra real. Não prometer
  barra real antes disso.

---

## 12. Estratégia de mensagens de erro

- Toda mensagem em **linguagem de chão de fábrica**, com **o que houve + o que fazer**. Ex.:
  hoje "Múltiplas pastas" → "Os programas marcados estão em pastas diferentes. Processe uma
  pasta por vez." (já existe, [linha 590](cnc_batch_editor/ui/main_window.py) — bom padrão,
  **estender a todas**).
- Sugestão de variante com zero à esquerda ("achei 'M08'?") já existe
  ([linha 557](cnc_batch_editor/ui/main_window.py)) — ótimo, **destacar mais** no preview.
- Erro nunca "mudo": o `sys.excepthook` global já garante isso ([STATUS.md](cnc_batch_editor/STATUS.md)).

---

## 13. Estratégia para iniciantes

- **Estado vazio orientado** (item G): ao abrir sem perfil/programas, painel central "Comece
  em 3 passos: 1 escolha o perfil · 2 abra os programas · 3 defina as trocas".
- Faixa de etapas passiva destaca o passo atual.
- Rótulos simples; tooltips explicando "troca comum" vs "extra".

---

## 14. Estratégia para experientes

- **Atalhos** (item B): F5 = revisar, Ctrl+S = salvar perfil, Del = remover linha, Ctrl+Enter
  = confirmar.
- **Nada de wizard bloqueante** — tela única preservada.
- Tudo visível de uma vez; faixa de etapas é só informativa, não obriga cliques.

---

## 15. Impacto esperado na produtividade

Estimativa **qualitativa** (sem números falsos):

- Hierarquia + CTA claro: menos hesitação por ação → **ganho moderado e constante** no uso
  diário.
- Atalhos: **ganho alto** para o operador que repete o lote dezenas de vezes.
- Preview unificado: elimina a ida-e-volta à aba Verificações → **menos passos por lote**.

---

## 16. Impacto esperado na redução de erros

- Verificação como porteiro antes de salvar (sobre o resultado): **maior** — pega "deve
  existir/não pode existir" antes de o arquivo ir pra máquina.
- Indicador "perfil modificado *" + aviso ao sair: elimina perda silenciosa de configuração
  (item A).
- Ícone+palavra junto da cor: reduz erro de leitura de severidade.
- Caminho de destino visível: reduz salvar no lugar errado.

---

## 17. Roadmap de implementação por prioridade

| Prio | Item | Impacto | Complexidade |
|------|------|---------|--------------|
| **P0** | QSS de hierarquia + CTA primária; renomear rótulos confusos ("+ da biblioteca", "Biblioteca de códigos…", remover "(preview)"); caminho de destino visível; indicador "perfil modificado *" + aviso ao sair; atalhos de teclado | Alto | Baixa (QSS + labels + pequena fiação; **sem core**) |
| **P1** | Verificações configuráveis dentro do preview, **rodando no resultado**, podendo bloquear "Confirmar"; tira-resumo do lote; faixa de etapas passiva; lista de programas colorida pós-preview | Alto | Média (mexe em `preview_dialog.py` + fiação; **sem core**) |
| **P2** | Feedback de progresso (cursor+status); diferenciação visual comuns×específicas; estado vazio orientado; ícone+palavra na severidade | Médio | Média |
| **P3** | Threading (Fase 8) → barra de progresso real; revisão de acessibilidade completa | Médio | Alta |

---

## 18. Classificação consolidada das sugestões

| Sugestão | Impacto operacional | Complexidade | Prioridade |
|----------|--------------------|--------------|------------|
| Hierarquia visual / CTA primária (QSS) | Alto | Baixa | P0 |
| Renomear rótulos confusos | Médio | Baixa | P0 |
| Caminho de destino visível | Médio | Baixa | P0 |
| Indicador "perfil modificado *" + aviso ao sair | Alto | Baixa | P0 |
| Atalhos de teclado | Alto (experts) | Baixa | P0 |
| Verificações no preview, sobre o resultado (porteiro) | Alto | Média | P1 |
| Tira-resumo do lote | Médio | Média | P1 |
| Faixa de etapas passiva | Médio | Média | P1 |
| Lista de programas colorida pós-preview | Médio | Média | P1 |
| Feedback de progresso (cursor+status) | Médio | Média | P2 |
| Diferenciação visual comuns×específicas | Médio | Média | P2 |
| Estado vazio orientado | Médio (iniciantes) | Baixa-Média | P2 |
| Ícone+palavra na severidade | Médio | Média | P2 |
| Threading → barra real | Médio | Alta | P3 |
| Acessibilidade completa | Médio | Alta | P3 |

---

## 19. Proposta consolidada (realista, compatível com a base)

**O CNC Batch Editor ideal mantém:** janela única, `QSplitter`, motor `core/` intocado,
preview + conferência SHA-256, abas existentes.

**E ganha:**
1. Hierarquia visual por QSS com uma CTA primária inequívoca;
2. Verificação configurável virando porteiro final dentro de um **preview unificado** que
   roda sobre o resultado;
3. Faixa de etapas **passiva** (não wizard);
4. Tira-resumo do lote;
5. Proteção contra perda de configuração de perfil;
6. Atalhos para o expert e estado-vazio para o iniciante.

Quase tudo é **P0/P1 em `ui/` + QSS** — **mínimo retrabalho, máximo ganho**, sem regressão no
motor de 106 testes.

**Discordâncias registradas:**
- Item 5 (feedback de conclusão já existe no salvar — gap real é nos passos intermediários).
- Item 12 (wizard de 6 passos bloqueante → trocar por faixa passiva de 5 passos).

---

## 20. Próximos passos

Nenhum código do app foi alterado. Sequência recomendada:

1. **Rodar a pesquisa** do `07-PROMPT-PESQUISA-UI.md` numa IA de pesquisa e trazer o
   resultado — decide **tela única vs wizard**, ordem/tamanho dos elementos e regras
   inteligentes (ex.: reabrir último perfil). Isso pode confirmar ou ajustar o layout/fluxo
   proposto aqui (§4–§8).
2. **Reconciliar** este relatório com a evidência da pesquisa e **validar com o Rafael**.
3. **Abrir proposta OpenSpec do P0** (uma mudança por vez) — só QSS + rótulos + fiação leve,
   sem tocar no `core/`.
4. **P1 seguinte:** integração das verificações no preview, rodando sobre o **resultado**
   (achado técnico do item 1/§10).

**Artefatos desta análise:** `06-ANALISE-UX-WORKFLOW.md` (este), `mockups\06-mockup-ux.html`,
`mockups\06-prototipo-navegavel.html`, `07-PROMPT-PESQUISA-UI.md`.
