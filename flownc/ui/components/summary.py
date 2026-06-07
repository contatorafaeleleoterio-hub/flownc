"""SummaryPanel: painel 3 do mockup aprovado.

O painel apenas renderiza o estado do lote. O `MainWindow` calcula contadores,
conflitos e ocorrencias usando o core e injeta tudo por `set_summary()`.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.models import Issue, Rule, Scope, Severity
from ui.theme import FONT_MONO, H_CTA


def _scope_label(rule: Rule) -> str:
    return "todos" if rule.scope is Scope.GLOBAL else "sel."


def _replace_label(rule: Rule) -> str:
    return rule.replace or "(remover)"


class SummaryPanel(QWidget):
    """Resumo rico do lote conforme `mockups/painel-final.v2.html`."""

    publicar_solicitado = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("SummaryPanel")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)

        head = QHBoxLayout()
        self.lbl_title = QLabel("3  Resumo")
        self.lbl_title.setProperty("heading", True)
        head.addWidget(self.lbl_title)
        head.addStretch(1)
        self.lbl_state = QLabel("✓ Pronto")
        self.lbl_state.setObjectName("StateChip")
        self.lbl_state.setProperty("state", "ok")
        head.addWidget(self.lbl_state)
        root.addLayout(head)

        counters = QHBoxLayout()
        self.lbl_rules_n = self._make_counter("0", "Regras")
        self.lbl_programs_n = self._make_counter("0", "Programas")
        self.lbl_changes_n = self._make_counter("0", "Alterações")
        counters.addWidget(self.lbl_rules_n)
        counters.addWidget(self.lbl_programs_n)
        counters.addWidget(self.lbl_changes_n)
        root.addLayout(counters)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._cards_host = QWidget()
        self._cards_layout = QVBoxLayout(self._cards_host)
        self._cards_layout.addStretch(1)
        self._scroll.setWidget(self._cards_host)
        root.addWidget(self._scroll, stretch=1)

        self.lbl_backup = QLabel("🛡 Originais preservados → backup será criado ao publicar")
        self.lbl_backup.setObjectName("BackupSeal")
        root.addWidget(self.lbl_backup)

        self.btn_aplicar = QPushButton("Executar Lote\nPré-visualizar antes de publicar")
        self.btn_aplicar.setObjectName("CTA")
        self.btn_aplicar.setProperty("primary", True)
        self.btn_aplicar.setFixedHeight(H_CTA)
        self.btn_aplicar.clicked.connect(self.publicar_solicitado.emit)
        root.addWidget(self.btn_aplicar)

    def _make_counter(self, value: str, label: str) -> QLabel:
        widget = QLabel(f"<b>{value}</b><br><span>{label}</span>")
        widget.setObjectName("Counter")
        widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return widget

    def set_rules(self, rules: list[Rule]) -> None:
        self.set_summary(rules)

    def set_summary(
        self,
        rules: list[Rule],
        program_count: int = 0,
        change_count: int = 0,
        occurrences_by_rule: dict[str, tuple[int, int]] | None = None,
        issues: list[Issue] | None = None,
        backup_path: str = "",
    ) -> None:
        issues = issues or []
        occurrences_by_rule = occurrences_by_rule or {}
        warning_count = sum(1 for issue in issues if issue.severity is Severity.WARNING)
        self.lbl_state.setText(f"⚠ {warning_count} conflito" if warning_count else "✓ Pronto")
        self.lbl_state.setProperty("state", "warn" if warning_count else "ok")
        self.lbl_state.style().unpolish(self.lbl_state)
        self.lbl_state.style().polish(self.lbl_state)

        self.lbl_rules_n.setText(f"<b>{len(rules)}</b><br><span>Regras</span>")
        self.lbl_programs_n.setText(f"<b>{program_count}</b><br><span>Programas</span>")
        self.lbl_changes_n.setText(f"<b>{change_count}</b><br><span>Alterações</span>")
        self.lbl_backup.setText(
            "🛡 Originais preservados → "
            + (backup_path if backup_path else "backup será criado ao publicar")
        )

        while self._cards_layout.count() > 1:
            item = self._cards_layout.takeAt(0)
            widget = item.widget() if item is not None else None
            if widget is not None:
                widget.deleteLater()

        conflicted = {rule_id for issue in issues for rule_id in issue.rule_ids}
        for idx, rule in enumerate(rules, start=1):
            issue_texts = [issue.message for issue in issues if rule.id in issue.rule_ids]
            counts = occurrences_by_rule.get(rule.id, (0, 0))
            card = self._make_card(idx, rule, counts, rule.id in conflicted, issue_texts)
            self._cards_layout.insertWidget(self._cards_layout.count() - 1, card)

    def _make_card(
        self,
        idx: int,
        rule: Rule,
        counts: tuple[int, int],
        conflict: bool,
        conflict_messages: list[str],
    ) -> QFrame:
        card = QFrame()
        card.setObjectName("RuleCard")
        card.setProperty("conflict", conflict)
        lay = QVBoxLayout(card)

        row = QHBoxLayout()
        index = QLabel(f"{idx:02d}")
        index.setProperty("tertiary", True)
        row.addWidget(index)
        formula = QLabel(f"{rule.find} → {_replace_label(rule)}")
        formula.setObjectName("RuleFormula")
        formula.setStyleSheet(f"font-family:{FONT_MONO};")
        row.addWidget(formula, stretch=1)
        row.addWidget(QLabel(_scope_label(rule)))
        if not conflict:
            chip = QLabel("✓ Validado")
            chip.setObjectName("ValidChip")
            row.addWidget(chip)
        actions = QLabel("✎  ⧉  🗑")
        actions.setProperty("tertiary", True)
        row.addWidget(actions)
        lay.addLayout(row)

        occurrence_count, file_count = counts
        meta = QLabel(f"{occurrence_count} ocorrências em {file_count} programas")
        meta.setProperty("tertiary", True)
        lay.addWidget(meta)

        for message in conflict_messages:
            conflict_line = QLabel(f"▲ Conflito: {message}")
            conflict_line.setObjectName("ConflictLine")
            lay.addWidget(conflict_line)
        return card
