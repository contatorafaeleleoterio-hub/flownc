"""Semente de fabrica — garante que data/ existe e esta valida ao lado do .exe.

Chame `ensure_seed()` no boot, antes de _load_library / _load_presets.
Nunca apaga dado do operador sem preservar — arquivos corrompidos ganham
sufixo .corrompido antes de serem substituidos.
"""
from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path

import app_paths

log = logging.getLogger(__name__)


def _is_valid_json(path: Path) -> bool:
    try:
        with path.open(encoding="utf-8") as f:
            json.load(f)
        return True
    except Exception:
        return False


def _copy_default(src: Path, dst: Path) -> None:
    """Copia src -> dst, criando pastas intermediarias."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    log.info("seed: copiado %s -> %s", src.name, dst)


def _safe_replace(src: Path, dst: Path) -> None:
    """Substitui dst por src preservando o arquivo corrompido com sufixo."""
    if dst.exists():
        corrupted = dst.with_suffix(dst.suffix + ".corrompido")
        dst.rename(corrupted)
        log.warning("seed: arquivo corrompido preservado em %s", corrupted)
    _copy_default(src, dst)


def ensure_seed() -> None:
    """Repoe data_default/ em data/ se ausente, vazio ou corrompido.

    Idempotente: se data/ ja tiver conteudo valido, nao toca em nada.
    """
    src_root = app_paths.data_default_dir()

    if not src_root.exists():
        log.warning("seed: data_default/ nao encontrado em %s — sem semente", src_root)
        return

    try:
        # --- biblioteca ---
        src_lib = src_root / "library.json"
        dst_lib = app_paths.library_path()

        if src_lib.exists():
            if not dst_lib.exists() or dst_lib.stat().st_size == 0:
                _copy_default(src_lib, dst_lib)
            elif not _is_valid_json(dst_lib):
                _safe_replace(src_lib, dst_lib)

        # --- presets ---
        src_presets = src_root / "presets"
        dst_presets = app_paths.presets_dir()

        if src_presets.exists():
            dst_presets.mkdir(parents=True, exist_ok=True)
            for src_preset in src_presets.glob("*.json"):
                dst_preset = dst_presets / src_preset.name
                if not dst_preset.exists() or dst_preset.stat().st_size == 0:
                    _copy_default(src_preset, dst_preset)
                elif not _is_valid_json(dst_preset):
                    _safe_replace(src_preset, dst_preset)

    except Exception as exc:
        log.error("seed: falha ao semear — %s (continuando sem dados)", exc)
