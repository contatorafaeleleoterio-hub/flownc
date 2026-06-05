"""Vetores §15.3 (plano sem cascata e resolucao de conflito) do PRD v2.3."""
from core.models import Mode, Rule, Scope
from core.replacement_plan import build_plan
from core.replacer import apply_edits


def _r(rid, find, replace, scope=Scope.GLOBAL, file=None, priority=100):
    return Rule(id=rid, find=find, replace=replace, scope=scope, mode=Mode.AUTO,
                file=file, priority=priority)


def _apply(rules, text, current_file=None):
    plan = build_plan(text, rules, True, current_file)
    return apply_edits(text, plan.edits), plan


def test_tv_plan_01_sem_cascata():
    got, _ = _apply([_r("r1", "G54", "G55"), _r("r2", "G55", "G56")], "G54 G55")
    assert got == "G55 G56"


def test_tv_plan_02_arquivo_suprime_global():
    rules = [
        _r("g", "T1", "T21", Scope.GLOBAL),
        _r("f", "T1", "T15", Scope.FILE, file="PECA01.nc"),
    ]
    got, plan = _apply(rules, "T1 M6", current_file="PECA01.nc")
    assert got == "T15 M6"
    assert len(plan.suppressions) == 1
    assert plan.suppressions[0].loser_rule_id == "g"
    assert plan.suppressions[0].winner_rule_id == "f"


def test_tv_plan_03_primeira_declarada_vence():
    got, plan = _apply([_r("g1", "T1", "T21"), _r("g2", "T1", "T15")], "T1 M6")
    assert got == "T21 M6"
    assert any(s.loser_rule_id == "g2" for s in plan.suppressions)
