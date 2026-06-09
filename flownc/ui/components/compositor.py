"""CompositorPanel — montagem de edicoes no formato editlist/rascunho (FASE 2).

Layout conforme mockup painel-final.v2.html:
  - Titulo "1 Configuracoes" (badge numerado + texto)
  - comp-row: dropdown origem | dropdown destino | botao "+ adicionar outra edicao"
  - editlist: cabecalho "Edicoes montadas (N)" + linhas empilhadas + linha "em edicao"

Fluxo fiel ao mockup:
  - "+ adicionar outra edicao" SO empilha a edicao atual na lista (nao publica).
  - O envio ao Resumo e feito pelo botao "Adicionar edicao ao lote ->" que mora no
    rodape da SECAO 2 (ProgramListPanel); o MainWindow chama commit_to_batch() aqui.

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
from ui.components.code_combo import CodeCombo


class _EditRow(QWidget):
    """Linha empilhada (pendente) na editlist: 'ORIGEM -> DESTINO  [✕]'."""

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
        btn.setFixedSize(22, 22)
        btn.setToolTip("Remover esta edição")
        btn.clicked.connect(lambda: self.remove_clicked.emit(self._idx))
        lay.addWidget(btn)

    def update_index(self, new_idx: int) -> None:
        self._idx = new_idx


class _DraftRow(QWidget):
    """Linha 'em edicao' — sempre ao final; reflete os combos em tempo real."""

    clear_clicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("DraftRow")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
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

        btn = QPushButton("✕")
        btn.setObjectName("ElRemove")
        btn.setFixedSize(22, 22)
        btn.setToolTip("Limpar esta edição")
        btn.clicked.connect(self.clear_clicked.emit)
        lay.addWidget(btn)

    def update_text(self, origem: str, destino: str) -> None:
        self.lbl_origem.setText(origem or "—")
        self.lbl_destino.setText(destino or "—")


class CompositorPanel(QWidget):
    """Compositor de edicoes no formato editlist/rascunho do mockup v2."""

    regra_adicionada = Signal(object)   # emite Rule (compatibilidade com main_window)
    regra_removida = Signal(int)        # emite indice de regra publicada removida
    estado_alterado = Signal()          # ha (ou nao) edicoes prontas para enviar ao lote

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("CompositorPanel")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._regras: list[Rule] = []          # publicadas (no Resumo)
        self._pending: list[tuple[str, str]] = []  # empilhadas, ainda nao publicadas
        self._rows: list[_EditRow] = []
        self._build_ui()

    # ---------- construcao ----------

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(8)
        root.setContentsMargins(12, 12, 12, 12)

        # Titulo: badge numerado + texto
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        znum = QLabel("1")
        znum.setObjectName("ZNum")
        title_row.addWidget(znum)
        title = QLabel("Configurações")
        title.setObjectName("ZTitle")
        title_row.addWidget(title)
        title_row.addStretch(1)
        root.addLayout(title_row)

        # comp-row: origem | destino | botao adicionar
        comp_row = QHBoxLayout()
        comp_row.setSpacing(8)

        col_origem = QVBoxLayout()
        col_origem.setSpacing(4)
        lbl_o = QLabel("CÓDIGO DE ORIGEM")
        lbl_o.setObjectName("LabelCaps")
        col_origem.addWidget(lbl_o)
        self.cb_origem = self._make_code_combo()
        col_origem.addWidget(self.cb_origem)
        comp_row.addLayout(col_origem, stretch=1)

        col_destino = QVBoxLayout()
        col_destino.setSpacing(4)
        lbl_d = QLabel("TROCAR POR")
        lbl_d.setObjectName("LabelCaps")
        col_destino.addWidget(lbl_d)
        self.cb_destino = self._make_code_combo()
        col_destino.addWidget(self.cb_destino)
        comp_row.addLayout(col_destino, stretch=1)

        col_add = QVBoxLayout()
        col_add.setSpacing(4)
        spacer = QLabel(" ")
        spacer.setObjectName("LabelCaps")
        col_add.addWidget(spacer)  # alinha o botao com os combos
        self.btn_add = QPushButton("+ adicionar outra edição")
        self.btn_add.setObjectName("CompAddBtn")
        self.btn_add.setToolTip("Empilha a edição atual na lista e abre uma nova")
        self.btn_add.clicked.connect(self._on_add)
        col_add.addWidget(self.btn_add)
        comp_row.addLayout(col_add)

        root.addLayout(comp_row)

        # editlist (container com header + linhas + rascunho)
        self._editlist_frame = QFrame()
        self._editlist_frame.setObjectName("EditList")
        self._editlist_frame.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        editlist_lay = QVBoxLayout(self._editlist_frame)
        editlist_lay.setContentsMargins(0, 0, 0, 0)
        editlist_lay.setSpacing(0)

        self._lbl_editlist_title = QLabel("Edições montadas (1)")
        self._lbl_editlist_title.setObjectName("EditListHead")
        editlist_lay.addWidget(self._lbl_editlist_title)

        # scroll para as linhas empilhadas
        self._rows_widget = QWidget()
        self._rows_widget.setObjectName("EditListBody")
        self._rows_widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._rows_layout = QVBoxLayout(self._rows_widget)
        self._rows_layout.setContentsMargins(0, 0, 0, 0)
        self._rows_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self._rows_widget)
        scroll.setMaximumHeight(132)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        editlist_lay.addWidget(scroll)

        # separador antes da linha "em edicao"
        sep = QFrame()
        sep.setObjectName("EditListSep")
        sep.setFixedHeight(1)
        editlist_lay.addWidget(sep)

        self._draft_row = _DraftRow()
        self._draft_row.clear_clicked.connect(self._clear_draft)
        editlist_lay.addWidget(self._draft_row)

        root.addWidget(self._editlist_frame)
        root.addStretch(1)

        # conectar combos para atualizar o rascunho em tempo real
        self.cb_origem.currentTextChanged.connect(self._on_draft_changed)
        self.cb_destino.currentTextChanged.connect(self._on_draft_changed)

    def _make_code_combo(self) -> QComboBox:
        return CodeCombo()

    @staticmethod
    def _combo_code(cb: QComboBox) -> str:
        idx = cb.currentIndex()
        if idx >= 0 and cb.itemText(idx) == cb.currentText():
            return str(cb.itemData(idx))
        return cb.currentText().strip()

    # ---------- acoes ----------

    def _on_add(self) -> None:
        """Empilha a edicao atual na lista (sem publicar no Resumo)."""
        origem = self._combo_code(self.cb_origem)
        destino = self._combo_code(self.cb_destino)
        if not origem:
            return
        idx = len(self._pending)
        self._pending.append((origem, destino))

        row = _EditRow(idx, origem, destino)
        row.remove_clicked.connect(self._on_remove)
        self._rows.append(row)
        self._rows_layout.addWidget(row)

        self.cb_origem.setCurrentText("")
        self.cb_destino.setCurrentText("")
        self._update_title()
        self._update_draft()
        self.estado_alterado.emit()

    def _on_remove(self, idx: int) -> None:
        if idx < 0 or idx >= len(self._pending):
            return
        del self._pending[idx]
        row = self._rows.pop(idx)
        row.deleteLater()
        for i, r in enumerate(self._rows):
            r.update_index(i)
        self._update_title()
        self.estado_alterado.emit()

    def _clear_draft(self) -> None:
        self.cb_origem.setCurrentText("")
        self.cb_destino.setCurrentText("")
        self._update_draft()
        self.estado_alterado.emit()

    def _on_draft_changed(self) -> None:
        self._update_draft()
        self.estado_alterado.emit()

    def _update_title(self) -> None:
        # a linha "em edicao" conta como 1 (igual ao mockup)
        n = len(self._pending) + 1
        self._lbl_editlist_title.setText(f"Edições montadas ({n})")

    def _update_draft(self) -> None:
        self._draft_row.update_text(
            self._combo_code(self.cb_origem),
            self._combo_code(self.cb_destino),
        )

    # ---------- API publica ----------

    def commit_to_batch(self) -> None:
        """Publica as edicoes empilhadas + a 'em edicao' no Resumo e limpa a lista."""
        to_add = list(self._pending)
        draft_origem = self._combo_code(self.cb_origem)
        draft_destino = self._combo_code(self.cb_destino)
        if draft_origem:
            to_add.append((draft_origem, draft_destino))
        if not to_add:
            return
        for origem, destino in to_add:
            rule = Rule(
                id=f"r_{uuid.uuid4().hex[:6]}",
                find=origem,
                replace=destino,
                scope=Scope.GLOBAL,
                mode=Mode.AUTO,
            )
            self._regras.append(rule)
            self.regra_adicionada.emit(rule)
        # limpa a lista de montagem
        self._pending.clear()
        for row in self._rows:
            row.deleteLater()
        self._rows.clear()
        self.cb_origem.setCurrentText("")
        self.cb_destino.setCurrentText("")
        self._update_title()
        self._update_draft()
        self.estado_alterado.emit()

    def remove_committed(self, idx: int) -> None:
        """Remove uma regra ja publicada (acionado pelo 🗑 do Resumo)."""
        if idx < 0 or idx >= len(self._regras):
            return
        del self._regras[idx]
        self.regra_removida.emit(idx)

    def tem_para_commitar(self) -> bool:
        return bool(self._pending) or bool(self._combo_code(self.cb_origem))

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
