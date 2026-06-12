"""Smoke tests da GUI (headless / offscreen) — estrutura v4 (rail + 4 telas).

Cobrem o maestro do v4: topo global (`TopBar`) + barra lateral (`RailWidget`) +
`QStackedWidget` com as 4 telas-lugar (Lote, Editor, Códigos, Histórico) e a
navegação entre elas. Os fluxos de cada tela são cobertos por testes próprios à
medida que cada tela é construída (Blocos 3+).
"""
from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication  # noqa: E402

from ui.components import RailWidget, TopBar  # noqa: E402
from ui.components.program_list_v4 import ProgramListV4  # noqa: E402
from ui.main_window import (  # noqa: E402
    TELA_CODIGOS,
    TELA_EDITOR,
    TELA_HISTORICO,
    TELA_LOTE,
    MainWindow,
)
from ui.screens import (  # noqa: E402
    CodigosScreen,
    EditorScreen,
    HistoricoScreen,
    LoteScreen,
)


@pytest.fixture(scope="module")
def app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


@pytest.fixture()
def win(app: QApplication) -> MainWindow:
    w = MainWindow()
    w.resize(1200, 700)
    w.show()
    app.processEvents()
    return w


# ============ estrutura / componentes ============


def test_componentes_v4_instanciam_isolados(app: QApplication) -> None:
    """Cada peça do v4 importa e instancia sem depender das demais."""
    assert RailWidget() is not None
    assert TopBar() is not None
    assert LoteScreen() is not None
    assert EditorScreen() is not None
    assert CodigosScreen() is not None
    assert HistoricoScreen() is not None


def test_maestro_monta_estrutura_v4(win: MainWindow) -> None:
    """Topo + rail + pilha de 4 telas na ordem fixa; Lote ativa por padrão."""
    assert isinstance(win._top, TopBar)
    assert isinstance(win._rail, RailWidget)
    assert win._stack.count() == 4
    assert win._stack.currentIndex() == TELA_LOTE
    assert isinstance(win._stack.widget(TELA_LOTE), LoteScreen)
    assert isinstance(win._stack.widget(TELA_EDITOR), EditorScreen)
    assert isinstance(win._stack.widget(TELA_CODIGOS), CodigosScreen)
    assert isinstance(win._stack.widget(TELA_HISTORICO), HistoricoScreen)


# ============ navegação pelo rail ============


def test_rail_sinal_troca_tela(win: MainWindow) -> None:
    """Emitir tela_mudou troca o widget central (conexão maestro)."""
    win._rail.tela_mudou.emit(TELA_HISTORICO)
    assert win._stack.currentIndex() == TELA_HISTORICO
    win._rail.tela_mudou.emit(TELA_LOTE)
    assert win._stack.currentIndex() == TELA_LOTE


def test_rail_clique_nos_4_botoes_troca_tela(win: MainWindow) -> None:
    """Clicar em cada um dos 4 botões do rail leva à tela correspondente."""
    for idx in (TELA_LOTE, TELA_EDITOR, TELA_CODIGOS, TELA_HISTORICO):
        win._rail._botoes[idx].click()
        assert win._stack.currentIndex() == idx


def test_rail_bolinha_editor_liga_desliga(win: MainWindow) -> None:
    """A bolinha de alteração não salva no botão Editor liga e desliga."""
    win._rail.set_editor_dirty(True)
    assert win._rail._dot.isVisible()
    win._rail.set_editor_dirty(False)
    assert not win._rail._dot.isVisible()


# ============ tela Lote · painel Programas ============


def _criar_programas(tmp_path, n: int = 2) -> list:
    paths = []
    for i in range(n):
        p = tmp_path / f"O{i}.nc"
        p.write_text("M8\n", encoding="utf-8")
        paths.append(p)
    return paths


def test_program_list_estado_vazio(app: QApplication) -> None:
    """Sem programas: mostra o estado vazio e esconde a lista; nada marcado."""
    pl = ProgramListV4()
    assert not pl._empty.isHidden()
    assert pl._scroll.isHidden()
    assert pl.get_marcados() == []


def test_program_list_renderiza_linhas(app: QApplication, tmp_path) -> None:
    pl = ProgramListV4()
    pl.set_programs(_criar_programas(tmp_path, 2))
    assert len(pl._rows) == 2
    assert pl._empty.isHidden()
    assert not pl._scroll.isHidden()
    assert pl._chip.text() == "0 de 2 marcados"


def test_program_list_marcar_atualiza_chip(app: QApplication, tmp_path) -> None:
    pl = ProgramListV4()
    pl.set_programs(_criar_programas(tmp_path, 2))
    pl._rows[0].toggled.emit()  # clique na primeira linha
    assert {p.name for p in pl.get_marcados()} == {"O0.nc"}
    assert pl._chip.text() == "1 de 2 marcados"


def test_program_list_marcar_todos(app: QApplication, tmp_path) -> None:
    pl = ProgramListV4()
    pl.set_programs(_criar_programas(tmp_path, 3))
    pl._toggle_all()
    assert len(pl.get_marcados()) == 3
    assert pl._btn_all.text() == "Desmarcar todos"
    pl._toggle_all()
    assert pl.get_marcados() == []
    assert pl._btn_all.text() == "Marcar todos"


def test_program_list_add_nao_duplica(app: QApplication, tmp_path) -> None:
    pl = ProgramListV4()
    progs = _criar_programas(tmp_path, 2)
    pl.add_programs(progs)
    assert len(pl._rows) == 2
    pl.add_programs(progs)  # mesmos arquivos
    assert len(pl._rows) == 2


def test_lote_screen_integra_program_list(win: MainWindow) -> None:
    lote = win._stack.widget(TELA_LOTE)
    assert isinstance(lote, LoteScreen)
    assert isinstance(lote.program_list, ProgramListV4)
