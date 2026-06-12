"""Testes da Sessao D — conferencia pos-salvamento (core/conference.py)."""
from __future__ import annotations

import hashlib
from pathlib import Path


from core.conference import (
    IntegrityResult,
    format_integrity_report,
    integrity_hash,
    verify_saved,
)


def test_integrity_hash_consistente() -> None:
    data = b"G54 G90\nM30\n"
    h1 = integrity_hash(data)
    h2 = integrity_hash(data)
    assert h1 == h2
    assert h1 == hashlib.sha256(data).hexdigest()


def test_integrity_hash_sensivel_a_alteracao() -> None:
    assert integrity_hash(b"M08") != integrity_hash(b"M07")


def test_integrity_hash_vazio() -> None:
    assert integrity_hash(b"") == hashlib.sha256(b"").hexdigest()


def test_verify_saved_ok(tmp_path: Path) -> None:
    data = b"M08 T1\nG54 M30\n"
    name = "PECA01.nc"
    (tmp_path / name).write_bytes(data)
    results = verify_saved(tmp_path, [(name, data)])
    assert len(results) == 1
    r = results[0]
    assert r.ok is True
    assert r.filename == name
    assert r.error == ""
    assert r.expected_hash == integrity_hash(data)
    assert r.actual_hash == integrity_hash(data)


def test_verify_saved_divergencia(tmp_path: Path) -> None:
    expected_data = b"M07 T1\nG55 M30\n"
    gravado_data = b"M07 T1\nG55 M30\nEXTRA"  # diferente
    name = "PECA01.nc"
    (tmp_path / name).write_bytes(gravado_data)
    results = verify_saved(tmp_path, [(name, expected_data)])
    assert len(results) == 1
    r = results[0]
    assert r.ok is False
    assert r.expected_hash != r.actual_hash


def test_verify_saved_arquivo_ausente(tmp_path: Path) -> None:
    results = verify_saved(tmp_path, [("AUSENTE.nc", b"M30\n")])
    assert len(results) == 1
    r = results[0]
    assert r.ok is False
    assert r.error != ""


def test_verify_saved_multiplos(tmp_path: Path) -> None:
    files = [("A.nc", b"G54"), ("B.nc", b"M30"), ("C.nc", b"T1")]
    for name, data in files:
        (tmp_path / name).write_bytes(data)
    results = verify_saved(tmp_path, files)
    assert all(r.ok for r in results)
    assert len(results) == 3


def test_verify_saved_um_falho(tmp_path: Path) -> None:
    (tmp_path / "OK.nc").write_bytes(b"M30")
    # "FALHO.nc" nao existe
    results = verify_saved(tmp_path, [("OK.nc", b"M30"), ("FALHO.nc", b"M30")])
    oks = [r for r in results if r.ok]
    fails = [r for r in results if not r.ok]
    assert len(oks) == 1
    assert len(fails) == 1
    assert fails[0].filename == "FALHO.nc"


def test_format_integrity_report_todos_ok() -> None:
    results = [
        IntegrityResult("A.nc", "aaa", "aaa", ok=True),
        IntegrityResult("B.nc", "bbb", "bbb", ok=True),
    ]
    report = format_integrity_report(results)
    assert "OK: 2" in report
    assert "Falhas: 0" in report
    assert "ATENCAO" not in report


def test_format_integrity_report_com_falha() -> None:
    results = [
        IntegrityResult("A.nc", "aaa", "xxx", ok=False),
    ]
    report = format_integrity_report(results)
    assert "Falhas: 1" in report
    assert "ATENCAO" in report
    assert "DIVERGENCIA" in report


def test_format_integrity_report_com_erro_leitura() -> None:
    results = [
        IntegrityResult("A.nc", "aaa", "", ok=False, error="Permission denied"),
    ]
    report = format_integrity_report(results)
    assert "FALHA DE LEITURA" in report
