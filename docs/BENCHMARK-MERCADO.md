# Benchmark de Mercado — FlowNC (2026-06-12)

> Escopo: editores de G-code e utilitários CNC (CAM excluído). Mercados BR e EUA.
> Método: pesquisa web enxuta + conhecimento setorial; fontes ao fim. Itens marcados
> **[validar]** são estimativas que precisam de confirmação em campo.

## 1. Concorrentes diretos (editores de G-code)

| Produto | Origem | Copy / posicionamento | Preço / modelo |
|---|---|---|---|
| **CIMCO Edit** | Dinamarca (líder mundial) | "The editor-of-choice for professional CNC programmers" — confiabilidade, simulação 3D, comparação de arquivos, DNC | Perpétua via revendas (~US$ 350–500 **[validar]**) + trial 30 dias |
| **NCPlot v3** | EUA | "Tools for CNC Programmers" — editor + backplot + macro B Fanuc | **US$ 299 perpétua** |
| **G-Wizard Editor** (CNCCookbook) | EUA | "Check, Optimize, and Learn G-Code Easily" | **DESCONTINUADO** — era assinatura barata |
| **NC Corrector** | Leste Europeu | Editor + visualizador gratuito | Grátis |
| **CNC PAD** | — (tem PT-BR) | "Editor de programas CNC freeware" — highlight Fanuc/Siemens/Heidenhain | Grátis |

**Leituras-chave:**
- **Ninguém vende "edição em lote multi-arquivo"** como proposta central. Todos vendem "editor profissional" (arquivo por arquivo) + simulação. O posicionamento do FlowNC ("o lote que o seu CAM não tem", tempo do gestor) está **vago no mercado**.
- A saída do G-Wizard Editor deixa órfão o público "editor leve e barato" nos EUA — e prova que o modelo assinatura barata existiu nesse nicho.
- O concorrente grátis mais perigoso no BR é o **CNC PAD** (PT-BR, grátis), mas sem lote, sem backup seguro, sem biblioteca.

## 2. Soluções onde o editor é secundário
- **CIMCO DNC-Max / MDC** — o motor de receita da CIMCO é DNC/coleta de dados; o Edit é porta de entrada.
- **Predator DNC/Editor** (EUA) — suíte de chão de fábrica; editor embutido.
- **dnc4u** — DNC com editor incluído, trial de 60 dias.
- **Frame** (BR) — comunicação DNC nacional.
- **Verificadores/simuladores** — CNC Simulator Pro, CutViewer, NC Viewer (grátis, navegador): editar é acessório, verificar é o produto.

Implicação: o "editor" sozinho historicamente vira feature de outra suíte. O FlowNC se defende sendo **especialista em lote** (o que as suítes não fazem) e barato.

## 3. Canais e posicionamento dos players
- **EUA:** SEO/conteúdo pesado (CNCCookbook construiu o negócio com blog + funil de e-mail), fóruns (Practical Machinist, CNCzone), YouTube com demos. Pouco anúncio pago visível; o canal dominante é **conteúdo + comunidade**.
- **BR:** venda via **revendas técnicas** (FIT Tecnologia, DNC Técnica, Infoaxis revendem CIMCO), portais setoriais (Usinagem Brasil, Revista Ferramental), feiras (Intermach/ABINFER Business Center, FEIMEC), grupos de Facebook/WhatsApp de programação CNC. As revendas BR produzem blog em PT-BR ("5 melhores aplicativos para programação CNC") — SEO fraco e fácil de competir.
- **Copy dominante do setor:** "profissional", "confiável", "simulação". Ninguém fala com o **gestor** (tempo, erro, prejuízo) — espaço aberto, coerente com a decisão do FlowNC.

## 4. Tamanho de mercado
**EUA (dados sólidos):**
- ~299,5 mil machinists + 55,2 mil tool & die makers (BLS, 2024); ~212 mil empregados em "machine shop services" (IBISWorld, 2024); ~34,2 mil vagas/ano projetadas (2024–2034).
- Mercado de software CNC não-CAM: nicho de utilities entre US$ 50–500 por licença.

**Brasil:**
- **~5.500 ferramentarias** = 3.500 cativas (dentro de montadoras etc.) + 2.000 de mercado (ABINFER); ~350 só em Joinville-SC. Concentração Sul/Sudeste.
- Somando job shops de usinagem em geral, o universo é maior **[validar — sem censo público]**.
- Conta de padaria para o FlowNC: se 2.000 ferramentarias de mercado + alguns milhares de job shops são endereçáveis, **1% de penetração ≈ 50–100 oficinas pagantes** — alcançável e suficiente para validar; teto BR na casa de poucos milhares de contas. Receita é negócio de nicho, não de escala — coerente com preço baixo + complemento de renda inicialmente.

## 5. Utilitários CNC de alta demanda (oportunidades, CAM excluído)
| Categoria | Exemplos / preço | Demanda |
|---|---|---|
| **Calculadora de corte (feeds & speeds)** | FSWizard (free + Pro ~US$ 50), HSMAdvisor, Machinist Calc Pro (~US$ 25) | **Altíssima** — o utilitário nº 1 do setor |
| **Simulador/backplot de G-code** | NC Viewer (grátis, navegador), CNC Simulator Pro, CutViewer | **Alta** — "ver antes de rodar" |
| **Trigonometria/geometria de oficina** | Machinist Calc, apps de trig | Alta entre operadores |
| **Conversores** (mm↔pol, DXF→G-code) | diversos grátis | Média |
| **Estimador de tempo de ciclo** | embutido em editores pagos | Média, mal atendida |
| **Comparador de arquivos NC** | CIMCO Edit (pago) | Média — quase sempre preso a suíte cara |

**Oportunidades para o FlowNC:** (a) comparador de versões e estimador de tempo de ciclo como features Pro — hoje exigem CIMCO; (b) calculadoras simples (corte/trig) grátis como **isca de marketing** em PT-BR (SEO fácil no BR); (c) backplot simples no futuro — é o que mais aproxima do CIMCO Edit sem virar CAM.

## Fontes
- CIMCO Edit (copy/recursos): cimco.com/software/cimco-edit
- NCPlot preço: ncplot.com · práticas do nicho: practicalmachinist.com (thread "G-code tool path editors")
- G-Wizard Editor descontinuado: cnccookbook.com/g-wizard-editor-pricing
- CNC PAD: cnc-pad.com/pt-BR · Revendas BR CIMCO: fit-tecnologia.com.br, dnctecnica.com, infoaxis.com.br · DNC BR: frame.com.br/dnc
- EUA: bls.gov/ooh (Machinists 2024), ibisworld.com (Machine Shop Services employment), datausa.io
- BR: abinfer.org.br + usinagem-brasil.com.br ("Setor de ferramentaria quer investir em modernização") + revistaferramental.com.br (100 maiores ferramentarias)
- Utilitários: fswizard.com, cncsourced.com (best CNC simulators), machinistguides.com
