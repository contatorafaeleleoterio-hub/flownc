"""Conferencia pos-salvamento (Sessao D — PRD secao 14 criterio 19).

Verifica integridade dos arquivos gravados comparando SHA-256 do conteudo em
memoria (pre-escrita) com o arquivo relido do disco. Uma divergencia de hash
indica problema na escrita (disco cheio, interrupcao, corrupção) e e relatada
como falha critica no log de sessao.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class IntegrityResult:
    """Resultado da verificacao de integridade de um arquivo gravado."""

    filename: str
    expected_hash: str
    actual_hash: str
    ok: bool
    error: str = ""

    def summary(self) -> str:
        if self.error:
            return f"{self.filename}: FALHA DE LEITURA — {self.error}"
        if self.ok:
            return f"{self.filename}: OK (SHA-256 conferido)"
        return (
            f"{self.filename}: DIVERGENCIA DE HASH\n"
            f"  esperado: {self.expected_hash[:16]}...\n"
            f"  gravado:  {self.actual_hash[:16]}..."
        )


def integrity_hash(data: bytes) -> str:
    """SHA-256 (hex) dos bytes do arquivo."""
    return hashlib.sha256(data).hexdigest()


def verify_saved(
    out_dir: Path,
    encoded: list[tuple[str, bytes]],
) -> list[IntegrityResult]:
    """Rele cada arquivo gravado e compara SHA-256 com o esperado.

    Args:
        out_dir: pasta onde os arquivos foram gravados.
        encoded: lista de (nome, bytes) que foi passada para ``write_encoded_batch``.

    Returns:
        Lista de :class:`IntegrityResult`, um por arquivo.
    """
    results: list[IntegrityResult] = []
    for name, expected_bytes in encoded:
        exp_hash = integrity_hash(expected_bytes)
        path = out_dir / name
        try:
            actual_bytes = path.read_bytes()
            act_hash = integrity_hash(actual_bytes)
            results.append(IntegrityResult(
                filename=name,
                expected_hash=exp_hash,
                actual_hash=act_hash,
                ok=(exp_hash == act_hash),
            ))
        except OSError as exc:
            results.append(IntegrityResult(
                filename=name,
                expected_hash=exp_hash,
                actual_hash="",
                ok=False,
                error=str(exc),
            ))
    return results


def format_integrity_report(results: list[IntegrityResult]) -> str:
    """Formata o relatorio de integridade como texto para o log de sessao."""
    lines = ["=== CONFERENCIA POS-SALVAMENTO ==="]
    ok_count = sum(1 for r in results if r.ok)
    fail_count = len(results) - ok_count
    lines.append(f"Arquivos: {len(results)}  OK: {ok_count}  Falhas: {fail_count}")
    lines.append("")
    for r in results:
        lines.append(r.summary())
    if fail_count:
        lines.append("")
        lines.append("ATENCAO: Ha divergencias. Pasta de saida mantida para auditoria.")
    return "\n".join(lines)
