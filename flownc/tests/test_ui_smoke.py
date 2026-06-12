"""Smoke tests da GUI (headless / offscreen) — estrutura v4 (rail + 4 telas).

Cobrem o maestro do v4: topo global (`TopBar`) + barra lateral (`RailWidget`) +
`QStackedWidget` com as 4 telas-lugar (Lote, Editor, Códigos, Histórico) e a
navegação entre elas. Os fluxos de cada tela são cobertos por testes próprios à
medida que cada tela é construída (Blocos 3+).
"""
from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication  # noqa: E402

from ui.components import RailWidget, TopBar  # noqa: E402
from ui.components.program_list_v4 import ProgramListV4  # noqa: E402
from ui.main_window import (  # noqa: E402
    TELA_CODIGOS,
    TELA_EDITOR,
    TELA_HISTORICO,
    TELA_LOTE,
    MainWindow,
)
from ui.screens import (  # noqa: E402
    CodigosScreen,
    EditorScreen,
    HistoricoScreen,
    LoteScreen,
)


@pytest.fixture(scope="module")
def app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


@pytest.fixture()
def win(app: QApplication) -> MainWindow:
    w = MainWindow()
    w.resize(1200, 700)
    w.show()
    app.processEvents()
    return w


# ============ estrutura / componentes ============


def test_componentes_v4_instanciam_isolados(app: QApplication) -> None:
    """Cada peça do v4 importa e instancia sem depender das demais."""
    assert RailWidget() is not None
    assert TopBar() is not None
    assert LoteScreen() is not None
    assert EditorScreen() is not None
    assert CodigosScreen() is not None
    assert HistoricoScreen() is not None


def test_maestro_monta_estrutura_v4(win: MainWindow) -> None:
    """Topo + rail + pilha de 4 telas na ordem fixa; Lote ativa por padrão."""
    assert isinstance(win._top, TopBar)
    assert isinstance(win._rail, RailWidget)
    assert win._stack.count() == 4
    assert win._stack.currentIndex() == TELA_LOTE
    assert isinstance(win._stack.widget(TELA_LOTE), LoteScreen)
    assert isinstance(win._stack.widget(TELA_EDITOR), EditorScreen)
    assert isinstance(win._stack.widget(TELA_CODIGOS), CodigosScreen)
    assert isinstance(win._stack.widget(TELA_HISTORICO), HistoricoScreen)


# ============ navegação pelo rail ============


def test_rail_sinal_troca_tela(win: MainWindow) -> None:
    """Emitir tela_mudou troca o widget central (conexão maestro)."""
    win._rail.tela_mudou.emit(TELA_HISTORICO)
    assert win._stack.currentIndex() == TELA_HISTORICO
    win._rail.tela_mudou.emit(TELA_LOTE)
    assert win._stack.currentIndex() == TELA_LOTE


def test_rail_clique_nos_4_botoes_troca_tela(win: MainWindow) -> None:
    """Clicar em cada um dos 4 botões do rail leva à tela correspondente."""
    for idx in (TELA_LOTE, TELA_EDITOR, TELA_CODIGOS, TELA_HISTORICO):
        win._rail._botoes[idx].click()
        assert win._stack.currentIndex() == idx


def test_rail_bolinha_editor_liga_desliga(win: MainWindow) -> None:
    """A bolinha de alteração não salva no botão Editor liga e desliga."""
    win._rail.set_editor_dirty(True)
    assert win._rail._dot.isVisible()
    win._rail.set_editor_dirty(False)
    assert not win._rail._dot.isVisible()


# ============ tela Lote · painel Programas ============


def _criar_programas(tmp_path, n: int = 2) -> list:
    paths = []
    for i in range(n):
        p = tmp_path / f"O{i}.nc"
        p.write_text("M8\n", encoding="utf-8")
        paths.append(p)
    return paths


