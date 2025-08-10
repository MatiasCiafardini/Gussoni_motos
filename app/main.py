import sys
from pathlib import Path

# Asegurar que src esté en PYTHONPATH cuando se ejecuta este archivo
CURRENT = Path(__file__).resolve()
ROOT = CURRENT.parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.ui.theme import load_theme
from src.data.util_excel import ensure_excel_files_exist

def main():
    ensure_excel_files_exist()
    app = QApplication(sys.argv)
    app.setStyleSheet(load_theme())
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
