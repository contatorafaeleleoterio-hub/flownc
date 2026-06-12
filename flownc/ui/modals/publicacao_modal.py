"""Modal de Publicação — barra de progresso + gravação real (mockup v4).

`QDialog` que NÃO pode ser fechado durante a publicação. Mostra a barra de
progresso (Backup → Gravação → Conferência SHA-256), grava de verdade cada
programa marcado e, ao concluir, exibe a tela de resultado ("Publicado ✓",
caminho do backup, "Ver no Histórico" / "OK — novo lote").

Gravação segura (o original nunca se perde): copia o original para uma pasta de
backup versionada por data/hora e grava in-place via `core.inplace_save`
(atômico + conferência SHA-256). Em caso de falha, o backup é preservado e o erro
é exibido — nunca silenciado.
"""
from __future__ import annotations

import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QCloseEvent, QKeyEvent
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.file_handler import read_file
from core.inplace_save import salvar_no_lugar
from ui.lote_scan import ScanLote, aplicar_edicoes
from ui.components.compositor_v4 import Edicao


@dataclass(frozen=True)
class PublicacaoEntrada:
    """Entrada para o Histórico, devolvida ao concluir a publicação."""

    quando: str
    config: str
    edicoes: int
    programas: int
    trocas: int
    blocos: int
    backup: str


