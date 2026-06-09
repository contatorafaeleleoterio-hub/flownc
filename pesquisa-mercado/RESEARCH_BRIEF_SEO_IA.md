# Briefing de Pesquisa — Benchmarking, Mercado e SEO para IA
## FlowNC — Editor de Lotes CNC para Windows

**Versão:** 1.0  
**Data de criação:** 2026-06-08  
**Destinatário:** Agente de IA responsável pela pesquisa  
**Autonomia:** Total — execute todas as seções sem aguardar instruções adicionais  

---

## 1. CONTEXTO DO PRODUTO

### 1.1 O que é o FlowNC

FlowNC é um aplicativo desktop Windows para **edição em lote de programas CNC**. Ele permite que operadores e programadores CNC realizem substituições de códigos G/M em múltiplos arquivos simultaneamente, com validação automática, editor integrado por arquivo e publicação segura com backup versionado.

O produto é distribuído como um **executável portátil** (`.exe` onedir), sem instalação, ideal para uso em pen drive em ambientes industriais.

### 1.2 Funcionalidades principais

- **Compositor de edições:** montagem de regras origem→destino usando uma biblioteca de códigos G/M Fanuc editável
- **Edição em lote:** aplicação das regras em múltiplos arquivos `.NC`/`.MPF`/`.TAP` de uma só vez
- **Editor integrado por arquivo:** editor de texto estilo Bloco de Notas com localizador, realce de ocorrências, substituição um a um ou global e salvamento in-place atômico
- **Validação:** detecção de conflitos entre regras, boundary CNC rigoroso (`M8` ≠ `M80`) e conferência SHA-256 antes/depois de salvar
- **Backup versionado:** cópia datada dos originais antes de qualquer publicação em lote
- **Preservação de codificação:** UTF-8, UTF-8-BOM, UTF-16, ANSI/cp1252 e EOL CRLF/LF preservados byte a byte

### 1.3 Stack técnica

- Python 3.11+, PySide6 (Qt Widgets), PyInstaller
- Interface: duas colunas dinâmicas (60/40 ↔ 40/60), biblioteca de códigos G/M, perfis de máquina
- Distribuição: EXE portátil Windows, sem dependências externas

### 1.4 Estágio atual

Produto funcional em refinamento de design (Fase 2 de 3 do redesign visual). EXE já entregue em produção (versão beta de uso interno). Ainda sem site ou presença web estabelecida.

### 1.5 Modelo de negócio (a definir)

Ainda não formalizado. Possibilidades em aberto: licença perpétua por máquina, SaaS desktop com assinatura anual, freemium com limitação de regras/arquivos, licenciamento por empresa/planta industrial.

---

## 2. OBJETIVO DA PESQUISA

Produzir um **plano completo de benchmarking, pesquisa de mercado e estratégia de SEO** que permita, em seguida, criar um plano de execução para:

1. Criar e otimizar o site do FlowNC
2. Posicionar o produto nos resultados de busca tradicionais (Google, Bing)
3. Posicionar o produto para ser descoberto, citado e recomendado por **agentes de IA e sistemas de busca generativa** (ChatGPT, Perplexity, Claude, Gemini, Copilot, SearchGPT e similares)
4. Definir estratégia de conteúdo e comunicação para o nicho de automação industrial e programação CNC

---

## 3. SEÇÕES OBRIGATÓRIAS DA PESQUISA

Execute cada seção completamente antes de passar para a próxima. Documente fontes e raciocínio em cada resposta.

---

### SEÇÃO A — BENCHMARKING DE MERCADO

#### A.1 — Panorama do mercado de software CNC

Pesquise e documente:

- Tamanho estimado do mercado global de software para CNC (CAM, editores, pós-processadores, verificadores de código). Inclua projeções para 2025–2030.
- Principais segmentos: CAM (geração de código), editores de código G/M, simuladores, DNC (Direct Numeric Control), ferramentas de verificação/validação.
- Taxa de adoção de ferramentas desktop vs. web vs. SaaS no ambiente industrial.
- Principais países/regiões consumidores: EUA, Alemanha, Japão, China, Brasil.
- Barreiras de entrada: ambientes air-gapped (sem internet), resistência à mudança em chão de fábrica, certificação/homologação de software.
- Tendências: integração com Industry 4.0, cloud manufacturing, edge computing em CNCs, adoção de IA em CAM.

#### A.2 — Posicionamento do FlowNC no mercado

