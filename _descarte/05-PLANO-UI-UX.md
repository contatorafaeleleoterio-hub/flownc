# 05 — PLANO DE REDESENHO DE UI/UX — CNC Batch Editor

> **Para a próxima sessão:** leia este arquivo + `00-HANDOFF.md`. O sistema está
> funcional e estável (106 testes verdes). O foco agora é **melhorar a interface
> e a usabilidade** — o Rafael acha a tela atual confusa e pouco didática.
> **Status (2026-06-02):** o Rafael **devolveu a análise do workflow** (os 12 problemas).
> Já produzi o relatório `06-ANALISE-UX-WORKFLOW.md` (novo layout/fluxo + roadmap), os
> mockups em `mockups\06-*.html`, e o prompt de pesquisa `07-PROMPT-PESQUISA-UI.md`.
> **Próximo:** rodar a pesquisa do `07` para decidir **tela única vs wizard** com base em
> evidência (normas + benchmark) e então implementar o **P0** do `06`. Ver §4.

---

## 1. Objetivo

Redesenhar a interface do app (decisão do Rafael: **redesenho visual completo**),
mantendo 100% do motor seguro do `core/` (não tocar em matcher/replacement_plan/
replacer/verifier). A mudança é só na camada de apresentação (`ui/` + QSS).

**Dores apontadas pelo Rafael (o que mais incomoda hoje):**
1. **"Não sei por onde começar"** — abrir o app não deixa clara a ordem dos passos.
2. **"Nomes e termos confusos"** — rótulos técnicos demais ("trocas comuns", "perfil", etc.).
3. **"Falta de feedback"** — clica e não sabe se funcionou, se está processando, ou se deu erro.

---

## 2. Skill de design escolhida

### Decisão: **frontend-design (Anthropic)**

- **Repositório:** https://github.com/anthropics/skills/tree/main/skills/frontend-design
- **Por quê esta e não a outra:** entre as duas indicadas, é a melhor para o nosso caso —
  está disponível no marketplace oficial, é da Anthropic, e seus princípios
  (hierarquia visual, tipografia, cor coesa, espaçamento, agrupamento) são
  *framework-agnostic*, ou seja, transportáveis para o Qt/QSS manualmente.
- **Ressalva técnica importante:** nosso app é **desktop Qt/PySide6**, NÃO web. A skill
  **não gera código Qt** — ela serve como guia de *princípios*. Além disso, ela tende a
  empurrar para visuais "bold/maximalistas"; para uma **ferramenta de chão de fábrica**
  o caminho é o oposto: **sóbrio, limpo, legível, operacional** (alinhado ao PRD §11).
  Usar os princípios de **clareza e hierarquia**, não os de "estética marcante".

### Alternativa avaliada e descartada: **ui-ux-pro-max-skill**

- **Repositório:** https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
- **Por que descartada:** é estritamente **web + mobile** (React, Tailwind, Vue, Flutter,
  SwiftUI...) e orientada a estética de produto/marketing por indústria. Não encaixa
  numa ferramenta desktop Qt industrial.

### Estado da instalação (verificado em 2026-06-01)

- A `frontend-design` está **baixada** no cache do marketplace, mas **NÃO instalada/ativada**
  (`~/.claude/plugins/installed_plugins.json` está com `"plugins": {}`).
- O conteúdo do `SKILL.md` **já foi lido** na sessão; os princípios estão disponíveis
  mesmo sem ativação formal.

### Como instalar (ação do Rafael na interface do Claude Code)

A instalação de plugin é feita pelo menu interativo `/plugin` (o assistente não consegue
clicar nesse menu por você). Passos:

1. Digite no chat: **`/plugin`** → Enter.
2. **Browse marketplaces** → **`claude-plugins-official`**.
3. Procure **`frontend-design`** → **Install** → **Enable** (se perguntar).
4. Recarregar/reiniciar se for solicitado.

> Caminho do arquivo já baixado (referência):
> `~/.claude/plugins/marketplaces/claude-plugins-official/plugins/frontend-design/skills/frontend-design/SKILL.md`

---

## 3. Abordagem combinada

- **Nível de mudança:** redesenho visual completo (escolha do Rafael).
- **Restrição de segurança:** não alterar o `core/`. Só `ui/` + `main.py` + QSS.
- **Princípios a aplicar (da frontend-design, adaptados a ferramenta sóbria):**
  hierarquia visual clara, agrupamento por passos, tipografia legível, cor por estado
  (verde/amarelo/vermelho já existe no domínio), espaçamento generoso, feedback explícito.
- **Foco real:** resolver as 3 dores (§1) — que são de *usabilidade/arquitetura de
  informação*, não de enfeite. Ex.: fluxo guiado por passos, rótulos em linguagem de
  chão de fábrica, indicadores de estado/progresso, mensagens claras.
