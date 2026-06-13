# Decisoes

## Decisões do roadmap de produto

| ID | Decisão |
| --- | --- |
| `#1` | Não há varredura/contagem automática no painel principal: contagem é função do editor integrado (varredura sob demanda). _Supera a decisão anterior de varredura prévia em segundo plano._ |
| `#2` | A ação separada `Retirar` foi **descartada**: remoção de código é feita por substituição-por-vazio no mesmo fluxo de regras. A remoção limpa espaços e apaga a linha se ela ficar vazia. |
| `#3` | Implementar a nova interface em fases (OpenSpec), atacando primeiro a fundação visual, depois layout/painéis, depois editor/limpeza/entrega. |
| `#4` | Adotar biblioteca de códigos orientada a catálogo, com migração do perfil atual. |
| `#5` | Publicar o editado direto na pasta de trabalho e mandar os originais para backup versionado, com troca atômica e dupla conferência SHA-256. |

## Decisões de design (mockup v4 aprovado — 2026-06-11)

> O **v4 (`mockups/painel-final.v4.html`) é o único contrato visual válido.** Ele **supera o v2**
> (`painel-final.v2.html`) e o conceito de 2 colunas dinâmicas. Mockups anteriores (`painel-final.html`,
> 3 colunas, v2) ficam só como histórico em `_descarte/`. Descrição completa: `docs/CONTEXTO-IA.md`.

| ID | Decisão |
| --- | --- |
| `#6` | Design de referência único: `mockups/painel-final.v4.html`. v2, `painel-final.html` e o conceito de 3 colunas estão **descartados** (só histórico). |
| `#7` | Navegação por **4 telas fixas num rail** (Lote · Editor · Códigos · Histórico) — "lugares, não modos". Substitui o layout de 2 colunas dinâmicas do v2. |
| `#8` | Tela Lote: compositor com **duas abas** ("Trocar código" e "➕ Inserir bloco") e **um único** `+ Adicionar ao lote`; lote de edições como lista única de cartões numerados. |
| `#9` | Conferência com **números reais** num modal (varredura simula o mesmo encadeamento da publicação) → publicação com backup versionado + dupla conferência SHA-256. CTA "Conferir lote" nunca grava. |
| `#10` | **Topo global** em todas as telas: seletor de configuração ("receita", com "Salvar lote atual como…") + chip de pasta de backup clicável. |
| `#11` | Design 100% por tokens (`theme.py` + QSS central); paleta "Precisão Laranja" (laranja `#E85D04` = ação); tipografia IBM Plex Sans/Mono embutida, fallback Segoe UI/Consolas. |
| `#12` | O editor por arquivo salva **direto, sem backup** (proposital, para ajuste manual rápido, com Desfazer); o backup versionado vale para a publicação em lote. |

## Decisões do rebrand FlowNC

- Nome de exibição adotado: `FlowNC`.
- Nome técnico/distribuição adotado: `FlowNC`.
- Nome de pacote/projeto adotado: `flownc`.
- Pasta de código adotada: `flownc/`, com venv recriado a partir de `requirements.lock`.
- Manter a pasta-raiz `Sistema_verificador_codigos_cnc/` para preservar referências externas já em uso.
- Não apagar histórico de imediato: mover o obsoleto para `_descarte/`.
