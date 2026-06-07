"""Editor de texto integrado por arquivo (mudanca editor-integrado-por-arquivo).

Editor embutido estilo Bloco de Notas (numeracao de linha, fonte mono, edicao
direta) com um localizador no cabecalho que reusa `core.matcher.find_matches`
para contar/navegar/substituir com a MESMA borda CNC do Lote, e gravacao
in-place segura via `core.inplace_save.salvar_no_lugar` (atomica, conferida por
SHA, sem backup).

A logica de busca/substituicao mora em funcoes puras de modulo
(`build_find_rule`, `replace_all_spans`, `replace_one_by_one`), testaveis sem GUI
(tests/test_editor_localizador.py). O `EditorPanel` (QWidget) so apresenta e
delega.
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QRect, QSize, Qt, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QTextCursor
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
    """Aplica decisoes (substituir/pular) por ocorrencia, na ordem do texto.

    Usa os intervalos do texto ORIGINAL e reconstroi da esquerda p/ direita, de
    modo que pular/substituir nunca invalida os offsets seguintes.
    """
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
        painter.fillRect(event.rect(), QColor(235, 238, 242))
        block = self.firstVisibleBlock()
        block_num = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())
        line_h = self.fontMetrics().height()
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                painter.setPen(QColor(120, 128, 136))
                painter.drawText(
                    0, top, self._lna.width() - 4, line_h,
                    int(Qt.AlignmentFlag.AlignRight), str(block_num + 1),
                )
            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_num += 1


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
        self._build_ui()

    # ---------- construcao ----------
    def _build_ui(self) -> None:
        root = QVBoxLayout(self)

        head = QHBoxLayout()
        self.lbl_file = QLabel("(nenhum arquivo)")
        self.lbl_file.setStyleSheet("font-weight:600;")
        head.addWidget(self.lbl_file)
        head.addStretch(1)
        warn = QLabel("⚠ salva direto, sem cópia")
        warn.setStyleSheet("color:#b35900;")
        head.addWidget(warn)
        self.btn_save = QPushButton("Salvar")
        self.btn_save.setEnabled(False)
        self.btn_save.clicked.connect(self._on_save)
        head.addWidget(self.btn_save)
        self.btn_close = QPushButton("✕ Voltar ao resumo")
        self.btn_close.clicked.connect(self.closeRequested.emit)
        head.addWidget(self.btn_close)
        root.addLayout(head)

        find_row = QHBoxLayout()
        find_row.addWidget(QLabel("Localizar"))
        self.cb_find = self._make_code_combo()
        find_row.addWidget(self.cb_find, stretch=1)
        self.btn_scan = QPushButton("🔎")
        self.btn_scan.clicked.connect(self._on_scan)
        find_row.addWidget(self.btn_scan)
        self.lbl_count = QLabel("—")
        find_row.addWidget(self.lbl_count)
        self.btn_prev = QPushButton("◂")
        self.btn_prev.setFixedWidth(32)
        self.btn_prev.clicked.connect(lambda: self._navigate(-1))
        find_row.addWidget(self.btn_prev)
        self.lbl_pos = QLabel("0/0")
        find_row.addWidget(self.lbl_pos)
        self.btn_next = QPushButton("▸")
        self.btn_next.setFixedWidth(32)
        self.btn_next.clicked.connect(lambda: self._navigate(1))
        find_row.addWidget(self.btn_next)
        root.addLayout(find_row)

        repl_row = QHBoxLayout()
        repl_row.addWidget(QLabel("Substituir por"))
        self.cb_repl = self._make_code_combo()
        repl_row.addWidget(self.cb_repl, stretch=1)
        self.btn_replace_all = QPushButton("Substituir todos")
        self.btn_replace_all.clicked.connect(self._on_replace_all)
        repl_row.addWidget(self.btn_replace_all)
        self.btn_one = QPushButton("Um a um")
        self.btn_one.clicked.connect(self._on_one_by_one)
        repl_row.addWidget(self.btn_one)
        root.addLayout(repl_row)

        self.editor = CodeEditor()
        self.editor.textChanged.connect(self._on_text_changed)
        root.addWidget(self.editor, stretch=1)

    def _make_code_combo(self) -> QComboBox:
        cb = QComboBox()
        cb.setEditable(True)
        cb.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self._fill_combo(cb)
        return cb

    def _fill_combo(self, cb: QComboBox) -> None:
        cb.clear()
        for e in self._library:
            label = f"{e.label}  " if e.label else ""
            cb.addItem(f"{label}{e.find}", e.find)
        cb.setCurrentText("")

    def set_library(self, library: list[CodeEntry]) -> None:
        """Atualiza a biblioteca injetada e repopula os dropdowns."""
        self._library = library
        self._fill_combo(self.cb_find)
        self._fill_combo(self.cb_repl)

    def set_case_sensitive(self, case_sensitive: bool) -> None:
        self._case_sensitive = case_sensitive

    @staticmethod
    def _combo_code(cb: QComboBox) -> str:
        """Codigo escolhido: usa o data da entrada quando bate, senao o texto."""
        idx = cb.currentIndex()
        if idx >= 0 and cb.itemText(idx) == cb.currentText():
            return str(cb.itemData(idx))
        return cb.currentText().strip()

    # ---------- abrir / dirty / salvar ----------
    def _to_editor(self, text: str) -> str:
        """Normaliza EOL para \\n (o QPlainTextEdit so trabalha com \\n)."""
        return text.replace("\r\n", "\n").replace("\r", "\n")

    def _from_editor(self, text: str) -> str:
        """Reaplica o EOL original do arquivo ao salvar (preserva CRLF/CR)."""
        eol = self._info.eol if self._info else "\n"
        return text if eol == "\n" else text.replace("\n", eol)

    def abrir(self, path: Path) -> None:
        text, info = read_file(path)
        self._path = path
        self._info = info
        # baseline e buffer vivem em \n; o EOL real e reaplicado so na gravacao.
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
        if self._spans:
            self._count_stale = True
            self.lbl_count.setText("contagem desatualizada — varra de novo")
        self._update_dirty()

    def salvar(self) -> bool:
        """Grava in-place; retorna True em sucesso. Usado pelo Salvar e pela guarda."""
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

    def _on_scan(self) -> None:
        code = self._combo_code(self.cb_find)
        # Varredura NAO move o cursor nem rola: so conta e guarda os intervalos.
        self._spans = count_matches(self.editor.toPlainText(), code, self._case_sensitive)
        self._count_stale = False
        self._idx = 0 if self._spans else -1
        n = len(self._spans)
        self.lbl_count.setText(f"{n} encontrado(s)")
        self.lbl_pos.setText(f"{1 if n else 0}/{n}")

    def _navigate(self, step: int) -> None:
        if not self._spans:
            return
        n = len(self._spans)
        self._idx = (self._idx + step) % n
        start, end = self._spans[self._idx]
        cursor = self.editor.textCursor()
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
        self.editor.setTextCursor(cursor)
        self.editor.ensureCursorVisible()
        self.lbl_pos.setText(f"{self._idx + 1}/{n}")

    def _on_replace_all(self) -> None:
        code = self._combo_code(self.cb_find)
        repl = self._combo_code(self.cb_repl)
        text = self.editor.toPlainText()
        spans = count_matches(text, code, self._case_sensitive)
        if not spans:
            QMessageBox.information(self, "Nada encontrado", f"'{code}' não foi encontrado.")
            return
        novo = replace_all_spans(text, spans, repl)
        self.editor.setPlainText(novo)  # dispara textChanged -> dirty + stale
        self._on_scan()
        QMessageBox.information(self, "Substituído", f"{len(spans)} ocorrência(s) trocada(s).")

    def _on_one_by_one(self) -> None:
        code = self._combo_code(self.cb_find)
        repl = self._combo_code(self.cb_repl)
        text = self.editor.toPlainText()
        spans = count_matches(text, code, self._case_sensitive)
        if not spans:
            QMessageBox.information(self, "Nada encontrado", f"'{code}' não foi encontrado.")
            return
        self._spans = spans
        decisions: list[bool] = []
        for i in range(len(spans)):
            self._idx = i
            self._navigate(0)  # rola/seleciona a ocorrencia atual
            resp = QMessageBox.question(
                self, "Um a um",
                f"Ocorrência {i + 1}/{len(spans)} de '{code}'.\n\nSubstituir por '{repl}'?",
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
                | QMessageBox.StandardButton.Cancel,
            )
            if resp == QMessageBox.StandardButton.Cancel:
                break
            decisions.append(resp == QMessageBox.StandardButton.Yes)
        if any(decisions):
            novo = replace_one_by_one(text, code, repl, decisions, self._case_sensitive)
            self.editor.setPlainText(novo)
            self._on_scan()
