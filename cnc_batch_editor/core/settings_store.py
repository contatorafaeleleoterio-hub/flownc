"""Configuracoes persistentes do aplicativo (Sessao C).

Schema v1:
  output_mode: "ao_lado" | "fixa"
  output_dir:  caminho absoluto (usado so quando output_mode == "fixa")

Carrega com fallback seguro para defaults quando ausente ou malformado.
Grava de forma atomica via json_store.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .json_store import read_json, write_json_atomic

SUPPORTED_SCHEMA = 1
OUTPUT_MODES = ("ao_lado", "fixa")


class SettingsError(Exception):
    """Falha ao ler ou gravar configuracoes."""


@dataclass
class AppSettings:
    schema_version: int = SUPPORTED_SCHEMA
    output_mode: str = "ao_lado"
    output_dir: str = ""


def _defaults() -> AppSettings:
    return AppSettings()


def load_settings(path: Path) -> AppSettings:
    """Carrega configuracoes; retorna defaults em qualquer falha (nunca levanta)."""
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
        schema_version=int(data.get("schema_version", SUPPORTED_SCHEMA)),
        output_mode=mode,
        output_dir=str(data.get("output_dir", "")),
    )


def save_settings(path: Path, settings: AppSettings) -> None:
    """Grava configuracoes de forma atomica."""
    if settings.output_mode not in OUTPUT_MODES:
        raise SettingsError(
            f"output_mode invalido: '{settings.output_mode}'. "
            f"Validos: {OUTPUT_MODES}"
        )
    data = {
        "schema_version": settings.schema_version,
        "output_mode": settings.output_mode,
        "output_dir": settings.output_dir,
    }
    try:
        write_json_atomic(Path(path), data)
    except OSError as exc:
        raise SettingsError(f"Falha ao gravar configuracoes: {exc}") from exc
