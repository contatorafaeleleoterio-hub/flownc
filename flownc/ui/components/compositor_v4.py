"""CompositorV4: compositor de edições da tela Lote (mockup v4).

`QTabWidget` com duas abas — "Trocar código" e "+ Inserir bloco" — e um único
botão "+ Adicionar ao lote" abaixo, compartilhado pelas duas. O botão só habilita
com os campos obrigatórios da aba ativa preenchidos; remover é escolha explícita
("✕ Remover (sem código)" no dropdown de destino, estado vermelho).

Inclui o `LibDropdown` (dropdown pesquisável da biblioteca: busca + "★ Frequentes",
só o código visível, descrição no tooltip) e a dataclass `Edicao`, o item que o
compositor emite para o lote da `LoteScreen`.

FASE 2: a biblioteca exibida é a amostra fixa do mockup (`LIB_EXEMPLO`); a Fase 3
liga `set_biblioteca()` aos dados reais de `core/library_store.py`.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLayout,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from core.matcher import find_spans
from ui.icons import icon_pixmap
from core.models import Mode

# Amostra da biblioteca (FASE 2) — espelha LIB/FREQ de mockups/painel-final.v4.html.
LIB_EXEMPLO: list[tuple[str, str]] = [
    ("M3", "Liga eixo-árvore (horário)"), ("M5", "Para eixo-árvore"),
    ("M6", "Troca de ferramenta"), ("M8", "Liga refrigeração"),
    ("M08", "Refrigeração (normalizado)"), ("M9", "Desliga refrigeração"),
    ("M30", "Fim de programa"), ("G54", "Origem de peça 1"),
    ("G55", "Origem de peça 2"), ("G43", "Compensação de altura"),
    ("T1", "Ferramenta 1"), ("T01", "Ferramenta 1 (normalizado)"),
    ("T1.0", "Ferramenta 1 (decimal)"), ("S1200", "Rotação 1200 rpm"),
    ("F150", "Avanço 150 mm/min"),
]
FREQ_EXEMPLO: list[str] = ["M8", "M08", "G54", "G55", "M6", "T1", "T01"]

_TXT_REMOVER = "× Remover (sem código)"


@dataclass(frozen=True)
class Edicao:
    """Uma edição do lote: troca de código (`swap`) ou bloco a inserir (`ins`)."""

    tipo: str  # "swap" | "ins"
    # swap
    origem: str = ""
    destino: str = ""
    remover: bool = False
    # ins
    texto: str = ""
    modo: str = "code"  # "code" | "line"
    codigo: str = ""
    linha: int = 1

    def duplicada(self) -> "Edicao":
        """Cópia completa (⧉) — preserva o tipo e todos os campos."""
        return replace(self)


def _repolish(w: QWidget) -> None:
    style = w.style()
    style.unpolish(w)
    style.polish(w)


def _clear_layout(layout: QLayout) -> None:
    """Remove e descarta todos os widgets de um layout (guard p/ mypy)."""
    while layout.count():
        item = layout.takeAt(0)
        if item is None:
            continue
        w = item.widget()
        if w is not None:
            w.deleteLater()


class LibDropdown(QWidget):
    """Dropdown pesquisável da biblioteca (libdrop do v4).

    Botão com só o código (descrição no tooltip) que abre um popup com campo de
    busca, seção "★ Frequentes" e a lista completa. Com `com_remover=True`, o
    primeiro item é "✕ Remover (sem código)" e selecioná-lo deixa o botão
    vermelho com o texto "✕ remover".
    """

    alterado = Signal()

    def __init__(
        self,
        placeholder: str = "Selecione o código",
        com_remover: bool = False,
        big: bool = True,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._placeholder = placeholder
        self._com_remover = com_remover
        self._lib: list[tuple[str, str]] = list(LIB_EXEMPLO)
        self._freq: list[str] = list(FREQ_EXEMPLO)
        self._value = ""
        self._is_remove = False

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        self._btn = QPushButton()
        self._btn.setObjectName("LibDropBtn")
        self._btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn.setFixedHeight(44 if big else 32)
        blay = QHBoxLayout(self._btn)
        blay.setContentsMargins(12, 0, 12, 0)
        self._code = QLabel()
        self._code.setObjectName("LibDropCode")
        self._caret = QLabel()
        self._caret.setObjectName("LibDropCaret")
        self._caret.setPixmap(icon_pixmap("caret-down", 14, "#4E6278"))
        for lbl in (self._code, self._caret):
            lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        blay.addWidget(self._code)
        blay.addStretch(1)
        blay.addWidget(self._caret)
        self._btn.clicked.connect(self._abrir_popup)
        lay.addWidget(self._btn)

        self._pop: QFrame | None = None
        self._sync_btn()

    # ============ API pública ============
    def value(self) -> str:
        return self._value

    def is_remove(self) -> bool:
        return self._is_remove

    def set_biblioteca(
        self, biblioteca: list[tuple[str, str]], frequentes: list[str] | None = None
    ) -> None:
        self._lib = list(biblioteca)
        if frequentes is not None:
            self._freq = list(frequentes)

    def set_value(self, code: str, desc: str = "", remover: bool = False) -> None:
        self._value = code
        self._is_remove = bool(remover) and code == ""
        if code and not desc:
            desc = self._desc(code)
        self._btn.setToolTip(
            "Remove o código nos programas marcados" if self._is_remove else desc
        )
        self._sync_btn()
        self.alterado.emit()

    def clear(self) -> None:
        self.set_value("", "", remover=False)

    # ============ interno ============
    def _desc(self, code: str) -> str:
        return next((d for c, d in self._lib if c == code), "")

    def _sync_btn(self) -> None:
        empty = self._value == "" and not self._is_remove
        self._btn.setProperty("empty", empty)
        self._btn.setProperty("remove", self._is_remove)
        if self._is_remove:
            self._code.setText("× remover")
        else:
            self._code.setText(self._value or self._placeholder)
        for w in (self._btn, self._code):
            w.setProperty("empty", empty)
            w.setProperty("remove", self._is_remove)
            _repolish(w)

    def _abrir_popup(self) -> None:
        pop = QFrame(self, Qt.WindowType.Popup)
        pop.setObjectName("LibPop")
        pop.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        play = QVBoxLayout(pop)
        play.setContentsMargins(8, 8, 8, 8)
        play.setSpacing(8)

        busca = QLineEdit()
        busca.setObjectName("LibSearch")
        busca.setPlaceholderText("Procurar código…")
        busca.setClearButtonEnabled(True)
        play.addWidget(busca)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        host = QWidget()
        self._list_lay = QVBoxLayout(host)
        self._list_lay.setContentsMargins(0, 0, 0, 0)
        self._list_lay.setSpacing(2)
        scroll.setWidget(host)
        play.addWidget(scroll)

        busca.textChanged.connect(self._render_lista)
        self._pop = pop
        self._render_lista("")

        pop.setFixedWidth(max(240, self._btn.width()))
        pop.setMaximumHeight(280)
        abaixo = self._btn.mapToGlobal(self._btn.rect().bottomLeft())
        pop.move(abaixo.x(), abaixo.y() + 4)
        pop.show()
        busca.setFocus()

    def _render_lista(self, q: str) -> None:
        _clear_layout(self._list_lay)
        q = (q or "").strip().lower()

        def add_item(code: str, desc: str, remover: bool = False) -> None:
            it = QPushButton(_TXT_REMOVER if remover else code)
            it.setObjectName("LibItem")
            it.setProperty("remove", remover)
            it.setToolTip("Destino vazio = remover o código" if remover else desc)
            it.setCursor(Qt.CursorShape.PointingHandCursor)
            it.clicked.connect(lambda _=False, c=code, d=desc, r=remover: self._pick(c, d, r))
            self._list_lay.addWidget(it)

        def add_hint(texto: str) -> None:
            h = QLabel(texto)
            h.setObjectName("LibHint")
            self._list_lay.addWidget(h)

        if self._com_remover and not q:
            add_item("", "", remover=True)
        if not q:
            freq = [(c, d) for c, d in self._lib if c in self._freq]
            if freq:
                add_hint("★ Frequentes")
                for c, d in freq:
                    add_item(c, d)
            add_hint(f"Todos · {len(self._lib)}")
            for c, d in self._lib:
                add_item(c, d)
        else:
            achados = [
                (c, d) for c, d in self._lib
                if q in c.lower() or q in d.lower()
            ]
            if achados:
                for c, d in achados:
                    add_item(c, d)
            else:
                vazio = QLabel("Nenhum código")
                vazio.setObjectName("LibHint")
                self._list_lay.addWidget(vazio)
        self._list_lay.addStretch(1)

    def _pick(self, code: str, desc: str, remover: bool) -> None:
        if self._pop is not None:
            self._pop.close()
            self._pop = None
        self.set_value(code, desc, remover=remover)


class CompositorV4(QWidget):
    """Compositor com abas: monta uma `Edicao` e emite `adicionar` para o lote."""

    adicionar = Signal(object)  # Edicao

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("CompositorV4")
        self._marcados: list[Path] = []
        self._modelos: list[tuple[str, str, str]] = []  # (nome, descrição, texto)
        self._build()
        self._refresh_add()

    # ============ construção ============
    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        self.tabs = QTabWidget()
        self.tabs.setObjectName("CompTabs")
        self.tabs.addTab(self._build_swap(), "Trocar código")
        self.tabs.addTab(self._build_ins(), "+ Inserir bloco")
        self.tabs.currentChanged.connect(self._on_tab_changed)
        root.addWidget(self.tabs)

        rodape = QHBoxLayout()
        rodape.addStretch(1)
        self.btn_add = QPushButton("+ Adicionar ao lote")
        self.btn_add.setObjectName("CompAddBtn")
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.clicked.connect(self._emit_add)
        rodape.addWidget(self.btn_add)
        root.addLayout(rodape)

    @staticmethod
    def _label_caps(texto: str) -> QLabel:
        lbl = QLabel(texto)
        lbl.setObjectName("LabelCaps")
        return lbl

    def _build_swap(self) -> QWidget:
        page = QWidget()
        lay = QHBoxLayout(page)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)

        campo_src = QVBoxLayout()
        campo_src.setSpacing(8)
        campo_src.addWidget(self._label_caps("CÓDIGO DE ORIGEM"))
        self.drop_origem = LibDropdown(placeholder="Selecione o código")
        self.drop_origem.alterado.connect(self._refresh_add)
        campo_src.addWidget(self.drop_origem)
        lay.addLayout(campo_src, stretch=1)

        campo_dst = QVBoxLayout()
        campo_dst.setSpacing(8)
        campo_dst.addWidget(self._label_caps("TROCAR POR"))
        self.drop_destino = LibDropdown(
            placeholder="Selecione o destino", com_remover=True)
        self.drop_destino.alterado.connect(self._refresh_add)
        campo_dst.addWidget(self.drop_destino)
        lay.addLayout(campo_dst, stretch=1)
        return page

    def _build_ins(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)

        linha = QHBoxLayout()
        linha.setSpacing(12)

        campo_txt = QVBoxLayout()
        campo_txt.setSpacing(8)
        campo_txt.addWidget(self._label_caps("BLOCO A INSERIR (UMA INSTRUÇÃO POR LINHA)"))
        self.ins_texto = QPlainTextEdit()
        self.ins_texto.setObjectName("InsText")
        self.ins_texto.setPlaceholderText("ex.:\nG68 R90.\nG54")
        self.ins_texto.setFixedHeight(96)
        self.ins_texto.textChanged.connect(self._on_ins_mudou)
        campo_txt.addWidget(self.ins_texto)
        linha.addLayout(campo_txt, stretch=2)

        campo_pos = QVBoxLayout()
        campo_pos.setSpacing(8)
        campo_pos.addWidget(self._label_caps("POSIÇÃO EM CADA PROGRAMA"))
        self._grupo_pos = QButtonGroup(self)

        l1 = QHBoxLayout()
        l1.setSpacing(8)
        self.rad_code = QRadioButton("Abaixo da 1ª ocorrência de")
        self.rad_code.setChecked(True)
        self._grupo_pos.addButton(self.rad_code)
        l1.addWidget(self.rad_code)
        self.drop_ancora = LibDropdown(big=False)
        self.drop_ancora.set_value("G54")
        self.drop_ancora.alterado.connect(self._on_ins_mudou)
        l1.addWidget(self.drop_ancora)
        l1.addStretch(1)
        campo_pos.addLayout(l1)

        l2 = QHBoxLayout()
        l2.setSpacing(8)
        self.rad_line = QRadioButton("Abaixo da linha Nº")
        self._grupo_pos.addButton(self.rad_line)
        l2.addWidget(self.rad_line)
        self.ins_linha = QSpinBox()
        self.ins_linha.setObjectName("InsLineNum")
        self.ins_linha.setRange(1, 999999)
        self.ins_linha.valueChanged.connect(self._on_ins_mudou)
        l2.addWidget(self.ins_linha)
        l2.addStretch(1)
        campo_pos.addLayout(l2)

        self.aviso_linha = QLabel(
            "O número da linha pode variar entre programas — prefira a opção por código.")
        self.aviso_linha.setObjectName("InsWarnLine")
        self.aviso_linha.setWordWrap(True)
        self.aviso_linha.setVisible(False)
        campo_pos.addWidget(self.aviso_linha)
        campo_pos.addStretch(1)
        linha.addLayout(campo_pos, stretch=1)
        lay.addLayout(linha)

        self.rad_code.toggled.connect(self._on_pos_mudou)
        self.rad_line.toggled.connect(self._on_pos_mudou)

        self._chips_host = QWidget()
        self._chips_lay = QHBoxLayout(self._chips_host)
        self._chips_lay.setContentsMargins(0, 0, 0, 0)
        self._chips_lay.setSpacing(8)
        lay.addWidget(self._chips_host)
        self._render_chips()

        previa_box = QFrame()
        previa_box.setObjectName("PreviewBox")
        pv_lay = QVBoxLayout(previa_box)
        pv_lay.setContentsMargins(0, 0, 0, 0)
        pv_lay.setSpacing(0)
        self.previa_head = QLabel("Prévia")
        self.previa_head.setObjectName("PvHead")
        pv_lay.addWidget(self.previa_head)
        self.previa = QLabel("—")
        self.previa.setObjectName("InsPreview")
        self.previa.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.previa.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        pv_lay.addWidget(self.previa)
        lay.addWidget(previa_box)
        return page

    # ============ API pública ============
    def set_biblioteca(
        self, biblioteca: list[tuple[str, str]], frequentes: list[str] | None = None
    ) -> None:
        """Atualiza os três dropdowns com a biblioteca real (código, descrição)."""
        for drop in (self.drop_origem, self.drop_destino, self.drop_ancora):
            drop.set_biblioteca(biblioteca, frequentes)

    def set_marcados(self, paths: list[Path]) -> None:
        """Programas marcados (a prévia usa o primeiro que recebe o bloco)."""
        self._marcados = list(paths)
        self._atualizar_previa()

    def set_modelos(self, modelos: list[tuple[str, str, str]]) -> None:
        """Modelos de bloco da biblioteca: lista de (nome, descrição, texto)."""
        self._modelos = list(modelos)
        self._render_chips()

    def carregar_edicao(self, ed: Edicao) -> None:
        """✎ de um cartão: recarrega a edição na aba certa; botão vira 'Atualizar'."""
        if ed.tipo == "ins":
            self.tabs.setCurrentIndex(1)
            self.ins_texto.setPlainText(ed.texto)
            if ed.modo == "line":
                self.rad_line.setChecked(True)
                self.ins_linha.setValue(max(1, ed.linha))
            else:
                self.rad_code.setChecked(True)
                if ed.codigo:
                    self.drop_ancora.set_value(ed.codigo)
        else:
            self.tabs.setCurrentIndex(0)
            self.drop_origem.set_value(ed.origem)
            self.drop_destino.set_value(ed.destino, remover=ed.remover)
        self.btn_add.setText("Atualizar")
        self._refresh_add()

    # ============ interno ============
    def _on_tab_changed(self, _idx: int) -> None:
        self._refresh_add()
        self._atualizar_previa()

    def _on_pos_mudou(self, _checked: bool) -> None:
        self.aviso_linha.setVisible(self.rad_line.isChecked())
        self._on_ins_mudou()

    def _on_ins_mudou(self) -> None:
        self._refresh_add()
        self._atualizar_previa()

    def _swap_ok(self) -> bool:
        return bool(self.drop_origem.value()) and (
            bool(self.drop_destino.value()) or self.drop_destino.is_remove())

    def _ins_ok(self) -> bool:
        if not self.ins_texto.toPlainText().strip():
            return False
        return self.rad_line.isChecked() or bool(self.drop_ancora.value())

    def _refresh_add(self) -> None:
        if self.tabs.currentIndex() == 0:
            ok = self._swap_ok()
            if ok:
                dica = "Adicionar esta edição ao lote"
            elif not self.drop_origem.value():
                dica = "Escolha o código de origem"
            else:
                dica = "Escolha o destino — ou × Remover para apagar o código"
        else:
            ok = self._ins_ok()
            if ok:
                dica = "Adicionar esta edição ao lote"
            elif not self.ins_texto.toPlainText().strip():
                dica = "Digite o bloco a inserir"
            else:
                dica = "Escolha o código de referência"
        self.btn_add.setEnabled(ok)
        self.btn_add.setToolTip(dica)

    def _montar_edicao(self) -> Edicao | None:
        if self.tabs.currentIndex() == 0:
            if not self._swap_ok():
                return None
            return Edicao(
                tipo="swap",
                origem=self.drop_origem.value(),
                destino=self.drop_destino.value(),
                remover=self.drop_destino.is_remove(),
            )
        if not self._ins_ok():
            return None
        return Edicao(
            tipo="ins",
            texto=self.ins_texto.toPlainText().rstrip(),
            modo="line" if self.rad_line.isChecked() else "code",
            codigo=self.drop_ancora.value(),
            linha=self.ins_linha.value(),
        )

    def _emit_add(self) -> None:
        ed = self._montar_edicao()
        if ed is None:
            return
        if ed.tipo == "swap":
            self.drop_origem.clear()
            self.drop_destino.clear()
        else:
            self.ins_texto.clear()
            self._atualizar_previa()
        self.btn_add.setText("+ Adicionar ao lote")
        self._refresh_add()
        self.adicionar.emit(ed)

    # ============ chips de modelos ============
    def _render_chips(self) -> None:
        _clear_layout(self._chips_lay)
        if not self._modelos:
            vazio = QLabel("Nenhum modelo salvo — crie um em “+ Adicionar código” (tela Códigos).")
            vazio.setObjectName("InsChipEmpty")
            self._chips_lay.addWidget(vazio)
        else:
            for nome, desc, texto in self._modelos:
                chip = QPushButton(nome)
                chip.setObjectName("InsChip")
                chip.setToolTip(desc)
                chip.setCursor(Qt.CursorShape.PointingHandCursor)
                chip.clicked.connect(
                    lambda _=False, t=texto: self.ins_texto.setPlainText(t))
                self._chips_lay.addWidget(chip)
        self._chips_lay.addStretch(1)

    # ============ prévia real ============
    def _ponto_insercao(self, texto: str, ed: Edicao) -> int:
        """Índice da linha onde o bloco entraria; -1 se a âncora não aparece."""
        linhas = texto.split("\n")
        if ed.modo == "code":
            for i, ln in enumerate(linhas):
                if find_spans(ln, ed.codigo, Mode.AUTO):
                    return i + 1
            return -1
        return min(max(1, ed.linha), len(linhas))

    def _atualizar_previa(self) -> None:
        if self.tabs.currentIndex() != 1:
            return
        self.previa_head.setText("Prévia")
        ed = Edicao(
            tipo="ins",
            texto=self.ins_texto.toPlainText().rstrip(),
            modo="line" if self.rad_line.isChecked() else "code",
            codigo=self.drop_ancora.value(),
            linha=self.ins_linha.value(),
        )
        if not ed.texto:
            self.previa.setText("(digite o bloco para ver a prévia)")
            return
        if not self._marcados:
            self.previa.setText("(marque programas à esquerda para ver a prévia)")
            return
        alvo: Path | None = None
        at = -1
        for path in self._marcados:
            try:
                conteudo = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            ponto = self._ponto_insercao(conteudo, ed)
            if ponto >= 0:
                alvo, at = path, ponto
                break
        if alvo is None:
            self.previa.setText(
                f"Nenhum programa marcado tem {ed.codigo} — nada seria inserido.")
            return
        self.previa_head.setText(f"Prévia real — {alvo.name}")
        linhas = alvo.read_text(encoding="utf-8", errors="replace").split("\n")
        saida: list[str] = []
        for i in range(max(0, at - 2), at):
            saida.append(f"   {i + 1}  {linhas[i]}")
        for ln in ed.texto.split("\n"):
            saida.append(f" + ▶  {ln}")
        for i in range(at, min(len(linhas), at + 2)):
            saida.append(f"   {i + 1}  {linhas[i]}")
        self.previa.setText("\n".join(saida))
