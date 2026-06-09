"""Smoke tests da GUI (headless / offscreen) — layout de 2 colunas (maestro).

Cobrem a estrutura nova (HeaderBar + QSplitter + QStackedWidget + 4 componentes)
e o caminho de substituicao que reusa o core/. Pega a classe de bug que escapa
aos testes de core puro: enum OnZeroMatches virando string ao trafegar pela GUI,
e a troca de painel (resumo <-> editor) ao abrir/fechar arquivo.
"""
from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QMessageBox  # noqa: E402

from core.models import OnZeroMatches, Scope  # noqa: E402
from ui.components import (  # noqa: E402
    CompositorPanel,
    HeaderBar,
    ProgramListPanel,
    SummaryPanel,
)
from ui.main_window import MainWindow  # noqa: E402


@pytest.fixture(scope="module")
def app() -> QApplication:
    existing = QApplication.instance()
    return existing or QApplication([])


@pytest.fixture()
def win(app: QApplication) -> MainWindow:
    w = MainWindow()
    w.resize(1200, 700)
    w.show()
    app.processEvents()  # garante geometria real p/ QSplitter.setSizes
    return w


# ============ estrutura / componentes ============


def test_componentes_instanciam_isolados(app: QApplication) -> None:
    """Cada componente importa e instancia sem depender dos demais."""
    assert HeaderBar() is not None
    assert CompositorPanel() is not None
    assert ProgramListPanel() is not None
    assert SummaryPanel() is not None


def test_maestro_monta_layout(win: MainWindow) -> None:
    assert win._header is not None
    assert win._compositor is not None
    assert win._program_list is not None
    assert win._summary is not None
    assert win._stack.count() == 2
    assert win._stack.currentIndex() == 0  # SummaryPanel por padrao


# ============ compositor -> summary ============


def test_compositor_combo_guia_e_seta(win: MainWindow) -> None:
    """CodeCombo: texto-guia 'Selecione o código' e flag da seta que inverte."""
    cb = win._compositor.cb_origem
    assert cb.lineEdit().placeholderText() == "Selecione o código"
    assert cb._popup_open is False
    cb.showPopup()
    assert cb._popup_open is True
    cb.hidePopup()
    assert cb._popup_open is False


def test_compositor_empilha_e_publica_no_lote(win: MainWindow) -> None:
    """Fluxo do mockup: '+ adicionar' empilha; 'Adicionar ao lote' publica."""
    capt: list = []
    win._compositor.regra_adicionada.connect(capt.append)
    win._compositor.cb_origem.setCurrentText("M08")
    win._compositor.cb_destino.setCurrentText("M07")
    # "+ adicionar outra edicao": so empilha, ainda nao publica
    win._compositor._on_add()
    assert win._compositor.get_regras() == []
    assert capt == []
    assert win._compositor.tem_para_commitar()
    # "Adicionar edicao ao lote ->": publica no Resumo
    win._compositor.commit_to_batch()
    regras = win._compositor.get_regras()
    assert len(regras) == 1
    assert regras[0].find == "M08"
    assert regras[0].replace == "M07"
    assert regras[0].scope is Scope.GLOBAL
    assert len(capt) == 1  # sinal emitido uma vez


def test_compositor_commit_inclui_rascunho(win: MainWindow) -> None:
    """Commit sem '+ adicionar' publica a propria linha 'em edicao'."""
    win._compositor.cb_origem.setCurrentText("G54")
    win._compositor.cb_destino.setCurrentText("G55")
    win._compositor.commit_to_batch()
    regras = win._compositor.get_regras()
    assert len(regras) == 1
    assert regras[0].find == "G54"
    assert regras[0].replace == "G55"
    # apos publicar, a lista de montagem fica vazia
    assert not win._compositor.tem_para_commitar()


def test_compositor_de_vazio_nao_publica(win: MainWindow) -> None:
    win._compositor.cb_origem.setCurrentText("")
    win._compositor._on_add()
    win._compositor.commit_to_batch()
    assert win._compositor.get_regras() == []


def test_compositor_remove_regra_publicada(win: MainWindow) -> None:
    win._compositor.cb_origem.setCurrentText("G54")
    win._compositor.commit_to_batch()
    assert len(win._compositor.get_regras()) == 1
    win._compositor.remove_committed(0)
    assert win._compositor.get_regras() == []


# ============ program list ============


def test_program_list_marca_todos_por_padrao(win: MainWindow, tmp_path) -> None:
    a = tmp_path / "A.nc"
    b = tmp_path / "B.nc"
    a.write_text("M8\n", encoding="utf-8")
    b.write_text("G54\n", encoding="utf-8")
    win._set_programs([a, b], str(tmp_path))
    selecionados = win._program_list.get_selecionados()
    assert {p.name for p in selecionados} == {"A.nc", "B.nc"}


# ============ caminho de substituicao (core puro) ============


