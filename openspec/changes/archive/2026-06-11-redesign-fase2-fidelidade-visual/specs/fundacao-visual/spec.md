## MODIFIED Requirements

### Requirement: Tokens de design em theme.py

O sistema SHALL expor todos os tokens visuais do mockup `painel-final.v2.html` **aprovado na FASE 1** como constantes Python em `flownc/ui/theme.py`, cobrindo: cores (`COLOR_*`), tipografia (`T_*`), espaçamentos (`SP_*`), raios (`RADIUS_*`), alturas (`H_*`), dimensões (`DIM_*`) e sombras (`SHADOW_*`/`METAL`). Os valores SHALL corresponder **exatamente** às variáveis CSS `--color-*`, `--t-*`, `--sp-*`, `--radius-*`, `--h-*`, `--dim-*` declaradas no protótipo (sincronização 1:1). O módulo MUST ser importável sem instanciar QApplication.

#### Scenario: Importação sem QApplication

- **WHEN** o módulo `flownc.ui.theme` é importado em contexto sem display Qt
- **THEN** a importação sucede sem levantar exceção e todas as constantes estão acessíveis

#### Scenario: Tokens de cor presentes e sincronizados com o protótipo

- **WHEN** o módulo `flownc.ui.theme` é inspecionado
- **THEN** as constantes `COLOR_BG_BASE`, `COLOR_TEXT_PRIMARY`, `COLOR_INTERACTIVE`, `COLOR_SUCCESS`, `COLOR_WARNING`, `COLOR_DANGER`, `COLOR_CTA_START`, `COLOR_OCCURRENCE` e `COLOR_OCCURRENCE_CURRENT` existem com valores hexadecimais idênticos aos do protótipo aprovado

#### Scenario: Tokens de tipografia e espaçamento presentes

- **WHEN** o módulo `flownc.ui.theme` é inspecionado
- **THEN** as constantes de tipografia (`T_FAMILY_SANS`, `T_FAMILY_MONO`, `T_SIZE_BASE`, `T_SIZE_CAPTION`) e de espaçamento (`SP_XS`, `SP_SM`, `SP_MD`, `SP_LG`) existem com valores numéricos corretos
