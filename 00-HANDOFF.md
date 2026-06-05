# 00 — HANDOFF / PONTO DE RETOMADA — CNC Batch Editor

> **PRÓXIMA SESSÃO: leia SÓ este arquivo para retomar.** Ele resume o que existe,
> o que foi feito, por quê, os erros/aprendizados e o próximo passo. Não precisa
> reexplicar nada.

**Projeto:** CNC Batch Editor — ferramenta desktop Windows para **substituição de
texto em programas CNC** (.nc/.txt/.iso), com preview e preservação do original.
**É outro projeto, separado do ToolOptimizer CNC** (calculadora de parâmetros).
**Última sessão:** 2026-06-03
**Pasta do app:** `C:\Users\USUARIO\Desktop\Projetos\Sistema_verificador_codigos_cnc\cnc_batch_editor\`
**Baseline/spec:** `02-PRD_CNC_BatchEditor_v2.3.md` (motor/código atual) +
**`08-WORKFLOW-NOVA-DINAMICA.md` (nova dinâmica de produto DECIDIDA — fonte da UX a implementar)**

---

## 1. ESTADO ATUAL (tudo verificado)

| Parte | Estado |
|-------|--------|
| Núcleo (`core/`): matcher, plano, replacer, file_handler, verifier, preset_store, conference | ✅ pronto |
| Testes `pytest` (vetores §15 do PRD + sessões A–D) | ✅ **95 verdes** |
| `mypy --strict` no `core/` | ✅ **limpo (13 arquivos)** |
| CLI (`cli.py`) | ✅ funciona (dry-run e salvar) |
| GUI PySide6 (`ui/`) — **modelo por programa, com abas** | ✅ funciona (validada headless) |
| EXE portátil onedir (`dist\CNC_BatchEditor\`, ~115 MB) | ✅ **regenerado 2026-06-01 com conferência (Sessão D)**, smoke test OK |
| Programas de teste (`programas_teste\`) | ✅ 3 programas Fanuc realistas |

**Sessões do plano `04-PLANO-MELHORIAS`:** Stage 0 (H0.1–H0.6) ✅ · A (biblioteca) ✅ ·
B (CRUD perfis) ✅ · C (pasta saída) ✅ · **D (conferência forte) ✅** · E (empacotamento)
✅ código/EXE — **falta só a validação operacional manual do Rafael com arquivos reais**.

**O app NUNCA altera o original** — grava em pasta nova `_processado_PERFIL_data_hora\` + log `.txt`.

---

## 2. COMO RODAR (sempre via venv)

```powershell
cd C:\Users\USUARIO\Desktop\Projetos\Sistema_verificador_codigos_cnc\cnc_batch_editor
.\.venv\Scripts\python.exe main.py            # abre a GUI (desenvolvimento)
.\.venv\Scripts\python.exe -m pytest tests -q # roda os 33 testes
powershell -ExecutionPolicy Bypass -File build_exe.ps1   # regera o EXE portátil
```

**EXE portátil (pen drive):** copie a pasta `dist\CNC_BatchEditor\` inteira e rode
`CNC_BatchEditor.exe` (duplo clique, sem Python). Presets editáveis em
`data\presets\*.json` ao lado do exe.

---

## 3. COMO A GUI FUNCIONA (modelo POR PROGRAMA)

Duas abas:

- **Aba "Substituições"**
  - Esquerda: **PROGRAMAS** — lista com checkbox (marque quais recebem trocas). Clicar um programa seleciona ele para editar as trocas específicas dele. Funciona com **1 ou vários** programas.
  - Direita: **Trocas COMUNS** (valem para todos os marcados) + **Trocas SÓ DESTE programa** (as específicas do programa selecionado). Só as marcadas em "Aplicar" são feitas.
  - Botão **Executar substituições** → abre **preview** (diff por programa, alertas, conflitos); só então **Confirmar e salvar**.
  - **Salvar perfil** grava o conjunto de trocas no JSON do perfil (reuso).
- **Aba "Verificações"** (separada): tabela de checagens (deve existir / não pode existir / mín / máx / exato) + botão **Executar verificações** (roda nos marcados, sem alterar nada).

Exemplo do uso real (validado): comuns `M08→M07`, `G54→G55`; PECA01 tem só dela `T1→T21`; dá pra adicionar `S1500→S2000` **só na PECA02** sem afetar as outras.

---

## 4. O QUE FOI FEITO NESTA SESSÃO (resumo)

1. **Analisei e refinei o PRD** v2.2 → **v2.3** (`02-PRD_CNC_BatchEditor_v2.3.md`), corrigindo erros e adicionando rastreabilidade.
2. **Construí o núcleo** (motor de substituição seguro) + **33 testes** cobrindo os vetores §15.
3. **CLI** funcional como primeira fatia (dry-run/salvar).
4. **GUI PySide6**: 1ª versão simples → reescrita para painel de regras → **reescrita final para modelo por programa** (abas, comuns + por-programa, verificações separadas), atendendo ao pedido do Rafael de escolher individualmente o que mudar em cada programa.
5. **EXE portátil onedir** gerado e regenerado com a UI nova.
6. **Programas de teste** Fanuc realistas criados (`programas_teste\`).
7. **Regra de segurança registrada** (ver §6).

---

## 5. DECISÕES IMPORTANTES (e por quê)

- **Estratégia "fatia vertical" (walking skeleton)**, não as 10 fases do PRD em ordem: motor já validado primeiro, depois casca, para ter algo rodando rápido.
- **Modelo de regras "Comuns + por programa"** (hierarquia §7.1 do PRD): escolhido por ser o padrão validado na indústria (pós-processadores CNC, CIMCO/Predator) e por atender tanto 1 programa isolado quanto lote.
- **Comentários `()` SÃO alterados** (o MVP não tem parser de comentário) — documentado como limitação.
- **Inserção de novas linhas/blocos fica fora do MVP**; `find`/`replace` são de linha única.
- **Boundary CNC** = `(?<![A-Z])FIND(?![0-9.])` (ver §6, foi um erro corrigido).

---

## 6. ERROS COMETIDOS E APRENDIZADOS (importante)

1. **Bug do boundary regex (PRD v2.2):** o padrão tinha `(?<![A-Z0-9.])`, que **bloqueava** `M6T1`/`G43H1T1` (casos concatenados reais Fanuc) — falso negativo perigoso. **Corrigido para `(?<![A-Z])…(?![0-9.])`** e provado com 14 vetores. Lição: testar o regex contra os próprios vetores antes de confiar.
2. **Bug de reingestão (§9.3):** o app relistava os arquivos `_processado_*` de saídas anteriores. **Corrigido** (pula nomes que começam com `_processado_`).
3. **Erro de UX (o mais importante):** a 1ª GUI **aplicava as regras do perfil sem o usuário escolher** — não era o que o Rafael precisava. Ele quer **escolher por programa** o que trocar. **Refeito** para o modelo por programa (§3). Lição: o coração do produto é a *escolha do usuário*, não rodar um preset.
4. **Screenshots sem autorização:** tirei capturas da tela do Rafael sem pedir. Ele proibiu. **Registrado e travado** (§7). Lição: nunca capturar a tela sem "sim" explícito.
5. **`pyinstaller.exe` quebrado após mover o venv (2026-06-01):** o wrapper `.venv\Scripts\pyinstaller.exe` saía com exit 1 sem nenhuma saída (shebang com caminho absoluto antigo, de quando a pasta era `Desktop\` sem `Projetos\`). O `build_exe.ps1` rodava, reportava "OK", mas **não regenerava nada** (arquivos do `dist` ficavam com data antiga — pista: comparar `LastWriteTime` com a hora atual). **Corrigido:** `build_exe.ps1` agora usa `python -m PyInstaller` (não o `.exe`) + `if ($LASTEXITCODE -ne 0) { throw }`. Lição: depois de `build_exe.ps1`, confira o timestamp do `dist`; um wrapper `.exe` de venv movido pode falhar silenciosamente.
6. **Botão "Executar" não fazia nada no EXE (2026-06-01) — DOIS bugs:**
   - **(a) Crash silencioso por enum→string.** Na Sessão D adicionei `r.on_zero_matches.value` no `_build_outcomes`. Mas `OnZeroMatches` herda de `str`, e o Qt, ao guardar/ler o enum num `QTableWidgetItem` (`setData`/`data`, UserRole), **devolve string pura** (`"warn"`), não o enum → `'str' object has no attribute 'value'` → `AttributeError`. Como o EXE é `--windowed` (sem console), o crash **sumia sem mensagem**. **Corrigido:** `_read_subs_table` reconstrói o enum (`OnZeroMatches(raw)`), `_build_outcomes` ficou defensivo, e adicionei `sys.excepthook` global em `main.py` que mostra erros em caixa de diálogo (nunca mais "fica mudo"). Lição: enum que herda de `str` + Qt `setData`/`data` perde o tipo; e os 95 testes eram **só de core puro** — bug de GUI escapou. Por isso criei `tests/test_ui_smoke.py` (GUI headless/offscreen).
   - **(b) Programas Fanuc sem extensão eram ignorados.** Os arquivos reais (`prog\O2169`...) não têm extensão; `list_input_files` filtrava por `.nc/.txt/.iso` → 0 arquivos → "Abrir pasta" não carregava nada. **Corrigido:** `list_input_files` agora aceita curinga `"*"`, **sempre** inclui arquivos sem extensão, e binários são rejeitados depois por `read_file`. Preset MAZAK passou a usar `extensions: ["*"]`; o "Abrir programa(s)..." abre em "Todos os arquivos" por padrão. Testes: `tests/test_list_input_files.py`.

---

## 7. REGRAS DO USUÁRIO (OBRIGATÓRIAS)

- **SCREENSHOT/CAPTURA DE TELA: PROIBIDO sem autorização explícita.** Sempre pedir "posso tirar um screenshot?" e só capturar após "sim". Registrado em `Desktop\CLAUDE.md`, em `~/.claude/settings.json` (`permissions.ask` para Windows-MCP Screenshot/Snapshot) e na memória.
- **Exclusão/mover/renomear pasta do desktop:** só com **dupla confirmação** explícita (ver `Desktop\CLAUDE.md`).

---

## 8. MAPA DE ARQUIVOS

```
Sistema_verificador_codigos_cnc\
├── 00-HANDOFF.md                 <- ESTE arquivo (leia primeiro)
├── 02-PRD_CNC_BatchEditor_v2.3.md  <- spec/baseline
├── 02-PRD_CNC_BatchEditor_v2.0.md  <- versão antiga (histórico)
├── 04-PLANO-MELHORIAS-2026-06-01.md <- plano Stage 0 + Sessões A–E (CONCLUÍDO)
├── 05-PLANO-UI-UX.md             <- redesenho de interface (skill, dores, workflow-base)
├── 06-ANALISE-UX-WORKFLOW.md     <- relatório de UX: 12 problemas + layout/fluxo (etapa anterior)
├── 07-PROMPT-PESQUISA-UI.md      <- prompt da pesquisa de UX (VALIDADA em 2026-06-03)
├── 08-WORKFLOW-NOVA-DINAMICA.md  <- ⭐ NOVA DINÂMICA "por código" (fonte do produto a implementar)
├── mockups\                      <- 06-*.html + 08 (tela única) + 09 (indicador) + 10 (fluxo por código, FINAL)
├── GUIA-DE-USO.md                <- guia passo a passo do operador (cópia .txt vai no EXE)
└── cnc_batch_editor\
    ├── STATUS.md                 <- status detalhado por fase
    ├── main.py                   <- entrada da GUI
    ├── cli.py                    <- versão linha de comando
    ├── app_paths.py              <- caminhos (dev x EXE)
    ├── build_exe.ps1             <- regenerar o EXE
    ├── PORTATIL_LEIA-ME.txt      <- guia do operador (vai no pen drive)
    ├── core\                     <- motor (puro, testado): matcher, replacement_plan,
    │                                replacer, file_handler, verifier, preset_store, models, session_log
    ├── ui\                       <- main_window.py (abas/por-programa) + preview_dialog.py
    ├── data\presets\             <- MAZAK_VTC530.json (perfil exemplo)
    ├── programas_teste\          <- PECA01/02/03 (teste)
    ├── tests\                    <- 33 testes pytest
    └── dist\CNC_BatchEditor\     <- EXE portátil pronto (copiar p/ pen drive)
