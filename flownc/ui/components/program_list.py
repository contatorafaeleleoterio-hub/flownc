"""ProgramListPanel: painel 2 do mockup aprovado."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class _ProgramRow(QWidget):
    def __init__(self, path: Path, edit_callback, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.path = path
        lay = QHBoxLayout(self)
        lay.setContentsMargins(8, 4, 8, 4)
        self.chk = QCheckBox()
        self.chk.setChecked(True)
        lay.addWidget(self.chk)

        text_box = QVBoxLayout()
        self.lbl_name = QLabel(path.name)
        self.lbl_name.setObjectName("ProgramName")
        text_box.addWidget(self.lbl_name)
        meta = QLabel(_file_meta(path))
        meta.setProperty("tertiary", True)
        text_box.addWidget(meta)
        lay.addLayout(text_box, stretch=1)

        self.btn_edit = QPushButton("✎ Editar")
        self.btn_edit.setProperty("interactive", True)
        self.btn_edit.clicked.connect(lambda: edit_callback(str(path)))
        lay.addWidget(self.btn_edit)

    def is_checked(self) -> bool:
        return self.chk.isChecked()


def _file_meta(path: Path) -> str:
    try:
        stat = path.stat()
    except OSError:
        return "arquivo indisponível"
    size_kb = max(1, round(stat.st_size / 1024))
    when = datetime.fromtimestamp(stat.st_mtime).strftime("%d/%m/%Y %H:%M")
    return f"{size_kb} KB · {when}"


class ProgramListPanel(QWidget):
    """Lista de programas com checkbox, metadados e botao Editar por linha."""

    editar_arquivo = Signal(str)
    adicionar_programas_solicitado = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("ProgramListPanel")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)

        head = QHBoxLayout()
        title = QLabel("2  Programas")
        title.setProperty("heading", True)
        head.addWidget(title)
        head.addStretch(1)
        self.btn_add = QPushButton("+ Adicionar programa(s)…")
        self.btn_add.clicked.connect(self.adicionar_programas_solicitado.emit)
        head.addWidget(self.btn_add)
        root.addLayout(head)

        self.lbl_match = QLabel("✓ Regra em edição — marque os programas que vão receber esta regra.")
        self.lbl_match.setObjectName("MatchBanner")
        root.addWidget(self.lbl_match)

        self.lst_prog = QListWidget()
        self.lst_prog.itemDoubleClicked.connect(lambda item: self._emit_edit_for_item(item))
        root.addWidget(self.lst_prog, stretch=1)

    def _emit_edit_for_item(self, item: QListWidgetItem | None) -> None:
        if item is None:
            return
        path = item.data(Qt.ItemDataRole.UserRole)
        if path:
            self.editar_arquivo.emit(str(path))

    def _emit_edit_for_path(self, path: str) -> None:
        self.editar_arquivo.emit(path)

    def set_programs(self, paths: list[Path]) -> None:
        self.lst_prog.clear()
        for path in paths:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, str(path))
            item.setSizeHint(QSize(0, 58))
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked)
            self.lst_prog.addItem(item)
            row = _ProgramRow(path, self._emit_edit_for_path)
            row.chk.stateChanged.connect(
                lambda state, it=item: it.setCheckState(
                    Qt.CheckState.Checked if state else Qt.CheckState.Unchecked
                )
            )
            self.lst_prog.setItemWidget(item, row)
        if paths:
            self.lst_prog.setCurrentRow(0)

    def get_selecionados(self) -> list[Path]:
        out: list[Path] = []
        for idx in range(self.lst_prog.count()):
            item = self.lst_prog.item(idx)
            row = self.lst_prog.itemWidget(item)
            checked = row.is_checked() if isinstance(row, _ProgramRow) else (
                item.checkState() is Qt.CheckState.Checked
            )
            if checked:
                out.append(Path(item.data(Qt.ItemDataRole.UserRole)))
        return out
