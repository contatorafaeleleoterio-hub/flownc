"""Publicacao segura com backup versionado (motor de batch, grupo 4).

Publica o resultado das edicoes diretamente na pasta de trabalho (a que a maquina
le) e preserva cada original movendo-o para um backup versionado por data/hora
(_backup_orig_DATA_HORA/) numa pasta de backup configuravel. Toca apenas os
arquivos que realmente mudaram.

Invariante: o original nunca se perde. Ordem a prova de falha:
  1. Backup do original (pasta versionada com data/hora)
  2. Conferencia SHA do backup vs. original
  3. Escrita atomica (.tmp na pasta de trabalho + os.replace)
  4. Conferencia SHA pos-publicacao
  5. Se falhar no meio, a pasta de trabalho permanece intacta (original ou nova, nunca vazia)

Reutiliza: _write_bytes_atomic, integrity_hash, verify_saved de existentes.
"""
from __future__ import annotations

import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

from .conference import integrity_hash
from .file_handler import _write_bytes_atomic


@dataclass(frozen=True)
class PublishItem:
    """Item a publicar: nome do arquivo + conteudo editado (bytes)."""

    name: str
    edited_bytes: bytes


@dataclass(frozen=True)
class PublishResult:
    """Resultado da publicacao em lote.

    Attributes:
        ok: True se todos os arquivos foram publicados com sucesso.
        published: dict[nome, True] para arquivos efetivamente gravados.
        backup_folder: caminho da pasta de backup versionada criada.
        mensagem: descricao legivel (sucesso ou motivo da falha).
        integridade_ok: True se todas as conferencias SHA passaram.
    """

    ok: bool
    published: dict[str, bool]
    backup_folder: Path | None = None
    mensagem: str = ""
    integridade_ok: bool = True


def publish_batch(
    working_dir: Path,
    backup_dir: Path,
    items: list[PublishItem],
    read_fn: Callable[[Path], bytes] | None = None,
) -> PublishResult:
    """Publica arquivos editados na pasta de trabalho com backup versionado.

    Args:
        working_dir: pasta de trabalho (onde os arquivos finais vao).
        backup_dir: pasta de backup (onde os originais sao preservados).
        items: lista de PublishItem (nome + conteudo editado).
        read_fn: funcao para ler bytes do disco (default: Path.read_bytes).
                 Injetavel para testes.

    Returns:
        PublishResult com status ok, arquivos publicados e pasta de backup.
    """

    def _default_read(p: Path) -> bytes:
        return p.read_bytes()

    if read_fn is None:
        read_fn = _default_read

    published: dict[str, bool] = {}
    backup_folder: Path | None = None
    errors: list[str] = []
    integridade_ok = True

    try:
        # Criar pasta de backup versionada (DATA_HORA)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_folder = backup_dir / f"_backup_orig_{timestamp}"
        backup_folder.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return PublishResult(
            ok=False,
            published={},
            backup_folder=None,
            mensagem=f"Nao foi possivel criar pasta de backup: {exc}",
            integridade_ok=False,
        )

    # Publicar cada arquivo
    for item in items:
        file_path = working_dir / item.name

        # Verificar se o arquivo existe na pasta de trabalho
        if not file_path.exists():
            errors.append(
                f"Arquivo nao existe na pasta de trabalho: {item.name}"
            )
            published[item.name] = False
            continue

        # Ler o arquivo original
        try:
            original_bytes = read_fn(file_path)
        except OSError as exc:
            errors.append(f"Nao foi possivel ler {item.name}: {exc}")
            published[item.name] = False
            continue

        # Conferir se o arquivo mudou
        if original_bytes == item.edited_bytes:
            published[item.name] = True
            continue

        # Fazer backup do original
        try:
            backup_path = backup_folder / item.name
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)
        except OSError as exc:
            errors.append(f"Nao foi possivel fazer backup de {item.name}: {exc}")
            published[item.name] = False
            continue

        # Conferir SHA do backup vs. original
        try:
            backup_bytes = read_fn(backup_path)
        except OSError as exc:
            errors.append(
                f"Nao foi possivel verificar backup de {item.name}: {exc}"
            )
            integridade_ok = False
            published[item.name] = False
            continue

        backup_hash = integrity_hash(backup_bytes)
        original_hash = integrity_hash(original_bytes)
        if backup_hash != original_hash:
            errors.append(
                f"DIVERGENCIA: SHA do backup de {item.name} "
                f"nao confere com o original"
            )
            integridade_ok = False
            published[item.name] = False
            continue

        # Escrita atomica (.tmp + os.replace)
        try:
            _write_bytes_atomic(file_path, item.edited_bytes)
        except OSError as exc:
            errors.append(f"Nao foi possivel publicar {item.name}: {exc}")
            published[item.name] = False
            continue

        # Conferir SHA pos-publicacao
        try:
            published_bytes = read_fn(file_path)
        except OSError as exc:
            errors.append(
                f"Arquivo publicado, mas nao foi possivel verificar {item.name}: {exc}"
            )
            integridade_ok = False
            published[item.name] = False
            continue

        published_hash = integrity_hash(published_bytes)
        edited_hash = integrity_hash(item.edited_bytes)
        if published_hash != edited_hash:
            errors.append(
                f"DIVERGENCIA: SHA do arquivo publicado {item.name} "
                f"nao confere com o editado em memoria"
            )
            integridade_ok = False
            published[item.name] = False
            continue

        published[item.name] = True

    # Compilar resultado
    ok = all(published.values())
    if errors:
        mensagem = "Erros durante a publicacao:\n" + "\n".join(errors)
    else:
        published_count = sum(1 for v in published.values() if v)
        mensagem = f"Publicacao concluida: {published_count}/{len(items)} arquivos"

    return PublishResult(
        ok=ok,
        published=published,
        backup_folder=backup_folder,
        mensagem=mensagem,
        integridade_ok=integridade_ok,
    )
