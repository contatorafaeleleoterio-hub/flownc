# Prompt de Pesquisa de Mercado — FlowNC (Editor de Lotes CNC)

> Gerado por Claude Code (Opus 4.8) seguindo o briefing `CLAUDE_CODE_PROMPT_market_research_generator.md`.
> Destino de execução: **Manus IA**. Idioma do prompt e do relatório: **Português (BR)**.

---

## Instruções de Uso

**Onde rodar:** cole o conteúdo da seção "Prompt Completo" em uma sessão nova do Manus IA (manus.im), no campo de tarefa inicial.

**Configurações recomendadas de sessão:**
- Use o modo de **pesquisa profunda / agente autônomo** (deep research). Se a sua conta tiver **Wide Research**, ative-a — esta tarefa tem 10 domínios independentes (A–J) que se beneficiam de pesquisa paralela.
- **Não fragmente a tarefa em vários prompts.** O prompt foi escrito para ser executado de uma vez, com escopo fechado. Quebrar em pedaços perde contexto entre etapas e gasta mais créditos.
- **Créditos:** esta é uma tarefa longa (pesquisa multi-fonte + relatório extenso). Reserve créditos suficientes para uma execução completa. O prompt já instrui o Manus a evitar caminhos desnecessários para economizar créditos.
- Tenha em mãos a URL do site do FlowNC **se já existir** (hoje não existe — o prompt já assume isso). Se passar a existir, cole a URL no início.

**Limitações do Manus que o prompt já contorna:**
- O Manus **não acessa conteúdo atrás de login/paywall nem resolve CAPTCHA** — o prompt prioriza fontes públicas (dados gratuitos de SEMrush/Ahrefs, G2, Capterra, Reddit, Product Hunt, Google Trends) e pede que o agente declare quando um dado estiver indisponível em vez de travar.
- Contexto pode fragmentar em projetos muito grandes — por isso o prompt fixa um **fluxo único** (pesquisar → sintetizar → relatório) e um formato de entrega rígido.

**O que esperar como output:** um relatório único em português, com índice navegável, tabelas comparativas, rankings por impacto × velocidade e uma recomendação final de monetização priorizada por **time-to-revenue**. 

**Tempo estimado:** de 30 a 90 minutos de execução assíncrona, dependendo da carga da plataforma e da profundidade. Deixe rodando em segundo plano.

---

## Prompt Completo

