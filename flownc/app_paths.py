"""Resolucao de caminhos compativel com execucao normal e com EXE empacotado.

Em EXE (PyInstaller onedir), os presets ficam na pasta `data/presets` AO LADO do
executavel, para o operador poder editar/adicionar JSONs direto no pen drive.
"""
from __future__ import annotations

import sys
from pathlib import Path


def base_dir() -> Path:
    if getattr(sys, "frozen", False):  # rodando como EXE
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent


def presets_dir() -> Path:
    return base_dir() / "data" / "presets"


def library_path() -> Path:
    return base_dir() / "data" / "library.json"


def settings_path() -> Path:
    return base_dir() / "data" / "settings.json"


def fonts_dir() -> Path:
    return base_dir() / "assets" / "fonts"


def qss_path() -> Path:
    return base_dir() / "ui" / "style.qss"
