"""Componentes isolados da UI do FlowNC (redesign-layout-principal).

Cada componente e um QWidget independente, importavel e instanciavel sem
depender dos demais. MainWindow age como maestro: instancia, conecta sinais
e mantem o estado.
"""
from __future__ import annotations

from ui.components.compositor import CompositorPanel
from ui.components.header import HeaderBar
from ui.components.program_list import ProgramListPanel
from ui.components.summary import SummaryPanel

__all__ = ["HeaderBar", "CompositorPanel", "ProgramListPanel", "SummaryPanel"]
