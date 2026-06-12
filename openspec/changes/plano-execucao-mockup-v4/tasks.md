# Tarefas — plano-execucao-mockup-v4 (Fase 2)

> **Fonte de verdade: `PLAN.md` (raiz).** Este `tasks.md` é o espelho operacional dele — se algo
> divergir, o PLAN.md vence e este arquivo é regenerado a partir dele. Critérios de conclusão,
> fallbacks (`↳ Se falhar:`) e a justificativa das marcações **[CRÍTICO]** estão no PLAN.md
> (Gate 0 + Blocos 1–12). Verificação sempre com o venv `flownc/.venv` (nunca o pytest global).
> Na Fase 2 só se altera `flownc/ui/**`; o `flownc/core/` não muda. Telas usam **dados de exemplo**
> (valores fixos no código da UI, não lidos de `core/`).

## 0. Gate — pendência da change v2 (RESOLVIDO 2026-06-11)

- [x] 0.1 Perguntar ao Mestre o destino da change `redesign-fase2-fidelidade-visual` — decidido: arquivar guardando só o histórico
- [x] 0.2 Arquivar com `openspec archive redesign-fase2-fidelidade-visual --skip-specs -y` (histórico preservado, specs base intactos; `openspec list` não a mostra mais)

## 1. Fundação visual v4 (tokens + QSS)

- [x] 1.1 [CRÍTICO] Atualizar `flownc/ui/theme.py` com os tokens da paleta v4 (ok: `COLOR_CTA == "#E85D04"`, existem `COLOR_RAIL`/`COLOR_TOP`, import sem erro)
- [x] 1.2 Atualizar `flownc/ui/style.qss` com seletores `QTabWidget` e `QDialog` via tokens (ok: blocos presentes, nenhuma cor hexadecimal literal)
- [x] 1.3 [CRÍTICO] Verificar a fundação (ok: pytest/mypy/ruff verdes)

## 2. Estrutura raiz (rail + topo + pilha de telas)

- [x] 2.1 Criar `flownc/ui/components/rail.py` (`RailWidget`: 4 botões + sinal `tela_mudou(int)`)
- [x] 2.2 Filete laranja no botão ativo do rail
- [x] 2.3 Bolinha de status no botão Editor do rail (método liga/desliga)
- [x] 2.4 Criar `flownc/ui/components/top_bar.py` (`TopBar`: combo de receitas com "💾 Salvar lote atual como…" + chip de backup)
- [x] 2.5 Criar o pacote `flownc/ui/screens/` (com `__init__.py`) + 4 stubs: `LoteScreen`, `EditorScreen`, `CodigosScreen`, `HistoricoScreen`
- [x] 2.6 [CRÍTICO] Reestruturar `flownc/ui/main_window.py`: topo + (rail + `QStackedWidget`), ordem 0=Lote/1=Editor/2=Códigos/3=Histórico; sem `QSplitter` raiz
- [x] 2.7 Conectar `RailWidget.tela_mudou` → `QStackedWidget.setCurrentIndex`
- [x] 2.8 [CRÍTICO] Verificar a estrutura raiz (app abre, 4 botões trocam de tela, pytest verde)

## 3. Tela Lote · painel Programas

- [x] 3.1 Criar `flownc/ui/components/program_list_v4.py` (checkbox, nome mono, data, tamanho, "✎ Abrir", "✕")
- [x] 3.2 Marcar/desmarcar com destaque visual + chip "N de M marcados"
- [x] 3.3 Botão "Marcar todos / Desmarcar todos"
- [x] 3.4 Arrastar-e-soltar arquivos na lista
- [x] 3.5 Estado vazio com botão "+ Adicionar programa(s)…"
- [x] 3.6 Integrar `program_list_v4` na coluna esquerda da `LoteScreen`

## 4. Tela Lote · Compositor com abas e Lote de edições

- [x] 4.1 Criar `flownc/ui/components/compositor_v4.py` (`QTabWidget` 2 abas + botão único "+ Adicionar ao lote")
- [x] 4.2 Aba "Trocar código": 2 dropdowns pesquisáveis (busca + "★ Frequentes", só código, descrição no tooltip)
- [x] 4.3 Opção "✕ Remover (sem código)" no dropdown de destino (visual vermelho)
- [x] 4.4 Habilitar "+ Adicionar ao lote" só com origem E destino preenchidos
- [x] 4.5 Aba "➕ Inserir bloco" (textarea, posição com aviso, chips de modelos, prévia do 1º programa marcado)
- [x] 4.6 Lista de edições (cartões numerados) na `LoteScreen`
- [x] 4.7 Editar/duplicar/excluir do cartão (✎ recarrega na aba certa, ⧉ duplica, ✕ remove e renumera)
- [x] 4.8 Detectar conflito (mesma origem): cartão âmbar + chip "⚠ N conflitos"
- [x] 4.9 CTA "Conferir lote →" (desabilita sem edição ou sem programa marcado, com tooltip)

