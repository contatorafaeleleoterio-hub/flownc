## MODIFIED Requirements

### Requirement: Barra de topo global persistente

O sistema SHALL exibir uma barra de topo (`TopBar`) fixa acima do `QStackedWidget`, visível em **todas as telas**. A barra SHALL conter o logotipo/nome "FlowNC" à esquerda e o chip de backup à direita. A barra NOT SHALL conter seletor de configuração/receita — salvar e abrir configurações são funções da tela Lote.

#### Scenario: Topo visível em todas as telas

- **WHEN** o usuário navega entre qualquer uma das 4 telas
- **THEN** a barra de topo permanece visível com o mesmo conteúdo (marca + chip de backup)

#### Scenario: Topo não tem seletor de configuração

- **WHEN** a barra de topo é exibida
- **THEN** não há nenhum seletor/dropdown de configuração ou receita no topo

## REMOVED Requirements

### Requirement: Seletor de configuração/receita

**Reason**: O seletor de receita no topo ("Máquina 1") era escondido e pouco usado, e misturava
"salvar" dentro de um dropdown. A função foi movida para a tela Lote como botões explícitos
("Salvar configuração" / "Abrir configuração"), especificados na capacidade `lote-configuracoes-salvas`.
**Migration**: Salvar/abrir configurações agora é feito pelos botões na linha do título "Lote de
edições". Presets antigos no diretório de receitas não são migrados automaticamente; o operador
recria a configuração pela tela Lote.
