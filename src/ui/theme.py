from PySide6.QtCore import QFile, QTextStream

# QSS inspirado en Bootstrap (limpio, colores suaves, bordes redondeados)
BOOTSTRAP_QSS = """
* { 
    font-family: 'Inter', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; 
    font-size: 13px;
}
QMainWindow, QWidget {
    background: #f8f9fa;
    color: #212529;
}
QFrame#Sidebar {
    background: #ffffff;
    border-right: 1px solid #e5e7eb;
}
QPushButton {
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 6px 10px;
    background: #ffffff;
}
QPushButton:hover {
    background: #f1f3f5;
}
QPushButton:pressed {
    background: #e9ecef;
}
QPushButton#Primary {
    background: #0d6efd;
    color: white;
    border-color: #0d6efd;
}
QPushButton#Primary:hover {
    background: #0b5ed7;
}
QPushButton#Danger {
    background: #dc3545;
    color: white;
    border-color: #dc3545;
}
QLineEdit, QComboBox, QSpinBox {
    border: 1px solid #ced4da;
    border-radius: 8px;
    padding: 6px 8px;
    background: white;
}
QGroupBox {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    margin-top: 16px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 4px 8px;
    color: #495057;
}
QTableView {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    gridline-color: #f1f3f5;
    selection-background-color: #e7f1ff;
    selection-color: #212529;
}
QHeaderView::section {
    background: #f8f9fa;
    border: none;
    border-bottom: 1px solid #e5e7eb;
    padding: 8px;
    font-weight: 600;
}
QStatusBar {
    background: #ffffff;
    border-top: 1px solid #e5e7eb;
}
"""

def load_theme():
    return BOOTSTRAP_QSS
