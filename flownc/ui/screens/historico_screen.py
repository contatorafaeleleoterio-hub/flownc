"""Tela Histórico (stub do Bloco 2).

No v4 lista uma linha por publicação com "↩ Restaurar originais". O conteúdo real
entra no Bloco 10; aqui só o esqueleto navegável.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class HistoricoScreen(QWidget):
    """Tela-lugar 'Histórico' (índice 3 do QStackedWidget)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("HistoricoScreen")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 16, 16, 16)
        titulo = QLabel("Histórico")
        titulo.setProperty("heading", True)
        lay.addWidget(titulo, alignment=Qt.AlignmentFlag.AlignLeft)
        lay.addStretch(1)