Avalie onde o FlowNC se encaixa considerando:

- Segmento: editor/substituidor de código G-code, não é CAM nem simulador
- Diferencial principal: operação offline, portátil (pen drive), simples e seguro
- Público imediato: operadores de máquina e programadores CNC em PMEs industriais

Defina: é um produto de nicho profundo ou tem potencial de mercado amplo? Justifique com dados.

---

### SEÇÃO B — ANÁLISE DE CONCORRENTES

#### B.1 — Concorrentes diretos

Pesquise ferramentas que realizam **edição ou substituição em lote de código G-code/M-code** para máquinas CNC. Para cada concorrente encontrado, documente:

- Nome e URL do produto
- Descrição funcional (o que faz)
- Preço / modelo de negócio
- Plataforma (Windows, web, plugin de CAM)
- Pontos fortes e fracos em relação ao FlowNC
- Presença online (site, SEO, comunidade, redes sociais)
- Autoridade de domínio estimada (se disponível)
- Palavras-chave que rankeiam
- Avaliações de usuários (se houver)

Exemplos de produtos a investigar (não limitante):
- CNC Editor (genérico)
- G-code editors com função de batch replace
- Macros/scripts em Fanuc, Heidenhain, Siemens para substituição em lote
- Plugins CAM com função de pós-processamento em lote
- Ferramentas específicas de fabricantes de CNC (Fanuc, Siemens, Mazak, DMG Mori)

#### B.2 — Concorrentes indiretos

Pesquise ferramentas que o operador CNC pode usar como alternativa ao FlowNC mesmo não sendo a mesma categoria:

- Editores de texto com suporte a macros/regex (Notepad++, VSCode com extensões)
- Scripts PowerShell/Python caseiros para substituição em lote
- Ferramentas de manipulação de texto em lote (TextSoap, Bulk Text Replacer)
- ERP/MES com módulo de edição de código CNC
- Macros de CAM (Mastercam, GibbsCAM, SolidCAM)

Para cada concorrente indireto: documente por que o usuário migraria do concorrente indireto para o FlowNC.

#### B.3 — Oportunidades de diferenciação identificadas

Com base na análise B.1 e B.2, liste:
- Lacunas de mercado não atendidas pelos concorrentes
- Funcionalidades que o FlowNC possui e os concorrentes não
- Segmentos de usuário sub-servidos
- Argumentos que nenhum concorrente usa na comunicação atual

---

### SEÇÃO C — PALAVRAS-CHAVE ESTRATÉGICAS

#### C.1 — Palavras-chave primárias (intenção de compra / uso direto)

Pesquise e documente volume, dificuldade e CPC estimado para os seguintes clusters. Para cada palavra-chave, inclua variações em português, inglês e espanhol (os três idiomas mais relevantes para o público-alvo):

**Cluster 1 — Edição de G-code:**
- "g-code editor" e variações
- "editar g-code em lote"
- "batch edit g-code"
- "substituir código cnc"
- "find and replace g-code"

**Cluster 2 — Substituição em lote:**
- "batch replace cnc"
- "substituição em lote código cnc"
- "bulk replace g-code"
- "trocar código m-code fanuc"

**Cluster 3 — Programação Fanuc:**
- "editor código fanuc"
- "fanuc g-code editor"
- "programação cnc fanuc"
- "substituir m-code fanuc"

**Cluster 4 — Software CNC para operador:**
- "software cnc operador"
- "ferramenta programação cnc"
- "cnc programming tool"
- "editor programa cnc"

**Cluster 5 — Segurança e backup CNC:**
- "backup programa cnc"
- "salvar programa cnc automaticamente"
- "proteção código cnc"

#### C.2 — Palavras-chave de cauda longa (long-tail)

Pesquise perguntas e termos específicos que programadores/operadores CNC usam ao buscar soluções para problemas que o FlowNC resolve:

- "como substituir código em vários arquivos nc de uma vez"
- "trocar m8 por m80 em todos os programas cnc"
- "substituição em lote arquivos .nc fanuc"
- "editor programa cnc offline windows"
- "como editar múltiplos programas cnc ao mesmo tempo"
- "ferramenta substituição g-code grátis"
- "batch process cnc programs"
- Perguntas em fóruns: CNC Zone, Practical Machinist, Reddit r/CNC, r/machining

#### C.3 — Palavras-chave para SEO de IA (AEO — Answer Engine Optimization)

