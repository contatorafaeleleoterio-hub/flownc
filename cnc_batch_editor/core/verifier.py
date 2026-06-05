"""Verificacoes configuraveis e estruturais (PRD secao 10). Funcoes puras.

Rodam sobre o RESULTADO pos-substituicao (secao 10.1). As estruturais sao
obrigatorias e nao desativaveis (secao 10.2).
"""
from __future__ import annotations

from .matcher import compile_rule
from .models import (
    Mode,
    Severity,
    Verification,
    VerificationResult,
    VerificationType,
)

# Comandos cuja remocao de linha gera alerta de atencao (PRD secao 10.2).
_CRITICAL_TOKENS = ("M30", "M02", "M06", "G43", "G44")


def _count(text: str, find: str, mode: Mode, case_sensitive: bool) -> int:
    return len(compile_rule(find, mode, case_sensitive).findall(text))


def _addr(text: str, token: str) -> int:
    """Conta um endereco CNC por match real (H0.2): 'M30' NAO casa 'M300'/'M30.5'."""
    return _count(text, token, Mode.CNC_ADDRESS, case_sensitive=True)


def run_configurable(
    result_text: str, verifications: list[Verification], case_sensitive: bool = True
) -> list[VerificationResult]:
    out: list[VerificationResult] = []
    for v in verifications:
        n = _count(result_text, v.find, v.mode, case_sensitive)
        label = v.label or v.find
        if v.type is VerificationType.MUST_EXIST and n == 0:
            out.append(VerificationResult(label, Severity.WARNING, f"'{v.find}' ausente"))
        elif v.type is VerificationType.MUST_NOT_EXIST and n > 0:
            out.append(VerificationResult(label, Severity.WARNING, f"'{v.find}' presente ({n}x)"))
        elif v.type is VerificationType.COUNT_MIN and n < v.count:
            out.append(VerificationResult(label, Severity.WARNING, f"'{v.find}' {n}x < min {v.count}"))
        elif v.type is VerificationType.COUNT_MAX and n > v.count:
            out.append(VerificationResult(label, Severity.WARNING, f"'{v.find}' {n}x > max {v.count}"))
        elif v.type is VerificationType.EXACT_COUNT and n != v.count:
            out.append(VerificationResult(label, Severity.WARNING, f"'{v.find}' {n}x != {v.count}"))
    return out


def run_structural(original: str, result: str) -> list[VerificationResult]:
    """Verificacoes estruturais obrigatorias (PRD secao 10.2)."""
    out: list[VerificationResult] = []

    if result.strip() == "":
        out.append(VerificationResult("Resultado nao vazio", Severity.CRITICAL,
                                      "Arquivo resultante ficou vazio"))
        return out  # vazio: demais checagens nao se aplicam

    if original.lstrip().startswith("%") and not result.lstrip().startswith("%"):
        out.append(VerificationResult("% inicial", Severity.CRITICAL,
                                      "Perdeu o '%' do inicio do programa"))
    if original.rstrip().endswith("%") and not result.rstrip().endswith("%"):
        out.append(VerificationResult("% final", Severity.CRITICAL,
                                      "Perdeu o '%' do fim do programa"))

    # Fim de programa por TOKEN CNC, nao substring (H0.2): 'M30' NAO casa 'M300'.
    orig_end = _addr(original, "M30") or _addr(original, "M02")
    res_end = _addr(result, "M30") or _addr(result, "M02")
    if orig_end and not res_end:
        out.append(VerificationResult("Fim de programa", Severity.CRITICAL,
                                      "Perdeu M30/M02 (fim de programa)"))

    # Atencao: comando critico removido (contagem caiu). Nao bloqueia (secao 10.2).
    for token in _CRITICAL_TOKENS:
        if _addr(result, token) < _addr(original, token):
            out.append(VerificationResult(f"Comando {token}", Severity.WARNING,
                                          f"Ocorrencias de {token} reduzidas"))
    return out


def is_blocking(results: list[VerificationResult]) -> bool:
    return any(r.severity is Severity.CRITICAL for r in results)
