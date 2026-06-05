# PRD v2.2 — CNC Batch Editor
## Editor Seguro de Substituições em Lote para Programas CNC

**Versão:** 2.2 — versão final, baseline de desenvolvimento
**Data:** 2026-05-29
**Autor / Owner:** Rafael Eleotério
**Status:** Aprovado para execução
**Uso:** Individual — operador/programador CNC
**Plataforma:** Windows Desktop — EXE portátil (`onedir`), sem instalação formal
**Idioma da aplicação:** Português (Brasil)
**Princípio central:** nunca alterar arquivos originais; toda alteração deve ser previsível, auditável em preview e gravada com preservação máxima do arquivo CNC.

---

## 0. Como Ler Este Documento

Este PRD é a **fonte única de verdade** para o desenvolvimento do MVP. Todo plano de execução, sprint, task e prompt de implementação deve referenciar seções deste documento por número (ex.: "implementar §8.2"). Decisões que divergirem deste PRD exigem atualização aqui antes do código.

- Seções §1–§6: contexto e escopo (read-only para devs).
- Seções §7–§13: especificação técnica de **o que** construir.
- Seções §14–§15: critérios verificáveis (Definition of Done).
- Seções §16–§19: riscos, padrões e roadmap de execução.
- Anexos A–C: glossário, schema JSON e matriz de rastreabilidade.

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
| Arquivos originais alterados acidentalmente | 0 |
| Lote concluído sem revisão de preview | Impossível por design |
| Taxa de regressão entre releases (testes §15) | 100% verde antes de gerar EXE |

---

## 3. Escopo do MVP

### 3.1 Dentro do Escopo

- Substituição textual em lote com múltiplos arquivos e múltiplas regras.
- Matching seguro para códigos CNC comuns (`T`, `H`, `D`, `G`, `M`, `S`, `F`) quando a regra tiver formato de endereço CNC.
- Substituição literal segura para textos livres, comentários e comandos compostos.
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
- **Inserção de comandos:** o MVP insere texto apenas por âncora textual (ex.: `M30` → `M00\nM30`). Não há "inserir após a linha 120" sem âncora.
- **Múltiplas peças na mesa:** replicar blocos para `G55`, `G56` etc. exige cópia e transformação de regiões. Fora do MVP.
- **T duplicado:** o MVP pode contar ocorrências e alertar duplicidade simples, mas não interpreta se a duplicidade é correta dentro da estratégia do programa.

---

## 4. Tipos de Alteração Suportados

| # | Categoria | Suporte no MVP | Observação |
|---|-----------|----------------|------------|
| 1 | Troca de ferramenta | Parcial | Substitui `T`, `H`, `D`; recomenda grupo vinculado |
| 2 | Ajuste de offset de origem | Sim | Ex.: `G54` → `G55` |
| 3 | Ajuste de rotação spindle | Sim | Ex.: `S2500` → `S3000` |
| 4 | Ajuste de avanço | Sim | Ex.: `F150` → `F300` |
| 5 | Controle de fluido/ar | Sim | Ex.: `M08` → `M07`, remover `M09` |
| 6 | Alturas de segurança | Sim | Ex.: `Z20.` → `Z50.` como texto literal |
| 7 | Inserção/remoção de comandos | Parcial | Inserção somente por âncora textual |
| 8 | Rotação/espelhamento textual | Parcial | Ex.: `R90` → `R180`; sem validar geometria |
| 9 | Múltiplas peças na mesa | Fora do MVP | Exige replicação de blocos |
| 10 | Verificação de consistência | Parcial | Presença, ausência, contagem e estrutura mínima |

> **Nota técnica:** o sistema não interpreta lógica CNC completa. Executa substituições textuais controladas, com matching seguro, preview obrigatório e validações de saída.

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
| `find` | Sim | string | Texto literal a localizar |
| `replace` | Sim | string | Novo texto; string vazia significa remoção |
| `mode` | Sim | enum | `auto`, `literal` ou `cnc_address` |
| `comment` | Não | string | Anotação livre |
| `on_zero_matches` | Sim | enum | `warn` (padrão), `ignore`, `error` |
| `priority` | Não | int | Desempate entre regras em conflito; menor vence; default 100 |

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
- Evitar casar `T1` dentro de `T10`, `T100` ou `T1.5`.
- Permitir casar `T1` em blocos concatenados como `M6T1` e `G43H1`.
- Case-sensitive por padrão; case-insensitive opcional via flag `case_sensitive: false` no preset.
- Aplicar regras contra o **conteúdo original** em uma etapa planejada, sem cascata.
- Detectar sobreposição entre matches e marcar conflito antes de salvar.

### 8.2 Boundary CNC

Para `cnc_address`, o padrão é:

```python
pattern = rf"(?<![A-Z0-9.]){re.escape(find)}(?![0-9.])"
```

