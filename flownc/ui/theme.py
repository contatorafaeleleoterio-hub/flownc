"""Tokens de design do FlowNC — extraídos de mockups/painel-final.v4.html.

Paleta "Precisão Laranja" do v4: laranja #E85D04 como ação principal (CTA),
fundo cinza-azulado claro, topo/rail em azul-ardósia escuro.

Constantes Python para uso no QSS (via ``render_qss``) e em código de UI.
Importável sem instanciar QApplication.
"""
from __future__ import annotations

import string

# ---------------------------------------------------------------------------
# Espaçamentos (px)
# ---------------------------------------------------------------------------
SP_2 = 2
SP_4 = 4
SP_8 = 8
SP_12 = 12
SP_16 = 16
SP_24 = 24
SP_32 = 32
SP_40 = 40
SP_48 = 48

# ---------------------------------------------------------------------------
# Fontes (family stacks — para uso em QSS font-family)
# ---------------------------------------------------------------------------
FONT_SANS = '"IBM Plex Sans", system-ui, "Segoe UI", Roboto, sans-serif'
FONT_MONO = '"IBM Plex Mono", "Consolas", ui-monospace, monospace'

# Família curta (para QFont)
FONT_SANS_FAMILY = "IBM Plex Sans"
FONT_MONO_FAMILY = "IBM Plex Mono"
FONT_SANS_FALLBACK = "Segoe UI"
FONT_MONO_FALLBACK = "Consolas"

# ---------------------------------------------------------------------------
# Tipografia — (peso, tamanho px, line-height)
# ---------------------------------------------------------------------------
T_LABEL_WEIGHT = 700
T_LABEL_SIZE = 10
T_LABEL_LH = 1.4

T_CAPTION_WEIGHT = 600
T_CAPTION_SIZE = 12
T_CAPTION_LH = 1.4

T_UI_WEIGHT = 600
T_UI_SIZE = 13
T_UI_LH = 1.0

T_BODY_WEIGHT = 400
T_BODY_SIZE = 14
T_BODY_LH = 1.5

T_BODY_STRONG_WEIGHT = 600
T_BODY_STRONG_SIZE = 14
T_BODY_STRONG_LH = 1.5

T_HEADING_WEIGHT = 700
T_HEADING_SIZE = 15
T_HEADING_LH = 1.2

T_DISPLAY_WEIGHT = 600
T_DISPLAY_SIZE = 16
T_DISPLAY_LH = 1.0

T_MONO_SM_WEIGHT = 600
T_MONO_SM_SIZE = 12
T_MONO_SM_LH = 1.4

T_MONO_MD_WEIGHT = 600
T_MONO_MD_SIZE = 14
T_MONO_MD_LH = 1.0

T_MONO_LG_WEIGHT = 600
T_MONO_LG_SIZE = 16
T_MONO_LG_LH = 1.0

T_MONO_DISPLAY_WEIGHT = 700
T_MONO_DISPLAY_SIZE = 24
T_MONO_DISPLAY_LH = 1.0

# Editor (corpo mono)
ED_FONT_SIZE = 13
ED_LINE_HEIGHT = 21

# ---------------------------------------------------------------------------
# Cores — paleta v4 (:root de painel-final.v4.html)
# ---------------------------------------------------------------------------

# Fundos
COLOR_BG_BASE = "#FFFFFF"
COLOR_BG_SUBTLE = "#FFFFFF"
COLOR_BG_RAIL = "#DDE3EE"
COLOR_BG_SURFACE = "#F7F9FC"
COLOR_WHITE = "#FFFFFF"
COLOR_PANEL_LEFT = "#EDF0F5"
COLOR_PANEL_RIGHT = "#E5EAF2"

# Textos
COLOR_TEXT_PRIMARY = "#1A2533"
COLOR_TEXT_SECONDARY = "#4E6278"
COLOR_TEXT_TERTIARY = "#8FA5C2"

# Bordas
COLOR_BORDER = "#CCD4E0"
COLOR_BORDER_STRONG = "#B8C6D6"

# Interativo (azul-ardósia)
COLOR_INTERACTIVE = "#2B3A4A"
COLOR_INTERACTIVE_HV = "#1F2C39"
COLOR_INTERACTIVE_BG = "#E5EAF2"
COLOR_SLATE_2 = "#3A4F63"

# Botão "ghost" (ações leves do cabeçalho de seção)
COLOR_GHOST_HOVER = "#CDD5E2"

