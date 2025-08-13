from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QGridLayout, QLabel,
    QLineEdit, QPushButton, QHBoxLayout, QWidget as _QWidget, QComboBox
)
from PySide6.QtCore import Qt
from src.data import util_excel as ux
from .clientes_tabla import ClientesTabla
from .clientes_detalle import ClienteDetalle
from .clientes_editar import ClienteEditar
import pandas as pd

LABEL_STRETCH = 1
FIELD_STRETCH = 3

class ClientesMain(QWidget):
    def __init__(self, parent=None, notify=None, navigate=None, navigate_back=None):
        super().__init__(parent)
        self._notify = notify or (lambda msg: None)
        self._navigate = navigate or (lambda w: None)
        self._navigate_back = navigate_back or (lambda: None)
        self._filter_cols = None  # 1/2/3 columnas de filtros
        self._first_show = True  # bandera para saber si es la primera vez
        lay = QVBoxLayout(self)

        # --- Filtros (SIN título) ---
        self.gb_filtros = QGroupBox("")
        self.gb_filtros.setStyleSheet("""
            QGroupBox { margin-top: 0px; }
            QLabel { background: transparent; }
            QWidget#btnContainer { background: transparent; }
        """)

        self.f_nombre = QLineEdit();  self.f_nombre.setPlaceholderText("Ej: Ana")
        self.f_dni    = QLineEdit();  self.f_dni.setPlaceholderText("Ej: 12345678A")
        self.f_email  = QLineEdit();  self.f_email.setPlaceholderText("Ej: nombre@correo.com")

        self.f_estado = QComboBox()
        self.f_estado.addItems(["Activo", "Inactivo", "Todos"])
        self.f_estado.setCurrentText("Activo")  # por defecto mostrar activos

        self.grid_filtros = QGridLayout()
        self.grid_filtros.setContentsMargins(12, 12, 12, 12)
        self.grid_filtros.setHorizontalSpacing(16)
        self.grid_filtros.setVerticalSpacing(10)
        self.gb_filtros.setLayout(self.grid_filtros)

        # Botones dentro del groupbox
        self._buttons_bar = QHBoxLayout()
        self.btn_buscar  = QPushButton("Buscar");  self.btn_buscar.setObjectName("Primary")
        self.btn_limpiar = QPushButton("Limpiar")
        self.btn_agregar = QPushButton("Agregar cliente"); self.btn_agregar.setObjectName("Primary")
        self._buttons_bar.addWidget(self.btn_buscar)
        self._buttons_bar.addWidget(self.btn_limpiar)
        self._buttons_bar.addStretch(1)
        self._buttons_bar.addWidget(self.btn_agregar)

        self._btn_container = _QWidget(); self._btn_container.setObjectName("btnContainer")
        self._btn_container.setLayout(self._buttons_bar)

        self._arrange_filters(cols=3)
        lay.addWidget(self.gb_filtros)

        # --- Tabla ---
        self.tabla = ClientesTabla(self)
        lay.addWidget(self.tabla)

        # Conexiones
        self.btn_buscar.clicked.connect(self.load_data)
        self.btn_limpiar.clicked.connect(self.clear_filters)
        self.btn_agregar.clicked.connect(self.open_new)
        self.tabla.perfil_clicked.connect(self.on_click_perfil)

        # 🔙 SIN búsqueda automática al iniciar
    def showEvent(self, event):
        """Se ejecuta cada vez que la pantalla es visible."""
        super().showEvent(event)
        # Limpiar tabla al entrar
        empty_df = pd.DataFrame(columns=[
            "id", "nombre", "dni", "email", "telefono", "direccion", "estado"
        ])
        self.tabla.set_dataframe(empty_df)
        if self._first_show:
            self._first_show = False
            return  # primera vez: no recargamos nada
        self.load_data()
    # ----- Disposición responsive con proporciones fijas -----
    def _arrange_filters(self, cols: int):
        if self._filter_cols == cols:
            return
        self._filter_cols = cols

        # Limpiar grid
        while self.grid_filtros.count():
            item = self.grid_filtros.takeAt(0)
            w = item.widget()
            if w: w.setParent(None)

        pairs = [
            (QLabel("Nombre:"), self.f_nombre),
            (QLabel("DNI:"),    self.f_dni),
            (QLabel("Email:"),  self.f_email),
            (QLabel("Estado:"), self.f_estado),
        ]

        for i, (lab, field) in enumerate(pairs):
            lab.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            row = i // cols
            col = (i % cols) * 2
            self.grid_filtros.addWidget(lab,   row, col)
            self.grid_filtros.addWidget(field, row, col + 1)

        total_cols = cols * 2
        for c in range(total_cols):
            self.grid_filtros.setColumnStretch(c, LABEL_STRETCH if c % 2 == 0 else FIELD_STRETCH)

        last_row = (len(pairs) - 1) // cols + 1
        self.grid_filtros.addWidget(self._btn_container, last_row, 0, 1, total_cols)

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        w = self.width()
        cols = 3 if w >= 1000 else 2 if w >= 700 else 1
        self._arrange_filters(cols)

    # ----- Acciones -----
    def clear_filters(self):
        self.f_nombre.clear(); self.f_dni.clear(); self.f_email.clear()
        self.f_estado.setCurrentText("Activo")
        self._notify("Filtros limpiados.")

    def load_data(self):
        estado_value = self.f_estado.currentText()
        filters = {
            "nombre": self.f_nombre.text().strip(),
            "dni":    self.f_dni.text().strip(),
            "email":  self.f_email.text().strip(),
            "estado": None if estado_value == "Todos" else estado_value,
        }
        filters = {k: v for k, v in filters.items() if v}
        df = ux.load_clientes(filters)
        self.tabla.set_dataframe(df)

    def on_click_perfil(self, row: int):
        cid = self.tabla.model.get_row_id(row)
        if cid is None:
            return
        detalle = ClienteDetalle(cliente_id=cid, notify=self._notify, navigate=self._navigate, navigate_back=self._navigate_back)
        self._navigate(detalle)

    def open_new(self):
        editor = ClienteEditar(cliente_id=None, notify=self._notify, navigate=self._navigate,
                               navigate_back=self._navigate_back, on_saved=self._after_new_saved,
                               back_steps_after_delete=1)
        self._navigate(editor)

    def _after_new_saved(self, cid: int):
        self.load_data()
