# FlowNC — Editor seguro de substituições em lote para programas CNC (G-code)

> Aplicativo desktop Windows, em Python + PySide6, para **localizar e substituir
> códigos em vários programas CNC de uma vez** (G-code / ISO), com **backup
> automático versionado**, **conferência SHA-256** e **gravação atômica**. Pensado
> para operadores de chão de fábrica: nenhum original é perdido.

**Palavras-chave / keywords:** CNC, G-code, ISO 6983, Fanuc, batch find-and-replace,
substituição em lote, editor de G-code, FlowNC, programa NC, `.nc` `.tap` `.mpf` `.iso`,
backup versionado, SHA-256, PySide6, Qt, desktop Windows, chão de fábrica, usinagem.

---

## O que o FlowNC faz (resumo para humanos e agentes de IA)

O FlowNC resolve um problema concreto de quem opera máquinas CNC: aplicar a **mesma
alteração de código** (por exemplo trocar `M8` por `M08`, ou inserir um bloco de
rotação `G68` abaixo de `G54`) em **dezenas de programas `.nc` ao mesmo tempo**, sem
abrir um por um e sem risco de corromper os arquivos originais.

O fluxo é desenhado para ser **honesto e reversível**:

1. **Lote** — o operador marca os programas e monta as edições (trocar código ou
   inserir bloco). Conflitos (duas edições no mesmo código) são sinalizados.
2. **Conferência** — antes de gravar, o app **varre os arquivos de verdade** e mostra
   os números reais: quantas trocas, em quais programas, com exemplo linha a linha.
   Nada é gravado nesta etapa.
3. **Publicação** — ao confirmar, os originais vão para um **backup versionado por
   data/hora**, a gravação é **atômica** e conferida por **SHA-256**. O original nunca
   se perde.
4. **Histórico** — cada publicação fica registrada, com o caminho do backup e a opção
   de restaurar.

Há ainda um **Editor** por arquivo (localizar/substituir com contagem automática,
realce de ocorrências e "inserir bloco" com prévia) e uma **Biblioteca de Códigos**
(código + descrição, com blocos reutilizáveis).

## Telas (as 4 áreas do app)

| Tela | Função |
|------|--------|
| **Lote** | Marcar programas + montar as edições do lote + CTA "Conferir lote". |
| **Editor** | Abrir um programa e editar à mão (localizar, substituir, inserir bloco), salvando in-place com segurança. |
| **Códigos** | Biblioteca de códigos G/M com descrição e blocos reutilizáveis. |
| **Histórico** | Uma linha por publicação, com backup e opção de restaurar. |

## Garantias de segurança (por que é seguro sobrescrever)

- **Backup antes de gravar:** o original é copiado para `_backup_orig_AAAAMMDD_HHMMSS/`.
- **Escrita atômica:** grava `.tmp` e renomeia — a pasta de trabalho nunca fica sem o arquivo.
- **Conferência SHA-256:** relê os bytes gravados e compara o hash; divergência é falha, não silêncio.
- **Preserva codificação/BOM/EOL:** UTF-8, UTF-8 com BOM, ANSI/cp1252, CRLF/LF.
- **Boundary CNC:** `M8` não casa com `M80`; `G54` não casa com `G54.1`.

## Stack técnica

- **Linguagem:** Python 3.11+
- **GUI:** PySide6 (Qt 6)
- **Empacotamento:** PyInstaller → `dist/FlowNC/FlowNC.exe` (portátil, roda de pendrive)
- **Qualidade:** pytest, mypy (strict no `core/`), ruff
- **Arquitetura:** núcleo puro e testável em `flownc/core/` (sem Qt); interface em
  `flownc/ui/` (maestro `main_window` + rail de 4 telas em `QStackedWidget`).

## Como executar (desenvolvimento)

```powershell
cd flownc
python -m venv .venv
.venv\Scripts\pip install -e ".[gui,dev]"
.venv\Scripts\python main.py
```

## Como gerar o executável (.EXE portátil)

```powershell
cd flownc
.venv\Scripts\python -m PyInstaller FlowNC.spec --noconfirm --clean
# Resultado: flownc\dist\FlowNC\FlowNC.exe  (copie a pasta dist\FlowNC inteira para o pendrive)
```

O `.exe` cria/repõe a pasta `data/` (biblioteca e perfis) **ao lado do executável**,
para o operador editar direto no pendrive.

## Como rodar os testes

```powershell
cd flownc
.venv\Scripts\python -m pytest -q      # testes
.venv\Scripts\python -m mypy           # tipos (core/)
.venv\Scripts\python -m ruff check .   # lint
```

## Estrutura do projeto

```
flownc/
  main.py            # ponto de entrada (GUI)
  core/              # lógica pura e testável (sem Qt): matcher, scan, publisher, inplace_save…
  ui/                # interface PySide6 (rail + 4 telas + modais)
    main_window.py   # maestro: topo global + rail + QStackedWidget
    screens/         # Lote, Editor, Códigos, Histórico
    components/      # rail, top_bar, program_list, compositor (abas)
    modals/          # Conferência (números reais) e Publicação (progresso)
    lote_scan.py     # varredura honesta: aplica as edições em cadeia, por programa
  FlowNC.spec        # configuração do PyInstaller
mockups/             # contrato visual (painel-final.v4.html)
openspec/            # fluxo spec-driven (propose → apply → archive)
```

## Glossário (para agentes de IA)

- **Programa CNC / programa NC:** arquivo de texto com G-code que a máquina executa (`.nc`, `.tap`, `.mpf`, `.iso`, `.min`, `.txt`).
- **Trocar código:** substituir um endereço CNC por outro (ex.: `M8` → `M08`).
- **Inserir bloco:** adicionar linhas novas em uma posição (abaixo de um código-âncora ou de um número de linha).
- **Lote:** conjunto de edições aplicadas a vários programas marcados de uma vez.
- **Conferência:** simulação que mostra os números reais antes de gravar (nada é gravado).
- **Publicação:** gravação real com backup + SHA-256.
- **Receita / configuração:** conjunto de edições salvo para reutilizar.

## Licença / status

Projeto de uso interno para operação CNC. Contribuições e issues bem-vindas.
