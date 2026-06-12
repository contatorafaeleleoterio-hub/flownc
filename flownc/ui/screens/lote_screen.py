"""Tela Lote (mockup v4): Programas (esquerda) + Compositor/Lote de edições (direita).

Bloco 4: o painel direito ganhou o `CompositorV4` (abas Trocar código / ➕ Inserir
bloco), a lista de edições como cartões numerados (✎ ⧉ ✕, conflito âmbar), o chip
de estado do lote e o CTA "Conferir lote →" com a regra de habilitação. O modal de
Conferência liga no CTA pelo sinal `conferir_solicitado` (Bloco 5).
"""
from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ui import theme
from ui.components.compositor_v4 import CompositorV4, Edicao
from ui.components.program_list_v4 import ProgramListV4


def _repolish(w: QWidget) -> None:
    style = w.style()
    style.unpolish(w)
    style.polish(w)


class _CtaButton(QFrame):
    """CTA de duas linhas (título + subtítulo) clicável — layout garantido.

    Usa QFrame em vez de QPushButton porque empilhar dois QLabel dentro de um
    QPushButton estilizado faz o texto se sobrepor em alguns temas do Qt.
    """

    clicado = Signal()

    def __init__(self, titulo: str, subtitulo: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("CtaConf")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(64)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(4)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.big = QLabel(titulo)
        self.big.setObjectName("CtaBig")
        self.big.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.small = QLabel(subtitulo)
        self.small.setObjectName("CtaSmall")
        self.small.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.big)
        lay.addWidget(self.small)

    def setEnabled(self, on: bool) -> None:  # noqa: N802 (Qt-style API)
        super().setEnabled(on)
        self.setProperty("off", not on)
        for lbl in (self.big, self.small):
            lbl.setProperty("off", not on)
            _repolish(lbl)
        _repolish(self)

    def mousePressEvent(self, event) -> None:  # noqa: N802, ANN001
        if self.isEnabled() and event.button() == Qt.MouseButton.LeftButton:
            self.clicado.emit()
        super().mousePressEvent(event)


