"""Testes da validacao de lote (core/batch.py)."""
from core.batch import validate_batch
from core.models import Mode, Rule, Scope, Severity


def _r(rid, find, replace="", mode=Mode.CNC_ADDRESS, active=True):
    return Rule(id=rid, find=find, replace=replace, scope=Scope.GLOBAL,
                mode=mode, active=active)


def test_conflito_de_regra_avisa_em_ambar():
    rules = [_r("r1", "M8", "M7"), _r("r2", "M8", "M9")]
    issues = validate_batch(rules)
    assert len(issues) == 1
    assert issues[0].severity is Severity.WARNING
    assert set(issues[0].rule_ids) == {"r1", "r2"}


def test_lote_valido_lista_vazia():
    rules = [_r("r1", "M8", "M7"), _r("r2", "T1", "T2")]
    assert validate_batch(rules) == []


def test_conflito_de_regra_diferente_de_conflito_de_pedaco():
    # Dois codigos de origem distintos (M8 e M08) podem casar o mesmo trecho de
    # bytes — isso e conflito de PEDACO (resolvido por Suppression), nao de regra.
    rules = [_r("r1", "M8", "M7"), _r("r2", "M08", "M07")]
    assert validate_batch(rules) == []


def test_regra_inativa_nao_conta_para_conflito():
    rules = [_r("r1", "M8", "M7"), _r("r2", "M8", "M9", active=False)]
    assert validate_batch(rules) == []
