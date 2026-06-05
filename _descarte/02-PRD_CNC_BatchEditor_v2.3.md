# PRD v2.3 — FlowNC
## Editor Seguro de Substituições em Lote para Programas CNC

**Versão:** 2.3 — baseline de desenvolvimento (substitui v2.2)
**Data:** 2026-05-29
**Autor / Owner:** Rafael Eleotério
**Status:** Aprovado para execução
**Uso:** Individual — operador/programador CNC
**Plataforma:** Windows Desktop — EXE portátil (`onedir`), sem instalação formal
**Idioma da aplicação:** Português (Brasil)
**Princípio central:** nunca alterar arquivos originais; toda alteração deve ser previsível, auditável em preview e gravada com preservação máxima do arquivo CNC.

---

## Changelog v2.2 → v2.3

Mudanças de baseline. Cada item foi verificado empiricamente (execução real do motor de regex) antes de entrar.

| # | Tipo | Mudança | Seção |
|---|------|---------|-------|
| 1 | **Correção crítica** | Boundary CNC reescrito de `(?<![A-Z0-9.])…(?![0-9.])` para `(?<![A-Z])…(?![0-9.])`. O padrão antigo **bloqueava** `M6T1` e `G43H1T1` (caracteres concatenados após dígito), contradizendo os próprios vetores e a própria nota. | §8.2 |
| 2 | Correção | Nota da §8.2 reescrita (a anterior justificava o comportamento com raciocínio de regex invertido). | §8.2 |
| 3 | Correção | Vetor ambíguo de `(T1 USADO)` resolvido: **casa** → `(T21 USADO)`. Decisão de produto: o MVP altera texto dentro de comentários (sem consciência de comentário). | §15.1, §8.2 |
| 4 | **Escopo** | Inserção de comandos que cria **novas linhas/blocos** movida para fora do MVP (decisão de produto). `replace` é texto de linha única. | §3.2, §3.3, §4 |
| 5 | Correção | Conflito entre regras **sempre resolve** (§8.4) → exibido como **Atenção (amarelo)** com log de supressão. Vermelho passa a ser exclusivo de falha estrutural/leitura/arquivo vazio. | §8.4, §11.5 |
| 6 | Correção | Condições de bloqueio de salvamento consolidadas (estrutural crítico **ou** `on_zero_matches=error` com 0 ocorrências **ou** falha de leitura em todos os arquivos). | §11.4, §11.7 |
| 7 | Melhoria | Dica de *leading-zero*: regra com 0 ocorrências cujo `find` casa com um endereço só por diferença de zero (ex.: `M8` vs `M08`) sugere a forma encontrada no lote. | §8.5 |
| 8 | Melhoria | Colisão de `basename` em regras `scope=file` definida explicitamente. | §7.2, §9.3 |
| 9 | Melhoria | Vetores de teste ganham **IDs estáveis** (`TV-*`); Anexo C passa a referenciar IDs, não números de linha. | §15, Anexo C |
| 10 | Correção | Rótulo dos anexos no §0 corrigido (Anexo B é Privacidade/Rede; o schema JSON está na §13.1). | §0 |
| 11 | Polimento | Notas: verificações usam só `literal`/`cnc_address` (sem `auto`); `replace` não preserva caixa; encoding de log/JSON é UTF-8; nota de licença PySide6 (LGPL). | §10.1, §12.1, §13 |

---

## 0. Como Ler Este Documento

Este PRD é a **fonte única de verdade** para o desenvolvimento do MVP. Todo plano de execução, sprint, task e prompt de implementação deve referenciar seções deste documento por número (ex.: "implementar §8.2"). Decisões que divergirem deste PRD exigem atualização aqui antes do código.

- Seções §1–§6: contexto e escopo (read-only para devs).
- Seções §7–§13: especificação técnica de **o que** construir.
- Seções §14–§15: critérios verificáveis (Definition of Done).
- Seções §16–§19: riscos, padrões e roadmap de execução.
- Anexos: **A** glossário, **B** política de privacidade/rede, **C** matriz de rastreabilidade. (O schema JSON do preset está na §13.1, não em anexo.)

---

## 1. Problema

Programas CNC gerados por CAM ou programadores externos chegam em padrão genérico. Antes de cada ordem de produção, o programador precisa adaptar manualmente dezenas de arquivos para a realidade da máquina: magazine de ferramentas, offsets, rotações, fluido, alturas de segurança e comandos operacionais.

Esse processo hoje é feito abrindo cada arquivo individualmente em editor de texto. É repetitivo, lento e sujeito a erros críticos como ferramenta incorreta, offset errado, colisão, refugo e parada de produção.

---

## 2. Objetivo do Sistema

Criar uma ferramenta desktop para Windows que permita configurar regras de substituição textual em lote, organizadas por perfil de máquina, aplicá-las a múltiplos arquivos NC e revisar o resultado antes de salvar.

O sistema deve:

- Processar múltiplos arquivos em uma operação controlada.
- Aplicar regras globais por perfil e regras específicas por arquivo.
- Mostrar contagem e preview/diff antes da gravação.
- Salvar sempre em pasta de saída separada.
- Preservar os arquivos originais intactos.
- Reduzir risco de substituições destrutivas por matching validado.
- Alertar quando uma regra ativa não encontrou ocorrência.
- Validar estrutura mínima do arquivo resultante antes de confirmar o salvamento.

### 2.1 Métricas de Sucesso do MVP

| Métrica | Alvo |
|---------|------|
| Tempo para preparar um lote típico (12 arquivos) | ≤ 3 min, vs. ~20 min manualmente |
| Falsos positivos em matching (ex.: `T1` casando em `T10`) | 0 nos vetores §15 |
| Falsos negativos em matching (ex.: `T1` não casando em `M6T1`) | 0 nos vetores §15 |
| Arquivos originais alterados acidentalmente | 0 |
| Lote concluído sem revisão de preview | Impossível por design |
| Taxa de regressão entre releases (testes §15) | 100% verde antes de gerar EXE |

---

## 3. Escopo do MVP

### 3.1 Dentro do Escopo

- Substituição textual em lote com múltiplos arquivos e múltiplas regras.
- Matching seguro para códigos CNC comuns (`T`, `H`, `D`, `G`, `M`, `S`, `F`) quando a regra tiver formato de endereço CNC.
- Substituição literal segura para textos livres, comentários e comandos compostos, **na mesma linha**.
- Remoção de texto (regra com `replace` vazio).
- Presets por máquina salvos em JSON local versionado.
- Regras globais por perfil.
- Regras individuais por arquivo, com resolução de conflito definida.
- Preview/diff obrigatório antes de salvar.
- Relatório visual de contagem por regra e por arquivo.
- Verificações configuráveis de presença, ausência e contagem.
- Verificações estruturais obrigatórias independentes do usuário.
- Salvamento em pasta separada com escrita atômica.
- Preservação de encoding, BOM e quebra de linha sempre que possível.
- Log de execução do lote, exportável manualmente como `.txt`.
- EXE portátil Windows.
- Interface em light mode, em Português (Brasil), objetiva e operacional.

