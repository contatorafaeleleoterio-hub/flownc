"""Janela principal do FlowNC (PRD secao 11) — modelo por programa.

Aba SUBSTITUICOES: lista de programas + 'Trocas comuns (todos)' + 'Trocas so do
programa selecionado'. Funciona com 1 ou varios programas. So as marcadas sao
aplicadas. Aba VERIFICACOES: separada, com seu proprio botao Executar.
Reusa integralmente o core/ (puro).
"""
from __future__ import annotations

import difflib
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from core.conference import format_integrity_report, verify_saved

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QAbstractItemView,
    QButtonGroup,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QRadioButton,
    QSplitter,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

import app_paths
from core.library_store import CodeEntry, LibraryError, load_library
from core.settings_store import AppSettings, load_settings, save_settings
from core.file_handler import (
    BatchEncodeError,
    BinaryFileError,
    encode_batch,
    list_input_files,
    make_output_dir,
    read_file,
    write_encoded_batch,
)
from core.matcher import suggest_leading_zero_variant
from core.models import (
    Mode,
    OnZeroMatches,
    Preset,
    Rule,
    Scope,
    Severity,
    Verification,
    VerificationType,
)
from core.preset_store import (
    PresetError,
    create_preset,
    delete_preset,
    duplicate_preset,
    load_preset,
    rename_preset,
    save_preset,
)
from core.replacement_plan import build_plan
from core.replacer import apply_edits
from core.session_log import SessionLog
from core.verifier import run_configurable, run_structural
from ui.editor_panel import EditorPanel
from ui.library_dialog import LibraryDialog, LibraryPickerDialog
from ui.preview_dialog import PreviewDialog

_GREEN = QColor(225, 245, 225)
_YELLOW = QColor(255, 247, 205)
_RED = QColor(250, 220, 220)

# colunas das tabelas de trocas
A_APPLY, A_FIND, A_REPL, A_OBS = range(4)
# colunas da tabela de verificacoes
V_APPLY, V_TYPE, V_FIND, V_VAL, V_OBS = range(5)

_VTYPES = {
    "Deve existir": VerificationType.MUST_EXIST,
    "Nao pode existir": VerificationType.MUST_NOT_EXIST,
    "Minimo": VerificationType.COUNT_MIN,
    "Maximo": VerificationType.COUNT_MAX,
    "Exato": VerificationType.EXACT_COUNT,
}
_VTYPES_INV = {v: k for k, v in _VTYPES.items()}


