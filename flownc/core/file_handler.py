"""Leitura/escrita binaria com preservacao de encoding, BOM e EOL (PRD secao 9).

Round-trip fiel: o que entra deve sair byte-a-byte quando nada muda
(vetores TV-RT-*). Nunca sobrescreve o original; escrita atomica.
"""
from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from .models import EncodingInfo

_BOM_UTF8 = b"\xef\xbb\xbf"
_BOM_UTF16_LE = b"\xff\xfe"
_BOM_UTF16_BE = b"\xfe\xff"


class BinaryFileError(Exception):
    """Arquivo nao textual (rejeitado, PRD secao 9.1)."""


class BatchEncodeError(Exception):
    """Algum arquivo do lote nao pode ser codificado (preflight H0.3 falhou)."""


def detect_eol(text: str) -> str:
    crlf = text.count("\r\n")
    lf = text.count("\n") - crlf
    cr = text.count("\r") - crlf
    if crlf >= lf and crlf >= cr and crlf > 0:
        return "\r\n"
    if cr > lf and cr > 0:
        return "\r"
    return "\n"


def read_file(path: Path) -> tuple[str, EncodingInfo]:
    """Le e decodifica preservando metadados (PRD secao 9.1)."""
    raw = path.read_bytes()
    if not raw:
        return "", EncodingInfo("utf-8", False, "\n", "alta")

    if raw.startswith(_BOM_UTF8):
        text = raw[len(_BOM_UTF8):].decode("utf-8")
        return text, EncodingInfo("utf-8-sig", True, detect_eol(text), "alta")
    if raw.startswith(_BOM_UTF16_LE):
        text = raw[len(_BOM_UTF16_LE):].decode("utf-16-le")
        return text, EncodingInfo("utf-16-le", True, detect_eol(text), "alta")
    if raw.startswith(_BOM_UTF16_BE):
        text = raw[len(_BOM_UTF16_BE):].decode("utf-16-be")
        return text, EncodingInfo("utf-16-be", True, detect_eol(text), "alta")

    # Sem BOM: bytes nulos indicam binario ou utf-16 sem BOM (rejeitado).
    if b"\x00" in raw:
        raise BinaryFileError(f"{path.name}: arquivo nao textual (bytes nulos)")

    for encoding, confidence in (("utf-8", "alta"), ("cp1252", "media")):
        try:
            text = raw.decode(encoding)
            return text, EncodingInfo(encoding, False, detect_eol(text), confidence)
        except UnicodeDecodeError:
            continue
    # latin-1 nunca falha (PRD secao 9.1, passo 4).
    text = raw.decode("latin-1")
    return text, EncodingInfo("latin-1", False, detect_eol(text), "baixa")


def encode_text(text: str, info: EncodingInfo) -> bytes:
    """Reconstroi os bytes na codificacao detectada, reaplicando BOM."""
    if info.encoding == "utf-8-sig":
        return _BOM_UTF8 + text.encode("utf-8")
    if info.encoding == "utf-16-le":
        return (_BOM_UTF16_LE if info.has_bom else b"") + text.encode("utf-16-le")
    if info.encoding == "utf-16-be":
        return (_BOM_UTF16_BE if info.has_bom else b"") + text.encode("utf-16-be")
    return text.encode(info.encoding)


def _write_bytes_atomic(out_path: Path, data: bytes) -> None:
    """Grava bytes via arquivo temporario + os.replace (PRD secao 9.2)."""
    tmp = out_path.with_name(out_path.name + ".tmp")
    try:
        with open(tmp, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, out_path)
    except Exception:
        if tmp.exists():
            tmp.unlink(missing_ok=True)
        raise


def write_atomic(out_path: Path, text: str, info: EncodingInfo) -> None:
    """Grava texto na codificacao detectada, de forma atomica (PRD secao 9.2)."""
    _write_bytes_atomic(out_path, encode_text(text, info))


def encode_batch(items: list[tuple[str, str, EncodingInfo]]) -> list[tuple[str, bytes]]:
    """Preflight de encodabilidade do lote (H0.3): (nome, texto, info) -> (nome, bytes).

    Codifica TODOS os textos em bytes ANTES de qualquer escrita. Se algum nao
    puder ser codificado na sua codificacao (ex.: caractere novo digitado numa
    troca, fora do cp1252), levanta `BatchEncodeError` citando o arquivo — sem
    tocar no disco — para o chamador abortar o lote inteiro (nada parcial).
    """
    encoded: list[tuple[str, bytes]] = []
    for name, text, info in items:
        try:
            encoded.append((name, encode_text(text, info)))
        except (UnicodeEncodeError, LookupError) as exc:
            raise BatchEncodeError(
                f"{name}: nao foi possivel codificar em '{info.encoding}' ({exc}). "
                f"Lote abortado — nenhum arquivo foi gravado."
            ) from exc
    return encoded


def write_encoded_batch(out_dir: Path, encoded: list[tuple[str, bytes]]) -> None:
    """Grava um lote ja codificado por `encode_batch`, cada arquivo atomico."""
    for name, data in encoded:
        _write_bytes_atomic(out_dir / name, data)


def make_output_dir(source_dir: Path, profile: str, base_dir: Path | None = None) -> Path:
    """Cria pasta de saida com perfil+timestamp e sufixo de colisao (secao 9.2).

    `base_dir` sobrescreve a raiz de destino (Sessao C: pasta fixa).
    Quando None, usa `source_dir` (comportamento legado).
    """
    root = Path(base_dir) if base_dir is not None else source_dir
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = root / f"_processado_{profile}_{ts}"
    candidate = base
    n = 2
    while candidate.exists():
        candidate = root / f"{base.name}_{n:02d}"
        n += 1
    candidate.mkdir(parents=True)
    return candidate


# Curingas que, presentes nas extensoes do perfil, fazem aceitar QUALQUER arquivo.
_WILDCARDS = {"*", "*.*", ".*"}


def list_input_files(source_dir: Path, extensions: list[str]) -> list[Path]:
    """Lista arquivos elegiveis, ignorando saidas anteriores (secao 9.3).

    Pula tudo (pasta ou arquivo) cujo nome comece com '_processado_', para nao
    reprocessar resultados nem o log de execucoes anteriores.

    Aceita um arquivo quando:
      - o perfil tem curinga ('*', '*.*' ou '.*') -> aceita QUALQUER arquivo; ou
      - a extensao do arquivo esta na lista do perfil; ou
      - o arquivo NAO tem extensao (programas Fanuc tipo 'O2169', comuns no chao
        de fabrica) -> sempre incluido.

    Arquivos binarios (imagens, etc.) nao sao filtrados aqui pela extensao, mas
    sao rejeitados depois por `read_file` (BinaryFileError) e marcados em vermelho.
    """
    exts = {e.lower() for e in extensions}
    accept_any = bool(exts & _WILDCARDS)
    out: list[Path] = []
    for p in sorted(source_dir.iterdir()):
        if p.name.startswith("_processado_"):
            continue
        if p.is_dir():
            continue
        if accept_any or p.suffix == "" or p.suffix.lower() in exts:
            out.append(p)
    return out