```
Você é um estrategista sênior de go-to-market e pesquisa de mercado para produtos de software B2B de nicho técnico, com especialização em SEO, AEO (otimização para mecanismos de resposta por IA) e monetização de produtos indie. Sua tarefa é produzir uma pesquisa de mercado exaustiva e acionável para o produto descrito abaixo.

Antes de escrever o relatório final, pense passo a passo: mapeie o mercado, identifique os concorrentes reais (verificando que cada site está no ar), valide os dados em pelo menos duas fontes quando possível e só então sintetize. Se um dado não puder ser encontrado em fonte pública, declare explicitamente "dado não encontrado" — nunca invente números, volumes de busca, preços ou estatísticas.

CRITÉRIO CENTRAL DA PESQUISA: priorize todas as recomendações pela VELOCIDADE DE MONETIZAÇÃO (time-to-revenue). Sempre que houver mais de um caminho, ordene do que gera receita mais rápido para o mais demorado, e justifique.

========================================================
CONTEXTO DO PRODUTO — FlowNC
========================================================

FlowNC é um aplicativo desktop para Windows voltado à edição em LOTE de programas CNC (arquivos de código G/M, extensões .NC, .MPF, .TAP, .ISO, .MIN). Ele permite que operadores e programadores de máquinas CNC substituam códigos (ex.: trocar um código M por outro) em dezenas ou centenas de arquivos de uma só vez, com segurança.

Diferenciais centrais:
- Funciona 100% OFFLINE e é PORTÁTIL (roda de um pen drive, sem instalação) — pensado para o chão de fábrica, ambientes sem internet.
- Faz BACKUP versionado automático dos arquivos originais antes de qualquer alteração em lote.
- VALIDAÇÃO rigorosa: detecta conflitos entre regras e respeita o "boundary" do código CNC (não confunde M8 com M80).
- Editor de texto integrado por arquivo, com localizar/substituir, realce de ocorrências e salvamento atômico com conferência de integridade (SHA-256).
- Preserva a codificação original do arquivo (UTF-8, ANSI, UTF-16) e o tipo de quebra de linha — crítico para máquinas CNC antigas.

Público principal: operadores e programadores CNC em pequenas e médias indústrias (metalurgia, usinagem, plástico, madeira), com forte presença de controladores FANUC. Mercado primário no BRASIL (conteúdo e comunicação em português), com potencial de expansão global em inglês.

Estágio: produto funcional, desenvolvido por UM único desenvolvedor (indie). Ainda NÃO possui site, presença web nem modelo de negócio formalizado — o modelo de monetização deve ser RECOMENDADO por esta pesquisa.

Concorrência a investigar (ponto de partida, não exaustivo): CIMCO Edit, Predator Editor/DNC, G-Wizard Editor, NC Viewer, CamBam, Universal G-code Sender, NCSimul, além de alternativas indiretas como Notepad++ com plugins, VSCode com regex, e scripts caseiros em PowerShell/Python.

========================================================
ESCOPO OBRIGATÓRIO DA PESQUISA (A–J)
========================================================

Cubra TODOS os domínios abaixo. Em cada um, cite as fontes consultadas.

<A. ANÁLISE COMPETITIVA>
- Mapeie concorrentes diretos (editores/substituidores de G-code) e indiretos (editores genéricos, scripts). Para cada um: nome, URL (confirme que está no ar), posicionamento, plataforma, faixa de preço e modelo de cobrança.
- Tabela comparativa: funcionalidades x pontos fortes x pontos fracos, com o FlowNC incluído na comparação.
- Identifique os GAPS de mercado e janelas de posicionamento que nenhum concorrente ocupa (especialmente: offline+portátil, backup automático, suporte e interface em português).
</A>

<B. PALAVRAS-CHAVE E SEO TRADICIONAL>
- Clusters de palavras-chave por intenção (informacional / comercial / transacional), em PT-BR e EN. Inclua cauda longa e perguntas reais de usuários.
- Para cada cluster: volume de busca estimado, CPC estimado e dificuldade — use dados públicos (Google Keyword Planner, dados gratuitos de SEMrush/Ahrefs, AnswerThePublic, AlsoAsked, "People Also Ask"). Declare a metodologia/fonte de cada número.
- Estratégia on-page: estrutura de conteúdo, headings, meta tags, tipos de página.
- Estratégia off-page: link building no nicho CNC (fóruns, diretórios de software, publicações técnicas), autoridade de domínio, citações.
</B>

<C. AEO / OTIMIZAÇÃO PARA BUSCA POR IA>
- Estratégias para o FlowNC aparecer nas RESPOSTAS de ChatGPT/SearchGPT, Perplexity, Google AI Overviews/Gemini, Microsoft Copilot, Claude e Grok.
- Formatos e estruturas de conteúdo privilegiados por LLMs ao citar fontes (FAQ estruturado, definições diretas, tabelas, schema markup, formato pergunta→resposta direta→desenvolvimento).
- Como construir autoridade semântica para ser citado por IA (E-E-A-T, consistência de informação entre fontes, dados originais, presença em diretórios como G2/Capterra/AlternativeTo/Product Hunt).
- Casos documentados de sucesso em AEO/GEO (Generative Engine Optimization).
- Comparação direta AEO x SEO tradicional: em qual cenário cada um entrega resultado mais RÁPIDO para um produto novo de nicho técnico. Liste robots.txt / crawlers de IA (GPTBot, PerplexityBot, ClaudeBot, etc.) a permitir.
</C>

<D. GOOGLE REDE DE PESQUISA (PAID SEARCH)>
- Estrutura recomendada de campanhas e grupos de anúncio para este nicho.
- Palavras-chave de alta intenção comercial com CPC estimado.
- Copy sugerida: headlines, descriptions e extensões de anúncio (em português).
- Estratégia de lances recomendada (Maximize Conversions, Target CPA, etc.) e por quê.
- Orçamento mínimo viável para validar (teste) e para escalar.
- Principais erros a evitar no Google Ads para software técnico de nicho.
</D>

<E. PÁGINA DE VENDAS / LANDING PAGE>
- Hierarquia de seções recomendada e lógica narrativa.
- Framework de copy mais adequado ao nicho (AIDA, PAS, StoryBrand ou outro) — justifique a escolha para um público técnico e cético.
- Prova social específica do segmento industrial/CNC.
- Gatilhos de conversão de maior impacto para o público-alvo.
- Posicionamento e design do CTA principal e secundários.
- Benchmarks de taxa de conversão para software B2B de nicho (visitante→lead, lead→cliente / download→compra).
</E>

<F. ESTRATÉGIAS DE MONETIZAÇÃO>  [DOMÍNIO PRIORITÁRIO]
- Modelos praticados no segmento: freemium, assinatura, licença perpétua (one-time), por uso, híbrido. Quais os concorrentes usam.
- Faixas de preço e ticket médio do segmento (com fontes — páginas de pricing dos concorrentes, G2, Capterra).
- RANKING das estratégias por TIME-TO-REVENUE — da que gera receita mais rápido à mais lenta, considerando que é um produto indie, sem audiência prévia e sem site.
- Upsell, cross-sell e expansão de receita aplicáveis (ex.: licença por máquina vs. por planta, pacotes de catálogos de código, suporte premium).
- Estimativas de LTV e CAC típicos do segmento.
- Estratégias de retenção e redução de churn.
</F>

<G. CANAIS DE AQUISIÇÃO>
- RANKING dos canais por impacto × velocidade de resultado × custo.
- Orgânicos: SEO, comunidades técnicas (CNCZone, Practical Machinist, Reddit r/CNC e r/machining, grupos de Facebook/WhatsApp de programadores CNC no Brasil), Product Hunt, newsletters, YouTube.
- Pagos: Google Ads vs. Meta Ads vs. LinkedIn Ads — qual é mais adequado a este nicho e por quê.
- Parcerias e distribuição alternativa: distribuidores de máquinas CNC (Fanuc, Mazak, DMG Mori, Romi), escolas técnicas/SENAI, marketplaces de software.
- Táticas de growth hacking com validação documentada no segmento.
</G>

<H. PERSONAS E ICP>
- Perfil detalhado do cliente ideal: cargo, setor, porte de empresa, dores, objetivos, gatilhos de compra.
- Crie ao menos 3 personas (ex.: programador CNC em PME, operador que também edita programas, supervisor/engenheiro de manufatura).
- Objeções mais comuns na jornada de venda e como superá-las por persona.
- Jornada de compra: touchpoints, ciclo, pontos de decisão.
- Onde e como essas personas buscam, avaliam e compram software (incluindo o que perguntariam a um assistente de IA).
</H>

<I. TENDÊNCIAS DE MERCADO>
- Direção do mercado de software CNC e automação industrial nos próximos 12–24 meses.
- Tecnologias emergentes (IA em CAM, Industry 4.0, cloud manufacturing) e seu impacto.
- Riscos regulatórios, competitivos ou de mercado.
- Oportunidades emergentes ainda pouco exploradas (especialmente no Brasil/lusófono).
</I>

<J. VALIDAÇÃO RÁPIDA E ROADMAP>
- Abordagens de MVP de marketing para testar hipóteses com custo e tempo mínimos.
- Métricas de validação e thresholds de go/no-go por canal.
- Roadmap de ações priorizadas para 30 / 60 / 90 dias.
- RECOMENDAÇÃO FINAL: qual estratégia de monetização e qual canal atacar PRIMEIRO, justificando pela velocidade de retorno.
</J>

========================================================
FONTES A CONSULTAR
========================================================
- SimilarWeb (tráfego e canais dos concorrentes)
- SEMrush / Ahrefs — dados públicos (keywords, dificuldade, CPC)
- Google Trends (demanda e sazonalidade, comparar termos PT-BR e EN)
- G2, Capterra, Trustpilot (reviews, comparativos e preços dos concorrentes)
- Product Hunt (lançamentos e recepção do nicho)
- Reddit, Hacker News, fóruns CNC (CNCZone, Practical Machinist), grupos brasileiros (dores e linguagem real do usuário)
- Relatórios de mercado de acesso público: Gartner, Statista, IDC, Grand View Research, ABIMAQ (dados do Brasil)
- Páginas de pricing dos concorrentes identificados
- Artigos e estudos especializados sobre AEO / GEO (2024–2026)

Se uma fonte exigir login, paywall ou CAPTCHA, NÃO trave: registre a limitação, busque o mesmo dado em fonte pública alternativa e siga. Evite caminhos desnecessários para economizar tempo e créditos.

========================================================
FORMATO DA ENTREGA
========================================================
Entregue UM relatório único em português (BR), com:
1. Sumário executivo (1 página): principais achados + as 3 ações prioritárias + a recomendação de monetização mais rápida.
2. Índice navegável.
3. Uma seção por domínio (A–J), claramente delimitada.
4. TABELAS COMPARATIVAS para: concorrentes (A), clusters de palavras-chave (B), canais de aquisição (G) e modelos de monetização (F).
5. RANKINGS ordenados por impacto × velocidade sempre que aplicável (F, G, J).
6. CITAÇÃO DE FONTES (URL e data) ao final de cada seção.
7. Conclusão acionável: a estratégia principal de monetização recomendada e o roadmap 30/60/90 dias.

Comece pela pesquisa. Só escreva o relatório depois de coletar e cruzar os dados. Não peça confirmação — execute a pesquisa completa e entregue o relatório final.
```