### 3.2 Fora do Escopo do MVP

- Simulação de trajeto, backplot ou validação geométrica.
- Parser CNC completo.
- Interpretação lógica profunda de G-code.
- Regex digitado pelo usuário.
- **Inserção de comandos que cria novas linhas/blocos** (ex.: `M30` → `M00` + nova linha + `M30`). O `replace` é de **linha única**; o motor não introduz quebras de linha.
- Consciência de comentários: o sistema **não** distingue código de comentário; texto dentro de `(...)` pode ser alterado por uma regra que case ali (ver §8.2 e §15.1).
- Comunicação DNC ou envio direto para máquina.
- Versão web ou mobile.
- Histórico persistente entre sessões (sessão atual apenas).
- Exportação de relatório em PDF/Excel (apenas `.txt` simples).
- Replicação automática de operações para múltiplas peças na mesa.
- Inserção arbitrária sem âncora textual.
- Detecção completa de colisão, ferramenta errada ou offset perigoso.
- Telemetria, analytics ou qualquer envio de dados pela rede.
- Internacionalização para outros idiomas.

### 3.3 Limitações Explícitas

Algumas necessidades operacionais podem ser parcialmente atendidas por substituição textual, mas **não devem ser prometidas** como validação CNC completa:

- **Troca de ferramenta:** o sistema pode substituir `T`, `H` e `D`, mas não garante semanticamente que ferramenta, comprimento e raio pertencem ao mesmo conjunto, exceto pelas verificações configuradas.
- **Inserção de comandos:** o MVP só faz substituição textual **na mesma linha**. Não cria linhas/blocos novos — nem por âncora, nem por número de linha. Trocar `M30` por uma sequência multilinha está fora do MVP.
- **Comentários:** uma regra que case dentro de um comentário `(...)` **vai alterar** o comentário (não há consciência de comentário). Endereços colados em palavras — ex.: `T1` dentro de `(OFFSET1)` — **não** casam, por causa do boundary §8.2.
- **Múltiplas peças na mesa:** replicar blocos para `G55`, `G56` etc. exige cópia e transformação de regiões. Fora do MVP.
- **T duplicado:** o MVP pode contar ocorrências e alertar duplicidade simples, mas não interpreta se a duplicidade é correta dentro da estratégia do programa.

---

## 4. Tipos de Alteração Suportados

| # | Categoria | Suporte no MVP | Observação |
|---|-----------|----------------|------------|
| 1 | Troca de ferramenta | Parcial | Substitui `T`, `H`, `D`; recomenda grupo vinculado (verificação opcional de consistência) |
| 2 | Ajuste de offset de origem | Sim | Ex.: `G54` → `G55` |
| 3 | Ajuste de rotação spindle | Sim | Ex.: `S2500` → `S3000` |
| 4 | Ajuste de avanço | Sim | Ex.: `F150` → `F300` |
| 5 | Controle de fluido/ar | Sim | Ex.: `M08` → `M07`, remover `M09` |
| 6 | Alturas de segurança | Sim | Ex.: `Z20.` → `Z50.` como texto literal |
| 7 | Inserção/remoção de comandos | Parcial | **Remoção:** sim (`replace` vazio). **Troca na mesma linha:** sim. **Inserir novas linhas/blocos:** fora do MVP |
| 8 | Rotação/espelhamento textual | Parcial | Ex.: `R90` → `R180`; sem validar geometria |
| 9 | Múltiplas peças na mesa | Fora do MVP | Exige replicação de blocos |
| 10 | Verificação de consistência | Parcial | Presença, ausência, contagem e estrutura mínima |

> **Nota técnica:** o sistema não interpreta lógica CNC completa nem distingue código de comentário. Executa substituições textuais controladas, com matching seguro, preview obrigatório e validações de saída.

---

## 5. Perfil do Usuário

- **Quem:** programador/preparador CNC individual.
- **Máquinas:** centros de usinagem de fresamento 3+ eixos.
- **Controles:** Fanuc como referência primária; sistema neutro ao dialeto sempre que possível.
- **Arquivos:** extensões configuráveis por perfil (`.nc`, `.txt`, `.iso`, `.ptp`, `.min`, `.mpf`).
- **Volume típico:** até 12 arquivos por lote; pico ocasional de 30 a 50.
- **Tamanho típico de arquivo:** 5 KB a 2 MB.
- **Local dos arquivos:** pasta local Windows (ex.: `C:\Programas_CNC`).
- **Ambiente:** PC de escritório ou chão de fábrica, possivelmente offline.

---

## 6. Requisitos de Plataforma

| Item | Requisito |
|------|-----------|
| Sistema operacional | Windows 10 x64 22H2 ou superior, Windows 11 |
| Memória | 4 GB RAM mínimo |
| Disco | 500 MB livres recomendado |
| Resolução mínima | 1366×768 |
| Permissões | Leitura na pasta de entrada e escrita na pasta de saída |
| Execução | 100% offline; nenhuma chamada de rede em qualquer caminho de código |
| Distribuição | PyInstaller `onedir` preferencial; `onefile` somente se validado com antivírus |

**Justificativa:** PySide6/Qt6 não suporta Windows 7/8. `onefile` aumenta probabilidade de falso positivo em AV.

### 6.1 Orçamento de Performance

| Cenário | Alvo |
|---------|------|
| Carregar lote de 50 arquivos (≤ 200 KB cada) | ≤ 2 s |
| Dry-run de 50 arquivos com 20 regras | ≤ 3 s |
| Renderizar preview de 1 arquivo | ≤ 500 ms |
| Salvar lote de 50 arquivos | ≤ 5 s |
| Arquivo individual máximo suportado sem aviso | 5 MB |
| Arquivo > 5 MB | Carrega com aviso visual amarelo |
| Arquivo > 50 MB | Bloqueia carregamento com mensagem clara |

A UI **não pode congelar** em nenhum cenário acima — qualquer operação que exceda 200 ms deve rodar em `QThread` com indicador de progresso.

---

## 7. Arquitetura de Regras

### 7.1 Hierarquia

```text
Perfil de Máquina: MAZAK_VTC530
├── Regras Globais do Perfil
│   ├── [✓] M08 → M07
│   ├── [✓] G54 → G55
│   └── [✓] S3000 M03 → vazio
│
└── Regras Individuais por Arquivo
    ├── PECA01.nc → T1: T21
    ├── PECA02.nc → T1: T15
    └── PECA03.nc → T1: T08
```

