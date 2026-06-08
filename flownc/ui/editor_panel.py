"""Editor de texto integrado por arquivo (mudanca editor-integrado-por-arquivo).

Editor embutido com numeracao de linha, localizador e gravacao in-place segura.
FASE 2: fidelidade visual ao mockup (glifos, realce QSyntaxHighlighter, stepbar inline,
botao Voltar proeminente no topo-esquerdo).

A logica de busca/substituicao mora em funcoes puras de modulo
(`build_find_rule`, `replace_all_spans`, `replace_one_by_one`), testaveis sem GUI
(tests/test_editor_localizador.py). O `EditorPanel` (QWidget) so apresenta e delega.
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QRect, QSize, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QFont,
    QPainter,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextCursor,
    QTextDocument,
)
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.file_handler import read_file
from core.inplace_save import salvar_no_lugar
from core.library_store import CodeEntry
from core.matcher import find_matches
from core.models import EncodingInfo, Mode, Rule

_MAX_LINES_HIGHLIGHT = 5000

# ============ logica pura (testavel sem GUI) ============


def build_find_rule(code: str) -> Rule:
    """Monta uma Rule de busca (mode AUTO -> mesma borda CNC do Lote)."""
    return Rule(id="_find", find=code, replace="", mode=Mode.AUTO)


def count_matches(text: str, code: str, case_sensitive: bool = True) -> list[tuple[int, int]]:
    """Intervalos (start, end) do codigo no texto, identicos aos do Lote."""
    if not code:
        return []
    return find_matches(text, build_find_rule(code), case_sensitive)


def replace_all_spans(text: str, spans: list[tuple[int, int]], replacement: str) -> str:
    """Troca todos os intervalos, de tras para frente (nao invalida offsets)."""
    out = text
    for start, end in sorted(spans, reverse=True):
        out = out[:start] + replacement + out[end:]
    return out


def replace_one_by_one(
    text: str,
    find_code: str,
    replacement: str,
    decisions: list[bool],
    case_sensitive: bool = True,
) -> str:
    """Aplica decisoes (substituir/pular) por ocorrencia, na ordem do texto."""
    spans = count_matches(text, find_code, case_sensitive)
    parts: list[str] = []
    last = 0
    for idx, (start, end) in enumerate(spans):
        decide = decisions[idx] if idx < len(decisions) else False
        parts.append(text[last:start])
        parts.append(replacement if decide else text[start:end])
        last = end
    parts.append(text[last:])
    return "".join(parts)


# ============ highlighter de ocorrencias ============


class OccurrenceHighlighter(QSyntaxHighlighter):
    """Realca todas as ocorrencias de um termo; a ocorrencia atual tem cor distinta."""

    _FMT_ALL = QTextCharFormat()
    _FMT_ALL.setBackground(QColor("#FAEED5"))  # COLOR_OCCURRENCE

    _FMT_CURRENT = QTextCharFormat()
    _FMT_CURRENT.setBackground(QColor("#FBD46A"))  # COLOR_OCCURRENCE_CURRENT

    def __init__(self, document: QTextDocument) -> None:
        super().__init__(document)
        self._term = ""
        self._case_sensitive = True
        self._spans: list[tuple[int, int]] = []
        self._current_span: tuple[int, int] | None = None

    def set_term(self, term: str, spans: list[tuple[int, int]], case_sensitive: bool = True) -> None:
        self._term = term
        self._spans = spans
        self._case_sensitive = case_sensitive
        self._current_span = None
        self.rehighlight()

    def set_current(self, span: tuple[int, int] | None) -> None:
        self._current_span = span
        self.rehighlight()

    def clear_highlight(self) -> None:
        self._term = ""
        self._spans = []
        self._current_span = None
        self.rehighlight()

    def highlightBlock(self, text: str) -> None:  # noqa: N802 (override Qt)
        if not self._spans:
            return
        block_start = self.currentBlock().position()
        block_end = block_start + len(text)
        for start, end in self._spans:
            if end <= block_start or start >= block_end:
                continue
            rel_start = max(0, start - block_start)
            rel_end = min(len(text), end - block_start)
            fmt = self._FMT_CURRENT if (start, end) == self._current_span else self._FMT_ALL
            self.setFormat(rel_start, rel_end - rel_start, fmt)


# ============ editor com numeracao de linha ============


class _LineNumberArea(QWidget):
    def __init__(self, editor: CodeEditor) -> None:
        super().__init__(editor)
        self._editor = editor

    def sizeHint(self) -> QSize:  # noqa: N802 (override Qt)
        return QSize(self._editor.line_number_area_width(), 0)

    def paintEvent(self, event) -> None:  # noqa: N802 (override Qt)
        self._editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    """QPlainTextEdit em fonte mono com gutter de numeracao sincronizado."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFont(QFont("Consolas", 11))
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self._lna = _LineNumberArea(self)
        self.blockCountChanged.connect(lambda _=0: self._update_width())
        self.updateRequest.connect(self._update_area)
        self._update_width()

    def line_number_area_width(self) -> int:
        digits = len(str(max(1, self.blockCount())))
        return 12 + self.fontMetrics().horizontalAdvance("9") * digits

    def _update_width(self) -> None:
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def _update_area(self, rect: QRect, dy: int) -> None:
        if dy:
            self._lna.scroll(0, dy)
        else:
            self._lna.update(0, rect.y(), self._lna.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self._update_width()

    def resizeEvent(self, event) -> None:  # noqa: N802 (override Qt)
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._lna.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def line_number_area_paint_event(self, event) -> None:
        painter = QPainter(self._lna)
        painter.fillRect(event.rect(), QColor("#EEF1F4"))
        block = self.firstVisibleBlock()
        block_num = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())
        line_h = self.fontMetrics().height()
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                painter.setPen(QColor("#9aa3ad"))
                painter.drawText(
                    0, top, self._lna.width() - 4, line_h,
                    int(Qt.AlignmentFlag.AlignRight), str(block_num + 1),
                )
            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_num += 1


