"""Carga, validacao e CRUD de presets JSON (PRD secao 13). Sem dependencia externa.

Stage 0 (H0.1): toda falha de preset malformado vira `PresetError` com campo +
motivo — nunca `KeyError`/`ValueError`/`TypeError` cru (que derrubaria a GUI).
Stage 0 (H0.5): `save_preset` grava de forma atomica via `core.json_store`.
Sessao B: create/duplicate/rename/delete + backup_before_write (retencao 10).
"""
from __future__ import annotations

import json
import re
import shutil

from enum import Enum
from pathlib import Path
from typing import TypeVar

from .json_store import read_json, write_json_atomic
from .models import (
    Mode,
    OnZeroMatches,
    Preset,
    Rule,
    Scope,
    Verification,
    VerificationType,
)

SUPPORTED_SCHEMA = 1

_E = TypeVar("_E", bound=Enum)

_SAFE_NAME_RE = re.compile(r"^[A-Za-z0-9._\- ]+$")
_WINDOWS_RESERVED = {
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
}


class PresetError(Exception):
    """Preset invalido ou de schema incompativel (PRD secao 13.2)."""


# ---------- helpers de validacao (H0.1): falham sempre como PresetError ----------

def _require_dict(value: object, where: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise PresetError(f"{where}: esperado objeto JSON, veio {type(value).__name__}.")
    return value


def _require_list(value: object, where: str) -> list[object]:
    if not isinstance(value, list):
        raise PresetError(f"{where}: esperado lista, veio {type(value).__name__}.")
    return value


def _as_str(value: object, where: str, *, default: str | None = None) -> str:
    """Coage escalar para str; rejeita None (sem default), dict e list."""
    if value is None:
        if default is not None:
            return default
        raise PresetError(f"Campo '{where}' ausente ou nulo.")
    if isinstance(value, (dict, list)):
        raise PresetError(f"Campo '{where}': esperado texto, veio {type(value).__name__}.")
    return str(value)


def _as_int(value: object, where: str, default: int) -> int:
    if value is None:
        return default
    if isinstance(value, (int, float, str)):  # bool e subclasse de int
        try:
            return int(value)
        except (TypeError, ValueError) as exc:
            raise PresetError(f"Campo '{where}': esperado inteiro, veio {value!r}.") from exc
    raise PresetError(f"Campo '{where}': esperado inteiro, veio {value!r}.")


def _enum(enum_cls: type[_E], value: object, where: str) -> _E:
    if value is None:
        raise PresetError(f"Campo '{where}' ausente.")
    try:
        return enum_cls(value)
    except ValueError as exc:
        validos = ", ".join(e.value for e in enum_cls)
        raise PresetError(
            f"Campo '{where}': valor {value!r} invalido (validos: {validos})."
        ) from exc


def _rule_from_dict(d: object, default_scope: Scope, where: str) -> Rule:
    d = _require_dict(d, where)
    file_val = d.get("file")
    if file_val is not None and not isinstance(file_val, str):
        raise PresetError(f"{where}.file: esperado texto, veio {type(file_val).__name__}.")
    return Rule(
        id=_as_str(d.get("id"), f"{where}.id"),
        find=_as_str(d.get("find"), f"{where}.find"),
        replace=_as_str(d.get("replace", ""), f"{where}.replace", default=""),
        scope=_enum(Scope, d.get("scope", default_scope.value), f"{where}.scope"),
        mode=_enum(Mode, d.get("mode", "auto"), f"{where}.mode"),
        active=bool(d.get("active", True)),
        file=file_val,
        comment=_as_str(d.get("comment", ""), f"{where}.comment", default=""),
        on_zero_matches=_enum(OnZeroMatches, d.get("on_zero_matches", "warn"),
                              f"{where}.on_zero_matches"),
        priority=_as_int(d.get("priority", 100), f"{where}.priority", 100),
    )


def _verification_from_dict(d: object, where: str) -> Verification:
    d = _require_dict(d, where)
    return Verification(
        id=_as_str(d.get("id"), f"{where}.id"),
        type=_enum(VerificationType, d.get("type"), f"{where}.type"),
        find=_as_str(d.get("find"), f"{where}.find"),
        mode=_enum(Mode, d.get("mode", "literal"), f"{where}.mode"),
        label=_as_str(d.get("label", ""), f"{where}.label", default=""),
        count=_as_int(d.get("count", 0), f"{where}.count", 0),
    )


def load_preset(path: Path) -> Preset:
    try:
        data = read_json(Path(path))
    except (OSError, json.JSONDecodeError) as exc:
        raise PresetError(f"Falha ao ler preset: {exc}") from exc

    data = _require_dict(data, "preset (topo)")

    schema = data.get("schema_version")
    if schema is None:
        raise PresetError("Preset sem 'schema_version' (secao 13.2).")
    if schema != SUPPORTED_SCHEMA:
        raise PresetError(
            f"schema_version {schema} incompativel (suportado: {SUPPORTED_SCHEMA})."
        )

    extensions = _require_list(data.get("extensions", [".nc", ".txt"]), "extensions")
    global_raw = _require_list(data.get("global_rules", []), "global_rules")
    file_raw = _require_list(data.get("file_rules", []), "file_rules")
    verif_raw = _require_list(data.get("verifications", []), "verifications")

    return Preset(
        machine=_as_str(data.get("machine"), "machine"),
        schema_version=schema,
        description=_as_str(data.get("description", ""), "description", default=""),
        extensions=[_as_str(e, f"extensions[{i}]") for i, e in enumerate(extensions)],
        case_sensitive=bool(data.get("case_sensitive", True)),
        global_rules=[_rule_from_dict(r, Scope.GLOBAL, f"global_rules[{i}]")
                      for i, r in enumerate(global_raw)],
        file_rules=[_rule_from_dict(r, Scope.FILE, f"file_rules[{i}]")
                    for i, r in enumerate(file_raw)],
        verifications=[_verification_from_dict(v, f"verifications[{i}]")
                       for i, v in enumerate(verif_raw)],
    )


def all_rules(preset: Preset) -> list[Rule]:
    """Regras globais primeiro, depois de arquivo (ordem de declaracao, secao 8.4)."""
    return [*preset.global_rules, *preset.file_rules]


def _rule_to_dict(r: Rule) -> dict[str, object]:
    d: dict[str, object] = {
        "id": r.id,
        "active": r.active,
        "scope": r.scope.value,
        "find": r.find,
        "replace": r.replace,
        "mode": r.mode.value,
        "comment": r.comment,
        "on_zero_matches": r.on_zero_matches.value,
        "priority": r.priority,
    }
    if r.scope is Scope.FILE and r.file:
        d["file"] = r.file
    return d


def _verification_to_dict(v: Verification) -> dict[str, object]:
    return {
        "id": v.id,
        "type": v.type.value,
        "find": v.find,
        "mode": v.mode.value,
        "label": v.label,
        "count": v.count,
    }


def save_preset(preset: Preset, path: Path) -> None:
    """Grava o preset em JSON (UTF-8) de forma atomica (H0.5). Usado por 'Salvar perfil'."""
    data = {
        "schema_version": preset.schema_version,
        "machine": preset.machine,
        "description": preset.description,
        "extensions": preset.extensions,
        "case_sensitive": preset.case_sensitive,
        "global_rules": [_rule_to_dict(r) for r in preset.global_rules],
        "file_rules": [_rule_to_dict(r) for r in preset.file_rules],
        "verifications": [_verification_to_dict(v) for v in preset.verifications],
    }
    write_json_atomic(Path(path), data)


# ---------- CRUD de presets (Sessao B) ----------

def _validate_name(name: str) -> None:
    """Valida nome de perfil: charset seguro, sem reservados Windows, sem traversal."""
    if not name or not name.strip():
        raise PresetError("Nome de perfil nao pode ser vazio.")
    if not _SAFE_NAME_RE.match(name):
        raise PresetError(
            f"Nome '{name}' contem caracteres invalidos. "
            "Use apenas letras, numeros, espaco, ponto, traco e underline."
        )
    if name.upper() in _WINDOWS_RESERVED:
        raise PresetError(f"Nome '{name}' e reservado pelo sistema operacional.")
    if ".." in name:
        raise PresetError(f"Nome '{name}' invalido.")


def backup_before_write(path: Path, keep: int = 10) -> None:
    """Copia o arquivo para `_backups/<stem>_bak<NNN>.json` antes de sobrescrever.

    Mantem no maximo `keep` backups; remove os mais antigos quando exceder.
    Nao faz nada se o arquivo nao existir.
    """
    path = Path(path)
    if not path.exists():
        return
    backup_dir = path.parent / "_backups"
    backup_dir.mkdir(exist_ok=True)
    stem = path.stem
    existing = sorted(backup_dir.glob(f"{stem}_bak*.json"))
    n = len(existing) + 1
    shutil.copy2(path, backup_dir / f"{stem}_bak{n:03d}.json")
    all_backups = sorted(backup_dir.glob(f"{stem}_bak*.json"))
    for old in all_backups[:-keep]:
        old.unlink(missing_ok=True)


def create_preset(name: str, dir_path: Path, template: Preset | None = None) -> Path:
    """Cria novo preset (vazio ou a partir de template). Retorna o caminho criado."""
    _validate_name(name)
    path = Path(dir_path) / f"{name}.json"
    if path.exists():
        raise PresetError(f"Perfil '{name}' ja existe nesta pasta.")
    new_preset = Preset(
        machine=name,
        schema_version=template.schema_version if template else SUPPORTED_SCHEMA,
        description=template.description if template else "",
        extensions=list(template.extensions) if template else [".nc", ".txt"],
        case_sensitive=template.case_sensitive if template else True,
        global_rules=list(template.global_rules) if template else [],
        file_rules=list(template.file_rules) if template else [],
        verifications=list(template.verifications) if template else [],
    )
    save_preset(new_preset, path)
    return path


def duplicate_preset(src_path: Path, new_name: str) -> Path:
    """Duplica preset existente com novo nome. Retorna o caminho da copia."""
    _validate_name(new_name)
    template = load_preset(src_path)
    return create_preset(new_name, Path(src_path).parent, template)


def rename_preset(src_path: Path, new_name: str) -> Path:
    """Renomeia preset: grava copia com novo nome, faz backup do original e remove-o."""
    _validate_name(new_name)
    src = Path(src_path)
    new_path = src.parent / f"{new_name}.json"
    if new_path.exists():
        raise PresetError(f"Perfil '{new_name}' ja existe nesta pasta.")
    preset = load_preset(src)
    new_preset = Preset(
        machine=new_name,
        schema_version=preset.schema_version,
        description=preset.description,
        extensions=list(preset.extensions),
        case_sensitive=preset.case_sensitive,
        global_rules=list(preset.global_rules),
        file_rules=list(preset.file_rules),
        verifications=list(preset.verifications),
    )
    backup_before_write(src)
    save_preset(new_preset, new_path)
    src.unlink()
    return new_path


def delete_preset(path: Path) -> None:
    """Remove preset apos criar backup de seguranca."""
    path = Path(path)
    if not path.exists():
        raise PresetError(f"Perfil '{path.name}' nao encontrado.")
    backup_before_write(path)
    path.unlink()
