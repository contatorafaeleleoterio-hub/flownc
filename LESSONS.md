# Lessons — FlowNC

## 2026-06-07 — Não inferir direção a partir de arquivo de exemplo
O preset `MAZAK_VTC530.json` tem `global_rules`/`verifications` por ser exemplo antigo. Isso NÃO reflete o sistema definido no plano: verificações automáticas e regras de perfil foram **retiradas do escopo**. A biblioteca é só código + descrição editável (operador monta a troca manualmente, origem→destino). Antes de propor conteúdo de perfil/biblioteca, conferir a direção no `PLAN.md` — não copiar do exemplo. Quando algo antigo não reflete mais o plano, descartar e marcar "como fica na nova atualização" no próprio plano, para o próximo agente não reler nem perguntar.

## 2026-06-07 — Biblioteca tem `replace` vazio de propósito (NÃO preencher)
A biblioteca (`data/library.json` e `data_default/library.json`, 89 códigos) usa schema `find`=código, `replace`=**vazio**, `label`=descrição, `tags`=categoria. O `replace` vazio é **intencional**: a biblioteca é um **dicionário de códigos** (código + significado), não uma lista de trocas prontas; o destino quem escolhe é o operador, na tela de montar edição.
- **Risco transitório:** enquanto o Compositor não for reescrito (Próximo passo 1), a tela antiga espera um par "de → para" e pode tratar um código da biblioteca como "trocar por nada" (apagar). Até a reescrita, não usar os códigos da biblioteca direto na tela antiga.
- **NÃO "consertar" preenchendo o `replace`** — isso volta ao modelo de pares prontos, que foi **descartado**. A correção certa é a tela nova com **dois campos** (código que sai / código que entra).
- **3 perfis iniciais:** `MAQ01`/`MAQ02`/`MAQ03` (só esses; sem regras nem verificações). Exemplo `MAZAK_VTC530.json` removido (git preserva).

## 2026-06-07 — Design é contrato: protótipo HTML antes do código (Regra de Ouro)
Causa raiz das entregas que saíam visualmente diferentes do proposto: o design era improvisado durante a programação. Decisão do Mestre: **separar a decisão visual da construção**. Fase 1 = protótipo HTML completo e interativo (TODAS as telas e popups do inventário), offline, aprovado pelo Mestre ("é esse") — vira o **contrato visual congelado**. Só depois: Fase 2 = app nativo (PySide6) reproduzindo o protótipo à risca, tela por tela com conferência lado a lado; Fase 3 = ligar backend sem tocar no layout aprovado.
- **Regra prática:** nenhuma tela/popup nasce no código sem antes existir e estar aprovada no protótipo. Mudança visual = primeiro o protótipo + nova aprovação, depois o código.
- **Tecnologia:** protótipo em HTML/CSS/JS; produção em PySide6 nativo (o HTML NÃO roda dentro do app — é só referência). Mantém EXE pequeno, sem navegador embutido.
- Registrado no topo do `PLAN.md` (Regra de Ouro + Reestruturação em 3 fases). Próximos passos 1–6 → Fase 2; 4/7/8/9 + Mudanças C/D → Fase 3.

## 2026-06-07 — Auditoria de terceiro também erra: verificar cada afirmação no código real
Uma auditoria do "sênior" (`auditoria_plano.md`) apontou 3 "erros críticos"; só 1 era real. Conferindo arquivo por arquivo: **CRLF no `publisher.py`** = alarme falso (ele é **byte-exato**, `read_bytes`/`_write_bytes_atomic`, não usa `read_text`/`write_text`); **`scope-select` faltando** = alarme falso (não existe no mockup v2, 0 ocorrências); **`verifier.py` não existe** = errado (existe). Real mesmo: só `data_default/` fora do `datas` do `.spec`. As classes de overlay citadas (`diff-line`/`summary-grid`/…) eram fictícias — as reais são `.run`/`.res`/`.confirm`/`.saved`.
- **Regra prática:** antes de agir sobre qualquer auditoria/relatório externo, validar cada item lendo o código real (nome de função > número de linha, que sofre drift). Registrar o veredito por escrito no `PLAN.md` ("Resposta à auditoria") para não reabrir a discussão.