### 7.2 Estrutura de uma Regra

| Campo | Obrigatório | Tipo | Descrição |
|-------|-------------|------|-----------|
| `id` | Sim | string | Identificador único estável (UUIDv4 sugerido) |
| `active` | Sim | bool | Liga/desliga a regra sem apagá-la |
| `scope` | Sim | enum | `global` ou `file` |
| `file` | Condicional | string | Nome do arquivo (basename) quando `scope=file` |
| `find` | Sim | string | Texto literal a localizar (linha única) |
| `replace` | Sim | string | Novo texto (linha única); string vazia significa remoção |
| `mode` | Sim | enum | `auto`, `literal` ou `cnc_address` |
| `comment` | Não | string | Anotação livre |
| `on_zero_matches` | Sim | enum | `warn` (padrão), `ignore`, `error` |
| `priority` | Não | int | Desempate entre regras em conflito; menor vence; default 100 |

**Restrições de campo:**

- `find` e `replace` são de **linha única**. O editor de regra rejeita quebras de linha coladas; o motor nunca introduz quebra de linha (ver §3.2).
- `scope=file` casa pelo **basename** do arquivo. Se o lote contiver dois arquivos com o mesmo basename vindos de pastas diferentes, a regra de arquivo se aplica a **todos** os arquivos com aquele basename, e o sistema **alerta a duplicidade** (§9.3). Recomenda-se basenames únicos por lote.

### 7.3 Modos de Matching

| Modo | Uso | Comportamento |
|------|-----|---------------|
| `auto` | Padrão | Aplica heurística §7.3.1 para escolher entre `cnc_address` e `literal` |
| `literal` | Texto livre | `re.escape(find)` + busca direta, sem boundary CNC |
| `cnc_address` | Endereços como `T1`, `M08`, `G54` | `re.escape(find)` + boundary CNC §8.2 |

O usuário **não digita regex**. Todo conteúdo do campo `find` é tratado como texto literal antes de virar expressão interna.

#### 7.3.1 Heurística do Modo `auto`

`find` é classificado como `cnc_address` se, e somente se, satisfaz **todas**:

1. Casa o padrão `^[A-Z][0-9]+$` (uma letra maiúscula seguida só de dígitos).
2. A letra inicial está no conjunto `{T, H, D, G, M, S, F, N, O, P, Q, R}`.
3. Não contém ponto, espaço, vírgula, parênteses, ou múltiplos tokens.

Caso contrário, `auto` cai em `literal`. Exemplos:

| `find` | Resolvido como | Motivo |
|--------|----------------|--------|
| `T1` | `cnc_address` | Letra+dígitos |
| `M08` | `cnc_address` | Letra+dígitos |
| `S3000 M03` | `literal` | Múltiplos tokens |
| `Z20.` | `literal` | Contém ponto |
| `(FRESA Ø12)` | `literal` | Texto livre |
| `X-1.5` | `literal` | Contém sinal e ponto |

---

## 8. Motor de Substituição Seguro

### 8.1 Regras Obrigatórias

- Nunca usar `str.replace()` simples para códigos CNC.
- Sempre aplicar `re.escape(find)` ao texto fornecido pelo usuário.
- Aplicar boundary CNC somente quando o modo resolvido for `cnc_address`.
- Evitar casar `T1` dentro de `T10`, `T100` ou `T1.5` (lookahead §8.2).
- Permitir casar `T1` em blocos concatenados como `M6T1`, `G43H1T1` e `Z20.T1` (o caractere anterior é dígito ou ponto, fim do endereço anterior).
- Evitar casar `T1` dentro de uma palavra de comentário como `(OFFSET1)` (caractere anterior é letra).
- Case-sensitive por padrão; case-insensitive opcional via flag `case_sensitive: false` no preset.
- Aplicar regras contra o **conteúdo original** em uma etapa planejada, sem cascata.
- Detectar sobreposição entre matches e marcar conflito antes de salvar.

### 8.2 Boundary CNC

Para `cnc_address`, o padrão é:

```python
pattern = rf"(?<![A-Z]){re.escape(find)}(?![0-9.])"
```

- **Lookbehind `(?<![A-Z])`**: impede casar quando o `find` está colado a uma **letra** antes — isto é, dentro de uma palavra (ex.: `T1` em `(OFFSET1)`). **Permite** caractere anterior dígito ou ponto, porque em CNC o caractere antes de um endereço real é o fim do endereço anterior (`M6T1`, `G43H1T1`, `Z20.T1`).
- **Lookahead `(?![0-9.])`**: impede `T1` casar em `T10`, `T100`, `T1.5`, e impede `G54` casar em `G54.1` (código estendido diferente).

> **Por que o lookbehind NÃO inclui `0-9` nem `.`:** em Fanuc real é comum concatenar endereços sem espaço (`M6T1`, `G43H1T1`) e endereços após coordenada decimal (`Z20.T1`). Se o lookbehind proibisse dígito/ponto antes, o motor **deixaria de aplicar** a regra exatamente nesses casos — falha silenciosa que leva ferramenta errada à máquina. Por isso o lookbehind testa **apenas letra**. Vetores `TV-CNC-02`, `TV-CNC-03` e `TV-CNC-04` cobrem isto e **devem** passar.

Exemplos esperados (todos verificados por execução real do motor):

| Regra | Texto | Casa? | Motivo |
|-------|-------|-------|--------|
| `T1` | `T1 M6` | Sim | Código isolado |
| `T1` | `M6T1` | Sim | Bloco concatenado real (dígito antes) |
| `T1` | `G43H1T1` | Sim | Após dígito de outro endereço |
| `T1` | `Z20.T1` | Sim | Após coordenada decimal (ponto antes) |
| `T1` | `(T1 USADO)` | Sim | Token isolado dentro de comentário; o MVP altera comentários (§3.3) |
| `T1` | `(OFFSET1)` | Não | `T1` colado em letra → parte de palavra, não endereço |
| `T1` | `T10` | Não | Evita troca destrutiva |
| `T1` | `T100` | Não | Evita troca destrutiva |
| `F1` | `F1.5` | Não | Evita corromper decimal |
| `G54` | `G54.1` | Não | `G54.1` é código estendido diferente |
| `M8` | `M08` | Não | Formato diferente; alerta 0 ocorrências + dica de leading-zero §8.5 |

### 8.3 Plano de Substituição (sem cascata)

```text
Regra 1: G54 → G55
Regra 2: G55 → G56
```

Se aplicadas em cascata, `G54` viraria `G56`. Comportamento correto:

1. Localizar todos os matches de **todas** as regras contra o **conteúdo original**.
2. Construir lista de intervalos `(start, end, rule_id, replacement)`.
3. Detectar sobreposições (§8.4).
4. Compor o resultado final em uma única passagem, do fim para o início.
5. Registrar no plano qual regra alterou cada trecho.

### 8.4 Resolução de Conflitos

Conflito = dois matches com sobreposição de bytes no original.

Ordem de desempate (sempre produz um vencedor determinístico):

1. **Regra de arquivo** vence regra global sobreposta no escopo daquele arquivo (regra global suprimida, registrada no log).
2. Caso ainda haja conflito: `priority` menor vence.
3. Caso `priority` igual: regra declarada primeiro vence (ordem do JSON).
4. Sempre exibir no preview: qual regra venceu, qual foi suprimida e por quê.

Como o passo 3 é um critério total, **todo conflito é resolvido**. Conflito não bloqueia o salvamento: é sinalizado como **Atenção (amarelo)** com a decisão registrada no log (§11.5).

### 8.5 Regras Sem Ocorrência

Regra ativa com 0 matches no lote inteiro:

- `on_zero_matches=warn` (padrão): alerta amarelo, não bloqueia salvar.
- `on_zero_matches=ignore`: silencia (útil para regra opcional que só se aplica a alguns arquivos).
- `on_zero_matches=error`: bloqueia salvar até desativar ou ajustar.

Contagem é **por lote**, não por arquivo, salvo se for `scope=file` (aí é por arquivo específico).

**Dica de leading-zero:** quando uma regra `cnc_address` casa 0 vezes mas existe no lote um endereço idêntico a menos de zeros à esquerda (ex.: regra `M8`, lote contém `M08`; regra `T1`, lote contém `T01`), o alerta inclui a sugestão: *"0 ocorrências de `M8`. Encontrado `M08` — você quis dizer `M08`?"*. Isso ataca o erro de campo mais comum (formato com/sem zero) sem adivinhar pelo usuário.

### 8.6 Whitespace Após Remoção

Quando `replace` é vazio e o match remove texto:

- Padrão: o motor remove **apenas** os caracteres casados; não tenta limpar espaços vizinhos.
- Espaços duplos resultantes são visíveis no preview e responsabilidade do usuário.
- Verificação estrutural não falha por espaço duplo.

---

## 9. Leitura, Escrita e Preservação de Arquivo

### 9.1 Leitura

Leitura sempre em **binário**, com detecção de:

- Encoding.
- Presença de BOM.
- Quebra de linha predominante: `CRLF`, `LF` ou `CR`.
- Arquivo vazio.
- Arquivo binário/não textual (rejeitar).

Estratégia:

1. Detectar BOM: `utf-8-sig`, `utf-16-le`, `utf-16-be`.
2. Tentar `utf-8`.
3. Tentar `cp1252`.
4. Fallback `latin-1` (nunca falha).
5. Registrar nível de confiança: `alta` (BOM ou utf-8 limpo), `média` (cp1252 válido), `baixa` (fallback latin-1).

Confiança `baixa` é exibida na coluna de status do arquivo em amarelo.

Arquivos com alta densidade de bytes nulos (típico de UTF-16 sem BOM ou binário real) são tratados como não textuais e rejeitados (§9.3).

`charset-normalizer` é opcional; gravação **deve preservar** a codificação detectada.

### 9.2 Escrita

- Gravar na mesma codificação detectada.
- Preservar BOM quando existir.
- Preservar EOL predominante do original.
- Escrita atômica: arquivo temporário (`.tmp` na pasta de saída), `flush`, `fsync` quando suportado, `os.replace` final.
- **Nunca** sobrescrever o original.
- **Nunca** deixar arquivo parcial como resultado final.
- Sufixo incremental quando a pasta de saída já existir.

Pasta de saída:

```text
[origem]/_processado_NOMEPERFIL_YYYYMMDD_HHMMSS/
```

Colisão:

```text
[origem]/_processado_NOMEPERFIL_YYYYMMDD_HHMMSS_02/
```

### 9.3 Proteções de Entrada

- Ignorar automaticamente pastas `_processado_*`.
- Alertar se o arquivo estiver somente leitura.
- Alertar duplicidade de basenames vindos de pastas diferentes — e, quando houver regra `scope=file` para esse basename, avisar que ela se aplicará a todos os arquivos homônimos (§7.2).
- Arquivos com falha de leitura são marcados em vermelho e **excluídos** do processamento; lote continua.
- Erro por arquivo nunca aborta o lote inteiro.

---

## 10. Verificações

### 10.1 Verificações Configuráveis

| Tipo | Exemplo | Resultado |
|------|---------|-----------|
| `must_exist` | `M30` | Alerta se ausente |
| `must_not_exist` | `M01` | Alerta se presente |
| `count_min` | `M08`, mín 1 | Alerta se abaixo |
| `count_max` | `M30`, máx 1 | Alerta se acima |
| `exact_count` | `%`, exato 2 | Alerta se diferente |

Rodam **sobre o resultado pós-substituição**. Usam matching `literal` por padrão; podem ser configuradas como `cnc_address` na declaração. Verificações **não** usam o modo `auto` — o `mode` deve ser explícito (`literal` ou `cnc_address`).

### 10.2 Verificações Estruturais Obrigatórias

Executadas em **todo** arquivo resultante, não desativáveis:

- Resultado não pode ficar vazio.
- Se o original começava com `%`, o resultado deve manter `%` inicial.
- Se o original terminava com `%`, o resultado deve manter `%` final.
- Se o original continha `M30` ou `M02`, o resultado deve conter **pelo menos um** dos dois.
- Alertar se uma regra de remoção apagou a única ocorrência de `M30`/`M02`.
- Alertar se uma regra de remoção apagou linha inteira contendo `T`, `M06`, `M30`, `M02` ou `G43`/`G44`.

Estas verificações não substituem revisão humana — reduzem riscos óbvios.

Nível de severidade:

- **Crítico (bloqueia salvar):** arquivo vazio, perda de `%`, perda total de fim de programa.
- **Atenção (não bloqueia):** linha removida contendo comando crítico (registra em log).

---

## 11. Interface e UX

### 11.1 Layout Principal

Três áreas:

- **Arquivos:** lista do lote, status de leitura, encoding (com confiança), EOL e contagem de alterações.
- **Regras:** globais do perfil e individuais por arquivo (abas ou seções).
- **Verificações:** configuráveis e estruturais, resultado por arquivo.

> **Nota de implementação (MVP v2.3):** a UI apresenta isto de forma **centrada no programa** — aba *Substituições* com a lista de programas (marcáveis) + *Trocas comuns* (valem para todos os marcados) e *Trocas só do programa selecionado* (= regras `file` da §7.1); e aba *Verificações* separada, com botão próprio "Executar verificações". Funciona com **1 ou vários** programas (não assume lote).