## 5. Modal Conferência

- [x] 5.1 Criar o pacote `flownc/ui/modals/` (com `__init__.py`) + `conferencia_modal.py` (`QDialog` bloqueante: faixa de total, avisos, cartões, linha de backup, rodapé fixo)
- [x] 5.2 Preencher o modal com dados de exemplo (valores fixos na UI)
- [x] 5.3 Rodapé conforme estado (laranja sem conflito, âmbar com conflito, desabilitado com total 0)
- [x] 5.4 Ligar CTA "Conferir lote →" para abrir o modal

## 6. Modal Publicação

- [x] 6.1 Criar `flownc/ui/modals/publicacao_modal.py` (barra de progresso backup→gravação→SHA-256; não fecha durante o progresso)
- [x] 6.2 Tela de resultado ("Publicado ✓", caminho do backup, "Ver no Histórico" / "OK — novo lote")
- [x] 6.3 "OK — novo lote" limpa a lista de edições da `LoteScreen`
- [x] 6.4 "Ver no Histórico" navega à tela Histórico
- [x] 6.5 Encadear Conferência → Publicação

## 7. Tela Editor

- [x] 7.1 Criar `flownc/ui/screens/editor_screen.py` reaproveitando o `editor_panel` existente (NÃO alterar `core/inplace_save.py` nem `core/file_handler.py`)
- [x] 7.2 Faixa de arquivos à esquerda (clicar troca o arquivo aberto)
- [x] 7.3 [CRÍTICO] Guarda de alterações ao trocar/sair (Salvar / Descartar / Cancelar)
- [x] 7.4 Cabeçalho ("Editando NOME.NC", aviso "⚠ salva direto, sem cópia", botões "Salvar como…" / "Salvar")
- [x] 7.5 Toast "Desfazer" após salvar
- [x] 7.6 Bolinha de alteração na faixa e no botão Editor do rail

## 8. Toolbar do Editor (3 grupos)

- [x] 8.1 Toolbar em 3 grupos com separadores (Localizar | Substituir | Inserir bloco)
- [x] 8.2 Contagem automática (recalcula ao trocar código, trocar arquivo ou editar o texto)
- [x] 8.3 Navegação ↑/↓ circular + realce da ocorrência corrente
- [x] 8.4 Realce de todas as ocorrências (`QSyntaxHighlighter`)
- [x] 8.5 "Substituir todos"
- [x] 8.6 "Um a um" como stepbar inline (sem `QMessageBox`)
- [x] 8.7 [CRÍTICO] "➕ Inserir bloco" no editor com proteção de âncora inexistente

## 9. Tela Códigos

- [x] 9.1 Criar `flownc/ui/screens/codigos_screen.py` (lista código+descrição, busca, contador "N cadastrados")
- [x] 9.2 "+ Adicionar código" (com bloco opcional) via `core/library_store.py`
- [x] 9.3 Tag "bloco" nos códigos com bloco + expô-los como chips nos inseridores

## 10. Tela Histórico

- [x] 10.1 Criar `flownc/ui/screens/historico_screen.py` (lista cronológica reversa: quando/resumo/backup/configuração)
- [x] 10.2 Estado vazio (ícone + texto-guia)
- [x] 10.3 "↩ Restaurar originais" por linha (confirmação; desabilita se backup não existe). Restauração real = Fase 3 [CRÍTICO lá]

## 11. Topo global (receitas + backup)

- [x] 11.1 Seleção de receita no combo (lote vazio carrega direto; lote cheio pede confirmação)
- [x] 11.2 "💾 Salvar lote atual como…" (diálogo de nome; gravação real via `preset_store` = Fase 3)
- [x] 11.3 Chip de backup clicável (`QFileDialog`; atualiza o caminho exibido)

## 12. Verificação da Fase 2

- [x] 12.1 [CRÍTICO] Rodar pytest (zero regressões frente ao baseline)
- [x] 12.2 [CRÍTICO] Rodar mypy (sem novos erros de tipo)
- [x] 12.3 [CRÍTICO] Rodar ruff (sem violações)
- [x] 12.4 Smoke visual de todas as telas vs `mockups/painel-final.v4.html` (divergências anotadas)
- [ ] 12.5 Pedir aprovação explícita do Mestre ("é esse") — gate de saída da Fase 2
