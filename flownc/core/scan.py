"""Varredura/contagem de ocorrencias de um codigo por arquivo (Mudanca motor).

Funcao pura, com leitura de arquivo injetavel (`read_fn`) — testavel sem disco.
Conta com o MESMO boundary CNC do motor de substituicao (via `find_spans`), de
modo que `M6` nao conte `M60`. Zero ocorrencias e sinal util, nao erro.
"""
from __future__ import annotations

from collections.abc import Callable, Iterable
from pathlib import Path

from .matcher import find_spans
from .models import Mode, ScanResult


def count_occurrences(
    find: str,
    mode: Mode,
    case_sensitive: bool,
    files: Iterable[Path],
    read_fn: Callable[[Path], str],
) -> ScanResult:
    """Conta ocorrencias de `find` em cada arquivo de `files`.

    Args:
        find: codigo de origem a contar (texto literal, nunca regex).
        mode: modo de match (AUTO/LITERAL/CNC_ADDRESS) — define o boundary.
        case_sensitive: respeita maiusculas/minusculas.
        files: caminhos a varrer (a contagem chaveia por `str(path)`).
        read_fn: le o texto de um caminho; injetavel para testar sem disco.

    Returns:
        ScanResult com contagem por arquivo + agregado "X de Y contem".
    """
    counts: dict[str, int] = {}
    for path in files:
        text = read_fn(path)
        counts[str(path)] = len(find_spans(text, find, mode, case_sensitive))
    return ScanResult(find=find, counts=counts)