Padrões:

- `QSplitter` para painéis redimensionáveis.
- Persistir largura dos painéis e tamanho da janela em `~/.cnc_batch_editor/ui_state.json`.
- Banner persistente com perfil ativo.
- Indicadores: regras ativas, regras com 0 ocorrências, alertas bloqueantes.
- Destacar visualmente regras com `replace` vazio (remoção).
- Confirmação obrigatória antes de processar lote com qualquer regra de remoção.

### 11.2 Atalhos de Teclado

| Ação | Atalho |
|------|--------|
| Carregar pasta | `Ctrl+O` |
| Adicionar arquivos | `Ctrl+Shift+O` |
| Nova regra global | `Ctrl+N` |
| Executar dry-run | `F5` |
| Abrir preview | `Ctrl+P` |
| Salvar lote | `Ctrl+S` |
| Trocar perfil | `Ctrl+M` |
| Buscar em regras | `Ctrl+F` |

### 11.3 Fluxo de Uso

```text
1. Selecionar perfil de máquina
2. Carregar arquivos por drag & drop ou seleção de pasta
3. Ler arquivos e mostrar encoding/EOL/status
4. Configurar ou ajustar regras
5. Executar dry-run automático
6. Exibir contagens, alertas e regras sem ocorrência (com dica de leading-zero)
7. Abrir preview/diff obrigatório
8. Confirmar perfil, pasta de saída e regras de remoção
9. Salvar resultados em pasta separada
10. Mostrar resumo final por arquivo e oferecer exportar log .txt
```

### 11.4 Preview

- Diff lado a lado por arquivo.
- Linhas alteradas com contexto (`±3` linhas), não o arquivo inteiro.
- Indica qual regra alterou cada linha.
- Lista regras ativas com 0 ocorrências.
- Lista conflitos e matches sobrepostos com a decisão tomada (qual venceu, qual foi suprimida).
- Navegação por arquivo (lista lateral).
- Botão "Confirmar e salvar" desabilitado quando houver condição de bloqueio (§11.7).

### 11.5 Estados de Alerta

| Estado | Cor | Significado |
|--------|-----|-------------|
| Sucesso | Verde | Regra aplicada e verificação passou |
| Atenção | Amarelo | 0 ocorrências, encoding baixa confiança, verificação opcional falhou, linha crítica removida, **conflito resolvido com supressão** |
| Crítico | Vermelho | Erro de leitura, arquivo vazio, estrutura mínima quebrada (perda de `%` ou de fim de programa) |

> Conflito entre regras **não** é estado crítico: a §8.4 sempre resolve. Aparece como Atenção, com a decisão no log.

### 11.6 Log de Sessão

- Mantido em memória durante a sessão.
- Exibe: arquivos carregados, regras aplicadas, contagens, conflitos, supressões, alertas, decisões.
- Botão "Exportar log" salva `.txt` (UTF-8) ao lado da pasta de saída.
- Não persiste entre sessões.

### 11.7 Condições de Bloqueio de Salvamento

O botão "Confirmar e salvar" fica **desabilitado** enquanto qualquer uma destas for verdadeira:

1. Há **erro estrutural crítico** em pelo menos um arquivo resultante (§10.2): vazio, perda de `%`, perda total de fim de programa.
2. Há regra ativa com `on_zero_matches=error` e **0 ocorrências** no lote (§8.5).
3. **Todos** os arquivos do lote falharam na leitura (nada a salvar).

Conflitos resolvidos, regras `warn` com 0 ocorrências e alertas de Atenção **não** bloqueiam — exigem apenas a confirmação do passo 8 do fluxo (§11.3).

---

## 12. Tecnologia

### 12.1 Stack Definida

| Componente | Tecnologia | Justificativa |
|------------|------------|---------------|
| Linguagem | Python 3.11+ | Estabilidade Qt6, dataclasses, type hints |
| Interface | PySide6 / Qt6 (LGPLv3) | Tabelas, drag & drop, diff, threading nativos. Distribuição dinâmica do Qt mantém compatibilidade com a LGPL |
| Substituição | `re` + composição própria | Matching controlado e testável |
| Encoding | Detecção determinística + opcional `charset-normalizer` (MIT) | Preservação de arquivos CNC legados |
| Presets | JSON local versionado (`schema_version`), UTF-8 | Simples, editável, sem banco |
| Distribuição | PyInstaller `onedir` | Menos falso positivo, inicialização previsível |
| Tema | Qt Light + QSS | Visual claro e operacional |
| Testes | `pytest` + `pytest-qt` | Regressão do motor e file round-trip |
| Lint | `ruff` + `mypy --strict` no `core/` | Garante invariantes do motor |

> **Nota de licença:** PySide6 é LGPLv3. Distribuir via `onedir` com o Qt em bibliotecas dinâmicas mantém o uso comercial dentro da LGPL sem exigir abertura do código da aplicação. Evitar linkagem estática do Qt.

### 12.2 Estrutura de Projeto

```text
cnc_batch_editor/
├── main.py
├── ui/
│   ├── main_window.py
│   ├── preview_dialog.py
│   ├── rule_table.py
│   ├── file_list.py
│   ├── verification_panel.py
│   └── styles.qss
├── core/
│   ├── models.py
│   ├── matcher.py
│   ├── replacement_plan.py
│   ├── replacer.py
│   ├── verifier.py
│   ├── file_handler.py
│   ├── preset_store.py
│   └── session_log.py
├── data/
│   └── presets/
│       ├── MAZAK_VTC530.json
│       └── ROMI_G360.json
├── tests/
│   ├── test_matcher.py
│   ├── test_replacement_plan.py
│   ├── test_replacer.py
│   ├── test_verifier.py
│   ├── test_file_roundtrip.py
│   ├── test_preset_store.py
│   └── fixtures/
└── build/
    └── FlowNC/
```

### 12.3 Responsabilidades

| Módulo | Responsabilidade |
|--------|------------------|
| `models.py` | Dataclasses tipadas para regras, presets, planos e resultados |
| `matcher.py` | Construção segura de padrões, heurística `auto`, localização de matches |
| `replacement_plan.py` | Planejar alterações contra o original, detectar conflitos, aplicar §8.4 |
| `replacer.py` | Compor o resultado final sem cascata |
| `verifier.py` | Verificações configuráveis e estruturais |
| `file_handler.py` | Leitura/escrita binária, encoding, BOM, EOL, atomic write |
| `preset_store.py` | CRUD, validação, migração e backup de presets |
| `session_log.py` | Log estruturado em memória, exportável como texto |

### 12.4 Funções Puras no Core

`matcher`, `replacement_plan`, `replacer` e `verifier` devem ser **funções puras** (entrada → saída, sem I/O nem estado global). Facilita teste e elimina race conditions com a UI.

