"""ProgramListV4: painel Programas da tela Lote (mockup v4).

Lista de programas marcáveis com colunas (✓ | Nome mono | Modificado | Tamanho |
✎ Abrir | ✕), chip "N de M marcados", botão "Marcar todos / Desmarcar todos",
arrastar-e-soltar de arquivos e estado vazio com CTA "+ Adicionar programa(s)…".

FASE 2: os dados vêm dos arquivos que o operador solta/adiciona (nome, data e
tamanho lidos do sistema de arquivos). A ligação ao núcleo (varredura/conferência)
é da Fase 3.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import (
    QDragEnterEvent,
    QDragLeaveEvent,
    QDropEvent,
    QMouseEvent,
)
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

# Extensões reconhecidas como programas CNC (para o filtro do diálogo).
_CNC_EXTS = (
    "*.nc *.txt *.iso *.ptp *.min *.mpf *.cnc *.prg *.eia *.tap *.gcode "
    "*.ngc *.spf *.h *.pgm *.din *.dnc"
)
_COL_MOD = 116
_COL_SIZE = 84


def _repolish(w: QWidget) -> None:
    style = w.style()
    style.unpolish(w)
    style.polish(w)


def _fmt_size(path: Path) -> str:
    try:
        n = path.stat().st_size
    except OSError:
        return "—"
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n / 1024:.1f} KB"
    return f"{n / (1024 * 1024):.1f} MB"


def _fmt_mtime(path: Path) -> str:
    try:
        ts = path.stat().st_mtime
    except OSError:
        return "—"
    return datetime.fromtimestamp(ts).strftime("%d/%m/%Y %H:%M")


class _FileRow(QFrame):
    """Uma linha da lista — clicar em qualquer ponto (fora dos botões) marca/desmarca."""

    toggled = Signal()
    abrir = Signal()
    remover = Signal()

    def __init__(self, path: Path, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("FileRow")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(50)
        self._path = path
        self._marcado = False
        self._build()
        self._sync()

    def _build(self) -> None:
        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 0, 12, 0)
        lay.setSpacing(12)

        self._chk = QLabel()
        self._chk.setObjectName("Chk")
        self._chk.setFixedSize(20, 20)
        self._chk.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._name = QLabel(self._path.name)
        self._name.setObjectName("FName")

        self._mod = QLabel(_fmt_mtime(self._path))
        self._mod.setObjectName("FCol")
        self._mod.setFixedWidth(_COL_MOD)

        self._size = QLabel(_fmt_size(self._path))
        self._size.setObjectName("FCol")
        self._size.setFixedWidth(_COL_SIZE)

        for lbl in (self._chk, self._name, self._mod, self._size):
            lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        self._btn_abrir = QPushButton("✎ Abrir")
        self._btn_abrir.setObjectName("RowEditBtn")
        self._btn_abrir.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_abrir.clicked.connect(self.abrir.emit)

        self._btn_x = QPushButton("✕")
        self._btn_x.setObjectName("RowFileX")
        self._btn_x.setFixedSize(32, 32)
        self._btn_x.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_x.clicked.connect(self.remover.emit)

        lay.addWidget(self._chk)
        lay.addWidget(self._name, stretch=1)
        lay.addWidget(self._mod)
        lay.addWidget(self._size)
        lay.addWidget(self._btn_abrir)
        lay.addWidget(self._btn_x)

    @property
    def path(self) -> Path:
        return self._path

    @property
    def marcado(self) -> bool:
        return self._marcado

    def set_marcado(self, valor: bool) -> None:
        self._marcado = valor
        self._sync()

    def _sync(self) -> None:
        self.setProperty("marcado", self._marcado)
        self._chk.setProperty("marcado", self._marcado)
        self._chk.setText("✓" if self._marcado else "")
        _repolish(self)
        _repolish(self._chk)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802 (Qt override)
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggled.emit()
        super().mousePressEvent(event)


class ProgramListV4(QWidget):
    """Painel Programas: lista marcável + chip + ações + estado vazio + D&D."""

    selecao_alterada = Signal()
    abrir_arquivo = Signal(str)
    programas_alterados = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("ProgramListV4")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAcceptDrops(True)
        self._paths: list[Path] = []
        self._rows: list[_FileRow] = []
        self._build()
        self._refresh()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # Cabeçalho: título + chip + ações
        phead = QHBoxLayout()
        phead.setSpacing(12)
        titulo = QLabel("Programas")
        titulo.setObjectName("PTitle")
        phead.addWidget(titulo)
        self._chip = QLabel()
        self._chip.setObjectName("ProgChip")
        phead.addWidget(self._chip)
        phead.addStretch(1)
        self._btn_all = QPushButton("Marcar todos")
        self._btn_all.setObjectName("GhostBtnV4")
        self._btn_all.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_all.clicked.connect(self._toggle_all)
        phead.addWidget(self._btn_all)
        btn_add = QPushButton("+ Adicionar programa(s)…")
        btn_add.setObjectName("GhostBtnV4")
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.clicked.connect(self._abrir_dialogo)
        phead.addWidget(btn_add)
        root.addLayout(phead)

        # Cabeçalho de colunas
        self._head = QWidget()
        self._head.setObjectName("FilesHead")
        head_lay = QHBoxLayout(self._head)
        head_lay.setContentsMargins(12, 4, 12, 4)
        head_lay.setSpacing(12)
        lbl_chk = QLabel("")
        lbl_chk.setFixedWidth(20)
        lbl_nome = QLabel("Nome")
        lbl_mod = QLabel("Modificado")
        lbl_mod.setFixedWidth(_COL_MOD)
        lbl_size = QLabel("Tamanho")
        lbl_size.setFixedWidth(_COL_SIZE)
        head_lay.addWidget(lbl_chk)
        head_lay.addWidget(lbl_nome, stretch=1)
        head_lay.addWidget(lbl_mod)
        head_lay.addWidget(lbl_size)
        root.addWidget(self._head)

        # Lista (scroll) — uma linha por programa
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._list_host = QWidget()
        self._list_lay = QVBoxLayout(self._list_host)
        self._list_lay.setContentsMargins(0, 0, 0, 0)
        self._list_lay.setSpacing(8)
        self._list_lay.addStretch(1)
        self._scroll.setWidget(self._list_host)
        root.addWidget(self._scroll, stretch=1)

        # Estado vazio
        self._empty = self._build_empty()
        root.addWidget(self._empty, stretch=1)

    def _build_empty(self) -> QWidget:
        box = QFrame()
        box.setObjectName("EmptyState")
        lay = QVBoxLayout(box)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.setSpacing(12)
        ic = QLabel("📂")
        ic.setObjectName("EmptyIcon")
        ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t1 = QLabel("Nenhum programa carregado")
        t1.setObjectName("EmptyT1")
        t1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t2 = QLabel("Arraste os arquivos NC aqui ou use o botão abaixo.")
        t2.setObjectName("EmptyT2")
        t2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t2.setWordWrap(True)
        cta = QPushButton("+ Adicionar programas")
        cta.setObjectName("EmptyCTA")
        cta.setCursor(Qt.CursorShape.PointingHandCursor)
        cta.clicked.connect(self._abrir_dialogo)
        lay.addWidget(ic)
        lay.addWidget(t1)
        lay.addWidget(t2)
        lay.addWidget(cta, alignment=Qt.AlignmentFlag.AlignCenter)
        return box

    # ============ API pública ============
    def set_programs(self, paths: list[Path]) -> None:
        self._paths = list(paths)
        self._rebuild_rows()
        self._refresh()

    def add_programs(self, paths: list[Path]) -> None:
        existentes = {str(p.resolve()) for p in self._paths}
        novos = [p for p in paths if str(p.resolve()) not in existentes]
        if not novos:
            return
        self._paths.extend(novos)
        self._rebuild_rows()
        self._refresh()
        self.programas_alterados.emit()

    def get_marcados(self) -> list[Path]:
        return [r.path for r in self._rows if r.marcado]

    def get_paths(self) -> list[Path]:
        return list(self._paths)

    # ============ interno ============
    def _rebuild_rows(self) -> None:
        for row in self._rows:
            row.setParent(None)
            row.deleteLater()
        self._rows = []
        for path in self._paths:
            row = _FileRow(path)
            row.toggled.connect(lambda r=row: self._on_row_toggled(r))
            row.abrir.connect(lambda r=row: self.abrir_arquivo.emit(str(r.path)))
            row.remover.connect(lambda r=row: self._on_row_removida(r))
            self._list_lay.insertWidget(self._list_lay.count() - 1, row)
            self._rows.append(row)

    def _on_row_toggled(self, row: _FileRow) -> None:
        row.set_marcado(not row.marcado)
        self._update_chip()
        self.selecao_alterada.emit()

    def _on_row_removida(self, row: _FileRow) -> None:
        self._paths = [p for p in self._paths if p is not row.path]
        self._rebuild_rows()
        self._refresh()
        self.programas_alterados.emit()
        self.selecao_alterada.emit()

    def _toggle_all(self) -> None:
        marcar = not (self._rows and all(r.marcado for r in self._rows))
        for row in self._rows:
            row.set_marcado(marcar)
        self._update_chip()
        self.selecao_alterada.emit()

    def _refresh(self) -> None:
        tem = bool(self._paths)
        self._scroll.setVisible(tem)
        self._head.setVisible(tem)
        self._empty.setVisible(not tem)
        self._update_chip()

    def _update_chip(self) -> None:
        total = len(self._rows)
        marcados = sum(1 for r in self._rows if r.marcado)
        self._chip.setText(f"{marcados} de {total} marcados")
        todos = total > 0 and marcados == total
        self._btn_all.setText("Desmarcar todos" if todos else "Marcar todos")
        self._btn_all.setEnabled(total > 0)

    def _abrir_dialogo(self) -> None:
        arquivos, _ = QFileDialog.getOpenFileNames(
            self,
            "Escolher programa(s) NC",
            "",
            f"Programas CNC ({_CNC_EXTS});;Todos os arquivos (*.*)",
        )
        if arquivos:
            self.add_programs([Path(a) for a in arquivos])

    # ============ arrastar-e-soltar ============
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:  # noqa: N802
        if event.mimeData().hasUrls():
            self.setProperty("dragover", True)
            _repolish(self)
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event: QDragLeaveEvent) -> None:  # noqa: N802
        self.setProperty("dragover", False)
        _repolish(self)
        super().dragLeaveEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:  # noqa: N802
        self.setProperty("dragover", False)
        _repolish(self)
        paths = [
            Path(url.toLocalFile())
            for url in event.mimeData().urls()
            if url.isLocalFile() and url.toLocalFile()
        ]
        arquivos = [p for p in paths if p.is_file()]
        if arquivos:
            self.add_programs(arquivos)
            event.acceptProposedAction()
        else:
            event.ignore()