def test_program_list_estado_vazio(app: QApplication) -> None:
    """Sem programas: mostra o estado vazio e esconde a lista; nada marcado."""
    pl = ProgramListV4()
    assert not pl._empty.isHidden()
    assert pl._scroll.isHidden()
    assert pl.get_marcados() == []


def test_program_list_renderiza_linhas(app: QApplication, tmp_path) -> None:
    pl = ProgramListV4()
    pl.set_programs(_criar_programas(tmp_path, 2))
    assert len(pl._rows) == 2
    assert pl._empty.isHidden()
    assert not pl._scroll.isHidden()
    assert pl._chip.text() == "0 de 2 marcados"


def test_program_list_marcar_atualiza_chip(app: QApplication, tmp_path) -> None:
    pl = ProgramListV4()
    pl.set_programs(_criar_programas(tmp_path, 2))
    pl._rows[0].toggled.emit()  # clique na primeira linha
    assert {p.name for p in pl.get_marcados()} == {"O0.nc"}
    assert pl._chip.text() == "1 de 2 marcados"


def test_program_list_marcar_todos(app: QApplication, tmp_path) -> None:
    pl = ProgramListV4()
    pl.set_programs(_criar_programas(tmp_path, 3))
    pl._toggle_all()
    assert len(pl.get_marcados()) == 3
    assert pl._btn_all.text() == "Desmarcar todos"
    pl._toggle_all()
    assert pl.get_marcados() == []
    assert pl._btn_all.text() == "Marcar todos"


def test_program_list_add_nao_duplica(app: QApplication, tmp_path) -> None:
    pl = ProgramListV4()
    progs = _criar_programas(tmp_path, 2)
    pl.add_programs(progs)
    assert len(pl._rows) == 2
    pl.add_programs(progs)  # mesmos arquivos
    assert len(pl._rows) == 2


def test_lote_screen_integra_program_list(win: MainWindow) -> None:
    lote = win._stack.widget(TELA_LOTE)
    assert isinstance(lote, LoteScreen)
    assert isinstance(lote.program_list, ProgramListV4)


# ============ tela Lote · compositor com abas (Bloco 4) ============


def test_compositor_tem_duas_abas_e_botao_unico(app: QApplication) -> None:
    """Compositor: 2 abas + 1 botão "Adicionar ao lote" desabilitado de início."""
    from ui.components.compositor_v4 import CompositorV4

    c = CompositorV4()
    assert c.tabs.count() == 2
    assert c.tabs.tabText(0) == "Trocar código"
    assert not c.btn_add.isEnabled()  # sem campos preenchidos


def test_compositor_swap_habilita_so_com_origem_e_destino(app: QApplication) -> None:
    from ui.components.compositor_v4 import CompositorV4

    c = CompositorV4()
    c.drop_origem.set_value("M8")
    assert not c.btn_add.isEnabled()  # falta destino
    c.drop_destino.set_value("M08")
    assert c.btn_add.isEnabled()


def test_compositor_remover_explicito_habilita(app: QApplication) -> None:
    from ui.components.compositor_v4 import CompositorV4

    c = CompositorV4()
    c.drop_origem.set_value("M9")
    c.drop_destino.set_value("", remover=True)
    assert c.drop_destino.is_remove()
    assert c.btn_add.isEnabled()


def test_compositor_emite_edicao_e_limpa(app: QApplication) -> None:
    from ui.components.compositor_v4 import CompositorV4, Edicao

    c = CompositorV4()
    recebidas: list[Edicao] = []
    c.adicionar.connect(recebidas.append)
    c.drop_origem.set_value("M8")
    c.drop_destino.set_value("M08")
    c._emit_add()
    assert len(recebidas) == 1
    assert recebidas[0].tipo == "swap"
    assert (recebidas[0].origem, recebidas[0].destino) == ("M8", "M08")
    assert c.drop_origem.value() == ""  # compositor limpa após adicionar