- Lookbehind `(?<![A-Z0-9.])` impede casar dentro de `XT1`, `9T1` ou `.T1` (raros, mas possíveis em comentários).
- Lookahead `(?![0-9.])` impede `T1` casar em `T10`, `T100`, `T1.5`.

Exemplos esperados:

| Regra | Texto | Casa? | Motivo |
|-------|-------|-------|--------|
| `T1` | `T1 M6` | Sim | Código isolado |
| `T1` | `M6T1` | Sim | Bloco concatenado real |
| `T1` | `G43H1T1` | Sim | Após dígito de outro endereço |
| `T1` | `T10` | Não | Evita troca destrutiva |
| `T1` | `T100` | Não | Evita troca destrutiva |
| `F1` | `F1.5` | Não | Evita corromper decimal |
| `M8` | `M08` | Não | Formato diferente; alerta 0 ocorrências |

> **Nota:** o caso "após dígito" (`G43H1T1`) é permitido porque o lookbehind testa o caractere imediatamente antes do `find`. O `1` antes pertence ao endereço anterior (`H1`), não ao endereço atual. Vetor §15.1 cobre isto.

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

Ordem de desempate:

1. **Regra de arquivo** vence regra global com mesmo `find` no escopo daquele arquivo (regra global suprimida, registrada no log).
2. Caso ainda haja conflito: `priority` menor vence.
3. Caso `priority` igual: regra declarada primeiro vence (ordem do JSON).
4. Sempre exibir no preview: qual regra venceu, qual foi suprimida e por quê.

### 8.5 Regras Sem Ocorrência

Regra ativa com 0 matches no lote inteiro:

- `on_zero_matches=warn` (padrão): alerta amarelo, não bloqueia salvar.
- `on_zero_matches=ignore`: silencia (útil para regra opcional que só se aplica a alguns arquivos).
- `on_zero_matches=error`: bloqueia salvar até desativar ou ajustar.

Contagem é **por lote**, não por arquivo, salvo se for `scope=file` (aí é por arquivo específico).

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
- Alertar duplicidade de nomes vindos de pastas diferentes.
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

Rodam **sobre o resultado pós-substituição**. Usam matching `literal` por padrão; podem ser configuradas como `cnc_address` na declaração.

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
6. Exibir contagens, alertas e regras sem ocorrência
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
- Lista conflitos e matches sobrepostos com decisão tomada.
- Navegação por arquivo (lista lateral).
- Botão "Confirmar e salvar" desabilitado se houver erro estrutural crítico.

### 11.5 Estados de Alerta

| Estado | Cor | Significado |
|--------|-----|-------------|
| Sucesso | Verde | Regra aplicada e verificação passou |
| Atenção | Amarelo | 0 ocorrências, encoding baixa confiança, verificação opcional falhou, linha crítica removida |
| Crítico | Vermelho | Erro de leitura, conflito sem resolução, arquivo vazio, estrutura mínima quebrada |

### 11.6 Log de Sessão

- Mantido em memória durante a sessão.
- Exibe: arquivos carregados, regras aplicadas, contagens, conflitos, supressões, alertas, decisões.
- Botão "Exportar log" salva `.txt` ao lado da pasta de saída.
- Não persiste entre sessões.

---

## 12. Tecnologia

### 12.1 Stack Definida

