"""Testes de selecao de arquivos de entrada (core/file_handler.list_input_files).

Cobre o caso real do chao de fabrica: programas Fanuc tipo 'O2169' SEM extensao,
que antes eram ignorados pelo filtro de extensao.
"""
from __future__ import annotations

from pathlib import Path

from core.file_handler import list_input_files


def _touch(d: Path, name: str, content: str = "M30\n") -> None:
    (d / name).write_text(content, encoding="utf-8")


def test_curinga_aceita_qualquer_arquivo(tmp_path: Path) -> None:
    _touch(tmp_path, "PECA.nc")
    _touch(tmp_path, "programa.xyz")
    _touch(tmp_path, "O2169")
    achados = list_input_files(tmp_path, ["*"])
    assert len(achados) == 3


def test_sem_extensao_sempre_incluido(tmp_path: Path) -> None:
    # Programas Fanuc 'O####' nao tem extensao — devem entrar mesmo com filtro .nc.
    _touch(tmp_path, "O2169")
    _touch(tmp_path, "O2170")
    achados = list_input_files(tmp_path, [".nc"])
    nomes = {p.name for p in achados}
    assert nomes == {"O2169", "O2170"}


def test_filtra_por_extensao_quando_sem_curinga(tmp_path: Path) -> None:
    _touch(tmp_path, "PECA.nc")
    _touch(tmp_path, "doc.pdf")
    _touch(tmp_path, "lista.txt")
    achados = list_input_files(tmp_path, [".nc", ".txt"])
    nomes = {p.name for p in achados}
    assert nomes == {"PECA.nc", "lista.txt"}  # doc.pdf fora


def test_ignora_processado(tmp_path: Path) -> None:
    _touch(tmp_path, "PECA.nc")
    (tmp_path / "_processado_MAZAK_20260101_000000").mkdir()
    _touch(tmp_path, "_processado_MAZAK_20260101_000000_log.txt")
    achados = list_input_files(tmp_path, ["*"])
    assert {p.name for p in achados} == {"PECA.nc"}


def test_ignora_subpastas(tmp_path: Path) -> None:
    _touch(tmp_path, "PECA.nc")
    (tmp_path / "subpasta").mkdir()
    _touch(tmp_path / "subpasta", "OUTRO.nc")
    achados = list_input_files(tmp_path, ["*"])
    assert {p.name for p in achados} == {"PECA.nc"}


def test_extensao_case_insensitive(tmp_path: Path) -> None:
    _touch(tmp_path, "PECA.NC")
    _touch(tmp_path, "outro.Iso")
    achados = list_input_files(tmp_path, [".nc", ".iso"])
    assert len(achados) == 2


def test_curinga_estrela_ponto_estrela(tmp_path: Path) -> None:
    _touch(tmp_path, "a.foo")
    _touch(tmp_path, "b.bar")
    assert len(list_input_files(tmp_path, ["*.*"])) == 2


def test_ordenacao_estavel(tmp_path: Path) -> None:
    for n in ["C", "A", "B"]:
        _touch(tmp_path, n)
    achados = [p.name for p in list_input_files(tmp_path, ["*"])]
    assert achados == sorted(achados)
