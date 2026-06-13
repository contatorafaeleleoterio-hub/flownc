## Why

Na tela Lote, ao adicionar uma edição (origem → destino) o operador não recebe **nenhum
feedback visual de quais programas receberam aquela edição**. Quando ele monta várias edições
com conjuntos diferentes de programas (ex.: `G54→G55` em 10 programas, depois `M8→M9` em 6), fica
confuso revisar o que vai onde — na dúvida, apaga tudo e recomeça. Além disso, ajustar uma edição
exige um round-trip pelo compositor, e desmarcar programas para a próxima edição é feito um a um.

## What Changes

- **BREAKING (modelo da tela Lote):** cada edição passa a **guardar seu próprio conjunto de
  programas**, fotografado no momento de "+ Adicionar ao lote" (antes: todas as edições valiam para
  os programas marcados na hora de conferir). A conferência/publicação passa a aplicar cada edição
  apenas aos programas dela.
- **Edição inline de origem/destino no cartão:** clicar no código de origem (ex.: `G54`) ou no
  destino abre o dropdown ali mesmo para troca imediata (afetar com ícone de seta/lápis). Vale para
  os dois inputs das edições de troca.
- **Contagem de programas + dropdown no fim do cartão:** onde hoje ficam os 3 ícones, passa a
  aparecer **"N programas"** (abre um dropdown listando os programas daquela edição). Mantém-se
  **duplicar (⧉)** e **excluir (✕)** a edição.
- **Remover programa de uma edição com desfazer:** cada item do dropdown de programas tem **✕** que
  o risca da lista e oferece **desfazer** (padrão de UI para qualquer remoção de item de lista).
- **Botão "Desmarcar selecionados"** no painel Programas (esquerda): limpa a marcação atual de uma
  vez, para o operador escolher outros programas para a próxima edição sem desmarcar um a um.
- **Habilitação:** "+ Adicionar ao lote" exige ≥1 programa marcado; "Conferir lote →" exige ≥1
  edição e que toda edição tenha ≥1 programa.

## Capabilities

### New Capabilities
- `lote-programas-por-edicao`: cada edição do lote carrega e exibe seu próprio conjunto de
  programas (snapshot ao adicionar), com contagem, dropdown de programas, remoção individual com
  desfazer e regras de habilitação de adicionar/conferir.

### Modified Capabilities
- `compositor-v4-abas`: o compositor passa a fotografar os programas marcados na `Edicao` ao
  adicionar e a exigir ≥1 programa marcado para habilitar "+ Adicionar ao lote".

## Impact

- **Código:** `flownc/ui/components/compositor_v4.py` (`Edicao` ganha campo `programas`; snapshot e
  habilitação), `flownc/ui/screens/lote_screen.py` (cartão com inline + contagem + dropdown de
  programas + desfazer; CTA), `flownc/ui/components/program_list_v4.py` ("Desmarcar selecionados"),
  `flownc/ui/main_window.py` (conferência por edição em vez de marcação global).
- **Conferência:** `scan_lote` / `ConferenciaModal` passam a receber o conjunto de programas por
  edição (não mais um único conjunto global de marcados).
- **Contrato visual:** evolui o mockup v4 (`mockups/painel-final.v4.html`) e o `docs/CONTEXTO-IA.md`
  — a dinâmica do cartão de edição muda; atualizar após aprovação.
- **Testes:** `flownc/tests/test_ui_smoke.py` (cartões, contagem, desmarcar, conferência por edição).
