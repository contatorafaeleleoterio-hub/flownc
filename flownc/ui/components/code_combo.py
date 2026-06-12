"""CodeCombo — combo editável de código com placeholder e seta unicode.

Widget reutilizado em todos os campos de código do app (origem/destino do
compositor e localizar/substituir do editor). Mostra o texto-guia
"Selecione o código" quando vazio e desenha uma seta ▾ à direita que inverte
para ▴ enquanto a lista está aberta, dando resposta visual ao clique.
"""
from __future__ import annotations

from PySide6.QtGui import QPainter
from ui.icons import icon_pixmap
from PySide6.QtWidgets import (
    QComboBox,
    QStyle,
    QStyleOptionComboBox,
    QWidget,
)


class CodeCombo(QComboBox):
    """Combo editável: placeholder + seta unicode que inverte ao abrir."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("CodeCombo")
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        line = self.lineEdit()
        if line is not None:  # editable=True garante o lineEdit; guard p/ mypy
            line.setPlaceholderText("Selecione o código")
        self._popup_open = False

    def showPopup(self) -> None:
        self._popup_open = True
        self.update()
        super().showPopup()

    def hidePopup(self) -> None:
        super().hidePopup()
        self._popup_open = False
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        super().paintEvent(event)
        opt = QStyleOptionComboBox()
        self.initStyleOption(opt)
        rect = self.style().subControlRect(
            QStyle.ComplexControl.CC_ComboBox, opt,
            QStyle.SubControl.SC_ComboBoxArrow, self)
        if rect.isValid():
            # Triângulo desenhado (a fonte da UI não tem os glifos ▴/▾).
            pm = icon_pixmap(
                "caret-up" if self._popup_open else "caret-down", 14, "#56616D")
            p = QPainter(self)
            x = rect.x() + (rect.width() - pm.width()) // 2
            y = rect.y() + (rect.height() - pm.height()) // 2
            p.drawPixmap(x, y, pm)
            p.end()