def test_compositor_aba_inserir_exige_texto(app: QApplication) -> None:
    from ui.components.compositor_v4 import CompositorV4

    c = CompositorV4()
    c.tabs.setCurrentIndex(1)
    assert not c.btn_add.isEnabled()  # textarea vazia
    c.ins_texto.setPlainText("G68 R90.\nG54")
    assert c.btn_add.isEnabled()  # texto + âncora G54 (padrão)


def test_lote_screen_adicionar_cria_cartao(app: QApplication) -> None:
    from ui.components.compositor_v4 import Edicao

    lote = LoteScreen()
    lote._on_adicionar(Edicao(tipo="swap", origem="M8", destino="M08"))
    assert len(lote._cards) == 1
    assert len(lote.get_edicoes()) == 1
    assert lote._chip.text() == "1 edição"


def test_lote_screen_conflito_mesma_origem(app: QApplication) -> None:
    from ui.components.compositor_v4 import Edicao

    lote = LoteScreen()
    lote._on_adicionar(Edicao(tipo="swap", origem="M8", destino="M08"))
    lote._on_adicionar(Edicao(tipo="swap", origem="M8", destino="M09"))
    assert lote._chip.text() == "! 1 conflito"
    assert lote._chip.property("estado") == "warn"
    assert lote._cards[0].property("warn") is True
    assert lote._cards[1].property("warn") is True


def test_lote_screen_excluir_renumera(app: QApplication) -> None:
    from ui.components.compositor_v4 import Edicao

    lote = LoteScreen()
    lote._on_adicionar(Edicao(tipo="swap", origem="M8", destino="M08"))
    lote._on_adicionar(Edicao(tipo="swap", origem="G54", destino="G55"))
    lote._on_excluir(0)
    assert len(lote._cards) == 1
    assert lote.get_edicoes()[0].origem == "G54"


def test_lote_screen_duplicar_preserva_tipo(app: QApplication) -> None:
    from ui.components.compositor_v4 import Edicao

    lote = LoteScreen()
    lote._on_adicionar(Edicao(tipo="ins", texto="G54", modo="code", codigo="G54"))
    lote._on_duplicar(0)
    assert len(lote.get_edicoes()) == 2
    assert all(e.tipo == "ins" for e in lote.get_edicoes())


def test_lote_screen_cta_regra_habilitacao(app: QApplication, tmp_path) -> None:
    from ui.components.compositor_v4 import Edicao

    lote = LoteScreen()
    assert not lote._cta.isEnabled()  # sem edição nem programa
    lote._on_adicionar(Edicao(tipo="swap", origem="M8", destino="M08"))
    assert not lote._cta.isEnabled()  # tem edição, falta programa marcado
    p = tmp_path / "O1.nc"
    p.write_text("M8\n", encoding="utf-8")
    lote.program_list.set_programs([p])
    lote.program_list._rows[0].toggled.emit()
    assert lote._cta.isEnabled()  # edição + programa marcado


def test_lote_screen_cta_emite_conferir(app: QApplication, tmp_path) -> None:
    from ui.components.compositor_v4 import Edicao

    lote = LoteScreen()
    disparos: list[bool] = []
    lote.conferir_solicitado.connect(lambda: disparos.append(True))
    lote._on_adicionar(Edicao(tipo="swap", origem="M8", destino="M08"))
    p = tmp_path / "O1.nc"
    p.write_text("M8\n", encoding="utf-8")
    lote.program_list.set_programs([p])
    lote.program_list._rows[0].toggled.emit()
    lote._cta.clicado.emit()
    assert disparos == [True]


# ============ varredura do lote + modais (Blocos 5/6) ============


