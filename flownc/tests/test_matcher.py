"""Vetores §15.1 (cnc_address) e §15.2 (literal) do PRD v2.3."""
import pytest

from core.models import Mode, Rule, Scope
from core.replacement_plan import build_plan
from core.replacer import apply_edits


def _apply(rules, text, case_sensitive=True, current_file=None):
    plan = build_plan(text, rules, case_sensitive, current_file)
    return apply_edits(text, plan.edits)


def _r(find, replace, mode=Mode.AUTO):
    return Rule(id="r", find=find, replace=replace, scope=Scope.GLOBAL, mode=mode)


@pytest.mark.parametrize("tid,find,replace,text,expected", [
    ("TV-CNC-01", "T1", "T21", "T1 M6", "T21 M6"),
    ("TV-CNC-02", "T1", "T21", "M6T1", "M6T21"),
    ("TV-CNC-03", "T1", "T21", "G43H1T1", "G43H1T21"),
    ("TV-CNC-04", "T1", "T21", "Z20.T1", "Z20.T21"),
    ("TV-CNC-05", "T1", "T21", "T10 M6", "T10 M6"),
    ("TV-CNC-06", "T1", "T21", "T100 M6", "T100 M6"),
    ("TV-CNC-07", "T1", "T21", "(T1 USADO)", "(T21 USADO)"),
    ("TV-CNC-08", "T1", "T21", "(OFFSET1)", "(OFFSET1)"),
    ("TV-CNC-09", "F1", "F2", "F1.5", "F1.5"),
    ("TV-CNC-10", "G54", "G55", "G54.1 P1", "G54.1 P1"),
    ("TV-CNC-11", "M8", "M7", "M08", "M08"),
    ("TV-CNC-12", "M08", "M07", "M08", "M07"),
    ("TV-CNC-13", "G54", "G55", "G54G90", "G55G90"),
    ("TV-CNC-14", "S3000", "S4000", "S30000", "S30000"),
])
def test_cnc_address(tid, find, replace, text, expected):
    assert _apply([_r(find, replace)], text) == expected, tid


@pytest.mark.parametrize("tid,find,replace,text,expected", [
    ("TV-LIT-01", "(FRESA Ø12)", "(FRESA Ø10)", "(FRESA Ø12)", "(FRESA Ø10)"),
    ("TV-LIT-02", "X1.5", "X2.5", "X1.5", "X2.5"),
    ("TV-LIT-03", "S3000 M03", "", "N10 S3000 M03 T1", "N10  T1"),
])
def test_literal(tid, find, replace, text, expected):
    assert _apply([_r(find, replace)], text) == expected, tid
