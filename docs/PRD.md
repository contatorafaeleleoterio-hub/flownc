# PRD

## Resumo

FlowNC é um app desktop para substituição e futura remoção controlada de códigos em programas CNC, com preview, verificações, persistência de presets e empacotamento portátil.

## Escopo atual validado

- Motor de substituição seguro com testes automatizados.
- Leitura e escrita preservando encoding e estrutura do arquivo.
- Presets, biblioteca e configurações persistidas em JSON.
- GUI PySide6 funcional para operação local.
- EXE portátil onedir para uso em ambiente Windows.

## Requisitos permanentes

- Preservação do original.
- Operação rastreável por log.
- Validação forte antes de salvar/publicar.
- Comportamento previsível para zero ocorrências, conflitos e batchs mistos.

## Próxima expansão funcional

As próximas mudanças planejadas em OpenSpec adicionam:

- ação `Retirar`;
- varredura/contagem prévia;
- validação de lote;
- publicação segura na pasta de trabalho com backup versionado.