class PublicacaoModal(QDialog):
    """Publicação com progresso e gravação real; emite `ver_historico`/`novo_lote`."""

    ver_historico = Signal(object)  # PublicacaoEntrada
    novo_lote = Signal(object)      # PublicacaoEntrada

    def __init__(
        self,
        scan: ScanLote,
        edicoes: list[Edicao],
        paths: list[Path],
        backup_dir: str,
        config: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("PublicacaoModal")
        self.setWindowTitle("Publicando…")
        self.setModal(True)
        self.setMinimumSize(560, 360)
        self._scan = scan
        self._edicoes = edicoes
        self._paths = paths
        self._backup_dir = backup_dir
        self._config = config
        self._entrada: PublicacaoEntrada | None = None
        self._publicando = True
        self._build()
        QTimer.singleShot(150, self._animar)

    # ============ construção ============
    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self._head = QLabel("Publicando…")
        self._head.setObjectName("ModalHead")
        root.addWidget(self._head)

        self._body = QWidget()
        self._blay = QVBoxLayout(self._body)
        self._blay.setContentsMargins(24, 24, 24, 24)
        self._blay.setSpacing(16)
        self._blay.setAlignment(Qt.AlignmentFlag.AlignTop)
        root.addWidget(self._body, stretch=1)

        self._etapa = QLabel(
            "Backup dos originais → grava na pasta original → conferência SHA-256…")
        self._etapa.setObjectName("PubStep")
        self._etapa.setWordWrap(True)
        self._blay.addWidget(self._etapa)

        self._bar = QProgressBar()
        self._bar.setObjectName("PubProgress")
        self._bar.setRange(0, 100)
        self._bar.setValue(0)
        self._blay.addWidget(self._bar)

    # ============ progresso ============
    def _animar(self) -> None:
        valor = self._bar.value()
        valor += max(6, int((100 - valor) * 0.16))
        if valor >= 100:
            self._bar.setValue(100)
            QTimer.singleShot(250, self._finalizar)
            return
        self._bar.setValue(valor)
        QTimer.singleShot(160, self._animar)

    def _finalizar(self) -> None:
        try:
            entrada, erros = self._publicar()
        except Exception as exc:  # noqa: BLE001 — falha nunca silenciada
            self._mostrar_erro(str(exc), None)
            return
        self._publicando = False
        if erros or entrada is None:
            backup = entrada.backup if entrada else None
            self._mostrar_erro("\n".join(erros) or "Falha desconhecida", backup)
            return
        self._entrada = entrada
        self._mostrar_sucesso(entrada)

    def _publicar(self) -> tuple[PublicacaoEntrada | None, list[str]]:
        """Grava de verdade: backup versionado + gravação in-place conferida."""
        erros: list[str] = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_folder = Path(self._backup_dir) / f"_backup_orig_{timestamp}"
        tot_swap = 0
        tot_ins = 0
        gravados = 0

        backup_criado = False
        for path in self._paths:
            try:
                texto, info = read_file(path)
            except Exception as exc:  # noqa: BLE001
                erros.append(f"{path.name}: não foi possível ler ({exc})")
                continue
            editor_text = texto.replace("\r\n", "\n").replace("\r", "\n")
            final, n_swap, n_ins = aplicar_edicoes(editor_text, self._edicoes)
            tot_swap += n_swap
            tot_ins += n_ins
            if final == editor_text:
                continue  # nada mudou neste programa
            # 1) backup do original
            try:
                backup_folder.mkdir(parents=True, exist_ok=True)
                backup_criado = True
                shutil.copy2(path, backup_folder / path.name)
            except OSError as exc:
                erros.append(f"{path.name}: falha no backup ({exc})")
                continue
            # 2) gravação in-place (atômica + SHA-256)
            out = final if info.eol == "\n" else final.replace("\n", info.eol)
            res = salvar_no_lugar(path, out, info)
            if res.ok:
                gravados += 1
            else:
                erros.append(f"{path.name}: {res.mensagem}")

        quando = datetime.now().strftime("%d/%m %H:%M")
        backup_str = f"{backup_folder}\\" if backup_criado else "(nenhum arquivo alterado)"
        entrada = PublicacaoEntrada(
            quando=quando,
            config=self._config,
            edicoes=len(self._edicoes),
            programas=gravados,
            trocas=tot_swap,
            blocos=self._scan.programas_com_bloco,
            backup=backup_str,
        )
        return entrada, erros

    # ============ telas de resultado ============
    def _limpar_corpo(self) -> None:
        while self._blay.count():
            item = self._blay.takeAt(0)
            if item is None:
                continue
            w = item.widget()
            if w is not None:
                w.deleteLater()

    def _facts(self, trocas: int, blocos: int) -> str:
        partes: list[str] = []
        if trocas:
            partes.append(f"{trocas} troca" + ("" if trocas == 1 else "s"))
        if blocos:
            partes.append(f"bloco em {blocos} programa" + ("" if blocos == 1 else "s"))
        return " · ".join(partes) if partes else "nada a alterar"

    def _mostrar_sucesso(self, entrada: PublicacaoEntrada) -> None:
        self._head.setText("Publicado ✓")
        self._limpar_corpo()
        ic = QLabel("✓")
        ic.setObjectName("SavedIcon")
        ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._blay.addWidget(ic)
        resumo = QLabel(
            f"{self._facts(entrada.trocas, entrada.blocos)} — gravado em "
            f"{entrada.programas} programa{'s' if entrada.programas != 1 else ''} · "
            "originais no backup · conferência dupla OK")
        resumo.setObjectName("PubStep")
        resumo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        resumo.setWordWrap(True)
        self._blay.addWidget(resumo)
        cam = QLabel(f"backup: {entrada.backup}")
        cam.setObjectName("PubMono")
        cam.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cam.setWordWrap(True)
        cam.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._blay.addWidget(cam)

        acoes = QHBoxLayout()
        acoes.addStretch(1)
        btn_hist = QPushButton("Ver no Histórico")
        btn_hist.clicked.connect(self._on_ver_historico)
        acoes.addWidget(btn_hist)
        btn_ok = QPushButton("OK — novo lote")
        btn_ok.setObjectName("PubBtn")
        btn_ok.setProperty("estado", "orange")
        btn_ok.clicked.connect(self._on_novo_lote)
        acoes.addWidget(btn_ok)
        acoes.addStretch(1)
        cont = QWidget()
        cont.setLayout(acoes)
        self._blay.addWidget(cont)

    def _mostrar_erro(self, mensagem: str, backup: str | None) -> None:
        self._publicando = False
        self._head.setText("Falha na publicação")
        self._limpar_corpo()
        ic = QLabel("⚠")
        ic.setObjectName("ErrIcon")
        ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._blay.addWidget(ic)
        msg = QLabel(mensagem)
        msg.setObjectName("PubStep")
        msg.setWordWrap(True)
        self._blay.addWidget(msg)
        if backup:
            cam = QLabel(f"Backup já criado e preservado: {backup}")
            cam.setObjectName("PubMono")
            cam.setWordWrap(True)
            self._blay.addWidget(cam)
        acoes = QHBoxLayout()
        acoes.addStretch(1)
        btn = QPushButton("Fechar")
        btn.clicked.connect(self.reject)
        acoes.addWidget(btn)
        cont = QWidget()
        cont.setLayout(acoes)
        self._blay.addWidget(cont)

    def _on_ver_historico(self) -> None:
        if self._entrada is not None:
            self.ver_historico.emit(self._entrada)
        self.accept()

    def _on_novo_lote(self) -> None:
        if self._entrada is not None:
            self.novo_lote.emit(self._entrada)
        self.accept()

    # ============ bloqueio de fechamento durante publicação ============
    def reject(self) -> None:
        if self._publicando:
            return  # ✕/Esc desabilitados enquanto publica
        super().reject()

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if self._publicando and event.key() == Qt.Key.Key_Escape:
            event.ignore()
            return
        super().keyPressEvent(event)

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        if self._publicando:
            event.ignore()
            return
        super().closeEvent(event)
