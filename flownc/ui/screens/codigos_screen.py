"""Tela Códigos (stub do Bloco 2).

No v4 é a biblioteca de códigos (lista + busca + "+ Adicionar código"). O
conteúdo real entra no Bloco 9; aqui só o esqueleto navegável.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class CodigosScreen(QWidget):
    """Tela-lugar 'Códigos' (índice 2 do QStackedWidget)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("CodigosScreen")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 16, 16, 16)
        titulo = QLabel("Códigos")
        titulo.setProperty("heading", True)
        lay.addWidget(titulo, alignment=Qt.AlignmentFlag.AlignLeft)
        lay.addStretch(1)
