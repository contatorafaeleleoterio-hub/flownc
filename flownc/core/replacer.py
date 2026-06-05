"""Composicao do resultado final sem cascata (PRD secao 8.3, passo 4).

Aplica as edicoes planejadas do FIM para o INICIO, para nao deslocar os
indices das edicoes ainda nao aplicadas. Funcao pura.
"""
from __future__ import annotations

from .models import PlannedEdit


def apply_edits(text: str, edits: list[PlannedEdit]) -> str:
    """Retorna o texto com as edicoes aplicadas. 'edits' nao pode se sobrepor."""
    for edit in sorted(edits, key=lambda e: e.start, reverse=True):
        text = text[: edit.start] + edit.replacement + text[edit.end :]
    return text
