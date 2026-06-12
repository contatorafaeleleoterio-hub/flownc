"""Varredura do lote de edições (mesma honestidade do `scanLote` do v4).

Aplica as edições **em cadeia, por programa, na ordem do lote** — exatamente o
que a publicação fará — para que os números da Conferência batam com o que é
gravado. Reaproveita o boundary CNC do motor (`core.matcher.find_spans`): `M8`
não conta `M80`.

Funções puras sobre texto (testáveis sem GUI nem disco). A UI lê os arquivos
marcados, chama `scan_lote` e apresenta os resultados.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from core.matcher import find_spans
from core.models import Mode
from ui.components.compositor_v4 import Edicao


@dataclass(frozen=True)
class Exemplo:
    """Exemplo real de uma troca: linha N, original e resultado."""

    arquivo: str
    linha: int
    original: str
    novo: str


@dataclass
class PorPrograma:
    """Efeito de uma edição num programa: nome + nº de ocorrências/aplicações."""

    nome: str
    n: int


@dataclass
class EdicaoResultado:
    """Resultado agregado de uma edição sobre todos os programas marcados."""

    edicao: Edicao
    por_programa: list[PorPrograma] = field(default_factory=list)
    total: int = 0
    exemplo: Exemplo | None = None


@dataclass
class ScanLote:
    """Resultado completo da varredura — pronto para a Conferência e a Publicação."""

    resultados: list[EdicaoResultado]
    finais: dict[str, str]      # nome do programa -> texto final (encadeado)
    originais: dict[str, str]   # nome do programa -> texto original

    @property
    def total_trocas(self) -> int:
        return sum(r.total for r in self.resultados if r.edicao.tipo == "swap")

    @property
    def total_geral(self) -> int:
        return sum(r.total for r in self.resultados)

    @property
    def programas_com_bloco(self) -> int:
        nomes: set[str] = set()
        for r in self.resultados:
            if r.edicao.tipo == "ins":
                nomes.update(p.nome for p in r.por_programa if p.n)
        return len(nomes)

    def programas_afetados(self) -> int:
        """Quantos programas mudaram (final != original)."""
        return sum(1 for n, txt in self.finais.items() if txt != self.originais[n])

    def sem_efeito(self) -> list[Edicao]:
        """Edições que não tocaram nenhum programa marcado."""
        return [r.edicao for r in self.resultados if r.total == 0]


def _aplicar_swap(texto: str, origem: str, destino: str) -> tuple[str, int]:
    """Troca todas as ocorrências de `origem` por `destino` (vazio = remover)."""
    spans = find_spans(texto, origem, Mode.AUTO, case_sensitive=True)
    if not spans:
        return texto, 0
    out = texto
    for start, end in sorted(spans, reverse=True):
        out = out[:start] + destino + out[end:]
    return out, len(spans)


def _ponto_insercao(texto: str, ed: Edicao) -> int:
    """Índice da linha onde o bloco entraria; -1 se a âncora não aparece."""
    linhas = texto.split("\n")
    if ed.modo == "code":
        for i, ln in enumerate(linhas):
            if find_spans(ln, ed.codigo, Mode.AUTO, case_sensitive=True):
                return i + 1
        return -1
    return min(max(1, ed.linha), len(linhas))


def _aplicar_ins(texto: str, ed: Edicao) -> tuple[str, int]:
    """Insere o bloco no ponto de inserção; n=1 se inseriu, 0 se âncora ausente."""
    at = _ponto_insercao(texto, ed)
    if at < 0:
        return texto, 0
    linhas = texto.split("\n")
    novas = ed.texto.split("\n")
    out = linhas[:at] + novas + linhas[at:]
    return "\n".join(out), 1


def _exemplo_swap(texto: str, ed: Edicao, nome: str) -> Exemplo | None:
    """Primeira linha de `texto` que contém a origem — original vs. resultado."""
    for i, linha in enumerate(texto.split("\n")):
        if find_spans(linha, ed.origem, Mode.AUTO, case_sensitive=True):
            nova, _ = _aplicar_swap(linha, ed.origem, ed.destino)
            return Exemplo(arquivo=nome, linha=i + 1, original=linha, novo=nova)
    return None


def aplicar_edicoes(texto: str, edicoes: list[Edicao]) -> tuple[str, int, int]:
    """Aplica as edições em cadeia num único texto (ordem do lote).

    Returns:
        (texto_final, total_trocas, total_blocos_inseridos).
    """
    n_swap = 0
    n_ins = 0
    for ed in edicoes:
        if ed.tipo == "ins":
            texto, n = _aplicar_ins(texto, ed)
            n_ins += n
        else:
            texto, n = _aplicar_swap(texto, ed.origem, ed.destino)
            n_swap += n
    return texto, n_swap, n_ins


def scan_lote(edicoes: list[Edicao], programas: dict[str, str]) -> ScanLote:
    """Aplica as edições em cadeia, por programa, e devolve os números reais.

    Args:
        edicoes: lista de edições do lote, na ordem em que serão publicadas.
        programas: mapa nome do programa -> texto original.

    Returns:
        `ScanLote` com o resultado por edição, os textos finais e os originais.
    """
    resultados = [EdicaoResultado(edicao=ed) for ed in edicoes]
    finais: dict[str, str] = {}
    originais: dict[str, str] = dict(programas)

    for nome, original in programas.items():
        texto = original
        for i, ed in enumerate(edicoes):
            if ed.tipo == "ins":
                texto, n = _aplicar_ins(texto, ed)
            else:
                if resultados[i].exemplo is None:
                    ex = _exemplo_swap(texto, ed, nome)
                    if ex is not None:
                        resultados[i].exemplo = ex
                texto, n = _aplicar_swap(texto, ed.origem, ed.destino)
            resultados[i].por_programa.append(PorPrograma(nome=nome, n=n))
        finais[nome] = texto

    for r in resultados:
        r.total = sum(p.n for p in r.por_programa)

    return ScanLote(resultados=resultados, finais=finais, originais=originais)
