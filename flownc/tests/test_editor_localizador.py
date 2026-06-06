"""Logica pura do localizador do editor (mudanca editor-integrado-por-arquivo).

Sem GUI: testa contagem (== find_matches), substituir todos, um a um e a borda
CNC (mesma semantica do Lote).
"""
from core.matcher import find_matches
from ui.editor_panel import (
    build_find_rule,
    count_matches,
    replace_all_spans,
    replace_one_by_one,
)

_TXT = "M8\nG54 M8\n(M80 nao conta)\nM8 fim\n"


def test_contagem_identica_ao_lote():
    spans_editor = count_matches(_TXT, "M8")
    spans_lote = find_matches(_TXT, build_find_rule("M8"))
    assert spans_editor == spans_lote
    assert len(spans_editor) == 3  # tres M8 reais


def test_borda_cnc_m8_nao_conta_dentro_de_m80():
    spans = count_matches("M80\nM8\n", "M8")
    assert len(spans) == 1  # so o M8 isolado, nao o M80


def test_substituir_todos():
    spans = count_matches(_TXT, "M8")
    out = replace_all_spans(_TXT, spans, "M08")
    assert out == "M08\nG54 M08\n(M80 nao conta)\nM08 fim\n"
    assert "M80" in out  # nao tocou o M80
    assert count_matches(out, "M8") == []  # nao sobrou M8 isolado


def test_um_a_um_substitui_e_pula():
    # 3 ocorrencias: substitui a 1a, pula a 2a, substitui a 3a.
    out = replace_one_by_one(_TXT, "M8", "M08", [True, False, True])
    assert out == "M08\nG54 M8\n(M80 nao conta)\nM08 fim\n"


def test_um_a_um_decisoes_faltantes_pulam():
    # Sem decisao para uma ocorrencia -> mantida (pula por padrao).
    out = replace_one_by_one(_TXT, "M8", "M08", [True])
    assert out == "M08\nG54 M8\n(M80 nao conta)\nM8 fim\n"