- **Sem regressão:** após o redesign, rodar `pytest` (106 testes) + `test_ui_smoke.py` +
  abrir o app headless; o motor e o fluxo lógico devem continuar idênticos.

---

## 4. Próximo passo concreto (retomar AQUI)

**Concluído (2026-06-02):**
- ✅ O Rafael devolveu a análise do workflow (12 problemas — texto-base no §5 abaixo).
- ✅ Relatório `06-ANALISE-UX-WORKFLOW.md`: avaliação dos 12 problemas (concordo/discordo/
  ajusto) + 7 achados extras + **novo workflow (5 passos)** + **novo layout** + hierarquia +
  estratégias de feedback/validação/erro + **roadmap P0→P3** classificado por impacto/esforço.
- ✅ Mockups: `mockups\06-mockup-ux.html` (anotado) e `mockups\06-prototipo-navegavel.html`
  (clicável, telas estáticas) — visualização da proposta.
- ✅ `07-PROMPT-PESQUISA-UI.md`: prompt para uma IA de pesquisa decidir a arquitetura com base
  em normas (ISA-101, ISO 9241, NN/g) + benchmark de CAM/HMI.

**A fazer (em ordem):**
1. **Rodar a pesquisa do `07`** e trazer o resultado — decide oficialmente **tela única vs
   wizard**, ordem/tamanho dos elementos e regras inteligentes (ex.: reabrir último perfil).
2. **Reconciliar `06` com o resultado da pesquisa** (ajustar layout/fluxo se a evidência
   divergir da minha proposta) e **validar com o Rafael** ANTES de codar.
3. **Implementar o P0** do `06` em `ui/` + QSS, **sem tocar no `core/`**. Rodar a suíte de
   testes (106) + `test_ui_smoke.py`.
4. **Regenerar o EXE** (`python -m PyInstaller` — NÃO o `pyinstaller.exe`, ver HANDOFF §6.5).

---

## 5. Texto-base entregue ao Rafael (workflow atual — para análise)

> Descrição fiel do comportamento do código atual (`ui/main_window.py`,
> `ui/preview_dialog.py`). Base da análise de UX do Rafael.

### Problema que o sistema resolve

Programas CNC (arquivos de texto com instruções de usinagem) chegam em padrão genérico e
precisam ser adaptados à realidade de cada máquina antes de produzir: trocar ferramenta,
offset, rotação, avanço, fluido, alturas. Hoje isso é feito abrindo arquivo por arquivo num
editor de texto — lento, repetitivo e sujeito a erro grave (ferramenta errada, colisão,
refugo). O sistema faz essas trocas de texto em vários arquivos de uma vez, mostra o que vai
mudar antes de gravar, e salva os resultados numa pasta nova — sem nunca alterar os
arquivos originais.

### Workflow atual

**ETAPA 0 — Abertura do programa**
- A janela abre com: barra superior (Perfil + botões Novo / Duplicar / Renomear / Excluir /
  Abrir pasta / Abrir programa(s)), uma linha "Destino", duas abas ("Substituições" e
  "Verificações") e uma barra de status embaixo.
- Ao abrir, o sistema lê a pasta de perfis e seleciona automaticamente o primeiro perfil
  encontrado. As trocas e verificações desse perfil já aparecem preenchidas nas tabelas.

**ETAPA 1 — Perfil de máquina**
- Campo "Perfil" lista os perfis salvos (arquivos .json).
- Botões: Novo (cria vazio), Duplicar (copia o atual), Renomear, Excluir (com dupla
  confirmação + backup automático).
- Trocar o perfil recarrega as tabelas de trocas comuns e de verificações com o conteúdo
  daquele perfil.

**ETAPA 2 — Definir destino dos arquivos**
- Linha "Destino" com duas opções: "Ao lado dos originais" (cria a pasta de saída na mesma
  pasta dos programas) ou "Pasta fixa" (grava sempre numa pasta escolhida no botão
  "Escolher...").
- A escolha é lembrada para a próxima vez que abrir o programa.

**ETAPA 3 — Carregar os programas**
- "Abrir pasta..." carrega todos os arquivos de uma pasta. "Abrir programa(s)..." carrega
  arquivos avulsos escolhidos.
- Os programas aparecem na lista da esquerda da aba "Substituições", cada um com uma caixa
  de marcação, todos marcados por padrão. O primeiro fica selecionado.

**ETAPA 4 — Definir as trocas (aba "Substituições")**
- Lado esquerdo: lista de PROGRAMAS com caixa de marcação. Só os marcados serão alterados.
  Clicar no nome de um programa o seleciona para editar as trocas específicas dele.
