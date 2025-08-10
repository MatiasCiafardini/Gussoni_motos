from PySide6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QFormLayout, QLineEdit, QPushButton, QHBoxLayout
from src.data import util_excel as ux
from .vehiculos_tabla import VehiculosTabla
from .vehiculos_perfil import VehiculoPerfil

class VehiculosMain(QWidget):
    def __init__(self, parent=None, notify=None):
        super().__init__(parent)
        self._notify = notify or (lambda msg: None)
        lay = QVBoxLayout(self)

        gb = QGroupBox("Filtros")
        f = QFormLayout()
        self.f_marca = QLineEdit()
        self.f_modelo = QLineEdit()
        self.f_anio = QLineEdit()
        self.f_vin = QLineEdit()
        self.f_estado = QLineEdit()
        f.addRow("Marca:", self.f_marca)
        f.addRow("Modelo:", self.f_modelo)
        f.addRow("Año:", self.f_anio)
        f.addRow("VIN:", self.f_vin)
        f.addRow("Estado:", self.f_estado)
        gb.setLayout(f)

        hb = QHBoxLayout()
        self.btn_buscar = QPushButton("Buscar")
        self.btn_buscar.setObjectName("Primary")
        self.btn_limpiar = QPushButton("Limpiar")
        hb.addWidget(self.btn_buscar)
        hb.addWidget(self.btn_limpiar)
        hb.addStretch(1)

        self.btn_agregar = QPushButton("Agregar vehículo")
        self.btn_agregar.setObjectName("Primary")
        hb.addWidget(self.btn_agregar)

        lay.addWidget(gb)
        lay.addLayout(hb)

        self.tabla = VehiculosTabla(self)
        lay.addWidget(self.tabla)

        self.btn_buscar.clicked.connect(self.load_data)
        self.btn_limpiar.clicked.connect(self.clear_filters)
        self.btn_agregar.clicked.connect(self.open_new)

        self.tabla.delegate.clicked.connect(self.on_click_perfil)

    def clear_filters(self):
        self.f_marca.clear()
        self.f_modelo.clear()
        self.f_anio.clear()
        self.f_vin.clear()
        self.f_estado.clear()
        self.tabla.set_dataframe(self.tabla.model._df.iloc[0:0])
        self._notify("Filtros limpiados.")

    def load_data(self):
        filters = {
            "marca": self.f_marca.text().strip(),
            "modelo": self.f_modelo.text().strip(),
            "anio": self.f_anio.text().strip(),
            "vin": self.f_vin.text().strip(),
            "estado": self.f_estado.text().strip(),
        }
        df = ux.load_vehiculos(filters)
        self.tabla.set_dataframe(df)
        self._notify(f"Se cargaron {len(df)} vehículos.")

    def on_click_perfil(self, row: int):
        vid = self.tabla.model.get_row_id(row)
        if vid is None:
            return
        dlg = VehiculoPerfil(self, vehiculo_id=vid)
        if dlg.exec():
            self.load_data()

    def open_new(self):
        dlg = VehiculoPerfil(self, vehiculo_id=None)
        if dlg.exec():
            self.load_data()
