"""HeaderBar: barra superior fixa do FlowNC (FASE 2 — fidelidade ao mockup)."""
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


class HeaderBar(QWidget):
    """Cabecalho com marca FlowNC, perfil e acoes globais conforme mockup aprovado."""

    perfil_alterado = Signal(str)
    biblioteca_solicitada = Signal()
    adicionar_codigo_solicitado = Signal()
    salvar_perfil_solicitado = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("HeaderBar")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._build_ui()

    def _build_ui(self) -> None:
        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 0, 16, 0)
        lay.setSpacing(16)

        # Logo (badge redondo) + marca
        brand = QHBoxLayout()
        brand.setSpacing(8)
        logo_badge = QLabel("◉")
        logo_badge.setObjectName("LogoBadge")
        logo_badge.setFixedSize(38, 38)
        logo_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand.addWidget(logo_badge)
        brand_text = QVBoxLayout()
        brand_text.setSpacing(2)
        self.lbl_logo = QLabel("FlowNC")
        self.lbl_logo.setObjectName("Logo")
        brand_text.addWidget(self.lbl_logo)
        sub = QLabel("EDITOR DE LOTES")
        sub.setObjectName("BrandSub")
        brand_text.addWidget(sub)
        brand.addLayout(brand_text)
        lay.addLayout(brand)

        # separador visual
        vline = QLabel()
        vline.setObjectName("VLine")
        vline.setFixedWidth(1)
        lay.addWidget(vline)

        # Seletor de maquina (pilula com nome + caret) + Salvar perfil
        self.cb_preset = QComboBox()
        self.cb_preset.setMinimumWidth(200)
        self.cb_preset.currentTextChanged.connect(self._on_preset_text_changed)
        lay.addWidget(self.cb_preset)

        self.btn_save_profile = QPushButton("Salvar perfil")
        self.btn_save_profile.clicked.connect(self.salvar_perfil_solicitado.emit)
        lay.addWidget(self.btn_save_profile)

        lay.addStretch(1)

        # Biblioteca de Codes
        self.btn_library = QPushButton("Biblioteca de Códigos")
        self.btn_library.clicked.connect(self.biblioteca_solicitada.emit)
        lay.addWidget(self.btn_library)

        # + Adicionar codigo (azul solido)
        self.btn_add_code = QPushButton("+ Adicionar código")
        self.btn_add_code.setObjectName("BtnInteractive")
        self.btn_add_code.clicked.connect(self.adicionar_codigo_solicitado.emit)
        lay.addWidget(self.btn_add_code)

    def _on_preset_text_changed(self, nome: str) -> None:
        if nome:
            self.perfil_alterado.emit(nome)

    def set_presets(self, nomes: list[str]) -> None:
        self.cb_preset.blockSignals(True)
        self.cb_preset.clear()
        self.cb_preset.addItems(nomes)
        self.cb_preset.blockSignals(False)

    def set_preset_atual(self, nome: str) -> None:
        idx = self.cb_preset.findText(nome)
        if idx < 0:
            return
        self.cb_preset.blockSignals(True)
        self.cb_preset.setCurrentIndex(idx)
        self.cb_preset.blockSignals(False)