Identifique as perguntas que usuários fariam a um assistente de IA (ChatGPT, Perplexity, Claude) que o FlowNC deveria responder. Exemplos do tipo:

- "Qual é o melhor software para editar g-code em lote no Windows?"
- "Como faço para substituir um código M em vários programas CNC de uma vez?"
- "Existe alguma ferramenta gratuita para editar arquivos .NC em lote?"
- "O que é um editor de g-code em lote?"
- "Como proteger os originais ao editar programas CNC em lote?"

Para cada pergunta identificada, avalie:
- Qual seria a resposta ideal que o FlowNC poderia fornecer
- Que tipo de conteúdo o site deveria ter para ser citado como fonte por IA
- Se há Featured Snippets ou AI Overviews do Google para esses termos

---

### SEÇÃO D — PESQUISA DE NICHO

#### D.1 — Mapeamento do nicho de programação CNC

Documente:

- Quantos operadores e programadores CNC existem globalmente (estimativa)
- Proporção que usa Fanuc, Siemens, Heidenhain, Mitsubishi, Mazak como controlador
- Perfil de empresa: PME industrial (5–200 máquinas CNC) vs. grandes plantas
- Frequência com que modificam programas existentes vs. criam do zero
- Ferramentas digitais mais utilizadas no dia a dia (CAM, editores, DNC, ERP)
- Grupos e comunidades online: fóruns, LinkedIn, Facebook Groups, YouTube channels

#### D.2 — Dores e frustrações do nicho

Pesquise em fóruns, Reddit, grupos do LinkedIn e YouTube quais são as principais reclamações e problemas que programadores/operadores CNC relatam ao lidar com:

- Edição repetitiva de código G/M em múltiplos arquivos
- Erros após substituições manuais
- Perda de originais
- Incompatibilidade de codificação de arquivos (UTF-8 vs ANSI)
- Dificuldade de rastreabilidade de alterações

#### D.3 — Canais de descoberta do nicho

Onde esse público busca ferramentas e soluções:
- Mecanismos de busca tradicionais
- Grupos Facebook / WhatsApp de técnicos CNC
- Fóruns especializados (CNCZone.com, PracticalMachinist.com)
- YouTube (canais de programação CNC)
- LinkedIn grupos de automação industrial
- Indicação boca a boca entre operadores
- Distribuidores de máquinas CNC (Fanuc, Mazak, DMG Mori, Romi)

---

### SEÇÃO E — PESQUISA DE MERCADO

#### E.1 — Tamanho do mercado endereçável

Calcule ou estime:

- **TAM (Total Addressable Market):** mercado global de software de edição/utilitários CNC
- **SAM (Serviceable Addressable Market):** empresas com máquinas Fanuc que poderiam usar o FlowNC no Brasil, América Latina e mundo lusófono + mercado em inglês
- **SOM (Serviceable Obtainable Market):** fatia realista para um produto indie nos próximos 2 anos

#### E.2 — Tendências de mercado relevantes

Pesquise e documente tendências que impactam o FlowNC:

- Crescimento da automação industrial em PMEs
- Adoção de controles Fanuc vs. Siemens no Brasil e América Latina
- Demanda por ferramentas CNC offline vs. conectadas
- Industry 4.0 e digitalização do chão de fábrica
- Crescimento do mercado de usinagem CNC no Brasil (2020–2026)
- Adoção de ferramentas SaaS em ambientes industriais

#### E.3 — Modelos de negócio do setor

Pesquise como softwares similares são precificados e vendidos:

- Licença perpétua: valores praticados
- Assinatura anual: valores praticados
- Freemium com upgrade pago: exemplos de conversão
- Licenciamento por empresa (site license): valores
- Modelos de distribuição: download direto, GitHub, marketplace de ferramentas CNC

---

### SEÇÃO F — DEFINIÇÃO DE PÚBLICO-ALVO

Com base nas pesquisas anteriores, defina os segmentos de público-alvo do FlowNC. Para cada segmento, documente:

**Formato obrigatório por segmento:**
- Nome do segmento
- Tamanho estimado (quantas pessoas/empresas)
- Características demográficas e profissionais
- Nível técnico (operador de máquina vs. programador CNC vs. engenheiro de manufatura)
- Tipo de empresa (porte, setor industrial)
- Dores principais que o FlowNC resolve
- Objeções mais comuns à compra/adoção
- Canal de descoberta preferido
- Disposição a pagar (R$/US$ por ferramenta similar)

