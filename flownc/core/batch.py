"""Validacao de seguranca de um lote de regras (Mudanca motor).

Reporta o **conflito de regra**: duas ou mais regras agindo sobre o MESMO codigo
de origem (severidade ambar/aviso, nao bloqueia). Isso e distinto do **conflito
de pedaco** (sobreposicao de bytes), que o motor ja resolve sozinho via
`Suppression` no `build_plan` — e portanto NAO e responsabilidade deste modulo.
"""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from .models import Issue, Rule, Severity


def validate_batch(rules: Iterable[Rule], library: object | None = None) -> list[Issue]:
    """Valida um lote de regras e devolve a lista de problemas encontrados.

    Args:
        rules: regras do lote a validar.
        library: biblioteca codigo+funcao+variacoes (Mudanca 2); aceita por
            compatibilidade de assinatura, ainda nao usada nesta validacao.

    Returns:
        Lista de `Issue`. Vazia quando o lote nao tem conflito de regra.
    """
    by_code: dict[str, list[Rule]] = defaultdict(list)
    for rule in rules:
        if not rule.active:
            continue
        by_code[rule.find].append(rule)

    issues: list[Issue] = []
    for code, group in by_code.items():
        if len(group) >= 2:
            issues.append(Issue(
                severity=Severity.WARNING,
                message=(
                    f"Conflito de regra: {len(group)} regras agem sobre o mesmo "
                    f"codigo de origem '{code}'."
                ),
                rule_ids=tuple(r.id for r in group),
            ))
    return issues
