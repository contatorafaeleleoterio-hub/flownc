"""CompositorPanel — montagem de edicoes (redesign-layout-principal, grupo 3).

Dropdowns De/Para/escopo + lista empilhada de "edicoes montadas" (mockup v2).
Cada edicao montada vira uma Rule. O painel mantem a lista de regras montadas e
emite sinais ao maestro; nao executa nenhuma logica de negocio.
"""
from __future__ import annotations

import uuid

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.library_store import CodeEntry
from core.models import Mode, Rule, Scope

_ESCOPO_TODOS = "Todos os programas"
_ESCOPO_ESTE = "Só este programa"


def _escopo_label(rule: Rule) -> str:
    return "todos" if rule.scope is Scope.GLOBAL else "só este"


class CompositorPanel(QWidget):
    """Compositor de edicoes: De → Para [escopo] empilhadas em lista."""

    regra_adicionada = Signal(object)  # emite Rule
    regra_removida = Signal(int)       # emite indice removido

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("CompositorPanel")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._regras: list[Rule] = []
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.addWidget(QLabel("Montar edição"))

        row = QHBoxLayout()
        row.addWidget(QLabel("De:"))
        self.cb_de = self._make_code_combo()
        row.addWidget(self.cb_de, stretch=1)
        row.addWidget(QLabel("Para:"))
        self.cb_para = self._make_code_combo()
        row.addWidget(self.cb_para, stretch=1)
        row.addWidget(QLabel("Escopo:"))
        self.cb_escopo = QComboBox()
        self.cb_escopo.addItems([_ESCOPO_TODOS, _ESCOPO_ESTE])
        row.addWidget(self.cb_escopo)
        root.addLayout(row)

        self.btn_add = QPushButton("➕ adicionar outra edição")
        self.btn_add.clicked.connect(self._on_add)
        root.addWidget(self.btn_add)

        root.addWidget(QLabel("Edições montadas"))
        self.lst_edicoes = QListWidget()
        root.addWidget(self.lst_edicoes, stretch=1)

        self.btn_remove = QPushButton("✕ remover selecionada")
        self.btn_remove.clicked.connect(self._on_remove)
        root.addWidget(self.btn_remove)

    def _make_code_combo(self) -> QComboBox:
        cb = QComboBox()
        cb.setEditable(True)
        cb.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        return cb

    @staticmethod
    def _combo_code(cb: QComboBox) -> str:
        idx = cb.currentIndex()
        if idx >= 0 and cb.itemText(idx) == cb.currentText():
            return str(cb.itemData(idx))
        return cb.currentText().strip()

    # ---------- acoes ----------
    def _on_add(self) -> None:
        de = self._combo_code(self.cb_de)
        para = self._combo_code(self.cb_para)
        if not de:
            return
        scope = Scope.GLOBAL if self.cb_escopo.currentText() == _ESCOPO_TODOS else Scope.FILE
        rule = Rule(id=f"r_{uuid.uuid4().hex[:6]}", find=de, replace=para,
                    scope=scope, mode=Mode.AUTO)
        self._regras.append(rule)
        self.lst_edicoes.addItem(f"{de} → {para or '(remover)'} [{_escopo_label(rule)}]")
        self.cb_de.setCurrentText("")
        self.cb_para.setCurrentText("")
        self.regra_adicionada.emit(rule)

    def _on_remove(self) -> None:
        row = self.lst_edicoes.currentRow()
        if row < 0:
            return
        self.lst_edicoes.takeItem(row)
        del self._regras[row]
        self.regra_removida.emit(row)

    # ---------- API publica ----------
    def set_library(self, entries: list[CodeEntry]) -> None:
        for cb in (self.cb_de, self.cb_para):
            cb.clear()
            for e in entries:
                label = f"{e.label}  " if e.label else ""
                cb.addItem(f"{label}{e.find}", e.find)
            cb.setCurrentText("")

    def get_regras(self) -> list[Rule]:
        return list(self._regras)