**Segmentos esperados (pesquise e valide):**
1. Programador CNC em PME industrial (metal, plástico, madeira)
2. Operador de máquina que também edita programas
3. Supervisor de produção / engenheiro de manufatura
4. Técnico de manutenção CNC
5. Freelancer de programação CNC
6. Empresa de treinamento CNC

---

### SEÇÃO G — DEFINIÇÃO DE PERSONAS

Crie ao menos **3 personas detalhadas** com base nos públicos identificados na Seção F. Cada persona deve ter:

- **Nome e foto fictícia** (descreva o perfil, sem imagem real)
- **Cargo e empresa** (tipo/porte)
- **Idade e localização**
- **Formação e experiência**
- **Rotina de trabalho** (como usa o CNC no dia a dia)
- **Problema específico** que levou a buscar o FlowNC
- **Como descobriu** o produto
- **Objeções antes de adotar**
- **Resultado esperado após adotar**
- **Frase que esse perfil diria** ao buscar uma solução
- **Palavras-chave que usaria** em uma busca no Google ou ao perguntar a um assistente de IA

---

### SEÇÃO H — ANÁLISE DE INTENÇÃO DE BUSCA

Para cada cluster de palavras-chave identificado na Seção C, classifique a intenção e defina o tipo de conteúdo ideal:

**Tipos de intenção:**
- **Informacional:** quer aprender ("o que é substituição em lote de g-code")
- **Comercial/investigação:** quer comparar ("melhor editor g-code em lote")
- **Transacional:** quer comprar/baixar ("baixar editor g-code windows grátis")
- **Navegacional:** quer ir ao site ("flowNC download")

**Para cada termo analisado, defina:**
- Tipo de intenção
- Tipo de conteúdo que melhor responde (artigo, comparativo, tutorial, landing page, ferramenta gratuita, vídeo)
- Formato ideal para ser recomendado por IA (resposta direta, lista numerada, tabela comparativa, definição estruturada)
- Onde inserir no site (blog, página de produto, FAQ, documentação)

---

### SEÇÃO I — ESTRUTURA IDEAL DO SITE

Com base nas Seções C, F e H, defina a estrutura de páginas ideal para o site do FlowNC que maximize tanto o SEO tradicional quanto o SEO para IA:

#### I.1 — Arquitetura de informação

Proponha um mapa de site com hierarquia de páginas. Inclua:

- **Home:** proposta de valor, CTA principal, social proof
- **Funcionalidades:** página de produto com detalhes de cada função
- **Casos de uso:** pages por cenário ("substituir código fanuc em lote", "editor g-code offline", etc.)
- **Downloads / Pricing:** página de conversão
- **Documentação / Tutoriais:** conteúdo de suporte e SEO
- **Blog / Base de conhecimento:** conteúdo para atrair tráfego orgânico
- **Comparativos:** FlowNC vs. concorrentes, FlowNC vs. Notepad++, etc.
- **Glossário CNC:** definições de termos para capturar buscas informacionais e ser citado por IA
- **FAQ:** perguntas frequentes estruturadas para Featured Snippets e respostas de IA

#### I.2 — Requisitos técnicos de SEO tradicional

- Velocidade de carregamento (Core Web Vitals)
- Estrutura de URL limpa e hierárquica
- Schema markup recomendado (SoftwareApplication, FAQPage, HowTo, Article)
- Sitemap XML e robots.txt
- Hreflang (PT-BR, EN, ES)
- Canonical tags

#### I.3 — Requisitos para SEO de IA (AEO/GEO)

- Estrutura de conteúdo que responde perguntas diretas (formato "Pergunta → Resposta direta → Desenvolvimento")
- Dados estruturados prioritários para aparecer em AI Overviews
- Como estruturar a página para que respostas sejam extraídas e citadas por LLMs
- Especificações técnicas do produto em formato estruturado (tabela, JSON-LD)
- Como aparecer em respostas do Perplexity, ChatGPT Search e Claude

---

### SEÇÃO J — ESTRATÉGIA DE CONTEÚDO

#### J.1 — Pilares de conteúdo

Defina os pilares temáticos do blog/base de conhecimento do FlowNC. Para cada pilar:
- Nome e descrição do pilar
- Justificativa (que dor do público-alvo resolve)
- Exemplos de artigos que poderiam ser publicados
- Volume de busca estimado do cluster
- Formato ideal (tutorial passo a passo, comparativo, guia definitivo, vídeo, ferramenta interativa)

