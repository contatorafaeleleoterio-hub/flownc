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

        # Logo + marca
        brand = QVBoxLayout()
        brand.setSpacing(2)
        self.lbl_logo = QLabel("FlowNC")
        self.lbl_logo.setObjectName("Logo")
        brand.addWidget(self.lbl_logo)
        sub = QLabel("EDITOR DE LOTES")
        sub.setObjectName("BrandSub")
        brand.addWidget(sub)
        lay.addLayout(brand)

        # separador visual
        vline = QLabel()
        vline.setObjectName("VLine")
        vline.setFixedWidth(1)
        lay.addWidget(vline)

        # Perfil + Salvar perfil (esquerda, juntos)
        profile_area = QHBoxLayout()
        profile_area.setSpacing(8)

        profile_col = QVBoxLayout()
        profile_col.setSpacing(2)
        lbl_perfil = QLabel("Perfil")
        lbl_perfil.setObjectName("LabelCaps")
        profile_col.addWidget(lbl_perfil)
        self.cb_preset = QComboBox()
        self.cb_preset.setMinimumWidth(180)
        self.cb_preset.currentTextChanged.connect(self._on_preset_text_changed)
        profile_col.addWidget(self.cb_preset)
        profile_area.addLayout(profile_col)

        self.btn_save_profile = QPushButton("Salvar perfil")
        self.btn_save_profile.clicked.connect(self.salvar_perfil_solicitado.emit)
        profile_area.addWidget(self.btn_save_profile)
        lay.addLayout(profile_area)

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