@dataclass
class FileOutcome:
    name: str
    info: object | None = None
    original: str = ""
    result: str = ""
    edits: list = field(default_factory=list)
    suppressions: list = field(default_factory=list)
    alerts: list = field(default_factory=list)
    zero: list = field(default_factory=list)
    read_error: str | None = None
    # checklist: [(find, replace, count, on_zero_label)]
    checklist: list[tuple[str, str, int, str]] = field(default_factory=list)

    def worst(self) -> Severity:
        if self.read_error or any(s is Severity.CRITICAL for s, _, _ in self.alerts):
            return Severity.CRITICAL
        if self.suppressions or self.zero or any(s is Severity.WARNING for s, _, _ in self.alerts):
            return Severity.WARNING
        return Severity.OK


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("FlowNC — Substituicoes em programas CNC")
        self.resize(1180, 720)
        self._preset: Preset | None = None
        self._programs: list[Path] = []
        self._file_subs: dict[str, list[tuple[bool, str, str, str]]] = {}
        self._current: str | None = None
        self._loading = False
        self._library: list[CodeEntry] = []
        self._settings: AppSettings = AppSettings()

        self._build_ui()
        self._load_presets()
        self._load_library()
        self._load_settings()

    # ============ construcao ============
    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        top = QHBoxLayout()
        top.addWidget(QLabel("Perfil:"))
        self.cb_preset = QComboBox()
        self.cb_preset.setMinimumWidth(180)
        self.cb_preset.currentIndexChanged.connect(self._on_preset_changed)
        top.addWidget(self.cb_preset)
        bn = QPushButton("Novo")
        bn.clicked.connect(self._on_preset_new)
        top.addWidget(bn)
        bdup = QPushButton("Duplicar")
        bdup.clicked.connect(self._on_preset_duplicate)
        top.addWidget(bdup)
        brn = QPushButton("Renomear")
        brn.clicked.connect(self._on_preset_rename)
        top.addWidget(brn)
        bdel = QPushButton("Excluir")
        bdel.clicked.connect(self._on_preset_delete)
        top.addWidget(bdel)
        top.addSpacing(12)
        b1 = QPushButton("Abrir pasta...")
        b1.clicked.connect(self._open_folder)
        top.addWidget(b1)
        b2 = QPushButton("Abrir programa(s)...")
        b2.clicked.connect(self._open_files)
        top.addWidget(b2)
        self.lbl_src = QLabel("(nenhum programa carregado)")
        self.lbl_src.setStyleSheet("color:#555;")
        top.addWidget(self.lbl_src, stretch=1)
        root.addLayout(top)

        dest = QHBoxLayout()
        dest.addWidget(QLabel("Destino:"))
        self._bg_dest = QButtonGroup(self)
        self.rb_ao_lado = QRadioButton("Ao lado dos originais")
        self.rb_fixo = QRadioButton("Pasta fixa:")
        self._bg_dest.addButton(self.rb_ao_lado, 0)
        self._bg_dest.addButton(self.rb_fixo, 1)
        self.rb_ao_lado.setChecked(True)
        self.rb_ao_lado.toggled.connect(self._on_dest_mode_changed)
        dest.addWidget(self.rb_ao_lado)
        dest.addWidget(self.rb_fixo)
        self.le_dest_dir = QLineEdit()
        self.le_dest_dir.setReadOnly(True)
        self.le_dest_dir.setMinimumWidth(260)
        self.le_dest_dir.setPlaceholderText("(selecione uma pasta)")
        dest.addWidget(self.le_dest_dir, stretch=1)
        self.btn_dest_browse = QPushButton("Escolher...")
        self.btn_dest_browse.clicked.connect(self._on_dest_browse)
        dest.addWidget(self.btn_dest_browse)
        root.addLayout(dest)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_subs_tab(), "Substituicoes")
        self.tabs.addTab(self._build_verif_tab(), "Verificacoes")
        root.addWidget(self.tabs, stretch=1)

        self.lbl_status = QLabel("Selecione um perfil e abra os programas.")
        root.addWidget(self.lbl_status)

    def _build_subs_tab(self) -> QWidget:
        w = QWidget()
        lay = QHBoxLayout(w)
        split = QSplitter(Qt.Orientation.Horizontal)

        left = QWidget()
        lv = QVBoxLayout(left)
        lv.setContentsMargins(0, 0, 0, 0)
        lv.addWidget(QLabel("PROGRAMAS  (marque os que vao receber as trocas)"))
        self.lst_prog = QListWidget()
        self.lst_prog.currentRowChanged.connect(self._on_program_selected)
        self.lst_prog.itemDoubleClicked.connect(lambda _it: self._on_edit_program())
        lv.addWidget(self.lst_prog)
        self.btn_edit_prog = QPushButton("✎ Editar programa selecionado")
        self.btn_edit_prog.clicked.connect(self._on_edit_program)
        lv.addWidget(self.btn_edit_prog)
        split.addWidget(left)

        right = QWidget()
        rv = QVBoxLayout(right)
        rv.setContentsMargins(0, 0, 0, 0)

        rv.addWidget(QLabel("Trocas COMUNS  (valem para todos os programas marcados)"))
        self.tbl_common = self._make_subs_table()
        rv.addWidget(self.tbl_common)
        c1 = QHBoxLayout()
        ba = QPushButton("+ troca comum")
        ba.clicked.connect(lambda: self._add_subs_row(self.tbl_common, True, "", "", ""))
        bd = QPushButton("- remover")
        bd.clicked.connect(lambda: self._remove_row(self.tbl_common))
        bl = QPushButton("+ da lista")
        bl.clicked.connect(lambda: self._on_from_library(self.tbl_common))
        c1.addWidget(ba)
        c1.addWidget(bd)
        c1.addWidget(bl)
        c1.addStretch(1)
        rv.addLayout(c1)

        self.lbl_prog = QLabel("Trocas SO DESTE programa:  (selecione um programa)")
        rv.addWidget(self.lbl_prog)
        self.tbl_file = self._make_subs_table()
        rv.addWidget(self.tbl_file)
        c2 = QHBoxLayout()
        ba2 = QPushButton("+ troca so deste")
        ba2.clicked.connect(lambda: self._add_subs_row(self.tbl_file, True, "", "", ""))
        bd2 = QPushButton("- remover")
        bd2.clicked.connect(lambda: self._remove_row(self.tbl_file))
        bl2 = QPushButton("+ da lista")
        bl2.clicked.connect(lambda: self._on_from_library(self.tbl_file))
        bmg = QPushButton("Gerenciar codigos...")
        bmg.clicked.connect(self._on_manage_library)
        c2.addWidget(ba2)
        c2.addWidget(bd2)
        c2.addWidget(bl2)
        c2.addStretch(1)
        c2.addWidget(bmg)
        self.btn_saveprof = QPushButton("Salvar perfil")
        self.btn_saveprof.clicked.connect(self._on_save_profile)
        c2.addWidget(self.btn_saveprof)
        rv.addLayout(c2)

        run = QHBoxLayout()
        self.btn_run_subs = QPushButton("Executar substituicoes  (preview)")
        self.btn_run_subs.clicked.connect(self._on_execute_subs)
        run.addWidget(self.btn_run_subs)
        run.addStretch(1)
        rv.addLayout(run)

        # Pilha na area da direita: pagina 0 = tabelas de trocas (Lote);
        # pagina 1 = editor por arquivo. "Editar" mostra o editor; "Voltar" retorna.
        self._right_stack = QStackedWidget()
        self._right_stack.addWidget(right)
        self._editor = EditorPanel(self._library, parent=self)
        self._editor.closeRequested.connect(self._close_editor)
        self._right_stack.addWidget(self._editor)
        split.addWidget(self._right_stack)
        split.setSizes([280, 900])
        lay.addWidget(split)
        return w

    def _build_verif_tab(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.addWidget(QLabel("VERIFICACOES  (rodam nos programas marcados, sem alterar nada)"))
        self.tbl_verif = QTableWidget(0, 5)
        self.tbl_verif.setHorizontalHeaderLabels(["Aplicar", "Tipo", "Codigo", "Valor", "Obs"])
        hh = self.tbl_verif.horizontalHeader()
        hh.setSectionResizeMode(V_APPLY, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(V_TYPE, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(V_FIND, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(V_VAL, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(V_OBS, QHeaderView.ResizeMode.Stretch)
        v.addWidget(self.tbl_verif)
        c = QHBoxLayout()
        ba = QPushButton("+ verificacao")
        ba.clicked.connect(lambda: self._add_verif_row(True, VerificationType.MUST_EXIST, "", 1, ""))
        bd = QPushButton("- remover")
        bd.clicked.connect(lambda: self._remove_row(self.tbl_verif))
        c.addWidget(ba)
        c.addWidget(bd)
        c.addStretch(1)
        self.btn_run_verif = QPushButton("Executar verificacoes")
        self.btn_run_verif.clicked.connect(self._on_execute_verifs)
        c.addWidget(self.btn_run_verif)
        v.addLayout(c)
        v.addWidget(QLabel("Resultado:"))
        self.txt_verif = QPlainTextEdit()
        self.txt_verif.setReadOnly(True)
        self.txt_verif.setFont(QFont("Consolas", 10))
        v.addWidget(self.txt_verif, stretch=1)
        return w

    # ============ tabelas helpers ============
    def _make_subs_table(self) -> QTableWidget:
        t = QTableWidget(0, 4)
        t.setHorizontalHeaderLabels(["Aplicar", "Buscar (o que esta)", "Trocar por", "Obs"])
        t.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        hh = t.horizontalHeader()
        hh.setSectionResizeMode(A_APPLY, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(A_FIND, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(A_REPL, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(A_OBS, QHeaderView.ResizeMode.Stretch)
        return t

    def _add_subs_row(self, t: QTableWidget, active: bool, find: str, replace: str, obs: str,
                      on_zero: OnZeroMatches = OnZeroMatches.WARN) -> None:
        r = t.rowCount()
        t.insertRow(r)
        chk = QTableWidgetItem()
        chk.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
        chk.setCheckState(Qt.CheckState.Checked if active else Qt.CheckState.Unchecked)
        chk.setData(Qt.ItemDataRole.UserRole, on_zero)
        t.setItem(r, A_APPLY, chk)
        t.setItem(r, A_FIND, QTableWidgetItem(find))
        t.setItem(r, A_REPL, QTableWidgetItem(replace))
        t.setItem(r, A_OBS, QTableWidgetItem(obs))
        if not find:
            t.setCurrentCell(r, A_FIND)
            t.editItem(t.item(r, A_FIND))

    @staticmethod
    def _read_subs_table(t: QTableWidget) -> list[tuple[bool, str, str, str, OnZeroMatches]]:
        out = []
        for r in range(t.rowCount()):
            chk = t.item(r, A_APPLY)
            act = chk.checkState() is Qt.CheckState.Checked
            # Qt devolve o enum (subclasse de str) como string pura; reconstroi o enum
            # para evitar AttributeError em '.value' depois (bug do botao Executar).
            raw = chk.data(Qt.ItemDataRole.UserRole)
            try:
                on_zero = OnZeroMatches(raw) if raw else OnZeroMatches.WARN
            except ValueError:
                on_zero = OnZeroMatches.WARN
            find = (t.item(r, A_FIND).text() if t.item(r, A_FIND) else "").strip()
            repl = t.item(r, A_REPL).text() if t.item(r, A_REPL) else ""
            obs = t.item(r, A_OBS).text() if t.item(r, A_OBS) else ""
            out.append((act, find, repl, obs, on_zero))
        return out

    def _load_subs_table(self, t: QTableWidget, rows: list) -> None:
        t.setRowCount(0)
        for row in rows:
            act, find, repl, obs = row[:4]
            on_zero = row[4] if len(row) > 4 else OnZeroMatches.WARN
            self._add_subs_row(t, act, find, repl, obs, on_zero)

    def _remove_row(self, t: QTableWidget) -> None:
        if t.currentRow() >= 0:
            t.removeRow(t.currentRow())

    def _add_verif_row(self, active: bool, vtype: VerificationType, find: str, val: int, obs: str) -> None:
        t = self.tbl_verif
        r = t.rowCount()
        t.insertRow(r)
        chk = QTableWidgetItem()
        chk.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
        chk.setCheckState(Qt.CheckState.Checked if active else Qt.CheckState.Unchecked)
        t.setItem(r, V_APPLY, chk)
        cb = QComboBox()
        cb.addItems(list(_VTYPES.keys()))
        cb.setCurrentText(_VTYPES_INV[vtype])
        t.setCellWidget(r, V_TYPE, cb)
        t.setItem(r, V_FIND, QTableWidgetItem(find))
        t.setItem(r, V_VAL, QTableWidgetItem(str(val)))
        t.setItem(r, V_OBS, QTableWidgetItem(obs))

    def _read_verifs(self) -> list[Verification]:
        t = self.tbl_verif
        out = []
        for r in range(t.rowCount()):
            if t.item(r, V_APPLY).checkState() is not Qt.CheckState.Checked:
                continue
            find = (t.item(r, V_FIND).text() if t.item(r, V_FIND) else "").strip()
            if not find:
                continue
            vtype = _VTYPES[t.cellWidget(r, V_TYPE).currentText()]
            try:
                val = int(t.item(r, V_VAL).text()) if t.item(r, V_VAL) else 0
            except ValueError:
                val = 0
            obs = t.item(r, V_OBS).text() if t.item(r, V_OBS) else ""
            out.append(Verification(id=f"v{r}", type=vtype, find=find, mode=Mode.LITERAL,
                                    label=obs or find, count=val))
        return out

    # ============ presets ============
    def _load_presets(self) -> None:
        self.cb_preset.clear()
        pdir = app_paths.presets_dir()
        files = sorted(pdir.glob("*.json")) if pdir.is_dir() else []
        if not files:
            self.cb_preset.addItem("(nenhum perfil)", None)
            return
        for f in files:
            self.cb_preset.addItem(f.stem, str(f))
        self._on_preset_changed(0)

    def _on_preset_changed(self, _i: int) -> None:
        path = self.cb_preset.currentData()
        if not path:
            self._preset = None
            return
        try:
            self._preset = load_preset(Path(path))
        except PresetError as exc:
            self._preset = None
            QMessageBox.critical(self, "Perfil invalido", str(exc))
            return
        self._load_subs_table(self.tbl_common,
                              [(r.active, r.find, r.replace, r.comment, r.on_zero_matches)
                               for r in self._preset.global_rules])
        self.tbl_verif.setRowCount(0)
        for v in self._preset.verifications:
            self._add_verif_row(True, v.type, v.find, v.count, v.label)
        self._seed_file_subs()
        if self._current:
            self._load_subs_table(self.tbl_file, self._file_subs.get(self._current, []))
        self._set_status(f"Perfil '{self._preset.machine}' carregado.")

    def _seed_file_subs(self) -> None:
        if self._preset is None:
            return
        for p in self._programs:
            key = str(p.resolve())
            seeded = [(r.active, r.find, r.replace, r.comment, r.on_zero_matches)
                      for r in self._preset.file_rules if r.file == p.name]
            self._file_subs.setdefault(key, seeded)

    # ============ abrir programas ============
    def _open_folder(self) -> None:
        d = QFileDialog.getExistingDirectory(self, "Escolher pasta com programas NC")
        if d:
            # Sem perfil: aceita qualquer arquivo de texto (curinga). Com perfil,
            # usa as extensoes dele (que ja pode ser '*').
            exts = self._preset.extensions if self._preset else ["*"]
            self._set_programs(list_input_files(Path(d), exts), d)

    def _open_files(self) -> None:
        # "Todos os arquivos" e o filtro PADRAO (1o): programas Fanuc tipo 'O2169'
        # nao tem extensao e ficariam escondidos por um filtro so de *.nc/*.txt.
        files, _ = QFileDialog.getOpenFileNames(
            self, "Escolher programa(s) NC", "",
            "Todos os arquivos (*.*);;Programas CNC (*.nc *.txt *.iso *.ptp *.min *.mpf "
            "*.cnc *.prg *.eia *.tap *.gcode *.ngc *.mpf *.spf *.h *.pgm *.din *.dnc)")
        if files:
            self._set_programs([Path(f) for f in files], "varios" if len(files) > 1 else files[0])

    def _set_programs(self, programs: list[Path], src_label: str) -> None:
        self._programs = programs
        self._file_subs = {}
        self._current = None
        self._seed_file_subs()
        self.lbl_src.setText(f"{len(programs)} programa(s) — {src_label}")
        self._loading = True
        self.lst_prog.clear()
        for p in programs:
            it = QListWidgetItem(p.name)
            it.setFlags(it.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            it.setCheckState(Qt.CheckState.Checked)
            it.setData(Qt.ItemDataRole.UserRole, str(p))
            self.lst_prog.addItem(it)
        self._loading = False
        self.tbl_file.setRowCount(0)
        if programs:
            self.lst_prog.setCurrentRow(0)
        self._set_status(f"{len(programs)} programa(s) carregado(s). "
                         f"Marque, defina as trocas e clique Executar substituicoes.",
                         warn=not programs)

    def _on_program_selected(self, row: int) -> None:
        if self._loading:
            return
        self._commit_file_table()
        if row < 0:
            self._current = None
            self.tbl_file.setRowCount(0)
            self.lbl_prog.setText("Trocas SO DESTE programa:  (selecione um programa)")
            return
        p = Path(self.lst_prog.item(row).data(Qt.ItemDataRole.UserRole))
        self._current = str(p.resolve())
        self.lbl_prog.setText(f"Trocas SO DE:  {p.name}")
        self._load_subs_table(self.tbl_file, self._file_subs.get(self._current, []))

    def _commit_file_table(self) -> None:
        if self._current is not None:
            self._file_subs[self._current] = self._read_subs_table(self.tbl_file)

    def _checked_programs(self) -> list[Path]:
        out = []
        for i in range(self.lst_prog.count()):
            it = self.lst_prog.item(i)
            if it.checkState() is Qt.CheckState.Checked:
                out.append(Path(it.data(Qt.ItemDataRole.UserRole)))
        return out

    # ============ executar substituicoes ============
    def _rules_for(self, name: str, common: list, perfile: list) -> list[Rule]:
        rules: list[Rule] = []
        for row in common:
            act, find, repl, obs = row[:4]
            on_zero = row[4] if len(row) > 4 else OnZeroMatches.WARN
            if act and find:
                rules.append(Rule(id=f"c_{uuid.uuid4().hex[:6]}", find=find, replace=repl,
                                  scope=Scope.GLOBAL, mode=Mode.AUTO, comment=obs,
                                  on_zero_matches=on_zero))
        for row in perfile:
            act, find, repl, obs = row[:4]
            on_zero = row[4] if len(row) > 4 else OnZeroMatches.WARN
            if act and find:
                rules.append(Rule(id=f"f_{uuid.uuid4().hex[:6]}", find=find, replace=repl,
                                  scope=Scope.FILE, file=name, mode=Mode.AUTO, comment=obs,
                                  on_zero_matches=on_zero))
        return rules

    def _build_outcomes(self, checked: list[Path], common: list, cs: bool) -> tuple[list[FileOutcome], bool]:
        outcomes: list[FileOutcome] = []
        blocked = False
        for p in checked:
            rules = self._rules_for(p.name, common, self._file_subs.get(str(p.resolve()), []))
            o = FileOutcome(name=p.name)
            try:
                text, info = read_file(p)
            except BinaryFileError as exc:
                o.read_error = str(exc)
                outcomes.append(o)
                blocked = True
                continue
            plan = build_plan(text, rules, cs, current_file=p.name)
            result = apply_edits(text, plan.edits)
            o.info, o.original, o.result = info, text, result
            o.edits, o.suppressions = plan.edits, plan.suppressions
            o.alerts = [(r.severity, r.label, r.message) for r in run_structural(text, result)]
            for r in rules:
                n = plan.match_count_by_rule.get(r.id, 0)
                oz = r.on_zero_matches
                oz_label = oz.value if isinstance(oz, OnZeroMatches) else str(oz)
                o.checklist.append((r.find, r.replace, n, oz_label))
                if n == 0:
                    if r.on_zero_matches is OnZeroMatches.IGNORE:
                        continue
                    hint = suggest_leading_zero_variant(text, r.find)
                    extra = f" (achei '{hint}'?)" if hint else ""
                    nivel = "[ERRO]" if r.on_zero_matches is OnZeroMatches.ERROR else "[aviso]"
                    o.zero.append(f"{nivel} '{r.find}'->'{r.replace}': 0 ocorrencias{extra}")
                    if r.on_zero_matches is OnZeroMatches.ERROR:
                        blocked = True
            if o.worst() is Severity.CRITICAL:
                blocked = True
            outcomes.append(o)
        return outcomes, blocked

    def _on_execute_subs(self) -> None:
        self._commit_file_table()
        if not self._programs:
            QMessageBox.warning(self, "Sem programas", "Abra uma pasta ou programa(s).")
            return
        checked = self._checked_programs()
        if not checked:
            QMessageBox.warning(self, "Nenhum marcado", "Marque ao menos um programa.")
            return
        basenames = [p.name for p in checked]
        dupes = sorted({n for n in basenames if basenames.count(n) > 1})
        if dupes:
            QMessageBox.critical(
                self, "Nomes duplicados no lote",
                "Os arquivos abaixo tem o mesmo nome e nao podem ser processados juntos:\n\n"
                + "\n".join(dupes)
                + "\n\nProcesse cada pasta separadamente.",
            )
            return
        parents = {p.parent for p in checked}
        if len(parents) > 1:
            QMessageBox.critical(
                self, "Multiplas pastas",
                "Os programas marcados estao em pastas diferentes.\n"
                "Abra e processe cada pasta separadamente.",
            )
            return
        common = self._read_subs_table(self.tbl_common)
        cs = self._preset.case_sensitive if self._preset else False
        outcomes, blocked = self._build_outcomes(checked, common, cs)
        if not any(o.edits for o in outcomes if not o.read_error):
            QMessageBox.information(self, "Nada a trocar",
                                    "Nenhuma das trocas marcadas encontrou ocorrencia nos "
                                    "programas marcados. Confira os codigos (ex.: M8 x M08).")
        items = [(o.name, o.worst().value, self._detail(o)) for o in outcomes]
        dlg = PreviewDialog(self._summary(outcomes, blocked), items, blocked, self)
        dlg.exec()
        if dlg.confirmed:
            self._save(outcomes, checked)

    def _summary(self, outcomes: list[FileOutcome], blocked: bool) -> str:
        total = sum(len(o.edits) for o in outcomes if not o.read_error)
        lines = [f"Programas: {len(outcomes)}   Trocas no total: {total}", ""]
        zeros = {z for o in outcomes for z in o.zero}
        if zeros:
            lines.append("Trocas marcadas que NAO encontraram nada em algum programa:")
            lines += [f"  - {z}" for z in sorted(zeros)]
            lines.append("")
        lines.append(">>> SALVAR BLOQUEADO: ha programa com erro estrutural (vermelho)." if blocked
                     else "Ok para salvar. Originais NUNCA sao alterados; saida vai p/ pasta separada.")
        return "\n".join(lines)

    def _detail(self, o: FileOutcome) -> str:
        if o.read_error:
            return f"{o.name}\n\nERRO DE LEITURA: {o.read_error}"
        info = o.info
        lines = [f"{o.name}   [{info.encoding} / {info.confidence} / EOL {info.eol!r}]",
                 f"Trocas aplicadas: {len(o.edits)}", ""]
        if o.checklist:
            lines.append("--- CHECKLIST DE TROCAS PLANEJADAS ---")
            for find, replace, count, oz in o.checklist:
                repl_str = repr(replace) if replace else "(remover)"
                if count > 0:
                    lines.append(f"  [OK] {find!r} -> {repl_str}: {count} ocorrencia(s)")
                elif oz == "ignore":
                    lines.append(f"  [--] {find!r} -> {repl_str}: 0 ocorrencias (ignorado)")
                elif oz == "error":
                    lines.append(f"  [ERRO] {find!r} -> {repl_str}: 0 ocorrencias (BLOQUEIA SALVAR)")
                else:
                    lines.append(f"  [aviso] {find!r} -> {repl_str}: 0 ocorrencias")
            lines.append("")
        for e in o.edits:
            ln = o.original.count("\n", 0, e.start) + 1
            lines.append(f"  linha {ln:>4}: {e.matched!r} -> {e.replacement!r}")
        for s in o.suppressions:
            lines.append(f"  [conflito] {s.reason}")
        for sev, label, msg in o.alerts:
            lines.append(f"  [{'VERMELHO' if sev is Severity.CRITICAL else 'amarelo'}] {label}: {msg}")
        for z in o.zero:
            lines.append(f"  [amarelo] {z}")
        lines.append("\n--- preview (linhas alteradas) ---")
        diff = difflib.unified_diff(o.original.splitlines(), o.result.splitlines(), lineterm="", n=1)
        body = [d for d in diff if d and d[0] in "+-" and not d.startswith(("+++", "---"))]
        lines += body[:80] or ["  (sem alteracoes neste programa)"]
        return "\n".join(lines)

    def _save(self, outcomes: list[FileOutcome], checked: list[Path]) -> None:
        base_dir = self._effective_base_dir()
        if self._settings.output_mode == "fixa" and not base_dir:
            QMessageBox.warning(self, "Pasta nao configurada",
                                "Selecione uma pasta fixa de destino antes de salvar.")
            return
        src_dir = checked[0].parent
        machine = self._preset.machine if self._preset else "PERFIL"
        items = [
            (o.name, o.result, o.info)
            for o in outcomes
            if not o.read_error and o.info is not None
        ]
        try:
            encoded = encode_batch(items)
            out_dir = make_output_dir(src_dir, machine, base_dir=base_dir)
            write_encoded_batch(out_dir, encoded)
        except BatchEncodeError as exc:
            QMessageBox.critical(self, "Erro de codificacao", str(exc))
            return
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Erro ao salvar", str(exc))
            return

        # --- Sessao D: conferencia pos-salvamento ---
        log = SessionLog()
        log.add(f"Lote salvo em: {out_dir}")
        integrity_ok = True
        try:
            integrity_results = verify_saved(out_dir, encoded)
            report = format_integrity_report(integrity_results)
            log.add(report)
            integrity_ok = all(r.ok for r in integrity_results)
        except Exception as exc:  # noqa: BLE001
            log.add(f"Conferencia pos-salvamento falhou: {exc}")
            integrity_ok = False

        for o in outcomes:
            if not o.read_error and o.info is not None:
                n_trocas = len(o.edits)
                log.add(f"{o.name}: {n_trocas} troca(s)")
                for find, replace, count, _ in o.checklist:
                    log.add(f"  {find!r} -> {replace!r}: {count} ocorrencia(s)")

        log.export_txt(out_dir.parent / f"{out_dir.name}_log.txt")

        saved = len(encoded)
        msg = f"{saved} programa(s) salvos em:\n{out_dir}\n\nOriginais intactos."
        if not integrity_ok:
            msg += "\n\nATENCAO: Falha na conferencia de integridade!\nVerifique o log para detalhes."
            QMessageBox.warning(self, "Salvo com alerta", msg)
        else:
            QMessageBox.information(self, "Salvo", msg)
        self._set_status(
            f"Salvo: {saved} em {out_dir.name}"
            + (" [INTEGRIDADE OK]" if integrity_ok else " [ATENCAO: falha integridade]")
        )

    # ============ executar verificacoes ============
    def _on_execute_verifs(self) -> None:
        if not self._programs:
            QMessageBox.warning(self, "Sem programas", "Abra uma pasta ou programa(s).")
            return
        verifs = self._read_verifs()
        if not verifs:
            QMessageBox.information(self, "Sem verificacoes", "Marque/adicione verificacoes.")
            return
        checked = self._checked_programs()
        cs = self._preset.case_sensitive if self._preset else False
        out = []
        for p in checked:
            try:
                text, _ = read_file(p)
            except BinaryFileError as exc:
                out.append(f"{p.name}: ERRO DE LEITURA ({exc})")
                continue
            res = run_configurable(text, verifs, cs)
            if not res:
                out.append(f"{p.name}: OK (todas passaram)")
            else:
                out.append(f"{p.name}:")
                out += [f"   [amarelo] {r.label}: {r.message}" for r in res]
        self.txt_verif.setPlainText("\n".join(out) or "(nenhum programa marcado)")
        self._set_status("Verificacoes concluidas.")

    # ============ salvar perfil ============
    def _on_save_profile(self) -> None:
        if self._preset is None:
            QMessageBox.warning(self, "Sem perfil", "Selecione um perfil.")
            return
        self._commit_file_table()
        self._preset.global_rules = [
            Rule(id=f"g_{uuid.uuid4().hex[:8]}", find=f, replace=rp, scope=Scope.GLOBAL,
                 mode=Mode.AUTO, active=a, comment=o, on_zero_matches=oz)
            for a, f, rp, o, oz in self._read_subs_table(self.tbl_common) if f]
        file_rules = []
        for key, rows in self._file_subs.items():
            basename = Path(key).name
            for row in rows:
                a, f, rp, o = row[:4]
                oz = row[4] if len(row) > 4 else OnZeroMatches.WARN
                if f:
                    file_rules.append(Rule(id=f"f_{uuid.uuid4().hex[:8]}", find=f, replace=rp,
                                           scope=Scope.FILE, file=basename, mode=Mode.AUTO,
                                           active=a, comment=o, on_zero_matches=oz))
        self._preset.file_rules = file_rules
        try:
            save_preset(self._preset, Path(self.cb_preset.currentData()))
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Erro", str(exc))
            return
        QMessageBox.information(self, "Perfil salvo", f"Trocas salvas em '{self._preset.machine}'.")

    # ============ configuracoes de destino ============
    def _load_settings(self) -> None:
        self._settings = load_settings(app_paths.settings_path())
        if self._settings.output_mode == "fixa":
            self.rb_fixo.setChecked(True)
            self.le_dest_dir.setText(self._settings.output_dir)
        else:
            self.rb_ao_lado.setChecked(True)

    def _save_settings(self) -> None:
        try:
            save_settings(app_paths.settings_path(), self._settings)
        except Exception:
            pass  # falha silenciosa: preferencia nao critica

    def _on_dest_mode_changed(self) -> None:
        mode = "ao_lado" if self.rb_ao_lado.isChecked() else "fixa"
        self._settings.output_mode = mode
        self._save_settings()

    def _on_dest_browse(self) -> None:
        d = QFileDialog.getExistingDirectory(self, "Escolher pasta de destino")
        if d:
            self.rb_fixo.setChecked(True)
            self.le_dest_dir.setText(d)
            self._settings.output_mode = "fixa"
            self._settings.output_dir = d
            self._save_settings()

    def _effective_base_dir(self) -> Path | None:
        if self._settings.output_mode == "fixa" and self._settings.output_dir:
            return Path(self._settings.output_dir)
        return None

    # ============ CRUD de perfis ============
    def _preset_dir(self) -> Path:
        return app_paths.presets_dir()

    def _ask_name(self, titulo: str, label: str, default: str = "") -> str | None:
        name, ok = QInputDialog.getText(self, titulo, label, text=default)
        return name.strip() if ok and name.strip() else None

    def _on_preset_new(self) -> None:
        name = self._ask_name("Novo perfil", "Nome do novo perfil:")
        if not name:
            return
        try:
            self._preset_dir().mkdir(parents=True, exist_ok=True)
            create_preset(name, self._preset_dir())
        except PresetError as exc:
            QMessageBox.critical(self, "Erro", str(exc))
            return
        self._load_presets()
        idx = self.cb_preset.findText(name)
        if idx >= 0:
            self.cb_preset.setCurrentIndex(idx)

    def _on_preset_duplicate(self) -> None:
        src_path = self.cb_preset.currentData()
        if not src_path:
            QMessageBox.warning(self, "Sem perfil", "Selecione um perfil para duplicar.")
            return
        default = self.cb_preset.currentText() + "_copia"
        name = self._ask_name("Duplicar perfil", "Nome da copia:", default)
        if not name:
            return
        try:
            duplicate_preset(Path(src_path), name)
        except PresetError as exc:
            QMessageBox.critical(self, "Erro", str(exc))
            return
        self._load_presets()
        idx = self.cb_preset.findText(name)
        if idx >= 0:
            self.cb_preset.setCurrentIndex(idx)

    def _on_preset_rename(self) -> None:
        src_path = self.cb_preset.currentData()
        if not src_path:
            QMessageBox.warning(self, "Sem perfil", "Selecione um perfil para renomear.")
            return
        name = self._ask_name("Renomear perfil", "Novo nome:", self.cb_preset.currentText())
        if not name:
            return
        try:
            rename_preset(Path(src_path), name)
        except PresetError as exc:
            QMessageBox.critical(self, "Erro", str(exc))
            return
        self._load_presets()
        idx = self.cb_preset.findText(name)
        if idx >= 0:
            self.cb_preset.setCurrentIndex(idx)

    def _on_preset_delete(self) -> None:
        src_path = self.cb_preset.currentData()
        current_name = self.cb_preset.currentText()
        if not src_path:
            QMessageBox.warning(self, "Sem perfil", "Selecione um perfil para excluir.")
            return
        resp = QMessageBox.question(
            self, "Excluir perfil",
            f"Excluir o perfil '{current_name}'?\n\nUm backup sera criado automaticamente.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resp != QMessageBox.StandardButton.Yes:
            return
        resp2 = QMessageBox.warning(
            self, "Confirmar exclusao",
            f"Tem certeza? O perfil '{current_name}' sera removido.\n(backup em _backups/)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
        )
        if resp2 != QMessageBox.StandardButton.Yes:
            return
        try:
            delete_preset(Path(src_path))
        except PresetError as exc:
            QMessageBox.critical(self, "Erro", str(exc))
            return
        self._load_presets()

    # ============ biblioteca de codigos ============
    def _load_library(self) -> None:
        try:
            self._library = load_library(app_paths.library_path())
        except LibraryError:
            self._library = []

    def _on_from_library(self, t: QTableWidget) -> None:
        if not self._library:
            QMessageBox.information(self, "Biblioteca vazia",
                                    "Nenhum codigo cadastrado. Use 'Gerenciar codigos...' para adicionar.")
            return
        dlg = LibraryPickerDialog(self._library, self)
        if dlg.exec() and dlg.selected:
            for e in dlg.selected:
                self._add_subs_row(t, True, e.find, e.replace, e.label)

    def _on_manage_library(self) -> None:
        dlg = LibraryDialog(self._library, app_paths.library_path(), self)
        dlg.exec()
        self._library = dlg.current_entries()

    # ============ editor por arquivo ============
    def _guard_unsaved(self) -> bool:
        """Se o editor tem alteracao pendente, pergunta salvar/descartar/cancelar.

        Retorna True se pode prosseguir (salvou ou descartou), False se cancelou.
        """
        if not self._editor.tem_alteracao():
            return True
        resp = QMessageBox.question(
            self, "Alteracoes nao salvas",
            "Ha alteracoes nao salvas no editor. Salvar antes de trocar?",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
        )
        if resp == QMessageBox.StandardButton.Save:
            return self._editor.salvar()
        if resp == QMessageBox.StandardButton.Discard:
            return True
        return False  # Cancel: preserva a edicao

    def _on_edit_program(self) -> None:
        row = self.lst_prog.currentRow()
        if row < 0:
            QMessageBox.information(self, "Sem programa", "Selecione um programa na lista.")
            return
        if not self._guard_unsaved():
            return
        path = Path(self.lst_prog.item(row).data(Qt.ItemDataRole.UserRole))
        self._editor.set_library(self._library)
        self._editor.set_case_sensitive(self._preset.case_sensitive if self._preset else True)
        try:
            self._editor.abrir(path)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Erro ao abrir", f"Nao foi possivel abrir o arquivo:\n{exc}")
            return
        self._right_stack.setCurrentWidget(self._editor)

    def _close_editor(self) -> None:
        if not self._guard_unsaved():
            return
        self._right_stack.setCurrentIndex(0)

    def _set_status(self, text: str, warn: bool = False) -> None:
        self.lbl_status.setText(text)
        self.lbl_status.setStyleSheet("color:#b35900;" if warn else "color:#225522;")
