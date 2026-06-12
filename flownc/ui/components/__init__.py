"""Componentes compartilhados da UI do FlowNC (mockup v4).

Cada componente é um QWidget independente, importável e instanciável sem depender
dos demais. O maestro (`main_window`) instancia, conecta os sinais e mantém o estado.
"""
from __future__ import annotations

from ui.components.rail import RailWidget
from ui.components.top_bar import TopBar

__all__ = ["RailWidget", "TopBar"]
