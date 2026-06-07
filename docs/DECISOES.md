# Decisoes

## Decisões do roadmap de produto

| ID | Decisão |
| --- | --- |
| `#1` | Não há varredura/contagem automática no painel principal: contagem é função do editor integrado (varredura sob demanda). _Supera a decisão anterior de varredura prévia em segundo plano._ |
| `#2` | A ação separada `Retirar` foi **descartada**: remoção de código é feita por substituição-por-vazio no mesmo fluxo de regras. A remoção limpa espaços e apaga a linha se ela ficar vazia. |
| `#3` | Implementar a nova interface em fases (OpenSpec), atacando primeiro a fundação visual, depois layout/painéis, depois editor/limpeza/entrega. |
| `#4` | Adotar biblioteca de códigos orientada a catálogo, com migração do perfil atual. |
| `#5` | Publicar o editado direto na pasta de trabalho e mandar os originais para backup versionado, com troca atômica e dupla conferência SHA-256. |

## Decisões de design (mockup v2 aprovado)

| ID | Decisão |
| --- | --- |
| `#6` | Design de referência único: `mockups/painel-final.v2.html`. O mockup `painel-final.html` e o conceito de 3 colunas estão **descartados** (só histórico). |
| `#7` | Layout em **2 colunas dinâmicas**: ~60/40 no modo padrão e ~40/60 quando o editor abre (coluna direita expande), com transição suave. |
| `#8` | Compositor de edições em **lista única** ("Edições montadas") com linha de rascunho "em edição", `✕` por linha e `+ adicionar outra edição`. |
| `#9` | Coluna direita alterna **Resumo ↔ Editor integrado** (QStackedWidget). |
| `#10` | Design 100% por tokens (`theme.py` + QSS central); tipografia IBM Plex Sans/Mono, com fallback Segoe UI/Consolas. |
| `#11` | O editor por arquivo salva **direto, sem backup** (proposital, para ajuste manual rápido); o backup versionado vale para a publicação em lote. |

## Decisões do rebrand FlowNC

- Nome de exibição adotado: `FlowNC`.
- Nome técnico/distribuição adotado: `FlowNC`.
- Nome de pacote/projeto adotado: `flownc`.
- Pasta de código adotada: `flownc/`, com venv recriado a partir de `requirements.lock`.
- Manter a pasta-raiz `Sistema_verificador_codigos_cnc/` para preservar referências externas já em uso.
- Não apagar histórico de imediato: mover o obsoleto para `_descarte/`.
