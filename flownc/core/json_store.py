"""Escrita/leitura atomica de JSON de configuracao (Stage 0, H0.5).

Espelha o padrao ja provado em `core/file_handler.write_atomic`: grava num
arquivo temporario, faz flush + fsync e troca por `os.replace` (atomico no
mesmo volume). Queda de energia no meio NUNCA corrompe o destino: sobra o
conteudo antigo OU o novo, nunca um arquivo parcial.

Reutilizavel por preset_store, library_store (Sessao A) e settings_store
(Sessao C).
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def write_json_atomic(path: Path, data: Any, *, indent: int = 2) -> None:
    """Grava `data` como JSON UTF-8 de forma atomica.

    A serializacao acontece ANTES de abrir o temporario: se `data` nao for
    serializavel, levanta antes de criar qualquer arquivo, deixando o destino
    intacto. Em erro de escrita, remove o temporario e propaga a excecao.
    """
    path = Path(path)
    payload = json.dumps(data, ensure_ascii=False, indent=indent).encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    try:
        with open(tmp, "wb") as fh:
            fh.write(payload)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except Exception:
        if tmp.exists():
            tmp.unlink(missing_ok=True)
        raise


def read_json(path: Path) -> Any:
    """Le e desserializa um JSON UTF-8.

    Erros de leitura/parse sobem como `OSError`/`json.JSONDecodeError` para o
    chamador encapsular na sua propria excecao de dominio (ex.: `PresetError`).
    """
    return json.loads(Path(path).read_text(encoding="utf-8"))
