"""Dialogo de gerenciamento e selecao da biblioteca de codigos (Sessao A)."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from core.library_store import CodeEntry, LibraryError, save_library

_F, _R, _L = range(3)


class LibraryDialog(QDialog):
    """Gerencia (adiciona/remove/salva) a biblioteca de codigos."""

    def __init__(self, entries: list[CodeEntry], library_path: Path, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Gerenciar biblioteca de codigos")
        self.resize(700, 480)
        self._path = library_path
        self._build_ui(entries)

    def _build_ui(self, entries: list[CodeEntry]) -> None:
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel(
            "Cadastre pares Buscar/Trocar reutilizaveis. "
            "Clique em 'Salvar' para persistir as alteracoes."
        ))
        self.tbl = QTableWidget(0, 3)
        self.tbl.setHorizontalHeaderLabels(["Buscar (o que esta)", "Trocar por", "Rotulo"])
        hh = self.tbl.horizontalHeader()
        hh.setSectionResizeMode(_F, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(_R, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(_L, QHeaderView.ResizeMode.ResizeToContents)
        lay.addWidget(self.tbl)

        for e in entries:
            self._add_row(e.find, e.replace, e.label)

        btns = QHBoxLayout()
        ba = QPushButton("+ Adicionar")
        ba.clicked.connect(self._add_empty)
        br = QPushButton("- Remover")
        br.clicked.connect(self._remove_row)
        bs = QPushButton("Salvar biblioteca")
        bs.clicked.connect(self._save)
        btns.addWidget(ba)
        btns.addWidget(br)
        btns.addStretch(1)
        btns.addWidget(bs)
        lay.addLayout(btns)

        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        bb.rejected.connect(self.reject)
        lay.addWidget(bb)

    def _add_row(self, find: str = "", replace: str = "", label: str = "") -> None:
        r = self.tbl.rowCount()
        self.tbl.insertRow(r)
        self.tbl.setItem(r, _F, QTableWidgetItem(find))
        self.tbl.setItem(r, _R, QTableWidgetItem(replace))
        self.tbl.setItem(r, _L, QTableWidgetItem(label))
        if not find:
            self.tbl.setCurrentCell(r, _F)
            self.tbl.editItem(self.tbl.item(r, _F))

    def _add_empty(self) -> None:
        self._add_row()

    def _remove_row(self) -> None:
        if self.tbl.currentRow() >= 0:
            self.tbl.removeRow(self.tbl.currentRow())

    def _save(self) -> None:
        entries = self._read_entries()
        try:
            save_library(self._path, entries)
            QMessageBox.information(self, "Salvo", f"{len(entries)} entrada(s) salvas.")
        except (LibraryError, OSError) as exc:
            QMessageBox.critical(self, "Erro ao salvar", str(exc))

    def _read_entries(self) -> list[CodeEntry]:
        out: list[CodeEntry] = []
        for r in range(self.tbl.rowCount()):
            find = (self.tbl.item(r, _F).text() if self.tbl.item(r, _F) else "").strip()
            replace = self.tbl.item(r, _R).text() if self.tbl.item(r, _R) else ""
            label = self.tbl.item(r, _L).text() if self.tbl.item(r, _L) else ""
            if find:
                out.append(CodeEntry(find=find, replace=replace, label=label))
        return out

    def current_entries(self) -> list[CodeEntry]:
        """Retorna as entradas atuais da tabela (inclusive nao salvas)."""
        return self._read_entries()


class LibraryPickerDialog(QDialog):
    """Seleciona uma ou mais entradas da biblioteca para inserir na tabela de trocas."""

    def __init__(self, entries: list[CodeEntry], parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Inserir da biblioteca")
        self.resize(520, 380)
        self.selected: list[CodeEntry] = []
        self._entries = entries
        self._build_ui()

    def _build_ui(self) -> None:
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("Filtre e selecione os codigos a inserir (Ctrl+clique para multiplos):"))

        self.search = QLineEdit()
        self.search.setPlaceholderText("Buscar na biblioteca...")
        self.search.textChanged.connect(self._filter)
        lay.addWidget(self.search)

        self.lst = QListWidget()
        self.lst.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.lst.itemDoubleClicked.connect(self._accept_selection)
        lay.addWidget(self.lst, stretch=1)

        self._populate(self._entries)

        bb = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        bb.accepted.connect(self._accept_selection)
        bb.rejected.connect(self.reject)
        lay.addWidget(bb)

    def _populate(self, entries: list[CodeEntry]) -> None:
        self.lst.clear()
        for e in entries:
            label = f"{e.label}  " if e.label else ""
            text = f"{label}'{e.find}'  →  '{e.replace}'"
            it = QListWidgetItem(text)
            it.setData(Qt.ItemDataRole.UserRole, e)
            self.lst.addItem(it)

    def _filter(self, query: str) -> None:
        q = query.lower()
        filtered = [
            e for e in self._entries
            if q in e.find.lower() or q in e.replace.lower() or q in e.label.lower()
        ] if q else self._entries
        self._populate(filtered)

    def _accept_selection(self) -> None:
        self.selected = [
            it.data(Qt.ItemDataRole.UserRole)
            for it in self.lst.selectedItems()
        ]
        if self.selected:
            self.accept()