---

## 13. Presets JSON

### 13.1 Schema Inicial (v1)

```json
{
  "schema_version": 1,
  "machine": "MAZAK_VTC530",
  "description": "Centro de usinagem principal",
  "extensions": [".nc", ".txt", ".iso"],
  "case_sensitive": false,
  "global_rules": [
    {
      "id": "rule_m08_to_m07",
      "active": true,
      "scope": "global",
      "find": "M08",
      "replace": "M07",
      "mode": "auto",
      "comment": "Névoa no lugar de fluido",
      "on_zero_matches": "warn",
      "priority": 100
    }
  ],
  "file_rules": [
    {
      "id": "rule_peca01_t1_to_t21",
      "active": true,
      "scope": "file",
      "file": "PECA01.nc",
      "find": "T1",
      "replace": "T21",
      "mode": "auto",
      "comment": "Fresa Ø12 posição 21",
      "on_zero_matches": "warn",
      "priority": 100
    }
  ],
  "verifications": [
    {
      "id": "verify_m30",
      "type": "must_exist",
      "find": "M30",
      "mode": "literal",
      "label": "Fim de programa"
    },
    {
      "id": "verify_m01_absent",
      "type": "must_not_exist",
      "find": "M01",
      "mode": "literal",
      "label": "Parada opcional removida"
    }
  ]
}
```

> **Nota sobre `case_sensitive`:** quando `false`, o matching ignora caixa no `find` (ex.: `t1` casa `T1`), mas o `replace` é gravado **literalmente como digitado** — não há preservação de caixa do texto original.

### 13.2 CRUD e Versionamento

- Criar, duplicar, renomear, salvar e excluir perfil (exclusão com confirmação).
- Validar JSON ao carregar (`pydantic` ou validação manual estrita).
- **Backup automático antes de salvar:** copiar arquivo atual para `data/presets/.backup/NOME_YYYYMMDD_HHMMSS.json`. Retenção: 10 backups por perfil; mais antigos são apagados.
- `schema_version` obrigatório. Versão futura > 1 dispara função de migração explícita; ausência aborta carregamento com mensagem clara.
- Perfis com schema desconhecido são listados como "incompatíveis" e não carregam.

---

## 14. Critérios de Aceitação (Definition of Done)

Cada critério deve ter teste automatizado correspondente em §15 (ver Anexo C).

| # | Critério | Prioridade | Teste |
|---|----------|------------|-------|
| 1 | Carregar arquivos por drag & drop ou seleção de pasta | Alta | manual + smoke |
| 2 | Filtrar extensões configuráveis por perfil | Alta | unit |
| 3 | Ignorar pastas `_processado_*` ao carregar pasta | Alta | unit |
| 4 | Mostrar encoding (com confiança), EOL e status por arquivo | Alta | unit |
| 5 | CRUD completo de presets com backup automático | Alta | unit |
| 6 | Ativar/desativar regras globais por linha | Alta | manual |
| 7 | Criar regras individuais por arquivo | Alta | manual |
| 8 | Regra individual suprimir global conflitante no mesmo arquivo | Alta | unit `TV-PLAN-02` |
| 9 | Substituir `T1` sem afetar `T10`, `T100` ou `T1.5` | Alta | unit `TV-CNC-05/06`, `TV-CNC-09` |
| 10 | Substituir `T1` em `M6T1`, `G43H1T1` e `Z20.T1` | Alta | unit `TV-CNC-02/03/04` |
| 11 | Não corromper decimal como `F1.5` ao buscar `F1` | Alta | unit `TV-CNC-09` |
| 12 | Escapar metacaracteres em texto livre com `re.escape` | Alta | unit `TV-LIT-01` |
| 13 | Evitar cascata entre regras `G54→G55` e `G55→G56` | Alta | unit `TV-PLAN-01` |
| 14 | Alertar regra ativa com 0 ocorrências (com dica leading-zero) | Alta | unit |
| 15 | Detectar conflito ou sobreposição entre matches | Alta | unit |
| 16 | Exibir dry-run com contagem por regra e arquivo | Alta | manual |
| 17 | Exibir preview/diff obrigatório antes de salvar | Alta | manual |
| 18 | Bloquear salvar conforme §11.7 | Alta | unit `TV-STR-*` |
| 19 | Salvar em pasta separada com perfil e timestamp | Alta | unit `TV-RT-07/08` |
| 20 | Preservar encoding, BOM e EOL | Alta | unit `TV-RT-01..06` |
| 21 | Escrita atômica (sem arquivo parcial em falha) | Alta | unit `TV-RT-09` |
| 22 | Nunca alterar arquivos originais | Alta | unit |
| 23 | Verificações configuráveis rodam sobre o resultado final | Média | unit |
| 24 | Heurística do modo `auto` conforme §7.3.1 | Alta | unit |
| 25 | Resolução de conflito conforme §8.4 | Alta | unit `TV-PLAN-02/03` |
| 26 | Log de sessão exportável como `.txt` | Média | manual |
| 27 | EXE portátil via PyInstaller `onedir` que abre em Win10/11 limpos | Alta | manual |
| 28 | Processamento não congelar UI em lotes grandes (§6.1) | Média | manual |
| 29 | Coluna de comentário nas regras | Baixa | manual |
| 30 | Atalhos de teclado §11.2 funcionam | Baixa | manual |
| 31 | Editor de regra rejeita quebra de linha em `find`/`replace` | Média | unit |

---

## 15. Vetores de Teste Obrigatórios

Cada vetor tem ID estável. Os IDs são a referência canônica (não usar números de linha).

### 15.1 Matching CNC (modo `cnc_address`)

| ID | Regra | Entrada | Saída esperada |
|----|-------|---------|----------------|
| `TV-CNC-01` | `T1→T21` | `T1 M6` | `T21 M6` |
| `TV-CNC-02` | `T1→T21` | `M6T1` | `M6T21` |
| `TV-CNC-03` | `T1→T21` | `G43H1T1` | `G43H1T21` |
| `TV-CNC-04` | `T1→T21` | `Z20.T1` | `Z20.T21` |
| `TV-CNC-05` | `T1→T21` | `T10 M6` | sem alteração |
| `TV-CNC-06` | `T1→T21` | `T100 M6` | sem alteração |
| `TV-CNC-07` | `T1→T21` | `(T1 USADO)` | `(T21 USADO)` — **casa**; MVP altera comentários (§3.3) |
| `TV-CNC-08` | `T1→T21` | `(OFFSET1)` | sem alteração — `T1` colado em letra |
| `TV-CNC-09` | `F1→F2` | `F1.5` | sem alteração |
| `TV-CNC-10` | `G54→G55` | `G54.1 P1` | sem alteração — código estendido diferente |
| `TV-CNC-11` | `M8→M7` | `M08` | sem alteração + alerta 0 ocorrências + dica leading-zero |
| `TV-CNC-12` | `M08→M07` | `M08` | `M07` |
| `TV-CNC-13` | `G54→G55` | `G54G90` | `G55G90` |
| `TV-CNC-14` | `S3000→S4000` | `S30000` | sem alteração — não casa dentro de número maior |

