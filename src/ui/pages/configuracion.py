from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFormLayout, QLineEdit, QPushButton
from src.data.settings import CLIENTES_XLSX, VEHICULOS_XLSX

class ConfiguracionPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ConfiguracionPage")
        lay = QVBoxLayout(self)
        title = QLabel("Configuración", self)
        title.setStyleSheet("font-size:16px; font-weight:600;")
        lay.addWidget(title)

        form = QFormLayout()
        self.path_clientes = QLineEdit(str(CLIENTES_XLSX))
        self.path_vehiculos = QLineEdit(str(VEHICULOS_XLSX))
        self.path_clientes.setReadOnly(True)
        self.path_vehiculos.setReadOnly(True)
        form.addRow("Ruta clientes.xlsx:", self.path_clientes)
        form.addRow("Ruta vehiculos.xlsx:", self.path_vehiculos)
        lay.addLayout(form)

        self.btn = QPushButton("Guardar cambios")
        self.btn.setEnabled(False)
        lay.addWidget(self.btn)

        hint = QLabel("Por ahora las rutas son fijas. Más adelante podremos editarlas y usar MySQL en la nube.", self)
        lay.addWidget(hint)
