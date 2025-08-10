from PySide6.QtGui import QFont, QPalette, QColor
from PySide6.QtWidgets import QApplication

PALETTE = {
    "ink": "#1f1f2e",
    "secondary": "#6c757d",
    "muted": "#adb5bd",
    "border": "#dee2e6",
    "bg": "#f8f9fa",
    "white": "#ffffff",
}

def _build_qss(p=PALETTE) -> str:
    return f"""
/* Reset */
QLabel {{ background: transparent; color: {p['ink']}; }}

/* Corner del QTableView sin iconos */
QTableCornerButton::section {{
    background: {p['bg']};
    border: 1px solid {p['border']};
    image: none;          /* 👈 evita que aparezca cualquier icono (la “lupa”) */
}}

/* Sidebar */
QFrame#Sidebar {{
    background: {p['ink']};
    border-right: 1px solid {p['border']};
}}
QFrame#Sidebar QLabel {{ color: {p['bg']}; }}
QFrame#Sidebar QPushButton {{
    background: transparent;
    color: {p['bg']};
    border: 1px solid {p['secondary']};
    border-radius: 10px;
    padding: 8px 12px;
    text-align: left;
}}
QFrame#Sidebar QPushButton:hover {{
    background: {p['secondary']};
    color: {p['bg']};
}}
QFrame#Sidebar QPushButton:pressed {{
    background: {p['ink']};
    border-color: {p['ink']};
}}

/* Botones */
QPushButton {{
    background: {p['white']};
    color: {p['ink']};
    border: 1px solid {p['border']};
    border-radius: 10px;
    padding: 8px 12px;
}}
QPushButton:hover {{ background: {p['bg']}; }}
QPushButton:disabled {{ color: {p['muted']}; background: {p['bg']}; }}
QPushButton#Primary {{
    background: {p['ink']};
    color: {p['white']};
    border: 1px solid {p['ink']};
}}
QPushButton#Primary:hover {{
    background: {p['secondary']};
    border-color: {p['secondary']};
}}
QPushButton#Primary:pressed {{
    background: {p['ink']};
    border-color: {p['ink']};
}}

/* GroupBox */
QGroupBox {{
    border: 1px solid {p['border']};
    border-radius: 10px;
    margin-top: 12px;
    background: {p['white']};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    top: -6px;
    padding: 0 6px;
    color: {p['secondary']};
    background: transparent;
}}

/* Inputs */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {{
    background: {p['white']};
    color: {p['ink']};
    border: 1px solid {p['border']};
    border-radius: 8px;
    padding: 6px 8px;
}}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {{
    border: 1px solid {p['secondary']};
    outline: none;
}}

/* Tablas */
QTableView {{
    background: {p['white']};
    color: {p['ink']};
    gridline-color: {p['border']};
    border: 1px solid {p['border']};
    border-radius: 8px;
    selection-background-color: rgba(31,31,46,0.10);
    selection-color: {p['ink']};
}}
QHeaderView::section {{
    background: {p['bg']};
    color: {p['ink']};
    padding: 6px 8px;
    border: 1px solid {p['border']};
    font-weight: 600;
}}

/* Cards */
QFrame#Card {{
    background: {p['white']};
    border: 1px solid {p['border']};
    border-radius: 12px;
}}
QLabel#KpiValue {{ color: {p['ink']}; }}
"""

def apply_theme(app: QApplication, base_font_pt: int = 11) -> None:
    f = QFont(); f.setFamily("Segoe UI"); f.setPointSize(base_font_pt)
    app.setFont(f)

    pal = QPalette()
    pal.setColor(QPalette.Window, QColor(PALETTE["bg"]))
    pal.setColor(QPalette.Base, QColor(PALETTE["white"]))
    pal.setColor(QPalette.Text, QColor(PALETTE["ink"]))
    pal.setColor(QPalette.ButtonText, QColor(PALETTE["ink"]))
    pal.setColor(QPalette.Button, QColor(PALETTE["white"]))
    pal.setColor(QPalette.WindowText, QColor(PALETTE["ink"]))
    pal.setColor(QPalette.ToolTipBase, QColor(PALETTE["bg"]))
    pal.setColor(QPalette.ToolTipText, QColor(PALETTE["ink"]))
    pal.setColor(QPalette.Highlight, QColor(PALETTE["secondary"]))
    pal.setColor(QPalette.HighlightedText, QColor(PALETTE["white"]))
    app.setPalette(pal)

    app.setStyleSheet(_build_qss(PALETTE))
