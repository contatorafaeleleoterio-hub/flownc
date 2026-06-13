# Página de Vendas — FlowNC (roteiro + copy)

> **Público da página: dono/gestor da oficina** (decisão 2026-06-12). A copy fala de tempo
> de máquina, erro evitado e padronização da equipe — não de features para o programador.
> Ordem que converte: **hero → dor/solução → benefícios → prova social → preço → CTA**.
> Princípios (pesquisa 2025/26): headline curta, **1 CTA primário** acima da dobra, preço
> **visível** (nunca "fale com vendas"), prova social junto do botão, formulário curto (3–5
> campos). Benchmark B2B: 2–6% de conversão é bom, 10%+ é topo.

---

## 1. Hero (acima da dobra)
**Headline (curta, <44 caract.):**
> Sua oficina perde horas editando G-code.

**Subheadline:**
> O FlowNC edita centenas de programas CNC de uma vez, com backup automático — sua equipe
> padroniza cabeçalhos, troca ferramentas e adapta máquinas em minutos, sem erro manual.

**CTA primário (1 botão):** `Baixar teste grátis`
**CTA secundário (texto):** Ver como funciona (demo de 60s)

**Visual:** print/GIF do app aplicando uma edição em vários arquivos de uma vez.
**Logo:** wordmark oficial em `docs/logo/logo FlowNC.jpeg` (fundo escuro) — usar no topo da
página; versão PNG transparente em `flownc/assets/logo/logo_flownc.png`.

---

## 2. Dor → Solução
Três dores do gestor de usinagem, cada uma com a resposta do FlowNC:

1. **"Minha equipe perde horas editando programa por programa."**
   → A mesma troca aplicada em todos os programas de uma vez — horas viram minutos.
2. **"Um erro de digitação quebra a peça (ou a máquina) e o prejuízo é meu."**
   → Salvamento in-place seguro, com backup automático antes de gravar. Tudo reversível.
3. **"Cada máquina/controle precisa de um ajuste diferente e nada é padronizado."**
   → Perfis de controle (Fanuc, Mach, Heidenhain) e biblioteca de códigos da oficina —
   o padrão fica no sistema, não na cabeça de cada programador.

Acompanhar cada item com mini-demo/GIF.

---

## 3. Benefícios em resultados
- ✅ **Lote ilimitado** — quantos programas precisar, de uma vez.
- ✅ **Salvamento in-place seguro** — grava no arquivo original com backup.
- ✅ **Biblioteca de códigos** — guarde trocas frequentes e reaplique.
- ✅ **Perfis de controle** — Fanuc, Mach, Heidenhain.
- ✅ **Histórico** — veja e desfaça o que foi alterado.
- ✅ **Roda no seu PC, com o CAM que você já usa** — complementa, não substitui.

---

## 4. Prova social
- Depoimentos de oficinas reais **ao lado dos CTAs**.
- Logos de oficinas/ferramentarias que usam.
- Métrica de uso assim que houver: _"Usado em X oficinas / Y programas editados"_.
> Coletar tudo no beta (Fase 0). Antes disso, usar depoimentos dos primeiros testadores.

---

## 5. Preço (transparente — sempre visível)

| Free | Pro | Shop (destaque) |
|---|---|---|
| R$ 0 | preço baixo de teste (1 posto) | **preço público por posto** — plano principal da página |
| Find/replace básico, lote pequeno | Lote ilimitado, backup, biblioteca, perfis, histórico | Tudo do Pro + vários postos, licença flutuante e suporte prioritário |
| `Começar grátis` | `Assinar Pro` | `Assinar para minha oficina` |

> Preços baixos de propósito nesta fase: **teste de demanda**. Definir valores no Stripe e
> revisar após as primeiras vendas.

**Também disponível:** licença **perpétua** (paga uma vez) + manutenção anual — para quem
prefere não assinar. **Garantia de 30 dias** ou seu dinheiro de volta.

---

## 6. FAQ
- **Funciona offline?** Sim — pensado para o chão de fábrica; licença com carência offline.
- **O antivírus bloqueia?** Não — o instalador é assinado digitalmente.
- **Funciona com o meu CAM/controle?** Sim — edita os programas G-code que seu CAM gera;
  perfis para Fanuc, Mach e Heidenhain.
- **Como ativo a licença?** Baixa, instala, ativa com a chave recebida na compra.
- **Substitui meu CAM?** Não — é complementar, faz a edição em lote que o CAM não faz.

---

## 7. CTA final
> Pare de editar programa por programa.
**Botão:** `Baixar teste grátis`
**Captura de e-mail** (para quem não compra agora): "Receba dicas de produtividade CNC +
novidades do FlowNC." (formulário curto: nome + e-mail.)

---
_Estrutura baseada em melhores práticas de conversão B2B/SaaS 2025–26 (Instapage, fibr.ai,
KlientBoost, SaaS Hero)._
