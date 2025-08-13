from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QComboBox
from src.data import util_excel as ux
from src.ui.notify import NotifyPopup

class ProveedorEditar(QWidget):
    def __init__(self, parent=None, proveedor_id: int | None = None, notify=None, navigate=None, navigate_back=None, on_saved=None, back_steps_after_delete:int=2):
        super().__init__()
        self._id = proveedor_id
        self._notify = notify if callable(notify) else (lambda msg, tipo="info": self._show_notify(msg, tipo))
        self._navigate = navigate
        self._navigate_back = navigate_back
        self._on_saved = on_saved

        layout = QVBoxLayout(self)

        # Formulario
        form = QFormLayout()
        self.txt_nombre = QLineEdit()
        self.txt_cuit = QLineEdit()
        self.txt_email = QLineEdit()
        self.txt_telefono = QLineEdit()
        self.txt_direccion = QLineEdit()

        form.addRow("Nombre:", self.txt_nombre)
        form.addRow("CUIT:", self.txt_cuit)
        form.addRow("Email:", self.txt_email)
        form.addRow("Teléfono:", self.txt_telefono)
        form.addRow("Dirección:", self.txt_direccion)

        # Campo Estado: solo en edición
        self.cmb_estado = None
        if self._id is not None:
            self.cmb_estado = QComboBox()
            self._cargar_estados_existentes()
            form.addRow("Estado:", self.cmb_estado)

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
        popup = NotifyPopup(text, tipo, parent=self.window())
        popup.show_centered()

    def _cargar_estados_existentes(self):
        """Carga lista única de estados desde proveedores.xlsx."""
        df = ux.load_proveedores()
        estados = sorted(set(df["estado"].dropna().astype(str).str.strip()))
        estados = [e for e in estados if e]  # eliminar vacíos
        if "Activo" not in estados:
            estados.insert(0, "Activo")
        self.cmb_estado.addItems(estados)

    def _cargar_datos(self):
        """Carga datos del proveedor en el formulario."""
        data = ux.get_proveedor_by_id(self._id)
        if data:
            self.txt_nombre.setText(str(data.get("nombre", "")))
            self.txt_cuit.setText(str(data.get("cuit", "")))
            self.txt_email.setText(str(data.get("email", "")))
            self.txt_telefono.setText(str(data.get("telefono", "")))
            self.txt_direccion.setText(str(data.get("direccion", "")))
            if self.cmb_estado:
                estado_actual = str(data.get("estado", "Activo")).strip()
                idx = self.cmb_estado.findText(estado_actual)
                if idx >= 0:
                    self.cmb_estado.setCurrentIndex(idx)

    def _validar(self):
        """Valida los campos antes de guardar."""
        if not self.txt_nombre.text().strip():
            self._notify("El nombre es obligatorio", "error")
            return False
        if not self.txt_cuit.text().strip():
            self._notify("El CUIT es obligatorio", "error")
            return False
        return True

    def _guardar(self):
        """Guarda o actualiza el proveedor."""
        if not self._validar():
            return

        payload = {
            "id": self._id,
            "nombre": self.txt_nombre.text().strip(),
            "cuit": self.txt_cuit.text().strip(),
            "email": self.txt_email.text().strip(),
            "telefono": self.txt_telefono.text().strip(),
            "direccion": self.txt_direccion.text().strip(),
            "estado": self.cmb_estado.currentText().strip() if self._id is not None else "Activo",
        }

        pid = ux.upsert_proveedor(payload)

        self._notify("Proveedor guardado correctamente", "success")
        if self._on_saved:
            self._on_saved(pid)
        self._navigate_back()