```

---

## 9. PRÓXIMOS PASSOS — RETOMAR AQUI

> ### 🚨 PRÓXIMO PASSO IMEDIATO (decidido 2026-06-04 cont. 2): EXECUTAR O REBRAND "FlowNC" + LIMPEZA DE DOCS
> O app vai ser renomeado de **CNC Batch Editor → FlowNC** e a documentação será consolidada
> (14 docs dispersos → conjunto enxuto em `docs\` + entrada única; obsoletos → `_descarte\`).
> **O plano está pronto, revisado e APROVADO:** **`PLANO-RENAME-FLOWNC.md`** (v3 — incorpora 17
> questões de revisão técnica; premissas verificadas contra o código real). **Comece pela Fase 0**
> (git init + `requirements.lock` + backup externo testado) e **pause a cada fase** esperando "pode
> seguir". Há um **GATE-5 obrigatório** antes da fase destrutiva (renomear pasta + recriar venv).
> **Bloqueadores já mapeados:** o projeto **NÃO é git** (criar baseline); venv com versões soltas
> (travar no lock). Depois do rebrand, implementar a Mudança 1 OpenSpec (abaixo).
>
> ### ⭐ FOCO (depois do rebrand): IMPLEMENTAR A NOVA DINÂMICA "POR CÓDIGO"
> O sistema está **funcional e estável** (106 testes verdes). A UX foi **redesenhada e a
> dinâmica está DECIDIDA** (não é mais só "melhorar a tela": mudou o **fluxo de trabalho**).
>
> **LEIA `08-WORKFLOW-NOVA-DINAMICA.md`** — é a fonte da nova dinâmica (contexto, problemas,
> funções, workflow passo a passo, regras de segurança). O mockup final interativo é
> **`mockups\10-mockup-fluxo-codigo.html`**.
>
> **A DECISÃO (vira o produto):** abandonado o fluxo "por programa". Adotado **FLUXO POR
> CÓDIGO** = padrão *rule builder* (o operador pensa primeiro no código, depois nos programas):
> 1. **① Código de origem** — dropdown rápido da biblioteca.
> 2. **② Ação** — **Substituir** (escolhe código novo, menos o já selecionado) **ou Retirar**.
> 3. **③ Programas** — lista começa **VAZIA**; botão fácil "Abrir pasta/Adicionar"; indicador
>    de quantos programas recebem a regra.
> 4. **Regra vira CARTÃO** no resumo em tempo real (editar/duplicar/excluir) + **aviso de
>    conflito** entre regras. Volta ao passo 1 para a próxima regra.
> 5. **Executar** (anima "Executando/Analisando") → **pop-up de resumo** → **Salvar** (anima
>    "Salvando") → **abre a pasta** automaticamente.
>
> **Travas/decisões do Rafael (NÃO reabrir):**
> - Lista de programas **sempre vazia** (programas mudam toda hora). Rejeitada a ideia de "pool".
> - ~~**Sem varredura** de códigos nos programas (rejeitado por complexidade)~~ **— SUPERADO em
>   2026-06-03** (decisão #1 do `10-PLANO`): a varredura **entra, em 2º plano (QThread)**. Mantido:
>   **0 ocorrências = sinal útil** de erro (âmbar) **+ desmarca o arquivo**.
> - **"Retirar" é controlado:** 1 código por execução · allowlist (só código válido da
>   biblioteca) · preview obrigatório das linhas afetadas · bloqueio por conflito · log.
>   (uso típico: remover `M6` pontual quando a ferramenta roda com spindle desligado.)
> - **Biblioteca:** código + função, editável, **variações por máquina/perfil** (M8/M08);
>   "Adicionar código" sempre visível + "+" salvar rápido (pergunta perfil ou global); já vem
>   com biblioteca padrão do mercado.
> - ~~**Salvar = COMO HOJE** (pasta com data, original NUNCA tocado); rejeitada pasta fixa/sobrescrever~~
>   **— SUPERADO em 2026-06-04** (decisão #5 do `10-PLANO`): o app **publica o editado direto na pasta de
>   trabalho da máquina** (fixa/configurável, pode ser de rede) e **leva os originais para um backup
>   versionado** (pasta configurável, qualquer lugar). Mantido e reforçado: conferência SHA-256 agora
>   **dupla** (backup + publicado), troca **atômica** (a pasta da máquina nunca fica sem o programa), log.
>   Objetivo: acabar com o trabalho manual de mover/copiar/colar arquivos entre pastas.
> - **Perfil salvo** carrega regras/códigos, mas **programas começam vazios** (reconfirmar).
> - **Verificações configuráveis FORA por enquanto** (decisão). Voltam depois como porteiro no
>   pop-up de resumo (bloqueia Salvar se verificação crítica falhar). Achado técnico antigo
>   continua válido: rodar verificações sobre o RESULTADO, não sobre o original.
>
> **Pesquisa do `07` — VALIDADA (2026-06-03):** rodei 8 buscas web. Confere ISA-101, ISO
> 9241-110, NN/G (wizard puro irrita uso diário → certo abandonar wizard), WCAG 2.2. Correções
> pequenas: 44px é Apple/AAA (o mínimo AA é 24px); 3:1 também vale p/ componentes de UI; fonte
> 14-16px é boa prática, não norma; o doc do Perplexity tem ruído de citações `[^16+]`. Veredito:
> **confiável**; sustenta o híbrido (tela única de preparação + ato de salvar separado/protegido).
>
> **PLANEJAMENTO CONCLUÍDO (2026-06-03 cont.):** o design e o plano de execução já existem:
> - **`09-DESIGN-3-COLUNAS.md`** — especificação VISUAL (layout 3 colunas, tokens de cor/fonte,
>   posições, componentes, lógica de execução). Extraída de mockup aprovado (export em `Downloads`).
> - **`10-PLANO-EXECUCAO-3-COLUNAS.md`** — PLANO de execução: 4 mudanças OpenSpec em ordem
>   (1 motor Retirar+contagem · 2 biblioteca · 3a UI Substituir+varredura · 3b Retirar+conflito) +
>   tudo que precisa (fontes IBM Plex, threading, ícones, migração, EXE).
>
> **4 decisões travadas (não reabrir):** (1) varredura prévia **SIM, em 2º plano/QThread**;
> (2) Retirar **junta espaços + apaga linha vazia**; (3) UI em **2 fases** (3a depois 3b);
> (4) biblioteca **catálogo padrão + migra o atual**.
>
> **STATUS DA MUDANÇA 1:** a proposta OpenSpec **já foi CRIADA e validada** (2026-06-04 cont.) —
> `openspec\changes\motor-retirar-contagem-e-publicacao\` com `proposal.md` + `design.md` +
> `specs\` (4: remocao-de-codigo, varredura-de-ocorrencias, validacao-de-lote, publicacao-segura) +
> `tasks.md` (7 grupos / 33 tarefas). `openspec validate` = válida. **Falta IMPLEMENTAR** (`/opsx:apply`).
> Núcleo: `core/` puro/sensível (Retirar replace-vazio+faxina · contagem · validadores · **publicação segura**).
> **Layout = 2 colunas (design B, §0 do `09`)** · **salvar = publicar na pasta da máquina + backup (decisão #5)**.
> Ver `10-PLANO-EXECUCAO-3-COLUNAS.md` §4 e §8. **Mas o rebrand FlowNC vem ANTES** (banner no topo de §9).
>
> **Skill de design (se for usar):** `frontend-design` (Anthropic) —
> https://github.com/anthropics/skills/tree/main/skills/frontend-design — baixada mas **não
> ativada**; instalar via `/plugin` → marketplace `claude-plugins-official` → Install/Enable.
>
> **Histórico (etapas anteriores do redesenho, antes da virada por código):** `05-PLANO-UI-UX.md`,
> `06-ANALISE-UX-WORKFLOW.md` (12 problemas + faixa passiva), `mockups\06-*.html`,
> `mockups\08` (tela única validada) e `mockups\09` (3 opções de indicador de troca exclusiva —
> superado: o escopo virou propriedade da regra no fluxo por código).

---

### SESSÃO 2026-06-04 (cont. 2) — OpenSpec Mudança 1 CRIADA + rebrand FlowNC + plano de limpeza de docs

1. **Criei a proposta OpenSpec da Mudança 1** `motor-retirar-contagem-e-publicacao` (via `/opsx:propose`):
   `proposal.md` + `design.md` (8 decisões técnicas) + `specs\` (4 capacidades) + `tasks.md` (7 grupos/33 tarefas).
   `openspec validate` = **válida**. Tudo fiel ao código real relido (`models`/`matcher`/`replacement_plan`/
   `replacer`/`file_handler`/`conference`/`settings_store`). **Ainda NÃO implementada** → `/opsx:apply` depois.
2. **Rafael decidiu renomear o app: `CNC Batch Editor` → `FlowNC`** (todas as formas: exibição, EXE,
   pacote `pyproject`, pasta `cnc_batch_editor`→`flownc` com venv recriado). E **consolidar a documentação**
   (objetivo: parar de queimar token lendo 14 docs redundantes) → estrutura enxuta `docs\` + entrada única;
   obsoletos para `_descarte\` (rastreável, com `_INDICE.md`); o útil sintetizado.
3. **Produzi e refinei o plano em 3 rodadas de revisão** → **`PLANO-RENAME-FLOWNC.md` (v3)**. Duas revisões
   técnicas externas foram conferidas contra o repo e incorporadas: v2 (13 correções) e v3 (17 questões:
   10 problemas P1–P10 + 7 lacunas L1–L7). **APROVADO**, aguardando só o "pode seguir" da Fase 0.
4. **Premissas VERIFICADAS no código (não assumidas):** layout plano (nenhum `from cnc_batch_editor` →
   renomear a pasta não quebra import); `app_paths.py` sem o nome do app (dados imunes); `build_exe.ps1`
   não usa o `.spec` (artefato morto); configs relativas; sem `conftest.py`; **projeto NÃO é git**;
   venv atual = mypy 2.1.0 / PySide6 6.11.1 / pyinstaller 6.20.0 / pytest 9.0.3 / **ruff ausente**; 83 `def test_`.
5. **Salvaguardas que o plano v3 obriga antes de mexer:** `git init`+commit baseline (sem isso não há rollback),
   `pip freeze > requirements.lock` (recriar o venv do lock, não solto), backup externo zip **testado**,
   **GATE-5** (internet + `pip download` dry-run + git limpo) antes de renomear a pasta, e preservar o `dist\`
   antigo até o `FlowNC.exe` novo passar no smoke.

**Próximo agente:** leia **`PLANO-RENAME-FLOWNC.md`** e execute da **Fase 0**, pausando a cada fase. NÃO renomeie
nada antes do git baseline. O rebrand vem ANTES de implementar a Mudança 1 (o plano mantém a change aberta e
atualiza os ponteiros `proposal/design/tasks` dela para os novos `docs\`).

**Aprendizado:** revisão adversarial em camadas valeu muito — cada passada pegou itens reais (a 1ª, mecânica do
Retirar e publicação; a 2ª, fragilidade do `pip install -e .` e dados sem nome; a 3ª, ausência de git, versões
soltas e falta de portão na fase destrutiva). Verificar a alegação no código antes de aceitar é o que separa
revisão útil de ruído.

---

### SESSÃO 2026-06-04 — revisão do plano + publicação + layout 2 colunas

1. **Revisei o `10-PLANO` contra o código real.** Mudança 1: "Retirar" **não** é motor novo — vira `Rule(find=X, replace="", action=RETIRAR)` reusando `build_plan`/`apply_edits` (boundary + conflito + lote misto já testados); só nasce a **faxina de linha** (`core/line_cleanup.py`). Corrigi a contradição "sem varredura". Separei "conflito de regra" × "conflito de pedaço". Mudança 2 congela `normalized_form(código, perfil)`.
2. **VIRADA de salvamento (decisão #5):** deixa de gravar em pasta nova. O app **publica o editado direto na pasta de trabalho da máquina** (fixa/configurável, pode ser de rede) e **move os originais para um backup versionado** (pasta configurável). Fluxo único, troca **atômica** (a pasta nunca fica sem o arquivo), **dupla conferência** SHA-256. Novo `core/publisher.py` + `working_dir`/`backup_dir` no `settings_store`. Rafael dispensou aviso anti-republicação (o backup versionado protege o original). Objetivo: acabar com mover/copiar/colar manual.
3. **VIRADA de layout (design B):** a interface deixou de ser 3 colunas iguais (col 1 sobrava vazia). Vira **2 COLUNAS**: esquerda empilhada (① compositor **horizontal/baixo** + ② programas **grande**) + ③ **resumo dominante** à direita (altura inteira), com o conflito em destaque. Spec no **§0 do `09`**.
4. **Mockups:** `mockups\11` (3 colunas, anterior) e **`mockups\12-mockup-bancada-resumo-dominante.html`** (2 colunas, **FINAL** — interativo: Substituir/Retirar+trava/varredura/pop-up resumo+preview). Fonte do design B: `Downloads\B _ Bancada _ montar_revisar_ resumo dominante _conflito_.html`.
5. **Docs atualizados:** `09` (§0 = layout 2 colunas), `10` (decisão #5 + `publisher` + layout + §9 pontos 1–8), `00-HANDOFF` (este bloco), memória.

**Aprendizado:** errei o 1º mockup do design B (fiz 3 colunas de novo); o certo eram **2 colunas** (esquerda empilhada + resumo à direita). Os widths repetidos `836px`/`470px` no HTML já denunciavam isso — ler os tokens computados antes de assumir o arranjo.

---

### SESSÃO 2026-06-03 (cont.) — design "3 colunas" extraído + plano de execução

1. **Rafael trouxe um mockup aprovado** (export HTML em `Downloads`, "Linha de Produção · 3 colunas").
   Extraí layout/design/posições/fluxo/lógica → **`09-DESIGN-3-COLUNAS.md`** (spec visual).
   É a **evolução em 3 colunas** do `08` (fluxo por código preservado; resumo+Executar sempre à direita).
2. **Achado importante:** o modelo mostra **contagem de ocorrências por arquivo** → reintroduz a
   **varredura** que o `08` tinha rejeitado. Rafael decidiu: **entra, em 2º plano (QThread)**.
3. **Produzi o plano** → **`10-PLANO-EXECUCAO-3-COLUNAS.md`**: 4 mudanças OpenSpec em ordem + infra
   (fontes IBM Plex, threading, ícones, migração de preset, rebuild EXE). 4 decisões travadas (ver bloco FOCO).
4. **Próximo:** proposta OpenSpec da Mudança 1 (`motor-retirar-e-contagem`).

**Aprendizado:** o motor (`core/`) muda pouco — escopo (quais programas) é estado de SESSÃO, não de
perfil; o motor já planeja por arquivo. O grosso é UI + biblioteca; o sensível é "Retirar" (core+testes).

---

### SESSÃO 2026-06-03 — pesquisa validada + VIRADA para "fluxo por código" (resumo)

1. **Validei a pesquisa do `07`** (o resultado veio do Perplexity, em `Downloads`): rodei 8
   buscas web próprias. Confere ISA-101, ISO 9241-110, NN/G (wizard puro irrita uso diário),
   WCAG 2.2. Correções pequenas registradas (44px=Apple/AAA, não AA; 3:1 vale p/ componentes;
   fonte 14-16px não é norma; ruído de citações no doc). **Veredito: confiável.**
2. **O Rafael propôs uma dinâmica melhor** — começar pelo **código**, não pelo programa. Investiguei
   o padrão (rule builder, regras de e-mail/formatação condicional, CIMCO "Replace All from File",
   dialetos de G-code) e **validei a proposta**. Discutimos melhorias; ele decidiu cada ponto.
3. **Decisão final travada** → **FLUXO POR CÓDIGO** (ver bloco FOCO ATUAL). Produzi:
   - **`08-WORKFLOW-NOVA-DINAMICA.md`** — documento completo (contexto, problemas, funções,
     workflow, regras de segurança, glossário, rastreabilidade). **Fonte do produto a implementar.**
   - **`mockups\10-mockup-fluxo-codigo.html`** — protótipo interativo do fluxo final.
   - `mockups\08` (tela única validada) e `mockups\09` (3 opções de indicador) como etapas.

**Aprendizados desta sessão:**
- A dinâmica "por programa" foi **substituída** pela "por código" — é o fluxo mental real do
  operador (decide o código, depois onde aplicar). O **escopo virou propriedade da regra**, o que
  de quebra resolveu o problema "qual programa tem troca exclusiva".
- **"Retirar código" é a peça mais sensível:** ação destrutiva, então é cercada (1 por execução,
  allowlist, preview, conflito, log). Provavelmente exige **`core/` + testes novos**.
- **Validar antes de decidir** (web) continua dando retorno: pegou imprecisões no doc de pesquisa
  e confirmou o padrão rule builder com fontes.

---

### SESSÃO 2026-06-02 — entrega verificada + análise de UX (resumo)

1. **Reverificação do sistema atual (sem mudar código):** `pytest` → **106/106 verdes** em
   ~3,4s (inclui `test_ui_smoke.py`); **EXE empacotado abre** sem erro (subiu com o título
   correto da janela, encerrado limpo); conteúdo da pasta `dist\CNC_BatchEditor\` conferido
   (EXE + `_internal\` + `data\presets\MAZAK_VTC530.json` + `GUIA-DE-USO.txt` idêntico ao
   `.md` da raiz + `LEIA-ME.txt`). **Pacote pronto para pendrive** (entregue como pasta, sem
   ZIP, por opção do Rafael).
2. **Análise de UX devolvida pelo Rafael** → produzi `06-ANALISE-UX-WORKFLOW.md`,
   `mockups\06-*.html` e o prompt de pesquisa `07-PROMPT-PESQUISA-UI.md` (ver bloco FOCO
   ATUAL acima).

**Aprendizados desta sessão:**
- O sistema entregue **não exigiu nenhuma mudança de código** — só verificação + empacotamento.
  Reforça que o `core/` está estável (106 testes) e o EXE portátil (`app_paths.py` resolve
  dados ao lado do executável quando `sys.frozen`).
- **Decisão de UX importante:** discordei do "wizard de 6 passos" (item 12 do Rafael) — para
  ferramenta de produção repetitiva, **tela única + faixa de etapas passiva** é melhor; mas a
  forma final (tela única vs wizard) será decidida pela **pesquisa do `07`**, não por palpite.
- **Achado técnico para a implementação futura:** as verificações configuráveis hoje rodam
  sobre o arquivo **original** (`ui/main_window.py:_on_execute_verifs`, `read_file(p)`), não
  sobre o **resultado** das trocas. Integrá-las como "porteiro" no preview exige rodá-las
  sobre o resultado — mudança de semântica deliberada (sem tocar no `core/`; `run_configurable`
  já existe).

---

### Trabalho de CÓDIGO já concluído (histórico)

> **O plano `04-PLANO-MELHORIAS` está concluído em código.** Stage 0 + Sessões A–E
> implementados. 106 testes verdes, `mypy --strict` limpo, EXE regenerado e com smoke test OK.

**Único passo restante (e SÓ o Rafael pode fazer): validação operacional manual.**
DoD da Sessão E: "Teste real assinado pelo operador". Ou seja:

1. Copiar `cnc_batch_editor\dist\CNC_BatchEditor\` para um pen drive.
2. Rodar `CNC_BatchEditor.exe` num PC sem Python (de preferência no chão de fábrica).
3. Fazer o fluxo completo com **arquivos NC reais da fábrica** (pasta `prog\` ou da máquina):
   abrir → marcar trocas comuns + por programa → Executar (preview com **checklist**) →
   Confirmar e salvar → conferir o **log** (`_log.txt`) com a seção
   `=== CONFERENCIA POS-SALVAMENTO ===` (SHA-256 de cada arquivo).
4. Conferir SmartScreen/antivírus no PC alvo (EXE não assinado pode alertar — falso positivo do `onedir`).

**Melhorias opcionais (não bloqueiam o uso):**
- Fase 8: `QThread` para lotes muito grandes (hoje síncrono; ok p/ lotes típicos ≤50).
- Editor explícito de política `OnZeroMatches`/`mode` por linha na GUI (hoje viaja só no dado).
- Verificações estruturais antecipadas na aba Verificações (hoje só aparecem no preview/salvar).

**Resumo do que foi feito (plano completo):**

| Item | Arquivo | Estado |
|------|---------|--------|
| H0.1–H0.6 (Stage 0 hardening) | `core/*`, `ui/main_window.py` | ✅ |
| Sessão A — biblioteca de códigos | `core/library_store.py`, `ui/library_dialog.py` | ✅ |
| Sessão B — CRUD de perfis + backup | `core/preset_store.py`, `ui/main_window.py` | ✅ |
| Sessão C — pasta de saída configurável | `core/settings_store.py`, `ui/main_window.py` | ✅ |
| **Sessão D — conferência forte (SHA-256)** | `core/conference.py`, `ui/main_window.py` | ✅ |
| Sessão E — EXE + validação | `build_exe.ps1`, `dist\` | ✅ código; 🟡 falta teste manual do Rafael |

---

> (Seção anterior mantida abaixo para histórico)

## 9-OLD. PRÓXIMOS PASSOS (sugeridos, em ordem)

> Revisão detalhada com priorização em `03-REVISAO-2026-06-01.md`.

**ALTA:**
1. **Rafael testar com programas NC REAIS** (pasta `prog/` ou arquivos da fábrica na GUI) — validação mais importante, pode revelar ajustes que nenhum teste revela.
2. **CRUD de perfis na GUI** (criar/duplicar/renomear/excluir) — maior lacuna funcional restante.
3. **Verificações estruturais na aba Verificações** — hoje erros críticos (ex: perda de M30) só aparecem ao salvar; melhor mostrar antes.

**MÉDIA:**
4. `QThread` para lotes grandes (Fase 8) — hoje síncrono, pode congelar janela em lotes pesados.
5. Preview com abas por arquivo — hoje tudo num texto único; difícil de ler com 10+ arquivos.

**BAIXA:**
6. Ícone do app, janela abrir maximizada, botão "copiar trocas para vários programas".
7. Checar **SmartScreen/antivírus** no PC do chão de fábrica (EXE não assinado).

---

## 10. PENDÊNCIAS / RISCOS CONHECIDOS

- GUI validada **headless** (construção + lógica) e o EXE **abre**; falta o Rafael fazer o **clique-a-clique** completo (ele já viu a tela).
- EXE **não assinado** → SmartScreen/AV pode alertar (falso positivo do `onedir`).
- O diálogo de preview foi validado por construção (não por clique automatizado).
