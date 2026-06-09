"""Resolucao de caminhos compativel com execucao normal e com EXE empacotado.

Dois "baldes" de caminho:
  - resource_dir(): recursos FIXOS de fabrica (style.qss, fontes, data_default).
    No EXE usa sys._MEIPASS (_internal/); em dev usa a pasta do projeto.
  - base_dir(): dados EDITAVEIS (presets, library, settings) ficam AO LADO do
    executavel para o operador editar/adicionar JSONs direto no pen drive.
"""
from __future__ import annotations

import sys
from pathlib import Path


def resource_dir() -> Path:
    """Recursos fixos empacotados (leitura apenas)."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parent


def base_dir() -> Path:
    """Base dos dados editaveis (ao lado do .exe ou raiz do projeto em dev)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent


def presets_dir() -> Path:
    return base_dir() / "data" / "presets"


def library_path() -> Path:
    return base_dir() / "data" / "library.json"


def settings_path() -> Path:
    return base_dir() / "data" / "settings.json"


def fonts_dir() -> Path:
    return resource_dir() / "assets" / "fonts"


def qss_path() -> Path:
    return resource_dir() / "ui" / "style.qss"


def data_default_dir() -> Path:
    return resource_dir() / "data_default"
