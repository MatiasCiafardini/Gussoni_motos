from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lbl = QLabel("Inicio (Dashboard)\n\nUsá el menú de la izquierda para navegar.", self)
        lbl.setStyleSheet("font-size:16px; font-weight:600;")
        lay.addWidget(lbl)
