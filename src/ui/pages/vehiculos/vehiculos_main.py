from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QGridLayout, QLabel,
    QLineEdit, QPushButton, QHBoxLayout, QWidget as _QWidget, QComboBox
)
from PySide6.QtCore import Qt
from src.data import util_excel as ux
from .vehiculos_tabla import VehiculosTabla
from .vehiculos_detalle import VehiculoDetalle
from .vehiculos_editar import VehiculoEditar

LABEL_STRETCH = 1
FIELD_STRETCH = 3

class VehiculosMain(QWidget):
    def __init__(self, parent=None, notify=None, navigate=None, navigate_back=None):
        super().__init__(parent)
        self._notify = notify or (lambda msg: None)
        self._navigate = navigate or (lambda w: None)
        self._navigate_back = navigate_back or (lambda: None)
        self._filter_cols = None

        lay = QVBoxLayout(self)

        # --- Filtros (SIN título) ---
        self.gb_filtros = QGroupBox("")
        self.gb_filtros.setStyleSheet("""
            QGroupBox { margin-top: 0px; }
            QLabel { background: transparent; }
            QWidget#btnContainer { background: transparent; }
        """)

        # Campos de filtro
        self.f_marca   = QLineEdit(); self.f_marca.setPlaceholderText("Ej: Yamaha")
        self.f_modelo  = QLineEdit(); self.f_modelo.setPlaceholderText("Ej: MT-07")
        self.f_anio    = QLineEdit(); self.f_anio.setPlaceholderText("Ej: 2024")
        self.f_cuadro  = QLineEdit(); self.f_cuadro.setPlaceholderText("Ej: 8DYC11076TB104918")
        self.f_motor   = QLineEdit(); self.f_motor.setPlaceholderText("Ej: ZS152FMH8S200701")
        self.f_estado  = QComboBox(); self.f_estado.addItems(["Todos","Disponible","Reservado","Vendido","No disponible"])
        self.f_estado.setCurrentText("Todos")

        self.grid_filtros = QGridLayout()
        self.grid_filtros.setContentsMargins(12, 12, 12, 12)
        self.grid_filtros.setHorizontalSpacing(16)
        self.grid_filtros.setVerticalSpacing(10)
        self.gb_filtros.setLayout(self.grid_filtros)

        # Botones dentro del groupbox
        self._buttons_bar = QHBoxLayout()
        self.btn_buscar  = QPushButton("Buscar");  self.btn_buscar.setObjectName("Primary")
        self.btn_limpiar = QPushButton("Limpiar")
        self.btn_agregar = QPushButton("Agregar vehículo"); self.btn_agregar.setObjectName("Primary")
        self._buttons_bar.addWidget(self.btn_buscar)
        self._buttons_bar.addWidget(self.btn_limpiar)
        self._buttons_bar.addStretch(1)
        self._buttons_bar.addWidget(self.btn_agregar)

        self._btn_container = _QWidget(); self._btn_container.setObjectName("btnContainer")
        self._btn_container.setLayout(self._buttons_bar)

        self._arrange_filters(cols=3)
        lay.addWidget(self.gb_filtros)

        # --- Tabla ---
        self.tabla = VehiculosTabla(self)
        lay.addWidget(self.tabla)

        # Conexiones
        self.btn_buscar.clicked.connect(self.load_data)
        self.btn_limpiar.clicked.connect(self.clear_filters)
        self.btn_agregar.clicked.connect(self.open_new)
        self.tabla.perfil_clicked.connect(self.on_click_perfil)  # emite fila

        # (Sin búsqueda automática al iniciar)

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
            (QLabel("Marca:"),          self.f_marca),
            (QLabel("Modelo:"),         self.f_modelo),
            (QLabel("Año:"),            self.f_anio),
            (QLabel("Nº CUADRO:"),      self.f_cuadro),
            (QLabel("Nº MOTOR:"),       self.f_motor),
            (QLabel("Estado:"),         self.f_estado),
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
        self.f_marca.clear()
        self.f_modelo.clear()
        self.f_anio.clear()
        self.f_cuadro.clear()
        self.f_motor.clear()
        self.f_estado.setCurrentText("Todos")
        self._notify("Filtros limpiados.")

    def load_data(self):
        # Armado de filtros (ignora vacíos)
        filters = {
            "marca":       self.f_marca.text().strip(),
            "modelo":      self.f_modelo.text().strip(),
            "anio":        self.f_anio.text().strip(),
            "nro_cuadro":  self.f_cuadro.text().strip(),
            "nro_motor":   self.f_motor.text().strip(),
            "estado":      self.f_estado.currentText(),
        }
        if filters["estado"] == "Todos":
            filters["estado"] = None

        filters = {k: v for k, v in filters.items() if v}
        df = ux.load_vehiculos(filters)
        self.tabla.set_dataframe(df)

    def on_click_perfil(self, row: int):
        vid = self.tabla.model.get_row_id(row)
        if vid is None:
            return
        detalle = VehiculoDetalle(vehiculo_id=vid, notify=self._notify, navigate=self._navigate, navigate_back=self._navigate_back)
        self._navigate(detalle)

    def open_new(self):
        editor = VehiculoEditar(vehiculo_id=None, notify=self._notify, navigate=self._navigate,
                                navigate_back=self._navigate_back, on_saved=self._after_new_saved)
        self._navigate(editor)

    def _after_new_saved(self, vid: int):
        self.load_data()
