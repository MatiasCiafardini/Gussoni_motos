from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFormLayout, QPushButton, QHBoxLayout, QGroupBox
from PySide6.QtCore import Qt
from src.data import util_excel as ux
from .proveedores_editar import ProveedorEditar


class ProveedorDetalle(QWidget):
    """Perfil interno del proveedor con botón Editar y Volver."""
    def __init__(self, parent=None, proveedor_id: int | None = None, notify=None, navigate=None, navigate_back=None):
        super().__init__(parent)
        self._id = proveedor_id
        self._notify = notify or (lambda msg, tipo="info": None)
        self._navigate = navigate or (lambda w: None)
        self._navigate_back = navigate_back or (lambda: None)

        root = QVBoxLayout(self)

        title = QLabel("Perfil del proveedor")
        title.setStyleSheet("font-size:16px; font-weight:600;")
        root.addWidget(title)

        # Datos
        self.gb_datos = QGroupBox("")
        form = QFormLayout()
        self.lbl_nombre = QLabel("")
        self.lbl_cuit = QLabel("")
        self.lbl_email = QLabel("")
        self.lbl_telefono = QLabel("")
        self.lbl_direccion = QLabel("")
        self.lbl_estado = QLabel("")
        for w in [self.lbl_nombre, self.lbl_cuit, self.lbl_email, self.lbl_telefono, self.lbl_direccion, self.lbl_estado]:
            w.setTextInteractionFlags(Qt.TextSelectableByMouse)

        form.addRow(QLabel("Nombre:"), self.lbl_nombre)
        form.addRow(QLabel("CUIT:"), self.lbl_cuit)
        form.addRow(QLabel("Email:"), self.lbl_email)
        form.addRow(QLabel("Teléfono:"), self.lbl_telefono)
        form.addRow(QLabel("Dirección:"), self.lbl_direccion)
        form.addRow(QLabel("Estado:"), self.lbl_estado)
        self.gb_datos.setLayout(form)
        root.addWidget(self.gb_datos)

        # Botón Editar
        row_edit = QHBoxLayout()
        self.btn_editar = QPushButton("Editar")
        self.btn_editar.setObjectName("Primary")
        row_edit.addStretch(1)
        row_edit.addWidget(self.btn_editar)
        root.addLayout(row_edit)

        # Botón Volver
        root.addStretch(1)
        bottom = QHBoxLayout()
        self.btn_volver = QPushButton("Volver")
        bottom.addStretch(1)
        bottom.addWidget(self.btn_volver)
        bottom.addStretch(1)
        root.addLayout(bottom)

        # Eventos
        self.btn_volver.clicked.connect(self._navigate_back)
        self.btn_editar.clicked.connect(self._on_editar)

        if proveedor_id is not None:
            self._load(proveedor_id)
        else:
            self.btn_editar.setEnabled(False)

    def _on_editar(self):
        editor = ProveedorEditar(
            proveedor_id=self._id,
            notify=self._notify,
            navigate=self._navigate,
            navigate_back=self._navigate_back,
            on_saved=self._after_edit_saved
        )
        self._navigate(editor)

    def _after_edit_saved(self, pid: int):
        self._load(pid)

    def _load(self, pid: int):
        data = ux.get_proveedor_by_id(pid)
        if not data:
            self._notify("Proveedor no encontrado", "error")
            self.btn_editar.setEnabled(False)
            return

        self.lbl_nombre.setText(str(data.get("nombre", "")))
        self.lbl_cuit.setText(str(data.get("cuit", "")))
        self.lbl_email.setText(str(data.get("email", "")))
        self.lbl_telefono.setText(str(data.get("telefono", "")))
        self.lbl_direccion.setText(str(data.get("direccion", "")))
        self.lbl_estado.setText(str(data.get("estado", "Activo")))
