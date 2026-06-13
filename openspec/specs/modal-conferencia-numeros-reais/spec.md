# modal-conferencia-numeros-reais Specification

## Purpose
TBD - created by archiving change plano-execucao-mockup-v4. Update Purpose after archive.
## Requirements
### Requirement: Modal de Conferência abre ao clicar "Conferir lote"

O sistema SHALL abrir um `QDialog` **bloqueante** ("Conferência do lote — números reais") ao clicar no CTA "Conferir lote →". O modal SHALL varrer os programas marcados com as edições do lote usando `build_plan` + `count_occurrences` do `core/`, exibindo os resultados **antes de qualquer gravação**. O modal NOT SHALL fechar ao clicar fora durante a varredura.

#### Scenario: Modal abre ao clicar "Conferir lote"

- **WHEN** o usuário clica em "Conferir lote →" com edições e programas marcados
- **THEN** o modal "Conferência do lote — números reais" é aberto e exibe o indicador de varredura em andamento

#### Scenario: Varredura usa o mesmo motor do Lote

- **WHEN** a varredura da Conferência é concluída
- **THEN** os números exibidos no modal são calculados pelo mesmo `build_plan` + `count_occurrences` que seria usado na publicação

### Requirement: Faixa de resumo da decisão

O modal SHALL exibir no topo uma **faixa verde** com número grande (total de alterações) e o texto "alterações em X de Y programas marcados · N trocas · bloco em M programas · nada foi gravado ainda". Se total = 0, a faixa SHALL ser **âmbar** com "nenhuma alteração encontrada".

#### Scenario: Faixa verde com alterações encontradas

- **WHEN** a varredura encontra ao menos uma alteração
- **THEN** a faixa é verde com o total em destaque e o texto descritivo

#### Scenario: Faixa âmbar sem alterações

- **WHEN** a varredura não encontra nenhuma alteração
- **THEN** a faixa é âmbar com "nenhuma alteração encontrada"

### Requirement: Avisos de conflito e edições sem efeito

O modal SHALL listar **avisos** logo abaixo da faixa: conflitos ("▲ Conflito: M8 é alterado por mais de uma edição") e edições sem efeito ("⚠ M5 não aparece em nenhum programa marcado").

#### Scenario: Aviso de conflito exibido

- **WHEN** há dois cartões com a mesma origem no lote
- **THEN** o modal exibe o aviso "▲ Conflito: [código] é alterado por mais de uma edição"

#### Scenario: Aviso de sem efeito exibido

- **WHEN** uma edição do lote não encontra o código em nenhum programa marcado
- **THEN** o modal exibe "⚠ [código] não aparece em nenhum programa marcado"

### Requirement: Cartão por edição com programas afetados e exemplo real

O modal SHALL exibir **um cartão por edição** com: fórmula no cabeçalho, total ("11 trocas em 4 programas"), lista **apenas dos programas afetados** com contagem individual. Programas com zero ocorrência SHALL ser recolhidos numa linha coletiva ("+ N programas sem [código] — nada muda"). Cada cartão de troca SHALL mostrar um **exemplo real**: linha original riscada → linha nova, com nome do arquivo e número da linha.

#### Scenario: Cartão mostra apenas programas afetados

- **WHEN** a varredura encontra M8 em 3 dos 5 programas marcados
- **THEN** o cartão de M8→M08 lista os 3 programas afetados com suas contagens e "+ 2 programas sem M8 — nada muda" recolhido

#### Scenario: Exemplo real com linha original e nova

- **WHEN** a varredura encontra M8 no arquivo PECA_01.NC linha 15
- **THEN** o cartão exibe a linha 15 original riscada e a linha modificada, com o nome e número da linha

### Requirement: Linha de backup no modal

O modal SHALL exibir a linha: "🛡 Ao publicar: originais vão para `[pasta]` (versionado por data/hora) · gravação com conferência dupla" com botão para **trocar a pasta** de backup. A troca SHALL atualizar o chip de backup no topo global.

#### Scenario: Linha de backup sempre visível no modal

- **WHEN** o modal de conferência está aberto
- **THEN** a linha de backup com o caminho configurado está visível

#### Scenario: Trocar pasta de backup no modal atualiza o chip global

- **WHEN** o usuário clica em trocar pasta dentro do modal e confirma um novo destino
- **THEN** o chip de backup no topo é atualizado com o novo caminho

### Requirement: Rodapé fixo com botão de Publicar

O modal SHALL ter um rodapé **fixo (não rola)** que repete o veredito e exibe o botão de ação:
- Sem problemas → botão laranja **"Publicar — N trocas · bloco em M programas"**.
- Com conflito → botão âmbar **"Publicar mesmo assim — …"** com aviso no rodapé.
- Total 0 → botão desabilitado "Nada a publicar".

#### Scenario: Botão laranja sem conflitos

- **WHEN** a varredura conclui sem conflitos e total > 0
- **THEN** o rodapé exibe botão laranja "Publicar — [N] trocas …" habilitado

#### Scenario: Botão âmbar com conflitos

- **WHEN** a varredura encontra conflitos
- **THEN** o rodapé exibe aviso de conflito e o botão âmbar "Publicar mesmo assim — …"

#### Scenario: Botão desabilitado sem alterações

- **WHEN** total de alterações é 0
- **THEN** o botão "Nada a publicar" está desabilitado

