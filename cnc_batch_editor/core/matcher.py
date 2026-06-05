"""Construcao segura de padroes e localizacao de matches (PRD secao 8).

Funcoes puras. O usuario nunca digita regex: todo 'find' passa por re.escape.
"""
from __future__ import annotations

import re

from .models import Mode, Rule

# Conjunto de letras de endereco CNC para a heuristica 'auto' (PRD secao 7.3.1).
CNC_LETTERS = frozenset("THDGMSFNOPQR")

# Forma de endereco CNC: uma letra maiuscula seguida so de digitos.
_ADDRESS_RE = re.compile(r"^[A-Z][0-9]+$")


def resolve_mode(find: str, mode: Mode) -> Mode:
    """Resolve o modo efetivo. Heuristica de 'auto' conforme PRD secao 7.3.1."""
    if mode is not Mode.AUTO:
        return mode
    if _ADDRESS_RE.match(find) and find[0] in CNC_LETTERS:
        return Mode.CNC_ADDRESS
    return Mode.LITERAL


def build_pattern(find: str, resolved_mode: Mode) -> str:
    """Monta a expressao regular interna a partir do texto literal do usuario.

    Boundary CNC (PRD secao 8.2):
        (?<![A-Z]) FIND (?![0-9.])
    - Lookbehind bloqueia apenas LETRA antes (find colado a uma palavra, ex.:
      'T1' em '(OFFSET1)'). Permite digito/ponto antes, pois e o fim do endereco
      anterior em blocos reais Fanuc: 'M6T1', 'G43H1T1', 'Z20.T1'.
    - Lookahead bloqueia 'T1' casar em 'T10'/'T100'/'T1.5' e 'G54' em 'G54.1'.
    """
    escaped = re.escape(find)
    if resolved_mode is Mode.CNC_ADDRESS:
        return rf"(?<![A-Z]){escaped}(?![0-9.])"
    return escaped


def compile_rule(find: str, mode: Mode, case_sensitive: bool = True) -> re.Pattern[str]:
    resolved = resolve_mode(find, mode)
    flags = 0 if case_sensitive else re.IGNORECASE
    return re.compile(build_pattern(find, resolved), flags)


def find_matches(
    text: str, rule: Rule, case_sensitive: bool = True
) -> list[tuple[int, int]]:
    """Retorna os intervalos (start, end) de cada ocorrencia da regra no texto."""
    if not rule.find:
        return []
    pattern = compile_rule(rule.find, rule.mode, case_sensitive)
    return [(m.start(), m.end()) for m in pattern.finditer(text)]


def suggest_leading_zero_variant(text: str, find: str) -> str | None:
    """Dica de leading-zero (PRD secao 8.5).

    Quando 'find' tem forma de endereco (ex.: 'M8') e nao casou, procura no texto
    um endereco da mesma letra e mesmo valor numerico, mas com zeros a esquerda
    (ex.: 'M08'). Retorna a forma encontrada, ou None.
    """
    m = _ADDRESS_RE.match(find)
    if not m:
        return None
    letter, num = find[0], int(find[1:])
    for hit in re.finditer(rf"(?<![A-Z]){re.escape(letter)}([0-9]+)(?![0-9.])", text):
        token = hit.group(0)
        if token != find and int(hit.group(1)) == num:
            return token
    return None