**Pilares esperados para pesquisar:**
1. Programação G-code (fundamentos e referência)
2. Edição e substituição em lote
3. Fanuc e controles CNC populares
4. Automação e produtividade no chão de fábrica
5. Segurança e rastreabilidade em programas CNC
6. Comparativos de ferramentas CNC

#### J.2 — Calendário editorial inicial (primeiros 90 dias)

Proponha uma lista priorizada de 20 artigos/páginas a criar nos primeiros 90 dias, ordenados por:
1. Impacto no SEO (volume × facilidade de rankeamento)
2. Probabilidade de ser citado por IA generativa
3. Relevância para conversão (leva o leitor a baixar/comprar o FlowNC)

Para cada artigo: título, tipo de conteúdo, intenção de busca, palavra-chave primária, estimativa de impacto.

#### J.3 — Conteúdo para ser recomendado por IA

Defina 10 conteúdos de "resposta definitiva" que o FlowNC deveria criar para aparecer quando usuários perguntarem a assistentes de IA sobre tópicos do nicho. Para cada conteúdo:
- Pergunta exata que o usuário faria ao assistente de IA
- Formato ideal da resposta (para que o LLM a cite)
- Estrutura mínima do conteúdo (introdução, definição, etapas, exemplos, FAQ)

---

### SEÇÃO K — POSICIONAMENTO DE MARCA

#### K.1 — Análise do posicionamento dos concorrentes

Com base na Seção B, mapeie como cada concorrente se posiciona:
- Proposta de valor principal
- Tom de voz (técnico, acessível, profissional, casual)
- Para quem fala (operador, programador, gerente, empresa)
- Lacunas de posicionamento (o que ninguém está dizendo)

#### K.2 — Proposta de posicionamento do FlowNC

Com base nas lacunas identificadas, proponha:

**Proposta de valor única (UVP):** uma frase de 10–15 palavras que comunique o principal benefício do FlowNC de forma diferenciada dos concorrentes.

**Tagline candidatas:** 3 opções de tagline para o site.

**Mensagens-chave por público:**
- Para o operador de máquina: mensagem sobre simplicidade e segurança
- Para o programador CNC: mensagem sobre produtividade e controle
- Para o gestor/supervisor: mensagem sobre rastreabilidade e redução de erros

**Tom de voz recomendado:** descreva como o FlowNC deve comunicar (técnico mas acessível, direto, confiável, sem jargão desnecessário).

#### K.3 — Posicionamento para IA

Como o FlowNC deve ser descrito em textos do site para que assistentes de IA (ChatGPT, Perplexity, Claude, Gemini) o recomendem da forma correta:
- Descrição padronizada de 50 palavras (para citação)
- Descrição padronizada de 150 palavras (para contexto)
- Atributos estruturados: categoria, funcionalidade, público, plataforma, modelo de negócio, idioma, origem
- Comparações autorizadas: "FlowNC é como X, mas para Y" (analogias que ajudam a IA a contextualizar)

---

### SEÇÃO L — SEO TRADICIONAL

#### L.1 — Auditoria de oportunidades técnicas

Para um site novo do FlowNC, documente as melhores práticas obrigatórias:

**On-page:**
- Meta titles e descriptions otimizados por intenção
- Uso correto de H1/H2/H3
- Densidade de palavras-chave ideal para o nicho
- Otimização de imagens (alt text técnico)
- Linkagem interna recomendada

**Off-page:**
- Oportunidades de link building no nicho CNC (fóruns, diretórios, publicações técnicas)
- HARO e ProfNet para citações em jornalismo técnico
- Parcerias com distribuidores de CNC
- Guest posts em blogs de automação industrial

**Backlinks:**
- Sites de maior autoridade no nicho que poderiam linkar para o FlowNC
- Tipos de conteúdo que naturalmente atraem links no nicho CNC (ferramentas, glossários, guias)

#### L.2 — Schema Markup prioritário

Defina os schemas JSON-LD a implementar:

```json
// Exemplo de estrutura (preencher com dados reais na implementação)
{
  "@type": "SoftwareApplication",
  "name": "FlowNC",
  "applicationCategory": "BusinessApplication",
  "operatingSystem": "Windows",
  "offers": {...},
  "featureList": [...]
}
```

Liste todos os schemas relevantes: `SoftwareApplication`, `FAQPage`, `HowTo`, `Article`, `BreadcrumbList`, `Organization`, `Product`.

