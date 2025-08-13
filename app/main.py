import sys
from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.ui.theme import apply_theme

def main():
    app = QApplication(sys.argv)

    # 🔎 Subí un punto la fuente global (antes ~10pt). Probá 11 o 12 según te guste.
    apply_theme(app, base_font_pt=15)

    win = MainWindow()
    win.showMaximized()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
