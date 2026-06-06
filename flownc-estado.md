# Estado FlowNC

## Atual

- Produto: FlowNC.
- Pasta de codigo: `flownc/`.
- Documentacao ativa: `docs/README.md` como entrada unica.
- Mockup v2 `mockups/painel-final.v2.html`: **construído e aprovado**.
- Editor integrado por arquivo: **implementado** (`core/inplace_save.py` + `ui/editor_panel.py` + integração no `main_window`).
- EXE novo: **gerado** em `flownc/dist/FlowNC/FlowNC.exe` (contém o editor). Atenção: ainda tem o **visual antigo** — o redesenho v2 não foi feito.
- OpenSpec pendente: `motor-contagem-e-publicacao` (proposta+validada; renomeada — a parte "Retirar" saiu do escopo).
- **Plano de execução vigente: `PLAN.md` (raiz).** Termos e definições em `docs/CONTEXTO.md`.
- **Design antigo: descartado.** Única referência válida é o mockup v2 (`mockups/painel-final.v2.html`).

## Proximo passo imediato

**Redesenho visual do app conforme o mockup v2.** A função de editar já existe, mas o visual
novo nunca foi construído — por isso o app "pronto" ainda parece o antigo.

Plano (esqueleto, sessões → etapas) em **`docs/PLANO-REDESIGN-VISUAL-V2.md`**. Decisões fechadas:
- **Componentes separados** em `flownc/ui/components/` (quebrar a `MainWindow` monolítica).
- **Fluxo OpenSpec**, dividido em **3 mudanças sequenciais**: A) fundação visual (tokens/tema),
  B) layout e painéis (header + 2 colunas + esquerda + direita), C) editor + limpeza + build.

Próxima ação concreta: **Sessão 0 da Mudança A** — criar a proposta OpenSpec da fundação visual.
Antes disso, o plano ainda será refinado (detalhar etapas).

A remoção da contagem automática (parte do redesenho, Sessão 6) converge com a change
`motor-contagem-e-publicacao`, que deve ser retomada depois.

## Gate pendente (não bloqueante)

Smoke test manual do `dist/FlowNC/FlowNC.exe`; entrega de uma cópia limpa na Área de Trabalho
e afastamento da versão antiga (`Desktop/CNC_BatchEditor/`, de 2026-06-01) só ao final do redesenho.
