"""Tela Lote (mockup v4): Programas (esquerda) + Compositor/Lote de edições (direita).

Bloco 3: o painel Programas (`ProgramListV4`) está integrado à esquerda. O Compositor
com abas e o Lote de edições (direita), além do CTA "Conferir lote →", entram no Bloco 4.
"""
from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.components.program_list_v4 import ProgramListV4


class LoteScreen(QWidget):
    """Tela-lugar 'Lote' (índice 0 do QStackedWidget)."""

    abrir_arquivo = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("LoteScreen")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(16)

        # Coluna esquerda — Programas
        self.program_list = ProgramListV4()
        self.program_list.abrir_arquivo.connect(self.abrir_arquivo.emit)
        lay.addWidget(self.program_list, stretch=11)

        # Coluna direita — Compositor + Lote de edições (Bloco 4)
        self._right = QFrame()
        self._right.setObjectName("LotePanelRight")
        rlay = QVBoxLayout(self._right)
        rlay.setContentsMargins(16, 16, 16, 16)
        titulo = QLabel("Compositor + Lote de edições")
        titulo.setProperty("heading", True)
        rlay.addWidget(titulo)
        rlay.addStretch(1)
        lay.addWidget(self._right, stretch=9)
