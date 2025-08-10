from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFormLayout, QLineEdit,
    QPushButton, QHBoxLayout, QComboBox
)
from src.data import util_excel as ux

class VehiculoEditar(QWidget):
    """
    Página interna para crear/editar un vehículo.
    - 'Estado' incluye: Disponible / Reservado / Vendido / No disponible
    - Abajo centrado: Guardar (izquierda) y Volver (derecha)
    """
    def __init__(self, parent=None, vehiculo_id: int | None = None, notify=None, navigate=None, navigate_back=None, on_saved=None):
        super().__init__(parent)
        self._id = vehiculo_id
        self._notify = notify or (lambda msg: None)
        self._navigate = navigate or (lambda w: None)
        self._navigate_back = navigate_back or (lambda: None)
        self._on_saved = on_saved or (lambda vid: None)

        root = QVBoxLayout(self)

        # Header
        hdr = QHBoxLayout()
        title = QLabel("Editar Vehículo" if vehiculo_id else "Nuevo Vehículo")
        title.setStyleSheet("font-size:16px; font-weight:600;")
        hdr.addWidget(title); hdr.addStretch(1)
        root.addLayout(hdr)

        # Formulario
        form = QFormLayout()
        self.marca = QLineEdit()
        self.modelo = QLineEdit()
        self.anio = QLineEdit()
        self.vin = QLineEdit()
        self.precio = QLineEdit()
        self.estado = QComboBox(); self.estado.addItems(["Disponible","Reservado","Vendido","No disponible"])

        form.addRow("Marca:", self.marca)
        form.addRow("Modelo:", self.modelo)
        form.addRow("Año:", self.anio)
        form.addRow("VIN:", self.vin)
        form.addRow("Precio:", self.precio)
        form.addRow("Estado:", self.estado)
        root.addLayout(form)

        # Abajo centrado: Guardar (izq) y Volver (der)
        root.addStretch(1)
        bottom = QHBoxLayout()
        self.btn_guardar = QPushButton("Guardar"); self.btn_guardar.setObjectName("Primary")
        self.btn_volver = QPushButton("Volver")
        bottom.addStretch(1); bottom.addWidget(self.btn_guardar); bottom.addWidget(self.btn_volver); bottom.addStretch(1)
        root.addLayout(bottom)

        # Eventos
        self.btn_volver.clicked.connect(self._navigate_back)
        self.btn_guardar.clicked.connect(self._on_guardar)

        if vehiculo_id is not None:
            self._load(vehiculo_id)

    def _load(self, vid: int):
        data = ux.get_vehiculo_by_id(vid)
        if not data:
            self._notify("Vehículo no encontrado."); self.btn_guardar.setEnabled(False); return
        self._id = vid
        self.marca.setText(str(data.get("marca","")))
        self.modelo.setText(str(data.get("modelo","")))
        self.anio.setText(str(data.get("anio","")))
        self.vin.setText(str(data.get("vin","")))
        self.precio.setText(str(data.get("precio","")))
        self.estado.setCurrentText(str(data.get("estado","Disponible")))

    def _on_guardar(self):
        # normalizar numéricos
        anio_val = self.anio.text().strip()
        precio_val = self.precio.text().strip()
        try:
            anio_val = int(anio_val) if anio_val else None
        except Exception:
            anio_val = None
        try:
            precio_val = float(precio_val) if precio_val else None
        except Exception:
            precio_val = None

        payload = {
            "id": self._id,
            "marca": self.marca.text().strip(),
            "modelo": self.modelo.text().strip(),
            "anio": anio_val,
            "vin": self.vin.text().strip(),
            "precio": precio_val,
            "estado": self.estado.currentText(),
        }
        vid = ux.save_vehiculo(payload)
        self._id = vid
        self._notify("Guardado correctamente.")
        self._on_saved(vid)
        self._navigate_back()
