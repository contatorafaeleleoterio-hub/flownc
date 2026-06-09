"""ProgramListPanel: painel 2 do mockup aprovado (FASE 2 — fidelidade visual)."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QStyle,
    QStyleOptionButton,
    QVBoxLayout,
    QWidget,
)


def _file_meta(path: Path) -> str:
    """Tamanho humanizado + tempo relativo da ultima modificacao."""
    try:
        stat = path.stat()
    except OSError:
        return "arquivo indisponível"

    # tamanho humanizado
    size = stat.st_size
    if size < 1024:
        size_str = f"{size} B"
    elif size < 1024 * 1024:
        size_str = f"{size / 1024:.1f} KB"
    else:
        size_str = f"{size / (1024 * 1024):.1f} MB"

    # tempo relativo
    mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
    now = datetime.now(tz=timezone.utc)
    delta = now - mtime
    secs = delta.total_seconds()
    if secs < 60:
        rel = "agora"
    elif secs < 3600:
        rel = f"há {int(secs // 60)} min"
    elif secs < 86400:
        rel = f"há {int(secs // 3600)} h"
    elif secs < 86400 * 2:
        rel = "ontem"
    elif secs < 86400 * 7:
        rel = f"há {int(secs // 86400)} dias"
    else:
        rel = mtime.strftime("%d/%m/%Y")

    return f"{size_str} · {rel}"


class _CheckBox(QCheckBox):
    """Checkbox que desenha um ✓ branco quando marcado (em vez de caixa cheia)."""

    def paintEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        super().paintEvent(event)  # caixa (borda/fundo) via QSS
        if not self.isChecked():
            return
        opt = QStyleOptionButton()
        self.initStyleOption(opt)
        rect = self.style().subElementRect(
            QStyle.SubElement.SE_CheckBoxIndicator, opt, self)
        if rect.isValid():
            p = QPainter(self)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            p.setPen(QColor("#FFFFFF"))
            f = p.font()
            f.setPixelSize(12)
            f.setBold(True)
            p.setFont(f)
            p.drawText(rect, Qt.AlignmentFlag.AlignCenter, "✓")
            p.end()


class _ProgramRow(QWidget):
    """Linha de programa: [checkbox] nome + meta  [✎ Editar ou Voltar]  [✕]."""

    edit_clicked = Signal(str)      # path
    remove_clicked = Signal(str)    # path
    check_changed = Signal(str, bool)  # path, checked

    def __init__(self, path: Path, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("ProgramRow")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.path = path
        self._editing = False
        lay = QHBoxLayout(self)
        lay.setContentsMargins(8, 4, 8, 4)
        lay.setSpacing(8)

        # UN checkbox — o item do QListWidget tambem tem checkstate, por isso
        # bloqueamos o setCheckState do item para nao duplicar.
        self.chk = _CheckBox()
        self.chk.setChecked(False)  # inicia desmarcado: usuario opta por incluir
        self.chk.stateChanged.connect(self._on_check_changed)
        self._set_off_style(True)   # visual "fora" coerente com o desmarcado
        lay.addWidget(self.chk)

        text_box = QVBoxLayout()
        text_box.setSpacing(0)
        self.lbl_name = QLabel(path.name)
        self.lbl_name.setObjectName("ProgramName")
        text_box.addWidget(self.lbl_name)
        self.lbl_meta = QLabel(_file_meta(path))
        self.lbl_meta.setProperty("tertiary", True)
        text_box.addWidget(self.lbl_meta)
        lay.addLayout(text_box, stretch=1)

        self.btn_edit = QPushButton("✎ Editar")
        self.btn_edit.setObjectName("EditBtn")
        self.btn_edit.clicked.connect(self._on_edit_clicked)
        lay.addWidget(self.btn_edit)

        self.btn_remove = QPushButton("✕")
        self.btn_remove.setObjectName("FileRemoveBtn")
        self.btn_remove.setFixedSize(28, 28)
        self.btn_remove.setToolTip("Remover da lista")
        self.btn_remove.clicked.connect(lambda: self.remove_clicked.emit(str(self.path)))
        lay.addWidget(self.btn_remove)

    def _on_check_changed(self, state: int) -> None:
        checked = state == Qt.CheckState.Checked.value
        self._set_off_style(not checked)
        self.check_changed.emit(str(self.path), checked)

    def _on_edit_clicked(self) -> None:
        if self._editing:
            self.edit_clicked.emit("__close__")
        else:
            self.edit_clicked.emit(str(self.path))

    def set_editing(self, editing: bool) -> None:
        """Alterna entre 'Editar' e 'Voltar' conforme o estado do editor."""
        self._editing = editing
        if editing:
            self.btn_edit.setText("Voltar")
            self.btn_edit.setObjectName("BackBtn")
        else:
            self.btn_edit.setText("✎ Editar")
            self.btn_edit.setObjectName("EditBtn")
        # reaplica o estilo apos mudar objectName
        self.btn_edit.style().unpolish(self.btn_edit)
        self.btn_edit.style().polish(self.btn_edit)
        self.setProperty("editing", editing)
        self.style().unpolish(self)
        self.style().polish(self)

    def _set_off_style(self, off: bool) -> None:
        self.setProperty("fileOff", off)
        self.style().unpolish(self)
        self.style().polish(self)

    def is_checked(self) -> bool:
        return self.chk.isChecked()


class ProgramListPanel(QWidget):
    """Lista de programas com checkbox, metadados, botao Editar/Voltar e ✕ por linha."""

    editar_arquivo = Signal(str)
    fechar_editor_solicitado = Signal()
    adicionar_programas_solicitado = Signal()
    adicionar_ao_lote_solicitado = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("ProgramListPanel")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._current_editing_path: str | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(8)
        root.setContentsMargins(12, 12, 12, 12)

        # cabecalho
        head = QHBoxLayout()
        head.setSpacing(8)
        znum = QLabel("2")
        znum.setObjectName("ZNum")
        head.addWidget(znum)
        title = QLabel("Seleção de Programas")
        title.setObjectName("ZTitle")
        head.addWidget(title)
        head.addStretch(1)
        self.btn_add = QPushButton("+ Adicionar programa(s)…")
        self.btn_add.setObjectName("GhostBtn")
        self.btn_add.clicked.connect(self.adicionar_programas_solicitado.emit)
        head.addWidget(self.btn_add)
        root.addLayout(head)

        # banner "regra em edicao"
        self.lbl_match = QLabel("✓ Regra em edição — marque os programas que vão receber esta regra.")
        self.lbl_match.setObjectName("MatchBanner")
        root.addWidget(self.lbl_match)

        # lista de programas (ou estado vazio)
        self.lst_prog = QListWidget()
        self.lst_prog.itemDoubleClicked.connect(self._emit_edit_for_item)
        root.addWidget(self.lst_prog, stretch=1)

        # estado vazio (mostrado quando a lista esta vazia)
        self.empty_state = QWidget()
        empty_lay = QVBoxLayout(self.empty_state)
        empty_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_empty = QLabel("Nenhum programa adicionado.")
        lbl_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_empty.setProperty("tertiary", True)
        empty_lay.addWidget(lbl_empty)
        btn_cta = QPushButton("+ Adicionar programa(s)…")
        btn_cta.setObjectName("EmptyCTA")
        btn_cta.clicked.connect(self.adicionar_programas_solicitado.emit)
        empty_lay.addWidget(btn_cta, alignment=Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self.empty_state)
        self.empty_state.hide()

        # CTA azul grande "Adicionar edicao ao lote ->" (rodape da secao 2)
        self.btn_add_rule = QPushButton("Adicionar edição ao lote →")
        self.btn_add_rule.setObjectName("AddRuleBtn")
        self.btn_add_rule.setEnabled(False)
        self.btn_add_rule.clicked.connect(self.adicionar_ao_lote_solicitado.emit)
        root.addWidget(self.btn_add_rule)

    def set_add_enabled(self, enabled: bool) -> None:
        """Habilita o CTA quando ha edicoes prontas para enviar ao lote."""
        self.btn_add_rule.setEnabled(enabled)

    # ---------- emissores ----------

    def _emit_edit_for_item(self, item: QListWidgetItem | None) -> None:
        if item is None:
            return
        path = item.data(Qt.ItemDataRole.UserRole)
        if path:
            self.editar_arquivo.emit(str(path))

    def _on_row_edit_clicked(self, signal: str) -> None:
        if signal == "__close__":
            self.fechar_editor_solicitado.emit()
        else:
            self.editar_arquivo.emit(signal)

    def _on_row_remove_clicked(self, path_str: str) -> None:
        for i in range(self.lst_prog.count()):
            item = self.lst_prog.item(i)
            if item and item.data(Qt.ItemDataRole.UserRole) == path_str:
                self.lst_prog.takeItem(i)
                break
        self._update_empty_state()

    # ---------- API publica ----------

    def set_programs(self, paths: list[Path]) -> None:
        self.lst_prog.clear()
        self._current_editing_path = None
        for path in paths:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, str(path))
            item.setSizeHint(QSize(0, 62))
            # sem checkstate no item (checkbox esta so no widget da linha)
            self.lst_prog.addItem(item)
            row = _ProgramRow(path)
            row.edit_clicked.connect(self._on_row_edit_clicked)
            row.remove_clicked.connect(self._on_row_remove_clicked)
            self.lst_prog.setItemWidget(item, row)
        if paths:
            self.lst_prog.setCurrentRow(0)
        self._update_empty_state()

    def set_editing_path(self, path: str | None) -> None:
        """Marca qual arquivo esta aberto no editor (botao Voltar contextual)."""
        self._current_editing_path = path
        for i in range(self.lst_prog.count()):
            item = self.lst_prog.item(i)
            row = self.lst_prog.itemWidget(item)
            if isinstance(row, _ProgramRow):
                editing = path is not None and item.data(Qt.ItemDataRole.UserRole) == path
                row.set_editing(editing)

    def get_selecionados(self) -> list[Path]:
        out: list[Path] = []
        for idx in range(self.lst_prog.count()):
            item = self.lst_prog.item(idx)
            row = self.lst_prog.itemWidget(item)
            if isinstance(row, _ProgramRow) and row.is_checked():
                out.append(Path(item.data(Qt.ItemDataRole.UserRole)))
        return out

    def _update_empty_state(self) -> None:
        empty = self.lst_prog.count() == 0
        self.lst_prog.setVisible(not empty)
        self.empty_state.setVisible(empty)
