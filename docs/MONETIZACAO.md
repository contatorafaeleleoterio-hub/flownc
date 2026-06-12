# Plano de Monetização — FlowNC

> Documento executivo. Mercado prioritário: **Brasil**. Modelo recomendado:
> **Freemium + Assinatura**, com opção de licença perpétua. Preços são **faixas de
> hipótese** — validar com 5–10 oficinas reais antes de fixar.

## 1. Posicionamento (a tese)
**"O editor em lote que o seu CAM não tem."**

Softwares da categoria CAM (Machining Strategist / WorkNC, Mastercam, Edgecam, PowerMill, NX)
são pesados, caros (dezenas de milhares de R$), instalados no PC, licenciados por dongle/chave
+ manutenção anual e vendidos por revendas (VARs). O FlowNC **não compete** com eles — entra
barato como ferramenta de **produtividade complementar**:

- padronizar cabeçalhos e comentários de programa;
- trocar ferramentas, M-codes e avanços em massa;
- adaptar programas entre máquinas/controles (Fanuc, Mach, Heidenhain);
- tudo isso em **muitos arquivos de uma vez**, com salvamento seguro, sem erro manual.

## 2. Público-alvo (Brasil primeiro)
1. **Programadores CNC / CAM** em ferramentarias e moldes & matrizes — editam muitos
   programas e sofrem com ajuste manual repetitivo.
2. **Job shops / usinagem sob demanda** (pequenas e médias) — precisam padronizar programas
   entre máquinas diferentes.
3. **Operadores de chão de fábrica** que ajustam programa direto no controle.

Geografia: BR primeiro (Pix/boleto, comunidades em PT-BR). Depois LATAM e global (USD).

## 3. Modelo de cobrança (decidido)
**Freemium + Assinatura como principal, com opção de licença perpétua.**

| Plano | Para quem | O que inclui | Preço (faixa BR — hipótese) |
|---|---|---|---|
| **Free** | Atrair / experimentar | Find/replace básico, lote pequeno (ex.: até N arquivos), sem biblioteca/perfis | R$ 0 |
| **Pro (1 posto)** | Programador individual | Lote ilimitado, salvamento in-place seguro c/ backup, biblioteca de códigos, perfis de controle, histórico | **R$ 39–79/mês** ou **R$ 390–790/ano** |
| **Shop (multi-posto)** | Oficina | Licença flutuante/rede, vários postos, suporte prioritário | sob proposta (por nº de postos) |
| **Perpétua + Manutenção** | Quem rejeita assinatura | Pro vitalício + ~20%/ano de manutenção (atualizações/suporte) | **R$ 1.200–1.900** + manutenção |

**Por quê:** assinatura dá receita recorrente e preço de entrada baixo; freemium reduz o
custo de aquisição via boca-a-boca; a opção perpétua remove a objeção cultural (mercado CNC é
conservador) sem perder o público.

## 4. Tecnologia (entrega, ativação e proteção)
Hoje o produto é um EXE portátil cru — insuficiente para vender. Necessário:

- **Assinatura de código (Authenticode / certificado OV)** — evita bloqueio do
  SmartScreen/antivírus num PC pago. **Crítico.** ~USD 100–400/ano.
- **Instalador (Inno Setup)** no lugar do EXE solto — confiança, atalho no menu,
  desinstalador.
- **Camada de licença/ativação**: node-locked por posto, com **período offline de carência**
  (chão de fábrica costuma estar sem internet) e **trial 14–30 dias**. Opções:
  **Keygen.sh**, Cryptolens ou LicenseSpring (SDK + servidor gerenciado).
- **Auto-update**: checagem de versão + download do instalador.
- **Telemetria opt-in** para medir o funil (trial → pago).

## 5. Distribuição e pagamento (Brasil primeiro)
- **Venda direta**: landing page (ex.: flownc.com.br) com download + trial + ativação.
- **Pagamento BR**: **Pix/boleto/cartão** via **Hotmart/Eduzz** (recorrência + nota fiscal) ou
  **Stripe** (cartão/recorrência). Pix é decisivo no BR. Global depois: **Paddle/Lemon
  Squeezy** (Merchant of Record cuida de imposto/VAT).
- **Aquisição (conteúdo)**: YouTube/Instagram/TikTok mostrando edição em lote ao vivo; grupos
  de Facebook ("Programação CNC"), fóruns; SEO ("editar G-code em lote").
- **Revendas/representantes** que já vendem CAM/ferramentas/máquinas às oficinas (comissão);
  bundle com distribuidores de ferramentas e dealers de máquina.
- **Microsoft Store** como vitrine de baixa fricção (controle de licença mais fraco).

## 6. Go-to-market por fases
- **Fase 0 — Beta grátis**: coletar usuários, depoimentos e lista de e-mail; validar a dor e
  os preços com oficinas reais.
- **Fase 1 — Lançamento**: code signing + instalador + servidor de licença + landing +
  planos Free/Pro (assinatura) + pagamento BR (Pix).
- **Fase 2 — Escala**: licença Shop multi-posto, revendas/representantes, opção perpétua.
- **Fase 3 — Upsell**: pacotes de perfis de controle, adaptação de post-processor,
  sincronização da biblioteca na nuvem (add-ons pagos).

## 7. Métricas-chave
Conversão trial→pago, MRR/ARR, nº de postos ativos, churn, CAC via conteúdo, NPS.

## 8. Riscos e mitigação
| Risco | Mitigação |
|---|---|
| Pirataria | Preço baixo + valor em nuvem (biblioteca/perfis) + assinatura de código |
| Mercado anti-assinatura | Oferecer licença perpétua + manutenção |
| Falso-positivo de antivírus | Certificado de assinatura de código |
| Suporte/atualização | Instalador + auto-update + base de conhecimento |

## 9. Checklist técnico de lançamento
- [ ] Certificado de assinatura de código (OV) e assinar o EXE/instalador.
- [ ] Instalador Inno Setup (atalho, desinstalador, auto-update).
- [ ] Integração com servidor de licença (Keygen.sh) — trial, ativação, offline, nº de postos.
- [ ] Gateway de pagamento BR (Hotmart/Eduzz ou Stripe) com Pix e recorrência.
- [ ] Landing page (ver `PAGINA-DE-VENDAS.md`).
- [ ] Telemetria opt-in do funil.
- [ ] Validar faixas de preço com 5–10 oficinas reais antes de fixar.

---
_Fontes da pesquisa de conversão de landing: Instapage (B2B best practices), fibr.ai e
KlientBoost (SaaS landing pages), SaaS Hero (CTA placement)._