| Componente | Tecnologia | Justificativa |
|------------|------------|---------------|
| Linguagem | Python 3.11+ | Estabilidade Qt6, dataclasses, type hints |
| Interface | PySide6 / Qt6 | Tabelas, drag & drop, diff, threading nativos |
| Substituição | `re` + composição própria | Matching controlado e testável |
| Encoding | Detecção determinística + opcional `charset-normalizer` | Preservação de arquivos CNC legados |
| Presets | JSON local versionado (`schema_version`) | Simples, editável, sem banco |
| Distribuição | PyInstaller `onedir` | Menos falso positivo, inicialização previsível |
| Tema | Qt Light + QSS | Visual claro e operacional |
| Testes | `pytest` + `pytest-qt` | Regressão do motor e file round-trip |
| Lint | `ruff` + `mypy --strict` no `core/` | Garante invariantes do motor |

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
    └── CNC_BatchEditor/
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
| 8 | Regra individual suprimir global conflitante no mesmo arquivo | Alta | unit §15.3 |
| 9 | Substituir `T1` sem afetar `T10`, `T100` ou `T1.5` | Alta | unit §15.1 |
| 10 | Substituir `T1` em `M6T1` e `G43H1T1` | Alta | unit §15.1 |
| 11 | Não corromper decimal como `F1.5` ao buscar `F1` | Alta | unit §15.1 |
| 12 | Escapar metacaracteres em texto livre com `re.escape` | Alta | unit §15.2 |
| 13 | Evitar cascata entre regras `G54→G55` e `G55→G56` | Alta | unit §15.3 |
| 14 | Alertar regra ativa com 0 ocorrências | Alta | unit |
| 15 | Detectar conflito ou sobreposição entre matches | Alta | unit |
| 16 | Exibir dry-run com contagem por regra e arquivo | Alta | manual |
| 17 | Exibir preview/diff obrigatório antes de salvar | Alta | manual |
| 18 | Bloquear salvar se houver erro estrutural crítico | Alta | unit §10.2 |
| 19 | Salvar em pasta separada com perfil e timestamp | Alta | unit §15.4 |
| 20 | Preservar encoding, BOM e EOL | Alta | unit §15.4 |
| 21 | Escrita atômica (sem arquivo parcial em falha) | Alta | unit |
| 22 | Nunca alterar arquivos originais | Alta | unit |
| 23 | Verificações configuráveis rodam sobre o resultado final | Média | unit |
| 24 | Heurística do modo `auto` conforme §7.3.1 | Alta | unit |
| 25 | Resolução de conflito conforme §8.4 | Alta | unit |
| 26 | Log de sessão exportável como `.txt` | Média | manual |
| 27 | EXE portátil via PyInstaller `onedir` que abre em Win10/11 limpos | Alta | manual |
| 28 | Processamento não congelar UI em lotes grandes (§6.1) | Média | manual |
| 29 | Coluna de comentário nas regras | Baixa | manual |
| 30 | Atalhos de teclado §11.2 funcionam | Baixa | manual |

---

## 15. Vetores de Teste Obrigatórios

### 15.1 Matching CNC (modo `cnc_address`)

| Regra | Entrada | Saída esperada |
|-------|---------|----------------|
| `T1→T21` | `T1 M6` | `T21 M6` |
| `T1→T21` | `M6T1` | `M6T21` |
| `T1→T21` | `G43H1T1` | `G43H1T21` |
| `T1→T21` | `T10 M6` | sem alteração |
| `T1→T21` | `T100 M6` | sem alteração |
| `F1→F2` | `F1.5` | sem alteração |
| `M8→M7` | `M08` | sem alteração + alerta 0 ocorrências |
| `M08→M07` | `M08` | `M07` |
| `G54→G55` | `G54G90` | `G55G90` |
| `T1→T21` | `(T1 USADO)` | sem alteração (comentário em parênteses não casa por estar isolado por texto) — **rever**: na prática casa, pois `(` não é dígito nem letra. Documentar comportamento esperado: **casa**. |

### 15.2 Texto Literal (modo `literal`)

| Regra | Entrada | Saída esperada |
|-------|---------|----------------|
| `(FRESA Ø12)→(FRESA Ø10)` | `(FRESA Ø12)` | `(FRESA Ø10)` |
| `X1.5→X2.5` | `X1.5` | `X2.5` |
| `S3000 M03→` (vazio) | `N10 S3000 M03 T1` | `N10  T1` (dois espaços preservados — ver §8.6) |

### 15.3 Plano de Substituição e Conflitos

| Regras | Entrada | Saída esperada |
|--------|---------|----------------|
| `G54→G55`, `G55→G56` (ambas globais) | `G54 G55` | `G55 G56` (sem cascata) |
| Global `T1→T21` + File `T1→T15` no mesmo arquivo | `T1 M6` | `T15 M6` + log de supressão da global |
| Duas globais `T1→T21` e `T1→T15` (mesma prioridade) | `T1 M6` | Primeira declarada vence; alerta de conflito |

### 15.4 Round-Trip de Arquivo

| Caso | Requisito |
|------|-----------|
| UTF-8 com BOM | Preservar BOM na saída |
| UTF-8 sem BOM | Não adicionar BOM |
| CP1252 com `Ø` em comentário | Não corromper caractere |
| UTF-16 LE com BOM | Preservar encoding e BOM |
| CRLF | Preservar CRLF |
| LF | Preservar LF |
| Arquivo sem regras casando | Saída byte-a-byte igual ao original quando solicitado salvar |
| Pasta de saída já existe | Sufixo `_02`, `_03` … |
| Falha simulada no meio da escrita | Nenhum `.tmp` permanece; mensagem de erro clara |

### 15.5 Verificações Estruturais

| Caso | Resultado esperado |
|------|--------------------|
| Original tem `%` início e fim; substituição preserva | OK |
| Regra remove `%` final | Bloqueio crítico vermelho |
| Original tem `M30`; regra remove `M30` | Bloqueio crítico vermelho |
| Original tem `M02`; regra remove `M02` | Bloqueio crítico vermelho |
| Regra remove linha contendo `M06` | Alerta amarelo, não bloqueia |

---

## 16. Riscos e Mitigações

