from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class ReportesPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lbl = QLabel("Reportes\n\n(Placeholder: KPIs, tablas y exportaciones.)", self)
        lbl.setStyleSheet("font-size:16px; font-weight:600;")
        lay.addWidget(lbl)
