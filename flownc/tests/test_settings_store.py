"""Testes do settings_store (Sessao C)."""
import json
from pathlib import Path

import pytest

from core.settings_store import AppSettings, SettingsError, load_settings, save_settings


def test_load_ausente_retorna_defaults(tmp_path):
    s = load_settings(tmp_path / "nao_existe.json")
    assert s.output_mode == "ao_lado"
    assert s.output_dir == ""


def test_roundtrip(tmp_path):
    p = tmp_path / "settings.json"
    s = AppSettings(output_mode="fixa", output_dir="C:/saida")
    save_settings(p, s)
    loaded = load_settings(p)
    assert loaded.output_mode == "fixa"
    assert loaded.output_dir == "C:/saida"


def test_load_json_invalido_retorna_defaults(tmp_path):
    p = tmp_path / "settings.json"
    p.write_bytes(b"isso nao e json{{{")
    s = load_settings(p)
    assert s.output_mode == "ao_lado"


def test_load_modo_invalido_retorna_ao_lado(tmp_path):
    p = tmp_path / "settings.json"
    p.write_text(json.dumps({"schema_version": 1, "output_mode": "invalido"}), encoding="utf-8")
    s = load_settings(p)
    assert s.output_mode == "ao_lado"


def test_load_nao_dict_retorna_defaults(tmp_path):
    p = tmp_path / "settings.json"
    p.write_text(json.dumps([1, 2, 3]), encoding="utf-8")
    s = load_settings(p)
    assert s.output_mode == "ao_lado"


def test_save_modo_invalido_levanta(tmp_path):
    p = tmp_path / "settings.json"
    with pytest.raises(SettingsError):
        save_settings(p, AppSettings(output_mode="invalido"))


def test_save_cria_pasta_pai(tmp_path):
    p = tmp_path / "subdir" / "settings.json"
    save_settings(p, AppSettings())
    assert p.exists()
