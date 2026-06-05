# 07 — PROMPT DE PESQUISA: melhor UI/navegação para o CNC Batch Editor (contexto industrial)

> Cole o bloco abaixo numa IA de pesquisa (deep research). Objetivo: descobrir, com base
> em evidência validada (normas + estudos + benchmark), a melhor arquitetura de tela,
> ordem/posição/tamanho dos elementos, regras de interação e padrões inteligentes —
> **não** limitado a opiniões. O resultado vai decidir: tela única vs múltiplas telas,
> agrupamento, ordem dos elementos, e regras (ex.: reabrir último perfil).

---

## PROMPT (copiar a partir daqui)

**Papel:** Você é um pesquisador sênior em **HMI/UX industrial, fatores humanos (human
factors/ergonomia cognitiva) e software de manufatura**. Sua tarefa é produzir um
**benchmark e uma síntese baseada em evidência** sobre a melhor forma de organizar a
interface e o fluxo de navegação de uma ferramenta desktop usada no chão de fábrica.
**Não se limite a opinião ou tendências de design web**: priorize normas reconhecidas,
estudos empíricos e diretrizes consolidadas. Onde houver conflito entre fontes, exponha o
conflito e diga qual prevalece e por quê.

### Contexto do produto (leia com atenção antes de pesquisar)

- **App:** editor em lote de programas CNC (G-code). O operador escolhe um **perfil de
  máquina**, abre vários programas, define **substituições de texto** (ex.: trocar `M8`→`M08`,
  `S2000`→`S1500`, ferramenta `T0101`→`T0303`), há trocas **comuns a todos** e trocas
  **específicas de um programa**, um **preview/revisão** antes de gravar, **verificações de
  segurança** (deve existir / não pode existir / contagem), e o salvamento em **pasta nova**
  (originais nunca são alterados), com conferência de integridade.
- **Plataforma:** **desktop Windows, PySide6/Qt** (NÃO é web nem mobile). As recomendações
  devem ser aplicáveis a widgets de desktop (janela, abas, tabelas, listas, diálogos).
- **Usuário:** operador técnico de CNC, conhecimento prático alto, mas **não** é usuário
  avançado de computador. Uso **repetitivo e diário** em produção.
- **Criticidade:** erro tem custo alto e físico — ferramenta errada, colisão, refugo de peça.
  Segurança operacional e prevenção de erro humano são prioridade.
- **Restrições de projeto:** estética **sóbria e funcional** de chão de fábrica (não
  "maximalista"); mudar só a camada de apresentação; mínimo retrabalho; máxima clareza,
  velocidade e baixa curva de aprendizado.

### Perguntas de pesquisa que a síntese DEVE responder

1. **Arquitetura de tela:** para uma tarefa com configuração + revisão + confirmação de
   alto risco, o que a evidência recomenda — **tela única** (formulário/painel coeso),
   **assistente passo a passo (wizard)**, ou **híbrido** (configuração numa tela + revisão/
   confirmação em etapa separada)? Sob quais condições cada um vence? Considere a literatura
   sobre *single-page vs multi-step forms*, *wizards*, *progressive disclosure* e a
   diferença entre usuário **iniciante** e **experiente/repetitivo**.
2. **Ordem e agrupamento dos elementos:** qual a sequência e o agrupamento ótimos para:
   seleção de perfil, abertura de arquivos, destino de saída, tabela de regras, ação
   principal (executar/revisar), revisão/preview, salvar. Quais elementos devem ficar
   **juntos na mesma área** e quais devem ser **separados**? (fundamentar em fluxo de leitura,
   lei de proximidade/Gestalt, modelo mental da tarefa, ISA-101).
3. **Hierarquia e ação primária:** como sinalizar a ação que "avança o processo" vs ações
   secundárias/administrativas/destrutivas (tamanho, cor, posição, peso). Onde posicionar o
   botão de ação principal (canto inferior direito? outro?). Evidência sobre posição de
   botões primários/confirmar/cancelar em desktop.
4. **Tamanho, densidade e alvos de clique:** dimensões/área de alvo recomendadas para
   ambiente industrial (possível uso com luvas, telas sujas, iluminação ruim, operadores com
   visão cansada), densidade de informação, tipografia legível, contraste. Citar números
   quando existirem (ex.: alvo mínimo em px/mm, contraste WCAG, tamanho de fonte).
5. **Cor e estado:** uso de cor para severidade (verde/amarelo/vermelho) em HMI; por que
   **não depender só de cor** (daltonismo) e o que usar junto (ícone, texto, forma). Normas
   de codificação por cor em painéis industriais.