---

## Notas de Design

Decisões de prompt engineering aplicadas (Claude Opus 4.8) e por quê:

**1. Role prompting específico (não genérico).** Em vez de "você é um analista", o papel fixa três especialidades — go-to-market, SEO/AEO e monetização indie — porque a documentação da Anthropic mostra que papéis específicos elevam a precisão em tarefas analíticas. O papel também ancora o agente no perfil de produto (B2B técnico de nicho), evitando recomendações genéricas de SaaS de massa.

**2. Chain-of-thought explícito antes do output.** A instrução "pense passo a passo: mapeie → identifique → valide → sintetize" força o agente a pesquisar antes de redigir. Para o Manus (agente autônomo), isso é crítico: sem essa ordem, agentes tendem a redigir cedo e preencher lacunas com suposições. Reforçado por "só escreva o relatório depois de coletar e cruzar os dados".

**3. XML tags para delimitar os 10 domínios (A–J).** Tags como `<F. ESTRATÉGIAS DE MONETIZAÇÃO>` segmentam o escopo de forma inequívoca. Isso reduz o risco de o agente fundir ou pular domínios e facilita o mapeamento 1:1 entre escopo pedido e seções do relatório. É a técnica de XML tags da Anthropic aplicada a um destinatário-agente.

**4. Critério único de priorização declarado no topo e repetido.** "Velocidade de monetização (time-to-revenue)" aparece logo após o papel e é reforçado em F, G e J. Repetir o critério de decisão em pontos-chave evita que o agente perca o norte ao longo de uma execução longa.

