from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFormLayout, QLineEdit,
    QPushButton, QHBoxLayout, QComboBox
)
from src.data import util_excel as ux

class ClienteEditar(QWidget):
    """
    Página interna para crear/editar un cliente.
    - Campo 'Estado' (Activo/Inactivo).
    - Abajo al centro: 'Guardar' (izquierda) y 'Volver' (derecha).
    """
    def __init__(self, parent=None, cliente_id: int | None = None, notify=None, navigate=None, navigate_back=None, on_saved=None, back_steps_after_delete:int=2):
        super().__init__(parent)
        self._id = cliente_id
        self._notify = notify or (lambda msg: None)
        self._navigate = navigate or (lambda w: None)
        self._navigate_back = navigate_back or (lambda: None)
        self._on_saved = on_saved or (lambda cid: None)
        self._back_steps_after_delete = max(1, int(back_steps_after_delete))

        root = QVBoxLayout(self)

        # Header solo con título
        hdr = QHBoxLayout()
        title = QLabel("Editar Cliente" if cliente_id else "Nuevo Cliente")
        title.setStyleSheet("font-size:16px; font-weight:600;")
        hdr.addWidget(title); hdr.addStretch(1)
        root.addLayout(hdr)

        # Formulario
        form = QFormLayout()
        self.nombre = QLineEdit()
        self.dni = QLineEdit()
        self.email = QLineEdit()
        self.telefono = QLineEdit()
        self.direccion = QLineEdit()
        self.estado = QComboBox(); self.estado.addItems(["Activo", "Inactivo"])
        form.addRow("Nombre:", self.nombre)
        form.addRow("DNI:", self.dni)
        form.addRow("Email:", self.email)
        form.addRow("Teléfono:", self.telefono)
        form.addRow("Dirección:", self.direccion)
        form.addRow("Estado:", self.estado)
        root.addLayout(form)

        # --- Abajo centrado: Guardar (izq) y Volver (der) ---
        root.addStretch(1)
        bottom = QHBoxLayout()
        self.btn_guardar = QPushButton("Guardar"); self.btn_guardar.setObjectName("Primary")
        self.btn_volver = QPushButton("Volver")
        bottom.addStretch(1)
        bottom.addWidget(self.btn_guardar)
        bottom.addWidget(self.btn_volver)
        bottom.addStretch(1)
        root.addLayout(bottom)

        # Eventos
        self.btn_volver.clicked.connect(self._navigate_back)
        self.btn_guardar.clicked.connect(self._on_guardar)

        if cliente_id is not None:
            self._load(cliente_id)
        else:
            # nuevo cliente -> estado por defecto Activo
            self.estado.setCurrentText("Activo")

    def _load(self, cid: int):
        data = ux.get_cliente_by_id(cid)
        if not data:
            self._notify("Cliente no encontrado.")
            self.btn_guardar.setEnabled(False)
            return
        self._id = cid
        self.nombre.setText(str(data.get("nombre","")))
        self.dni.setText(str(data.get("dni","")))
        self.email.setText(str(data.get("email","")))
        self.telefono.setText(str(data.get("telefono","")))
        self.direccion.setText(str(data.get("direccion","")))
        self.estado.setCurrentText(str(data.get("estado","Activo")))

    def _on_guardar(self):
        payload = {
            "id": self._id,
            "nombre": self.nombre.text().strip(),
            "dni": self.dni.text().strip(),
            "email": self.email.text().strip(),
            "telefono": self.telefono.text().strip(),
            "direccion": self.direccion.text().strip(),
            "estado": self.estado.currentText(),
        }
        cid = ux.save_cliente(payload)
        self._id = cid
        self._notify("Guardado correctamente.")
        self._on_saved(cid)
        self._navigate_back()
