# MANUAL DE PROGRAMAÇÃO — Fanuc CNC

> **CONTROLE NUMÉRICO COMPUTADORIZADO**
> Fanuc Series · Centros de Usinagem
>
> **Referência Técnica Completa**
>
> **Compatível com:** Fanuc 0M · Fanuc 0i · Fanuc 16i · Fanuc 18i · Fanuc 21i · Fanuc 30i
> Fresadoras CNC · Centros de Usinagem Vertical e Horizontal
>
> *Versão 1.0 · Português Brasileiro*

---

## Sumário

1. [Introdução ao Controle Fanuc](#1-introdução-ao-controle-fanuc)
2. [Códigos G — Referência Completa](#2-códigos-g--referência-completa)
3. [Códigos M — Funções Auxiliares](#3-códigos-m--funções-auxiliares)
4. [Sistemas de Coordenadas](#4-sistemas-de-coordenadas)
5. [Compensações de Ferramentas](#5-compensações-de-ferramentas)
6. [Ciclos Fixos de Usinagem](#6-ciclos-fixos-de-usinagem)
7. [Subprogramas e Macro B](#7-subprogramas-e-macro-b)
8. [Boas Práticas e Segurança](#8-boas-práticas-e-segurança)
9. [Exemplos de Programas Completos](#9-exemplos-de-programas-completos)

---

# 1. Introdução ao Controle Fanuc

O controle CNC Fanuc é o sistema de comando numérico mais amplamente utilizado em centros de usinagem e fresadoras no mundo. Desenvolvido pela FANUC Corporation (Japão), está presente desde máquinas com décadas de uso até os mais modernos centros de usinagem de alta velocidade. Este manual cobre a programação manual (programação ISO/EIA) para centros de usinagem com fresadoras.

## 1.1 Versões e Compatibilidade

| Série | Geração | Características Principais |
|---|---|---|
| Fanuc 0M | Clássica | Controle básico, 3 eixos, memória limitada, Macro B parcial |
| Fanuc 0i-MD/MF | Moderna | Macro B completo, G54.1 P1-P48, comunicação Ethernet, IOCP |
| Fanuc 16i / 18i | Advanced | Múltiplos canais, AICC, alta velocidade, Full Macro B |
| Fanuc 21i-MB | Mid-range | Semelhante ao 18i, interface modernizada |
| Fanuc 30i-B | Topo | Variables nomeadas em Macro, NURBS, 5 eixos avançado, AI Nano |

> ℹ️ **NOTA:** Códigos disponíveis podem variar de acordo com as opções adquiridas no CNC e configurações do fabricante da máquina (MTB — Machine Tool Builder). Consulte sempre o manual específico da sua máquina.

## 1.2 Estrutura Geral de um Programa NC

Um programa NC no controle Fanuc é formado por blocos (linhas) que contêm um ou mais endereços seguidos de valores numéricos. A estrutura básica é:

**Exemplo de Estrutura de Programa**

```gcode
O0001          (número do programa — endereço O, de 0001 a 9999)
N10 G21 G90 G17 G40 G49 G80 G54   (bloco de inicialização segura)
N20 T01 M06    (troca para ferramenta 1)
N30 S3000 M03  (spindle 3000 RPM, giro CW)
N40 G43 Z50. H01  (ativar comp. comprimento ferramenta 1)
N50 G00 X0. Y0.  (posicionar em XY)
N60 G01 Z-5. F300.  (descer em avanço até Z-5)
  ...
N9990 G00 Z100.   (recolher Z)
N9999 M30         (fim de programa, reset)
```

## 1.3 Endereços do Programa

| Endereço | Nome | Função / Uso |
|---|---|---|
| O | Número do programa | Identifica o programa (ex: O0001). Obrigatório no início. |
| N | Número de bloco | Número de sequência opcional (ex: N10, N20). Útil para desvios e debug. |
| G | Código G | Função preparatória de movimento, compensação, ciclo, etc. |
| M | Código M | Função auxiliar (spindle, refrigerante, troca de ferramenta, etc.) |
| X / Y / Z | Coordenadas lineares | Posição nos eixos de translação (em mm ou polegadas). |
| A / B / C | Coordenadas rotativas | Eixos rotativos (4º e 5º eixo — fresadoras avançadas). |
| I / J / K | Offsets de arco | Vetores incrementais do ponto inicial ao centro do arco em G02/G03. |
| R | Raio / Ponto R | Raio em interpolação circular ou plano de retorno em ciclos fixos. |
| F | Avanço (Feed rate) | Velocidade de avanço. Em mm/min (G94) ou mm/rev (G95). |
| S | Rotação (Speed) | Velocidade do spindle em RPM (ou m/min com G96 em torno). |
| T | Número de ferramenta | Seleciona a ferramenta (ex: T05 = ferramenta 5). |
| H | Registrador de comprimento | Número do offset de comprimento da ferramenta para G43/G44. |
| D | Registrador de raio | Número do offset de raio da ferramenta para G41/G42. |
| P | Parâmetro | Número de subprograma (M98), repetições em ciclos, dwell (G04) em ms. |
| Q | Profundidade de peck | Incremento de profundidade em ciclos G73/G83. |
| L | Número de repetições | Repetições em M98 e ciclos fixos (ex: M98 P100 L3). |
| # | Variável macro | Variável numérica usada em Macro B (ex: #100 = 25.5). |

## 1.4 Regras de Sintaxe

- A ordem dos endereços dentro de um bloco não é rígida, mas recomenda-se agrupar por tipo.
- Cada endereço pode aparecer apenas uma vez por bloco (exceto I, J, K em macros com múltiplos grupos).
- Blocos são executados sequencialmente, da primeira à última linha.
- Comentários são inseridos entre parênteses: (ISTO É UM COMENTÁRIO).
- O ponto decimal é necessário em valores com decimais: X10.0, não X10 (evita ambiguidade de unidades).
- Números de programa O0000 a O7999 são disponíveis para o usuário; O8000-O9999 são reservados pelo fabricante/MTB.

> ℹ️ **NOTA:** Códigos modais (ex: G01, G90, G54) permanecem ativos até serem cancelados ou substituídos por outro código do mesmo grupo. Códigos não-modais (ex: G04, G28) só afetam o bloco em que aparecem.

---

# 2. Códigos G — Referência Completa

Os códigos G (Funções Preparatórias) controlam os modos de operação da máquina. São classificados em modais — permanecem ativos até serem substituídos — e não-modais — válidos apenas no bloco em que aparecem. Cada código pertence a um grupo; dentro de um grupo, apenas um código pode estar ativo por vez.

## 2.1 Tabela Resumo — Todos os Códigos G

| Código G | Grupo | Modal | Função |
|---|---|---|---|
| G00 | 1 | Modal | Posicionamento rápido (rapid traverse) |
| G01 | 1 | Modal | Interpolação linear com avanço |
| G02 | 1 | Modal | Interpolação circular / helicoidal CW |
| G03 | 1 | Modal | Interpolação circular / helicoidal CCW |
| G04 | 0 | Não-modal | Tempo de espera (Dwell) |
| G09 | 0 | Não-modal | Parada exata — apenas no bloco atual |
| G10 | 0 | Não-modal | Entrada de dados programável (offsets, WCS) |
| G11 | 0 | Não-modal | Cancelamento de G10 |
| G15 | 17 | Modal | Cancelamento do modo de coordenada polar |
| G16 | 17 | Modal | Modo de coordenada polar ativo |
| G17 | 2 | Modal | Seleção do plano XY (padrão fresadoras) |
| G18 | 2 | Modal | Seleção do plano ZX |
| G19 | 2 | Modal | Seleção do plano YZ |
| G20 | 6 | Modal | Unidade em polegadas (inches) |
| G21 | 6 | Modal | Unidade em milímetros |
| G27 | 0 | Não-modal | Verificação de retorno ao ponto de referência |
| G28 | 0 | Não-modal | Retorno automático ao ponto de referência (home) |
| G29 | 0 | Não-modal | Retorno a partir do ponto de referência |
| G30 | 0 | Não-modal | Retorno ao 2º / 3º / 4º ponto de referência |
| G31 | 0 | Não-modal | Função de salto (skip) |
| G37 | 0 | Não-modal | Medição automática de comprimento de ferramenta |
| G39 | 0 | Não-modal | Compensação circular de canto (corner offset) |
| G40 | 7 | Modal | Cancelamento de compensação de raio |
| G41 | 7 | Modal | Compensação de raio à esquerda |
| G42 | 7 | Modal | Compensação de raio à direita |
| G43 | 8 | Modal | Compensação de comprimento de ferramenta (+H) |
| G44 | 8 | Modal | Compensação de comprimento de ferramenta (–H) |
| G49 | 8 | Modal | Cancelamento de compensação de comprimento |
| G50 | 11 | Modal | Cancelamento de escalonamento |
| G51 | 11 | Modal | Escalonamento (scaling) |
| G50.1 | 22 | Modal | Cancelamento de espelho programável |
| G51.1 | 22 | Modal | Espelho programável (programmable mirror image) |
| G52 | 0 | Não-modal | Sistema de coordenadas local temporário |
| G53 | 0 | Não-modal | Movimento em coordenadas de máquina (MCS) |
| G54 | 14 | Modal | Sistema de coordenadas de trabalho 1 (WCS 1) |
| G55 | 14 | Modal | Sistema de coordenadas de trabalho 2 (WCS 2) |
| G56 | 14 | Modal | Sistema de coordenadas de trabalho 3 (WCS 3) |
| G57 | 14 | Modal | Sistema de coordenadas de trabalho 4 (WCS 4) |
| G58 | 14 | Modal | Sistema de coordenadas de trabalho 5 (WCS 5) |
| G59 | 14 | Modal | Sistema de coordenadas de trabalho 6 (WCS 6) |
| G54.1 Px | 14 | Modal | Sistemas de coordenadas adicionais P1 a P48 |
| G61 | 15 | Modal | Modo de parada exata (exact stop mode) |
| G62 | 15 | Modal | Override automático de canto |
| G63 | 15 | Modal | Modo de roscamento (tapping mode) |
| G64 | 15 | Modal | Modo de corte contínuo (padrão) |
| G65 | 0 | Não-modal | Chamada simples de macro customizado (Macro B) |
| G66 | 12 | Modal | Chamada modal de macro customizado |
| G67 | 12 | Modal | Cancelamento de chamada modal de macro (G66) |
| G68 | 16 | Modal | Rotação do sistema de coordenadas |
| G69 | 16 | Modal | Cancelamento de rotação de coordenadas |
| G73 | 9 | Modal | Ciclo fixo: furação profunda rápida (chip-break) |
| G74 | 9 | Modal | Ciclo fixo: roscamento à esquerda |
| G76 | 9 | Modal | Ciclo fixo: mandrilamento fino |
| G80 | 9 | Modal | Cancelamento de todos os ciclos fixos |
| G81 | 9 | Modal | Ciclo fixo: furação simples |
| G82 | 9 | Modal | Ciclo fixo: furação com dwell |
| G83 | 9 | Modal | Ciclo fixo: furação profunda com peck |
| G84 | 9 | Modal | Ciclo fixo: roscamento à direita |
| G85 | 9 | Modal | Ciclo fixo: mandrilamento (retorno em avanço) |
| G86 | 9 | Modal | Ciclo fixo: mandrilamento (retorno rápido) |
| G87 | 9 | Modal | Ciclo fixo: mandrilamento reverso (back boring) |
| G88 | 9 | Modal | Ciclo fixo: mandrilamento manual |
| G89 | 9 | Modal | Ciclo fixo: mandrilamento com dwell |
| G90 | 3 | Modal | Programação em coordenadas absolutas |
| G91 | 3 | Modal | Programação em coordenadas incrementais |
| G92 | 0 | Não-modal | Definição de origem do sistema de coordenadas |
| G92.1 | 0 | Não-modal | Reset de coordenadas de trabalho ao padrão |
| G93 | 5 | Modal | Modo de avanço por tempo inverso |
| G94 | 5 | Modal | Modo de avanço por minuto (mm/min — padrão) |
| G95 | 5 | Modal | Modo de avanço por revolução (mm/rev) |
| G98 | 10 | Modal | Ciclos fixos: retorno ao plano inicial (I-level) |
| G99 | 10 | Modal | Ciclos fixos: retorno ao plano R |

## 2.2 Descrição Detalhada dos Códigos G Essenciais

### G00 — Posicionamento Rápido

Move a ferramenta à velocidade máxima da máquina (velocidade de rapid). Não realiza interpolação linear — cada eixo se move à sua própria velocidade máxima. Não deve ser usado durante o corte.

**Sintaxe:** `G00 X_ Y_ Z_`

**Exemplos G00**

```gcode
G00 X0. Y0. Z50.   (posiciona rapidamente em X0 Y0 Z50)
G00 Z5.            (sobe Z para 5mm acima da peça antes de XY)
```

> ⚠️ **ATENÇÃO:** Sempre recolha o eixo Z antes de movimentos laterais rápidos para evitar colisões com a peça.

### G01 — Interpolação Linear

Move a ferramenta em linha reta à velocidade de avanço programada (F). Utilizado durante o corte de material. O avanço F é obrigatório (ou deve estar ativo de um bloco anterior).

**Sintaxe:** `G01 X_ Y_ Z_ F_`

**Exemplos G01**

```gcode
G01 X100. F400.       (move de forma linear até X=100 a 400 mm/min)
G01 X50. Y30. Z-10. F250.  (movimento 3D simultâneo)
```

### G02 / G03 — Interpolação Circular

G02: arco no sentido horário (CW). G03: arco no sentido anti-horário (CCW). O plano deve estar selecionado (G17/G18/G19). O centro do arco é definido por I, J, K (vetores incrementais do ponto inicial ao centro) ou pelo raio R.

**Sintaxe com I,J:** `G02 X_ Y_ I_ J_ F_`
**Sintaxe com R:** `G02 X_ Y_ R_ F_`

**Exemplos G02/G03**

```gcode
(Arco CW no plano XY — centro via I,J)
G17 G02 X50. Y0. I25. J0. F200.

(Arco CCW usando raio R — semicírculo)
G17 G03 X0. Y50. R50. F200.

(Círculo completo com I,J — ponto final = ponto inicial)
G17 G02 I-25. J0. F200.   (circle de raio 25 a partir da posição atual)
```

> ℹ️ **NOTA:** Com R positivo: arco ≤ 180°. Com R negativo: arco > 180°. Para círculos completos, use apenas I, J, K (R não pode ser usado).

### G04 — Dwell (Tempo de Espera)

Pausa a execução pelo tempo especificado, sem movimento dos eixos. Usado para limpeza de cavaco, espera de refrigerante, ou estabilização do spindle.

**Sintaxe:** `G04 X_  ou  G04 P_  (P em milissegundos)`

**Exemplos G04**

```gcode
G04 X2.0    (pausa de 2 segundos)
G04 P2000   (pausa de 2000 ms = 2 segundos)
```

### G09 — Parada Exata (Não-modal)

Garante que o posicionamento seja exato no bloco em que aparece (desacelera até parar completamente antes do próximo bloco). Equivalente ao G61, mas válido apenas para um bloco.

**Exemplo G09**

```gcode
G09 G01 X100. F500.   (move a X100 e para exatamente antes do próximo bloco)
```

### G17 / G18 / G19 — Seleção de Plano

Define o plano de trabalho para interpolação circular (G02/G03), compensação de raio (G41/G42) e ciclos fixos. Padrão em fresadoras: G17 (plano XY).

| Código | Plano | Eixo Perpendicular | Uso Típico |
|---|---|---|---|
| G17 | XY | Z | Padrão — fresagem em plano horizontal |
| G18 | ZX | Y | Fresagem de perfis laterais em XZ |
| G19 | YZ | X | Fresagem de perfis laterais em YZ |

### G20 / G21 — Unidades de Medida

G21: milímetros (padrão no Brasil). G20: polegadas. Deve ser definido no início do programa e nunca alterado durante a execução.

> ⛔ **PERIGO:** Misturar G20/G21 em um mesmo programa causa erros imprevisíveis. Definir sempre no primeiro bloco e nunca alterar.

### G28 — Retorno ao Ponto de Referência

Retorna os eixos ao ponto de referência (home) da máquina, passando por um ponto intermediário definido no bloco. Essencial para trocas de ferramenta seguras.

**Sintaxe:** `G28 X_ Y_ Z_  (incrementais com G91 recomendado)`

**Exemplos G28**

```gcode
G91 G28 Z0.    (retorna Z ao home pelo ponto atual — mais seguro)
G91 G28 X0. Y0.  (retorna XY ao home)
G28 Z0.        (em absoluto — passando por Z=0 de máquina, perigoso!)
```

> ⛔ **PERIGO:** Sempre use G91 G28 Z0. para recolher Z antes. Em absoluto, G28 Z0. move para Z=0 do WCS atual antes do home, o que pode causar colisão.

### G30 — Retorno ao 2º Ponto de Referência

Retorna ao 2º (P2), 3º (P3) ou 4º (P4) ponto de referência. Muito usado para posição de troca de ferramenta quando diferente do home principal.

**Exemplos G30**

```gcode
G91 G30 Z0.     (retorna Z ao 2º ponto de referência — posição de troca)
G91 G30 P3 Z0.  (retorna Z ao 3º ponto de referência)
```

### G40 / G41 / G42 — Compensação de Raio da Ferramenta

Compensação automática do raio da fresa: G41 (à esquerda do caminho), G42 (à direita). O valor D define qual offset da tabela de ferramentas será usado. G40 cancela.

**Exemplo G41 — Compensação de Raio**

```gcode
(Ativar comp. de raio à esquerda — fresa subindo no contorno externo)
G41 G01 X10. Y10. D01 F200.   (ativar G41 com offset D01 em movimento linear)
G01 X100. Y10.                (contorno com compensação ativa)
G01 X100. Y80.
G01 X10.  Y80.
G01 X10.  Y10.
G40 G01 X0. Y0.               (cancelar G40 em movimento linear)
```

> ⚠️ **ATENÇÃO:** Sempre ative/desative G41/G42 em movimento linear (G00/G01), nunca em G02/G03. O caminho de entrada e saída deve ser maior que o raio da fresa.

### G43 / G44 / G49 — Compensação de Comprimento

G43: aplica o valor de comprimento do offset H à posição Z (adiciona). G44: subtrai. G49: cancela. Deve ser ativado após cada troca de ferramenta com o código H correspondente.

**Exemplo G43 — Compensação de Comprimento**

```gcode
T05 M06            (troca para ferramenta 5)
G43 Z50. H05       (ativa compensação de comprimento H05 — sobe para Z50 compensado)
S2500 M03
G00 X0. Y0.
G01 Z-3. F250.
  ...
G49 G00 Z200.      (cancela compensação e sobe Z — antes de nova troca)
```

### G52 — Sistema de Coordenadas Local

G52 cria um deslocamento temporário sobre o WCS ativo (G54-G59). Útil para programar padrões repetidos com origens locais. Cancelado com G52 X0 Y0 Z0 ou ao final do programa.

**Exemplo G52**

```gcode
G54              (seleciona WCS 1)
G52 X100. Y50.   (desloca temporariamente a origem 100mm em X e 50mm em Y)
  ... (programa da feature secundária aqui)
G52 X0. Y0. Z0.  (cancela deslocamento local — retorna à G54 original)
```

### G53 — Coordenadas de Máquina

Move em coordenadas absolutas de máquina (MCS), ignorando todos os offsets WCS. Não-modal — válido apenas no bloco em que aparece. Muito usado para posições de troca segura.

**Exemplos G53**

```gcode
G53 Z0.            (move Z ao zero de máquina — posição mais alta, segura)
G53 X-500. Y-200.  (posição de troca de ferramenta em coordenadas de máquina)
```

### G90 / G91 — Coordenadas Absolutas / Incrementais

G90 (padrão): todas as coordenadas referem-se à origem WCS ativa. G91: cada movimento é relativo à posição atual da ferramenta.

**Exemplos G90/G91**

```gcode
(Em G90 — absoluto)
G90 G01 X50. F200.   (move para X=50 em relação à origem)
G01 X100.            (move para X=100 em relação à origem — avanço 50mm)

(Em G91 — incremental)
G91 G01 X50. F200.   (move 50mm a partir da posição atual)
G01 X50.             (mais 50mm — posição resultante X=100 em relação à origem)
```

### G92 — Definição de Origem

Define a posição atual como o ponto de coordenada especificado, criando um deslocamento no WCS ativo. Alternativa a G52 para criar sub-origens.

**Exemplo G92**

```gcode
G92 X0. Y0. Z0.  (define posição atual como a nova origem X0 Y0 Z0)
```

> ⚠️ **ATENÇÃO:** G92 altera permanentemente o WCS ativo. Prefira usar G54.1 Px ou G52 para deslocamentos temporários, pois são mais seguros e previsíveis.

### G61 / G62 / G63 / G64 — Modos de Corte

| Código | Modo | Aplicação Típica |
|---|---|---|
| G61 | Parada exata (Exact Stop) | Cantos vivos, perfis angulares precisos. Desacelera até parar em cada bloco. |
| G62 | Override automático de canto | Reduce avanço automaticamente em cantos para melhorar superfície. |
| G63 | Modo roscamento | Ignora override de avanço — usado automaticamente em G84. |
| G64 | Corte contínuo (padrão) | Modo normal. Transições suaves entre blocos. Melhor para contornos curvos. |

### G68 / G69 — Rotação de Coordenadas

G68 rotaciona o sistema de coordenadas em torno de um ponto. Útil para usinar features em ângulos sem recalcular todas as coordenadas. G69 cancela a rotação.

**Sintaxe:** `G68 X_ Y_ R_` — onde X,Y é o centro de rotação e R é o ângulo em graus.

**Exemplo G68/G69**

```gcode
G68 X0. Y0. R45.    (rota o sistema 45° em torno da origem)
  ... (usinagem no sistema rotacionado)
G69                  (cancela a rotação — retorna ao WCS original)
```

> ℹ️ **NOTA:** G68 é disponível no Fanuc 16i, 18i, 21i e 30i. No Fanuc 0M, verifique se a opção está disponível.

### G94 / G95 — Modo de Avanço

| Código | Modo | Unidade | Aplicação |
|---|---|---|---|
| G94 | Avanço por minuto | mm/min (ou in/min com G20) | Padrão em fresadoras — usado na maioria das operações. |
| G95 | Avanço por rotação | mm/rev | Usado quando a alimentação depende da rotação (ex: rosqueamento de passo preciso). |

---

# 3. Códigos M — Funções Auxiliares

Os Códigos M controlam funções auxiliares da máquina-ferramenta: spindle, refrigerante, troca de ferramenta, paradas e chamadas de subprograma. Podem ser divididos em códigos padrão Fanuc e códigos definidos pelo fabricante da máquina (MTB).

> ⚠️ **ATENÇÃO:** Códigos M marcados como 'Fabricante' são exemplos comuns na indústria, mas podem variar ou não existir em sua máquina específica. Consulte o manual do fabricante da máquina.

## 3.1 Tabela Completa de Códigos M

| Código M | Tipo | Função | Observações |
|---|---|---|---|
| M00 | Padrão | Parada programada (Programmed Stop) | Interrompe ciclo. Operador deve pressionar [Cycle Start] para continuar. Spindle, coolant e feed pausam. |
| M01 | Padrão | Parada opcional (Optional Stop) | Para o ciclo somente se o botão 'Optional Stop' estiver ativado no painel. Útil em pontos de inspeção. |
| M02 | Padrão | Fim de programa (Program End) | Encerra o programa. Não reposiciona ao início em todos os controles. Menos usado que M30. |
| M03 | Padrão | Giro do spindle — horário (CW) | Deve ser acompanhado de S (ex: S2000 M03). Spindle gira CW visto de cima. |
| M04 | Padrão | Giro do spindle — anti-horário (CCW) | S deve estar programado. Giro CCW — para algumas fresas de forma especial ou machos à esquerda. |
| M05 | Padrão | Parada do spindle | Desacelera e para o spindle. Refrigerante não é afetado (requer M09 separado). |
| M06 | Padrão | Troca de ferramenta | Inicia a sequência de troca de ferramenta para a ferramenta T_ programada anteriormente. |
| M07 | Padrão* | Ligar refrigerante em névoa (Mist) | Ativa refrigerante em névoa. Disponível dependendo da máquina. |
| M08 | Padrão | Ligar refrigerante por inundação | Ativa refrigerante por inundação (flood coolant). Mais comum. |
| M09 | Padrão | Desligar refrigerante | Desativa todos os tipos de refrigerante. |
| M10 | Fabricante | Travar 4º eixo (clamp) | Bloqueia o eixo A/B para operações de fresagem. Varia por máquina. |
| M11 | Fabricante | Destravar 4º eixo (unclamp) | Libera o eixo A/B para indexação ou movimento. |
| M13 | Fabricante | Spindle CW + refrigerante | Combina M03 + M08 em um único bloco. Varia por máquina. |
| M14 | Fabricante | Spindle CCW + refrigerante | Combina M04 + M08 em um único bloco. Varia por máquina. |
| M19 | Padrão | Orientação do spindle | Para o spindle em posição angular definida. Necessário antes de G87 e em algumas trocas de ferramenta. |
| M30 | Padrão | Fim de programa + Rewind | Encerra o programa e retorna o cursor ao início. Reset de flags. Mais usado em produção em série. |
| M41 | Fabricante | Faixa de velocidade — 1ª marcha (baixa) | Seleciona a faixa de velocidade do câmbio. Válido em máquinas com câmbio mecânico. |
| M42 | Fabricante | Faixa de velocidade — 2ª marcha | |
| M43 | Fabricante | Faixa de velocidade — 3ª marcha | |
| M44 | Fabricante | Faixa de velocidade — 4ª marcha (alta) | |
| M48 | Fabricante | Habilitar override de avanço e spindle | Reativa os potenciômetros de override que foram desativados com M49. |
| M49 | Fabricante | Desabilitar override de avanço e spindle | Trava o override em 100% — usado em roscamento ou operações críticas. |
| M98 | Padrão | Chamada de subprograma | M98 Pxxxx — chama o programa Oxxxx. Com L: número de repetições. |
| M99 | Padrão | Fim de subprograma / Retorno de macro | Retorna ao bloco seguinte ao M98 no programa principal. Em macro, decrementa nível de variáveis. |

## 3.2 Descrição Detalhada e Exemplos

### M00 — Parada Programada

Para toda a execução: movimento, spindle e refrigerante. O operador inspeciona a peça e pressiona [Cycle Start] para retomar. É diferente do M01, que depende de chave.

**Exemplo M00 — Parada para Inspeção**

```gcode
G01 Z-10. F300.   (usina até Z-10)
M00               (pausa para inspeção — operador verifica cota)
G00 Z50.          (continua após pressionar Cycle Start)
```

### M01 — Parada Opcional

Idêntico ao M00, mas só é executado se o botão 'Optional Stop' no painel CNC estiver ligado. Usado para pontos de inspeção em série que podem ser saltados na produção normal.

**Exemplo M01**

```gcode
M01   (para somente se Optional Stop ativo no painel)
```

### M03 / M04 / M05 — Controle do Spindle

M03 gira o spindle no sentido horário; M04 no anti-horário; M05 para. O endereço S deve estar presente ou ter sido programado anteriormente.

**Exemplo M03/M05**

```gcode
S3000 M03     (liga spindle a 3000 RPM, sentido CW)
G04 X1.0      (aguarda 1 segundo para estabilizar)
G01 Z-5. F200. (inicia corte)
  ...
G00 Z50.      (recua Z)
M05           (para spindle)
M09           (desliga refrigerante)
```

### M06 — Troca de Ferramenta

Executa a troca de ferramenta. O endereço T define qual ferramenta deve estar no spindle após a troca. A sequência correta é essencial para segurança.

**Sequência Completa de Troca de Ferramenta**

```gcode
(Sequência recomendada de troca de ferramenta)
G49 G40 G80       (cancela compensações e ciclos fixos)
G91 G28 Z0.       (recolhe Z ao home incremental)
G91 G28 X0. Y0.   (recolhe XY ao home — opcional dependendo da máquina)
T02 M06           (troca para ferramenta 2)
G90 G54           (retorna ao modo absoluto, WCS 1)
G43 Z50. H02      (ativa compensação de comprimento da ferramenta 2)
S4000 M03         (liga spindle)
```

> ⛔ **PERIGO:** Nunca execute M06 com a ferramenta dentro da peça ou com Z baixo. Sempre recolha Z primeiro.

### M08 / M09 — Refrigerante

**Exemplo M08/M09**

```gcode
S2000 M03 M08   (liga spindle E refrigerante no mesmo bloco)
G01 Z-5. F250.
  ...
G00 Z50.
M05 M09         (para spindle E refrigerante juntos)
```

### M19 — Orientação do Spindle

Para o spindle em uma posição angular definida (tipicamente 0°). Necessário antes de operações de mandrilamento fino (G76, G87) onde a ferramenta precisa ser posicionada para não riscar o furo ao retrair.

**Exemplo M19**

```gcode
M19         (orienta spindle antes de retrair mandril fino)
G76 X50. Y30. Z-20. R2. Q0.5 F0.1   (mandrilamento fino — usa M19 internamente)
```

### M98 / M99 — Subprogramas

M98 chama um subprograma (outro programa O no controle). M99 encerra o subprograma e retorna ao próximo bloco no programa principal. O parâmetro L define o número de repetições.

**Exemplo M98/M99 — Subprograma**

```gcode
(Programa principal O0001)
G00 X0. Y0.
M98 P0100      (chama subprograma O0100 uma vez)
G00 X50. Y0.
M98 P0100 L3   (chama O0100 três vezes nesta posição)
M30

(Subprograma O0100)
O0100
G01 Z-5. F200.
G02 I10. J0. F300.    (círculo de raio 10)
G00 Z5.
M99            (retorna ao programa principal)
```

---

# 4. Sistemas de Coordenadas

O controle Fanuc opera com dois sistemas de referência principais: o sistema de coordenadas da máquina (MCS) e os sistemas de coordenadas de trabalho (WCS). Entender a diferença é fundamental para programação segura e correta.

## 4.1 Sistema de Coordenadas de Máquina (MCS)

O MCS tem origem no ponto de referência (home) da máquina, definido pelos sensores de referência. É ativado com G53. Todas as posições são brutas, sem offsets de WCS ou ferramentas.

**Exemplos com G53**

```gcode
G53 Z0.         (move Z ao zero de máquina — ponto mais alto, sempre seguro)
G53 X-600. Y0.  (posição absoluta de máquina — típica posição de troca)
```

> ℹ️ **NOTA:** G53 ignora todos os offsets (WCS, ferramenta, G52). Útil para posições fixas como troca de ferramenta e pontos de segurança absolutos.

## 4.2 Sistemas de Coordenadas de Trabalho (WCS)

Os WCS permitem definir a origem do programa em relação à peça. O Fanuc suporta 6 WCS padrão (G54–G59) e até 48 adicionais via G54.1 P1–P48 (disponível no 0i e superiores).

| Código | WCS | Uso Típico |
|---|---|---|
| G54 | WCS 1 | Padrão — peça única, fixação principal |
| G55 | WCS 2 | 2ª peça na mesma mesa ou 2ª operação |
| G56 | WCS 3 | 3ª peça ou 3ª face de usinagem |
| G57 | WCS 4 | 4ª peça |
| G58 | WCS 5 | 5ª peça ou posição especial |
| G59 | WCS 6 | 6ª peça ou posição de medição |
| G54.1 P1 | WCS 7 | Primeiro WCS adicional (0i em diante) |
| G54.1 P48 | WCS 54 | 48º WCS adicional (0i em diante) |

## 4.3 G52 — Deslocamento Local Temporário

Cria um offset temporário sobre o WCS ativo. Não altera o WCS em si — apenas desloca a origem localmente. Cancelado ao definir G52 X0. Y0. Z0.

**Exemplo G52 — Múltiplas Features com Sub-origem**

```gcode
G54               (origem no zero-peça principal)
G00 X0. Y0.

G52 X80. Y60.     (nova origem temporária em X80 Y60 do G54)
(agora X0 Y0 = ponto X80 Y60 do G54)
G01 X10. F300.    (move para X=10 da sub-origem = X90 do G54)
G52 X0. Y0. Z0.   (cancela G52 — retorna ao G54 puro)
```

## 4.4 G10 — Configuração de Offsets por Programa

Permite definir valores de WCS (G54–G59) e offsets de ferramenta diretamente no programa NC, sem intervenção manual no painel.

**Sintaxe WCS:** `G10 L2 Px X_ Y_ Z_` — Px = 1 para G54, 2 para G55, ..., 6 para G59
**Sintaxe Tool:** `G10 L10 Px Z_` — define comprimento da ferramenta Px

**Exemplos G10**

```gcode
G10 L2 P1 X-250. Y-180. Z-50.   (define G54: X=-250, Y=-180, Z=-50 de máquina)
G10 L10 P5 Z180.5               (define comprimento H05 = 180.5 mm)
G10 L12 P5 R6.35                (define raio D05 = 6.35 mm = fresa Ø12.7)
```

> ℹ️ **NOTA:** G10 L2 P1 = G54 (P1), P2 = G55, P3 = G56, P4 = G57, P5 = G58, P6 = G59. Para G54.1 Pxx adicional, use G10 L20 Pxx.

---

# 5. Compensações de Ferramentas

As compensações permitem que o programa trabalhe com coordenadas ideais enquanto o CNC ajusta automaticamente para as dimensões reais da ferramenta. Há dois tipos: compensação de comprimento (eixo Z) e compensação de raio (plano XY).

## 5.1 Compensação de Comprimento (G43 / G44 / G49)

Compensa a diferença entre o comprimento programado da ferramenta e o comprimento real. G43 adiciona o offset H ao Z programado; G44 subtrai; G49 cancela.

| Código | Efeito no Eixo Z | Uso Recomendado |
|---|---|---|
| G43 Hn | Z_real = Z_prog + H_n | Mais comum — offset positivo corresponde a ferramenta mais longa |
| G44 Hn | Z_real = Z_prog – H_n | Menos comum — evite se possível para simplificar setup |
| G49 | Cancela compensação | Executar antes de G28, G53 ou troca de ferramenta |

**Sequência com G43**

```gcode
(Setup de ferramenta: T01 = fresa Ø16, comp. comprimento H01 = 120.0 mm no offset)
T01 M06
G43 Z50. H01      (Z real = 50 + 120 = 170mm de máquina — acima da peça)
S3000 M03 M08
G00 X0. Y0.
G01 Z-2. F200.    (Z real = -2 + 120 = 118mm de máquina)
  ...
G49 G00 Z200.     (cancela compensação antes de nova troca)
M05 M09
```

> ⛔ **PERIGO:** O número H deve sempre corresponder à ferramenta montada no spindle. Usar H errado causa colisão catastrófica.

## 5.2 Compensação de Raio da Ferramenta (G41 / G42 / G40)

Permite programar o contorno da peça diretamente, sem calcular o offset do centro da fresa. G41: ferramenta à esquerda do caminho; G42: à direita. G40 cancela.

| Código | Posição da Ferramenta | Aplicação |
|---|---|---|
| G41 Dn | À esquerda da direção de avanço | Fresagem convencional de contorno externo; oco interno CCW |
| G42 Dn | À direita da direção de avanço | Fresagem em mergulho CW; contornos internos |
| G40 | Cancela compensação | Sempre necessário antes de saída do contorno |

**Exemplo G41 — Contorno Externo Retangular**

```gcode
(Fresar contorno retangular externo — fresa Ø16, D01 = 8.0 mm no offset)
G40 G00 X-20. Y-20.   (aproxima fora do contorno, G40 ativo)
G41 G01 X0. Y0. D01 F300.  (ativa G41 durante entrada — D01=raio)
G01 X100.
G01 Y80.
G01 X0.
G01 Y0.
G40 G01 X-20. Y-20.   (cancela G40 na saída do contorno)
```

> ⚠️ **ATENÇÃO:** A ativação de G41/G42 deve ocorrer em linha reta (G01), em um bloco que não esteja dentro da peça. O caminho de entrada e saída deve ser maior que o raio D.

## 5.3 Modos de Medição de Ferramenta

Os offsets de ferramenta (H e D) podem ser determinados e armazenados de três formas:

- **Manual:** operador mede e digita valores diretamente na tabela do CNC.
- **Por contato (Z-setter):** sensor de comprimento físico posicionado na mesa; G37 pode automatizar o processo.
- **Programático (G10):** valores inseridos diretamente no programa NC (ver seção de G10).

---

# 6. Ciclos Fixos de Usinagem

Os ciclos fixos (canned cycles) automatizam operações repetidas de furação, roscamento e mandrilamento. Uma vez ativado, o ciclo repete-se em cada posição XY programada até ser cancelado com G80.

> ℹ️ **NOTA:** Use G98 (retorno ao plano inicial) quando houver obstáculos entre furos. Use G99 (retorno ao plano R) quando a área entre furos for livre, para melhor desempenho.

## 6.1 Parâmetros Comuns dos Ciclos Fixos

| Parâmetro | Descrição | Observação |
|---|---|---|
| X, Y | Posição do furo no plano | Pode ser lista de pontos em blocos seguintes |
| Z | Profundidade final do furo | Posição Z de corte (normalmente negativo em G90) |
| R | Plano R (retraction plane) | Posição Z de segurança acima da peça (ex: R2. = 2mm acima de Z0) |
| Q | Incremento de peck / Shift | Profundidade de cada peck em G73/G83; deslocamento de centramento em G76/G87 |
| P | Dwell (ms) / Parâmetro | Tempo de pausa no fundo em G82, G88, G89. Em ms quando inteiro (P500 = 0.5s). |
| F | Avanço de corte | Velocidade de avanço durante a descida de corte (mm/min ou mm/rev) |
| K ou L | Repetições | Número de furos igualmente espaçados (apenas se K/L > 1) |
| G98 | Retorno ao nível inicial | Após o ciclo, Z retorna ao nível Z antes do ciclo (mais seguro) |
| G99 | Retorno ao plano R | Após o ciclo, Z retorna ao plano R (mais rápido entre furos próximos) |

## 6.2 Descrição Detalhada de Cada Ciclo Fixo

### G73 — Furação Profunda Rápida (High-Speed Peck)

Fura em pecks rápidos: desce Q mm, sobe um pequeno valor para quebrar o cavaco, repete até Z. Não retorna ao plano R entre pecks — mais rápido que G83.

**Sintaxe:** `G73 X_ Y_ Z_ R_ Q_ F_ K_`

**Exemplo G73**

```gcode
G98 G73 X30. Y20. Z-25. R2. Q3. F200.
(fura até Z=-25 em pecks de 3mm, retorna ao nível inicial entre posições)
```

### G74 — Roscamento à Esquerda (CCW)

Ciclo para machos de rosca à esquerda: desce com spindle CCW (M04), para no fundo, inverte para CW (M03) e retorna. O avanço F deve ser exatamente igual ao passo da rosca × RPM.

**Sintaxe:** `G74 X_ Y_ Z_ R_ F_`
**Cálculo de F:** F = S (RPM) × Passo (mm/rev)

**Exemplo G74**

```gcode
(Rosca M8×1.25 à esquerda — S=800, F = 800 × 1.25 = 1000)
S800 M04           (spindle CCW para rosca à esquerda)
G98 G74 X50. Y50. Z-20. R3. F1000.
```

### G76 — Mandrilamento Fino

Mandrilamento de alta precisão: desce em avanço, para no fundo com spindle orientado (M19), desloca Q no plano para liberar a faca da parede, e retorna rapidamente sem riscar o furo.

**Sintaxe:** `G76 X_ Y_ Z_ R_ Q_ P_ F_`

**Exemplo G76**

```gcode
(Mandrilar furo Ø30H7, profundidade 30mm, shift Q=0.3mm)
G98 G76 X100. Y50. Z-30. R2. Q0.3 P500 F0.08
(P500 = dwell de 500ms no fundo para acomodar pressão de corte)
```

> ℹ️ **NOTA:** Q é o shift (deslocamento para liberar a faca). Normalmente 0.1 a 0.5mm. P é dwell em ms no fundo. A direção do shift é definida por parâmetro da máquina.

### G80 — Cancelamento de Ciclo Fixo

Cancela qualquer ciclo fixo ativo (G73–G89). Deve ser programado quando o ciclo não for mais necessário ou antes de mudar de operação.

**Exemplo G80**

```gcode
G80   (cancela ciclo fixo ativo)
G80 G00 Z50.   (cancela ciclo e recua Z — forma mais comum no final de furação)
```

### G81 — Furação Simples

Ciclo básico: desce em avanço até Z, retorna a G98 ou R em rápido. Para furos rasos em material não problemático.

**Sintaxe:** `G81 X_ Y_ Z_ R_ F_`

**Exemplo G81 — Múltiplos Furos**

```gcode
G98 G81 X20. Y20. Z-15. R2. F250.  (furo em X20,Y20, Z-15)
X50. Y20.   (próximo furo — ciclo repete automaticamente)
X80. Y20.   (mais um furo)
G80         (cancela ciclo)
```

### G82 — Furação com Dwell

Igual ao G81, mas pausa no fundo (dwell P) antes de retrair. Útil para escarear, rebaixar ou melhorar o acabamento do fundo.

**Sintaxe:** `G82 X_ Y_ Z_ R_ P_ F_`

**Exemplo G82**

```gcode
G98 G82 X30. Y30. Z-8. R2. P500 F150.  (rebaixo com dwell 0.5s no fundo)
```

### G83 — Furação Profunda com Peck

Furação em incrementos Q: desce Q mm, retorna ao plano R para limpar cavaco, desce novamente Q+distância. Para furos profundos (L/D > 3) ou materiais com cavaco longo.

**Sintaxe:** `G83 X_ Y_ Z_ R_ Q_ F_`

**Exemplo G83**

```gcode
(Furo profundo Ø8, L=40mm, peck de 8mm, F=120 mm/min)
G98 G83 X0. Y0. Z-40. R2. Q8. F120.
```

> ℹ️ **NOTA:** G83 retorna ao plano R após cada peck — mais lento mas limpa melhor o cavaco. G73 é mais rápido (peck curto sem retorno completo).

### G84 — Roscamento (Tapping)

Ciclo de roscamento com macho: desce com spindle CW em avanço = S × passo, inverte para CCW e retorna. O controle ignora override de avanço (entra em G63 automaticamente).

**Sintaxe:** `G84 X_ Y_ Z_ R_ F_   (F = S × passo)`

**Exemplo G84 — Roscamento em Série**

```gcode
(Rosca M6×1.0 — S=800 RPM, F = 800×1.0 = 800 mm/min)
S800 M03
G98 G84 X30. Y30. Z-18. R3. F800.
X80. Y30.
X130. Y30.
G80 G00 Z50.
```

> ⚠️ **ATENÇÃO:** F deve ser calculado com precisão: F = S × Passo. Com avanço por revolução (G95), basta programar F = Passo diretamente (ex: F1.0 para M8×1).

### G85 — Mandrilamento

Desce em avanço até Z, retorna em avanço (não rápido). Bom acabamento na parede do furo — indicado para alvos de mandrilamento com tolerâncias medianas.

**Sintaxe:** `G85 X_ Y_ Z_ R_ F_`

**Exemplo G85**

```gcode
G98 G85 X60. Y40. Z-20. R2. F80.   (avanço de descida e retorno = F80)
```

### G86 — Mandrilamento com Retorno Rápido

Desce em avanço, para spindle no fundo, retorna rapidamente. O spindle parado permite retorno sem arranhar a parede, mas a parada pode deixar marca no fundo.

**Sintaxe:** `G86 X_ Y_ Z_ R_ F_`

**Exemplo G86**

```gcode
G98 G86 X60. Y40. Z-20. R2. F80.   (retorno rápido com spindle parado)
```

### G87 — Mandrilamento Reverso (Back Boring)

Usina a face inferior de um furo existente: a ferramenta desce com spindle orientado (tool nose deslocado), posiciona no fundo, gira o spindle e usina de baixo para cima.

**Sintaxe:** `G87 X_ Y_ Z_ R_ Q_ F_`

### G88 — Mandrilamento Manual

Desce em avanço até Z, para o spindle e entra em parada (como M00). O operador retira manualmente a ferramenta. Raramente usado em produção.

### G89 — Mandrilamento com Dwell

Como G85, mas com pausa no fundo (P). Retorna em avanço. Melhora acabamento do fundo e permite dissipar pressão de corte.

**Sintaxe:** `G89 X_ Y_ Z_ R_ P_ F_`

**Exemplo G89**

```gcode
G98 G89 X60. Y40. Z-20. R2. P500 F80.   (dwell 0.5s no fundo, retorno em avanço)
```

## 6.3 Quadro Resumo dos Ciclos Fixos

| Código | Descida | Fundo | Retorno | Aplicação |
|---|---|---|---|---|
| G73 | Avanço (pecks rápidos) | — | Rápido | Furos profundos — cavaco curto |
| G74 | Avanço (CCW) | Pausa + CW | Rápido | Roscamento à esquerda |
| G76 | Avanço | Dwell + Shift | Rápido | Mandrilamento fino de precisão |
| G81 | Avanço | — | Rápido | Furação simples |
| G82 | Avanço | Dwell | Rápido | Escareamento, rebaixo |
| G83 | Avanço (pecks) | — | Rápido ao R | Furos profundos — cavaco longo |
| G84 | Avanço (CW) | Pausa + CCW | Rápido | Roscamento à direita |
| G85 | Avanço | — | Avanço | Mandrilamento leve |
| G86 | Avanço | Para spindle | Rápido | Mandrilamento semi-fino |
| G87 | Avanço (reverso) | Gira spindle | Avanço (para cima) | Mandrilamento reverso |
| G88 | Avanço | Para + M00 | Manual | Mandrilamento manual |
| G89 | Avanço | Dwell | Avanço | Mandrilamento com dwell |

---

# 7. Subprogramas e Macro B

## 7.1 Subprogramas (M98 / M99)

Subprogramas permitem reutilizar sequências de código. São definidos como programas normais (Oxxxx) e chamados com M98. Não aceitam passagem de parâmetros (use Macro B para isso).

**Subprograma Completo com Repetições**

```gcode
(Programa principal O0010)
O0010
G21 G90 G17 G40 G49 G80 G54
T01 M06
G43 Z100. H01
S3000 M03 M08

G00 X0. Y0.       (posição 1)
M98 P0200         (executa subprograma O0200)

G00 X80. Y0.      (posição 2 — offset)
M98 P0200 L2      (executa O0200 duas vezes nesta posição)

G00 Z100.
M05 M09
M30

(Subprograma O0200 — fresar círculo)
O0200
G00 Z5.
G01 Z-3. F150.
G02 I20. J0. F400.
G00 Z5.
M99
```

> ℹ️ **NOTA:** Subprogramas podem ser aninhados em até 4 níveis (0i e 16i). No Fanuc 30i o limite pode ser maior. Subprogramas podem chamar outros subprogramas.

## 7.2 Macro B — Visão Geral

O Macro B (Custom Macro B) é a linguagem de programação paramétrica do Fanuc. Permite criar programas com variáveis, cálculos matemáticos, desvios condicionais (IF/WHILE), e chamadas com argumentos. Disponível a partir do Fanuc 0i com opção habilitada.

### Invocação de Macros

| Instrução | Tipo | Descrição |
|---|---|---|
| G65 Pxxx [args] | Simples (não-modal) | Chama macro Oxxx uma vez com argumentos. Não interfere no movimento. |
| G66 Pxxx [args] | Modal | Chama macro Oxxx após cada bloco de movimento até G67. |
| G67 | Cancelamento | Cancela chamada modal G66. |
| M98 Pxxx | Subprograma | Sem passagem de argumentos — variáveis locais não são criadas. |

### Mapeamento de Argumentos G65

Ao chamar uma macro com G65, os argumentos são passados via endereços de letra, que são mapeados automaticamente para variáveis locais #1–#33:

| Endereço | Variável | Endereço | Variável | Endereço | Variável |
|---|---|---|---|---|---|
| A | #1 | B | #2 | C | #3 |
| I | #4 | J | #5 | K | #6 |
| D | #7 | E | #8 | F | #9 |
| H | #11 | M | #13 | — | — |
| Q | #17 | R | #18 | S | #19 |
| T | #20 | U | #21 | V | #22 |
| W | #23 | X | #24 | Y | #25 |
| Z | #26 | — | — | — | — |

## 7.3 Variáveis Macro

| Faixa | Tipo | Comportamento | Uso Típico |
|---|---|---|---|
| #0 | Null | Sempre vazio/indefinido | Limpar variáveis: #100=#0 |
| #1 – #33 | Locais | Criadas por chamada G65; apagadas ao M99 | Argumentos e cálculos internos da macro |
| #100 – #199 | Comuns voláteis | Resetam ao desligar ou RESET | Contadores e dados temporários entre macros |
| #500 – #999 | Comuns não voláteis | Persistem após desligar (memória) | Contadores de peças, dados de setup, parâmetros |
| #1000+ | Sistema | Leitura/escrita de dados internos do CNC | Posição dos eixos, offsets, códigos modais |

### Variáveis de Sistema Importantes

| Variável | Leitura | Escrita | Descrição |
|---|---|---|---|
| #5001–#5005 | Sim | Não | Posição de bloco atual: #5001=X, #5002=Y, #5003=Z, #5004=A, #5005=B |
| #5021–#5025 | Sim | Não | Posição atual no WCS ativo: X, Y, Z, A, B |
| #5041–#5045 | Sim | Não | Posição atual em MCS (coordenadas de máquina) |
| #2001–#2200 | Sim | Sim | Offsets de comprimento de ferramenta (H01=desgaste, H01+200=geometria) |
| #2201–#2400 | Sim | Sim | Offsets de raio de ferramenta (D01–D200) |
| #5221–#5226 | Sim | Sim | Coordenadas do WCS G54 (X,Y,Z,A,B,C) |
| #5241–#5246 | Sim | Sim | Coordenadas do WCS G55 |
| #5261–#5266 | Sim | Sim | Coordenadas do WCS G56 |
| #4001–#4020 | Sim | Não | Código G modal do grupo 1–20 |
| #4120 | Sim | Não | Número da ferramenta (T) ativa |
| #3000 | Não | Sim | Emitir alarme de macro com mensagem (ex: #3000=1 (MSG)) |
| #3006 | Não | Sim | Exibir mensagem no painel CNC (ex: #3006=0 (PECA OK)) |

## 7.4 Operações Aritméticas e Funções

| Operação/Função | Sintaxe Macro B | Equivalente Matemático |
|---|---|---|
| Adição | `#i = #j + #k` | #i = #j + #k |
| Subtração | `#i = #j - #k` | #i = #j − #k |
| Multiplicação | `#i = #j * #k` | #i = #j × #k |
| Divisão | `#i = #j / #k` | #i = #j ÷ #k |
| Seno | `#i = SIN[#j]` | #i = sin(#j°) |
| Cosseno | `#i = COS[#j]` | #i = cos(#j°) |
| Tangente | `#i = TAN[#j]` | #i = tan(#j°) |
| Arcotangente | `#i = ATAN[#j]/[#k]` | #i = atan(#j/#k) em graus |
| Raiz quadrada | `#i = SQRT[#j]` | #i = √#j |
| Valor absoluto | `#i = ABS[#j]` | \|#j\| |
| Truncar decimal | `#i = FIX[#j]` | int(#j) — arredonda p/ zero |
| Arredondar | `#i = ROUND[#j]` | round(#j) |
| Teto | `#i = FUP[#j]` | ⌈#j⌉ |
| Logaritmo natural | `#i = LN[#j]` | ln(#j) |
| Exponencial | `#i = EXP[#j]` | e^#j |
| Potência | `#i = POW[#j,#k]` | #j ^ #k (30i) |

## 7.5 Controle de Fluxo

#### IF — Desvio Condicional

```gcode
IF [#1 GT 0] GOTO 100    (se #1 > 0, salta para bloco N100)
IF [#1 EQ 0] THEN #2=1   (se #1 = 0, executa: #2=1)

(Operadores de comparação)
(EQ = igual, NE = diferente, GT = maior, GE = maior/igual, LT = menor, LE = menor/igual)
```

#### WHILE — Loop

```gcode
WHILE [#1 LE 10] DO 1    (enquanto #1 <= 10, executa bloco DO 1)
  #2 = #2 + 1
  #1 = #1 + 1
END 1                    (fim do bloco DO 1)
```

## 7.6 Exemplo Completo de Macro B — Grade de Furos

```gcode
(Programa principal)
O0001
G21 G90 G17 G40 G49 G80 G54
T01 M06
G43 Z100. H01
S2500 M03 M08
(Chama macro O9010: grade de furos)
(A=Xcanto, B=Ycanto, I=EspX, J=EspY, K=QtdX, Q=QtdY, Z=Prof, R=PlanoR, F=Avanço)
G65 P9010 A0. B0. I25. J25. K4. Q3. Z-15. R2. F200.
G00 Z100.
M05 M09
M30

(Macro O9010 — Grade retangular de furos)
O9010
#100 = 0                    (contador coluna)
WHILE [#100 LT #6] DO 1     (#6 = K = qtd colunas)
  #101 = 0                  (contador linha)
  WHILE [#101 LT #17] DO 2  (#17 = Q = qtd linhas)
    #110 = #1 + #100 * #4   (X = A + coluna * I)
    #111 = #2 + #101 * #5   (Y = B + linha * J)
    G81 X#110 Y#111 Z#26 R#18 F#9
    #101 = #101 + 1
  END 2
  #100 = #100 + 1
END 1
G80
M99
```

---

# 8. Boas Práticas e Segurança

A programação CNC segura previne colisões, danos a ferramentas, peças e — mais importante — ao operador. Esta seção apresenta padrões e checklist recomendados para programação profissional com comando Fanuc.

## 8.1 Bloco de Inicialização Segura

Todo programa deve começar com um bloco que cancela todos os modos potencialmente herdados de um programa anterior. Nunca assuma o estado do controle ao iniciar.

**Bloco de Inicialização Padrão**

```gcode
O0001
(INICIALIZACAO SEGURA — sempre no inicio do programa)
G21          (mm — nunca omita a unidade)
G17          (plano XY)
G90          (coordenadas absolutas)
G94          (avanço por minuto)
G40          (cancela comp. de raio)
G49          (cancela comp. de comprimento)
G80          (cancela ciclos fixos)
G54          (seleciona WCS desejado)
(todos em um bloco, ou separados — ambos válidos)
G21 G17 G90 G94 G40 G49 G80 G54
```

## 8.2 Sequência Recomendada de Troca de Ferramenta

A sequência abaixo é a mais segura para troca de ferramenta em qualquer máquina Fanuc:

1. Cancelar compensações: G49 G40 G80
2. Recolher eixo Z ao home: G91 G28 Z0. (incremental — mais seguro)
3. Recolher XY se necessário: G91 G28 X0. Y0.
4. Selecionar ferramenta e executar troca: T_n_ M06
5. Retornar ao modo absoluto e WCS: G90 G54
6. Ativar compensação de comprimento: G43 Z_seguro_ H_n_
7. Ligar spindle e refrigerante: S___ M03 M08
8. Posicionar XY e iniciar corte.

**Modelo de Troca de Ferramenta**

```gcode
(Modelo de troca de ferramenta — copie e adapte)
G49 G40 G80         (cancela tudo)
G91 G28 Z0.         (Z ao home — incremental, seguro)
T02 M06             (troca para T02)
G90 G54             (absoluto, WCS 1)
G43 Z100. H02       (comp. comprimento T02, Z seguro)
S4500 M03 M08       (spindle + refrigerante)
G00 X0. Y0.         (posiciona XY)
```

## 8.3 Regras de Ouro — Prevenção de Colisão

> ⛔ **PERIGO:** Nunca mova XY em rápido (G00) sem garantir que Z está em posição segura acima da peça, fixações e grampos.

- **Regra do Z primeiro:** sempre recolha Z antes de qualquer movimento XY de deslocamento.
- **Nunca confie no estado do controle:** sempre inicialize G40, G49, G80 no início do programa.
- **Verifique o WCS:** confirme que G54 (ou outro) corresponde ao zero real da peça na máquina antes de executar.
- **Simule antes:** use as funções de simulação gráfica do CNC e reduza o avanço (override 0%) na primeira peça.
- **Verifique parâmetros de ciclos fixos:** confirme Z, R e F antes de iniciar qualquer ciclo de furação.
- **G98 vs G99:** prefira G98 (retorno ao plano inicial) em peças com grampos ou obstáculos entre furos.
- **H e T correspondentes:** o número H em G43 DEVE ser o mesmo que T para evitar crash por offset incorreto.
- **Limite de velocidade:** não exceda os limites de RPM da ferramenta e do mandril. Use S moderado na primeira passada.

## 8.4 Fim de Programa — Checklist

| Item | Código Recomendado | Finalidade |
|---|---|---|
| Recolher Z | G00 Z100. ou G91 G28 Z0. | Posição segura antes de desligar ou trocar peça |
| Parar spindle | M05 | Evita dano à ferramenta e peça |
| Desligar refrigerante | M09 | Evita acúmulo de fluido |
| Cancelar compensações | G40 G49 | Estado limpo para próximo programa |
| Cancelar ciclos fixos | G80 | Evita herança de ciclo ativo |
| Fim de programa | M30 | Reset e rewind — pronto para próxima peça |

**Bloco de Encerramento**

```gcode
(Bloco de encerramento recomendado)
G49 G40 G80         (cancela compensações e ciclos)
G91 G28 Z0.         (Z ao home)
G28 X0. Y0.         (XY ao home — opcional)
G90                  (retorna ao modo absoluto)
M05                  (para spindle)
M09                  (desliga refrigerante)
M30                  (fim de programa)
```

---

# 9. Exemplos de Programas Completos

## 9.1 Faceamento de Superfície

Fresar uma face retangular 100×80mm com fresa de face Ø80, em passadas no eixo X.

**Exemplo 1 — Faceamento**

```gcode
O0010  (FACEAMENTO 100x80mm  — FRESA FACE D80)
G21 G17 G90 G94 G40 G49 G80 G54
T01 M06           (fresa de face D80)
G43 Z100. H01
S800 M03 M08      (Vc aprox. 200 m/min para aço)

(Passada 1 — Y=-40, varredura em X de -50 a 150)
G00 X-50. Y-40.
G00 Z2.
G01 Z-0.3 F100.   (profundidade leve 0.3mm)
G01 X150. F500.

(Passada 2 — Y=0)
G00 Y0.
G01 X-50.

(Passada 3 — Y=40)
G00 Y40.
G01 X150.

G00 Z100.
M05 M09
M30
```

## 9.2 Fresagem de Contorno com Compensação de Raio

Fresar contorno externo retangular 80×60mm com ilhas nos cantos arredondados R10, fresa Ø10, G41.

**Exemplo 2 — Contorno com G41 e Cantos Arredondados**

```gcode
O0020  (CONTORNO EXTERNO ARREDONDADO — FRESA D10  G41)
G21 G17 G90 G94 G40 G49 G80 G54
T02 M06           (fresa cilíndrica Ø10)
G43 Z100. H02
S5000 M03 M08     (aço: Vc=157 m/min aprox.)

G00 X-15. Y-15.   (ponto de entrada — fora do contorno)
G00 Z5.
G01 Z-5. F150.    (desce para profundidade de corte 5mm)

(Ativa G41 na entrada)
G41 G01 X0. Y-10. D02 F400.

(Contorno — sentido CCW, G41 = ferramenta à esquerda = contorno externo)
G01 X80.
G02 X90. Y0. R10.
G01 Y60.
G02 X80. Y70. R10.
G01 X0.
G02 X-10. Y60. R10.
G01 Y0.
G02 X0. Y-10. R10.

(Cancela G40 na saída)
G40 G01 X-15. Y-15.

G00 Z100.
M05 M09
M30
```

## 9.3 Ciclo de Furação com Múltiplas Ferramentas

Furar, escareador e roscar uma grade de 3×2 furos M8×1.25, com pré-furo Ø6.8 e escareador 90°.

**Exemplo 3 — Furação, Escareamento e Roscamento**

```gcode
O0030  (GRADE DE FUROS M8 — PRE-FURO + ESCAREADOR + ROSCA)
G21 G17 G90 G94 G40 G49 G80 G54

(=== OPERAÇÃO 1: PRÉ-FURO Ø6.8 ===)
T03 M06           (broca Ø6.8)
G43 Z100. H03
S3000 M03 M08     (aço: ~64 m/min)
G00 Z5.

(Grade 3 colunas × 2 linhas, passo 40mm, canto inferior esquerdo X20 Y20)
G99 G83 X20. Y20. Z-22. R2. Q6. F100.
X60.
X100.
Y60. X20.
X60.
G98 X100.
G80 G00 Z100.
M05 M09

(=== OPERAÇÃO 2: ESCAREADOR 90° ===)
T04 M06           (escareador 90° Ø16)
G43 Z100. H04
S1200 M03 M08
G00 Z5.

G99 G82 X20. Y20. Z-3. R2. P300 F100.
X60.
X100.
Y60. X20.
X60.
G98 X100.
G80 G00 Z100.
M05 M09

(=== OPERAÇÃO 3: ROSCAMENTO M8×1.25 ===)
T05 M06           (macho M8×1.25)
G43 Z100. H05
S800 M03 M08
G00 Z5.

(F = S × passo = 800 × 1.25 = 1000 mm/min)
G99 G84 X20. Y20. Z-20. R5. F1000.
X60.
X100.
Y60. X20.
X60.
G98 X100.
G80 G00 Z100.
M05 M09
M30
```

## 9.4 Uso de Subprograma para Feature Repetida

**Exemplo 4 — Subprograma para Features Repetidas**

```gcode
O0040  (QUATRO REBAIXOS IGUAIS EM CANTOS — COM SUBPROGRAMA)
G21 G17 G90 G94 G40 G49 G80 G54
T06 M06           (fresa Ø20)
G43 Z100. H06
S2000 M03 M08

(Canto 1 — X20 Y20)
G00 X20. Y20.
M98 P0041

(Canto 2 — X120 Y20)
G00 X120. Y20.
M98 P0041

(Canto 3 — X120 Y100)
G00 X120. Y100.
M98 P0041

(Canto 4 — X20 Y100)
G00 X20. Y100.
M98 P0041

G00 Z100.
M05 M09
M30

(Subprograma O0041 — fresar rebaixo Ø30 prof. 5mm a partir da posição atual)
O0041
G00 Z3.
G01 Z-5. F150.
G02 I15. J0. F500.  (circulo Ø30 = raio 15)
G00 Z5.
M99
```

---

*Manual de Programação Fanuc CNC — Centros de Usinagem · Referência Técnica · v1.0*
