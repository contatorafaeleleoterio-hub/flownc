"""Stage 0 H0.1 — carga tolerante a preset malformado (sempre PresetError)."""
import json

import pytest

from core.models import OnZeroMatches, Scope
from core.preset_store import PresetError, load_preset, save_preset

_VALIDO = {
    "schema_version": 1,
    "machine": "TESTE",
    "extensions": [".nc"],
    "case_sensitive": True,
    "global_rules": [
        {"id": "r1", "find": "M08", "replace": "M07", "on_zero_matches": "error", "mode": "literal"}
    ],
    "file_rules": [],
    "verifications": [
        {"id": "v1", "type": "must_exist", "find": "M30"}
    ],
}


def _write(tmp_path, data):
    p = tmp_path / "preset.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


def test_carrega_preset_valido(tmp_path):
    preset = load_preset(_write(tmp_path, _VALIDO))
    assert preset.machine == "TESTE"
    assert preset.global_rules[0].on_zero_matches is OnZeroMatches.ERROR
    assert preset.global_rules[0].scope is Scope.GLOBAL


def test_round_trip_save_load(tmp_path):
    p = tmp_path / "out.json"
    save_preset(load_preset(_write(tmp_path, _VALIDO)), p)
    again = load_preset(p)
    assert again.machine == "TESTE"
    assert again.verifications[0].find == "M30"


@pytest.mark.parametrize("mutacao", [
    lambda d: d.pop("machine"),                       # campo obrigatorio ausente
    lambda d: d.pop("schema_version"),                # sem schema
    lambda d: d.update(schema_version=99),            # schema incompativel
    lambda d: d.update(global_rules={}),              # lista esperada, veio dict
    lambda d: d["global_rules"][0].pop("find"),       # regra sem 'find'
    lambda d: d["global_rules"][0].update(scope="x"), # enum invalido
    lambda d: d["global_rules"][0].update(on_zero_matches="talvez"),  # enum invalido
    lambda d: d["verifications"][0].pop("type"),      # verificacao sem 'type'
    lambda d: d["global_rules"][0].update(priority="muito"),  # int invalido
])
def test_malformado_levanta_preset_error(tmp_path, mutacao):
    import copy
    data = copy.deepcopy(_VALIDO)
    mutacao(data)
    with pytest.raises(PresetError):
        load_preset(_write(tmp_path, data))


def test_topo_nao_objeto_levanta_preset_error(tmp_path):
    p = tmp_path / "preset.json"
    p.write_text("[1, 2, 3]", encoding="utf-8")
    with pytest.raises(PresetError):
        load_preset(p)


def test_json_quebrado_levanta_preset_error(tmp_path):
    p = tmp_path / "preset.json"
    p.write_text("{ isto nao e json", encoding="utf-8")
    with pytest.raises(PresetError):
        load_preset(p)
