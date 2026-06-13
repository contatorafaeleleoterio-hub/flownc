## Context

A tela Lote (v4) tem duas colunas: **Programas** (esquerda, `ProgramListV4`) e **Lote de edições**
(direita, `LoteScreen` + `CompositorV4`). Hoje a `Edicao` (dataclass `frozen`) guarda só a troca
(origem/destino ou bloco) e **não** o conjunto de programas; a conferência usa
`program_list.get_marcados()` como conjunto **global** aplicado a todas as edições. Isso impede dar
feedback "quais programas recebem esta edição" e impede edições com escopos diferentes no mesmo lote.

A `Edicao` é `frozen` (imutável) e é reusada pelo `scan_lote`/`ConferenciaModal` e pelos testes
(`test_ui_smoke.py`) — qualquer campo novo precisa de default seguro para não quebrar chamadas
existentes.

## Goals / Non-Goals

**Goals:**
- Cada edição carrega seu próprio conjunto de programas (snapshot no "+ Adicionar ao lote").
- Cartão da edição mostra contagem de programas e abre dropdown com a lista; remoção individual de
  programa com **desfazer**.
- Origem/destino editáveis inline no cartão (clique abre o dropdown da biblioteca ali mesmo).
- Painel Programas ganha **"Desmarcar selecionados"**.
- Conferência/publicação respeitam o escopo por edição.

**Non-Goals:**
- Não mexer no núcleo de substituição (`core/matcher`, `inplace_save`, `publisher`) — só na forma
  como o conjunto de programas chega à varredura.
- Não redesenhar as abas do compositor nem o fluxo de "Inserir bloco" (bloco continua editável via
  compositor; inline vale para troca de código).
- Não atualizar mockup/`CONTEXTO-IA` nesta change (follow-up após aprovação visual do Mestre).

## Decisions

**1. `Edicao` ganha `programas: tuple[str, ...] = ()`.**
Tupla de caminhos (string) para manter o dataclass `frozen`/hashável; default vazio preserva todas
as chamadas atuais. `duplicada()` (via `replace`) copia o conjunto. Alternativa descartada: lista
mutável (quebra `frozen` e exige cuidado com aliasing).

**2. Snapshot no compositor, mutação na `LoteScreen`.**
`CompositorV4._montar_edicao` injeta `programas=tuple(str(p) for p in self._marcados)` ao adicionar.
Como `Edicao` é imutável, qualquer mudança posterior (remover programa, trocar origem/destino
inline) é feita pela `LoteScreen` substituindo o item: `self._edicoes[i] = replace(ed, ...)` +
re-render. Centraliza o estado em `LoteScreen` (mesma filosofia "MainWindow/telas como maestro").

**3. Edição inline reusa `LibDropdown`.**
No cartão de troca, origem e destino viram dois `LibDropdown` pequenos (`big=False`); destino com
`com_remover=True`. O sinal `alterado` atualiza a `Edicao` via `replace`. Mantém uma única
implementação de dropdown pesquisável (sem componente novo). O bloco (`ins`) continua mostrando o
resumo textual e usa ✎→compositor (inline de textarea não compensa).

**4. Dropdown de programas por cartão = popup com desfazer "riscar".**
Botão **"N programas ▾"** abre um `QFrame` popup (mesmo padrão do `LibDropdown._abrir_popup`) com
uma linha por programa (nome mono + ✕). Clicar no ✕ **risca** a linha e troca o ✕ por **"desfazer"**
(restaura). A remoção só é efetivada na `Edicao` ao fechar o popup (os riscados saem do conjunto).
Se o conjunto ficar vazio, o cartão fica em estado de aviso e a edição não conta para o "Conferir".

**5. Habilitação por escopo.**
"+ Adicionar ao lote" passa a exigir **≥1 programa marcado** (além dos campos). "Conferir lote →"
exige **≥1 edição** e **toda edição com ≥1 programa**; tooltip explica o que falta.

**6. Conferência por edição.**
`main_window._on_conferir` deixa de passar um conjunto global. Passa, por edição, o mapa
nome→texto só dos programas daquela edição. `scan_lote`/`ConferenciaModal` recebem essa associação
(edição → programas). Mantém-se `programas_texto(paths)` para ler o conteúdo; a associação é
montada a partir de `ed.programas`.

**7. "Desmarcar selecionados".**
Botão ghost no cabeçalho do `ProgramListV4`, ao lado de "Marcar todos", habilitado quando há ≥1
marcado; chama `desmarcar_todos()` (já existe).

## Risks / Trade-offs

- **Quebra de assinatura da conferência** (`scan_lote`/`ConferenciaModal` recebiam um único conjunto
  de programas) → manter compatibilidade aceitando tanto o formato antigo (um conjunto para todas)
  quanto o por-edição, ou atualizar os testes junto. Decisão: atualizar a assinatura e os testes na
  mesma change (a conferência por edição é o comportamento correto agora).
- **Programa removido de uma edição vs. ainda marcado à esquerda** → o conjunto da edição é
  independente da marcação atual (decisão 2); a marcação à esquerda serve só para semear novas
  edições. Documentar no tooltip/estado vazio para não confundir.
- **`Edicao.programas` como string** (não `Path`) → conversão nas bordas; aceitável e evita
  problemas de hash/serialização futura (receitas salvas).

## Migration Plan

Mudança só de UI + camada de conferência; sem dados persistidos novos. Sem rollback especial: a
`Edicao` com `programas=()` continua válida (comportamento antigo) até o compositor passar a
preencher. Receitas salvas antigas (sem `programas`) carregam com conjunto vazio — o operador
re-marca antes de conferir.

## Open Questions

- Receita salva deve persistir os programas por edição? (Provável que **não** — receita é regra
  reutilizável entre pastas; os programas variam por execução.) Tratar em change futura de receitas.
