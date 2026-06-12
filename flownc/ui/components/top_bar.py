"""TopBar: topo global do v4, presente em todas as telas.

Contém a marca FlowNC, o seletor de configuração/receita (um ``QComboBox`` com o
item de ação "💾 Salvar lote atual como…" no fim) e o chip de backup clicável que
mostra a pasta de destino dos backups. A lógica fina (carregar receita com
confirmação, salvar, trocar a pasta de backup) é ligada nos Blocos 11/Fase 3 — aqui
ficam só os sinais e a estrutura visual.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui import theme

# Texto do item de ação no fim do seletor de receitas.
ITEM_SALVAR = "Salvar lote atual como…"


class TopBar(QWidget):
    """Topo global: marca + seletor de receita + chip de backup."""

    receita_alterada = Signal(str)
    salvar_receita_solicitado = Signal()
    backup_clicado = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("TopBar")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedHeight(theme.DIM_TOP)
        self._backup_path = ""
        self._build_ui()

    def _build_ui(self) -> None:
        lay = QHBoxLayout(self)
        lay.setContentsMargins(theme.SP_16, 0, theme.SP_16, 0)
        lay.setSpacing(theme.SP_12)

        # Marca (nome + subtítulo)
        brand = QVBoxLayout()
        brand.setSpacing(0)
        nome = QLabel("FlowNC")
        nome.setObjectName("TopBrandName")
        brand.addWidget(nome)
        sub = QLabel("Editor de Lotes")
        sub.setObjectName("TopBrandSub")
        brand.addWidget(sub)
        lay.addLayout(brand)

        # Seletor de configuração/receita
        self.cb_receita = QComboBox()
        self.cb_receita.setObjectName("CfgSelect")
        self.cb_receita.setMinimumWidth(220)
        self.cb_receita.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cb_receita.addItem(ITEM_SALVAR)
        self.cb_receita.activated.connect(self._on_receita_activated)
        lay.addWidget(self.cb_receita)

        lay.addStretch(1)

        # Chip de backup clicável
        self.btn_backup = QPushButton()
        self.btn_backup.setObjectName("ChipBackup")
        self.btn_backup.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_backup.clicked.connect(self.backup_clicado.emit)
        lay.addWidget(self.btn_backup)
        self.set_backup_path("D:\\CNC\\backup\\")

    def _on_receita_activated(self, _index: int) -> None:
        texto = self.cb_receita.currentText()
        if texto == ITEM_SALVAR:
            self.salvar_receita_solicitado.emit()
        elif texto:
            self.receita_alterada.emit(texto)

    def set_receitas(self, nomes: list[str]) -> None:
        """Preenche o seletor com as receitas + o item de ação 'Salvar lote atual como…'."""
        self.cb_receita.blockSignals(True)
        self.cb_receita.clear()
        self.cb_receita.addItems(nomes)
        self.cb_receita.insertSeparator(self.cb_receita.count())
        self.cb_receita.addItem(ITEM_SALVAR)
        self.cb_receita.blockSignals(False)

    def set_backup_path(self, caminho: str) -> None:
        self._backup_path = caminho
        self.btn_backup.setText(f"backup: {caminho} · mudar")
