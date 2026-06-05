"""Smoke tests da GUI (headless / offscreen).

Pega a classe de bug que escapou aos testes de core puro: o botao 'Executar
substituicoes' nao fazia nada porque o enum OnZeroMatches (subclasse de str)
virava string ao passar pelo QTableWidgetItem.setData/data, e '.value' crashava.
Como o EXE roda '--windowed', o crash era silencioso.
"""
from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication  # noqa: E402

from core.models import OnZeroMatches  # noqa: E402
from ui.main_window import MainWindow  # noqa: E402


@pytest.fixture(scope="module")
def app() -> QApplication:
    existing = QApplication.instance()
    return existing or QApplication([])


@pytest.fixture()
def win(app: QApplication) -> MainWindow:
    return MainWindow()


def test_read_subs_table_retorna_enum(win: MainWindow) -> None:
    """O bug raiz: on_zero_matches deve voltar como enum, nunca string pura."""
    win.tbl_common.setRowCount(0)  # ignora regras semeadas pelo preset
    win._add_subs_row(win.tbl_common, True, "M08", "M07", "obs")
    rows = win._read_subs_table(win.tbl_common)
    assert len(rows) == 1
    on_zero = rows[0][4]
    assert isinstance(on_zero, OnZeroMatches)
    assert on_zero is OnZeroMatches.WARN


def test_read_subs_table_preserva_politica_error(win: MainWindow) -> None:
    win.tbl_common.setRowCount(0)
    win._add_subs_row(win.tbl_common, True, "G54", "G55", "", OnZeroMatches.ERROR)
    rows = win._read_subs_table(win.tbl_common)
    assert rows[0][4] is OnZeroMatches.ERROR


def test_build_outcomes_nao_crasha(win: MainWindow, tmp_path) -> None:
    """Reproduz o fluxo do botao Executar (sem o dialog modal)."""
    p = tmp_path / "O2169"  # programa Fanuc sem extensao
    p.write_text("M08\nG54 T1\nM30\n", encoding="utf-8")
    win._set_programs([p], str(tmp_path))
    win.tbl_common.setRowCount(0)
    win._add_subs_row(win.tbl_common, True, "M08", "M07", "")
    common = win._read_subs_table(win.tbl_common)
    checked = win._checked_programs()
    outcomes, blocked = win._build_outcomes(checked, common, cs=False)
    assert len(outcomes) == 1
    assert not blocked
    o = outcomes[0]
    assert o.read_error is None
    assert len(o.edits) == 1  # M08 -> M07
    # checklist (Sessao D) e gerado sem crash
    assert o.checklist
    assert o.checklist[0][2] == 1  # 1 ocorrencia

    # _summary e _detail tambem montam sem crash
    assert win._summary(outcomes, blocked)
    assert win._detail(o)
