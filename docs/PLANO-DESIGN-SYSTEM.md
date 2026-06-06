# Plano — Refinar e padronizar o Design System do painel FlowNC

> Criado em: 2026-06-05
> Status: **APROVADO — aguardando execução**
> Próxima sessão: começar pela **Etapa 1**

---

## Contexto

O layout e o posicionamento dos blocos do painel (`mockups/painel-final.html`, design B / 2 colunas) já estão **aprovados**. O que falta é **padronizar a apresentação**: hoje há desalinhamentos, deslocamentos visuais, espaçamentos inconsistentes e áreas com excesso de informação/redundância, gerando sobrecarga visual.

**Objetivo:** deixar o painel mais limpo, alinhado e fácil de usar — **mantendo todas as funcionalidades** — adotando uma folha de tokens (padrão **IBM Carbon**, que combina com a fonte IBM Plex já usada) aplicada pelo Claude na conversa, **sem instalar nada por terminal**.

**Regras travadas neste trabalho:**
- Mexer **só no mockup HTML** agora. O app Qt/PySide6 (`flownc/`) e o `core/` **não** são tocados — porte para QSS é etapa futura separada.
- **Original preservado**: nunca sobrescrever `painel-final.html`; trabalhar em cópia.
- **Sem screenshot** sem "sim" explícito do Rafael.
- **Pausa ao fim de cada etapa** para aprovação antes de seguir.

---

## Etapa 1 — Auditoria (diagnóstico, somente leitura)

Ler `mockups/painel-final.html` por completo e produzir um **relatório de diagnóstico** (em markdown, para aprovação). Nada é alterado.

Conteúdo do relatório:
1. **Mapa estrutural** — lista de cada bloco/seção do layout 2 colunas (compositor, lista de programas, resumo, botões, pop-up), com a hierarquia.
2. **Sistema de estilo atual** — como o CSS está organizado (inline, `<style>`, se usa variáveis CSS).
3. **Inventário de valores de fato usados** (expõe inconsistência): todos os espaçamentos distintos, tamanhos e pesos de fonte, cores e border-radius distintos.
4. **Lista numerada de problemas concretos**, cada um com *onde* + *o quê* + *valor*:
   - Desalinhamentos e deslocamentos visuais.
   - Espaçamentos fora de escala.
   - Inconsistências de apresentação (botões/cantos/cores quase-iguais/pesos aleatórios).
   - Excesso de informação / redundância / conteúdo desnecessário.
5. **Inventário de funcionalidades** que NÃO podem ser perdidas (dropdown de código, toggle Substituir/Retirar, abrir pasta, varredura/contagem, cartões de regra editar/duplicar/excluir, aviso de conflito, Executar, pop-up resumo, Salvar).

**Entrega:** relatório de diagnóstico. **Pausa para aprovação.**

---

## Etapa 2 — Folha de tokens (no papel, sem código)

Definir os padrões visuais com base no **IBM Carbon**, adaptados ao painel. Apresentado como tabelas para aprovação dos números **antes** de aplicar.

1. **Espaçamento** — escala única (grade 2x do Carbon): 2, 4, 8, 12, 16, 24, 32, 40, 48 px. Todo padding/margin/gap passa a usar só esses valores.
2. **Tipografia** — escala com IBM Plex Sans (interface) e IBM Plex Mono (código): tamanhos, pesos e altura de linha definidos (legenda, corpo, rótulo, título).
3. **Cor** — tokens nomeados: fundos em camadas, texto primário/secundário, bordas, cor interativa (botão), conflito/erro (destaque) e sucesso.
4. **Componentes** — regras fixas: altura de botão, altura de campo, recuo (padding) dos cartões, border-radius único, espessura de borda, anel de foco.

E um **mapa "problema → token que resolve"**: cada item da Etapa 1 ligado ao token/regra que o corrige.

**Entrega:** tabela de tokens + mapa de correções. **Pausa para aprovação.**

---

## Etapa 3 — Aplicar numa CÓPIA do mockup

Após o "sim" da Etapa 2:
1. Criar **`mockups/painel-final.v2.html`** — o `painel-final.html` original fica intacto.
2. Refatorar o CSS para um único bloco de variáveis (`:root`) com os tokens aprovados.
3. Aplicar as correções da Etapa 1: alinhar elementos, normalizar espaçamentos/componentes, e **remover redundâncias/sobrecarga mantendo 100% das funcionalidades** do inventário.

**Entrega:** arquivo `v2` pronto para abrir no navegador e comparar lado a lado com o original. **Pausa para aprovação.**

---

## Arquivos

| Ação | Arquivo |
|------|---------|
| Lê (Etapa 1) | `mockups/painel-final.html` |
| Cria (Etapa 3) | `mockups/painel-final.v2.html` ← novo; original preservado |
| Não toca | `flownc/` (app Qt), `core/`, qualquer `.qss`, OpenSpec |

## Verificação

- Abrir `painel-final.v2.html` no navegador e comparar com o original lado a lado.
- Checklist de funcionalidades: confirmar que todos os itens do inventário da Etapa 1 continuam presentes e operáveis.
- Conferir visualmente: alinhamentos corrigidos, espaçamentos só na escala definida, sem áreas sobrecarregadas.

## Fora de escopo (etapas futuras, NÃO neste plano)

- Portar os tokens para o QSS do app Qt (`flownc/ui/`).
- Implementar as mudanças OpenSpec de UI (Mudanças 3a/3b).

---

## Referência de pesquisa

Padrão adotado: **IBM Carbon Design System** (Apache 2.0, 9,2k★, v11.109.0 de 2026-06-03, usa IBM Plex — mesma fonte do projeto).
Motor de entrega: skill `design-system` do Claude (sem instalação por terminal).