### 15.2 Texto Literal (modo `literal`)

| ID | Regra | Entrada | Saída esperada |
|----|-------|---------|----------------|
| `TV-LIT-01` | `(FRESA Ø12)→(FRESA Ø10)` | `(FRESA Ø12)` | `(FRESA Ø10)` |
| `TV-LIT-02` | `X1.5→X2.5` | `X1.5` | `X2.5` |
| `TV-LIT-03` | `S3000 M03→` (vazio) | `N10 S3000 M03 T1` | `N10  T1` (dois espaços preservados — ver §8.6) |

### 15.3 Plano de Substituição e Conflitos

| ID | Regras | Entrada | Saída esperada |
|----|--------|---------|----------------|
| `TV-PLAN-01` | `G54→G55`, `G55→G56` (ambas globais) | `G54 G55` | `G55 G56` (sem cascata) |
| `TV-PLAN-02` | Global `T1→T21` + File `T1→T15` no mesmo arquivo | `T1 M6` | `T15 M6` + log de supressão da global |
| `TV-PLAN-03` | Duas globais `T1→T21` e `T1→T15` (mesma prioridade) | `T1 M6` | `T21 M6` (primeira declarada vence) + alerta de conflito (amarelo) |

### 15.4 Round-Trip de Arquivo

| ID | Caso | Requisito |
|----|------|-----------|
| `TV-RT-01` | UTF-8 com BOM | Preservar BOM na saída |
| `TV-RT-02` | UTF-8 sem BOM | Não adicionar BOM |
| `TV-RT-03` | CP1252 com `Ø` em comentário | Não corromper caractere |
| `TV-RT-04` | UTF-16 LE com BOM | Preservar encoding e BOM |
| `TV-RT-05` | CRLF | Preservar CRLF |
| `TV-RT-06` | LF | Preservar LF |
| `TV-RT-07` | Arquivo sem regras casando | Saída byte-a-byte igual ao original quando solicitado salvar |
| `TV-RT-08` | Pasta de saída já existe | Sufixo `_02`, `_03` … |
| `TV-RT-09` | Falha simulada no meio da escrita | Nenhum `.tmp` permanece; mensagem de erro clara |

### 15.5 Verificações Estruturais

| ID | Caso | Resultado esperado |
|----|------|--------------------|
| `TV-STR-01` | Original tem `%` início e fim; substituição preserva | OK |
| `TV-STR-02` | Regra remove `%` final | Bloqueio crítico vermelho |
| `TV-STR-03` | Original tem `M30`; regra remove `M30` | Bloqueio crítico vermelho |
| `TV-STR-04` | Original tem `M02`; regra remove `M02` | Bloqueio crítico vermelho |
| `TV-STR-05` | Regra remove linha contendo `M06` | Alerta amarelo, não bloqueia |
| `TV-STR-06` | Resultado ficaria vazio | Bloqueio crítico vermelho |

---

## 16. Riscos e Mitigações

| Risco | Prob. | Impacto | Mitigação |
|-------|-------|---------|-----------|
| Substituição ambígua (falso positivo) | Alta | Alto | Lookahead do boundary §8.2 + vetores `TV-CNC-05/06/09/10/14` |
| Substituição não aplicada (falso negativo) | Alta | Alto | Lookbehind correto §8.2 + vetores `TV-CNC-02/03/04` + alerta de 0 ocorrências §8.5 |
| Regra sem efeito | Alta | Alto | Alerta obrigatório para 0 ocorrências + dica leading-zero §8.5 |
| Cascata inesperada | Média | Alto | Plano de substituição contra original §8.3 |
| Encoding incorreto | Média | Alto | Leitura binária + preservação §9 + nível de confiança |
| Perfil errado aplicado | Média | Alto | Banner persistente + confirmação antes de salvar + perfil no nome da pasta |
| Remoção acidental | Média | Alto | Destaque visual + confirmação de regras com `replace` vazio |
| Comentário alterado sem intenção | Baixa | Baixo | Documentado (§3.3); visível no preview; máquina ignora comentário |
| Regra de arquivo aplicada a homônimo errado | Baixa | Médio | Alerta de duplicidade de basename §9.3; recomendar nomes únicos |
| Arquivo parcial | Baixa | Alto | Escrita atômica + `fsync` |
| Auto-reprocessar saída anterior | Média | Médio | Ignorar `_processado_*` |
| UI congelar em arquivo grande | Média | Médio | `QThread` + orçamento §6.1 + preview por trecho |
| Antivírus bloquear EXE | Média | Médio | `onedir` + documentar fingerprint |
| Falha no meio do lote | Baixa | Médio | Erro por arquivo + resumo final |
| Preset corrompido | Baixa | Médio | Validação + backup automático §13.2 |
| Schema futuro incompatível | Baixa | Médio | `schema_version` obrigatório §13.2 |

---

## 17. Boas Práticas de Desenvolvimento

- Separar domínio (`core`) da interface (`ui`); core não importa Qt.
- Cobrir motor de substituição com testes **antes** da UI (TDD no core).
- Dataclasses tipadas + `mypy --strict` no `core/`.
- Validar presets ao carregar com mensagem clara.
- Não misturar I/O com lógica de substituição.
- Nunca bloquear thread principal da UI.
- Tratar erros por arquivo e consolidar no resumo final.
- Logs em memória durante o lote; exportação opcional como `.txt`.
- Evitar dependências desnecessárias.
- Não executar comandos externos sobre arquivos CNC.
- **Zero rede:** nenhum import de `requests`, `urllib`, `socket` no projeto final (verificável por teste de import que falha o build se encontrar).
- Funções puras no core.
- Commits pequenos e atômicos; cada feature com teste antes do merge.

---

## 18. Referências Técnicas

| Fonte | URL | Relevância |
|-------|-----|------------|
| CIMCO Edit V8 User Guide | https://www.cimco.com/documentation/documents/cimco_edit/user_guides/en/cimco-edit-8-user-guide-en.pdf | UX de edição CNC |
| Predator CNC Editor | https://www.predator-software.com/predator_cnc_editor_software.htm | Referência operacional |
| PySide6 Docs | https://doc.qt.io/qtforpython-6/ | Widgets, threading |
| Python `re` Docs | https://docs.python.org/3/library/re.html | Matching e escaping |
| PyInstaller Docs | https://pyinstaller.org | Distribuição desktop |
| charset-normalizer | https://pypi.org/project/charset-normalizer/ | Detecção auxiliar de encoding |
| ISO 6983 (G-code) | (norma) | Estrutura de programa CNC |
| Fanuc Programming Manual | (referência interna do usuário) | Dialeto CNC primário |