#### L.3 — Estratégia local e por idioma

- Relevância de SEO local (Brasil primeiro vs. lançamento global simultâneo)
- Estratégia de conteúdo PT-BR vs. EN vs. ES
- Diferenças de vocabulário por região (G-code no Brasil vs. "código NC" vs. "programa CNC")

---

### SEÇÃO M — SEO PARA AGENTES DE IA (AEO/GEO)

Esta é a seção mais estratégica e diferenciada do briefing. O objetivo é garantir que o FlowNC seja descoberto, citado e recomendado por sistemas de IA generativa (ChatGPT, Perplexity, Claude, Gemini, Copilot, SearchGPT, Grok).

#### M.1 — Fundamentos do SEO para IA

Pesquise e documente o estado atual (2025–2026) de:

- Como os LLMs indexam e "aprendem" sobre produtos e sites
- Diferença entre treinamento de modelo e recuperação em tempo real (RAG)
- Qual o papel do Bing Web Search na indexação para ChatGPT Search
- Como o Perplexity seleciona fontes para citar
- O que é GEO (Generative Engine Optimization) e AEO (Answer Engine Optimization)
- Principais estudos e dados sobre citação de fontes por IA generativa
- Como o Google AI Overview seleciona conteúdo para exibir

#### M.2 — Fatores de rankeamento para IA

Documente os fatores que aumentam a probabilidade de um site ser citado por IA:

**Fatores de autoridade:**
- E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness)
- Menções em sites de alta autoridade
- Dados de produto estruturados e verificáveis
- Consistência de informações em múltiplas fontes

**Fatores de conteúdo:**
- Conteúdo que responde perguntas diretas (FAQ, definições, tutoriais)
- Comprimento e profundidade (conteúdo longo e abrangente vs. curto e direto)
- Dados únicos e originais (estatísticas, estudos próprios, benchmarks)
- Clareza e especificidade técnica

**Fatores técnicos:**
- Schema markup (especialmente FAQPage, HowTo, SoftwareApplication)
- Velocidade de carregamento
- Acessibilidade
- HTTPS e segurança
- Robots.txt permissivo para crawlers de IA (GPTBot, PerplexityBot, ClaudeBot)

#### M.3 — Estratégia de visibilidade em cada plataforma de IA

Para cada plataforma, documente estratégia específica:

**ChatGPT / SearchGPT (OpenAI):**
- Como funciona a indexação
- Tipos de conteúdo mais citados
- Ações para aumentar visibilidade
- Como verificar se o FlowNC está sendo citado

**Perplexity AI:**
- Fontes priorizadas pelo Perplexity
- Estrutura de conteúdo ideal
- Estratégia de backlinks para aparecer no Perplexity

**Google AI Overviews / Gemini:**
- Critérios para aparecer no AI Overview
- Diferença de AI Overview para Featured Snippet
- Conteúdo que aparece no AI Overview para buscas de software técnico

**Microsoft Copilot / Bing:**
- Integração com indexação do Bing
- Oportunidades via Microsoft Start e parceiros Bing

**Claude (Anthropic):**
- Como o Claude recupera informações em tempo real
- Importância do conteúdo público e indexável

#### M.4 — Checklist técnico de AEO/GEO

Crie um checklist completo de implementações técnicas para o site do FlowNC, priorizadas por impacto:

**Alta prioridade:**
- [ ] Página "Sobre" com informações verificáveis da empresa/produto
- [ ] FAQ estruturado com schema FAQPage
- [ ] Conteúdo em formato "Pergunta + Resposta direta de 1–2 frases + Desenvolvimento"
- [ ] Schema SoftwareApplication completo
- [ ] robots.txt permitindo GPTBot, PerplexityBot, ClaudeBot, BingBot
- [ ] Sitemap atualizado e submetido ao Bing Webmaster Tools
- [ ] Definição clara de produto nas primeiras 100 palavras de cada página
- [ ] Especificações técnicas em tabela estruturada

**Média prioridade:**
- [ ] Dados originais sobre o produto (benchmarks, comparativos de velocidade)
- [ ] Citações e menções em sites terceiros (links de qualidade)
- [ ] Conteúdo de tutorial em formato HowTo schema
- [ ] Glossário de termos CNC com schema DefinedTerm
- [ ] Página de comparativo com concorrentes
- [ ] Presskit / media page para jornalistas e criadores de conteúdo

