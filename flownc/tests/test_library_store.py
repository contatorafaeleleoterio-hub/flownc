"""Testes do library_store (Sessao A)."""
import json
from pathlib import Path

import pytest

from core.library_store import CodeEntry, LibraryError, load_library, save_library


def test_load_ausente_retorna_vazio(tmp_path):
    assert load_library(tmp_path / "nao_existe.json") == []


def test_rejeita_item_sem_find(tmp_path):
    p = tmp_path / "lib.json"
    p.write_text(json.dumps([{"find": "", "replace": "X"}, {"replace": "Y"}]), encoding="utf-8")
    assert load_library(p) == []


def test_roundtrip_json(tmp_path):
    p = tmp_path / "lib.json"
    entries = [
        CodeEntry(find="M6", replace="M06", label="tool change"),
        CodeEntry(find="G0", replace="G00", label="rapid"),
    ]
    save_library(p, entries)
    loaded = load_library(p)
    assert {(e.find, e.replace) for e in loaded} == {("M6", "M06"), ("G0", "G00")}


def test_deduplicacao(tmp_path):
    p = tmp_path / "lib.json"
    entries = [
        CodeEntry(find="M6", replace="M06"),
        CodeEntry(find="M6", replace="M06"),
        CodeEntry(find="M6", replace="M06", label="duplicata com label diferente"),
    ]
    save_library(p, entries)
    loaded = load_library(p)
    assert len(loaded) == 1
    assert loaded[0].find == "M6"


def test_ordenacao_estavel(tmp_path):
    p = tmp_path / "lib.json"
    entries = [
        CodeEntry(find="Z", replace="z", label="ultimo"),
        CodeEntry(find="A", replace="a", label="primeiro"),
        CodeEntry(find="M", replace="m", label="meio"),
    ]
    save_library(p, entries)
    loaded = load_library(p)
    labels = [e.label for e in loaded]
    assert labels == sorted(labels)


def test_load_nao_lista_levanta_library_error(tmp_path):
    p = tmp_path / "lib.json"
    p.write_text(json.dumps({"find": "X"}), encoding="utf-8")
    with pytest.raises(LibraryError):
        load_library(p)


def test_load_json_invalido_levanta_library_error(tmp_path):
    p = tmp_path / "lib.json"
    p.write_bytes(b"isso nao e json{{{")
    with pytest.raises(LibraryError):
        load_library(p)


def test_item_sem_find_ignorado_mas_validos_carregados(tmp_path):
    p = tmp_path / "lib.json"
    p.write_text(json.dumps([
        {"find": "M6", "replace": "M06"},
        {"find": "", "replace": "ignorado"},
        {"replace": "tambem ignorado"},
    ]), encoding="utf-8")
    loaded = load_library(p)
    assert len(loaded) == 1
    assert loaded[0].find == "M6"
