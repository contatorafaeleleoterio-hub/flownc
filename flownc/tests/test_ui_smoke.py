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

from PySide6.QtWidgets import QApplication, QMessageBox  # noqa: E402

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


# ============ editor por arquivo ============


def _abrir_editor(win: MainWindow, p) -> None:
    win._set_programs([p], str(p.parent))
    win.lst_prog.setCurrentRow(0)
    win._on_edit_program()


def test_editor_abre_no_stack_e_salvar_comeca_desabilitado(win: MainWindow, tmp_path) -> None:
    p = tmp_path / "O0001.nc"
    p.write_text("M8\nG54\nM30\n", encoding="utf-8")
    _abrir_editor(win, p)
    assert win._right_stack.currentWidget() is win._editor
    assert win._editor.lbl_file.text() == "O0001.nc"
    assert not win._editor.btn_save.isEnabled()  # nada alterado ainda


def test_editor_editar_habilita_salvar_e_salvar_grava(win: MainWindow, tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(QMessageBox, "information", staticmethod(lambda *a, **k: None))
    p = tmp_path / "O0002.nc"
    p.write_text("M8\nM30\n", encoding="utf-8")
    _abrir_editor(win, p)
    win._editor.editor.setPlainText("M08\nM30\n")
    assert win._editor.tem_alteracao()
    assert win._editor.btn_save.isEnabled()
    assert win._editor.salvar()
    assert p.read_text(encoding="utf-8") == "M08\nM30\n"  # original sobrescrito
    assert not win._editor.btn_save.isEnabled()  # voltou ao estado limpo


def test_editor_varredura_conta_como_o_lote(win: MainWindow, tmp_path) -> None:
    p = tmp_path / "O0003.nc"
    p.write_text("M8\nM80\nM8\n", encoding="utf-8")  # M80 nao deve contar
    _abrir_editor(win, p)
    win._editor.cb_find.setCurrentText("M8")
    win._editor._on_scan()
    assert win._editor.lbl_count.text() == "2 encontrado(s)"


def test_editor_preserva_crlf_ao_salvar_sem_mudar(win: MainWindow, tmp_path, monkeypatch) -> None:
    """Regressao: QPlainTextEdit usa \\n, mas o EOL CRLF do disco deve sobreviver."""
    monkeypatch.setattr(QMessageBox, "information", staticmethod(lambda *a, **k: None))
    p = tmp_path / "CRLF.nc"
    raw = b"M8\r\nG54\r\nM30\r\n"
    p.write_bytes(raw)
    _abrir_editor(win, p)
    assert not win._editor.tem_alteracao()  # abrir nao deve marcar como sujo
    assert win._editor.salvar()
    assert p.read_bytes() == raw  # CRLF preservado byte-a-byte


def test_editor_trocar_com_aviso_descartar(win: MainWindow, tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        QMessageBox, "question",
        staticmethod(lambda *a, **k: QMessageBox.StandardButton.Discard),
    )
    p1 = tmp_path / "A.nc"
    p2 = tmp_path / "B.nc"
    p1.write_text("M8\n", encoding="utf-8")
    p2.write_text("G54\n", encoding="utf-8")
    win._set_programs([p1, p2], str(tmp_path))
    win.lst_prog.setCurrentRow(0)
    win._on_edit_program()
    win._editor.editor.setPlainText("ALTERADO\n")  # fica sujo
    win.lst_prog.setCurrentRow(1)
    win._on_edit_program()  # guarda dispara -> Discard -> abre B.nc
    assert win._editor.lbl_file.text() == "B.nc"
    assert not win._editor.tem_alteracao()
    assert p1.read_text(encoding="utf-8") == "M8\n"  # A.nc nao foi alterado em disco
