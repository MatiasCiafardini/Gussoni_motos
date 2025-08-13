from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QHBoxLayout
)
from src.data import util_excel as ux
from src.ui.notify import NotifyPopup


class VehiculoEditar(QWidget):
    def __init__(self, vehiculo_id=None, notify=None, navigate=None, navigate_back=None, on_saved=None):
        super().__init__()
        self._id = vehiculo_id
        # Si no se pasa notify, usar el popup centrado por defecto
        self._notify = notify if callable(notify) else (lambda msg, tipo="info": self._show_notify(msg, tipo))
        self._navigate = navigate
        self._navigate_back = navigate_back
        self._on_saved = on_saved

        layout = QVBoxLayout(self)

        # Formulario
        form = QFormLayout()
        self.txt_marca = QLineEdit()
        self.txt_modelo = QLineEdit()
        self.txt_anio = QLineEdit()
        self.txt_vin = QLineEdit()
        self.txt_precio = QLineEdit()
        self.txt_estado = QLineEdit()

        form.addRow("Marca:", self.txt_marca)
        form.addRow("Modelo:", self.txt_modelo)
        form.addRow("Año:", self.txt_anio)
        form.addRow("VIN:", self.txt_vin)
        form.addRow("Precio:", self.txt_precio)
        form.addRow("Estado:", self.txt_estado)

        layout.addLayout(form)

        # Botones
        btn_row = QHBoxLayout()
        btn_guardar = QPushButton("Guardar")
        btn_cancelar = QPushButton("Cancelar")
        btn_guardar.clicked.connect(self._guardar)
        btn_cancelar.clicked.connect(self._navigate_back)
        btn_row.addWidget(btn_guardar)
        btn_row.addWidget(btn_cancelar)

        layout.addLayout(btn_row)

        if self._id is not None:
            self._cargar_datos()

    def _show_notify(self, text, tipo="info"):
        """Muestra un popup de notificación centrado sobre la ventana principal."""
        popup = NotifyPopup(text, tipo, parent=self)
        popup.show_centered()

    def _cargar_datos(self):
        """Carga datos del vehículo en el formulario."""
        data = ux.get_vehiculo_by_id(self._id)
        if data:
            self.txt_marca.setText(str(data.get("marca", "")))
            self.txt_modelo.setText(str(data.get("modelo", "")))
            self.txt_anio.setText(str(data.get("anio", "")))
            self.txt_vin.setText(str(data.get("vin", "")))
            self.txt_precio.setText(str(data.get("precio", "")))
            self.txt_estado.setText(str(data.get("estado", "")))

    def _validar(self):
        """Valida los campos antes de guardar."""


        if not self.txt_marca.text().strip():
            self._notify("La marca es obligatoria", "error")
            return False
        if not self.txt_modelo.text().strip():
            self._notify("El modelo es obligatorio", "error")
            return False
        if not self.txt_anio.text().isdigit() or len(self.txt_anio.text()) != 4:
            
            print("VALIDANDO vehiculo...")
            self._show_notify("El año debe tener 4 dígitos numéricos", "error")
            return False
        try:
            precio = float(self.txt_precio.text().replace(",", "."))
            if precio < 0:
                raise ValueError
        except ValueError:
            self._notify("El precio debe ser un número válido y positivo", "error")
            return False
        return True

    def _guardar(self):
        """Guarda o actualiza el vehículo."""
        if not self._validar():
            return

        payload = {
            "id": self._id,
            "marca": self.txt_marca.text().strip(),
            "modelo": self.txt_modelo.text().strip(),
            "anio": self.txt_anio.text().strip(),
            "vin": self.txt_vin.text().strip(),
            "precio": float(self.txt_precio.text().replace(",", ".")),
            "estado": self.txt_estado.text().strip(),
        }

        vid = ux.upsert_vehiculo(payload)

        self._notify("Vehículo guardado correctamente", "success")
        if self._on_saved:
            self._on_saved(vid)
        self._navigate_back()
