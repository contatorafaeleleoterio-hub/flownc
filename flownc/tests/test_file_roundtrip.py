"""Vetores §15.4 (round-trip de encoding/BOM/EOL) do PRD v2.3."""
from core.file_handler import encode_text, make_output_dir, read_file, write_atomic


def _roundtrip_bytes(tmp_path, raw: bytes) -> bytes:
    src = tmp_path / "PROG.nc"
    src.write_bytes(raw)
    text, info = read_file(src)
    return encode_text(text, info)


def test_tv_rt_01_utf8_bom_preservado(tmp_path):
    raw = b"\xef\xbb\xbf%\nO0001\nM30\n%\n"
    assert _roundtrip_bytes(tmp_path, raw) == raw


def test_tv_rt_02_utf8_sem_bom_nao_adiciona(tmp_path):
    raw = b"%\nO0001\nM30\n%\n"
    out = _roundtrip_bytes(tmp_path, raw)
    assert not out.startswith(b"\xef\xbb\xbf")
    assert out == raw


def test_tv_rt_03_cp1252_com_o_cortado(tmp_path):
    raw = "(FRESA Ø12)\nM30\n".encode("cp1252")
    assert _roundtrip_bytes(tmp_path, raw) == raw


def test_tv_rt_04_utf16le_bom_preservado(tmp_path):
    raw = "%\nO0001\nM30\n%\n".encode("utf-16-le")
    raw = b"\xff\xfe" + raw
    assert _roundtrip_bytes(tmp_path, raw) == raw


def test_tv_rt_05_crlf_preservado(tmp_path):
    raw = b"%\r\nO0001\r\nM30\r\n%\r\n"
    text, info = read_file_bytes(tmp_path, raw)
    assert info.eol == "\r\n"
    assert encode_text(text, info) == raw


def test_tv_rt_06_lf_preservado(tmp_path):
    raw = b"%\nO0001\nM30\n%\n"
    text, info = read_file_bytes(tmp_path, raw)
    assert info.eol == "\n"
    assert encode_text(text, info) == raw


def test_tv_rt_07_sem_regras_byte_identico(tmp_path):
    raw = b"%\r\nO0001\r\n(FRESA)\r\nM30\r\n%\r\n"
    assert _roundtrip_bytes(tmp_path, raw) == raw


def test_tv_rt_09_atomico_sem_tmp(tmp_path):
    src = tmp_path / "OUT.nc"
    text, info = read_file_bytes(tmp_path, b"%\nM30\n%\n")
    write_atomic(src, text, info)
    assert src.exists()
    assert not (tmp_path / "OUT.nc.tmp").exists()


def read_file_bytes(tmp_path, raw: bytes):
    p = tmp_path / "X.nc"
    p.write_bytes(raw)
    return read_file(p)


def test_make_output_dir_base_dir(tmp_path):
    src = tmp_path / "origem"
    dest = tmp_path / "destino_fixo"
    src.mkdir()
    out = make_output_dir(src, "PERFIL", base_dir=dest)
    assert out.parent == dest
    assert out.exists()


def test_make_output_dir_sem_base_dir_usa_source(tmp_path):
    src = tmp_path / "origem"
    src.mkdir()
    out = make_output_dir(src, "PERFIL")
    assert out.parent == src
    assert out.exists()
