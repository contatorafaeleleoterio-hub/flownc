"""Janela principal do FlowNC — maestro do layout v4 (rail + 4 telas).

MainWindow monta o **topo global** (`TopBar`) acima de uma linha com a **barra
lateral** (`RailWidget`) + um `QStackedWidget` com as 4 telas-lugar, na ordem fixa
0=Lote, 1=Editor, 2=Códigos, 3=Histórico. O rail troca a tela ativa por sinal.

FASE 2 (Bloco 2): as telas são stubs e exibem dados de exemplo; a ligação ao
núcleo (`core/`) entra na Fase 3. Cada tela ganha o seu conteúdo real nos Blocos 3+.
"""
from __future__ import annotations

import sys

from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

import app_paths
from core.library_store import CodeEntry, LibraryError, load_library
from core.settings_store import AppSettings, load_settings
from ui import theme
from ui.components import RailWidget, TopBar
from ui.screens import CodigosScreen, EditorScreen, HistoricoScreen, LoteScreen

# Índices-lugar (espelham a ordem dos botões do rail)
TELA_LOTE = 0
TELA_EDITOR = 1
TELA_CODIGOS = 2
TELA_HISTORICO = 3


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._register_fonts()
        self._apply_stylesheet()
        self.setWindowTitle("FlowNC — Substituicoes em programas CNC")
        self.resize(1180, 720)

        # Estado carregado do disco (usado pelas telas a partir dos Blocos 3+).
        self._library: list[CodeEntry] = []
        self._settings: AppSettings = AppSettings()
        self._preset_paths: dict[str, str] = {}

        self._build_ui()
        self._connect_signals()
        self._load_state()

    # ============ tema visual ============
    def _register_fonts(self) -> None:
        fonts_dir = app_paths.fonts_dir()
        for ttf in fonts_dir.glob("*.ttf"):
            font_id = QFontDatabase.addApplicationFont(str(ttf))
            if font_id < 0:
                print(f"[FlowNC] fonte nao carregada: {ttf}", file=sys.stderr)

    def _apply_stylesheet(self) -> None:
        qss_file = app_paths.qss_path()
        try:
            template = qss_file.read_text(encoding="utf-8")
            qss = theme.render_qss(template)
            self.setStyleSheet(qss)
        except (OSError, KeyError, ValueError):
            pass  # sem QSS valido: app usa estilo padrao do Qt

    # ============ construcao (maestro) ============
    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Topo global (visível em todas as telas)
        self._top = TopBar()
        root.addWidget(self._top)

        # Linha: rail (esquerda) + pilha de telas (centro)
        corpo = QWidget()
        corpo_lay = QHBoxLayout(corpo)
        corpo_lay.setContentsMargins(0, 0, 0, 0)
        corpo_lay.setSpacing(0)

        self._rail = RailWidget()
        corpo_lay.addWidget(self._rail)

        self._stack = QStackedWidget()
        self._lote = LoteScreen()
        self._editor_screen = EditorScreen()
        self._codigos = CodigosScreen()
        self._historico = HistoricoScreen()
        self._stack.addWidget(self._lote)            # índice 0 = Lote
        self._stack.addWidget(self._editor_screen)   # índice 1 = Editor
        self._stack.addWidget(self._codigos)         # índice 2 = Códigos
        self._stack.addWidget(self._historico)       # índice 3 = Histórico
        corpo_lay.addWidget(self._stack, stretch=1)

        root.addWidget(corpo, stretch=1)
        self._stack.setCurrentIndex(TELA_LOTE)

    def _connect_signals(self) -> None:
        self._rail.tela_mudou.connect(self._ir_para_tela)
        self._top.receita_alterada.connect(self._on_receita_alterada)
        self._top.salvar_receita_solicitado.connect(self._on_salvar_receita)
        self._top.backup_clicado.connect(self._on_trocar_backup)

    # ============ navegacao ============
    def _ir_para_tela(self, idx: int) -> None:
        self._stack.setCurrentIndex(idx)
        self._rail.set_tela_ativa(idx)

    # ============ topo (stubs — ligados nos Blocos 11/Fase 3) ============
    def _on_receita_alterada(self, _nome: str) -> None:
        """Carregar a receita selecionada (Bloco 11.1 / Fase 3)."""

    def _on_salvar_receita(self) -> None:
        """Salvar o lote atual como receita (Bloco 11.2 / Fase 3)."""

    def _on_trocar_backup(self) -> None:
        """Trocar a pasta de backup (Bloco 11.3 / Fase 3)."""

    # ============ carga de estado (defensiva) ============
    def _load_state(self) -> None:
        try:
            self._library = load_library(app_paths.library_path())
        except LibraryError:
            self._library = []

        try:
            self._settings = load_settings(app_paths.settings_path())
        except OSError:
            self._settings = AppSettings()
        backup_dir = self._settings.backup_dir or self._settings.output_dir
        if backup_dir:
            self._top.set_backup_path(backup_dir)

        pdir = app_paths.presets_dir()
        files = sorted(pdir.glob("*.json")) if pdir.is_dir() else []
        self._preset_paths = {f.stem: str(f) for f in files}
        self._top.set_receitas(list(self._preset_paths.keys()))
