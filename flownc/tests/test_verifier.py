"""Vetores §15.5 (verificacoes estruturais obrigatorias) do PRD v2.3."""
from core.models import Severity
from core.verifier import is_blocking, run_structural


def test_tv_str_01_percent_preservado_ok():
    original = "%\nO1\nM30\n%\n"
    result = "%\nO1\nM30\n%\n"
    assert not is_blocking(run_structural(original, result))


def test_tv_str_02_remove_percent_final_bloqueia():
    original = "%\nO1\nM30\n%\n"
    result = "%\nO1\nM30\n"
    res = run_structural(original, result)
    assert is_blocking(res)


def test_tv_str_03_remove_m30_bloqueia():
    original = "%\nO1\nM30\n%\n"
    result = "%\nO1\n\n%\n"
    assert is_blocking(run_structural(original, result))


def test_tv_str_05_remove_m06_apenas_alerta():
    original = "%\nM06 T1\nM30\n%\n"
    result = "%\n\nM30\n%\n"
    res = run_structural(original, result)
    assert not is_blocking(res)
    assert any(r.severity is Severity.WARNING for r in res)


def test_tv_str_06_resultado_vazio_bloqueia():
    assert is_blocking(run_structural("%\nM30\n%\n", "   \n  "))


def test_tv_str_07_m300_nao_mascara_perda_de_m30():
    # H0.2: substring antiga ('M30' in 'M300' == True) mascararia a perda do M30 real.
    # Com token CNC, 'M300' nao conta como 'M30' -> a perda do fim e ACUSADA.
    original = "%\nO1\nM30\nX10. M300\n%\n"  # um M30 real + um M300 (codigo qualquer)
    result = "%\nO1\nX10. M300\n%\n"         # perdeu o M30 real; sobrou so o M300
    assert is_blocking(run_structural(original, result))
