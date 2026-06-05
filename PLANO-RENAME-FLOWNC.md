# PLANO — Renomear para "FlowNC" + Limpeza/Consolidação da documentação

> **Status:** aguardando aprovação ("pode seguir"). NÃO executar antes.
> **Revisão:** v3 — incorporadas as 17 questões da revisão técnica (10 problemas P1–P10 + 7 lacunas L1–L7, via melhorias M1–M12). Premissas centrais **verificadas contra o código real**.
> **Objetivo:** (1) renomear o app `CNC Batch Editor` → **FlowNC** em tudo; (2) limpar e consolidar a documentação numa estrutura enxuta, profissional e econômica em tokens; (3) descartar (de forma rastreável) o que é histórico/inútil.
> **Princípio:** nada é apagado de imediato — o obsoleto vai para `_descarte\` (recuperável). **Git de baseline + backup testado** antes de mexer. Gates obrigatórios entre fases.

---

## 0. Decisões já travadas (do Rafael)

| # | Decisão |
|---|---|
| A | Trocar **todas** as formas do nome: exibição (`CNC Batch Editor`), executável (`CNC_BatchEditor`) e pasta do código (`cnc_batch_editor`). |
| B | **Renomear a pasta** `cnc_batch_editor` → `flownc` e **recriar o venv do zero**. |
| C | Formato da doc = **decisão do agente** → adotado **conjunto enxuto + entrada única** (boas práticas AI-friendly). |
| D | Os JSON de dados (`data\presets\`, `data\library.json`, `data\settings.json`) **podem ser recriados** — **mas o caminho NÃO contém o nome do app** (verificado: `app_paths.py:18-27`), então o rename não exige tocá-los. Recriar o "banco" é **opcional** e independente do rename. |
| E | Descartar histórico inútil numa **pasta de descarte**, com **índice**; sintetizar o útil. |

---

## 0-bis. Premissas VERIFICADAS contra o repositório (não assumidas)

- ✅ **Layout plano:** nenhum `from cnc_batch_editor...` no código → renomear a pasta **não quebra import**. Só o `.venv` (caminhos absolutos) é afetado.
- ✅ **`app_paths.py` sem o nome do app** (`data/presets` relativo ao executável) → dados imunes ao rename.
- ✅ **`build_exe.ps1` não usa o `.spec`** (`--onedir --name` sobre `main.py`) → `.spec` é artefato morto.
- ✅ **Configs relativas** (`pythonpath=["."]`, `mypy files=["core"]`) → imunes ao rename.
- ✅ **Sem `conftest.py` no projeto**; `exemplo_lote` não referenciado por `.py` → mover é seguro.
- ✅ **NÃO é repositório git** (`fatal: not a git repository`) → ver M1/P1.
- ✅ **Venv atual:** mypy 2.1.0 · PySide6 6.11.1 · pyinstaller 6.20.0 · pytest 9.0.3 · **ruff NÃO instalado** → ver M2/P2 e M12/P9.
- ✅ **Contagem de testes:** 83 `def test_` (+parametrize ≈106) → baseline exata na F0 (M9/P10).

---

## 1. Transformações de nome (exato)

| De | Para | Onde |
|---|---|---|
| `CNC Batch Editor` | `FlowNC` | títulos de janela, docs, guias, **comentários/docstrings** |
| `CNC_BatchEditor` | `FlowNC` | `build_exe.ps1` (`--name`), nome do EXE e da pasta `dist\` |
| `cnc-batch-editor` | `flownc` | `pyproject.toml` (`[project] name`) |
| `cnc_batch_editor` (pasta) | `flownc` (pasta) | raiz do projeto |

> **Rename da pasta — risco real é baixo** (premissa verificada acima). O único efeito é o `.venv`, recriado na Fase 6.
> A pasta-raiz `Sistema_verificador_codigos_cnc` **permanece** — divergência consciente do produto "FlowNC"; **motivo documentado** no `docs\README.md` (L5/M11): evitar quebrar caminhos da memória/`Desktop\CLAUDE.md`.

---

## 2. Estrutura-alvo da documentação (enxuta + entrada única)

```
docs\
├── README.md       ← ENTRADA ÚNICA. Visão geral + "para X, leia Y" + como rodar/buildar/testar + nota do mismatch de nome da pasta-raiz.
├── CONTEXTO.md     ← estado atual + próximos passos (substitui 00-HANDOFF + STATUS.md).
├── DECISOES.md     ← decisões travadas, estilo ADR enxuto. PRESERVA a numeração #1..#5 do antigo 10-PLANO §0.
├── PRODUTO.md      ← dinâmica "por código" + design do painel **2 colunas** (funde 08 + 09; 3 colunas marcado como SUPERADO).
├── PRD.md          ← especificação formal enxuta (era 02-PRD v2.3), nome FlowNC.
├── PLANO.md        ← roadmap das 4 mudanças OpenSpec (era 10-PLANO, atualizado).
└── CHANGELOG.md    ← NOVO: linha de rebrand FlowNC + bump de versão (M11).
mockups\
└── painel-final.html  ← era 12-mockup-bancada-resumo-dominante.html (o único vigente, 2 colunas).
_descarte\
├── _INDICE.md      ← tabela: arquivo → motivo → o que foi aproveitado e para onde. Desambigua 08/09 `.md` (sintetizados) × `.html` (descartados).
└── (arquivos obsoletos movidos para cá)
```

**Regra anti-desperdício:** o agente lê **só o `docs\README.md`** e ele aponta o que abrir conforme a tarefa.

### Fontes de síntese (de → para)
- `00-HANDOFF.md` + `cnc_batch_editor\STATUS.md` → `docs\CONTEXTO.md`
- decisões do handoff + `10-PLANO §0` → `docs\DECISOES.md` (**manter os IDs #1/#2/#5** citados pela change OpenSpec)
- `08-WORKFLOW-NOVA-DINAMICA.md` + `09-DESIGN-3-COLUNAS.md` → `docs\PRODUTO.md` — **na síntese, marcar 3 colunas como superado pelo mockup 12 (2 colunas / resumo dominante)** (M7/P8).
- `02-PRD_..._v2.3.md` (enxugado) → `docs\PRD.md`
- `10-PLANO-EXECUCAO-3-COLUNAS.md` (atualizado FlowNC) → `docs\PLANO.md`

### Para `_descarte\` (após extrair a essência) — contagem precisa
Docs (9): `01-Descrição-Problema` · `02-PRD_v2.0` (superado) · `03-REVISAO` · `04-PLANO-MELHORIAS` (concluído) · `05-PLANO-UI-UX` (superado) · `06-ANALISE-UX-WORKFLOW` (superado) · `07-PROMPT-PESQUISA-UI` (one-off) · `sugestoes...v2.0` · `Comandos.txt` (vazio).
Mockups (6): `06-mockup-ux.html` · `06-prototipo-navegavel.html` · `08-mockup-validado.html` · `09-mockup-opcoes-indicador.html` · `10-mockup-fluxo-codigo.html` · `11-mockup-3-colunas-estados.html` *(os "06" são DOIS arquivos distintos)*.
Build morto (1): `cnc_batch_editor\CNC_BatchEditor.spec` → `_descarte\` (regenerável, mas preserva histórico de paths; M10/P7).
Saída velha (1): `cnc_batch_editor\exemplo_lote\` inteiro — **mover só após o gate de grep confirmar que nenhum teste o referencia**.

### Dados de teste/reais — mantidos (fora do escopo do rename)
- `prog\` (programas CNC reais, ~7 MB) → **manter**.
- `cnc_batch_editor\programas_teste\` (fixtures `.nc`) → **manter**.

---

## 3. Fases de execução (ordem à prova de erro)

### Fase 0 — Baseline, git, lock e backup
- [ ] **`git init` + commit da baseline** (M1/P1) — rollback atômico grátis; criar `.gitignore` (`.venv/`, `build/`, `dist/`, `*cache*/`).
- [ ] **`pip freeze > requirements.lock`** com o venv atual intacto (M2/P2) — congela mypy 2.1.0 / PySide6 6.11.1 / pyinstaller 6.20.0 / pytest 9.0.3.
- [ ] Rodar `pytest -q` e **registrar a contagem exata** de testes como baseline (M9/P10) — comparar **delta=0** depois (não "≥106" fixo).
- [ ] **Backup especificado** (M6/L1-L2): cópia **zip** num **local FORA da árvore do projeto**, **excluindo** `.venv\`, `build\`, `dist\`(*ver P6 abaixo*), `*cache*`, `prog\`; **testar a restauração** num diretório temporário antes de seguir.
- [ ] **P6/M5:** incluir o `dist\CNC_BatchEditor\` atual (EXE bom) **no backup** (ou preservá-lo até o `FlowNC.exe` novo passar no smoke da F6) — fallback do último executável funcional.

### Fase 1 — Descarte (não-destrutivo)
- [ ] Criar `_descarte\` + `_INDICE.md` (tabela rastreável, contagem da §2, desambiguação 08/09 `.md`×`.html`).
- [ ] **Mover** (não apagar) os obsoletos da §2 para `_descarte\` (inclui o `.spec`; `exemplo_lote` só após gate de grep).

### Fase 2 — Síntese da nova documentação
- [ ] Escrever `docs\README/CONTEXTO/DECISOES/PRODUTO/PRD/PLANO/CHANGELOG.md` já com nome **FlowNC**.
- [ ] `DECISOES.md` **preserva os IDs #1..#5**; `PRODUTO.md` marca **3 colunas como superado** pelas 2 colunas (M7).
- [ ] `README.md` documenta o **mismatch** pasta-raiz × FlowNC (M11/L5).
- [ ] `CHANGELOG.md` + **bump de versão** no `pyproject.toml` (M11/L4).
- [ ] Mover/renomear `mockups\12-...html` → `mockups\painel-final.html`.

### Fase 3 — Renomear conteúdo (código/config/guias/memória) — **sem mexer na pasta ainda**
- [ ] `main.py`, `cli.py`, `core\__init__.py`, `ui\main_window.py`: nome de exibição → FlowNC, **incluindo comentários/docstrings** (`main.py` L1/L43, `main_window.py` L1/L128, `cli.py` L1/L143, `__init__.py` L1).
- [ ] `pyproject.toml`: `name = "flownc"` + descrição + **bump de versão** + (opcional) extra `[project.optional-dependencies] build = ["pyinstaller"]` (M11; relacionado a P2).
- [ ] `build_exe.ps1`: `--name FlowNC`, caminhos `dist\FlowNC`, mensagens.
- [ ] `PORTATIL_LEIA-ME.txt`: nome FlowNC + **nota de migração de presets** (operador com EXE antigo deve copiar seus `data\presets\*.json` para a pasta nova) (M11/L3).
- [ ] `GUIA-DE-USO.md`: nome FlowNC.
- [ ] `openspec\config.yaml` (linha de contexto) → FlowNC.
- [ ] **Mudança OpenSpec ativa** (`motor-retirar-contagem-e-publicacao`): **manter aberta** e **atualizar os ponteiros** em **`proposal.md`** (cita 08 e 10), **`design.md`** (cita 10 §0 / #1#2#5) e **`tasks.md`** (cita 00-HANDOFF) → novos `docs\`. **Não** listar `specs/` (não tem ref) (M4/P3). Refs por ID de decisão continuam válidas (DECISOES.md preserva a numeração).
- [ ] `app_paths.py`: **verificado — sem mudança** (não contém o nome do app; marca a varredura como completa).
- [ ] **`Desktop\CLAUDE.md`:** **confirmar existência/escopo antes** (é externo ao repo) (L6); se existir, atualizar nome FlowNC + caminhos de doc.
- [ ] Memória: `MEMORY.md` (índice + links `[[...]]`) + `cnc-batch-editor-estado.md` (**slug mantido**, conteúdo atualizado para FlowNC; L7) → nome FlowNC, novos caminhos de doc, **e corrigir o nome da change** `motor-retirar-e-contagem` → `motor-retirar-contagem-e-publicacao`.

### Fase 4 — Verificação intermediária (gate)
- [ ] `pytest` → **delta=0** vs. baseline da F0.
- [ ] `mypy --strict` limpo. **Cobertura declarada:** o `[tool.mypy]` só cobre `core/` (M8/P4). Para esta verificação, **ampliar temporariamente `files` para incluir `main.py`/`ui`/`cli.py`** e rodar uma vez (os arquivos editados), depois reverter. (venv ainda intacto.)
- [ ] (Opcional) `ruff check` — **só se ruff for instalado**; hoje não está no venv (M12/P9).

### GATE-5 — portão obrigatório antes da fase destrutiva (M3/P5)
> **Só prosseguir se TODOS abaixo = OK.** Se algum falhar, PARAR aqui (nome já trocado, pasta/venv intactos).
- [ ] (a) Backup restaurável **testado** (Fase 0) — confirmado.
- [ ] (b) **Internet OK** + `pip download` dry-run das deps do lock funciona (garante que a F6 conseguirá reinstalar).
- [ ] (c) **Git baseline** commitado e limpo (`git status` sem pendências não intencionais).

### Fase 5 — Renomear pasta + limpar gerados (DESTRUTIVA — venv quebra de propósito)
- [ ] Renomear `cnc_batch_editor\` → `flownc\`.
- [ ] `CNC_BatchEditor.spec` **já foi para `_descarte\`** na Fase 1 (M10/P7) — não há "delete" aqui.
- [ ] Deletar o `.venv` antigo (caminhos absolutos inválidos; puramente regenerável) e limpar gerados: `build\`, `.mypy_cache\`, `.pytest_cache\`, `__pycache__\`. **`dist\` antigo: NÃO apagar ainda** — preservar até o smoke da F6 (M5/P6).

### Fase 6 — Recriar ambiente, dados e EXE
- [ ] Recriar venv **a partir do lock** (M2/P2): `py -m venv .venv` → `pip install -r requirements.lock`.
  - *NÃO usar `pip install -e .`* — layout plano sem `[build-system]` falha com "Multiple top-level packages". **Requer internet** (já validado no GATE-5).
- [ ] (Opcional, independente do rename) recriar/limpar os JSON de `data\` — conteúdo não muda por causa do nome.
- [ ] `pytest` → **delta=0** vs. baseline; `mypy --strict` limpo (mesma cobertura ampliada da F4).
- [ ] `build_exe.ps1` → gerar `dist\FlowNC\FlowNC.exe`; **smoke test (abre/fecha limpo)**.
- [ ] **Só depois do smoke OK:** remover o `dist\CNC_BatchEditor\` antigo (M5/P6).

### Fase 7 — Fechamento
- [ ] Varredura final de verificação (DoD §5).
- [ ] Atualizar `docs\CONTEXTO.md`, `CHANGELOG.md` e a memória com o estado final.
- [ ] **Commit final no git**; mover este `PLANO-RENAME-FLOWNC.md` para `_descarte\` ou `docs\` como histórico curto.

---

## 4. Riscos e mitigações

| Risco | Mitigação |
|---|---|
| **Sem git → rollback impossível** (P1) | `git init` + commit baseline na F0 (M1); rollback via `git restore`/branch. |
| **Venv recriado com versão nova quebra o gate sozinho** (P2) | `requirements.lock` na F0; instalar do lock na F6 (M2). |
| **Internet/pip falha após a fase destrutiva** (P5) | **GATE-5** (internet + `pip download` dry-run) antes da Fase 5; senão, parar na F4. |
| **EXE bom apagado e build novo falha** (P6) | Backup do `dist\` na F0 + preservar `dist\` antigo até o smoke da F6 (M5). |
| **Change OpenSpec com ponteiro pendurado** (P3) | Atualizar `proposal.md`+`design.md`+`tasks.md` (não `specs/`); preservar IDs #1/#2/#5 (M4). |
| **mypy "limpo" não cobre os arquivos editados** (P4) | Ampliar `files` na verificação (F4/F6) ou declarar a limitação (M8). |
| **Síntese reintroduz layout 3 colunas abandonado** (P8) | `PRODUTO.md` marca 3 col como superado por 12 (2 col); desambiguar `.md`×`.html` no índice (M7). |
| **Backup inútil/lento** (L1-L2) | Local externo + zip + exclusões + **teste de restauração** (M6). |
| Editable install (`pip install -e .`) falha (layout plano) | Instalar do lock; editable só após `[build-system]`+`[tool.setuptools]`. |
| Backup lento / caminho longo no Windows | Excluir `.venv/build/caches/prog` do backup (F0). |
| Perder info útil ao descartar | Mover (não apagar) + `_INDICE.md` + síntese revisada antes. |
| `exemplo_lote` referenciado por teste | Gate de grep antes de mover (F1). |
| Regressão silenciosa | `pytest` (delta=0) + `mypy` nas Fases 0/4/6. |

---

## 5. Definição de pronto (DoD)
- [ ] **Varredura de verificação com escopo definido** — `CNC Batch Editor` / `CNC_BatchEditor` / `cnc_batch_editor` zero ocorrências em **código + docs + config**, **excluindo** `.venv\`, `build\`, `dist\`, `*cache*`, `prog\`, `_descarte\`.
- [ ] Git inicializado, baseline e commit final presentes; backup externo testado.
- [ ] `requirements.lock` criado e usado para recriar o venv.
- [ ] `docs\` enxuto com entrada única; obsoletos em `_descarte\` com índice (08/09 `.md`×`.html` desambiguados; `.spec` movido, não deletado).
- [ ] `PRODUTO.md` reflete **2 colunas** (3 colunas marcado como superado); memória atualizada.
- [ ] Change OpenSpec ativa com ponteiros válidos (`proposal/design/tasks`; IDs de decisão preservados).
- [ ] `pytest` **delta=0** vs. baseline; `mypy --strict` limpo (cobertura ampliada para os arquivos editados ou limitação declarada).
- [ ] `dist\FlowNC\FlowNC.exe` gerado e abrindo; `dist\` antigo removido só após o smoke OK.
- [ ] `CHANGELOG.md` + bump de versão; nota de migração de presets no `PORTATIL_LEIA-ME`.
- [ ] Memória + (se existir) `Desktop\CLAUDE.md` atualizados para FlowNC (inclui correção do nome da change).
