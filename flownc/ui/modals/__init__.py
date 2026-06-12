"""Modais do v4 (QDialog): Conferência (números reais) e Publicação (progresso).

Cada modal é um `QDialog` independente. A `LoteScreen` abre a Conferência pelo
CTA "Conferir lote →"; a Conferência encadeia a Publicação ao confirmar.
"""
from __future__ import annotations

from ui.modals.conferencia_modal import ConferenciaModal
from ui.modals.publicacao_modal import PublicacaoModal

__all__ = ["ConferenciaModal", "PublicacaoModal"]
