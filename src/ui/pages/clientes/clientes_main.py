from PySide6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QFormLayout, QLineEdit, QPushButton, QHBoxLayout
from src.data import util_excel as ux
from .clientes_tabla import ClientesTabla
from .clientes_perfil import ClientePerfil

class ClientesMain(QWidget):
    def __init__(self, parent=None, notify=None):
        super().__init__(parent)
        self._notify = notify or (lambda msg: None)
        lay = QVBoxLayout(self)

        # Filtros (tabla inicia vacía)
        gb = QGroupBox("Filtros")
        f = QFormLayout()
        self.f_nombre = QLineEdit()
        self.f_dni = QLineEdit()
        self.f_email = QLineEdit()
        f.addRow("Nombre:", self.f_nombre)
        f.addRow("DNI:", self.f_dni)
        f.addRow("Email:", self.f_email)
        gb.setLayout(f)

        hb = QHBoxLayout()
        self.btn_buscar = QPushButton("Buscar")
        self.btn_buscar.setObjectName("Primary")
        self.btn_limpiar = QPushButton("Limpiar")
        hb.addWidget(self.btn_buscar)
        hb.addWidget(self.btn_limpiar)
        hb.addStretch(1)

        self.btn_agregar = QPushButton("Agregar cliente")
        self.btn_agregar.setObjectName("Primary")
        hb.addWidget(self.btn_agregar)

        lay.addWidget(gb)
        lay.addLayout(hb)

        # Tabla
        self.tabla = ClientesTabla(self)
        lay.addWidget(self.tabla)

        # Conexiones
        self.btn_buscar.clicked.connect(self.load_data)
        self.btn_limpiar.clicked.connect(self.clear_filters)
        self.btn_agregar.clicked.connect(self.open_new)

        # click en Perfil
        self.tabla.delegate.clicked.connect(self.on_click_perfil)

    def clear_filters(self):
        self.f_nombre.clear()
        self.f_dni.clear()
        self.f_email.clear()
        self.tabla.set_dataframe(self.tabla.model._df.iloc[0:0])  # vaciar
        self._notify("Filtros limpiados.")

    def load_data(self):
        filters = {
            "nombre": self.f_nombre.text().strip(),
            "dni": self.f_dni.text().strip(),
            "email": self.f_email.text().strip(),
        }
        df = ux.load_clientes(filters)
        self.tabla.set_dataframe(df)
        self._notify(f"Se cargaron {len(df)} clientes.")

    def on_click_perfil(self, row: int):
        cid = self.tabla.model.get_row_id(row)
        if cid is None:
            return
        dlg = ClientePerfil(self, cliente_id=cid)
        if dlg.exec():
            # recargar por si hubo cambios
            self.load_data()

    def open_new(self):
        dlg = ClientePerfil(self, cliente_id=None)
        if dlg.exec():
            self.load_data()
