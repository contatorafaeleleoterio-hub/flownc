#!/usr/bin/env python3
"""Preview manual (não-pytest) do CodeCombo: placeholder + seta unicode.

Rode a partir da pasta flownc/:  python preview_combo.py
"""
import sys

from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget

from ui.components.code_combo import CodeCombo

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Janela simples
    win = QMainWindow()
    win.setWindowTitle("CodeCombo Test — Placeholder + Seta Unicode")
    win.setGeometry(100, 100, 400, 300)

    widget = QWidget()
    layout = QVBoxLayout(widget)

    # Label de instrução
    label = QLabel("Clique nos combos abaixo para ver o dropdown com a lista de códigos.")
    layout.addWidget(label)

    # Combo 1: Vazio (mostra placeholder)
    label1 = QLabel("Código de origem (vazio — mostra 'Selecione o código'):")
    layout.addWidget(label1)
    combo1 = CodeCombo()
    combo1.addItem("M8", "M8")
    combo1.addItem("M6", "M6")
    combo1.addItem("G54", "G54")
    combo1.addItem("T1", "T1")
    layout.addWidget(combo1)

    # Combo 2: Preenchido
    label2 = QLabel("Trocar por (preenchido com 'M08'):")
    layout.addWidget(label2)
    combo2 = CodeCombo()
    combo2.addItem("M08", "M08")
    combo2.addItem("M06", "M06")
    combo2.addItem("G55", "G55")
    combo2.addItem("T01", "T01")
    combo2.setCurrentText("M08")
    layout.addWidget(combo2)

    layout.addStretch()
    win.setCentralWidget(widget)
    win.show()

    print("✓ App aberta. Teste:")
    print("  1. Clique em 'Código de origem' — vê placeholder + lista + seta ▾→▴")
    print("  2. Clique em 'Trocar por' — vé valor já preenchido + lista + seta")
    print("  3. Selecione um código — placeholder some, combo fica com valor")

    sys.exit(app.exec())
