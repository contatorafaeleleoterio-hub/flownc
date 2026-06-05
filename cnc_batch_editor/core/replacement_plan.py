"""Planejamento de substituicoes contra o conteudo ORIGINAL (PRD secao 8.3/8.4).

Sem cascata: todas as regras casam contra o original; conflitos (sobreposicao
de bytes) sao resolvidos de forma deterministica antes de compor o resultado.
Funcao pura.
"""
from __future__ import annotations

from .matcher import find_matches
from .models import (
    PlannedEdit,
    PlanResult,
    Rule,
    Scope,
    Suppression,
)


def _applies_to_file(rule: Rule, current_file: str | None) -> bool:
    """Regra global aplica a todos; regra de arquivo so ao basename casado."""
    if rule.scope is Scope.GLOBAL:
        return True
    # scope == FILE: aplica quando o basename bate (PRD secao 7.2).
    return current_file is not None and rule.file == current_file


def _winner(a: tuple[int, Rule], b: tuple[int, Rule]) -> tuple[tuple[int, Rule], str]:
    """Decide o vencedor entre dois candidatos em conflito (PRD secao 8.4).

    Cada candidato e (decl_index, rule). Retorna (vencedor, motivo).
    Ordem: 1) regra de arquivo > global; 2) priority menor; 3) declarado antes.
    """
    _, ra = a
    _, rb = b
    if ra.scope is Scope.FILE and rb.scope is Scope.GLOBAL:
        return a, "regra de arquivo suprime global (secao 8.4.1)"
    if rb.scope is Scope.FILE and ra.scope is Scope.GLOBAL:
        return b, "regra de arquivo suprime global (secao 8.4.1)"
    if ra.priority != rb.priority:
        return (a, "menor priority vence (secao 8.4.2)") if ra.priority < rb.priority \
            else (b, "menor priority vence (secao 8.4.2)")
    # priority igual: a declarada primeiro vence (secao 8.4.3).
    return (a, "primeira declarada vence (secao 8.4.3)") if a[0] < b[0] \
        else (b, "primeira declarada vence (secao 8.4.3)")


def build_plan(
    text: str,
    rules: list[Rule],
    case_sensitive: bool = True,
    current_file: str | None = None,
) -> PlanResult:
    """Constroi o plano de edicoes nao-sobrepostas para um arquivo."""
    # 1. Coletar todos os candidatos (start, end, decl_index, rule).
    candidates: list[tuple[int, int, int, Rule]] = []
    match_count: dict[str, int] = {}
    for decl_index, rule in enumerate(rules):
        if not rule.active or not _applies_to_file(rule, current_file):
            continue
        hits = find_matches(text, rule, case_sensitive)
        match_count[rule.id] = match_count.get(rule.id, 0) + len(hits)
        for start, end in hits:
            candidates.append((start, end, decl_index, rule))

    # 2. Ordenar por posicao inicial; resolver sobreposicoes.
    candidates.sort(key=lambda c: (c[0], c[1]))
    edits: list[PlannedEdit] = []
    suppressions: list[Suppression] = []
    last_end = -1
    last: tuple[int, int, int, Rule] | None = None

    for cand in candidates:
        start, end, decl_index, rule = cand
        overlaps = last is not None and start < last_end and end > last[0]
        if not overlaps:
            edits.append(_to_edit(text, cand))
            last, last_end = cand, end
            continue
        # Conflito: decide vencedor entre 'cand' e 'last'.
        assert last is not None
        winner, reason = _winner((decl_index, rule), (last[2], last[3]))
        if winner == (last[2], last[3]):
            # 'last' ja esta em edits; 'cand' e suprimido.
            suppressions.append(
                Suppression(start, end, rule.id, last[3].id, reason)
            )
        else:
            # 'cand' vence: remove o 'last' de edits e registra supressao dele.
            removed = edits.pop()
            suppressions.append(
                Suppression(
                    removed.start, removed.end, removed.rule_id, rule.id, reason
                )
            )
            edits.append(_to_edit(text, cand))
            last, last_end = cand, end

    return PlanResult(
        edits=edits, suppressions=suppressions, match_count_by_rule=match_count
    )


def _to_edit(text: str, cand: tuple[int, int, int, Rule]) -> PlannedEdit:
    start, end, _decl, rule = cand
    return PlannedEdit(
        start=start,
        end=end,
        rule_id=rule.id,
        matched=text[start:end],
        replacement=rule.replace,
    )
