"""Telas-lugar do v4 (rail + QStackedWidget).

Cada tela é um QWidget independente; o maestro (`main_window`) as empilha na
ordem fixa 0=Lote, 1=Editor, 2=Códigos, 3=Histórico. No Bloco 2 são stubs
(título + área vazia); o conteúdo real entra nos Blocos 3+.
"""
from __future__ import annotations

from ui.screens.codigos_screen import CodigosScreen
from ui.screens.editor_screen import EditorScreen
from ui.screens.historico_screen import HistoricoScreen
from ui.screens.lote_screen import LoteScreen

__all__ = ["LoteScreen", "EditorScreen", "CodigosScreen", "HistoricoScreen"]
