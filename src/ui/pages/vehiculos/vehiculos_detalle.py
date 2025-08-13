from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFormLayout, QPushButton,
    QHBoxLayout, QGroupBox
)
from PySide6.QtCore import Qt
from src.data import util_excel as ux
from src.data.util_format import format_currency
from .vehiculos_editar import VehiculoEditar

class VehiculoDetalle(QWidget):
    """Perfil interno del vehículo. 'Editar' debajo de Datos (derecha). 'Volver' abajo centrado."""
    def __init__(self, parent=None, vehiculo_id: int | None = None, notify=None, navigate=None, navigate_back=None):
        super().__init__(parent)
        self._id = vehiculo_id
        self._notify = notify or (lambda msg: None)
        self._navigate = navigate or (lambda w: None)
        self._navigate_back = navigate_back or (lambda: None)

        root = QVBoxLayout(self)

        title = QLabel("Perfil del vehículo")
        title.setStyleSheet("font-size:16px; font-weight:600;")
        root.addWidget(title)

        self.gb_datos = QGroupBox("")
        form = QFormLayout()

        self.lbl_id = QLabel("")
        self.lbl_marca = QLabel("")
        self.lbl_modelo = QLabel("")
        self.lbl_anio = QLabel("")
        self.lbl_vin = QLabel("")
        self.lbl_precio = QLabel("")
        self.lbl_estado = QLabel("")
        self.lbl_cliente_id = QLabel("")

        for w in [
            self.lbl_id, self.lbl_marca, self.lbl_modelo, self.lbl_anio,
            self.lbl_vin, self.lbl_precio, self.lbl_estado, self.lbl_cliente_id
        ]:
            w.setTextInteractionFlags(Qt.TextSelectableByMouse)

        form.addRow(QLabel("Marca:"), self.lbl_marca)
        form.addRow(QLabel("Modelo:"), self.lbl_modelo)
        form.addRow(QLabel("Año:"), self.lbl_anio)
        form.addRow(QLabel("VIN:"), self.lbl_vin)
        form.addRow(QLabel("Precio:"), self.lbl_precio)
        form.addRow(QLabel("Estado:"), self.lbl_estado)
        form.addRow(QLabel("Cliente ID:"), self.lbl_cliente_id)

        self.gb_datos.setLayout(form)
        root.addWidget(self.gb_datos)

        row_edit = QHBoxLayout()
        self.btn_editar = QPushButton("Editar")
        self.btn_editar.setObjectName("Primary")
        row_edit.addStretch(1)
        row_edit.addWidget(self.btn_editar)
        root.addLayout(row_edit)

        root.addStretch(1)
        bottom = QHBoxLayout()
        self.btn_volver = QPushButton("Volver")
        bottom.addStretch(1)
        bottom.addWidget(self.btn_volver)
        bottom.addStretch(1)
        root.addLayout(bottom)

        self.btn_volver.clicked.connect(self._navigate_back)
        self.btn_editar.clicked.connect(self._on_editar)

        if vehiculo_id is not None:
            self._load(vehiculo_id)
        else:
            self.btn_editar.setEnabled(False)

    def _on_editar(self):
        editor = VehiculoEditar(
            vehiculo_id=self._id,
            notify=self._notify,
            navigate=self._navigate,
            navigate_back=self._navigate_back,
            on_saved=self._after_edit_saved
        )
        self._navigate(editor)

    def _after_edit_saved(self, vid: int):
        self._load(vid)

    def _load(self, vid: int):
        data = ux.get_vehiculo_by_id(vid)
        if not data:
            self._notify("Vehículo no encontrado.")
            self.btn_editar.setEnabled(False)
            return

        self.lbl_id.setText(str(data.get("id", "")))
        self.lbl_marca.setText(str(data.get("marca", "")))
        self.lbl_modelo.setText(str(data.get("modelo", "")))
        self.lbl_anio.setText(str(data.get("anio", "")))
        self.lbl_vin.setText(str(data.get("vin", "")))
        self.lbl_precio.setText(format_currency(data.get("precio", 0)))
        self.lbl_estado.setText(str(data.get("estado", "")))
        self.lbl_cliente_id.setText("" if pd_isna(data.get("cliente_id")) else str(data.get("cliente_id")))

        self._id = vid

def pd_isna(x):
    try:
        import pandas as pd
        return pd.isna(x)
    except Exception:
        return x is None
