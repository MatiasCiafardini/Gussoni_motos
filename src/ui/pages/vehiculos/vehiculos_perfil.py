from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QMessageBox, QLabel, QSpinBox
from src.data import util_excel as ux

class VehiculoPerfil(QDialog):
    def __init__(self, parent=None, vehiculo_id: int | None = None):
        super().__init__(parent)
        self.setWindowTitle("Perfil de Vehículo")
        self.setModal(True)
        self._id = vehiculo_id

        lay = QVBoxLayout(self)
        title = QLabel("Vehículo")
        title.setStyleSheet("font-size:16px; font-weight:600;")
        lay.addWidget(title)

        form = QFormLayout()
        self.marca = QLineEdit()
        self.modelo = QLineEdit()
        self.anio = QSpinBox()
        self.anio.setRange(1950, 2100)
        self.vin = QLineEdit()
        self.precio = QLineEdit()
        self.estado = QLineEdit()
        self.cliente_id = QLineEdit()
        form.addRow("Marca:", self.marca)
        form.addRow("Modelo:", self.modelo)
        form.addRow("Año:", self.anio)
        form.addRow("VIN:", self.vin)
        form.addRow("Precio:", self.precio)
        form.addRow("Estado:", self.estado)
        form.addRow("Cliente ID:", self.cliente_id)
        lay.addLayout(form)

        btns = QHBoxLayout()
        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.setObjectName("Primary")
        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_eliminar.setObjectName("Danger")
        self.btn_cancelar = QPushButton("Cerrar")
        btns.addWidget(self.btn_guardar)
        btns.addWidget(self.btn_eliminar)
        btns.addStretch(1)
        btns.addWidget(self.btn_cancelar)
        lay.addLayout(btns)

        self.btn_guardar.clicked.connect(self.on_guardar)
        self.btn_eliminar.clicked.connect(self.on_eliminar)
        self.btn_cancelar.clicked.connect(self.reject)

        if vehiculo_id is not None:
            self._load(vehiculo_id)
        else:
            self.btn_eliminar.setEnabled(False)

    def _load(self, vid: int):
        data = ux.get_vehiculo_by_id(vid)
        if not data:
            QMessageBox.warning(self, "Aviso", "Vehículo no encontrado.")
            self.reject()
            return
        self._id = vid
        self.marca.setText(str(data.get("marca","")))
        self.modelo.setText(str(data.get("modelo","")))
        self.anio.setValue(int(data.get("anio", 2000) or 2000))
        self.vin.setText(str(data.get("vin","")))
        self.precio.setText(str(data.get("precio","")))
        self.estado.setText(str(data.get("estado","")))
        self.cliente_id.setText("" if data.get("cliente_id") in (None, float('nan')) else str(int(data.get("cliente_id"))))

    def on_guardar(self):
        payload = {
            "id": self._id,
            "marca": self.marca.text().strip(),
            "modelo": self.modelo.text().strip(),
            "anio": int(self.anio.value()),
            "vin": self.vin.text().strip(),
            "precio": float(self.precio.text().strip() or 0),
            "estado": self.estado.text().strip() or "Disponible",
            "cliente_id": None if not self.cliente_id.text().strip() else int(self.cliente_id.text().strip()),
        }
        vid = ux.save_vehiculo(payload)
        self._id = vid
        QMessageBox.information(self, "OK", "Guardado correctamente.")
        self.accept()

    def on_eliminar(self):
        if self._id is None:
            return
        ok = ux.delete_vehiculo(self._id)
        if ok:
            QMessageBox.information(self, "OK", "Vehículo eliminado.")
            self.accept()
        else:
            QMessageBox.warning(self, "Aviso", "No se pudo eliminar.")