## 2026-06-07 — Protótipo em `mockups/`: caminho relativo de `@font-face` é armadilha
Ao tornar o protótipo offline, o `@font-face` com `src:url("assets/fonts/...ttf")` **não** resolve a partir da raiz do projeto — resolve a partir da pasta do HTML (`mockups/`), ou seja procura `mockups/assets/fonts/`, que não existe. Resultado: todas as fontes caem no fallback (Segoe UI/Consolas) e o próprio critério de aprovação da FASE 1 ("abrir sem internet e ver IBM Plex") **falha silenciosamente**. Correção: copiar os `.ttf` também para `mockups/assets/fonts/` (ou usar `../flownc/assets/fonts/`); os canônicos ficam em `flownc/assets/fonts/` (insumo do EXE, Passo 7d). Pesos realmente usados no CSS: Sans 400/600/700 + Mono 500/600/700 (Sans nunca usa 500).
- **Regra prática:** caminho relativo em HTML é relativo ao arquivo, não ao repo. Ao prototipar offline, conferir que os assets existem a partir da pasta do HTML.
- **Achado de medição:** contar com grep engana — os 40 `drop` do protótipo eram todos de dropdown (`drop-btn`/`drop-list`/`dropdown`), nenhum de arrastar-soltar. Sempre desambiguar o que o número representa antes de concluir "existe".

## 2026-06-07 — Fonte dos `.ttf` IBM Plex: Google Fonts só tem variável; usar `IBM/plex`
Ao baixar as fontes para offline: o repo `google/fonts` em `ofl/ibmplexsans/` só tem a **fonte variável** `IBMPlexSans[wdth,wght].ttf` (+ italic) — **sem instâncias estáticas**. Já `ofl/ibmplexmono/` ainda tem os estáticos. Para os estáticos do **Sans**, usar o repo `IBM/plex`: `packages/plex-sans/fonts/complete/ttf/IBMPlexSans-{Regular,SemiBold,Bold}.ttf` (raw em `github.com/IBM/plex/raw/master/...`). Pesos realmente usados no CSS do protótipo: **Sans 400/600/700 · Mono 500/600/700** (Sans não usa 500; Mono não usa 400).
- **Regra prática:** `github.com/<repo>/raw/master/<path>` funciona bem; jsDelivr `gh` às vezes dá 403/404. Validar cada download pelo cabeçalho TrueType (`00 01 00 00`) e tamanho > 20 KB, não só pelo HTTP 200.
- **Verificação sem navegador no Windows:** o Control_Chrome MCP é Mac-only (usa AppleScript) → não roda aqui. Alternativa que funcionou: `node --check` no `<script>` extraído + harness **jsdom** carregando o HTML real e exercitando as funções (28/28). jsdom não renderiza fonte de verdade — render visual fica para conferência humana.

## 2026-06-08 (sessão 6) — Catálogo Técnico DESCARTADO; mockup é iterativo
O Mestre reavaliou ao ver o protótipo e **descartou o Catálogo Técnico** (Passo 11 / modelo LIGADO): volta ao modelo **biblioteca simples código + descrição** (`data/library.json` é a fonte; sem catálogo-mestre nem `active_catalog`). A lição anterior (2026-06-08 "Feature ligada…") fica **histórica**. O **Passo 12** (dropdowns só-código + descrição no hover) foi **mantido** e aprovado.
- **Regra prática:** decisão tomada no papel (PLAN) pode cair quando vira pixel. O valor da FASE 1 é exatamente esse — o Mestre vê e corta o que não serve **antes** de virar código. Não tratar o PLAN como imutável durante o refino do protótipo; anotar a reversão no PLAN (decisão supersede) e seguir.
- **Refino de espaço:** seção de Programas é o ponto principal → ganhar área tirando o que rouba linha (banner virou nota inline no cabeçalho; listas auxiliares com altura máx + scroll). Ações de remover (✕) em TODA lista (edições montadas, "em edição", programas).

## 2026-06-08 — Feature "ligada" ≠ reescrever o core: usar a fonte existente como cache
Ao adicionar o **Catálogo Técnico** como fonte-mestre dos códigos (decisão do Mestre "LIGADO"), o caminho de menor risco NÃO é trocar o que o Compositor/Editor consomem: é manter `data/library.json` como **cache gerado** (achatamento do catálogo ativo, mesmo schema `find`/`replace`/`label`/`tags`). Assim `load_library`/`set_library` e os testes existentes ficam intactos — muda só a **origem** dos dados, não a assinatura. O catálogo guarda o rico (categorias, exemplo, observação, exemplos livres); o cache é o achatado.
- **Regra prática:** quando uma feature nova vira "fonte" de algo já consumido, prefira adaptar a fonte para o formato atual (cache/adaptador) a reescrever os consumidores. Confirma o `replace=""` (destino é do operador).
- **UI:** descrição do código **não** vai inline no input (polui) — só no `title`/tooltip (hover). Isso muda o contrato visual do mockup (Compositor mostra descrição inline) → reaprovar no protótipo antes de codar.