def test_build_outcomes_nao_crasha(win: MainWindow, tmp_path) -> None:
    p = tmp_path / "O2169"  # programa Fanuc sem extensao
    p.write_text("M08\nG54 T1\nM30\n", encoding="utf-8")
    win._set_programs([p], str(tmp_path))
    common = [(True, "M08", "M07", "", OnZeroMatches.WARN)]
    outcomes, blocked = win._build_outcomes([p], common, cs=False)
    assert len(outcomes) == 1
    assert not blocked
    o = outcomes[0]
    assert o.read_error is None
    assert len(o.edits) == 1  # M08 -> M07
    assert o.checklist and o.checklist[0][2] == 1  # 1 ocorrencia
    assert win._summary_text(outcomes, blocked)
    assert win._detail(o)


def test_politica_error_bloqueia_salvar(win: MainWindow, tmp_path) -> None:
    p = tmp_path / "X.nc"
    p.write_text("M30\n", encoding="utf-8")  # 'G54' nao existe -> 0 ocorrencias
    common = [(True, "G54", "G55", "", OnZeroMatches.ERROR)]
    _outcomes, blocked = win._build_outcomes([p], common, cs=False)
    assert blocked


def test_rules_for_program_escopo_file_so_no_selecionado(win: MainWindow, tmp_path) -> None:
    from core.models import Mode, Rule
    p = tmp_path / "P.nc"
    p.write_text("M8\n", encoding="utf-8")
    win._set_programs([p], str(tmp_path))
    win._program_list.lst_prog.setCurrentRow(0)  # define _current
    regra = Rule(id="r1", find="M8", replace="M08", scope=Scope.FILE, mode=Mode.AUTO)
    aplicaveis = win._rules_for_program(p, [regra])
    assert len(aplicaveis) == 1
    assert aplicaveis[0].file == "P.nc"


# ============ editor por arquivo (troca de painel) ============


def _abrir_editor(win: MainWindow, p) -> None:
    win._set_programs([p], str(p.parent))
    win._program_list.lst_prog.setCurrentRow(0)
    win._abrir_editor(str(p))


def test_abrir_editor_troca_stack(win: MainWindow, tmp_path) -> None:
    p = tmp_path / "O0001.nc"
    p.write_text("M8\nG54\nM30\n", encoding="utf-8")
    _abrir_editor(win, p)
    assert win._stack.currentIndex() == 1
    assert win._stack.currentWidget() is win._editor_panel
    assert win._editor_panel.lbl_file.text() == "O0001.nc"
    assert not win._editor_panel.btn_save.isEnabled()  # nada alterado ainda


def test_fechar_editor_volta_ao_resumo(win: MainWindow, tmp_path) -> None:
    p = tmp_path / "O0009.nc"
    p.write_text("M8\n", encoding="utf-8")
    _abrir_editor(win, p)
    win._fechar_editor()
    assert win._stack.currentIndex() == 0
    assert win._stack.currentWidget() is win._summary


def test_editor_editar_habilita_salvar_e_grava(win: MainWindow, tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(QMessageBox, "information", staticmethod(lambda *a, **k: None))
    p = tmp_path / "O0002.nc"
    p.write_text("M8\nM30\n", encoding="utf-8")
    _abrir_editor(win, p)
    win._editor_panel.editor.setPlainText("M08\nM30\n")
    assert win._editor_panel.tem_alteracao()
    assert win._editor_panel.btn_save.isEnabled()
    assert win._editor_panel.salvar()
    assert p.read_text(encoding="utf-8") == "M08\nM30\n"  # original sobrescrito
    assert not win._editor_panel.btn_save.isEnabled()


def test_editor_varredura_conta_como_o_lote(win: MainWindow, tmp_path) -> None:
    p = tmp_path / "O0003.nc"
    p.write_text("M8\nM80\nM8\n", encoding="utf-8")  # M80 nao deve contar
    _abrir_editor(win, p)
    win._editor_panel.cb_find.setCurrentText("M8")
    win._editor_panel._on_find_text_changed()
    assert win._editor_panel.lbl_count.text() == "2 encontrado(s)"


def test_editor_preserva_crlf_ao_salvar_sem_mudar(win: MainWindow, tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(QMessageBox, "information", staticmethod(lambda *a, **k: None))
    p = tmp_path / "CRLF.nc"
    raw = b"M8\r\nG54\r\nM30\r\n"
    p.write_bytes(raw)
    _abrir_editor(win, p)
    assert not win._editor_panel.tem_alteracao()
    assert win._editor_panel.salvar()
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
    win._program_list.lst_prog.setCurrentRow(0)
    win._abrir_editor(str(p1))
    win._editor_panel.editor.setPlainText("ALTERADO\n")  # fica sujo
    win._program_list.lst_prog.setCurrentRow(1)
    win._abrir_editor(str(p2))  # guarda dispara -> Discard -> abre B.nc
    assert win._editor_panel.lbl_file.text() == "B.nc"
    assert not win._editor_panel.tem_alteracao()
    assert p1.read_text(encoding="utf-8") == "M8\n"  # A.nc nao foi alterado em disco
