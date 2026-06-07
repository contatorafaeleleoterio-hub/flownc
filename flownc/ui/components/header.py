"""HeaderBar: barra superior fixa do FlowNC."""
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
    """Cabecalho com marca, perfil e acoes globais do mockup aprovado."""

    perfil_alterado = Signal(str)
    abrir_pasta_solicitado = Signal()
    abrir_arquivos_solicitado = Signal()
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

        brand = QVBoxLayout()
        self.lbl_logo = QLabel("⚙ FlowNC")
        self.lbl_logo.setObjectName("Logo")
        brand.addWidget(self.lbl_logo)
        sub = QLabel("LOCAL · OFFLINE")
        sub.setProperty("tertiary", True)
        brand.addWidget(sub)
        lay.addLayout(brand)
        lay.addSpacing(16)

        profile = QVBoxLayout()
        label = QLabel("Perfil")
        label.setProperty("tertiary", True)
        profile.addWidget(label)
        self.cb_preset = QComboBox()
        self.cb_preset.setMinimumWidth(200)
        self.cb_preset.currentTextChanged.connect(self._on_preset_text_changed)
        profile.addWidget(self.cb_preset)
        lay.addLayout(profile)

        self.btn_open_folder = QPushButton("Abrir pasta…")
        self.btn_open_folder.clicked.connect(self.abrir_pasta_solicitado.emit)
        lay.addWidget(self.btn_open_folder)

        self.btn_open_files = QPushButton("Abrir programa(s)…")
        self.btn_open_files.clicked.connect(self.abrir_arquivos_solicitado.emit)
        lay.addWidget(self.btn_open_files)

        lay.addStretch(1)

        self.btn_library = QPushButton("Biblioteca de Códigos")
        self.btn_library.clicked.connect(self.biblioteca_solicitada.emit)
        lay.addWidget(self.btn_library)

        self.btn_add_code = QPushButton("+ Adicionar código")
        self.btn_add_code.setProperty("interactive", True)
        self.btn_add_code.clicked.connect(self.adicionar_codigo_solicitado.emit)
        lay.addWidget(self.btn_add_code)

        self.btn_save_profile = QPushButton("Salvar perfil")
        self.btn_save_profile.clicked.connect(self.salvar_perfil_solicitado.emit)
        lay.addWidget(self.btn_save_profile)

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
