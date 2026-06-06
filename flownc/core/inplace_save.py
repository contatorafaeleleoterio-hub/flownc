"""Gravacao in-place segura para o editor por arquivo (mudanca editor-integrado).

Diferente do Lote (que grava em pasta separada e mantem o invariante "o
original nunca e sobrescrito"), o editor e o atalho de ajuste manual rapido e
SOBRESCREVE o arquivo original, SEM criar backup (decisao de produto). Para que
isso seja seguro, a ausencia de backup e compensada por tres garantias:

1. Preflight de codificacao: se o texto editado nao puder ser codificado na
   codificacao do arquivo (ex.: caractere novo fora do cp1252), aborta ANTES de
   tocar o disco — original intacto, nenhum `.tmp` orfao.
2. Escrita atomica: `.tmp` no mesmo diretorio + `os.replace` (reusa
   `_write_bytes_atomic`), de modo que a pasta de origem nunca fica sem o arquivo.
3. Conferencia pos-escrita: rele os bytes gravados e compara o SHA-256 com o dos
   bytes esperados (reusa `integrity_hash`); qualquer divergencia vira falha.

A funcao e pura/testavel com `tmp_path` (sem Qt). A UI (ui/editor_panel.py)
apenas delega e exibe o resultado.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .conference import integrity_hash
from .file_handler import _write_bytes_atomic, encode_text
from .models import EncodingInfo


@dataclass(frozen=True)
class ResultadoGravacao:
    """Resultado de uma gravacao in-place, sem excecao silenciosa.

    Attributes:
        ok: True somente se a escrita ocorreu E a conferencia SHA-256 bateu.
        mensagem: descricao legivel (sucesso ou motivo da falha).
        sha_conferido: True se a conferencia pos-escrita foi executada e bateu.
    """

    ok: bool
    mensagem: str
    sha_conferido: bool


def salvar_no_lugar(path: Path, text: str, info: EncodingInfo) -> ResultadoGravacao:
    """Sobrescreve o arquivo original no lugar, sem backup, de forma segura.

    Ordem: (1) preflight de codificacao; (2) escrita atomica; (3) conferencia
    SHA-256 pos-escrita. Preserva encoding/BOM/EOL via ``info``.
    """
    # (1) Preflight: codifica ANTES de tocar o disco. Se falhar, original intacto.
    try:
        expected = encode_text(text, info)
    except (UnicodeEncodeError, LookupError) as exc:
        return ResultadoGravacao(
            ok=False,
            mensagem=(
                f"Nao foi possivel codificar em '{info.encoding}' ({exc}). "
                f"O arquivo original NAO foi alterado."
            ),
            sha_conferido=False,
        )

    # (2) Escrita atomica (tmp no mesmo diretorio + os.replace; limpa tmp em falha).
    try:
        _write_bytes_atomic(path, expected)
    except OSError as exc:
        return ResultadoGravacao(
            ok=False,
            mensagem=f"Falha ao gravar o arquivo: {exc}",
            sha_conferido=False,
        )

    # (3) Conferencia pos-escrita: rele os bytes e compara o SHA-256.
    try:
        actual = path.read_bytes()
    except OSError as exc:
        return ResultadoGravacao(
            ok=False,
            mensagem=f"Arquivo gravado, mas nao foi possivel reler para conferir: {exc}",
            sha_conferido=False,
        )

    if integrity_hash(actual) != integrity_hash(expected):
        return ResultadoGravacao(
            ok=False,
            mensagem=(
                "DIVERGENCIA DE HASH apos a gravacao — o conteudo no disco nao "
                "confere com o editado. Verifique o arquivo."
            ),
            sha_conferido=False,
        )

    return ResultadoGravacao(
        ok=True,
        mensagem="Salvo no lugar (SHA-256 conferido).",
        sha_conferido=True,
    )
