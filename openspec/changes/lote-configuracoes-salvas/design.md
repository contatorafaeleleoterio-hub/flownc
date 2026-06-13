## Context

A `TopBar` tem hoje um `QComboBox` (`cb_receita`) com as receitas + o item "Salvar lote atual
como…". O `main_window` liga isso ao `preset_store` (`save_preset`/`load_preset`,
`app_paths.presets_dir()`), convertendo `Preset.global_rules` ↔ `Edicao(tipo="swap")` — **blocos
(`ins`) são descartados ao salvar**. O fluxo é pouco visível e o operador não usa.

Esta change move a função para a tela Lote, com botões explícitos, e amplia o armazenamento para
guardar também blocos. Interage com `lote-edicoes-por-programa`: as configurações guardam só regras;
os programas entram via "Aplicar aos marcados".

## Goals / Non-Goals

**Goals:**
- Botões "Salvar configuração" e "Abrir configuração" na linha do título "Lote de edições".
- Salvar = nome + Salvar/Cancelar; guarda edições (swap + ins), sem programas.
- Abrir = lista de configs; edições entram no lote como cartões com 0 programas.
- "Aplicar aos marcados" preenche os programas das edições carregadas.
- Remover o seletor de receita da `TopBar`.
- Configs compartilhadas (diretório de dados da aplicação).

**Non-Goals:**
- Não persistir programas na configuração.
- Não renomear/editar configs nesta change (só salvar, listar, abrir) — fica para follow-up.
- Não atualizar mockup/`CONTEXTO-IA` aqui (follow-up após aprovação visual).

## Decisions

**1. Armazenamento: estender o conceito de receita para guardar blocos.**
Opção escolhida: um **`config_store.py`** dedicado que serializa uma lista de `Edicao`
(swap + ins) em JSON, em `app_paths.configs_dir()` (novo, compartilhado). Alternativa descartada:
forçar tudo em `Preset.global_rules` — não representa blocos sem hack. O `config_store` reusa
`json_store` para IO atômico. Cada config = `{ "nome": str, "edicoes": [ {campos da Edicao sem
programas} ] }`.

**2. Botões na tela Lote, espelhando o painel Programas.**
Na `LoteScreen._build_right`, a linha do título "Lote de edições" ganha, à direita, dois botões
ghost: **"Abrir configuração"** e **"Salvar configuração"** (mesmo estilo `GhostBtnV4` usado em
"Marcar todos"/"+ Adicionar programa(s)…"). Mantém o chip de estado do lote.

**3. Salvar = popup de nome simples.**
"Salvar configuração" abre um pequeno input (campo de nome + Salvar/Cancelar). Pode ser um
`QInputDialog` ou um popup inline no padrão do projeto; serializa `self._edicoes` (sem o campo
`programas`) via `config_store.save_config(nome, edicoes)`. Nome repetido pede confirmação de
sobrescrever.

**4. Abrir = lista + entrada direta no lote.**
"Abrir configuração" lista os nomes salvos (popup/menu). Ao escolher, carrega as edições via
`config_store.load_config(nome)` e chama `self._lote.set_edicoes(edicoes)` — os cartões aparecem com
`programas=()`. Se já houver lote montado, confirma a substituição (reusa o padrão atual).

**5. "Aplicar aos marcados".**
Botão que aparece/habilita quando há edições com 0 programas e há ≥1 programa marcado. Ao clicar,
para cada edição sem programas (ou todas, conforme regra), define
`programas = tuple(marcados_atuais)` via `replace`. Casa com o modelo de `lote-edicoes-por-programa`
(programas entram por aqui em vez de pelo compositor). Tooltip explica o que falta quando
desabilitado.

**6. Remoção do seletor no topo.**
`TopBar` perde `cb_receita`, `ITEM_SALVAR`, `set_receitas`, `receita_alterada`,
`salvar_receita_solicitado`. `main_window` deixa de ligar esses sinais; a lógica de salvar/abrir
passa a ser disparada por sinais novos da `LoteScreen` (`salvar_config_solicitado`,
`abrir_config_solicitado`) ou tratada dentro da própria `LoteScreen` com o `config_store`.

## Risks / Trade-offs

- **Ordem de aplicação:** esta change assume o modelo de programas-por-edição. → Aplicar
  `lote-edicoes-por-programa` antes; se aplicada isolada, "Aplicar aos marcados" vira no-op até o
  campo `programas` existir. Documentar a dependência no proposal (feito).
- **Configs compartilhadas num app local:** "compartilhado entre operadores" = mesmo diretório de
  dados na mesma máquina/instalação. Sincronização entre máquinas está fora de escopo. → Deixar o
  diretório configurável no futuro (pasta de rede), não agora.
- **Migração de receitas antigas:** presets existentes (`presets_dir`) não viram configs
  automaticamente. → Como a função antiga do topo era pouco usada, não migrar; documentar.

## Migration Plan

Sem dado destrutivo. Novo diretório `configs_dir()` para os JSONs de configuração. A `TopBar` perde
o seletor — nenhuma persistência depende dele. Rollback = reverter o commit (configs salvas ficam no
disco, inertes).

## Open Questions

- Editar/renomear/excluir configurações salvas — desejável, mas fica para change futura (aqui só
  salvar, listar, abrir).
