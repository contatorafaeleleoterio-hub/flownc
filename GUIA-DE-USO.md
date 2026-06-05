# GUIA DE USO — CNC Batch Editor

> Guia passo a passo para trocar códigos em lote nos seus programas CNC, com
> segurança. **O programa NUNCA altera seus arquivos originais** — ele sempre
> grava cópias em uma pasta nova.

---

## 0. Antes de começar (1 minuto)

1. A pasta `CNC_BatchEditor` (no pen drive ou no PC) precisa ter, lado a lado:
   - `CNC_BatchEditor.exe`  ← o programa
   - pasta `_internal`      ← as "tripas" (não precisa abrir)
   - pasta `data`           ← dentro tem `presets` (os perfis de máquina)
2. Dê **dois cliques** em `CNC_BatchEditor.exe`. A janela abre direto, sem instalar
   nada e sem tela preta de comando. **Isso é o normal.**
3. Se o Windows mostrar "SmartScreen" (tela azul "Windows protegeu seu PC"):
   clique em **"Mais informações" → "Executar assim mesmo"**. É falso positivo
   (o programa não é assinado digitalmente, mas é seguro e 100% offline).

---

## 1. O fluxo, em 7 passos

### Passo 1 — Conferir o perfil
No alto da janela, em **"Perfil:"**, deve aparecer `MAZAK_VTC530` (ou o seu).
O perfil guarda as trocas que você costuma usar, para reaproveitar.

### Passo 2 — Abrir os programas
Use um dos dois botões:
- **"Abrir pasta..."** → escolhe uma pasta inteira; ele lista todos os programas.
- **"Abrir programa(s)..."** → escolhe arquivos específicos.

> **IMPORTANTE — arquivos sem extensão (tipo `O2169`):** agora o programa
> aceita **qualquer arquivo de texto**, inclusive os Fanuc sem extensão. No
> "Abrir programa(s)...", o filtro já vem em **"Todos os arquivos"** — se não
> aparecerem, confira que está nesse filtro (canto inferior direito da janela
> de escolha).

Os programas aparecem na lista da **esquerda**, cada um com uma **caixinha ✓**.

### Passo 3 — Marcar quais programas vão receber as trocas
Só os **marcados (✓)** serão alterados. Por padrão vêm todos marcados.
Clicar em cima do nome de um programa **seleciona ele** para você ver/editar as
trocas que são só dele (lado direito, parte de baixo).

### Passo 4 — Definir as trocas
No lado **direito**:
- **"Trocas COMUNS"** (em cima): valem para **todos** os programas marcados.
  Ex.: `M08` → `M07` (troca fluido por névoa).
- **"Trocas SÓ DESTE programa"** (embaixo): valem só para o programa selecionado.
  Ex.: na PECA01, `T1` → `T21`.

Para cada linha de troca:
- **Aplicar (✓):** se está marcada, a troca é feita.
- **Buscar (o que está):** o código atual. Ex.: `M08`
- **Trocar por:** o código novo. Ex.: `M07`  (deixe **vazio** para *remover*)
- **Obs:** anotação livre (opcional).

Botões úteis: **"+ troca comum"** / **"+ troca só deste"** (nova linha),
**"- remover"** (apaga a linha selecionada), **"+ da lista"** (puxa de uma
biblioteca de códigos salvos).

### Passo 5 — Executar (preview obrigatório)
Clique em **"Executar substituições (preview)"**.

Abre uma tela de **revisão** onde você vê, **antes de salvar**:
- **CHECKLIST DE TROCAS PLANEJADAS** — quantas vezes cada troca foi encontrada:
  - `[OK] 'M08' -> 'M07': 3 ocorrência(s)` ✅ encontrou
  - `[aviso] 'M8' -> 'M7': 0 ocorrências` ⚠️ não achou (confira: era `M08`?)
- As **linhas alteradas** de cada programa (diff).
- **Alertas** (amarelo = atenção, vermelho = bloqueia salvar).

> Se aparecer **"Nada a trocar"**: nenhuma troca marcada encontrou ocorrência.
> Quase sempre é diferença de formato — ex.: você buscou `M8` mas no programa
> está `M08`. O sistema até sugere: *"achei 'M08'?"*.

### Passo 6 — Confirmar e salvar
Se estiver tudo certo, clique em **"Confirmar e salvar"**.
(Se houver erro **vermelho/crítico**, o botão fica **desabilitado** — corrija antes.)

### Passo 7 — Conferir o resultado
- Os arquivos novos vão para uma pasta **`_processado_PERFIL_data_hora`**, criada
  **ao lado dos originais** (ou na pasta fixa, se você escolheu uma em "Destino:").
- **Os originais continuam intactos.**
- Junto vem um arquivo **`..._log.txt`** com:
  - quantas trocas em cada programa,
  - a seção **`=== CONFERENCIA POS-SALVAMENTO ===`** que confere, por "impressão
    digital" (SHA-256), que cada arquivo foi gravado sem corrupção.

---

## 2. Aba "Verificações" (opcional, não altera nada)

Serve para checar regras nos programas **sem mexer neles**. Ex.:
- **Deve existir** `M30` (fim de programa)
- **Não pode existir** `M01`
- **Mínimo / Máximo / Exato** de um código

Marque as verificações e clique **"Executar verificações"**. O resultado aparece
embaixo. Use antes de processar para pegar problemas cedo.

---

## 3. Perguntas rápidas

**O botão "Executar" não fazia nada — e agora?**
Era um defeito (corrigido nesta versão). Agora, se acontecer qualquer erro, o
programa **mostra uma caixa de erro** em vez de ficar mudo. Se aparecer uma,
me mande o texto dela (tem um botão "Mostrar detalhes").

**Posso usar arquivos sem extensão (`O2169`, `O2170`...)?**
Sim. Agora o programa aceita qualquer arquivo de texto, com ou sem extensão.
Arquivos que não são texto (imagem, etc.) são marcados em vermelho e ignorados.

**E se eu errar?**
Nada é perdido: o original nunca muda. É só apagar a pasta `_processado_...` e
tentar de novo.

**Onde ficam minhas trocas salvas?**
Em **"Salvar perfil"** você grava o conjunto de trocas no perfil (arquivo JSON
em `data/presets`), para reaproveitar na próxima vez.

---

## 4. Em caso de problema

Anote: o que você clicou, o que esperava, e o que apareceu (ou não apareceu).
Se surgir caixa de erro, copie o texto dela. Isso ajuda a corrigir rápido.