class _EdicaoCard(QFrame):
    """Cartão numerado de uma edição do lote (✎ editar, ⧉ duplicar, ✕ excluir)."""

    editar = Signal()
    duplicar = Signal()
    excluir = Signal()

    def __init__(
        self, indice: int, ed: Edicao, conflito: bool, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setObjectName("RCard")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setProperty("warn", conflito)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(8)

        linha = QHBoxLayout()
        linha.setSpacing(12)
        idx = QLabel(f"{indice + 1:02d}")
        idx.setObjectName("RIdx")
        linha.addWidget(idx)

        formula = QLabel(self._formula(ed))
        formula.setObjectName("RFormula")
        formula.setTextFormat(Qt.TextFormat.RichText)
        linha.addWidget(formula, stretch=1)

        for simbolo, dica, sinal, eh_del in (
            ("✎", "Editar (volta ao compositor)", self.editar, False),
            ("⧉", "Duplicar", self.duplicar, False),
            ("✕", "Remover do lote", self.excluir, True),
        ):
            btn = QPushButton(simbolo)
            btn.setObjectName("RcActDel" if eh_del else "RcAct")
            btn.setFixedSize(32, 32)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setToolTip(dica)
            btn.clicked.connect(sinal.emit)
            linha.addWidget(btn)
        lay.addLayout(linha)

        if conflito:
            aviso = QLabel(
                f"▲ Conflito: <b>{ed.origem}</b> é alterado por mais de uma edição.")
            aviso.setObjectName("RcConflict")
            aviso.setTextFormat(Qt.TextFormat.RichText)
            lay.addWidget(aviso)

    @staticmethod
    def _formula(ed: Edicao) -> str:
        if ed.tipo == "ins":
            n = len(ed.texto.split("\n")) if ed.texto else 0
            plural = "s" if n > 1 else ""
            ancora = (
                f"após {ed.codigo}" if ed.modo == "code" else f"após a linha {ed.linha}")
            cor = theme.COLOR_TEXT_TERTIARY
            return (
                f"➕ bloco · {n} linha{plural} "
                f"<span style='color:{cor};'>{ancora}</span>"
            )
        if ed.remover:
            return (
                f"{ed.origem} → "
                f"<span style='color:{theme.COLOR_DANGER};'>remover</span>"
            )
        return f"{ed.origem} → {ed.destino}"

    def flash(self) -> None:
        """Pisca brevemente (cartão recém-adicionado)."""
        self.setProperty("flash", True)
        _repolish(self)

        def apagar() -> None:
            self.setProperty("flash", False)
            _repolish(self)

        QTimer.singleShot(900, apagar)


class LoteScreen(QWidget):
    """Tela-lugar 'Lote' (índice 0 do QStackedWidget)."""

    abrir_arquivo = Signal(str)
    conferir_solicitado = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("LoteScreen")
        self._edicoes: list[Edicao] = []
        self._cards: list[_EdicaoCard] = []

        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(16)

        # Coluna esquerda — Programas
        self.program_list = ProgramListV4()
        self.program_list.abrir_arquivo.connect(self.abrir_arquivo.emit)
        self.program_list.selecao_alterada.connect(self._on_selecao_alterada)
        self.program_list.programas_alterados.connect(self._on_selecao_alterada)
        lay.addWidget(self.program_list, stretch=11)

        # Coluna direita — Lote de edições
        lay.addWidget(self._build_right(), stretch=9)
        self._render_lote()

    # ============ construção (painel direito) ============
    def _build_right(self) -> QWidget:
        painel = QFrame()
        painel.setObjectName("LotePanelRight")
        painel.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        rlay = QVBoxLayout(painel)
        rlay.setContentsMargins(16, 16, 16, 16)
        rlay.setSpacing(12)

        # Cabeçalho: título + chip de estado
        phead = QHBoxLayout()
        phead.setSpacing(12)
        titulo = QLabel("Lote de edições")
        titulo.setObjectName("PTitle")
        phead.addWidget(titulo)
        self._chip = QLabel("vazio")
        self._chip.setObjectName("LoteChip")
        self._chip.setProperty("estado", "mut")
        phead.addWidget(self._chip)
        phead.addStretch(1)
        rlay.addLayout(phead)

        # Compositor com abas
        self.compositor = CompositorV4()
        self.compositor.adicionar.connect(self._on_adicionar)
        rlay.addWidget(self.compositor)

        # Lista de edições (cartões) + estado vazio
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        host = QWidget()
        self._lista_lay = QVBoxLayout(host)
        self._lista_lay.setContentsMargins(0, 0, 0, 0)
        self._lista_lay.setSpacing(8)
        self._lista_lay.addStretch(1)
        self._scroll.setWidget(host)
        rlay.addWidget(self._scroll, stretch=1)

        self._empty = self._build_empty()
        rlay.addWidget(self._empty, stretch=1)

        # Rodapé: facts + CTA
        self._facts = QLabel()
        self._facts.setObjectName("LoteFacts")
        rlay.addWidget(self._facts)

        self._cta = _CtaButton(
            "CONFERIR LOTE →",
            "varre os programas e mostra os números reais — nada é gravado")
        self._cta.clicado.connect(self.conferir_solicitado.emit)
        rlay.addWidget(self._cta)
        return painel

    def _build_empty(self) -> QWidget:
        box = QFrame()
        box.setObjectName("EmptyState")
        lay = QVBoxLayout(box)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.setSpacing(12)
        ic = QLabel("📋")
        ic.setObjectName("EmptyIcon")
        ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t1 = QLabel("Lote vazio")
        t1.setObjectName("EmptyT1")
        t1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t2 = QLabel(
            "Monte uma edição acima — troca de código ou bloco a inserir — e clique em "
            "“+ Adicionar ao lote”. Ou carregue uma configuração salva no topo.")
        t2.setObjectName("EmptyT2")
        t2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t2.setWordWrap(True)
        lay.addWidget(ic)
        lay.addWidget(t1)
        lay.addWidget(t2)
        return box

    # ============ API pública (Blocos 5/6 usam) ============
    def get_edicoes(self) -> list[Edicao]:
        return list(self._edicoes)

    def limpar_edicoes(self) -> None:
        self._edicoes = []
        self._render_lote()

    def set_edicoes(self, edicoes: list[Edicao]) -> None:
        """Substitui o lote de edições (ex.: ao carregar uma receita salva)."""
        self._edicoes = list(edicoes)
        self._render_lote()

    def tem_edicoes(self) -> bool:
        return bool(self._edicoes)

    # ============ lote de edições ============
    def _conflitos_por_origem(self) -> dict[str, int]:
        contagem: dict[str, int] = {}
        for ed in self._edicoes:
            if ed.tipo == "swap":
                contagem[ed.origem] = contagem.get(ed.origem, 0) + 1
        return contagem

    def _on_adicionar(self, ed: Edicao) -> None:
        self._edicoes.append(ed)
        self._render_lote(flash=True)

    def _on_excluir(self, i: int) -> None:
        del self._edicoes[i]
        self._render_lote()

    def _on_duplicar(self, i: int) -> None:
        self._edicoes.insert(i + 1, self._edicoes[i].duplicada())
        self._render_lote()

    def _on_editar(self, i: int) -> None:
        ed = self._edicoes.pop(i)
        self._render_lote()
        self.compositor.carregar_edicao(ed)

    def _render_lote(self, flash: bool = False) -> None:
        for card in self._cards:
            card.setParent(None)
            card.deleteLater()
        self._cards = []

        origem = self._conflitos_por_origem()
        for i, ed in enumerate(self._edicoes):
            conflito = ed.tipo == "swap" and origem.get(ed.origem, 0) > 1
            card = _EdicaoCard(i, ed, conflito)
            card.editar.connect(lambda i=i: self._on_editar(i))
            card.duplicar.connect(lambda i=i: self._on_duplicar(i))
            card.excluir.connect(lambda i=i: self._on_excluir(i))
            self._lista_lay.insertWidget(self._lista_lay.count() - 1, card)
            self._cards.append(card)

        tem = bool(self._edicoes)
        self._scroll.setVisible(tem)
        self._empty.setVisible(not tem)
        if flash and self._cards:
            ultimo = self._cards[-1]
            ultimo.flash()
            QTimer.singleShot(0, lambda: self._scroll.ensureWidgetVisible(ultimo))

        self._update_chip()
        self._refresh_cta()

    def _update_chip(self) -> None:
        if not self._edicoes:
            texto, estado = "vazio", "mut"
        else:
            origem = self._conflitos_por_origem()
            n_conf = sum(1 for n in origem.values() if n > 1)
            if n_conf:
                plural = "s" if n_conf > 1 else ""
                texto, estado = f"⚠ {n_conf} conflito{plural}", "warn"
            else:
                n = len(self._edicoes)
                texto = f"{n} edição" if n == 1 else f"{n} edições"
                estado = "ok"
        self._chip.setText(texto)
        self._chip.setProperty("estado", estado)
        _repolish(self._chip)

    # ============ CTA ============
    def _on_selecao_alterada(self) -> None:
        self.compositor.set_marcados(self.program_list.get_marcados())
        self._refresh_cta()

    def _refresh_cta(self) -> None:
        n = len(self._edicoes)
        p = len(self.program_list.get_marcados())
        ed_txt = "1 edição" if n == 1 else f"{n} edições"
        pr_txt = "1 programa marcado" if p == 1 else f"{p} programas marcados"
        self._facts.setText(f"{ed_txt} · {pr_txt}")

        habilita = n > 0 and p > 0
        self._cta.setEnabled(habilita)
        if n == 0:
            self._cta.setToolTip("Adicione ao menos 1 edição ao lote")
        elif p == 0:
            self._cta.setToolTip("Marque ao menos 1 programa")
        else:
            self._cta.setToolTip("Varre os programas marcados e mostra a conferência")