**Baixa prioridade (mas recomendado):**
- [ ] Podcast ou série de vídeos para ampliar menções em transcrições indexadas
- [ ] Presença em diretórios de software (Product Hunt, AlternativeTo, Capterra, G2)
- [ ] Wikipedia relevante (artigo sobre edição em lote de G-code)
- [ ] Perfil no Wikidata
- [ ] Schema Organization com dados verificáveis (CNPJ, endereço, fundação)

#### M.5 — Conteúdo otimizado para resposta direta (AI Snippets)

Identifique 15 perguntas que usuários fazem a assistentes de IA sobre o tema do FlowNC e que o site deveria responder de forma estruturada. Para cada pergunta:

- Texto exato da pergunta
- Resposta direta ideal em 1–3 frases (para o snippet)
- Desenvolvimento recomendado (200–500 palavras de apoio)
- Schema markup recomendado
- Página do site onde inserir

**Exemplos de perguntas a pesquisar e responder:**
1. "O que é edição em lote de código G-code?"
2. "Como substituir um código M em todos os programas CNC de uma vez?"
3. "Quais são as diferenças entre G-code e M-code?"
4. "O que é Fanuc e por que é o controle CNC mais usado?"
5. "Como fazer backup de programas CNC antes de editar?"
6. "Quais são os melhores editores de G-code para Windows?"
7. "Como editar arquivos .NC sem instalar nada?"
8. "O que é um arquivo de código CNC e como abrir?"
9. "Como evitar erros ao substituir códigos em programas CNC?"
10. "O que significa o código M08 no Fanuc?"

---

### SEÇÃO N — OPORTUNIDADES DE DIFERENCIAÇÃO

Com base em toda a pesquisa anterior, consolide:

#### N.1 — Matriz de diferenciação

Crie uma tabela comparativa: FlowNC × principais concorrentes × principais critérios de escolha do público.

Critérios sugeridos (adapte com base nos achados da pesquisa):
- Operação offline (sem internet)
- Portabilidade (pen drive / sem instalação)
- Backup automático dos originais
- Validação antes de salvar
- Suporte a múltiplos encodings (UTF-8, ANSI, UTF-16)
- Boundary CNC rigoroso (M8 ≠ M80)
- Editor integrado por arquivo
- Preço
- Curva de aprendizado
- Suporte em português
- Interface em português

#### N.2 — Oportunidades de conteúdo não exploradas

Identifique tópicos do nicho CNC que:
- Têm volume de busca relevante
- Não têm conteúdo de qualidade disponível em PT-BR
- Se bem respondidos, posicionariam o FlowNC como referência no nicho
- Seriam citados por IA como fonte autoritativa

#### N.3 — Oportunidades de distribuição não exploradas

Identifique canais de distribuição que os concorrentes não utilizam, onde o FlowNC poderia ser descoberto:
- Comunidades técnicas específicas
- Grupos de WhatsApp/Telegram de técnicos CNC
- Canais de YouTube de programação CNC
- Distribuidores de máquinas CNC como parceiros de distribuição
- Escolas técnicas e cursos de programação CNC

---

## 4. ENTREGÁVEIS ESPERADOS

Ao concluir a pesquisa, o agente deve produzir um documento único estruturado com:

### 4.1 — Relatório executivo (máximo 2 páginas)
- Principais achados de mercado
- Oportunidade de posicionamento recomendada
- Top 3 ações prioritárias para SEO e visibilidade
- Modelo de negócio recomendado

### 4.2 — Dados de benchmarking
- Tabela de concorrentes diretos e indiretos com todos os campos da Seção B
- Matriz de diferenciação preenchida (Seção N.1)

### 4.3 — Lista de palavras-chave
- Planilha organizada por cluster, com: termo, idioma, volume estimado, dificuldade estimada, intenção de busca, tipo de conteúdo recomendado, prioridade (alta/média/baixa)

### 4.4 — Personas
- 3+ personas detalhadas com todos os campos da Seção G

### 4.5 — Arquitetura do site
- Mapa de site completo com hierarquia de páginas (Seção I.1)
- Lista de schemas a implementar (Seção L.2 + M.4)

### 4.6 — Plano de conteúdo
- Calendário editorial dos primeiros 90 dias (Seção J.2)
- Lista de 15 conteúdos de resposta direta para AEO (Seção M.5)

### 4.7 — Estratégia de posicionamento
- UVP, taglines, mensagens por público (Seção K.2)
- Descrição padronizada do produto para IA (Seção K.3)

