"""Configuracoes persistentes do aplicativo (Sessao C).

Schema v2:
  output_mode: "ao_lado" | "fixa"
  output_dir:  caminho absoluto (usado so quando output_mode == "fixa")
  working_dir: pasta onde as mudancas sao gravadas (default: cwd ao carregar)
  backup_dir:  pasta onde backups sao armazenados (default: ~/FlowNC_backups)

Carrega com fallback seguro para defaults quando ausente ou malformado (v1 compativel).
Grava de forma atomica via json_store, sempre em v2.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .json_store import read_json, write_json_atomic

SUPPORTED_SCHEMA = 2
OUTPUT_MODES = ("ao_lado", "fixa")


class SettingsError(Exception):
    """Falha ao ler ou gravar configuracoes."""


@dataclass
class AppSettings:
    schema_version: int = SUPPORTED_SCHEMA
    output_mode: str = "ao_lado"
    output_dir: str = ""
    working_dir: str = ""
    backup_dir: str = ""


def _defaults() -> AppSettings:
    return AppSettings()


def load_settings(path: Path) -> AppSettings:
    """Carrega configuracoes; retorna defaults em qualquer falha (nunca levanta).

    Compativel com schema v1 (carrega sem erro, adiciona defaults para v2).
    """
    try:
        data = read_json(Path(path))
    except (OSError, json.JSONDecodeError):
        return _defaults()
    if not isinstance(data, dict):
        return _defaults()
    mode = data.get("output_mode", "ao_lado")
    if mode not in OUTPUT_MODES:
        mode = "ao_lado"
    return AppSettings(
        schema_version=SUPPORTED_SCHEMA,
        output_mode=mode,
        output_dir=str(data.get("output_dir", "")),
        working_dir=str(data.get("working_dir", "")),
        backup_dir=str(data.get("backup_dir", "")),
    )


def save_settings(path: Path, settings: AppSettings) -> None:
    """Grava configuracoes de forma atomica (sempre em schema v2)."""
    if settings.output_mode not in OUTPUT_MODES:
        raise SettingsError(
            f"output_mode invalido: '{settings.output_mode}'. "
            f"Validos: {OUTPUT_MODES}"
        )
    data = {
        "schema_version": SUPPORTED_SCHEMA,
        "output_mode": settings.output_mode,
        "output_dir": settings.output_dir,
        "working_dir": settings.working_dir,
        "backup_dir": settings.backup_dir,
    }
    try:
        write_json_atomic(Path(path), data)
    except OSError as exc:
        raise SettingsError(f"Falha ao gravar configuracoes: {exc}") from exc