def test_scan_lote_encadeia_e_conta(app: QApplication, tmp_path) -> None:
    from ui.components.compositor_v4 import Edicao
    from ui.lote_scan import scan_lote
    from ui.modals.conferencia_modal import programas_texto

    p1 = tmp_path / "O1.NC"
    p1.write_text("N10 G54\nN20 M8\nN30 M8\nN40 M30\n", encoding="utf-8")
    p2 = tmp_path / "O2.NC"
    p2.write_text("N10 G55\nN20 M9\nN30 M30\n", encoding="utf-8")
    edic = [
        Edicao(tipo="swap", origem="M8", destino="M08"),
        Edicao(tipo="ins", texto="G68 R90.", modo="code", codigo="G54"),
    ]
    scan = scan_lote(edic, programas_texto([p1, p2]))
    assert scan.total_trocas == 2
    assert scan.programas_com_bloco == 1
    assert scan.programas_afetados() == 1  # só O1 muda
    assert scan.sem_efeito() == []


def test_conferencia_modal_botao_por_estado(app: QApplication, tmp_path) -> None:
    from ui.components.compositor_v4 import Edicao
    from ui.modals.conferencia_modal import ConferenciaModal, programas_texto

    p = tmp_path / "O1.NC"
    p.write_text("N10 M8\nN20 M8\n", encoding="utf-8")
    edic = [Edicao(tipo="swap", origem="M8", destino="M08")]
    modal = ConferenciaModal(edic, programas_texto([p]), "D:\\bk\\")
    assert modal._btn_pub.isEnabled()
    assert "Publicar — 2 trocas" in modal._btn_pub.text()


def test_conferencia_modal_total_zero_desabilita(app: QApplication, tmp_path) -> None:
    from ui.components.compositor_v4 import Edicao
    from ui.modals.conferencia_modal import ConferenciaModal, programas_texto

    p = tmp_path / "O1.NC"
    p.write_text("N10 G54\n", encoding="utf-8")
    edic = [Edicao(tipo="swap", origem="M8", destino="M08")]  # M8 não existe
    modal = ConferenciaModal(edic, programas_texto([p]), "D:\\bk\\")
    assert not modal._btn_pub.isEnabled()
    assert modal._btn_pub.text() == "Nada a publicar"


def test_publicacao_modal_grava_e_faz_backup(app: QApplication, tmp_path) -> None:
    from ui.components.compositor_v4 import Edicao
    from ui.lote_scan import scan_lote
    from ui.modals.conferencia_modal import programas_texto
    from ui.modals.publicacao_modal import PublicacaoModal

    p = tmp_path / "O1.NC"
    p.write_text("N10 M8\nN20 M8\n", encoding="utf-8")
    bk = tmp_path / "backup"
    bk.mkdir()
    edic = [Edicao(tipo="swap", origem="M8", destino="M08")]
    scan = scan_lote(edic, programas_texto([p]))
    modal = PublicacaoModal(scan, edic, [p], str(bk) + "\\", "cfg")
    entrada, erros = modal._publicar()
    assert erros == []
    assert entrada is not None
    assert entrada.trocas == 2
    assert entrada.programas == 1
    assert "M08" in p.read_text(encoding="utf-8")
    assert "M8\n" not in p.read_text(encoding="utf-8")
    # backup versionado preservou o original
    backups = list(bk.glob("_backup_orig_*/O1.NC"))
    assert len(backups) == 1
    assert backups[0].read_text(encoding="utf-8") == "N10 M8\nN20 M8\n"


def test_historico_screen_estado_vazio_e_linhas(app: QApplication) -> None:
    from ui.modals.publicacao_modal import PublicacaoEntrada
    from ui.screens import HistoricoScreen

    h = HistoricoScreen()
    assert not h._empty.isHidden()
    h.set_historico([PublicacaoEntrada("12/06 10:00", "fanuc", 2, 3, 2, 1, "D:\\bk\\")])
    assert len(h._rows) == 1
    assert h._empty.isHidden()


# ============ tela Editor (Bloco 7) ============


