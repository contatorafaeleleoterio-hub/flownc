"""Dialogo de preview/diff antes de salvar (PRD secao 11.4).

Recebe itens ja formatados pela janela principal e apenas exibe + confirma.
Salvar fica desabilitado se houver erro estrutural critico (secao 11.7).
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

_GREEN = QColor(225, 245, 225)
_YELLOW = QColor(255, 247, 205)
_RED = QColor(250, 220, 220)


class PreviewDialog(QDialog):
    def __init__(
        self,
        summary: str,
        items: list[tuple[str, str, str]],  # (nome, severidade, detalhe)
        blocked: bool,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.confirmed = False
        self.setWindowTitle("Preview — revise antes de salvar")
        self.resize(900, 600)

        root = QVBoxLayout(self)
        split = QSplitter(Qt.Orientation.Horizontal)

        self.lst = QListWidget()
        self.lst.setMinimumWidth(240)
        resume = QListWidgetItem("== RESUMO ==")
        resume.setData(Qt.ItemDataRole.UserRole, summary)
        self.lst.addItem(resume)
        for nome, sev, detalhe in items:
            it = QListWidgetItem(nome)
            it.setData(Qt.ItemDataRole.UserRole, detalhe)
            it.setBackground(_RED if sev == "critical" else _YELLOW if sev == "warning" else _GREEN)
            self.lst.addItem(it)
        self.lst.currentItemChanged.connect(self._show)
        split.addWidget(self.lst)

        self.txt = QPlainTextEdit()
        self.txt.setReadOnly(True)
        self.txt.setFont(QFont("Consolas", 10))
        split.addWidget(self.txt)
        split.setStretchFactor(1, 1)
        root.addWidget(split, stretch=1)

        btns = QHBoxLayout()
        if blocked:
            lbl = QLabel("SALVAR BLOQUEADO: ha erro estrutural critico (vermelho).")
            lbl.setStyleSheet("color:#a00; font-weight:bold;")
            btns.addWidget(lbl)
        btns.addStretch(1)
        self.btn_save = QPushButton("Confirmar e salvar")
        self.btn_save.setEnabled(not blocked)
        self.btn_save.clicked.connect(self._confirm)
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(self.btn_save)
        btns.addWidget(btn_cancel)
        root.addLayout(btns)

        self.lst.setCurrentRow(0)

    def _show(self, item: QListWidgetItem | None) -> None:
        if item is not None:
            self.txt.setPlainText(item.data(Qt.ItemDataRole.UserRole))

    def _confirm(self) -> None:
        self.confirmed = True
        self.accept()
