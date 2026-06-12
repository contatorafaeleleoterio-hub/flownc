"""Editor de texto integrado por arquivo.

Editor embutido com numeracao de linha, localizador e gravacao in-place segura.
Sera adaptado a tela Editor do v4 (tela cheia + faixa de arquivos + toolbar em 3
grupos) no Bloco 7; o motor de edicao/gravacao e reaproveitado sem alteracao.

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
    QButtonGroup,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from core.file_handler import read_file
from core.inplace_save import salvar_no_lugar
from core.library_store import CodeEntry
from core.matcher import find_matches, find_spans
from core.models import EncodingInfo, Mode, Rule
from ui.components.code_combo import CodeCombo

_MAX_LINES_HIGHLIGHT = 5000


def ponto_insercao(texto: str, modo: str, codigo: str, linha: int) -> int:
    """Índice da linha onde o bloco entraria; -1 se a âncora (código) não existe.

    Função pura (testável sem GUI). Espelha a inserção do compositor do Lote, com
    o mesmo boundary CNC: o bloco entra logo ABAIXO da 1ª ocorrência do código
    (modo 'code') ou abaixo da linha Nº informada (modo 'line').
    """
    linhas = texto.split("\n")
    if modo == "code":
        for i, ln in enumerate(linhas):
            if find_spans(ln, codigo, Mode.AUTO):
                return i + 1
        return -1
    return min(max(1, linha), len(linhas))

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


# ============ diálogo "Inserir bloco" do editor ============


class _InserirBlocoDialog(QDialog):
    """Insere um bloco no buffer do editor, com prévia e proteção de âncora.

    Se o código-âncora não existir no arquivo aberto, a prévia avisa "não aparece
    neste arquivo — nada será inserido" e o botão Inserir fica bloqueado.
    """

    def __init__(
        self,
        texto: str,
        library: list[CodeEntry],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Inserir bloco de linhas")
        self.setModal(True)
        self.setMinimumWidth(460)
        self._texto = texto
        self._library = library
        self._modelos = [
            (e.find, e.label or e.find, e.replace)
            for e in library if "bloco" in e.tags and e.replace
        ]
        self._build()
        self._atualizar_previa()

    def _build(self) -> None:
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(12)

        if self._modelos:
            chips = QHBoxLayout()
            chips.setSpacing(8)
            for nome, desc, txt in self._modelos:
                chip = QPushButton(nome)
                chip.setObjectName("InsChip")
                chip.setToolTip(desc)
                chip.clicked.connect(lambda _=False, t=txt: self.ed_block.setPlainText(t))
                chips.addWidget(chip)
            chips.addStretch(1)
            lay.addLayout(chips)

        self.ed_block = QPlainTextEdit()
        self.ed_block.setObjectName("InsText")
        self.ed_block.setPlaceholderText("ex.:\nG68 R90.\nG54")
        self.ed_block.setFixedHeight(96)
        self.ed_block.textChanged.connect(self._atualizar_previa)
        lay.addWidget(self.ed_block)

        self._grupo = QButtonGroup(self)
        l1 = QHBoxLayout()
        self.rad_code = QRadioButton("Abaixo da 1ª ocorrência de")
        self.rad_code.setChecked(True)
        self.rad_code.toggled.connect(self._atualizar_previa)
        self._grupo.addButton(self.rad_code)
        l1.addWidget(self.rad_code)
        self.cb_code = CodeCombo()
        for e in self._library:
            self.cb_code.addItem(e.find, e.find)
            if e.label:
                self.cb_code.setItemData(
                    self.cb_code.count() - 1, e.label, Qt.ItemDataRole.ToolTipRole)
        self.cb_code.setCurrentText("")
        self.cb_code.currentTextChanged.connect(self._atualizar_previa)
        l1.addWidget(self.cb_code, stretch=1)
        lay.addLayout(l1)

        l2 = QHBoxLayout()
        self.rad_line = QRadioButton("Abaixo da linha Nº")
        self.rad_line.toggled.connect(self._atualizar_previa)
        self._grupo.addButton(self.rad_line)
        l2.addWidget(self.rad_line)
        self.sp_line = QSpinBox()
        self.sp_line.setRange(1, 999999)
        self.sp_line.valueChanged.connect(self._atualizar_previa)
        l2.addWidget(self.sp_line)
        l2.addStretch(1)
        lay.addLayout(l2)

        prev = QFrame()
        prev.setObjectName("PreviewBox")
        pv = QVBoxLayout(prev)
        pv.setContentsMargins(0, 0, 0, 0)
        cab = QLabel("Prévia")
        cab.setObjectName("PvHead")
        pv.addWidget(cab)
        self.previa = QLabel("—")
        self.previa.setObjectName("InsPreview")
        self.previa.setWordWrap(True)
        pv.addWidget(self.previa)
        lay.addWidget(prev)

        self._botoes = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel)
        self.btn_inserir = self._botoes.addButton(
            "Inserir bloco", QDialogButtonBox.ButtonRole.AcceptRole)
        self.btn_inserir.setObjectName("CompAddBtn")
        self._botoes.accepted.connect(self.accept)
        self._botoes.rejected.connect(self.reject)
        lay.addWidget(self._botoes)

    def _modo(self) -> str:
        return "line" if self.rad_line.isChecked() else "code"

    def _codigo(self) -> str:
        return self.cb_code.currentText().strip()

    def resultado(self) -> tuple[str, int]:
        """(texto_resultante, indice_de_insercao) — válido só se `pode_inserir`."""
        at = ponto_insercao(self._texto, self._modo(), self._codigo(), self.sp_line.value())
        linhas = self._texto.split("\n")
        bloco = self.ed_block.toPlainText().rstrip().split("\n")
        novo = "\n".join(linhas[:at] + bloco + linhas[at:])
        return novo, at

    def _atualizar_previa(self) -> None:
        bloco = self.ed_block.toPlainText().rstrip()
        if not bloco:
            self.previa.setText("(digite o bloco para ver a prévia)")
            self.btn_inserir.setEnabled(False)
            return
        if self._modo() == "code" and not self._codigo():
            self.previa.setText("Escolha o código de referência.")
            self.btn_inserir.setEnabled(False)
            return
        at = ponto_insercao(self._texto, self._modo(), self._codigo(), self.sp_line.value())
        if at < 0:
            self.previa.setText(
                f"“{self._codigo()}” não aparece neste arquivo — nada será inserido.")
            self.btn_inserir.setEnabled(False)
            return
        linhas = self._texto.split("\n")
        out: list[str] = []
        for i in range(max(0, at - 2), at):
            out.append(f"   {i + 1}  {linhas[i]}")
        for ln in bloco.split("\n"):
            out.append(f" + ▶  {ln}")
        for i in range(at, min(len(linhas), at + 2)):
            out.append(f"   {i + 1}  {linhas[i]}")
        self.previa.setText("\n".join(out))
        self.btn_inserir.setEnabled(True)


# ============ painel do editor ============


class EditorPanel(QWidget):
    """Editor por arquivo: abrir, localizar/substituir e salvar in-place."""

    dirtyChanged = Signal(bool)
    closeRequested = Signal()
    saved = Signal(str)  # emite o conteúdo ANTERIOR ao save (para o toast "Desfazer")

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

        warn = QLabel("salva direto, sem cópia — sobrescreve o original")
        warn.setObjectName("EdNoBackup")
        head.addWidget(warn)

        self.btn_save_as = QPushButton("Salvar como…")
        self.btn_save_as.setEnabled(False)
        self.btn_save_as.clicked.connect(self._on_save_as)
        head.addWidget(self.btn_save_as)

        self.btn_save = QPushButton("Salvar")
        self.btn_save.setEnabled(False)
        self.btn_save.clicked.connect(self._on_save)
        head.addWidget(self.btn_save)

        root.addLayout(head)

        # toolbar de busca — grupo "Localizar"
        find_row = QHBoxLayout()
        find_row.setSpacing(6)
        lbl_loc = QLabel("Localizar")
        lbl_loc.setObjectName("EdGroup")
        find_row.addWidget(lbl_loc)
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

        # toolbar de substituicao — grupo "Substituir" | grupo "Inserir bloco"
        repl_row = QHBoxLayout()
        repl_row.setSpacing(6)
        lbl_sub = QLabel("Substituir")
        lbl_sub.setObjectName("EdGroup")
        repl_row.addWidget(lbl_sub)
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
        sep = QFrame()
        sep.setObjectName("EdSep")
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFixedWidth(1)
        repl_row.addWidget(sep)
        self.btn_insert = QPushButton("+ Inserir bloco")
        self.btn_insert.setObjectName("EdInsertBtn")
        self.btn_insert.clicked.connect(self._on_inserir_bloco)
        repl_row.addWidget(self.btn_insert)
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
        cb = CodeCombo()
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
        self.btn_save_as.setEnabled(True)
        self._reset_scan()
        self._update_dirty()

    def tem_alteracao(self) -> bool:
        return self.editor.toPlainText() != self._baseline

    def _update_dirty(self) -> None:
        dirty = self.tem_alteracao()
        self.btn_save.setEnabled(dirty)
        self.dirtyChanged.emit(dirty)

    def _on_text_changed(self) -> None:
        # Contagem automática (8.2): recalcula ao editar o texto, sem mover o cursor.
        if not self._in_scan:
            code = self._combo_code(self.cb_find)
            if code and self.editor.document().blockCount() <= _MAX_LINES_HIGHLIGHT:
                self._recount_silent(code)
        self._update_dirty()

    def _recount_silent(self, code: str) -> None:
        """Recalcula contagem + realce sem reposicionar o cursor (contagem automática)."""
        self._in_scan = True
        try:
            self._spans = count_matches(self.editor.toPlainText(), code, self._case_sensitive)
            self._count_stale = False
            n = len(self._spans)
            if self._idx >= n:
                self._idx = n - 1
            self.lbl_count.setText(f"{n} encontrado(s)")
            pos = (self._idx + 1) if (self._spans and self._idx >= 0) else 0
            self.lbl_pos.setText(f"{pos}/{n}")
            self._highlighter.set_term(code, self._spans, self._case_sensitive)
            if self._spans and 0 <= self._idx < n:
                self._highlighter.set_current(self._spans[self._idx])
        finally:
            self._in_scan = False

    def _on_inserir_bloco(self) -> None:
        """Abre o diálogo de inserir bloco; aplica no buffer (não salva)."""
        if self._path is None:
            return
        dlg = _InserirBlocoDialog(self.editor.toPlainText(), self._library, self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        novo, _at = dlg.resultado()
        self.editor.setPlainText(novo)

    def salvar(self) -> bool:
        if self._path is None or self._info is None:
            return False
        anterior = self._baseline  # conteúdo salvo antes desta gravação (p/ Desfazer)
        out = self._from_editor(self.editor.toPlainText())
        res = salvar_no_lugar(self._path, out, self._info)
        if res.ok:
            self._baseline = self.editor.toPlainText()
            self._update_dirty()
            self.saved.emit(anterior)
            return True
        QMessageBox.critical(self, "Falha ao salvar", res.mensagem)
        return False

    def _on_save(self) -> None:
        self.salvar()

    def _on_save_as(self) -> None:
        """Salva uma cópia em outro caminho, preservando o formato do original."""
        if self._path is None or self._info is None:
            return
        from PySide6.QtWidgets import QFileDialog
        destino, _ = QFileDialog.getSaveFileName(
            self, "Salvar cópia como…", self._path.name,
            "Programas CNC (*.nc *.txt *.tap *.iso *.min *.mpf);;Todos os arquivos (*.*)")
        if not destino:
            return
        out = self._from_editor(self.editor.toPlainText())
        res = salvar_no_lugar(Path(destino), out, self._info)
        if not res.ok:
            QMessageBox.critical(self, "Falha ao salvar como…", res.mensagem)

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
