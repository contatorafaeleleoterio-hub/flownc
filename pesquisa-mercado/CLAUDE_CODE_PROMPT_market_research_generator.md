# CLAUDE CODE — GERAÇÃO DE PROMPT DE PESQUISA DE MERCADO PARA MANUS IA

---

## VISÃO GERAL DA MISSÃO

Esta tarefa possui duas camadas:

1. **Esta instrução** (Prompt A) orienta você, Claude Code, a pesquisar, sintetizar e **gerar** um prompt.
2. **O prompt gerado** (Prompt B) será usado na plataforma **Manus IA** para executar uma pesquisa de mercado exaustiva sobre o sistema documentado neste projeto.

Seu produto final é o Prompt B — otimizado para Manus IA, construído com as melhores práticas de prompt engineering para Claude Opus 4.8, e calibrado para identificar as **estratégias de monetização com maior velocidade de retorno** para o sistema.

---

## PAPEL E RESPONSABILIDADE

Você é um especialista sênior em prompt engineering e estratégia de go-to-market. Sua capacidade analítica deve ser exercida ao máximo nesta tarefa, que exige síntese de múltiplas fontes técnicas antes de produzir qualquer output.

**Não gere o Prompt B antes de concluir todas as fases de pesquisa abaixo.**

---

## FASE 1 — PESQUISA DE REFERÊNCIAS TÉCNICAS

Execute cada etapa na sequência. Documente os aprendizados internamente — eles alimentarão diretamente a qualidade do Prompt B.

---

### 1.1 Melhores Práticas de Prompt Engineering — Claude Opus 4.8

Acesse e processe as seguintes URLs da documentação oficial da Anthropic:

```
https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview
https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/use-xml-tags
https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/chain-of-thought
https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/extended-thinking-tips
https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/be-clear-and-direct
https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/give-claude-a-role
https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/use-examples
https://docs.anthropic.com/en/docs/about-claude/models/
```

**Registre internamente:**

- Como o role prompting aumenta foco e qualidade em tarefas analíticas complexas
- Uso correto de XML tags para segmentar seções de prompt e delimitar contexto
- Como induzir chain-of-thought para tarefas de pesquisa e síntese multifonte
- Como instruir o modelo a usar extended thinking para raciocínio de alta profundidade
- Técnicas específicas para tarefas de agente (multi-step, uso de ferramentas, geração de relatórios)
- Diferenças relevantes entre Opus 4.8 e versões anteriores no que tange a capacidade analítica

---

### 1.2 Plataforma Manus IA — Capacidades, Limitações e Melhores Práticas

Acesse o site oficial e qualquer documentação disponível:

```
https://manus.im
```

Em seguida, execute buscas na web pelas seguintes queries:

```
Manus AI agent prompting best practices 2025
Manus IA research prompt guide
how to write effective prompts for Manus AI agent
Manus AI deep research prompt examples
Manus AI agent limitations and workarounds
```

Complemente consultando Reddit, YouTube, X/Twitter e Hacker News por experiências da comunidade.

**Registre internamente:**

- Capacidades do agente Manus: web browsing, navegação em profundidade, geração de relatórios, execução de tarefas paralelas
- Limitações conhecidas e como contorná-las via estrutura de prompt
- Estrutura de prompt que maximiza qualidade, cobertura e profundidade das entregas
- Formatos de output que o Manus produz com maior consistência (tabelas, relatórios estruturados, rankings)
- Qualquer parâmetro ou configuração de sessão que impacte a qualidade da pesquisa

---

### 1.3 Leitura Completa da Documentação do Projeto

Leia **todos** os arquivos relevantes disponíveis neste projeto. Priorize:

- `CLAUDE.md`
- `HANDOFF.md`
- Qualquer PRD, README, especificação de produto ou documento técnico existente

**Sintetize internamente:**

- Proposta de valor central e problema resolvido
- Público-alvo e perfil do usuário ideal
- Diferenciais competitivos identificados
- Estado atual de desenvolvimento e hipóteses de produto
- Qualquer dado de posicionamento ou mercado já mapeado pela equipe

---

## FASE 2 — SÍNTESE ANALÍTICA INTERNA

Antes de escrever o Prompt B, realize uma análise interna aprofundada respondendo às seguintes questões. Seu raciocínio aqui determina diretamente a qualidade do output.

