"""Modal de Conferência — números reais antes de gravar (mockup v4).

`QDialog` bloqueante que varre os programas marcados com as edições do lote (via
`ui.lote_scan.scan_lote`, mesmo motor da publicação) e mostra: faixa de total,
avisos de conflito/sem-efeito, um cartão por edição (com programas afetados e
exemplo real) e um rodapé fixo com o botão de publicar conforme o estado. Nada é
gravado aqui — o botão emite `publicar_confirmado(ScanLote)`.
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ui.components.compositor_v4 import Edicao
from ui.lote_scan import EdicaoResultado, ScanLote, scan_lote


def _facts(trocas: int, programas_bloco: int) -> str:
    partes: list[str] = []
    if trocas:
        partes.append(f"{trocas} troca" + ("" if trocas == 1 else "s"))
    if programas_bloco:
        plural = "" if programas_bloco == 1 else "s"
        partes.append(f"bloco em {programas_bloco} programa{plural}")
    return " · ".join(partes) if partes else "nada a alterar"


def _formula(ed: Edicao) -> str:
    if ed.tipo == "ins":
        n = len(ed.texto.split("\n")) if ed.texto else 0
        plural = "s" if n > 1 else ""
        ancora = f"após {ed.codigo}" if ed.modo == "code" else f"após a linha {ed.linha}"
        return f"➕ bloco · {n} linha{plural} · {ancora}"
    if ed.remover:
        return f"{ed.origem} → remover"
    return f"{ed.origem} → {ed.destino}"


class ConferenciaModal(QDialog):
    """Conferência do lote — números reais; emite `publicar_confirmado(ScanLote)`."""

    publicar_confirmado = Signal(object)  # ScanLote
    trocar_backup_solicitado = Signal()

    def __init__(
        self,
        edicoes: list[Edicao],
        programas: dict[str, str],
        backup_dir: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("ConferenciaModal")
        self.setWindowTitle("Conferência do lote — números reais")
        self.setModal(True)
        self.setMinimumSize(720, 600)
        self._edicoes = edicoes
        self._programas = programas
        self._backup_dir = backup_dir
        self._scan: ScanLote = scan_lote(edicoes, programas)
        self._build()
        self._preencher()

    # ============ construção ============
    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        head = QLabel("Conferência do lote — números reais")
        head.setObjectName("ModalHead")
        root.addWidget(head)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        body = QWidget()
        self._body = QVBoxLayout(body)
        self._body.setContentsMargins(20, 20, 20, 20)
        self._body.setSpacing(12)
        self._scroll.setWidget(body)
        root.addWidget(self._scroll, stretch=1)

        # Rodapé fixo
        footer = QFrame()
        footer.setProperty("modalFooter", True)
        footer.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        flay = QVBoxLayout(footer)
        flay.setContentsMargins(20, 12, 20, 12)
        flay.setSpacing(8)
        self._facts_lbl = QLabel()
        self._facts_lbl.setObjectName("ConfFacts")
        self._facts_lbl.setWordWrap(True)
        flay.addWidget(self._facts_lbl)
        brow = QHBoxLayout()
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        brow.addWidget(btn_cancelar)
        brow.addStretch(1)
        self._btn_pub = QPushButton()
        self._btn_pub.setObjectName("PubBtn")
        self._btn_pub.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_pub.clicked.connect(self._on_publicar)
        brow.addWidget(self._btn_pub)
        flay.addLayout(brow)
        root.addWidget(footer)

    # ============ preenchimento ============
    def _conflitos(self) -> list[str]:
        contagem: dict[str, int] = {}
        for ed in self._edicoes:
            if ed.tipo == "swap":
                contagem[ed.origem] = contagem.get(ed.origem, 0) + 1
        return [c for c, n in contagem.items() if n > 1]

    def _preencher(self) -> None:
        scan = self._scan
        total = scan.total_geral
        n_sel = len(self._programas)
        n_hit = scan.programas_afetados()
        conflitos = self._conflitos()

        # Faixa de resumo
        faixa = QFrame()
        faixa.setObjectName("ConfSum")
        faixa.setProperty("zero", total == 0)
        faixa.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        fx = QHBoxLayout(faixa)
        fx.setContentsMargins(16, 16, 16, 16)
        fx.setSpacing(16)
        num = QLabel(str(total))
        num.setObjectName("ConfSumN")
        fx.addWidget(num)
        col = QVBoxLayout()
        if total == 0:
            t1 = QLabel("nenhuma alteração encontrada nos programas marcados")
        else:
            plural = "ão" if total == 1 else "ões"
            t1 = QLabel(f"alteraç{plural} em {n_hit} de {n_sel} programas marcados")
        t1.setObjectName("ConfSumT")
        t1.setWordWrap(True)
        col.addWidget(t1)
        sub = QLabel(
            f"{_facts(scan.total_trocas, scan.programas_com_bloco)} · nada foi gravado ainda")
        sub.setObjectName("ConfSumSub")
        col.addWidget(sub)
        fx.addLayout(col, stretch=1)
        self._body.addWidget(faixa)

        # Avisos: conflitos + sem efeito
        for c in conflitos:
            self._body.addWidget(self._aviso(
                f"▲ Conflito: {c} é alterado por mais de uma edição — revise antes de publicar."))
        for ed in scan.sem_efeito():
            if ed.tipo == "ins":
                if ed.modo == "code":
                    msg = (f"⚠ Bloco sem destino: o código {ed.codigo} não aparece em "
                           "nenhum programa marcado — nada será inserido.")
                else:
                    msg = "⚠ Bloco sem destino: nenhum programa marcado recebe a posição."
            else:
                msg = (f"⚠ {ed.origem} não aparece em nenhum programa marcado — "
                       "esta edição não vai trocar nada.")
            self._body.addWidget(self._aviso(msg))

        # Cartão por edição
        for i, res in enumerate(scan.resultados):
            self._body.addWidget(self._cartao(i, res))

        # Linha de backup
        linha = QFrame()
        linha.setObjectName("BackupLine")
        linha.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        bl = QHBoxLayout(linha)
        bl.setContentsMargins(12, 10, 12, 10)
        txt = QLabel(
            f"🛡 Ao publicar: originais vão para {self._backup_dir} (versionado por "
            "data/hora) · gravação na pasta original com conferência dupla")
        txt.setObjectName("BackupLineTxt")
        txt.setWordWrap(True)
        bl.addWidget(txt, stretch=1)
        btn_mudar = QPushButton("Mudar pasta")
        btn_mudar.clicked.connect(self.trocar_backup_solicitado.emit)
        bl.addWidget(btn_mudar)
        self._body.addWidget(linha)
        self._body.addStretch(1)

        # Rodapé conforme estado
        n_conf = len(conflitos)
        if total == 0:
            self._facts_lbl.setText("nada a publicar")
            self._btn_pub.setText("Nada a publicar")
            self._btn_pub.setEnabled(False)
            self._btn_pub.setProperty("estado", "ghost")
        else:
            prefixo = (f"▲ {n_conf} conflito{'s' if n_conf > 1 else ''} no lote · "
                       if n_conf else "")
            self._facts_lbl.setText(
                prefixo
                + "nada foi gravado — “Publicar” aplica e guarda os originais no backup")
            facts = _facts(scan.total_trocas, scan.programas_com_bloco)
            verbo = "Publicar mesmo assim — " if n_conf else "Publicar — "
            self._btn_pub.setText(verbo + facts)
            self._btn_pub.setEnabled(True)
            self._btn_pub.setProperty("estado", "warn" if n_conf else "orange")
        self._repolish(self._btn_pub)

    def _aviso(self, texto: str) -> QLabel:
        lbl = QLabel(texto)
        lbl.setObjectName("ConfWarn")
        lbl.setWordWrap(True)
        return lbl

    def _cartao(self, indice: int, res: EdicaoResultado) -> QWidget:
        ed = res.edicao
        card = QFrame()
        card.setObjectName("ConfCard")
        card.setProperty("zero", res.total == 0)
        card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(8)

        # Cabeçalho do cartão
        h = QHBoxLayout()
        idx = QLabel(f"{indice + 1:02d}")
        idx.setObjectName("RIdx")
        h.addWidget(idx)
        f = QLabel(_formula(ed))
        f.setObjectName("ConfFormula")
        h.addWidget(f, stretch=1)
        hits = [p for p in res.por_programa if p.n]
        if ed.tipo == "ins":
            tot_txt = ("não insere" if res.total == 0
                       else f"insere em {res.total} de {len(res.por_programa)} programas")
        else:
            tot_txt = ("0 trocas" if res.total == 0
                       else f"{res.total} troca{'s' if res.total > 1 else ''} "
                            f"em {len(hits)} programa{'s' if len(hits) > 1 else ''}")
        tot = QLabel(tot_txt)
        tot.setObjectName("ConfTot")
        h.addWidget(tot)
        lay.addLayout(h)

        # Programas afetados (com zeros recolhidos)
        zeros = len(res.por_programa) - len(hits)
        for p in hits:
            row = QHBoxLayout()
            nome = QLabel(p.nome)
            nome.setObjectName("CfName")
            row.addWidget(nome, stretch=1)
            if ed.tipo == "ins":
                detalhe = "insere o bloco"
            else:
                detalhe = f"{p.n} ocorrência{'s' if p.n > 1 else ''}"
            cn = QLabel(detalhe)
            cn.setObjectName("CfN")
            row.addWidget(cn)
            lay.addLayout(row)
        if zeros:
            row = QHBoxLayout()
            sufixo = f" sem {ed.origem}" if ed.tipo == "swap" else ""
            nome = QLabel(f"+ {zeros} programa{'s' if zeros > 1 else ''}{sufixo}")
            nome.setObjectName("CfNameZero")
            row.addWidget(nome, stretch=1)
            cn = QLabel("nada muda" if ed.tipo == "swap" else "não recebe o bloco")
            cn.setObjectName("CfNZero")
            row.addWidget(cn)
            lay.addLayout(row)

        # Exemplo real (swap) ou prévia do bloco (ins)
        if ed.tipo == "swap" and res.exemplo is not None:
            ex = res.exemplo
            exrow = QHBoxLayout()
            tag = QLabel("exemplo real")
            tag.setObjectName("ConfTag")
            exrow.addWidget(tag)
            old = QLabel(ex.original.strip())
            old.setObjectName("ConfExOld")
            exrow.addWidget(old)
            exrow.addWidget(QLabel("→"))
            novo_txt = ex.novo.strip() or "(linha removida)"
            new = QLabel(novo_txt)
            new.setObjectName("ConfExNew")
            exrow.addWidget(new)
            onde = QLabel(f"{ex.arquivo} · linha {ex.linha}")
            onde.setObjectName("ConfExWhere")
            exrow.addWidget(onde, stretch=1)
            lay.addLayout(exrow)
        elif ed.tipo == "ins" and ed.texto:
            exrow = QHBoxLayout()
            tag = QLabel("bloco")
            tag.setObjectName("ConfTag")
            exrow.addWidget(tag)
            bloco = QLabel(ed.texto.replace("\n", "  ⏎  "))
            bloco.setObjectName("ConfExNew")
            exrow.addWidget(bloco, stretch=1)
            lay.addLayout(exrow)
        return card

    @staticmethod
    def _repolish(w: QWidget) -> None:
        style = w.style()
        style.unpolish(w)
        style.polish(w)

    # ============ ações ============
    def _on_publicar(self) -> None:
        self.publicar_confirmado.emit(self._scan)

    def atualizar_backup(self, backup_dir: str) -> None:
        """Reabre a varredura/visual com a nova pasta de backup."""
        self._backup_dir = backup_dir
        # Recria o corpo (simples e seguro: limpa e repreenche).
        while self._body.count():
            item = self._body.takeAt(0)
            if item is None:
                continue
            w = item.widget()
            if w is not None:
                w.deleteLater()
        self._preencher()


def programas_texto(paths: list[Path]) -> dict[str, str]:
    """Lê os programas marcados como mapa nome -> texto (para a varredura)."""
    out: dict[str, str] = {}
    for p in paths:
        try:
            out[p.name] = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            out[p.name] = ""
    return out