def test_editor_screen_abre_arquivo(app: QApplication, tmp_path) -> None:
    p = tmp_path / "O1.NC"
    p.write_text("N10 G54\nN20 M8\n", encoding="utf-8")
    ed = EditorScreen()
    ed.set_programs([p])
    assert len(ed._rows) == 1
    ed.abrir(p)
    assert ed._atual == p
    assert not ed.panel.isHidden()
    assert ed._empty.isHidden()


def test_editor_screen_dirty_emite_sinal(app: QApplication, tmp_path) -> None:
    p = tmp_path / "O1.NC"
    p.write_text("N10 M8\n", encoding="utf-8")
    ed = EditorScreen()
    estados: list[bool] = []
    ed.dirty_changed.connect(estados.append)
    ed.abrir(p)
    ed.panel.editor.setPlainText("N10 M08\n")
    assert ed.tem_alteracao()
    assert estados and estados[-1] is True


def test_editor_screen_toast_desfazer_restaura(app: QApplication, tmp_path) -> None:
    p = tmp_path / "O1.NC"
    p.write_text("N10 M8\n", encoding="utf-8")
    ed = EditorScreen()
    ed.abrir(p)
    ed.panel.editor.setPlainText("N10 M08\n")
    assert ed.panel.salvar() is True
    assert "M08" in p.read_text(encoding="utf-8")
    ed._on_desfazer()  # restaura o conteúdo anterior ao save no buffer
    assert ed.panel.editor.toPlainText() == "N10 M8\n"


# ============ tela Códigos (Bloco 9) ============


def test_codigos_screen_adiciona_e_filtra(app: QApplication, tmp_path, monkeypatch) -> None:
    import app_paths
    from core.library_store import CodeEntry
    from ui.screens import CodigosScreen

    monkeypatch.setattr(app_paths, "library_path", lambda: tmp_path / "library.json")
    cs = CodigosScreen()
    cs.set_library([CodeEntry(find="G54", replace="", label="Origem 1")])
    assert len(cs._rows) == 1
    cs._busca.setText("zzz")
    assert len(cs._rows) == 0
    cs._busca.setText("")
    assert len(cs._rows) == 1


def test_codigos_screen_modelos_de_bloco(app: QApplication, tmp_path, monkeypatch) -> None:
    import app_paths
    from core.library_store import CodeEntry
    from ui.screens import CodigosScreen
    from ui.screens.codigos_screen import TAG_BLOCO

    monkeypatch.setattr(app_paths, "library_path", lambda: tmp_path / "library.json")
    cs = CodigosScreen()
    cs.set_library([
        CodeEntry(find="G54", replace="", label="Origem 1"),
        CodeEntry(find="REFRIG", replace="M8\nG43 H01", label="Liga refrig", tags=[TAG_BLOCO]),
    ])
    modelos = cs.get_modelos()
    assert modelos == [("REFRIG", "Liga refrig", "M8\nG43 H01")]


# ============ topo · receitas (Bloco 11) ============


def test_topo_carrega_receita_em_edicoes(win: MainWindow, tmp_path) -> None:
    from core.models import Preset, Rule
    from core.preset_store import save_preset

    p = tmp_path / "fanuc.json"
    save_preset(Preset(machine="fanuc", global_rules=[
        Rule(id="r1", find="M8", replace="M08"),
        Rule(id="r2", find="G54", replace=""),
    ]), p)
    win._preset_paths["fanuc"] = str(p)
    win._on_receita_alterada("fanuc")
    eds = win._lote.get_edicoes()
    assert len(eds) == 2
    assert (eds[0].origem, eds[0].destino) == ("M8", "M08")
    assert eds[1].origem == "G54" and eds[1].remover is True


# ============ editor · inserir bloco (Bloco 8.7) ============


def test_editor_ponto_insercao_ancora() -> None:
    from ui.editor_panel import ponto_insercao

    texto = "N10 G54\nN20 M8\nN30 M30\n"
    assert ponto_insercao(texto, "code", "G54", 1) == 1  # abaixo da linha do G54
    assert ponto_insercao(texto, "code", "G99", 1) == -1  # âncora ausente
    assert ponto_insercao(texto, "line", "", 2) == 2