**2.1 Técnicas de Prompt Engineering**
Quais técnicas identificadas para Claude Opus 4.8 são mais eficazes quando o destinatário é um agente autônomo de pesquisa (Manus), em vez de um modelo em sessão conversacional? Qual combinação de role prompting + XML tags + chain-of-thought maximiza a profundidade analítica para esta tarefa específica?

**2.2 Adaptação para Manus IA**
Como estruturar a tarefa de pesquisa para que o Manus mantenha foco, profundidade e produza entregas acionáveis? Quais armadilhas de prompt devem ser evitadas com base nas limitações identificadas?

**2.3 Síntese de Contexto do Produto**
Que síntese mínima e suficiente do sistema deve ser incluída no Prompt B para que o Manus direcione a pesquisa corretamente — sem reproduzir documentação técnica desnecessária?

**2.4 Estrutura de Output**
Qual formato de entrega torna os resultados da pesquisa diretamente acionáveis para decisões de marketing e monetização? Como o Prompt B deve instruir o Manus sobre o relatório final?

---

## FASE 3 — GERAÇÃO DO PROMPT B PARA MANUS IA

Com base em toda a pesquisa e síntese anteriores, escreva o Prompt B completo. Ele deve:

- Aplicar explicitamente as melhores práticas de prompt engineering identificadas na Fase 1
- Ser **autocontido**: funcionar em sessão Manus sem contexto externo adicional
- Incluir síntese de contexto do produto (derivada da Fase 1.3) sem reproduzir documentação técnica
- Orientar o Manus a pesquisar fontes primárias e confiáveis
- Priorizar estratégias pela **velocidade de monetização** — este é o critério central da pesquisa
- Instruir claramente sobre profundidade esperada e formato das entregas

---

### ESCOPO OBRIGATÓRIO DA PESQUISA

O Prompt B deve cobrir **integralmente** os seguintes domínios:

<scope>

**A. Análise Competitiva**
- Mapeamento de concorrentes diretos e indiretos: nome, URL, posicionamento, faixa de preço
- Tabela comparativa de funcionalidades, pontos fortes e fracos
- Gaps de mercado e janelas de posicionamento diferenciado

**B. Palavras-Chave e SEO Tradicional**
- Clusters de palavras-chave por intenção (informacional / comercial / transacional)
- Volume de busca, CPC estimado e dificuldade por cluster
- Estratégia on-page: estrutura de conteúdo, headings, meta tags
- Estratégia off-page: link building, autoridade de domínio, citações

**C. AEO / AI Search Optimization**
- Estratégias para aparecer nas respostas de ChatGPT, Perplexity, Claude, Gemini e Grok
- Estruturas e formatos de conteúdo privilegiados por modelos de linguagem em suas respostas
- Autoridade semântica: como construí-la para ser citado por IA
- Casos de sucesso documentados em AEO / GEO (Generative Engine Optimization)
- Comparação AEO vs. SEO tradicional: quando cada um entrega resultados mais rápidos

**D. Google Rede de Pesquisa — Paid Search**
- Estrutura recomendada de campanhas e grupos de anúncio para o nicho
- Palavras-chave de alta intenção comercial com CPC estimado
- Copy sugerida: headlines, descriptions e extensões de anúncio
- Estratégia de bidding recomendada (Target CPA, Maximize Conversions, etc.)
- Orçamento mínimo viável para validação e escala
- Principais erros a evitar no Google Ads para este segmento

**E. Estrutura da Página de Vendas / Landing Page**
- Hierarquia de seções recomendada e lógica narrativa
- Framework de copy mais adequado ao nicho (AIDA, PAS, StoryBrand ou outro — justificar)
- Elementos de prova social específicos para o segmento
- Gatilhos de conversão de maior impacto para o público-alvo
- Posicionamento e design ideal do CTA principal e secundários
- Benchmarks de taxa de conversão para o segmento (visitante → lead, lead → cliente)

**F. Estratégias de Monetização**
- Modelos praticados no mercado: freemium, subscription, one-time, usage-based, hybrid
- Faixas de preço e ticket médio do segmento
- Ranking das estratégias por **time-to-revenue** (da mais rápida à mais demorada)
- Modelos de upsell, cross-sell e expansão de receita aplicáveis
- Estimativas de LTV e CAC típicos do segmento
- Estratégias de retenção e redução de churn

