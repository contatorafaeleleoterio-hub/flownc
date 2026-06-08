"""CompositorPanel — montagem de edicoes no formato editlist/rascunho (FASE 2).

Layout conforme mockup painel-final.v2.html:
  - Titulo "1 Configuracoes"
  - comp-row: dropdown origem | dropdown destino | botao "+ adicionar outra edicao"
  - editlist: cabecalho "Edicoes montadas (N)" + linhas confirmadas + linha rascunho
  - CTA "Adicionar edicao ao lote ->" (desabilitado quando lista vazia)

So apresenta e emite sinais; nao executa logica de negocio.
"""
from __future__ import annotations

import uuid

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.library_store import CodeEntry
from core.models import Mode, Rule, Scope


class _EditRow(QWidget):
    """Linha confirmada na editlist: 'ORIGEM -> DESTINO  [✕]'."""

    remove_clicked = Signal(int)

    def __init__(self, idx: int, origem: str, destino: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._idx = idx
        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 6, 8, 6)
        lay.setSpacing(8)

        pill_o = QLabel(origem or "—")
        pill_o.setObjectName("ElPill")
        lay.addWidget(pill_o)

        arr = QLabel("→")
        arr.setObjectName("ElArr")
        lay.addWidget(arr)

        pill_d = QLabel(destino or "(remover)")
        pill_d.setObjectName("ElPill")
        lay.addWidget(pill_d)

        lay.addStretch(1)

        btn = QPushButton("✕")
        btn.setObjectName("ElRemove")
        btn.setFixedSize(24, 24)
        btn.setToolTip("Remover esta edição")
        btn.clicked.connect(lambda: self.remove_clicked.emit(self._idx))
        lay.addWidget(btn)

    def update_index(self, new_idx: int) -> None:
        self._idx = new_idx