| Risco | Prob. | Impacto | Mitigação |
|-------|-------|---------|-----------|
| Substituição ambígua | Alta | Alto | Boundary CNC §8.2 + vetores §15.1 |
| Regra sem efeito | Alta | Alto | Alerta obrigatório para 0 ocorrências §8.5 |
| Cascata inesperada | Média | Alto | Plano de substituição contra original §8.3 |
| Encoding incorreto | Média | Alto | Leitura binária + preservação §9 + nível de confiança |
| Perfil errado aplicado | Média | Alto | Banner persistente + confirmação antes de salvar |
| Remoção acidental | Média | Alto | Destaque visual + confirmação de regras com `replace` vazio |
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
- **Zero rede:** nenhum import de `requests`, `urllib`, `socket` no projeto final.
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
| Fanuc Programming Manual | (referência interna do usuário) | Dialeto CNC primário |

---

## 19. Roadmap de Execução

Ordem **obrigatória**. Cada fase tem entregável testável antes de avançar.

### Fase 1 — Núcleo de Matching e Plano (sem UI)
**Entregáveis:** `models.py`, `matcher.py`, `replacement_plan.py`, `replacer.py`, testes §15.1, §15.2, §15.3.
**DoD:** todos os vetores §15.1–§15.3 passam; cobertura ≥ 90% no core; `mypy --strict` limpo.

### Fase 2 — File Handling e Verificações
**Entregáveis:** `file_handler.py`, `verifier.py`, testes §15.4 e §15.5.
**DoD:** round-trip de todos os encodings/EOL preservado; verificações estruturais bloqueiam o que devem bloquear.

### Fase 3 — Preset Store
**Entregáveis:** `preset_store.py`, validação, backup, migração, 2 presets de exemplo.
**DoD:** CRUD completo; backup retém 10 versões; schema inválido rejeitado com mensagem.

### Fase 4 — UI Esqueleto
**Entregáveis:** `main_window.py`, layout §11.1, drag & drop, lista de arquivos com status, banner de perfil.
**DoD:** carrega lote, mostra encoding/EOL, persiste tamanho de painéis.

### Fase 5 — UI de Regras
**Entregáveis:** `rule_table.py`, edição de regras globais e por arquivo, ativação, comentário.
**DoD:** CRUD de regras refletindo no preset em memória; atalhos §11.2.

### Fase 6 — Dry-Run, Preview e Verificações na UI
**Entregáveis:** `preview_dialog.py`, `verification_panel.py`, contagens, diff com âncora de regra.
**DoD:** preview obrigatório; bloqueia salvar em erro crítico; mostra supressões e conflitos.

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

A ordem das fases §19 reduz o risco principal do produto: gerar um arquivo aparentemente correto, mas semanticamente perigoso para máquina.

Este documento é a baseline. Mudanças significativas exigem atualização da seção afetada **antes** do código.

---

## Anexo A — Glossário

| Termo | Definição |
|-------|-----------|
| **Programa CNC** | Arquivo de texto com instruções de usinagem |
| **G-code** | Linguagem de programação CNC, padronizada por ISO 6983 |
| **Endereço CNC** | Letra seguida de número (`T1`, `M08`, `G54`) |
| **Offset de origem** | `G54`–`G59`, zero-peça |
| **Boundary CNC** | Regra de fronteira que impede casar `T1` em `T10` |
| **Cascata** | Aplicar regra 2 sobre o resultado da regra 1; comportamento proibido §8.3 |
| **Dry-run** | Simulação sem gravar arquivo |
| **Atomic write** | Escrita via temp + rename, garante "tudo ou nada" |
| **BOM** | Byte Order Mark, marcador de encoding |
| **EOL** | End of Line: `CRLF`, `LF` ou `CR` |
| **Preset / Perfil** | Conjunto de regras + verificações para uma máquina |
| **Lote** | Conjunto de arquivos processados em uma operação |

## Anexo B — Política de Privacidade e Rede

- Aplicação é **100% offline**.
- Nenhum import de bibliotecas de rede no código de produção.
- Nenhuma telemetria.
- Nenhum log enviado externamente.
- Atualizações do EXE são manuais (substituir a pasta).

## Anexo C — Matriz de Rastreabilidade (resumo)

Critério §14 → Especificação → Teste §15:

- C8 → §8.4 → §15.3 linha 2
- C9, C10, C11 → §8.2 → §15.1
- C12 → §7.3, §8.1 → §15.2
- C13 → §8.3 → §15.3 linha 1
- C18 → §10.2 → §15.5
- C19, C20, C21, C22 → §9 → §15.4
- C24 → §7.3.1 → §15.1 + casos de §15.2 (heurística)
- C25 → §8.4 → §15.3

Cada critério restante mapeia para teste manual ou de UI documentado durante a Fase correspondente.
