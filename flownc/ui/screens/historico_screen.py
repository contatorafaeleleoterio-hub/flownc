"""Tela Histórico (mockup v4): uma linha por publicação, mais recente no topo.

Cada linha mostra quando, o resumo (edições · trocas/bloco · programas), o caminho
do backup e a configuração usada, com o botão "↩ Restaurar originais". O estado
vazio orienta o operador. A restauração real (copiar os originais de volta) é da
Fase 3 — aqui a ação confirma e registra a intenção.
"""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from ui.modals.publicacao_modal import PublicacaoEntrada


def _facts(trocas: int, blocos: int) -> str:
    partes: list[str] = []
    if trocas:
        partes.append(f"{trocas} troca" + ("" if trocas == 1 else "s"))
    if blocos:
        partes.append(f"bloco em {blocos} programa" + ("" if blocos == 1 else "s"))
    return " · ".join(partes) if partes else "nada alterado"


class HistoricoScreen(QWidget):
    """Tela-lugar 'Histórico' (índice 3 do QStackedWidget)."""

    restaurar_solicitado = Signal(object)  # PublicacaoEntrada

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("HistoricoScreen")
        self._entries: list[PublicacaoEntrada] = []
        self._rows: list[QWidget] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        titulo = QLabel("Histórico de publicações")
        titulo.setObjectName("PTitle")
        root.addWidget(titulo)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        host = QWidget()
        self._lay = QVBoxLayout(host)
        self._lay.setContentsMargins(0, 0, 0, 0)
        self._lay.setSpacing(8)
        self._lay.addStretch(1)
        self._scroll.setWidget(host)
        root.addWidget(self._scroll, stretch=1)

        self._empty = self._build_empty()
        root.addWidget(self._empty, stretch=1)
        self._refresh()

    def _build_empty(self) -> QWidget:
        box = QFrame()
        box.setObjectName("EmptyState")
        lay = QVBoxLayout(box)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.setSpacing(12)
        ic = QLabel("🕘")
        ic.setObjectName("EmptyIcon")
        ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t1 = QLabel("Nenhuma publicação ainda")
        t1.setObjectName("EmptyT1")
        t1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t2 = QLabel(
            "Cada “Publicar” aparece aqui, com o backup dos originais e a opção de restaurar.")
        t2.setObjectName("EmptyT2")
        t2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t2.setWordWrap(True)
        lay.addWidget(ic)
        lay.addWidget(t1)
        lay.addWidget(t2)
        return box

    # ============ API pública ============
    def set_historico(self, entries: list[PublicacaoEntrada]) -> None:
        self._entries = list(entries)
        self._rebuild()

    # ============ interno ============
    def _rebuild(self) -> None:
        for row in self._rows:
            row.setParent(None)
            row.deleteLater()
        self._rows = []
        for entrada in self._entries:
            row = self._build_row(entrada)
            self._lay.insertWidget(self._lay.count() - 1, row)
            self._rows.append(row)
        self._refresh()

    def _build_row(self, entrada: PublicacaoEntrada) -> QWidget:
        row = QFrame()
        row.setObjectName("HistRow")
        row.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        lay = QHBoxLayout(row)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(12)

        quando = QLabel(entrada.quando)
        quando.setObjectName("HistWhen")
        lay.addWidget(quando)

        plural = "ões" if entrada.edicoes > 1 else ""
        prog_pl = "s" if entrada.programas != 1 else ""
        facts = QLabel(
            f"{entrada.edicoes} edição{plural} · {_facts(entrada.trocas, entrada.blocos)} "
            f"em {entrada.programas} programa{prog_pl} · backup {entrada.backup}")
        facts.setObjectName("HistFacts")
        facts.setWordWrap(True)
        lay.addWidget(facts, stretch=1)

        cfg = QLabel(entrada.config)
        cfg.setObjectName("HistCfg")
        lay.addWidget(cfg)

        btn = QPushButton("↩ Restaurar originais")
        btn.setObjectName("GhostBtnV4")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        existe = self._backup_existe(entrada.backup)
        btn.setEnabled(existe)
        if not existe:
            btn.setToolTip("Backup não encontrado nesta pasta")
        btn.clicked.connect(lambda _=False, e=entrada: self._on_restaurar(e))
        lay.addWidget(btn)
        return row

    @staticmethod
    def _backup_existe(backup: str) -> bool:
        caminho = backup.rstrip("\\/")
        if not caminho or caminho.startswith("("):
            return False
        try:
            return Path(caminho).is_dir()
        except OSError:
            return False

    def _on_restaurar(self, entrada: PublicacaoEntrada) -> None:
        resp = QMessageBox.question(
            self,
            "Restaurar originais",
            f"Restaurar os originais da publicação de {entrada.quando}?\n\n"
            f"Backup: {entrada.backup}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resp == QMessageBox.StandardButton.Yes:
            self.restaurar_solicitado.emit(entrada)

    def _refresh(self) -> None:
        tem = bool(self._entries)
        self._scroll.setVisible(tem)
        self._empty.setVisible(not tem)
