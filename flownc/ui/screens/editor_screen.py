"""Tela Editor (stub do Bloco 2).

No v4 é o editor em tela cheia com faixa de arquivos à esquerda e toolbar em 3
grupos. O conteúdo real entra nos Blocos 7 e 8; aqui só o esqueleto navegável.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class EditorScreen(QWidget):
    """Tela-lugar 'Editor' (índice 1 do QStackedWidget)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("EditorScreen")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 16, 16, 16)
        titulo = QLabel("Editor")
        titulo.setProperty("heading", True)
        lay.addWidget(titulo, alignment=Qt.AlignmentFlag.AlignLeft)
        lay.addStretch(1)