# Semânticas
COLOR_SUCCESS = "#2D6B2D"
COLOR_SUCCESS_BG = "#EAF5EA"
COLOR_SUCCESS_BORDER = "#8FC98F"
COLOR_WARNING = "#A16207"
COLOR_WARNING_BG = "#FFF8E1"
COLOR_WARNING_BORDER = "#D4A840"
COLOR_DANGER = "#D93025"
COLOR_DANGER_BG = "#FEECEB"
COLOR_DANGER_BORDER = "#F0948D"

# CTA / Acento laranja "Precisão Laranja" (ação principal)
COLOR_CTA = "#E85D04"
COLOR_CTA_START = "#E85D04"
COLOR_CTA_END = "#E85D04"
COLOR_CTA_TEXT = "#FFFFFF"
COLOR_CTA_TEXT_SOFT = "#FFE3D1"
COLOR_ACCENT = "#E85D04"
COLOR_ACCENT_HV = "#C94E00"
COLOR_ACCENT_ACTIVE = "#A83E00"
COLOR_ACCENT_BG = "#FFF3ED"
COLOR_ACCENT_BORDER = "#F0A87A"

# Desabilitado
COLOR_BTN_DISABLED_BG = "#EEF1F5"
COLOR_BTN_DISABLED_TEXT = "#B0BFD0"
COLOR_DISABLED_BG = "#EEF1F5"

# Utilitários
COLOR_OVERLAY = "rgba(15,20,25,.55)"
COLOR_CODE_BG = "#EDF0F5"
COLOR_MODAL_FOOTER = "#E5EAF2"
COLOR_SPINNER_TRACK = "#DDE3EE"

# Topo + Rail (azul-ardósia escuro — color-head do v4; topo e rail compartilham)
COLOR_HEAD = "#2B3A4A"
COLOR_HEAD_BORDER = "#1F2C39"
COLOR_RAIL = "#2B3A4A"
COLOR_TOP = "#2B3A4A"
COLOR_RAIL_TEXT = "#B9C6D6"
COLOR_RAIL_FOOT = "#5E748B"
COLOR_TOP_BORDER_SOFT = "#4A6076"
COLOR_TOP_BTN_TEXT = "#D7E0EA"

# Editor
COLOR_EDITOR_GUTTER = "#EEF1F4"
COLOR_EDITOR_GUTTER_TEXT = "#9aa3ad"
COLOR_OCCURRENCE = "#FAEED5"
COLOR_OCCURRENCE_CURRENT = "#FBD46A"

# ---------------------------------------------------------------------------
# Raios de borda (px) — v4
# ---------------------------------------------------------------------------
RADIUS_XS = 2
RADIUS_SM = 4
RADIUS_MD = 6
RADIUS_PILL = 20

# ---------------------------------------------------------------------------
# Alturas de controle (px)
# ---------------------------------------------------------------------------
H_CTA = 56
H_BTN = 44
H_GHOST = 32
H_FIELD = 44

# ---------------------------------------------------------------------------
# Dimensões de layout (px) — v4
# ---------------------------------------------------------------------------
DIM_TOP = 56
DIM_RAIL = 84
DIM_GUTTER = 48
DIM_STRIP = 216
APP_MIN = 1180
APP_MAX = 1800
BORDER_WIDTH = 1

# ---------------------------------------------------------------------------
# Sombras e efeitos (valores CSS — usados em QSS quando suportado)
# ---------------------------------------------------------------------------
FOCUS_RING = "0 0 0 3px rgba(43,58,74,.28)"
METAL = (
    "inset 0 1px 0 rgba(255,255,255,.35),"
    " 0 1px 2px rgba(20,28,38,.08)"
)
SHADOW_SCREEN = "0 12px 32px rgba(0,0,0,.22)"
SHADOW_MODAL = "0 16px 40px rgba(0,0,0,.30)"


# ---------------------------------------------------------------------------
# Interpolação de tokens no QSS
# ---------------------------------------------------------------------------
def _token_map() -> dict[str, str]:
    """Mapa nome→valor de todos os tokens string deste módulo (placeholders QSS)."""
    return {k: v for k, v in globals().items() if k.isupper() and isinstance(v, str)}


def render_qss(template: str) -> str:
    """Interpola ``${TOKEN}`` no template QSS com os tokens deste módulo.

    Levanta ``KeyError`` se o template referenciar um token inexistente — o que
    mantém o contrato "todos os valores de cor vêm de tokens de theme.py".
    """
    return string.Template(template).substitute(_token_map())
