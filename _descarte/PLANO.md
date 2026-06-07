# Plano

## Objetivo

Executar o rebrand para FlowNC e manter a continuidade do roadmap do produto sem perder histórico nem capacidade de rollback.

## Ordem macro

1. Baseline, git, lock e backup externo testado.
2. Descarte não destrutivo e consolidação da documentação.
3. Rename textual em código, docs, config, build e memória.
4. Gate técnico com `pytest` e `mypy`.
5. Rename destrutivo da pasta para `flownc/` e limpeza de gerados.
6. Recriação do venv a partir de `requirements.lock`.
7. Build do novo `FlowNC.exe`, smoke test e fechamento.

## Roadmap de produto em paralelo

- Mudança 1: motor para `Retirar`, varredura, validação de lote e publicação segura.
- Mudança 2: biblioteca código-cêntrica e migração.
- Mudança 3: interface principal da nova dinâmica.
- Mudança 4: completar `Retirar`, conflitos visuais e polimento.

As decisões `#1`, `#2` e `#5` seguem sendo a base do OpenSpec ativo.
