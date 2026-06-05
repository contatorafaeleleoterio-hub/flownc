"""Biblioteca reutilizavel de pares buscar/trocar (Sessao A).

Persistida em JSON atomico via `json_store`. Carrega silenciosamente quando
ausente (lista vazia). Rejeita entradas sem `find`; deduplicacao por
(find, replace) na escrita; ordenacao estavel por rotulo/find para facilitar
diff entre versoes.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .json_store import read_json, write_json_atomic


class LibraryError(Exception):
    """Erro de leitura/escrita da biblioteca."""


@dataclass(frozen=True)
class CodeEntry:
    find: str
    replace: str
    label: str = ""
    tags: list[str] = field(default_factory=list)


def load_library(path: Path) -> list[CodeEntry]:
    """Carrega biblioteca; retorna lista vazia se arquivo ausente."""
    if not Path(path).exists():
        return []
    try:
        data = read_json(path)
    except Exception as exc:
        raise LibraryError(f"Erro ao ler biblioteca: {exc}") from exc
    if not isinstance(data, list):
        raise LibraryError("Biblioteca invalida: esperado lista JSON na raiz")
    entries: list[CodeEntry] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        find = str(item.get("find", "")).strip()
        if not find:
            continue
        replace = str(item.get("replace", ""))
        label = str(item.get("label", ""))
        tags = [str(t) for t in item.get("tags", []) if isinstance(t, str)]
        entries.append(CodeEntry(find=find, replace=replace, label=label, tags=tags))
    return entries


def save_library(path: Path, entries: list[CodeEntry]) -> None:
    """Salva biblioteca com deduplicacao e ordenacao estaveis."""
    seen: set[tuple[str, str]] = set()
    deduped: list[CodeEntry] = []
    for e in entries:
        key = (e.find, e.replace)
        if key not in seen:
            seen.add(key)
            deduped.append(e)
    deduped.sort(key=lambda e: (e.label.lower(), e.find.lower()))
    data = [
        {"find": e.find, "replace": e.replace, "label": e.label, "tags": list(e.tags)}
        for e in deduped
    ]
    write_json_atomic(path, data)