6. **Feedback e progresso:** o que a evidência exige de feedback de progresso, conclusão e
   erro em operações que podem demorar; quando usar barra de progresso, status inline,
   diálogo modal; como redigir mensagens de erro acionáveis.
7. **Prevenção de erro e confirmação:** padrões para ações de alto risco (confirmar antes de
   gravar, preview obrigatório, bloqueio quando verificação de segurança falha, proteção
   contra perda de trabalho não salvo). Quanta fricção é certa — e onde é excessiva.
8. **Regras inteligentes / padrões (defaults) que reduzem esforço:** investigar e validar
   práticas como **reabrir automaticamente com o último perfil/configuração usada**,
   **lembrar a última pasta de destino**, **lembrar o último diretório aberto**, pré-seleção
   inteligente, persistência de preferências, *recent items*. Quando esses defaults ajudam e
   quando atrapalham (e como sinalizá-los para não esconder estado importante).
9. **Benchmark de ferramentas análogas:** como softwares reais de manufatura/edição resolvem
   esse fluxo — ex.: pós-processadores e CAM (Mastercam, Autodesk Fusion/HSM, SolidCAM,
   Esprit), editores/simuladores de G-code (NC editors, CIMCO Edit), painéis HMI de CNC
   (Fanuc, Siemens Sinumerik, Heidenhain, Mazatrol), e ferramentas de *find & replace em
   lote* em geral (IDEs, editores de texto). Extraia padrões recorrentes e o que é
   considerado boa prática.

### Fontes e nível de evidência (exija qualidade)

- **Normas/diretrizes:** ISA-101 (HMI), ISO 9241 (ergonomia de interação humano-sistema, esp.
  -110 princípios de diálogo, -112 apresentação de informação), IEC 62682 (gestão de alarmes),
  EEMUA 201, NUREG-0700 (HMI de salas de controle), diretrizes de GUI de desktop
  (ex.: guidelines clássicos de plataforma).
- **Fatores humanos / UX baseada em pesquisa:** Nielsen Norman Group (heurísticas, formulários,
  wizards, progressive disclosure, error messages), literatura de human factors/ergonomics,
  estudos empíricos comparando single-page vs multi-step.
- **Hierarquia de evidência:** prefira norma + estudo empírico + diretriz consolidada acima de
  blog post avulso. **Marque o nível de confiança** de cada recomendação (alto/médio/baixo) e
  **cite a fonte** (com link quando possível). Sinalize quando algo for consenso de prática
  sem estudo forte por trás.

### Metodologia exigida

1. Levante as fontes acima e extraia as recomendações pertinentes a cada pergunta.
2. Faça o **benchmark** das ferramentas análogas (o que cada uma faz no ponto em questão).
3. **Triangule**: onde normas, estudos e benchmark concordam, marque como recomendação forte.
   Onde divergem, explique o trade-off e decida com base no nosso contexto (industrial,
   repetitivo, alto risco, operador técnico não-avançado).
4. Traduza tudo numa **especificação concreta e aplicável a Qt/desktop**, não em conselhos
   genéricos.

### Formato da resposta (obrigatório)

Entregue **destilado e acionável**, nesta estrutura:

1. **Veredito sobre a arquitetura de tela** — tela única, wizard ou híbrido — com a
   justificativa e as condições. Responda explicitamente: *para este app, os passos Perfil →
   Programas → Trocas devem ficar juntos numa tela ou separados? Revisar e Salvar devem ser
   etapas/telas próprias?*
2. **Especificação de layout** — ordem e agrupamento dos elementos (de cima para baixo /
   esquerda para direita), com um diagrama em texto/ASCII.
3. **Hierarquia visual** — primário/secundário/destrutivo: cor, tamanho, posição.
4. **Tamanhos e densidade** — números recomendados (alvo de clique, fonte, contraste,
   espaçamento) adequados a ambiente industrial.
5. **Cor e sinalização de estado** — esquema e por que não só cor.
6. **Feedback, progresso e mensagens de erro** — quando e como.
7. **Prevenção de erro e confirmação** — padrões para a etapa de gravar.
8. **Regras/defaults inteligentes** — lista priorizada (ex.: reabrir último perfil, lembrar
   destino) marcando quais são validadas e por quê.
9. **Tabela de benchmark** — ferramenta × como resolve cada ponto-chave.
10. **Lista priorizada de recomendações** — cada item com: **impacto**, **esforço**,
    **nível de confiança** e **fonte**.
11. **Referências** — lista de fontes citadas com links.

Seja específico, cite as fontes, marque a confiança e evite generalidades. O objetivo é uma
síntese mineirada dos melhores dados disponíveis para **este** contexto, que sirva de base
para decidir a navegação e o layout finais.

## (fim do prompt)
