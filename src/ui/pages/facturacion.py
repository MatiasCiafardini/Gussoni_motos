from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class FacturacionPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lbl = QLabel("Facturación\n\n(Placeholder: aquí irá la gestión de facturas.)", self)
        lbl.setStyleSheet("font-size:16px; font-weight:600;")
        lay.addWidget(lbl)
