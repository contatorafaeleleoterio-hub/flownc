"""Log de sessao em memoria, exportavel como .txt (PRD secao 11.6)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class SessionLog:
    lines: list[str] = field(default_factory=list)

    def add(self, message: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        self.lines.append(f"[{ts}] {message}")

    def export_txt(self, path: Path) -> None:
        Path(path).write_text("\n".join(self.lines) + "\n", encoding="utf-8")

    def text(self) -> str:
        return "\n".join(self.lines)
