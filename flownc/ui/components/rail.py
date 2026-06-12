"""RailWidget: barra lateral escura com os 4 botões-lugar do v4.

Lugares fixos (índices fixos — mesma ordem do QStackedWidget do maestro):
0=Lote · 1=Editor · 2=Códigos · 3=Histórico. Emite ``tela_mudou(int)`` ao clicar.
O botão ativo recebe o filete laranja (via QSS, propriedade ``active``); o botão
Editor exibe uma bolinha laranja quando há alteração não salva (``set_editor_dirty``).
"""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import (
    QButtonGroup,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui import theme

# Índices-lugar (espelham a ordem das telas no QStackedWidget do maestro)
LOTE = 0
EDITOR = 1
CODIGOS = 2
HISTORICO = 3

_ITENS = [
    (LOTE, "▦", "Lote"),
    (EDITOR, "✎", "Editor"),
    (CODIGOS, "🏷", "Códigos"),
    (HISTORICO, "🕘", "Histórico"),
]


def _repolish(w: QWidget) -> None:
    """Reaplica o QSS após mudar uma propriedade dinâmica (active/dot)."""
    style = w.style()
    style.unpolish(w)
    style.polish(w)


class RailWidget(QWidget):
    """Barra lateral com os 4 botões-lugar; troca de tela por ``tela_mudou(int)``."""

    tela_mudou = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("Rail")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedWidth(theme.DIM_RAIL)
        self._botoes: list[QPushButton] = []
        self._build_ui()
        self.set_tela_ativa(LOTE)

    def _build_ui(self) -> None:
        lay = QVBoxLayout(self)
        lay.setContentsMargins(theme.SP_8, theme.SP_12, theme.SP_8, theme.SP_12)
        lay.setSpacing(theme.SP_8)

        logo = QLabel("◉")
        logo.setObjectName("RailLogo")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(logo, alignment=Qt.AlignmentFlag.AlignHCenter)

        grupo = QButtonGroup(self)
        grupo.setExclusive(True)
        for idx, icon, texto in _ITENS:
            btn = QPushButton(f"{icon}\n{texto}")
            btn.setObjectName("RailItem")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _checked=False, i=idx: self._on_click(i))
            grupo.addButton(btn, idx)
            self._botoes.append(btn)
            lay.addWidget(btn)

        lay.addStretch(1)

        foot = QLabel("v4")
        foot.setObjectName("RailFoot")
        foot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(foot)

        # Bolinha de status (alteração não salva) sobreposta ao botão Editor.
        self._dot = QLabel(self._botoes[EDITOR])
        self._dot.setObjectName("RailDot")
        self._dot.setFixedSize(8, 8)
        self._dot.hide()

    def _on_click(self, idx: int) -> None:
        self.set_tela_ativa(idx)
        self.tela_mudou.emit(idx)

    def set_tela_ativa(self, idx: int) -> None:
        """Marca o botão `idx` como ativo (filete laranja) e os demais como inativos."""
        for i, btn in enumerate(self._botoes):
            ativo = i == idx
            btn.setChecked(ativo)
            btn.setProperty("active", ativo)
            _repolish(btn)

    def set_editor_dirty(self, dirty: bool) -> None:
        """Liga/desliga a bolinha de alteração não salva no botão Editor."""
        self._dot.setVisible(dirty)
        if dirty:
            self._position_dot()

    def _position_dot(self) -> None:
        btn = self._botoes[EDITOR]
        self._dot.move(btn.width() - 16, 8)

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802 (Qt override)
        super().resizeEvent(event)
        self._position_dot()
