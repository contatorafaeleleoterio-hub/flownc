## ADDED Requirements

### Requirement: Validação de segurança do lote

O sistema SHALL validar um lote de regras antes da execução e devolver uma lista de problemas (`Issue`), cada um com severidade. A validação MUST cobrir: (1) **conflito de regra** — duas ou mais regras agindo sobre o **mesmo código de origem** (severidade âmbar/aviso); (2) **limite de Retirar** — no máximo **uma** regra de ação RETIRAR por execução (severidade crítica/bloqueia); (3) **allowlist** — toda regra de Retirar MUST referenciar um código presente na biblioteca (severidade crítica/bloqueia). Esse "conflito de regra" MUST ser distinto do "conflito de pedaço" (`Suppression`), que o motor resolve sozinho durante o plano.

#### Scenario: Conflito de regra avisa em âmbar

- **WHEN** o lote tem duas regras cujo código de origem é `M8`
- **THEN** `validate_batch` retorna um `Issue` de aviso (âmbar) apontando o conflito de regra

#### Scenario: Mais de um Retirar bloqueia

- **WHEN** o lote tem duas regras de ação RETIRAR
- **THEN** `validate_batch` retorna um `Issue` crítico (limite de 1 Retirar por execução)

#### Scenario: Retirar fora da allowlist bloqueia

- **WHEN** uma regra de Retirar referencia um código que não está na biblioteca
- **THEN** `validate_batch` retorna um `Issue` crítico (allowlist)

#### Scenario: Lote válido não gera problemas

- **WHEN** o lote tem regras de Substituir em códigos distintos e no máximo um Retirar de código válido
- **THEN** `validate_batch` retorna lista vazia

#### Scenario: Conflito de regra ≠ conflito de pedaço

- **WHEN** duas regras tocam o mesmo trecho de bytes mas têm códigos de origem diferentes
- **THEN** isso é tratado como conflito de **pedaço** (resolvido por `Suppression`), e **não** é reportado por `validate_batch` como conflito de regra
