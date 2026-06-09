"""Ponto de entrada do FlowNC (GUI PySide6)."""
from __future__ import annotations

import sys
import traceback


def _install_excepthook() -> None:
    """Mostra erros nao tratados numa caixa de dialogo.

    Em EXE '--windowed' nao ha console: sem isso, qualquer excecao some sem
    deixar rastro (o app parece 'nao fazer nada'). Aqui o operador ve a mensagem.
    """
    from PySide6.QtWidgets import QMessageBox

    def hook(exc_type: type[BaseException], exc: BaseException, tb) -> None:  # type: ignore[no-untyped-def]
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc, tb)
            return
        detalhe = "".join(traceback.format_exception(exc_type, exc, tb))
        try:
            box = QMessageBox()
            box.setIcon(QMessageBox.Icon.Critical)
            box.setWindowTitle("Erro inesperado")
            box.setText(
                "Ocorreu um erro inesperado. O programa tentara continuar.\n\n"
                f"{exc_type.__name__}: {exc}"
            )
            box.setDetailedText(detalhe)
            box.exec()
        except Exception:
            sys.__excepthook__(exc_type, exc, tb)

    sys.excepthook = hook


def main() -> int:
    from PySide6.QtWidgets import QApplication

    from core.seed import ensure_seed
    from ui.main_window import MainWindow

    ensure_seed()  # garante data/ ao lado do .exe antes de carregar biblioteca/presets
    app = QApplication(sys.argv)
    app.setApplicationName("FlowNC")
    _install_excepthook()
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
