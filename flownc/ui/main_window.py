"""Janela principal do FlowNC — maestro do layout v4 (rail + 4 telas).

MainWindow monta o **topo global** (`TopBar`) acima de uma linha com a **barra
lateral** (`RailWidget`) + um `QStackedWidget` com as 4 telas-lugar, na ordem fixa
0=Lote, 1=Editor, 2=Códigos, 3=Histórico. O rail troca a tela ativa por sinal.

FASE 2 (Bloco 2): as telas são stubs e exibem dados de exemplo; a ligação ao
núcleo (`core/`) entra na Fase 3. Cada tela ganha o seu conteúdo real nos Blocos 3+.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

import app_paths
from core.library_store import CodeEntry, LibraryError, load_library
from core.models import Preset, Rule
from core.preset_store import PresetError, load_preset, save_preset
from core.settings_store import AppSettings, load_settings
from ui import theme
from ui.components import RailWidget, TopBar
from ui.components.compositor_v4 import Edicao
from ui.lote_scan import ScanLote
from ui.modals.conferencia_modal import ConferenciaModal, programas_texto
from ui.modals.publicacao_modal import PublicacaoEntrada, PublicacaoModal
from ui.screens import CodigosScreen, EditorScreen, HistoricoScreen, LoteScreen

# Índices-lugar (espelham a ordem dos botões do rail)
TELA_LOTE = 0
TELA_EDITOR = 1
TELA_CODIGOS = 2
TELA_HISTORICO = 3


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._register_fonts()
        self._apply_stylesheet()
        self.setWindowTitle("FlowNC — Substituicoes em programas CNC")
        self.resize(1180, 720)

        # Estado carregado do disco (usado pelas telas a partir dos Blocos 3+).
        self._library: list[CodeEntry] = []
        self._settings: AppSettings = AppSettings()
        self._preset_paths: dict[str, str] = {}
        self._backup_dir: str = "D:\\CNC\\backup\\"
        self._historico_entries: list[PublicacaoEntrada] = []

        self._build_ui()
        self._connect_signals()
        self._load_state()

    # ============ tema visual ============
    def _register_fonts(self) -> None:
        fonts_dir = app_paths.fonts_dir()
        for ttf in fonts_dir.glob("*.ttf"):
            font_id = QFontDatabase.addApplicationFont(str(ttf))
            if font_id < 0:
                print(f"[FlowNC] fonte nao carregada: {ttf}", file=sys.stderr)

    def _apply_stylesheet(self) -> None:
        qss_file = app_paths.qss_path()
        try:
            template = qss_file.read_text(encoding="utf-8")
            qss = theme.render_qss(template)
            self.setStyleSheet(qss)
        except (OSError, KeyError, ValueError):
            pass  # sem QSS valido: app usa estilo padrao do Qt

    # ============ construcao (maestro) ============
    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Topo global (visível em todas as telas)
        self._top = TopBar()
        root.addWidget(self._top)

        # Linha: rail (esquerda) + pilha de telas (centro)
        corpo = QWidget()
        corpo_lay = QHBoxLayout(corpo)
        corpo_lay.setContentsMargins(0, 0, 0, 0)
        corpo_lay.setSpacing(0)

        self._rail = RailWidget()
        corpo_lay.addWidget(self._rail)

        self._stack = QStackedWidget()
        self._lote = LoteScreen()
        self._editor_screen = EditorScreen()
        self._codigos = CodigosScreen()
        self._historico_screen = HistoricoScreen()
        self._stack.addWidget(self._lote)            # índice 0 = Lote
        self._stack.addWidget(self._editor_screen)   # índice 1 = Editor
        self._stack.addWidget(self._codigos)         # índice 2 = Códigos
        self._stack.addWidget(self._historico_screen)  # índice 3 = Histórico
        corpo_lay.addWidget(self._stack, stretch=1)

        root.addWidget(corpo, stretch=1)
        self._stack.setCurrentIndex(TELA_LOTE)

    def _connect_signals(self) -> None:
        self._rail.tela_mudou.connect(self._ir_para_tela)
        self._top.receita_alterada.connect(self._on_receita_alterada)
        self._top.salvar_receita_solicitado.connect(self._on_salvar_receita)
        self._top.backup_clicado.connect(self._on_trocar_backup)
        self._lote.conferir_solicitado.connect(self._on_conferir)
        self._lote.abrir_arquivo.connect(self._on_abrir_no_editor)
        self._lote.program_list.programas_alterados.connect(self._sync_editor_programs)
        self._editor_screen.dirty_changed.connect(self._rail.set_editor_dirty)
        self._codigos.biblioteca_alterada.connect(self._on_biblioteca_alterada)

    # ============ navegacao ============
    def _ir_para_tela(self, idx: int) -> None:
        # Guarda de saída do Editor: se há alteração pendente, confirmar antes.
        if self._stack.currentIndex() == TELA_EDITOR and idx != TELA_EDITOR:
            if not self._editor_screen.pode_sair():
                self._rail.set_tela_ativa(TELA_EDITOR)
                return
        self._stack.setCurrentIndex(idx)
        self._rail.set_tela_ativa(idx)

    def _sync_editor_programs(self) -> None:
        """Mantém a faixa de arquivos do Editor em dia com os programas do Lote."""
        self._editor_screen.set_programs(self._lote.program_list.get_paths())

    def _aplicar_biblioteca(self) -> None:
        """Propaga a biblioteca às telas; mantém os exemplos do v4 quando vazia."""
        self._codigos.set_library(self._library)
        self._editor_screen.set_library(self._library)
        if self._library:
            pares = [(e.find, e.label) for e in self._library]
            self._lote.compositor.set_biblioteca(pares)
        self._lote.compositor.set_modelos(self._codigos.get_modelos())

    def _on_biblioteca_alterada(self, entries: list[CodeEntry]) -> None:
        """Recadastro de códigos na tela Códigos: repropaga a todas as telas."""
        self._library = list(entries)
        self._aplicar_biblioteca()

    # ============ Conferência → Publicação (Blocos 5 e 6) ============
    def _on_conferir(self) -> None:
        edicoes = self._lote.get_edicoes()
        marcados = self._lote.program_list.get_marcados()
        if not edicoes or not marcados:
            return
        programas = programas_texto(marcados)
        modal = ConferenciaModal(edicoes, programas, self._backup_dir, self)
        modal.trocar_backup_solicitado.connect(
            lambda m=modal: self._on_trocar_backup_modal(m))
        modal.publicar_confirmado.connect(
            lambda scan, m=modal: self._on_publicar(scan, m, edicoes, marcados))
        modal.exec()

    def _on_publicar(self, scan: ScanLote, conf: ConferenciaModal,
                     edicoes: list[Edicao], marcados: list[Path]) -> None:
        conf.accept()
        pub = PublicacaoModal(
            scan, edicoes, marcados, self._backup_dir,
            self._top.cb_receita.currentText() or "sem configuração", self)
        pub.ver_historico.connect(self._on_publicado_ver_historico)
        pub.novo_lote.connect(self._on_publicado_novo_lote)
        pub.exec()

    def _on_trocar_backup_modal(self, modal: ConferenciaModal) -> None:
        if self._escolher_backup():
            modal.atualizar_backup(self._backup_dir)

    def _registrar_historico(self, entrada: PublicacaoEntrada) -> None:
        self._historico_entries.insert(0, entrada)
        self._historico_screen.set_historico(self._historico_entries)

    def _pos_publicacao(self, entrada: PublicacaoEntrada) -> None:
        """Estado 'novo lote': registra no Histórico e zera a tela Lote."""
        self._registrar_historico(entrada)
        self._lote.limpar_edicoes()
        self._lote.program_list.desmarcar_todos()
        self._lote.program_list.atualizar_lista()  # data/tamanho mudaram ao gravar

    def _on_publicado_ver_historico(self, entrada: PublicacaoEntrada) -> None:
        self._pos_publicacao(entrada)
        self._ir_para_tela(TELA_HISTORICO)

    def _on_publicado_novo_lote(self, entrada: PublicacaoEntrada) -> None:
        self._pos_publicacao(entrada)
        self._ir_para_tela(TELA_LOTE)

    def _on_abrir_no_editor(self, caminho: str) -> None:
        """Abrir o arquivo na tela Editor (Bloco 7)."""
        self._ir_para_tela(TELA_EDITOR)
        if self._stack.currentIndex() == TELA_EDITOR:
            self._editor_screen.abrir(Path(caminho))

    # ============ topo (receita/backup — Bloco 11) ============
    def _on_receita_alterada(self, nome: str) -> None:
        """Carregar a receita selecionada (Bloco 11.1)."""
        from PySide6.QtWidgets import QMessageBox
        caminho = self._preset_paths.get(nome)
        if not caminho:
            return
        try:
            preset = load_preset(Path(caminho))
        except PresetError:
            return
        edicoes = [
            Edicao(tipo="swap", origem=r.find, destino=r.replace, remover=r.replace == "")
            for r in preset.global_rules
        ]
        if self._lote.tem_edicoes():
            resp = QMessageBox.question(
                self,
                "Carregar configuração",
                f"Carregar “{nome}” substitui o lote de edições atual. Continuar?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if resp != QMessageBox.StandardButton.Yes:
                return
        self._lote.set_edicoes(edicoes)

    def _on_salvar_receita(self) -> None:
        """Salvar o lote atual como receita (Bloco 11.2)."""
        from PySide6.QtWidgets import QInputDialog
        nome, ok = QInputDialog.getText(
            self, "Salvar lote atual como…", "Nome da configuração:")
        nome = nome.strip()
        if not ok or not nome:
            return
        rules = [
            Rule(id=f"r{i + 1}", find=ed.origem, replace=ed.destino)
            for i, ed in enumerate(self._lote.get_edicoes())
            if ed.tipo == "swap"
        ]
        preset = Preset(machine=nome, global_rules=rules)
        pdir = app_paths.presets_dir()
        try:
            pdir.mkdir(parents=True, exist_ok=True)
            save_preset(preset, pdir / f"{nome}.json")
        except (PresetError, OSError):
            return
        self._preset_paths[nome] = str(pdir / f"{nome}.json")
        self._top.set_receitas(list(self._preset_paths.keys()))

    def _escolher_backup(self) -> bool:
        """Abre QFileDialog para escolher a pasta de backup; atualiza chip e estado."""
        from PySide6.QtWidgets import QFileDialog
        pasta = QFileDialog.getExistingDirectory(
            self, "Escolher pasta de backup", self._backup_dir)
        if pasta:
            self._backup_dir = pasta if pasta.endswith(("\\", "/")) else pasta + "\\"
            self._top.set_backup_path(self._backup_dir)
            return True
        return False

    def _on_trocar_backup(self) -> None:
        """Trocar a pasta de backup (Bloco 11.3)."""
        self._escolher_backup()

    # ============ carga de estado (defensiva) ============
    def _load_state(self) -> None:
        try:
            self._library = load_library(app_paths.library_path())
        except LibraryError:
            self._library = []
        self._aplicar_biblioteca()

        try:
            self._settings = load_settings(app_paths.settings_path())
        except OSError:
            self._settings = AppSettings()
        backup_dir = self._settings.backup_dir or self._settings.output_dir
        if backup_dir:
            self._backup_dir = backup_dir if backup_dir.endswith(("\\", "/")) \
                else backup_dir + "\\"
            self._top.set_backup_path(self._backup_dir)

        pdir = app_paths.presets_dir()
        files = sorted(pdir.glob("*.json")) if pdir.is_dir() else []
        self._preset_paths = {f.stem: str(f) for f in files}
        self._top.set_receitas(list(self._preset_paths.keys()))