## 2026-06-09 (sessão 9) — Aplicar paleta em mockup por tokens: trocar valor, não nome
O mockup é 100% por tokens no `:root` ("zero cor solta"). Para aplicar a paleta "Precisão Laranja", o caminho de menor risco é **manter os nomes dos tokens e trocar só os valores** — recolore as ~900 linhas de CSS de uma vez, consistente. Cuidado com **tokens sobrecarregados** (um nome usado em papéis que a nova paleta separa): `--color-bg-base` servia painel + input + botão de header; `--color-interactive` (azul) servia botão relevante + realce + foco. Resolver com poucos overrides estruturais (painel L/R, header slate, CTA laranja) em vez de reescrever tudo.
- **Regra de ouro da paleta:** laranja `#E85D04` é **exclusivo da única ação executável por tela** (Executar Lote); nunca decoração. O resto da hierarquia é slate (nível 2) / cinza (auxiliar) / outline.
- **Armadilha:** botão slate sobre header slate **some**. Usar um slate mais claro (`#3A4F63`) enquanto o botão mora no header; quando migrar para painel claro, volta ao slate padrão.
- **Fonte da verdade de cor:** `docs/PALETA_PRECISAO_LARANJA.md`.

## 2026-06-09 (sessão 9) — Decisão abstrata cai quando vira pixel; doc supersede
No Q&A o Mestre escolheu "🗑 exclui / ✕ só fecha"; ao ver na tela, aprovou o **botão ✕** da lista de programas como padrão único de exclusão (nas 3 seções) — revertendo a escolha anterior. Mesmo padrão da lição da FASE 1: a aprovação **no componente em tela** vence a decisão no papel.
- **Regra prática:** quando uma decisão é superada, **atualizar o documento fonte da verdade na hora** (anotar "substitui X") para o próximo agente não reabrir. Aqui: `docs/CORRECOES_MOCKUP.md` item 5 + seção de decisões.
- **Polimento ≠ redesign:** o que mais transmite "fofo/infantil" é o **arredondamento excessivo (pílulas)**, o **brilho glossy** e **emojis coloridos decorativos** — reduzir esses três (raios menores, sombras sóbrias, glifos neutros) profissionaliza sem tocar em layout/fluxo/contraste.

## 2026-06-10 (sessão 10) — Protótipo precisa REAGIR: estado vivo + feedback, não só telas
Após implementar os 17 itens, o Mestre revisou clicando e cobrou comportamento, não aparência: "ao selecionar, tem que tomar cor e os números subirem". Lições da rodada de revisão:
- **Contadores/estados orientados a dados e ao vivo:** marcar um programa deve mudar cor da linha + "Programas"/"Alterações"/escopo dos cards + nota "X de Y marcados" + travar "Executar" se 0 marcados. Guardar valor fixo no card (`prog` no add) quebra isso — calcular ao vivo (`selectedCount()` no `renderSummary`).
- **Alvo de clique generoso:** selecionar pela **linha inteira** (delegação no `#files`), não só no quadradinho. Quadrado desmarcado **precisa de borda** (branco sobre card branco some).
- **Feedback visível (toast)** em cada ação simulada — o Mestre não-técnico precisa ver que "funcionou".
- **Não deixar clique morto:** todo botão faz algo (Biblioteca de Códigos não abria nada; "+ Adicionar programa(s)" só com lista vazia). Modal: abrir limpo+focado, fechar por ✕/Esc/fundo, anti-duplicado.
- **Agrupar por tema, sem redundância:** controles de "configuração" (seletor ativo + salvar + adicionar código) moram no **bloco Configurações**, não no header; seletor ao lado do título dispensa rótulo "Config." repetido. Rótulo solto em cima de **um só** controle numa fileira desalinha.

## 2026-06-11 (sessão refino v4) — Escopo enxuto: não disparar workflow/pesquisa extensa sem o Mestre pedir
O Mestre pediu "resolver as pontas soltas, uma pergunta de cada vez". Em vez disso, disparei um workflow multi-agente (62 agentes, ~1,2M tokens) para mapear TODAS as pendências — estourou o limite de sessão e o Mestre cortou ("não autorizei isso").
- **Regra prática:** trazer só o que foi explicitamente mencionado/pedido; **uma pergunta por vez**, com recomendação em 1º lugar. Não escalar para fan-out/Workflow sem autorização explícita — Ultracode/Workflow **não** é o default deste projeto.
- **Processo de plano:** o pipeline `/plan-*` opera no `PLAN.md` (raiz). Quando o detalhamento vive numa change OpenSpec, definir o **PLAN.md como fonte de verdade** e regenerar o `tasks.md` a partir dele (mantê-los em sincronia).
- **Arquivar change não-implementada polui specs:** usar `openspec archive --skip-specs` guarda o histórico **sem** consolidar os deltas nos specs base (ou descartar a pasta). Foi a escolha do Mestre para a change v2 `redesign-fase2-fidelidade-visual`.
- **Achado:** a "Fase 2" já tinha sido codada uma vez contra o v2 (commit `f28fdb8`) apesar do HANDOFF dizer que não havia começado — sempre conferir o git, não só o HANDOFF. Decisão do Mestre: refazer a UI do zero pro v4, preservando o `core/`.