**G. Canais de Aquisição de Usuários**
- Ranking por impacto × velocidade de resultado × custo
- Canais orgânicos: SEO, comunidades, Product Hunt, newsletters, redes sociais
- Canais pagos: Google Ads, Meta Ads, LinkedIn Ads — comparativo de adequação ao nicho
- Parcerias, marketplaces, integrações e canais de distribuição alternativos
- Estratégias de growth hacking com validação documentada no segmento

**H. Personas e ICP (Ideal Customer Profile)**
- Perfil detalhado do cliente ideal: cargo, setor, porte de empresa, dores, objetivos, gatilhos de compra
- Objeções mais comuns na jornada de venda e argumentos de superação por persona
- Jornada de compra típica: touchpoints, ciclo e pontos de decisão
- Onde e como essas personas buscam, avaliam e compram soluções

**I. Tendências de Mercado**
- Direção do mercado para os próximos 12-24 meses
- Tecnologias emergentes e seus impactos no segmento
- Riscos regulatórios, competitivos ou de mercado
- Oportunidades emergentes ainda não amplamente exploradas

**J. Estratégia de Validação Rápida e Roadmap**
- Abordagens de MVP de marketing para testar hipóteses com custo e tempo mínimos
- Métricas de validação e thresholds de go/no-go por canal
- Roadmap de ações prioritárias nos primeiros **30 / 60 / 90 dias**
- Recomendação final: qual estratégia atacar primeiro e por quê

</scope>

---

### REQUISITOS DE FORMATO DAS ENTREGAS A INSTRUIR O MANUS

O Prompt B deve instruir o Manus a entregar:

- Relatório com **índice navegável** e seções claramente delimitadas
- **Tabelas comparativas** para análise de concorrentes, canais e modelos de monetização
- **Rankings de prioridade** ordenados por impacto × velocidade sempre que aplicável
- **Conclusão acionável** com recomendação clara da estratégia principal de monetização
- **Citação de fontes** para todas as informações pesquisadas

**Fontes que o Prompt B deve instruir o Manus a consultar:**

```
- SimilarWeb (tráfego e canais de concorrentes)
- SEMrush / Ahrefs — dados públicos (keywords, dificuldade, CPC)
- Google Trends (demanda e sazonalidade)
- G2, Capterra, Trustpilot (reviews, comparativos e preços de concorrentes)
- Product Hunt (lançamentos e recepção do nicho)
- Reddit, Hacker News, comunidades do segmento (dores e linguagem real do usuário)
- Relatórios de mercado: Gartner, Statista, IDC — dados de acesso público
- Sites e páginas de pricing dos concorrentes identificados
- Fontes de AEO: artigos especializados, estudos sobre Generative Engine Optimization
```

---

## SAÍDA DESTA TAREFA

Salve o resultado final em:

```
docs/MANUS_MARKET_RESEARCH_PROMPT.md
```

Estruture o arquivo com exatamente as seguintes seções:

```
# Prompt de Pesquisa de Mercado — [Nome do Sistema]

## Instruções de Uso
Como aplicar este prompt no Manus IA, configurações recomendadas de sessão,
e o que esperar como output e em quanto tempo.

---

## Prompt Completo
[Prompt pronto para copiar e colar diretamente no Manus IA]

---

## Notas de Design
Decisões técnicas e de prompt engineering tomadas na construção —
justificando cada escolha estrutural com base nas referências pesquisadas.
```

---

## CRITÉRIOS DE QUALIDADE — VALIDAÇÃO ANTES DE SALVAR

Antes de salvar o arquivo, valide cada item abaixo:

- [ ] O Prompt B é autocontido: funciona sem contexto externo no Manus
- [ ] As técnicas de prompt engineering do Opus 4.8 estão explicitamente aplicadas e justificadas nas Notas de Design
- [ ] O escopo completo da pesquisa (A a J) está integralmente coberto
- [ ] O Manus recebe instruções claras sobre profundidade esperada, fontes a consultar e formato de entrega
- [ ] O critério de **velocidade de monetização** está explícito como prioridade central
- [ ] As hipóteses de Google Rede de Pesquisa e AEO/AI Search estão tratadas com profundidade comparativa
- [ ] Documentação técnica de implementação NÃO foi reproduzida no Prompt B — apenas contexto de produto e mercado
- [ ] O Prompt B não gera ambiguidade sobre o que o Manus deve pesquisar, em qual profundidade, e como entregar

---

*Este prompt foi estruturado para maximizar o desempenho analítico do Claude Opus 4.8 via role definition explícito, segmentação em fases sequenciais, síntese interna antes do output, e especificação granular dos critérios de qualidade.*
