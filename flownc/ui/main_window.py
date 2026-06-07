"""Janela principal do FlowNC — maestro do layout de 2 colunas (redesign-layout-principal).

MainWindow instancia os 4 componentes isolados (`HeaderBar`, `CompositorPanel`,
`ProgramListPanel`, `SummaryPanel`), conecta os sinais e mantem TODO o estado de
negocio (preset, programas, regras montadas). Layout: header fixo no topo +
`QSplitter` horizontal; a coluna direita e um `QStackedWidget` que alterna entre
o resumo (SummaryPanel) e o editor por arquivo (EditorPanel). A logica de
substituicao reusa integralmente o core/ (puro).
"""
from __future__ import annotations

import difflib
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from core.conference import format_integrity_report, verify_saved

from PySide6.QtCore import Qt
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

import app_paths
from core.batch import validate_batch
from core.library_store import CodeEntry, LibraryError, load_library
from core.settings_store import AppSettings, load_settings
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
)
from core.preset_store import PresetError, load_preset
from core.scan import count_occurrences
from core.replacement_plan import build_plan
from core.replacer import apply_edits
from core.session_log import SessionLog
from core.verifier import run_structural
from ui.components import CompositorPanel, HeaderBar, ProgramListPanel, SummaryPanel
from ui.editor_panel import EditorPanel
from ui.library_dialog import LibraryDialog
from ui.preview_dialog import PreviewDialog


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
        self._register_fonts()
        self._apply_stylesheet()
        self.setWindowTitle("FlowNC — Substituicoes em programas CNC")
        self.resize(1180, 720)
        self._preset: Preset | None = None
        self._preset_paths: dict[str, str] = {}
        self._programs: list[Path] = []
        self._file_subs: dict[str, list[tuple[bool, str, str, str]]] = {}
        self._current: str | None = None
        self._library: list[CodeEntry] = []
        self._settings: AppSettings = AppSettings()

        self._build_ui()
        self._connect_signals()
        self._load_library()
        self._load_presets()
        self._load_settings()

    # ============ tema visual ============
    def _register_fonts(self) -> None:
        fonts_dir = app_paths.fonts_dir()
        for ttf in fonts_dir.glob("*.ttf"):
            font_id = QFontDatabase.addApplicationFont(str(ttf))
            if font_id < 0:
                import sys
                print(f"[FlowNC] fonte nao carregada: {ttf}", file=sys.stderr)

    def _apply_stylesheet(self) -> None:
        qss_file = app_paths.qss_path()
        try:
            qss = qss_file.read_text(encoding="utf-8")
            self.setStyleSheet(qss)
        except OSError:
            pass  # sem QSS: app usa estilo padrao do Qt

    # ============ construcao (maestro) ============
    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._header = HeaderBar()
        root.addWidget(self._header)

        self._splitter = QSplitter(Qt.Orientation.Horizontal)

        left = QWidget()
        lv = QVBoxLayout(left)
        lv.setContentsMargins(8, 8, 8, 8)
        self._compositor = CompositorPanel()
        lv.addWidget(self._compositor, stretch=0)
        self._program_list = ProgramListPanel()
        lv.addWidget(self._program_list, stretch=1)
        self._splitter.addWidget(left)

        self._stack = QStackedWidget()
        self._summary = SummaryPanel()
        self._stack.addWidget(self._summary)               # indice 0
        self._editor_panel = EditorPanel(self._library, parent=self)
        self._stack.addWidget(self._editor_panel)          # indice 1
        self._splitter.addWidget(self._stack)
        self._splitter.setSizes([600, 400])
        root.addWidget(self._splitter, stretch=1)

        self.lbl_status = QLabel("Selecione um perfil e abra os programas.")
        self.lbl_status.setContentsMargins(8, 4, 8, 4)
        root.addWidget(self.lbl_status)

    def _connect_signals(self) -> None:
        self._header.perfil_alterado.connect(self._on_preset_changed_by_name)
        self._header.abrir_pasta_solicitado.connect(self._open_folder)
        self._header.abrir_arquivos_solicitado.connect(self._open_files)
        self._header.biblioteca_solicitada.connect(self._open_library_dialog)
        self._header.adicionar_codigo_solicitado.connect(self._open_library_dialog)
        self._header.salvar_perfil_solicitado.connect(self._save_profile_stub)
        self._compositor.regra_adicionada.connect(self._on_regra_adicionada)
        self._compositor.regra_removida.connect(self._on_regra_removida)
        self._program_list.editar_arquivo.connect(self._abrir_editor)
        self._program_list.adicionar_programas_solicitado.connect(self._open_files)
        self._program_list.lst_prog.currentRowChanged.connect(self._on_program_selected)
        self._summary.publicar_solicitado.connect(self._on_aplicar)
        self._editor_panel.closeRequested.connect(self._fechar_editor)

    # ============ presets ============
    def _load_presets(self) -> None:
        pdir = app_paths.presets_dir()
        files = sorted(pdir.glob("*.json")) if pdir.is_dir() else []
        self._preset_paths = {f.stem: str(f) for f in files}
        names = list(self._preset_paths.keys())
        self._header.set_presets(names)
        if names:
            self._header.set_preset_atual(names[0])
            self._on_preset_changed_by_name(names[0])

    def _on_preset_changed_by_name(self, nome: str) -> None:
        path = self._preset_paths.get(nome)
        if not path:
            self._preset = None
            return
        try:
            self._preset = load_preset(Path(path))
        except PresetError as exc:
            self._preset = None
            QMessageBox.critical(self, "Perfil invalido", str(exc))
            return
        self._header.set_preset_atual(nome)
        self._editor_panel.set_case_sensitive(self._preset.case_sensitive)
        self._compositor.set_library(self._library)
        self._refresh_summary()
        self._set_status(f"Perfil '{self._preset.machine}' carregado.")

    # ============ compositor -> summary ============
    def _on_regra_adicionada(self, _rule: Rule) -> None:
        self._refresh_summary()

    def _on_regra_removida(self, _idx: int) -> None:
        self._refresh_summary()

    # ============ abrir programas ============
    def _open_folder(self) -> None:
        d = QFileDialog.getExistingDirectory(self, "Escolher pasta com programas NC")
        if d:
            exts = self._preset.extensions if self._preset else ["*"]
            self._set_programs(list_input_files(Path(d), exts), d)

    def _open_files(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self, "Escolher programa(s) NC", "",
            "Todos os arquivos (*.*);;Programas CNC (*.nc *.txt *.iso *.ptp *.min *.mpf "
            "*.cnc *.prg *.eia *.tap *.gcode *.ngc *.mpf *.spf *.h *.pgm *.din *.dnc)")
        if files:
            self._set_programs([Path(f) for f in files],
                               "varios" if len(files) > 1 else files[0])

    def _set_programs(self, programs: list[Path], src_label: str) -> None:
        self._programs = programs
        self._file_subs = {}
        self._current = None
        self._program_list.set_programs(programs)
        self._refresh_summary()
        self._set_status(
            f"{len(programs)} programa(s) — {src_label}. "
            f"Monte as edicoes e clique Executar Lote.",
            warn=not programs,
        )

    def _on_program_selected(self, row: int) -> None:
        if row < 0:
            self._current = None
            self._refresh_summary()
            return
        item = self._program_list.lst_prog.item(row)
        if item is None:
            self._current = None
            self._refresh_summary()
            return
        p = Path(item.data(Qt.ItemDataRole.UserRole))
        self._current = str(p.resolve())
        self._refresh_summary()

    def _read_text_for_scan(self, path: Path) -> str:
        text, _info = read_file(path)
        return text

    def _refresh_summary(self) -> None:
        if not hasattr(self, "_summary"):
            return
        regras = self._compositor.get_regras()
        checked = self._program_list.get_selecionados()
        cs = self._preset.case_sensitive if self._preset else True
        issues = validate_batch(regras, self._library)
        occurrences: dict[str, tuple[int, int]] = {}
        total_changes = 0

        for rule in regras:
            files = [
                path for path in checked
                if rule.scope is Scope.GLOBAL or self._current == str(path.resolve())
            ]
            if not files:
                occurrences[rule.id] = (0, 0)
                continue
            try:
                scan = count_occurrences(
                    rule.find,
                    rule.mode,
                    cs,
                    files,
                    self._read_text_for_scan,
                )
            except Exception:  # noqa: BLE001
                occurrences[rule.id] = (0, len(files))
                continue
            rule_total = sum(scan.counts.values())
            total_changes += rule_total
            occurrences[rule.id] = (rule_total, len(scan.files_with_matches))

        backup_path = self._settings.backup_dir or self._settings.output_dir
        self._summary.set_summary(
            regras,
            program_count=len(checked),
            change_count=total_changes,
            occurrences_by_rule=occurrences,
            issues=issues,
            backup_path=backup_path,
        )

    # ============ executar substituicoes (core puro) ============
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

    def _outcome_for(self, p: Path, rules: list[Rule], cs: bool) -> tuple[FileOutcome, bool]:
        """Constroi o resultado de um programa. Retorna (outcome, bloqueia_salvar)."""
        o = FileOutcome(name=p.name)
        try:
            text, info = read_file(p)
        except BinaryFileError as exc:
            o.read_error = str(exc)
            return o, True
        blocked = False
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
        return o, blocked

    def _build_outcomes(self, checked: list[Path], common: list,
                        cs: bool) -> tuple[list[FileOutcome], bool]:
        outcomes: list[FileOutcome] = []
        blocked = False
        for p in checked:
            rules = self._rules_for(p.name, common, self._file_subs.get(str(p.resolve()), []))
            o, b = self._outcome_for(p, rules, cs)
            outcomes.append(o)
            blocked = blocked or b
        return outcomes, blocked

    def _rules_for_program(self, p: Path, regras: list[Rule]) -> list[Rule]:
        """Regras aplicaveis a um programa: GLOBAL sempre; FILE so no selecionado."""
        out: list[Rule] = []
        for r in regras:
            if r.scope is Scope.GLOBAL:
                out.append(r)
            elif r.scope is Scope.FILE and self._current == str(p.resolve()):
                out.append(Rule(id=r.id, find=r.find, replace=r.replace, scope=Scope.FILE,
                                file=p.name, mode=r.mode, comment=r.comment,
                                on_zero_matches=r.on_zero_matches))
        return out

    def _on_aplicar(self) -> None:
        if not self._programs:
            QMessageBox.warning(self, "Sem programas", "Abra uma pasta ou programa(s).")
            return
        checked = self._program_list.get_selecionados()
        if not checked:
            QMessageBox.warning(self, "Nenhum marcado", "Marque ao menos um programa.")
            return
        regras = self._compositor.get_regras()
        if not regras:
            QMessageBox.information(self, "Sem edicoes",
                                    "Monte ao menos uma edicao no compositor.")
            return
        basenames = [p.name for p in checked]
        dupes = sorted({n for n in basenames if basenames.count(n) > 1})
        if dupes:
            QMessageBox.critical(
                self, "Nomes duplicados no lote",
                "Os arquivos abaixo tem o mesmo nome e nao podem ser processados juntos:\n\n"
                + "\n".join(dupes) + "\n\nProcesse cada pasta separadamente.",
            )
            return
        if len({p.parent for p in checked}) > 1:
            QMessageBox.critical(
                self, "Multiplas pastas",
                "Os programas marcados estao em pastas diferentes.\n"
                "Abra e processe cada pasta separadamente.",
            )
            return
        cs = self._preset.case_sensitive if self._preset else False
        outcomes: list[FileOutcome] = []
        blocked = False
        for p in checked:
            o, b = self._outcome_for(p, self._rules_for_program(p, regras), cs)
            outcomes.append(o)
            blocked = blocked or b
        if not any(o.edits for o in outcomes if not o.read_error):
            QMessageBox.information(self, "Nada a trocar",
                                    "Nenhuma das edicoes encontrou ocorrencia nos programas "
                                    "marcados. Confira os codigos (ex.: M8 x M08).")
        items = [(o.name, o.worst().value, self._detail(o)) for o in outcomes]
        dlg = PreviewDialog(self._summary_text(outcomes, blocked), items, blocked, self)
        dlg.exec()
        if dlg.confirmed:
            self._save(outcomes, checked)

    def _summary_text(self, outcomes: list[FileOutcome], blocked: bool) -> str:
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

        # --- conferencia pos-salvamento ---
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
                log.add(f"{o.name}: {len(o.edits)} troca(s)")
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

    def _effective_base_dir(self) -> Path | None:
        if self._settings.output_mode == "fixa" and self._settings.output_dir:
            return Path(self._settings.output_dir)
        return None

    # ============ biblioteca / settings ============
    def _load_library(self) -> None:
        try:
            self._library = load_library(app_paths.library_path())
        except LibraryError:
            self._library = []
        self._compositor.set_library(self._library)
        self._editor_panel.set_library(self._library)
        self._refresh_summary()

    def _load_settings(self) -> None:
        self._settings = load_settings(app_paths.settings_path())
        self._refresh_summary()

    def _open_library_dialog(self) -> None:
        dlg = LibraryDialog(self._library, app_paths.library_path(), self)
        dlg.exec()
        self._library = dlg.current_entries()
        self._compositor.set_library(self._library)
        self._editor_panel.set_library(self._library)
        self._refresh_summary()

    def _save_profile_stub(self) -> None:
        QMessageBox.information(
            self,
            "Salvar perfil",
            "O perfil atual permanece carregado. A biblioteca ja salva codigos; "
            "a persistencia completa do perfil sera consolidada na proxima fase.",
        )

    # ============ editor por arquivo ============
    def _guard_unsaved(self) -> bool:
        """Se o editor tem alteracao pendente, pergunta salvar/descartar/cancelar.

        Retorna True se pode prosseguir (salvou ou descartou), False se cancelou.
        """
        if not self._editor_panel.tem_alteracao():
            return True
        resp = QMessageBox.question(
            self, "Alteracoes nao salvas",
            "Ha alteracoes nao salvas no editor. Salvar antes de trocar?",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
        )
        if resp == QMessageBox.StandardButton.Save:
            return self._editor_panel.salvar()
        if resp == QMessageBox.StandardButton.Discard:
            return True
        return False  # Cancel: preserva a edicao

    def _abrir_editor(self, path: str) -> None:
        if not self._guard_unsaved():
            return
        self._editor_panel.set_library(self._library)
        self._editor_panel.set_case_sensitive(
            self._preset.case_sensitive if self._preset else True)
        try:
            self._editor_panel.abrir(Path(path))
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Erro ao abrir", f"Nao foi possivel abrir o arquivo:\n{exc}")
            return
        self._stack.setCurrentIndex(1)
        self._splitter.setSizes([400, 600])

    def _fechar_editor(self) -> None:
        if not self._guard_unsaved():
            return
        self._stack.setCurrentIndex(0)
        self._splitter.setSizes([600, 400])

    def _set_status(self, text: str, warn: bool = False) -> None:
        self.lbl_status.setText(text)
        self.lbl_status.setStyleSheet("color:#b35900;" if warn else "color:#225522;")
