# FlowNC

Entrada única da documentação do projeto.

## O que é

FlowNC é o app desktop Windows para edição em lote de programas CNC: substituições controladas por regras, editor integrado por arquivo, preview, verificações e preservação rastreável do material original. Design de referência: `mockups/painel-final.v2.html`.

## Onde estamos

- O código agora vive na pasta `flownc/`.
- A pasta-raiz do projeto continua `Sistema_verificador_codigos_cnc/` por decisão consciente, para não quebrar referências externas e memória operacional já existente.
- Baseline técnica: **`146` testes `pytest` aprovados (2026-06-07)** no venv `flownc/.venv` (PySide6 6.11.1), congelado em `requirements.lock`.

## Para cada assunto, leia

- Estado atual, retomada e próximos passos: `docs/CONTEXTO.md`
- Decisões travadas do produto, design e rebrand: `docs/DECISOES.md`
- Dinâmica do produto e interface final (mockup v2): `docs/PRODUTO.md`
- Especificação formal enxuta: `docs/PRD.md`
- Plano de execução vivo: `PLAN.md` (raiz) · estado entre sessões: `HANDOFF.md` (raiz)
- Histórico de mudanças relevantes: `docs/CHANGELOG.md`

## Como rodar

```powershell
cd flownc
.\.venv\Scripts\python.exe main.py
.\.venv\Scripts\python.exe -m pytest -q
powershell -ExecutionPolicy Bypass -File build_exe.ps1
```

## Build portátil

O build gera `dist/FlowNC/FlowNC.exe`. O `dist` antigo fica preservado apenas até o smoke test do novo executável.
