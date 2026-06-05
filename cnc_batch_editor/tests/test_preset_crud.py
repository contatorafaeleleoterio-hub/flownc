"""Testes do CRUD de presets (Sessao B)."""
import pytest
from pathlib import Path

from core.preset_store import (
    PresetError,
    backup_before_write,
    create_preset,
    delete_preset,
    duplicate_preset,
    load_preset,
    rename_preset,
)


def test_create_cria_arquivo(tmp_path):
    path = create_preset("FANUC", tmp_path)
    assert path.exists()
    assert load_preset(path).machine == "FANUC"


def test_create_com_template_copia_regras(tmp_path):
    src = create_preset("ORIGEM", tmp_path)
    from core.models import Mode, OnZeroMatches, Rule, Scope
    import uuid
    preset = load_preset(src)
    preset.global_rules.append(
        Rule(id=uuid.uuid4().hex[:8], find="M6", replace="M06",
             scope=Scope.GLOBAL, mode=Mode.AUTO)
    )
    from core.preset_store import save_preset
    save_preset(preset, src)
    template = load_preset(src)
    dup_path = create_preset("DESTINO", tmp_path, template=template)
    dup = load_preset(dup_path)
    assert dup.machine == "DESTINO"
    assert len(dup.global_rules) == 1
    assert dup.global_rules[0].find == "M6"


def test_create_existente_falha(tmp_path):
    create_preset("FANUC", tmp_path)
    with pytest.raises(PresetError, match="ja existe"):
        create_preset("FANUC", tmp_path)


def test_duplicate(tmp_path):
    src = create_preset("ORIGINAL", tmp_path)
    dup = duplicate_preset(src, "COPIA")
    assert dup.exists()
    assert load_preset(dup).machine == "COPIA"
    assert src.exists()  # original intacto


def test_rename(tmp_path):
    src = create_preset("ANTES", tmp_path)
    new = rename_preset(src, "DEPOIS")
    assert new.exists()
    assert not src.exists()
    assert load_preset(new).machine == "DEPOIS"


def test_rename_cria_backup(tmp_path):
    src = create_preset("ANTES", tmp_path)
    rename_preset(src, "DEPOIS")
    backups = list((tmp_path / "_backups").glob("ANTES_bak*.json"))
    assert len(backups) == 1


def test_rename_destino_existente_falha(tmp_path):
    src = create_preset("ANTES", tmp_path)
    create_preset("DEPOIS", tmp_path)
    with pytest.raises(PresetError, match="ja existe"):
        rename_preset(src, "DEPOIS")


def test_delete(tmp_path):
    path = create_preset("EXCLUIR", tmp_path)
    delete_preset(path)
    assert not path.exists()


def test_delete_cria_backup(tmp_path):
    path = create_preset("EXCLUIR", tmp_path)
    delete_preset(path)
    backups = list((tmp_path / "_backups").glob("EXCLUIR_bak*.json"))
    assert len(backups) == 1


def test_delete_inexistente_falha(tmp_path):
    with pytest.raises(PresetError):
        delete_preset(tmp_path / "nao_existe.json")


def test_backup_retencao_maxima(tmp_path):
    path = create_preset("MAQUINA", tmp_path)
    for _ in range(15):
        backup_before_write(path, keep=10)
    backups = list((tmp_path / "_backups").glob("MAQUINA_bak*.json"))
    assert len(backups) <= 10


def test_backup_arquivo_ausente_nao_falha(tmp_path):
    backup_before_write(tmp_path / "nao_existe.json")  # nao deve levantar


def test_nome_invalido_caractere(tmp_path):
    with pytest.raises(PresetError):
        create_preset("nome/invalido", tmp_path)


def test_nome_invalido_vazio(tmp_path):
    with pytest.raises(PresetError):
        create_preset("", tmp_path)


def test_nome_reservado_windows(tmp_path):
    with pytest.raises(PresetError, match="reservado"):
        create_preset("CON", tmp_path)


def test_nome_path_traversal(tmp_path):
    with pytest.raises(PresetError):
        create_preset("../../evil", tmp_path)
