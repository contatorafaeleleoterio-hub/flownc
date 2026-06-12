"""Ícones vetoriais desenhados via QPainter — independentes de fonte.

A fonte da UI (IBM Plex) não cobre dingbats/formas (✎ ▦ ❖ ⧉ ▾ ●…): em máquinas
sem fallback esses glifos viram quadradinhos ou somem. Aqui cada ícone é
desenhado com primitivas (linhas/retângulos/arcos) num `QPixmap`, então renderiza
igual em qualquer Windows.

Uso: ``icon_pixmap("pencil", 16, theme.COLOR_RAIL_TEXT)``.
"""
from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen, QPixmap, QPolygonF


def icon_pixmap(kind: str, size: int, color: str) -> QPixmap:
    """Desenha o ícone `kind` em um QPixmap quadrado de `size` px na cor dada."""
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    c = QColor(color)
    pen = QPen(c, max(1.4, size / 11))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    s = float(size)

    if kind == "grid":  # Lote: grade 2×2
        g, cell = s * 0.14, s * 0.32
        for dx in (g, s - g - cell):
            for dy in (g, s - g - cell):
                p.drawRect(QRectF(dx, dy, cell, cell))
    elif kind == "pencil":  # Editor: lápis diagonal
        p.drawLine(QPointF(s * 0.28, s * 0.72), QPointF(s * 0.72, s * 0.28))
        p.drawLine(QPointF(s * 0.20, s * 0.80), QPointF(s * 0.28, s * 0.72))
        p.drawLine(QPointF(s * 0.66, s * 0.22), QPointF(s * 0.78, s * 0.34))
    elif kind == "tag":  # Códigos: etiqueta com furo
        poly = QPolygonF([
            QPointF(s * 0.18, s * 0.18), QPointF(s * 0.55, s * 0.18),
            QPointF(s * 0.82, s * 0.50), QPointF(s * 0.55, s * 0.82),
            QPointF(s * 0.18, s * 0.82),
        ])
        p.drawPolygon(poly)
        p.drawEllipse(QPointF(s * 0.36, s * 0.40), s * 0.05, s * 0.05)
    elif kind == "clock":  # Histórico: relógio
        m = s * 0.16
        p.drawEllipse(QRectF(m, m, s - 2 * m, s - 2 * m))
        p.drawLine(QPointF(s / 2, s / 2), QPointF(s / 2, s * 0.30))
        p.drawLine(QPointF(s / 2, s / 2), QPointF(s * 0.66, s * 0.58))
    elif kind == "copy":  # Duplicar: duas folhas sobrepostas
        off, w = s * 0.16, s * 0.52
        p.drawRect(QRectF(s * 0.18, s * 0.30, w, w))
        p.drawLine(QPointF(s * 0.18 + off, s * 0.30 - off + w), QPointF(s * 0.18 + off, s * 0.30 - off))
        p.drawLine(QPointF(s * 0.18 + off, s * 0.30 - off), QPointF(s * 0.18 + off + w, s * 0.30 - off))
        p.drawLine(QPointF(s * 0.18 + off + w, s * 0.30 - off), QPointF(s * 0.18 + off + w, s * 0.30 - off + w * 0.7))
    elif kind == "folder":  # Pasta (estados vazios)
        p.drawRect(QRectF(s * 0.14, s * 0.30, s * 0.72, s * 0.46))
        p.drawLine(QPointF(s * 0.14, s * 0.30), QPointF(s * 0.30, s * 0.20))
        p.drawLine(QPointF(s * 0.30, s * 0.20), QPointF(s * 0.46, s * 0.20))
        p.drawLine(QPointF(s * 0.46, s * 0.20), QPointF(s * 0.52, s * 0.30))
    elif kind == "caret-down":
        poly = QPolygonF([
            QPointF(s * 0.28, s * 0.40), QPointF(s * 0.72, s * 0.40),
            QPointF(s * 0.50, s * 0.66),
        ])
        p.setBrush(c)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPolygon(poly)
    elif kind == "caret-up":
        poly = QPolygonF([
            QPointF(s * 0.28, s * 0.62), QPointF(s * 0.72, s * 0.62),
            QPointF(s * 0.50, s * 0.36),
        ])
        p.setBrush(c)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPolygon(poly)
    elif kind == "dot":
        p.setBrush(c)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QRectF(s * 0.22, s * 0.22, s * 0.56, s * 0.56))
    elif kind == "warn":  # triângulo de atenção com "!"
        poly = QPolygonF([
            QPointF(s * 0.50, s * 0.14), QPointF(s * 0.88, s * 0.82),
            QPointF(s * 0.12, s * 0.82),
        ])
        p.drawPolygon(poly)
        p.drawLine(QPointF(s * 0.50, s * 0.38), QPointF(s * 0.50, s * 0.60))
        p.drawLine(QPointF(s * 0.50, s * 0.70), QPointF(s * 0.50, s * 0.72))

    p.end()
    return pm