- Lado direito, parte de cima: tabela "Trocas COMUNS" (colunas: Aplicar, Buscar, Trocar por,
  Obs) — valem para todos os programas marcados.
- Lado direito, parte de baixo: tabela "Trocas SÓ DESTE programa" — valem apenas para o
  programa selecionado.
- Botões das tabelas: "+ troca comum" / "+ troca só deste" (adiciona linha), "- remover"
  (remove a linha selecionada), "+ da lista" (insere uma troca da biblioteca de códigos
  salvos), "Gerenciar codigos..." (abre a biblioteca), "Salvar perfil" (grava as trocas
  atuais no perfil).

**ETAPA 5 — Executar substituições (preview)**
- Botão "Executar substituições (preview)".
- O sistema verifica as condições (ver variáveis abaixo) e, se passar, abre uma janela de
  revisão.
- Janela de revisão: lista lateral com "RESUMO" + cada programa (colorido por severidade);
  ao clicar em um item, o painel mostra: checklist de cada troca planejada (quantas
  ocorrências encontrou), as linhas alteradas (antes/depois), conflitos, alertas e o trecho
  modificado.
- Botão "Confirmar e salvar" (fica desabilitado se houver erro crítico).

**ETAPA 6 — Salvar**
- Ao confirmar: o sistema primeiro testa se todos os arquivos podem ser gravados; cria a
  pasta de saída com nome "_processado_PERFIL_data_hora"; grava cada arquivo de forma segura.
- Em seguida relê cada arquivo gravado e confere a "impressão digital" (SHA-256) contra o
  esperado.
- Gera um arquivo de log ".txt" com a contagem de trocas por programa e o resultado da
  conferência de integridade.
- Mostra uma mensagem final de sucesso (ou de alerta, se a conferência falhar).

**ETAPA 7 — Verificações (aba "Verificações", opcional, não altera nada)**
- Tabela com regras (colunas: Aplicar, Tipo, Codigo, Valor, Obs). Tipos: Deve existir / Não
  pode existir / Mínimo / Máximo / Exato.
- Botão "Executar verificações" roda as checagens nos programas marcados e mostra o
  resultado em texto, sem gravar nada.

### Variáveis de interação / comportamento

**Perfil**
- Existente: carrega trocas e verificações.
- Nenhum perfil na pasta: campo mostra "(nenhum perfil)".
- Perfil com arquivo inválido: mostra erro "Perfil inválido" e não carrega.

**Destino**
- "Ao lado dos originais": cria a pasta de saída junto dos programas.
- "Pasta fixa" sem pasta escolhida: ao salvar, bloqueia com aviso "Pasta não configurada".
- Se a pasta de saída já existir, cria com sufixo (_02, _03...).

**Programas**
- Nenhum carregado: ao executar, aviso "Sem programas".
- Nenhum marcado: ao executar, aviso "Nenhum marcado".
- Dois ou mais programas com o mesmo nome: bloqueia com aviso "Nomes duplicados no lote".
- Programas marcados em pastas diferentes: bloqueia com aviso "Múltiplas pastas".
- Arquivo que não é texto (binário): marcado em vermelho e excluído do processamento.

**Trocas**
- Caixa "Aplicar" desmarcada: a troca é ignorada.
- "Buscar" vazio: a linha é ignorada.
- "Trocar por" vazio: significa remoção (apaga o texto encontrado).
- Cada troca tem uma política para "0 ocorrências": avisar (padrão), ignorar (silencia) ou
  erro (bloqueia salvar). Quando uma troca não encontra nada, o sistema pode sugerir uma
  variante com zero à esquerda (ex.: procurou "M8", sugere "M08").
- Toda troca digitada na tela é tratada como texto literal (não é expressão/código
  especial); o casamento de endereços CNC evita trocar "T1" dentro de "T10".

**Resultado / severidade (cores)**
- Verde: troca aplicada, sem problemas.
- Amarelo (atenção, não bloqueia): troca com 0 ocorrências, codificação de baixa confiança,
  verificação opcional falhou, ou linha com comando crítico removida.
- Vermelho (crítico, bloqueia salvar): erro de leitura, resultado vazio, perda do "%" de
  início/fim, ou perda do fim de programa (M30/M02).

**Conflito entre trocas**
- Quando duas trocas atingiriam o mesmo trecho: vence a regra específica do programa sobre a
  comum; depois a de menor prioridade; depois a declarada primeiro. A perdedora é registrada
  como "suprimida" e mostrada no preview.

**Execução sem efeito**
- Se nenhuma troca marcada encontrar ocorrência em nenhum programa: mensagem "Nada a trocar".

**Pós-salvamento**
- Conferência de integridade OK: mensagem de sucesso.
- Conferência falha: mensagem de alerta e a pasta de saída é mantida para auditoria.
