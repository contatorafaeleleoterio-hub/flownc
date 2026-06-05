# Decisoes

## Decisões do roadmap de produto

| ID | Decisão |
| --- | --- |
| `#1` | Fazer varredura prévia de ocorrências por arquivo em segundo plano. |
| `#2` | Em `Retirar`, remover o código, limpar espaços e apagar a linha se ela ficar vazia por causa da remoção. |
| `#3` | Implementar a nova interface em fases, atacando primeiro a fatia de Substituir. |
| `#4` | Adotar biblioteca de códigos orientada a catálogo, com migração do perfil atual. |
| `#5` | Publicar o editado direto na pasta de trabalho e mandar os originais para backup versionado, com troca atômica. |

## Decisões do rebrand FlowNC

- Nome de exibição adotado: `FlowNC`.
- Nome técnico/distribuição adotado: `FlowNC`.
- Nome de pacote/projeto adotado: `flownc`.
- Pasta de código adotada: `flownc/`, com venv recriado a partir de `requirements.lock`.
- Manter a pasta-raiz `Sistema_verificador_codigos_cnc/` para preservar referências externas já em uso.
- Não apagar histórico de imediato: mover o obsoleto para `_descarte/`.
