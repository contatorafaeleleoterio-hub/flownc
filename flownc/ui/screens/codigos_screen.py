"""Tela Códigos (mockup v4): biblioteca de códigos da máquina.

Lista código + descrição com busca e contador ("N cadastrados"). "+ Adicionar
código" cadastra um par código/descrição e, opcionalmente, um **bloco** (várias
linhas) — esses viram modelos reutilizáveis no "➕ Inserir bloco" (compositor e
editor) e ganham a tag "bloco" na lista. Persistência via `core.library_store`.

Modelo de dados: um código com bloco é um `CodeEntry` com a tag "bloco" e o texto
do bloco em `replace`; o nome é `find` e a descrição é `label`.
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

import app_paths
from core.library_store import CodeEntry, LibraryError, save_library

TAG_BLOCO = "bloco"


def tem_bloco(entry: CodeEntry) -> bool:
    return TAG_BLOCO in entry.tags and bool(entry.replace)


class _AddCodeDialog(QDialog):
    """Diálogo de cadastro: código, descrição e bloco opcional."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Adicionar código")
        self.setModal(True)
        self.setMinimumWidth(420)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(12)

        lay.addWidget(self._caps("CÓDIGO"))
        self.ed_code = QLineEdit()
        self.ed_code.setPlaceholderText("ex.: G54")
        lay.addWidget(self.ed_code)

        lay.addWidget(self._caps("DESCRIÇÃO"))
        self.ed_desc = QLineEdit()
        self.ed_desc.setPlaceholderText("ex.: Origem de peça 1")
        lay.addWidget(self.ed_desc)

        lay.addWidget(self._caps("BLOCO (OPCIONAL — UMA INSTRUÇÃO POR LINHA)"))
        self.ed_block = QPlainTextEdit()
        self.ed_block.setObjectName("InsText")
        self.ed_block.setPlaceholderText("Várias linhas viram um modelo de “Inserir bloco”.\nex.:\nG43 H01\nM8")
        self.ed_block.setFixedHeight(96)
        lay.addWidget(self.ed_block)

        botoes = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        botoes.accepted.connect(self._validar)
        botoes.rejected.connect(self.reject)
        lay.addWidget(botoes)

    @staticmethod
    def _caps(texto: str) -> QLabel:
        lbl = QLabel(texto)
        lbl.setObjectName("LabelCaps")
        return lbl

    def _validar(self) -> None:
        if not self.ed_code.text().strip():
            self.ed_code.setFocus()
            return
        self.accept()

    def resultado(self) -> CodeEntry:
        bloco = self.ed_block.toPlainText().rstrip()
        return CodeEntry(
            find=self.ed_code.text().strip(),
            replace=bloco,
            label=self.ed_desc.text().strip(),
            tags=[TAG_BLOCO] if bloco else [],
        )


class CodigosScreen(QWidget):
    """Tela-lugar 'Códigos' (índice 2 do QStackedWidget)."""

    biblioteca_alterada = Signal(list)  # list[CodeEntry]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("CodigosScreen")
        self._entries: list[CodeEntry] = []
        self._filtro = ""
        self._rows: list[QWidget] = []
        self._build()

    # ============ construção ============
    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        head = QHBoxLayout()
        head.setSpacing(12)
        titulo = QLabel("Biblioteca de códigos")
        titulo.setObjectName("PTitle")
        head.addWidget(titulo)
        self._contador = QLabel()
        self._contador.setObjectName("ProgChip")
        head.addWidget(self._contador)
        head.addStretch(1)
        self._busca = QLineEdit()
        self._busca.setPlaceholderText("Procurar código ou descrição…")
        self._busca.setClearButtonEnabled(True)
        self._busca.setFixedWidth(260)
        self._busca.textChanged.connect(self._on_busca)
        head.addWidget(self._busca)
        btn_add = QPushButton("+ Adicionar código")
        btn_add.setObjectName("EmptyCTA")
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.clicked.connect(self._on_adicionar)
        head.addWidget(btn_add)
        root.addLayout(head)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        host = QWidget()
        self._lay = QVBoxLayout(host)
        self._lay.setContentsMargins(0, 0, 0, 0)
        self._lay.setSpacing(6)
        self._lay.addStretch(1)
        self._scroll.setWidget(host)
        root.addWidget(self._scroll, stretch=1)

    # ============ API pública ============
    def set_library(self, entries: list[CodeEntry]) -> None:
        self._entries = list(entries)
        self._rebuild()

    def get_modelos(self) -> list[tuple[str, str, str]]:
        """Modelos de bloco: (nome, descrição, texto) para os chips de inserir."""
        return [
            (e.find, e.label or e.find, e.replace)
            for e in self._entries if tem_bloco(e)
        ]

    # ============ interno ============
    def _on_busca(self, texto: str) -> None:
        self._filtro = texto.strip().lower()
        self._rebuild()

    def _filtrados(self) -> list[CodeEntry]:
        if not self._filtro:
            return self._entries
        q = self._filtro
        return [
            e for e in self._entries
            if q in e.find.lower() or q in e.label.lower()
        ]

    def _rebuild(self) -> None:
        for row in self._rows:
            row.setParent(None)
            row.deleteLater()
        self._rows = []
        itens = self._filtrados()
        for entry in itens:
            row = self._build_row(entry)
            self._lay.insertWidget(self._lay.count() - 1, row)
            self._rows.append(row)
        total = len(self._entries)
        plural = "" if total == 1 else "s"
        texto = f"{total} código{plural} cadastrado{plural}"
        if self._filtro:
            texto += f" · {len(itens)} no filtro"
        self._contador.setText(texto)

    def _build_row(self, entry: CodeEntry) -> QWidget:
        row = QFrame()
        row.setObjectName("LibRow")
        row.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        lay = QHBoxLayout(row)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(12)
        code = QLabel(entry.find)
        code.setObjectName("LibCode")
        code.setFixedWidth(90)
        lay.addWidget(code)
        desc = QLabel(entry.label or "—")
        desc.setObjectName("LibDesc")
        lay.addWidget(desc, stretch=1)
        if tem_bloco(entry):
            tag = QLabel("bloco")
            tag.setObjectName("LibBlk")
            tag.setToolTip(entry.replace)
            lay.addWidget(tag)
        btn = QPushButton("✕")
        btn.setObjectName("RowFileX")
        btn.setFixedSize(28, 28)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setToolTip("Remover da biblioteca")
        btn.clicked.connect(lambda _=False, e=entry: self._on_remover(e))
        lay.addWidget(btn)
        return row

    def _on_adicionar(self) -> None:
        dlg = _AddCodeDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        novo = dlg.resultado()
        self._entries = [e for e in self._entries if e.find != novo.find]
        self._entries.append(novo)
        self._persistir()
        self._rebuild()
        self.biblioteca_alterada.emit(list(self._entries))

    def _on_remover(self, entry: CodeEntry) -> None:
        self._entries = [e for e in self._entries if e.find != entry.find]
        self._persistir()
        self._rebuild()
        self.biblioteca_alterada.emit(list(self._entries))

    def _persistir(self) -> None:
        path: Path = app_paths.library_path()
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            save_library(path, self._entries)
        except (LibraryError, OSError):
            pass  # falha de gravação não derruba a UI; estado em memória mantido
