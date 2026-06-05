# FlowNC

Entrada única da documentação do projeto.

## O que é

FlowNC é o app desktop Windows para substituições controladas em programas CNC, com preview, verificações e preservação rastreável do material original.

## Onde estamos

- O código agora vive na pasta `flownc/`.
- A pasta-raiz do projeto continua `Sistema_verificador_codigos_cnc/` por decisão consciente, para não quebrar referências externas e memória operacional já existente.
- Baseline técnica em 2026-06-04: `106` testes `pytest` aprovados e venv congelado em `requirements.lock`.

## Para cada assunto, leia

- Estado atual, retomada e próximos passos: `docs/CONTEXTO.md`
- Decisões travadas do produto e do rebrand: `docs/DECISOES.md`
- Dinâmica do produto e interface final: `docs/PRODUTO.md`
- Especificação formal enxuta: `docs/PRD.md`
- Roadmap de execução: `docs/PLANO.md`
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
