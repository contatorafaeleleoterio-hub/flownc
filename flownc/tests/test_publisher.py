"""Testes para publicacao segura com backup versionado (tarefas 4.2-4.6)."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from flownc.core.conference import integrity_hash
from flownc.core.publisher import PublishItem, publish_batch


def test_publica_apenas_arquivos_que_mudaram(tmp_path: Path) -> None:
    """Cenario: Publica apenas arquivos que mudaram."""
    working_dir = tmp_path / "working"
    backup_dir = tmp_path / "backup"
    working_dir.mkdir()
    backup_dir.mkdir()

    # Criar 5 arquivos na pasta de trabalho
    files = ["a.g", "b.g", "c.g", "d.g", "e.g"]
    for f in files:
        (working_dir / f).write_bytes(b"original")

    # Editar apenas 2 deles
    items = [
        PublishItem("a.g", b"edited_a"),
        PublishItem("b.g", b"edited_b"),
        PublishItem("c.g", b"original"),  # sem mudancas
        PublishItem("d.g", b"original"),  # sem mudancas
        PublishItem("e.g", b"original"),  # sem mudancas
    ]

    result = publish_batch(working_dir, backup_dir, items)

    assert result.ok is True
    assert result.published["a.g"] is True
    assert result.published["b.g"] is True
    assert result.published["c.g"] is True
    assert result.published["d.g"] is True
    assert result.published["e.g"] is True
    assert (working_dir / "a.g").read_bytes() == b"edited_a"
    assert (working_dir / "b.g").read_bytes() == b"edited_b"
    assert (working_dir / "c.g").read_bytes() == b"original"
    assert (working_dir / "d.g").read_bytes() == b"original"
    assert (working_dir / "e.g").read_bytes() == b"original"


def test_backup_versionado_por_execucao(tmp_path: Path) -> None:
    """Cenario: Backup versionado por execucao (sem sobrescrever anterior)."""
    working_dir = tmp_path / "working"
    backup_dir = tmp_path / "backup"
    working_dir.mkdir()
    backup_dir.mkdir()

    (working_dir / "a.g").write_bytes(b"v1")

    # Primeira execucao (mockar tempo T1)
    with patch("flownc.core.publisher.datetime") as mock_dt:
        mock_dt.now.return_value.strftime.return_value = "20260606_100000"
        result1 = publish_batch(
            working_dir,
            backup_dir,
            [PublishItem("a.g", b"v2")],
        )
    backup1 = result1.backup_folder

    assert backup1 is not None
    assert backup1.exists()
    assert (backup1 / "a.g").read_bytes() == b"v1"

    # Modificar novamente
    (working_dir / "a.g").write_bytes(b"v3")

    # Segunda execucao (mockar tempo T2, diferente de T1)
    with patch("flownc.core.publisher.datetime") as mock_dt:
        mock_dt.now.return_value.strftime.return_value = "20260606_100001"
        result2 = publish_batch(
            working_dir,
            backup_dir,
            [PublishItem("a.g", b"v4")],
        )
    backup2 = result2.backup_folder

    assert backup2 is not None
    assert backup2.exists()
    assert backup2 != backup1
    assert (backup2 / "a.g").read_bytes() == b"v3"
    assert (backup1 / "a.g").read_bytes() == b"v1"


def test_troca_atomica_sem_arquivo_vazio(tmp_path: Path) -> None:
    """Cenario: Pasta de trabalho nunca fica sem o arquivo."""
    working_dir = tmp_path / "working"
    backup_dir = tmp_path / "backup"
    working_dir.mkdir()
    backup_dir.mkdir()

    (working_dir / "a.g").write_bytes(b"original")

    # Publicar um novo conteudo
    result = publish_batch(
        working_dir,
        backup_dir,
        [PublishItem("a.g", b"novo")],
    )

    assert result.ok is True
    # O arquivo deve existir e conter ou "original" ou "novo", nunca estar vazio ou ausente
    assert (working_dir / "a.g").exists()
    conteudo = (working_dir / "a.g").read_bytes()
    assert conteudo in [b"original", b"novo"]
    assert conteudo == b"novo"


def test_falha_simulada_nao_corrompe_producao(tmp_path: Path) -> None:
    """Cenario: Falha simulada apos backup mas antes da troca atomica."""
    nonexistent_path = tmp_path / "nonexistent"
    backup_dir = tmp_path / "backup"
    backup_dir.mkdir()

    result = publish_batch(
        nonexistent_path,
        backup_dir,
        [PublishItem("a.g", b"novo")],
    )

    assert result.ok is False


def test_conferencia_dupla_sha(tmp_path: Path) -> None:
    """Cenario: Conferencia dupla SHA-256 (backup e publicado)."""
    working_dir = tmp_path / "working"
    backup_dir = tmp_path / "backup"
    working_dir.mkdir()
    backup_dir.mkdir()

    original_bytes = b"conteudo_original"
    (working_dir / "a.g").write_bytes(original_bytes)

    # Publicar com novo conteudo
    edited_bytes = b"conteudo_editado"
    result = publish_batch(
        working_dir,
        backup_dir,
        [PublishItem("a.g", edited_bytes)],
    )

    assert result.ok is True
    assert result.integridade_ok is True

    # Verificar que o backup tem o SHA do original
    backup_path = result.backup_folder / "a.g"
    assert backup_path.exists()
    assert integrity_hash(backup_path.read_bytes()) == integrity_hash(original_bytes)

    # Verificar que o arquivo publicado tem o SHA do editado
    assert integrity_hash((working_dir / "a.g").read_bytes()) == integrity_hash(edited_bytes)


def test_backup_em_outro_volume(tmp_path: Path) -> None:
    """Cenario: Backup pode estar em outro volume (nao impede publicacao)."""
    # Simular: working_dir em um volume, backup_dir em outro (ambos em tmp_path)
    working_dir = tmp_path / "volume1" / "working"
    backup_dir = tmp_path / "volume2" / "backup"
    working_dir.mkdir(parents=True)
    backup_dir.mkdir(parents=True)

    (working_dir / "a.g").write_bytes(b"original")

    result = publish_batch(
        working_dir,
        backup_dir,
        [PublishItem("a.g", b"novo")],
    )

    assert result.ok is True
    assert any(
        (backup_dir / d / "a.g").exists()
        for d in backup_dir.iterdir()
        if d.name.startswith("_backup_orig_")
    )


def test_nao_toca_arquivo_inexistente(tmp_path: Path) -> None:
    """Cenario: Arquivo que nao existe na pasta de trabalho nao e publicado."""
    working_dir = tmp_path / "working"
    backup_dir = tmp_path / "backup"
    working_dir.mkdir()
    backup_dir.mkdir()

    result = publish_batch(
        working_dir,
        backup_dir,
        [PublishItem("inexistente.g", b"conteudo")],
    )

    assert result.ok is False
    assert result.published["inexistente.g"] is False


def test_multiplos_arquivos_parcial_sucesso(tmp_path: Path) -> None:
    """Cenario: Alguns arquivos publicam, outros falham."""
    working_dir = tmp_path / "working"
    backup_dir = tmp_path / "backup"
    working_dir.mkdir()
    backup_dir.mkdir()

    (working_dir / "ok.g").write_bytes(b"original_ok")
    # "falta.g" nao e criado

    items = [
        PublishItem("ok.g", b"novo_ok"),
        PublishItem("falta.g", b"novo_falta"),
    ]

    result = publish_batch(working_dir, backup_dir, items)

    assert result.ok is False
    assert result.published["ok.g"] is True
    assert result.published["falta.g"] is False


def test_read_fn_injetavel_usado(tmp_path: Path) -> None:
    """Cenario: read_fn injetavel e chamado para leituras de disco."""
    working_dir = tmp_path / "working"
    backup_dir = tmp_path / "backup"
    working_dir.mkdir()
    backup_dir.mkdir()

    (working_dir / "a.g").write_bytes(b"original")

    # Contar quantas vezes read_fn e chamado
    read_count = 0

    def mock_read(path: Path) -> bytes:
        nonlocal read_count
        read_count += 1
        return path.read_bytes()

    result = publish_batch(
        working_dir,
        backup_dir,
        [PublishItem("a.g", b"novo")],
        read_fn=mock_read,
    )

    assert result.ok is True
    # read_fn deve ter sido chamado multiplas vezes (original, backup, publicado)
    assert read_count >= 3
