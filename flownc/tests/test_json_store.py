"""Stage 0 H0.5 — escrita atomica de JSON de configuracao."""
import pytest

from core.json_store import read_json, write_json_atomic


def test_round_trip(tmp_path):
    path = tmp_path / "cfg.json"
    data = {"schema_version": 1, "itens": ["M08", "G54"], "ativo": True}
    write_json_atomic(path, data)
    assert read_json(path) == data


def test_cria_pasta_pai(tmp_path):
    path = tmp_path / "sub" / "dir" / "cfg.json"
    write_json_atomic(path, {"ok": 1})
    assert read_json(path) == {"ok": 1}


def test_utf8_sem_escape(tmp_path):
    path = tmp_path / "cfg.json"
    write_json_atomic(path, {"nome": "Nevoa/refrigeracao acao"})
    assert "acao" in path.read_text(encoding="utf-8")


def test_dado_invalido_nao_corrompe_destino(tmp_path):
    path = tmp_path / "cfg.json"
    write_json_atomic(path, {"valido": True})
    original = path.read_bytes()
    # set nao e serializavel em JSON -> json.dumps levanta TypeError ANTES de tocar no arquivo.
    with pytest.raises(TypeError):
        write_json_atomic(path, {"ruim": {1, 2, 3}})
    assert path.read_bytes() == original          # destino intacto
    assert not (path.with_name(path.name + ".tmp")).exists()  # sem temporario orfao
