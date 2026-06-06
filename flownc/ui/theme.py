"""Tokens de design do FlowNC — extraídos de mockups/painel-final.v2.html.

Constantes Python para uso no QSS e em código de UI.
Importável sem instanciar QApplication.
"""
from __future__ import annotations

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
FONT_SANS = '"IBM Plex Sans", "Segoe UI", system-ui, -apple-system, Roboto, sans-serif'
FONT_MONO = '"IBM Plex Mono", "Consolas", ui-monospace, monospace'

# Família curta (para QFont)
FONT_SANS_FAMILY = "IBM Plex Sans"
FONT_MONO_FAMILY = "IBM Plex Mono"
FONT_SANS_FALLBACK = "Segoe UI"
FONT_MONO_FALLBACK = "Consolas"

# ---------------------------------------------------------------------------
# Tipografia — (peso, tamanho px, line-height)
# Usados para montar regras QSS: font-size / font-weight / line-height
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
# Cores
# ---------------------------------------------------------------------------

# Fundos
COLOR_BG_BASE = "#F8FAFB"
COLOR_BG_SUBTLE = "#ECEFF3"
COLOR_BG_RAIL = "#E1E6EC"
COLOR_BG_SURFACE = "#C2C9D1"
COLOR_WHITE = "#FFFFFF"

# Textos
COLOR_TEXT_PRIMARY = "#1B2128"
COLOR_TEXT_SECONDARY = "#56616D"
COLOR_TEXT_TERTIARY = "#899099"

# Bordas
COLOR_BORDER = "#CDD4DB"
COLOR_BORDER_STRONG = "#aeb6bf"

# Interativo (links, botões secundários, foco)
COLOR_INTERACTIVE = "#1F5F9E"
COLOR_INTERACTIVE_HV = "#2B76C0"
COLOR_INTERACTIVE_BG = "#E4EEF7"

# Semânticas
COLOR_SUCCESS = "#1C8A4D"
COLOR_SUCCESS_BG = "#E1F1E8"
COLOR_WARNING = "#A86A07"
COLOR_WARNING_BG = "#FAEED5"
COLOR_DANGER = "#BB3324"
COLOR_DANGER_BG = "#FAE4E1"
COLOR_DANGER_DEEP = "#8a2a2a"
COLOR_DANGER_DEEP_BG = "#efd6d6"

# CTA (botão principal / Executar Lote)
COLOR_CTA_START = "#3A434E"
COLOR_CTA_END = "#232A33"
COLOR_CTA_TEXT = "#F4F7FA"
COLOR_CTA_TEXT_SOFT = "#aeb8c2"

# Utilitários
COLOR_OVERLAY = "rgba(15,20,25,.55)"
COLOR_CODE_BG = "#eef1f4"
COLOR_ROW_DELETED = "#fcf2f2"
COLOR_MODAL_FOOTER = "#e7ebee"
COLOR_DISABLED_BG = "#9fb3c6"
COLOR_SPINNER_TRACK = "#d6dee4"

# Header gradiente
COLOR_HEAD_TOP = "#D3DAE1"
COLOR_HEAD_MID = "#c3cbd3"
COLOR_HEAD_BOT = "#B9C2CB"
COLOR_HEAD_BORDER = "#a7afb8"

# Editor
COLOR_EDITOR_GUTTER = "#EEF1F4"
COLOR_EDITOR_GUTTER_TEXT = "#9aa3ad"
COLOR_OCCURRENCE = "#FAEED5"
COLOR_OCCURRENCE_CURRENT = "#FBD46A"

# ---------------------------------------------------------------------------
# Raios de borda (px)
# ---------------------------------------------------------------------------
RADIUS_XS = 4
RADIUS_SM = 8
RADIUS_MD = 12
RADIUS_PILL = 20

# ---------------------------------------------------------------------------
# Alturas de controle (px)
# ---------------------------------------------------------------------------
H_CTA = 56
H_BTN = 44
H_GHOST = 32
H_FIELD = 44

# ---------------------------------------------------------------------------
# Dimensões de layout (px)
# ---------------------------------------------------------------------------
DIM_SCREEN = 1340
DIM_HEADER = 70
DIM_GUTTER = 48
BORDER_WIDTH = 1

# ---------------------------------------------------------------------------
# Sombras e efeitos (valores CSS — usados em QSS box-shadow quando suportado)
# ---------------------------------------------------------------------------
FOCUS_RING = "0 0 0 3px rgba(31,95,158,.35)"
CONFLICT_BAR = "inset 3px 0 0 #A86A07"
METAL = (
    "inset 0 1px 0 rgba(255,255,255,.85),"
    " 0 1px 2px rgba(20,28,38,.10),"
    " 0 2px 6px rgba(20,28,38,.05)"
)
SHADOW_SCREEN = "0 18px 50px rgba(0,0,0,.30)"
SHADOW_MODAL = "0 20px 60px rgba(0,0,0,.40)"