### 4.8 — Checklist de implementação SEO/AEO
- Checklist priorizado da Seção M.4
- Recomendações técnicas da Seção L.1

---

## 5. CRITÉRIOS DE QUALIDADE DA PESQUISA

O agente deve garantir que:

1. **Todos os dados de mercado** têm fonte citada (URL, relatório, data)
2. **Volumes de busca** são estimativas baseadas em ferramentas (Ahrefs, SEMrush, Google Keyword Planner) ou em benchmarks do setor — declarar a metodologia quando não for possível acessar ferramentas diretas
3. **Concorrentes** foram verificados como ativos (site acessível, produto funcionando)
4. **Personas** são baseadas em evidências de fóruns, grupos e depoimentos reais, não apenas em hipóteses
5. **Recomendações de AEO/GEO** são baseadas em estudos publicados e boas práticas documentadas de 2024–2026
6. **Toda recomendação** inclui justificativa ("por quê isso importa para o FlowNC")
7. Quando uma informação não for encontrada, declara explicitamente "dado não encontrado" em vez de inventar

---

## 6. RESTRIÇÕES E PREMISSAS

- O FlowNC atende **principalmente o mercado com controladores Fanuc**, mas é tecnicamente compatível com qualquer arquivo de texto de código CNC
- O produto é **offline-first** — não requer internet para operar. Isso é um diferencial central a ser explorado
- O público principal está no **Brasil** (PT-BR), mas a estratégia deve contemplar expansão para **mercado global em inglês**
- O site ainda **não existe** — toda a arquitetura e conteúdo serão criados do zero
- O produto é desenvolvido por **um único desenvolvedor** (indie) — estratégias que exijam grande equipe de marketing devem ser marcadas como "fase 2" ou "longo prazo"
- O modelo de negócio **não está definido** — a pesquisa deve recomendar o mais adequado com base nos achados de mercado
- Priorizar **conteúdo em PT-BR** nos primeiros 6 meses; inglês na fase seguinte

---

## 7. REFERÊNCIAS E RECURSOS PARA O AGENTE

### Sites de referência do setor CNC
- CNCZone.com (maior fórum de CNC em inglês)
- PracticalMachinist.com (fórum de usinagem)
- Reddit: r/CNC, r/machining, r/Manufacturing
- LinkedIn grupos: CNC Machining, Manufacturing Automation, Fanuc Users
- Grupo Facebook: Programadores CNC Brasil (buscar equivalentes)

### Ferramentas de pesquisa de palavras-chave a usar
- Google Keyword Planner
- Google Trends
- Ahrefs Free / SEMrush Free (se disponível)
- AnswerThePublic
- AlsoAsked
- People Also Ask do Google

### Fontes de dados de mercado
- Relatórios da Grand View Research sobre CNC Software Market
- Relatórios da MarketsandMarkets sobre Machine Tool Software
- Relatórios da Technavio sobre G-code editors / CNC programming software
- ABIMAQ (Associação Brasileira de Máquinas e Equipamentos) — dados do Brasil
- Eurostat dados de manufatura

### Fontes de referência para SEO de IA
- Estudos da Anita Chadha, Neil Patel, Semrush sobre GEO
- Artigos do Search Engine Journal sobre AI Overviews
- Relatório da BrightEdge sobre AI in Search
- Guia do Google sobre como criar conteúdo útil
- Documentação oficial do OpenAI sobre GPTBot
- Documentação do Perplexity sobre indexação

### Competidores potenciais a pesquisar (ponto de partida, não exaustivo)
- CNCSimul / NCSimul
- CamBam
- G-code Ripper
- Universal G-code Sender (foco diferente, mas relevante)
- NC Viewer
- G-Wizard Editor
- Notepad++ com plugins CNC
- Fanuc FOCAS (API oficial Fanuc)
- CIMCO Edit
- Predator DNC / Editor

---

## 8. FORMATO DE SAÍDA ESPERADO

O documento final deve ser entregue em **Markdown** (`.md`) estruturado, com:

- Sumário executivo no início
- Cada seção com numeração clara (A, B, C...)
- Tabelas para dados comparativos
- Listas numeradas para rankings e prioridades
- Blocos de destaque para insights críticos
- Fontes citadas ao final de cada seção
- Glossário de termos técnicos ao final (para uso futuro em conteúdo do site)

---

*Fim do briefing. Execute todas as seções e entregue o relatório completo conforme os critérios acima.*