def test_program_list_atualizar_remove_apagados(app: QApplication, tmp_path) -> None:
    """↻ Atualizar descarta arquivos apagados do disco e preserva a marcação."""
    pl = ProgramListV4()
    progs = _criar_programas(tmp_path, 3)
    pl.set_programs(progs)
    pl._rows[0].toggled.emit()  # marca o primeiro
    progs[2].unlink()           # apaga o terceiro fora do app
    pl.atualizar_lista()
    assert len(pl._rows) == 2
    assert {p.name for p in pl.get_marcados()} == {"O0.nc"}


def test_program_list_desmarcar_todos(app: QApplication, tmp_path) -> None:
    pl = ProgramListV4()
    pl.set_programs(_criar_programas(tmp_path, 2))
    pl._toggle_all()
    assert len(pl.get_marcados()) == 2
    pl.desmarcar_todos()
    assert pl.get_marcados() == []


def test_editor_banner_alteracao_externa(app: QApplication, tmp_path) -> None:
    """Arquivo alterado fora do app: banner aparece; Recarregar atualiza o buffer."""
    p = tmp_path / "O1.NC"
    p.write_text("N10 M8\n", encoding="utf-8")
    ed = EditorScreen()
    ed.abrir(p)
    assert ed._banner_ext.isHidden()
    p.write_text("N10 M08\n", encoding="utf-8")  # mudança externa
    ed._on_arquivo_mudou_fora(str(p))            # (gatilho direto: watcher é assíncrono)
    assert not ed._banner_ext.isHidden()
    ed._recarregar_do_disco()
    assert ed.panel.editor.toPlainText() == "N10 M08\n"
    assert ed._banner_ext.isHidden()


def test_publicacao_fechar_pelo_x_apos_sucesso_limpa_lote(app: QApplication, tmp_path) -> None:
    """Publicou e fechou pelo ✕ (sem clicar OK): o lote ainda assim é limpo."""
    from ui.components.compositor_v4 import Edicao
    from ui.lote_scan import scan_lote
    from ui.modals.conferencia_modal import programas_texto
    from ui.modals.publicacao_modal import PublicacaoModal

    p = tmp_path / "O1.NC"
    p.write_text("N10 M8\n", encoding="utf-8")
    bk = tmp_path / "bk"
    bk.mkdir()
    edic = [Edicao(tipo="swap", origem="M8", destino="M08")]
    scan = scan_lote(edic, programas_texto([p]))
    modal = PublicacaoModal(scan, edic, [p], str(bk) + "\\", "cfg")
    recebidos: list = []
    modal.novo_lote.connect(recebidos.append)
    entrada, erros = modal._publicar()
    modal._publicando = False
    modal._entrada = entrada
    modal.reject()  # fechar pelo Esc/✕ após sucesso
    assert len(recebidos) == 1  # ainda assim emitiu novo_lote (lote será limpo)


def test_editor_inserir_bloco_dialog_bloqueia_ancora_ausente(app: QApplication) -> None:
    from core.library_store import CodeEntry
    from ui.editor_panel import _InserirBlocoDialog

    texto = "N10 G54\nN20 M8\n"
    dlg = _InserirBlocoDialog(texto, [CodeEntry(find="G54", replace="", label="Origem")])
    dlg.ed_block.setPlainText("G68 R90.")
    dlg.cb_code.setCurrentText("G99")  # não existe no arquivo
    dlg._atualizar_previa()
    assert not dlg.btn_inserir.isEnabled()
    dlg.cb_code.setCurrentText("G54")  # existe
    dlg._atualizar_previa()
    assert dlg.btn_inserir.isEnabled()
    novo, at = dlg.resultado()
    assert at == 1
    assert novo.split("\n")[1] == "G68 R90."