**5. Anti-alucinação explícito.** "Nunca invente números… declare 'dado não encontrado'." Pesquisa de mercado é exatamente onde LLMs inventam volumes e preços plausíveis. A instrução transforma ausência de dado em saída aceitável, o que aumenta a confiabilidade do relatório.

**6. Contexto de produto sintético, não documentação técnica.** Conforme o critério de qualidade do briefing, incluí só o que direciona a pesquisa (proposta de valor, diferenciais, público, estágio, concorrentes-semente) e omiti detalhes de implementação (PySide6, arquitetura de código, OpenSpec) — irrelevantes para mercado e que só diluiriam o foco do agente.

**7. Adaptações específicas ao Manus (pesquisa volátil da Fase 1).** Três ajustes vieram das limitações reais documentadas da plataforma: (a) instrução para **não travar em paywall/CAPTCHA** e buscar fonte alternativa — o Manus para diante de login em vez de contornar; (b) **fluxo único pesquisar→sintetizar→relatório** com escopo fechado, porque o Manus perde qualidade quando a tarefa é fragmentada ou o contexto estoura; (c) **economia de créditos** ("evite caminhos desnecessários"), já que tarefas longas no Manus consomem créditos rápido. As instruções de uso recomendam ativar **Wide Research** quando disponível, pois os 10 domínios são independentes e paralelizáveis.

**8. Formato de entrega rígido e verificável.** O Manus produz com mais consistência quando o formato é especificado item a item (sumário → índice → seções A–J → tabelas nomeadas → rankings → fontes → conclusão). Nomear *quais* seções exigem tabela e *quais* exigem ranking remove ambiguidade e garante que o entregável seja diretamente acionável para decisões de marketing.

**9. Fecho que dispensa confirmação.** "Não peça confirmação — execute a pesquisa completa e entregue o relatório final." Agentes autônomos às vezes pausam pedindo aprovação intermediária; isso encerra a tarefa antes da hora e gasta uma rodada. O fecho garante execução ponta a ponta.

---

*Fontes da pesquisa volátil sobre o Manus IA (Fase 1.2):*
- [Context Engineering for AI Agents — Manus](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus)
- [Manus Wide Research](https://manus.im/blog/manus-wide-research-solve-context-problem)
- [Otimização de uso e créditos do Manus — Ithy](https://ithy.com/article/manus-im-credit-control-rbqh7xal)
- [Prompt Engineering for Manus 1.5 — Skywork](https://skywork.ai/blog/ai-agent/prompt-engineering-manus-1-5-structure-guardrails-evaluation/)