# ============ stepbar "Um a um" inline ============


class _StepBar(QWidget):
    """Widget inline para substituicao um-a-um — sem QMessageBox."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("StepBar")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(8, 4, 8, 4)
        lay.setSpacing(8)

        self.lbl_pos = QLabel("0/0")
        self.lbl_pos.setObjectName("StepPos")
        lay.addWidget(self.lbl_pos)

        lay.addStretch(1)

        self.btn_prev = QPushButton("← Anterior")
        self.btn_prev.setFixedHeight(28)
        lay.addWidget(self.btn_prev)

        self.btn_next = QPushButton("→ Próxima")
        self.btn_next.setFixedHeight(28)
        lay.addWidget(self.btn_next)

        self.btn_replace = QPushButton("Substituir")
        self.btn_replace.setFixedHeight(28)
        lay.addWidget(self.btn_replace)

        self.btn_end = QPushButton("Encerrar")
        self.btn_end.setFixedHeight(28)
        lay.addWidget(self.btn_end)

        self.hide()


# ============ painel do editor ============


class EditorPanel(QWidget):
    """Editor por arquivo: abrir, localizar/substituir e salvar in-place."""

    dirtyChanged = Signal(bool)
    closeRequested = Signal()

    def __init__(
        self,
        library: list[CodeEntry],
        case_sensitive: bool = True,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._library = library
        self._case_sensitive = case_sensitive
        self._path: Path | None = None
        self._info: EncodingInfo | None = None
        self._baseline = ""
        self._spans: list[tuple[int, int]] = []
        self._idx = -1
        self._count_stale = False
        self._in_scan = False  # guard: evita marcar stale durante varredura
        self._step_decisions: list[bool] = []
        self._step_idx = 0
        self._build_ui()

    # ---------- construcao ----------
    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(6)
        root.setContentsMargins(12, 8, 12, 12)

        # cabecalho: Voltar (proeminente, topo-esquerdo) | nome do arquivo | aviso | Salvar
        head = QHBoxLayout()
        head.setSpacing(8)

        self.btn_close = QPushButton("✕ Voltar ao resumo")
        self.btn_close.setObjectName("EdBack")
        self.btn_close.clicked.connect(self.closeRequested.emit)
        head.addWidget(self.btn_close)

        self.lbl_file = QLabel("(nenhum arquivo)")
        self.lbl_file.setObjectName("EdFileName")
        head.addWidget(self.lbl_file, stretch=1)

        warn = QLabel("⚠ salva direto, sem cópia")
        warn.setObjectName("EdNoBackup")
        head.addWidget(warn)

        self.btn_save = QPushButton("💾 Salvar")
        self.btn_save.setEnabled(False)
        self.btn_save.clicked.connect(self._on_save)
        head.addWidget(self.btn_save)

        root.addLayout(head)

        # toolbar de busca
        find_row = QHBoxLayout()
        find_row.setSpacing(6)
        find_row.addWidget(QLabel("🔍"))
        self.cb_find = self._make_code_combo()
        self.cb_find.currentTextChanged.connect(self._on_find_text_changed)
        find_row.addWidget(self.cb_find, stretch=1)
        self.lbl_count = QLabel("—")
        find_row.addWidget(self.lbl_count)
        self.btn_prev = QPushButton("↑")
        self.btn_prev.setFixedWidth(32)
        self.btn_prev.clicked.connect(lambda: self._navigate(-1))
        find_row.addWidget(self.btn_prev)
        self.lbl_pos = QLabel("0/0")
        find_row.addWidget(self.lbl_pos)
        self.btn_next = QPushButton("↓")
        self.btn_next.setFixedWidth(32)
        self.btn_next.clicked.connect(lambda: self._navigate(1))
        find_row.addWidget(self.btn_next)
        root.addLayout(find_row)

        # toolbar de substituicao
        repl_row = QHBoxLayout()
        repl_row.setSpacing(6)
        repl_row.addWidget(QLabel("Substituir"))
        self.cb_repl = self._make_code_combo()
        repl_row.addWidget(self.cb_repl, stretch=1)
        repl_row.addWidget(QLabel("por"))
        self.cb_repl_dest = self._make_code_combo()
        repl_row.addWidget(self.cb_repl_dest, stretch=1)
        self.btn_replace_all = QPushButton("Substituir todos")
        self.btn_replace_all.clicked.connect(self._on_replace_all)
        repl_row.addWidget(self.btn_replace_all)
        self.btn_one = QPushButton("Um a um")
        self.btn_one.clicked.connect(self._on_one_by_one_start)
        repl_row.addWidget(self.btn_one)
        root.addLayout(repl_row)

        # stepbar inline (oculto por padrao)
        self._stepbar = _StepBar()
        self._stepbar.btn_prev.clicked.connect(self._step_prev)
        self._stepbar.btn_next.clicked.connect(self._step_next)
        self._stepbar.btn_replace.clicked.connect(self._step_replace)
        self._stepbar.btn_end.clicked.connect(self._step_end)
        root.addWidget(self._stepbar)

        self.editor = CodeEditor()
        self.editor.textChanged.connect(self._on_text_changed)
        root.addWidget(self.editor, stretch=1)

        # highlighter de ocorrencias
        self._highlighter = OccurrenceHighlighter(self.editor.document())

    def _make_code_combo(self) -> QComboBox:
        cb = QComboBox()
        cb.setEditable(True)
        cb.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self._fill_combo(cb)
        return cb

    def _fill_combo(self, cb: QComboBox) -> None:
        cb.clear()
        for i, e in enumerate(self._library):
            cb.addItem(e.find, e.find)
            if e.label:
                cb.setItemData(i, e.label, Qt.ItemDataRole.ToolTipRole)
        cb.setCurrentText("")

    def set_library(self, library: list[CodeEntry]) -> None:
        self._library = library
        for cb in (self.cb_find, self.cb_repl, self.cb_repl_dest):
            self._fill_combo(cb)

    def set_case_sensitive(self, case_sensitive: bool) -> None:
        self._case_sensitive = case_sensitive

    @staticmethod
    def _combo_code(cb: QComboBox) -> str:
        idx = cb.currentIndex()
        if idx >= 0 and cb.itemText(idx) == cb.currentText():
            return str(cb.itemData(idx))
        return cb.currentText().strip()

    # ---------- abrir / dirty / salvar ----------
    def _to_editor(self, text: str) -> str:
        return text.replace("\r\n", "\n").replace("\r", "\n")

    def _from_editor(self, text: str) -> str:
        eol = self._info.eol if self._info else "\n"
        return text if eol == "\n" else text.replace("\n", eol)

    def abrir(self, path: Path) -> None:
        text, info = read_file(path)
        self._path = path
        self._info = info
        self._baseline = self._to_editor(text)
        self.lbl_file.setText(path.name)
        self.editor.blockSignals(True)
        self.editor.setPlainText(self._baseline)
        self.editor.blockSignals(False)
        self._reset_scan()
        self._update_dirty()

    def tem_alteracao(self) -> bool:
        return self.editor.toPlainText() != self._baseline

    def _update_dirty(self) -> None:
        dirty = self.tem_alteracao()
        self.btn_save.setEnabled(dirty)
        self.dirtyChanged.emit(dirty)

    def _on_text_changed(self) -> None:
        if self._spans and not self._in_scan:
            self._count_stale = True
            self.lbl_count.setText("contagem desatualizada — varra de novo")
        self._update_dirty()

    def salvar(self) -> bool:
        if self._path is None or self._info is None:
            return False
        out = self._from_editor(self.editor.toPlainText())
        res = salvar_no_lugar(self._path, out, self._info)
        if res.ok:
            self._baseline = self.editor.toPlainText()
            self._update_dirty()
            QMessageBox.information(self, "Salvo", res.mensagem)
            return True
        QMessageBox.critical(self, "Falha ao salvar", res.mensagem)
        return False

    def _on_save(self) -> None:
        self.salvar()

    # ---------- localizador ----------
    def _reset_scan(self) -> None:
        self._spans = []
        self._idx = -1
        self._count_stale = False
        self.lbl_count.setText("—")
        self.lbl_pos.setText("0/0")
        self._highlighter.clear_highlight()

    def _on_find_text_changed(self) -> None:
        code = self._combo_code(self.cb_find)
        if not code:
            self._reset_scan()
            return
        n_lines = self.editor.document().blockCount()
        if n_lines > _MAX_LINES_HIGHLIGHT:
            self.lbl_count.setText("arquivo grande — realce desativado")
            self._highlighter.clear_highlight()
            return
        self._in_scan = True
        try:
            self._spans = count_matches(self.editor.toPlainText(), code, self._case_sensitive)
            self._count_stale = False
            self._idx = 0 if self._spans else -1
            n = len(self._spans)
            self.lbl_count.setText(f"{n} encontrado(s)")
            self.lbl_pos.setText(f"{1 if n else 0}/{n}")
            self._highlighter.set_term(code, self._spans, self._case_sensitive)
            if self._spans:
                self._highlighter.set_current(self._spans[0])
                self._navigate_to(0)
        finally:
            self._in_scan = False

    def _navigate_to(self, idx: int) -> None:
        if not self._spans:
            return
        self._idx = idx % len(self._spans)
        start, end = self._spans[self._idx]
        cursor = self.editor.textCursor()
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
        self.editor.setTextCursor(cursor)
        self.editor.ensureCursorVisible()
        n = len(self._spans)
        self.lbl_pos.setText(f"{self._idx + 1}/{n}")
        self._highlighter.set_current(self._spans[self._idx])

    def _navigate(self, step: int) -> None:
        if not self._spans:
            return
        self._navigate_to(self._idx + step)

    def _on_replace_all(self) -> None:
        code = self._combo_code(self.cb_find)
        repl = self._combo_code(self.cb_repl_dest)
        text = self.editor.toPlainText()
        spans = count_matches(text, code, self._case_sensitive)
        if not spans:
            QMessageBox.information(self, "Nada encontrado", f"'{code}' não foi encontrado.")
            return
        novo = replace_all_spans(text, spans, repl)
        self.editor.setPlainText(novo)
        self._on_find_text_changed()
        QMessageBox.information(self, "Substituído", f"{len(spans)} ocorrência(s) trocada(s).")

    # ---------- stepbar Um a um ----------

    def _on_one_by_one_start(self) -> None:
        code = self._combo_code(self.cb_find)
        text = self.editor.toPlainText()
        spans = count_matches(text, code, self._case_sensitive)
        if not spans:
            QMessageBox.information(self, "Nada encontrado", f"'{code}' não foi encontrado.")
            return
        self._spans = spans
        self._step_idx = 0
        self._step_decisions = [False] * len(spans)
        self._stepbar.show()
        self.btn_one.setEnabled(False)
        self._step_update()

    def _step_update(self) -> None:
        n = len(self._spans)
        self.lbl_pos.setText(f"{self._step_idx + 1}/{n}")
        self._stepbar.lbl_pos.setText(f"{self._step_idx + 1}/{n}")
        self._navigate_to(self._step_idx)

    def _step_prev(self) -> None:
        if self._step_idx > 0:
            self._step_idx -= 1
            self._step_update()

    def _step_next(self) -> None:
        if self._step_idx < len(self._spans) - 1:
            self._step_idx += 1
            self._step_update()

    def _step_replace(self) -> None:
        self._step_decisions[self._step_idx] = True
        if self._step_idx < len(self._spans) - 1:
            self._step_idx += 1
            self._step_update()

    def _step_end(self) -> None:
        repl = self._combo_code(self.cb_repl_dest)
        code = self._combo_code(self.cb_find)
        text = self.editor.toPlainText()
        if any(self._step_decisions):
            novo = replace_one_by_one(
                text, code, repl, self._step_decisions, self._case_sensitive
            )
            self.editor.setPlainText(novo)
            self._on_find_text_changed()
        self._stepbar.hide()
        self.btn_one.setEnabled(True)
        self._step_decisions = []
