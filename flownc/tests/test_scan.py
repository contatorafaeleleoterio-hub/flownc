"""Testes da varredura/contagem (core/scan.py)."""
from pathlib import Path

from core.models import Mode
from core.scan import count_occurrences


def _reader(textos: dict[str, str]):
    """read_fn em memoria: mapeia str(path) -> texto, sem tocar o disco."""
    return lambda p: textos[str(p)]


def test_conta_ocorrencias_por_arquivo():
    textos = {
        "arq1": "M8\nG0 M8 X1",     # 2
        "arq2": "G0 X1 Y2",          # 0
        "arq3": "M8 S1000",          # 1
    }
    res = count_occurrences(
        "M8", Mode.CNC_ADDRESS, True,
        [Path("arq1"), Path("arq2"), Path("arq3")],
        _reader(textos),
    )
    assert res.counts == {"arq1": 2, "arq2": 0, "arq3": 1}


def test_agregado_de_cobertura():
    textos = {f"a{i}": ("M8" if i != 3 else "G0") for i in range(6)}
    res = count_occurrences(
        "M8", Mode.CNC_ADDRESS, True,
        [Path(f"a{i}") for i in range(6)],
        _reader(textos),
    )
    assert len(res.files_with_matches) == 5
    assert res.total_files == 6
    assert res.coverage_summary == "5 de 6 arquivos contem M8"


def test_boundary_aplicado_na_contagem():
    textos = {"arq": "M6\nM60\nM6 M60 M6"}  # M6 conta 3, M60 nao entra
    res = count_occurrences(
        "M6", Mode.CNC_ADDRESS, True, [Path("arq")], _reader(textos),
    )
    assert res.counts["arq"] == 3


def test_read_fn_injetavel_sem_disco(tmp_path):
    # Caminho aponta para arquivo inexistente; read_fn devolve da memoria.
    inexistente = tmp_path / "nao_existe.nc"
    res = count_occurrences(
        "M8", Mode.CNC_ADDRESS, True, [inexistente],
        lambda p: "M8 M8",
    )
    assert res.counts[str(inexistente)] == 2
    assert not inexistente.exists()


def test_zero_ocorrencias_sinalizado():
    textos = {"com": "M8", "sem": "G0 X1"}
    res = count_occurrences(
        "M8", Mode.CNC_ADDRESS, True,
        [Path("com"), Path("sem")], _reader(textos),
    )
    assert res.files_without_matches == ["sem"]
    assert "com" not in res.files_without_matches
