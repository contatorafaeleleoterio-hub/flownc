"""Gravacao in-place segura sem backup (mudanca editor-integrado-por-arquivo).

Cobre as garantias substitutas que tornam aceitavel a ausencia de backup:
atomicidade, preservacao de encoding/EOL, round-trip byte-a-byte, conferencia
SHA-256 e aborto seguro em falha de codificacao (original intacto, sem .tmp).
"""
from core import inplace_save
from core.file_handler import read_file
from core.inplace_save import salvar_no_lugar


def test_sobrescreve_no_lugar_preservando_cp1252_crlf(tmp_path):
    raw = "(FRESA Ø12)\r\nM30\r\n".encode("cp1252")  # Ø = O cortado
    src = tmp_path / "PROG.nc"
    src.write_bytes(raw)
    _, info = read_file(src)
    assert info.encoding == "cp1252"
    assert info.eol == "\r\n"

    novo = "(FRESA Ø16)\r\nM30\r\n"
    res = salvar_no_lugar(src, novo, info)

    assert res.ok and res.sha_conferido
    assert src.read_bytes() == novo.encode("cp1252")  # mesmo encoding/EOL


def test_round_trip_byte_a_byte_quando_nada_muda(tmp_path):
    raw = b"%\r\nO0001\r\n(FRESA)\r\nM30\r\n%\r\n"
    src = tmp_path / "PROG.nc"
    src.write_bytes(raw)
    text, info = read_file(src)

    res = salvar_no_lugar(src, text, info)

    assert res.ok
    assert src.read_bytes() == raw


def test_conferencia_sha_detecta_corrupcao(tmp_path, monkeypatch):
    raw = b"%\nO0001\nM30\n%\n"
    src = tmp_path / "PROG.nc"
    src.write_bytes(raw)
    text, info = read_file(src)

    # Simula corrupcao na escrita: o que vai pro disco difere do esperado.
    def _corrompe(path, data):
        path.write_bytes(data + b"LIXO")

    monkeypatch.setattr(inplace_save, "_write_bytes_atomic", _corrompe)

    res = salvar_no_lugar(src, text, info)

    assert not res.ok
    assert not res.sha_conferido
    assert "DIVERGENCIA" in res.mensagem.upper()


def test_falha_de_codificacao_nao_toca_o_original_nem_deixa_tmp(tmp_path):
    raw = "(FRESA Ø12)\nM30\n".encode("cp1252")  # 0xD8 forca deteccao cp1252
    src = tmp_path / "PROG.nc"
    src.write_bytes(raw)
    _, info = read_file(src)
    assert info.encoding == "cp1252"

    # Caractere fora do cp1252 -> encode_text levanta UnicodeEncodeError no preflight.
    res = salvar_no_lugar(src, "(FRESA Ø12)\nM30 中\n", info)

    assert not res.ok and not res.sha_conferido
    assert src.read_bytes() == raw  # original intacto
    assert not (tmp_path / "PROG.nc.tmp").exists()


def test_nao_cria_pasta_de_backup(tmp_path):
    raw = b"M30\n"
    src = tmp_path / "PROG.nc"
    src.write_bytes(raw)
    text, info = read_file(src)

    res = salvar_no_lugar(src, text + "M2\n", info)

    assert res.ok
    # Nada alem do proprio arquivo: sem .bak, sem pasta de backup, sem .tmp orfao.
    nomes = sorted(p.name for p in tmp_path.iterdir())
    assert nomes == ["PROG.nc"]