---

## 19. Roadmap de Execução

Ordem **obrigatória**. Cada fase tem entregável testável antes de avançar.

### Fase 1 — Núcleo de Matching e Plano (sem UI)
**Entregáveis:** `models.py`, `matcher.py`, `replacement_plan.py`, `replacer.py`, vetores `TV-CNC-*`, `TV-LIT-*`, `TV-PLAN-*`.
**DoD:** todos os vetores §15.1–§15.3 passam; cobertura ≥ 90% no core; `mypy --strict` limpo.

### Fase 2 — File Handling e Verificações
**Entregáveis:** `file_handler.py`, `verifier.py`, vetores `TV-RT-*` e `TV-STR-*`.
**DoD:** round-trip de todos os encodings/EOL preservado; verificações estruturais bloqueiam o que devem bloquear.

### Fase 3 — Preset Store
**Entregáveis:** `preset_store.py`, validação, backup, migração, 2 presets de exemplo.
**DoD:** CRUD completo; backup retém 10 versões; schema inválido rejeitado com mensagem.

### Fase 4 — UI Esqueleto
**Entregáveis:** `main_window.py`, layout §11.1, drag & drop, lista de arquivos com status, banner de perfil.
**DoD:** carrega lote, mostra encoding/EOL, persiste tamanho de painéis.

### Fase 5 — UI de Regras
**Entregáveis:** `rule_table.py`, edição de regras globais e por arquivo, ativação, comentário, rejeição de quebra de linha.
**DoD:** CRUD de regras refletindo no preset em memória; atalhos §11.2.

### Fase 6 — Dry-Run, Preview e Verificações na UI
**Entregáveis:** `preview_dialog.py`, `verification_panel.py`, contagens, diff com âncora de regra, dica leading-zero.
**DoD:** preview obrigatório; bloqueia salvar conforme §11.7; mostra supressões e conflitos.

### Fase 7 — Salvamento e Log
**Entregáveis:** integração de `file_handler` com UI, pasta de saída, log de sessão, exportar `.txt`.
**DoD:** lote completo do drag & drop ao log exportado funciona em PC limpo.

### Fase 8 — Threading e Performance
**Entregáveis:** `QThread` para leitura/dry-run/salvamento, progress bar.
**DoD:** orçamento §6.1 cumprido; UI nunca congela em lote de 50 arquivos.

### Fase 9 — Empacotamento
**Entregáveis:** build `onedir`, ícone, smoke test em Win10 e Win11 limpos.
**DoD:** EXE abre em < 3 s, sem dependência externa, sem aviso de AV no Windows Defender padrão.

### Fase 10 — Hardening
**Entregáveis:** testes manuais com arquivos reais do usuário, ajustes de UX, documentação curta no `README.md`.
**DoD:** critérios §14 todos verde; usuário valida lote real.

---

## 20. Veredito

O MVP é viável e recomendado, **desde que tratado como editor de substituições textuais seguro**, não como validador CNC completo.

A ordem das fases §19 reduz o risco principal do produto: gerar um arquivo aparentemente correto, mas semanticamente perigoso para máquina. O motor de matching (§8.2) é o componente de maior risco e deve ser fechado por teste antes de qualquer UI.

Este documento é a baseline. Mudanças significativas exigem atualização da seção afetada **antes** do código, com entrada correspondente no Changelog.

---

## Anexo A — Glossário

| Termo | Definição |
|-------|-----------|
| **Programa CNC** | Arquivo de texto com instruções de usinagem |
| **G-code** | Linguagem de programação CNC, padronizada por ISO 6983 |
| **Endereço CNC** | Letra seguida de número (`T1`, `M08`, `G54`) |
| **Offset de origem** | `G54`–`G59`, zero-peça |
| **Boundary CNC** | Regra de fronteira que impede casar `T1` em `T10` e permite casar em `M6T1` |
| **Lookbehind / Lookahead** | Asserções de regex que testam o caractere anterior/seguinte sem consumi-lo |
| **Leading-zero** | Zero à esquerda em endereço (`M08` vs `M8`, `T01` vs `T1`) |
| **Cascata** | Aplicar regra 2 sobre o resultado da regra 1; comportamento proibido §8.3 |
| **Dry-run** | Simulação sem gravar arquivo |
| **Atomic write** | Escrita via temp + rename, garante "tudo ou nada" |
| **BOM** | Byte Order Mark, marcador de encoding |
| **EOL** | End of Line: `CRLF`, `LF` ou `CR` |
| **Basename** | Nome do arquivo sem o caminho da pasta (ex.: `PECA01.nc`) |
| **Preset / Perfil** | Conjunto de regras + verificações para uma máquina |
| **Lote** | Conjunto de arquivos processados em uma operação |

## Anexo B — Política de Privacidade e Rede

- Aplicação é **100% offline**.
- Nenhum import de bibliotecas de rede no código de produção (verificável por teste).
- Nenhuma telemetria.
- Nenhum log enviado externamente.
- Atualizações do EXE são manuais (substituir a pasta).

## Anexo C — Matriz de Rastreabilidade

Critério §14 → Especificação → Vetor §15:

| Critério | Especificação | Vetor(es) |
|----------|---------------|-----------|
| C8 | §8.4 | `TV-PLAN-02` |
| C9 | §8.2 | `TV-CNC-05`, `TV-CNC-06`, `TV-CNC-09` |
| C10 | §8.2 | `TV-CNC-02`, `TV-CNC-03`, `TV-CNC-04` |
| C11 | §8.2 | `TV-CNC-09` |
| C12 | §7.3, §8.1 | `TV-LIT-01` |
| C13 | §8.3 | `TV-PLAN-01` |
| C18 | §10.2, §11.7 | `TV-STR-02`, `TV-STR-03`, `TV-STR-04`, `TV-STR-06` |
| C19 | §9.2 | `TV-RT-07`, `TV-RT-08` |
| C20 | §9.1, §9.2 | `TV-RT-01`..`TV-RT-06` |
| C21 | §9.2 | `TV-RT-09` |
| C22 | §9 | `TV-RT-07` (original intacto) |
| C24 | §7.3.1 | `TV-CNC-*` + `TV-LIT-*` (heurística) |
| C25 | §8.4 | `TV-PLAN-02`, `TV-PLAN-03` |

Cada critério restante mapeia para teste manual ou de UI documentado durante a Fase correspondente.
