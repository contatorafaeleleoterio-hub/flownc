"""Dataclasses tipadas do dominio (PRD v2.3, secao 12.3 -> models.py).

Identificadores em ingles para clareza de codigo; strings ao usuario sao PT-BR.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Scope(str, Enum):
    GLOBAL = "global"
    FILE = "file"


class Mode(str, Enum):
    AUTO = "auto"
    LITERAL = "literal"
    CNC_ADDRESS = "cnc_address"


class OnZeroMatches(str, Enum):
    WARN = "warn"
    IGNORE = "ignore"
    ERROR = "error"


class VerificationType(str, Enum):
    MUST_EXIST = "must_exist"
    MUST_NOT_EXIST = "must_not_exist"
    COUNT_MIN = "count_min"
    COUNT_MAX = "count_max"
    EXACT_COUNT = "exact_count"


class Severity(str, Enum):
    OK = "ok"            # verde
    WARNING = "warning"  # amarelo (nao bloqueia)
    CRITICAL = "critical"  # vermelho (bloqueia salvar)


@dataclass(frozen=True)
class Rule:
    """Regra de substituicao (PRD secao 7.2)."""

    id: str
    find: str
    replace: str
    scope: Scope = Scope.GLOBAL
    mode: Mode = Mode.AUTO
    active: bool = True
    file: str | None = None  # basename, obrigatorio quando scope=FILE
    comment: str = ""
    on_zero_matches: OnZeroMatches = OnZeroMatches.WARN
    priority: int = 100


@dataclass(frozen=True)
class Verification:
    """Verificacao configuravel (PRD secao 10.1)."""

    id: str
    type: VerificationType
    find: str
    mode: Mode = Mode.LITERAL  # secao 10.1: verificacao nao usa 'auto'
    label: str = ""
    count: int = 0  # usado por count_min / count_max / exact_count


@dataclass
class Preset:
    """Perfil de maquina (PRD secao 13.1)."""

    machine: str
    schema_version: int = 1
    description: str = ""
    extensions: list[str] = field(default_factory=lambda: [".nc", ".txt"])
    case_sensitive: bool = True
    global_rules: list[Rule] = field(default_factory=list)
    file_rules: list[Rule] = field(default_factory=list)
    verifications: list[Verification] = field(default_factory=list)


@dataclass(frozen=True)
class PlannedEdit:
    """Um intervalo do texto original que sera substituido (PRD secao 8.3)."""

    start: int
    end: int
    rule_id: str
    matched: str
    replacement: str


@dataclass(frozen=True)
class Suppression:
    """Match descartado por conflito (PRD secao 8.4)."""

    start: int
    end: int
    loser_rule_id: str
    winner_rule_id: str
    reason: str


@dataclass
class PlanResult:
    """Resultado do planejamento contra o conteudo original."""

    edits: list[PlannedEdit] = field(default_factory=list)
    suppressions: list[Suppression] = field(default_factory=list)
    match_count_by_rule: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class VerificationResult:
    """Resultado de uma verificacao (config. ou estrutural)."""

    label: str
    severity: Severity
    message: str


@dataclass
class EncodingInfo:
    """Metadados de leitura do arquivo (PRD secao 9.1)."""

    encoding: str
    has_bom: bool
    eol: str          # "\r\n", "\n" ou "\r"
    confidence: str   # "alta" | "media" | "baixa"


@dataclass(frozen=True)
class ScanResult:
    """Resultado da varredura de um codigo de origem por arquivo.

    `counts` mapeia cada arquivo -> numero de ocorrencias (com boundary CNC).
    Zero ocorrencias e sinal util (nao erro): arquivo entra com contagem 0.
    """

    find: str
    counts: dict[str, int] = field(default_factory=dict)

    @property
    def files_with_matches(self) -> list[str]:
        return [name for name, n in self.counts.items() if n > 0]

    @property
    def files_without_matches(self) -> list[str]:
        """Arquivos com 0 ocorrencias (insumo para o ambar/desmarcar na UI)."""
        return [name for name, n in self.counts.items() if n == 0]

    @property
    def total_files(self) -> int:
        return len(self.counts)

    @property
    def coverage_summary(self) -> str:
        """Agregado 'X de Y arquivos contem <codigo>'."""
        return f"{len(self.files_with_matches)} de {self.total_files} arquivos contem {self.find}"


@dataclass(frozen=True)
class Issue:
    """Problema detectado na validacao de um lote (validate_batch).

    Severidade WARNING (ambar) nao bloqueia; CRITICAL bloqueia. `rule_ids`
    referencia a(s) regra(s) envolvidas no problema.
    """

    severity: Severity
    message: str
    rule_ids: tuple[str, ...] = ()