class _DraftRow(QWidget):
    """Linha rascunho — sempre ao final da editlist; reflete os combos em tempo real."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("DraftRow")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 6, 8, 6)
        lay.setSpacing(8)

        self.lbl_origem = QLabel("—")
        self.lbl_origem.setObjectName("ElPill")
        lay.addWidget(self.lbl_origem)

        arr = QLabel("→")
        arr.setObjectName("ElArr")
        lay.addWidget(arr)

        self.lbl_destino = QLabel("—")
        self.lbl_destino.setObjectName("ElPill")
        lay.addWidget(self.lbl_destino)

        lay.addStretch(1)

        badge = QLabel("em edição")
        badge.setObjectName("DraftBadge")
        lay.addWidget(badge)

    def update_text(self, origem: str, destino: str) -> None:
        self.lbl_origem.setText(origem or "—")
        self.lbl_destino.setText(destino or "—")


class CompositorPanel(QWidget):
    """Compositor de edicoes no formato editlist/rascunho do mockup v2."""

    regra_adicionada = Signal(object)   # emite Rule (compatibilidade com main_window)
    regra_removida = Signal(int)        # emite indice removido
    adicionar_ao_lote = Signal()        # CTA "Adicionar edicao ao lote ->"

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("CompositorPanel")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._regras: list[Rule] = []
        self._rows: list[_EditRow] = []
        self._build_ui()

    # ---------- construcao ----------

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(8)
        root.setContentsMargins(12, 12, 12, 12)

        # Titulo
        title = QLabel("1  Configurações")
        title.setObjectName("ZTitle")
        root.addWidget(title)

        # comp-row: origem | destino | botao adicionar
        comp_row = QHBoxLayout()
        comp_row.setSpacing(8)

        col_origem = QVBoxLayout()
        lbl_o = QLabel("CÓDIGO DE ORIGEM")
        lbl_o.setObjectName("LabelCaps")
        col_origem.addWidget(lbl_o)
        self.cb_origem = self._make_code_combo()
        col_origem.addWidget(self.cb_origem)
        comp_row.addLayout(col_origem, stretch=1)

        col_destino = QVBoxLayout()
        lbl_d = QLabel("TROCAR POR")
        lbl_d.setObjectName("LabelCaps")
        col_destino.addWidget(lbl_d)
        self.cb_destino = self._make_code_combo()
        col_destino.addWidget(self.cb_destino)
        comp_row.addLayout(col_destino, stretch=1)

        col_add = QVBoxLayout()
        col_add.addWidget(QLabel(""))  # espaçador de altura
        self.btn_add = QPushButton("+ adicionar outra edição")
        self.btn_add.setObjectName("CompAddBtn")
        self.btn_add.clicked.connect(self._on_add)
        col_add.addWidget(self.btn_add)
        comp_row.addLayout(col_add)

        root.addLayout(comp_row)

        # editlist (container com header + linhas + rascunho)
        self._editlist_frame = QFrame()
        self._editlist_frame.setObjectName("EditList")
        editlist_lay = QVBoxLayout(self._editlist_frame)
        editlist_lay.setContentsMargins(0, 0, 0, 0)
        editlist_lay.setSpacing(0)

        self._lbl_editlist_title = QLabel("Edições montadas (0)")
        self._lbl_editlist_title.setObjectName("EditListHead")
        editlist_lay.addWidget(self._lbl_editlist_title)

        # scroll para as linhas confirmadas
        self._rows_widget = QWidget()
        self._rows_widget.setObjectName("EditListBody")
        self._rows_layout = QVBoxLayout(self._rows_widget)
        self._rows_layout.setContentsMargins(0, 0, 0, 0)
        self._rows_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self._rows_widget)
        scroll.setMaximumHeight(160)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        editlist_lay.addWidget(scroll)

        # linha rascunho (sempre ao final)
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setObjectName("EditListSep")
        editlist_lay.addWidget(sep)

        self._draft_row = _DraftRow()
        editlist_lay.addWidget(self._draft_row)

        root.addWidget(self._editlist_frame)

        # CTA "Adicionar edicao ao lote ->"
        self.btn_cta = QPushButton("Adicionar edição ao lote →")
        self.btn_cta.setObjectName("AddRuleBtn")
        self.btn_cta.setEnabled(False)
        self.btn_cta.clicked.connect(self.adicionar_ao_lote.emit)
        root.addWidget(self.btn_cta)

        root.addStretch(1)

        # conectar combos para atualizar o rascunho em tempo real
        self.cb_origem.currentTextChanged.connect(self._update_draft)
        self.cb_destino.currentTextChanged.connect(self._update_draft)

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
        origem = self._combo_code(self.cb_origem)
        destino = self._combo_code(self.cb_destino)
        if not origem:
            return
        rule = Rule(
            id=f"r_{uuid.uuid4().hex[:6]}",
            find=origem,
            replace=destino,
            scope=Scope.GLOBAL,
            mode=Mode.AUTO,
        )
        idx = len(self._regras)
        self._regras.append(rule)

        row = _EditRow(idx, origem, destino)
        row.remove_clicked.connect(self._on_remove)
        self._rows.append(row)
        self._rows_layout.addWidget(row)

        self._update_title()
        self.cb_origem.setCurrentText("")
        self.cb_destino.setCurrentText("")
        self._update_cta()
        self.regra_adicionada.emit(rule)

    def _on_remove(self, idx: int) -> None:
        if idx < 0 or idx >= len(self._regras):
            return
        del self._regras[idx]
        row = self._rows.pop(idx)
        row.deleteLater()
        # reindexar linhas restantes
        for i, r in enumerate(self._rows):
            r.update_index(i)
        self._update_title()
        self._update_cta()
        self.regra_removida.emit(idx)

    def _update_title(self) -> None:
        n = len(self._regras)
        self._lbl_editlist_title.setText(f"Edições montadas ({n})")

    def _update_cta(self) -> None:
        self.btn_cta.setEnabled(len(self._regras) > 0)

    def _update_draft(self) -> None:
        self._draft_row.update_text(
            self._combo_code(self.cb_origem),
            self._combo_code(self.cb_destino),
        )

    # ---------- API publica ----------

    def set_library(self, entries: list[CodeEntry]) -> None:
        """Popula os combos: codigo como texto visivel, descricao no tooltip."""
        for cb in (self.cb_origem, self.cb_destino):
            cb.blockSignals(True)
            cb.clear()
            for i, e in enumerate(entries):
                cb.addItem(e.find, e.find)
                if e.label:
                    cb.setItemData(i, e.label, Qt.ItemDataRole.ToolTipRole)
            cb.setCurrentText("")
            cb.blockSignals(False)
        self._update_draft()

    def get_regras(self) -> list[Rule]:
        return list(self._regras)
