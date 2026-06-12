"""Tela Editor (mockup v4): faixa de arquivos à esquerda + editor em tela cheia.

Reaproveita o motor de edição existente (`ui.editor_panel.EditorPanel`) — abrir,
localizar/substituir, inserir bloco e gravação in-place segura (`core/inplace_save`,
intocado). Acrescenta o que o v4 pede: faixa de arquivos clicável, guarda de
alterações ao trocar/sair (Salvar / Descartar / Cancelar), toast "Desfazer" após
salvar e bolinha laranja de alteração não salva (na faixa e, via sinal, no rail).
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QFileSystemWatcher, Qt, QTimer, Signal
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

from core.library_store import CodeEntry
from ui.icons import icon_pixmap
from ui.editor_panel import EditorPanel


class _StripRow(QFrame):
    """Item da faixa de arquivos: nome + bolinha de alteração não salva."""

    clicado = Signal()

    def __init__(self, path: Path, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("StripRow")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._path = path
        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(8)
        self._dot = QLabel()
        self._dot.setObjectName("StripDot")
        self._dot.setVisible(False)
        lay.addWidget(self._dot)
        self._nome = QLabel(path.name)
        self._nome.setObjectName("StripName")
        lay.addWidget(self._nome, stretch=1)

    @property
    def path(self) -> Path:
        return self._path

    def set_ativo(self, ativo: bool) -> None:
        self.setProperty("ativo", ativo)
        self._repolish()

    def set_dirty(self, dirty: bool) -> None:
        self._dot.setVisible(dirty)

    def _repolish(self) -> None:
        style = self.style()
        style.unpolish(self)
        style.polish(self)

    def mousePressEvent(self, event) -> None:  # noqa: N802, ANN001
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicado.emit()
        super().mousePressEvent(event)


class _Toast(QFrame):
    """Toast inline de rodapé com ação 'Desfazer' (some sozinho em ~5 s)."""

    desfazer = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("EdToast")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(16)
        self._msg = QLabel("Salvo ✓")
        self._msg.setObjectName("EdToastMsg")
        lay.addWidget(self._msg, stretch=1)
        btn = QPushButton("Desfazer")
        btn.setObjectName("EdToastBtn")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(self._on_desfazer)
        lay.addWidget(btn)
        self.hide()

    def mostrar(self, mensagem: str) -> None:
        self._msg.setText(mensagem)
        self.show()
        QTimer.singleShot(5000, self.hide)

    def _on_desfazer(self) -> None:
        self.hide()
        self.desfazer.emit()


class EditorScreen(QWidget):
    """Tela-lugar 'Editor' (índice 1 do QStackedWidget)."""

    dirty_changed = Signal(bool)  # maestro liga no rail.set_editor_dirty

    def __init__(
        self,
        library: list[CodeEntry] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("EditorScreen")
        self._library = library or []
        self._paths: list[Path] = []
        self._rows: list[_StripRow] = []
        self._atual: Path | None = None
        self._ignorar_watch = False  # save próprio também dispara fileChanged
        self._build()
        self._watcher = QFileSystemWatcher(self)
        self._watcher.fileChanged.connect(self._on_arquivo_mudou_fora)

    # ============ construção ============
    def _build(self) -> None:
        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(16)

        # Faixa de arquivos (esquerda)
        faixa = QFrame()
        faixa.setObjectName("EdStrip")
        faixa.setFixedWidth(216)
        faixa.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        flay = QVBoxLayout(faixa)
        flay.setContentsMargins(12, 12, 12, 12)
        flay.setSpacing(8)
        titulo = QLabel("Arquivos")
        titulo.setObjectName("PTitle")
        flay.addWidget(titulo)
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        host = QWidget()
        self._strip_lay = QVBoxLayout(host)
        self._strip_lay.setContentsMargins(0, 0, 0, 0)
        self._strip_lay.setSpacing(4)
        self._strip_lay.addStretch(1)
        self._scroll.setWidget(host)
        flay.addWidget(self._scroll, stretch=1)
        lay.addWidget(faixa)

        # Editor (direita) — motor reaproveitado + estado vazio + toast
        right = QWidget()
        rlay = QVBoxLayout(right)
        rlay.setContentsMargins(0, 0, 0, 0)
        rlay.setSpacing(8)

        # Banner de alteração externa (arquivo mudou fora do FlowNC)
        self._banner_ext = QFrame()
        self._banner_ext.setObjectName("ExtChangeBanner")
        self._banner_ext.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        blay = QHBoxLayout(self._banner_ext)
        blay.setContentsMargins(12, 8, 12, 8)
        blay.setSpacing(12)
        self._banner_msg = QLabel()
        self._banner_msg.setObjectName("ExtChangeMsg")
        self._banner_msg.setWordWrap(True)
        blay.addWidget(self._banner_msg, stretch=1)
        btn_rec = QPushButton("↻ Recarregar do disco")
        btn_rec.setObjectName("ExtChangeBtn")
        btn_rec.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_rec.clicked.connect(self._recarregar_do_disco)
        blay.addWidget(btn_rec)
        btn_ign = QPushButton("Manter como está")
        btn_ign.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ign.clicked.connect(self._banner_ext.hide)
        blay.addWidget(btn_ign)
        self._banner_ext.hide()
        rlay.addWidget(self._banner_ext)

        self._empty = self._build_empty()
        rlay.addWidget(self._empty, stretch=1)

        self.panel = EditorPanel(self._library)
        self.panel.btn_close.hide()  # v4 navega pelo rail, sem "voltar"
        self.panel.dirtyChanged.connect(self._on_dirty)
        self.panel.saved.connect(self._on_saved)
        self.panel.hide()
        rlay.addWidget(self.panel, stretch=1)

        self._toast = _Toast()
        self._toast.desfazer.connect(self._on_desfazer)
        rlay.addWidget(self._toast)
        lay.addWidget(right, stretch=1)

    def _build_empty(self) -> QWidget:
        box = QFrame()
        box.setObjectName("EmptyState")
        lay = QVBoxLayout(box)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.setSpacing(12)
        ic = QLabel()
        ic.setObjectName("EmptyIcon")
        ic.setPixmap(icon_pixmap("pencil", 36, "#8FA5C2"))
        ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t1 = QLabel("Nenhum arquivo aberto")
        t1.setObjectName("EmptyT1")
        t1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t2 = QLabel("Escolha um programa na faixa ao lado, ou abra pelo ✎ na tela Lote.")
        t2.setObjectName("EmptyT2")
        t2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t2.setWordWrap(True)
        lay.addWidget(ic)
        lay.addWidget(t1)
        lay.addWidget(t2)
        return box

    # ============ API pública ============
    def set_library(self, library: list[CodeEntry]) -> None:
        self._library = library
        self.panel.set_library(library)

    def set_programs(self, paths: list[Path]) -> None:
        self._paths = list(paths)
        self._rebuild_strip()

    def abrir(self, path: Path) -> None:
        """Abre `path` no editor, com guarda se houver alteração pendente."""
        if not self._guarda_ok():
            return
        if path not in self._paths:
            self._paths.append(path)
            self._rebuild_strip()
        self._abrir_sem_guarda(path)

    def tem_alteracao(self) -> bool:
        return self.panel.tem_alteracao() if self._atual else False

    # ============ faixa ============
    def _rebuild_strip(self) -> None:
        for row in self._rows:
            row.setParent(None)
            row.deleteLater()
        self._rows = []
        for path in self._paths:
            row = _StripRow(path)
            row.clicado.connect(lambda p=path: self._on_strip_click(p))
            self._strip_lay.insertWidget(self._strip_lay.count() - 1, row)
            self._rows.append(row)
        self._sync_strip()

    def _sync_strip(self) -> None:
        for row in self._rows:
            row.set_ativo(row.path == self._atual)
            row.set_dirty(row.path == self._atual and self.tem_alteracao())

    def _on_strip_click(self, path: Path) -> None:
        if path == self._atual:
            return
        if not self._guarda_ok():
            return
        self._abrir_sem_guarda(path)

    def _abrir_sem_guarda(self, path: Path) -> None:
        self.panel.abrir(path)
        self._atual = path
        self._empty.hide()
        self._banner_ext.hide()
        self.panel.show()
        self._vigiar(path)
        self._sync_strip()

    # ============ vigilância de alteração externa ============
    def _vigiar(self, path: Path) -> None:
        """Observa só o arquivo aberto; mudou fora do FlowNC → banner de aviso."""
        antigos = self._watcher.files()
        if antigos:
            self._watcher.removePaths(antigos)
        if path.exists():
            self._watcher.addPath(str(path))

    def _on_arquivo_mudou_fora(self, caminho: str) -> None:
        if self._ignorar_watch or self._atual is None:
            return
        if str(self._atual) != caminho:
            return
        # Editores externos costumam trocar o arquivo (delete+rename): re-armar.
        QTimer.singleShot(300, lambda: self._vigiar(self._atual) if self._atual else None)
        nome = self._atual.name
        if self._atual.exists():
            self._banner_msg.setText(
                f"O arquivo {nome} foi alterado fora do FlowNC. O que você vê pode estar "
                "desatualizado — recarregue para ver a versão do disco.")
        else:
            self._banner_msg.setText(
                f"O arquivo {nome} foi removido ou renomeado fora do FlowNC.")
        self._banner_ext.show()

    def _recarregar_do_disco(self) -> None:
        if self._atual is None:
            return
        if not self._atual.exists():
            self._banner_ext.hide()
            return
        if self.panel.tem_alteracao():
            resp = QMessageBox.question(
                self,
                "Recarregar do disco",
                "Recarregar descarta as alterações não salvas deste arquivo. Continuar?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if resp != QMessageBox.StandardButton.Yes:
                return
        self._banner_ext.hide()
        self._abrir_sem_guarda(self._atual)

    # ============ guarda de alterações ============
    def _guarda_ok(self) -> bool:
        """Retorna True se pode prosseguir; trata Salvar/Descartar/Cancelar."""
        if self._atual is None or not self.panel.tem_alteracao():
            return True
        resp = QMessageBox.question(
            self,
            "Alterações não salvas",
            f"Salvar as alterações em {self._atual.name} antes de trocar?",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
        )
        if resp == QMessageBox.StandardButton.Cancel:
            return False
        if resp == QMessageBox.StandardButton.Save:
            return self.panel.salvar()
        return True  # Descartar

    def pode_sair(self) -> bool:
        """O maestro chama ao tentar sair da tela Editor (guarda de saída)."""
        return self._guarda_ok()

    # ============ dirty / toast ============
    def _on_dirty(self, dirty: bool) -> None:
        self._sync_strip()
        self.dirty_changed.emit(dirty)

    def _on_saved(self, anterior: str) -> None:
        self._pre_save = anterior
        # O save do próprio FlowNC também dispara o watcher — ignora por 1 s.
        self._ignorar_watch = True

        def rearmar() -> None:
            self._ignorar_watch = False
            if self._atual is not None:
                self._vigiar(self._atual)

        QTimer.singleShot(1000, rearmar)
        self._toast.mostrar("Salvo ✓ — gravado no original")
        self._sync_strip()

    def _on_desfazer(self) -> None:
        if hasattr(self, "_pre_save"):
            self.panel.editor.setPlainText(self._pre_save)
