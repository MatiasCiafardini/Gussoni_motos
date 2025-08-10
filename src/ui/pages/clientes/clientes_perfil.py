from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QMessageBox, QLabel
from src.data import util_excel as ux

class ClientePerfil(QDialog):
    def __init__(self, parent=None, cliente_id: int | None = None):
        super().__init__(parent)
        self.setWindowTitle("Perfil de Cliente")
        self.setModal(True)
        self._id = cliente_id

        lay = QVBoxLayout(self)
        title = QLabel("Cliente")
        title.setStyleSheet("font-size:16px; font-weight:600;")
        lay.addWidget(title)

        form = QFormLayout()
        self.nombre = QLineEdit()
        self.dni = QLineEdit()
        self.email = QLineEdit()
        self.telefono = QLineEdit()
        self.direccion = QLineEdit()
        form.addRow("Nombre:", self.nombre)
        form.addRow("DNI:", self.dni)
        form.addRow("Email:", self.email)
        form.addRow("Teléfono:", self.telefono)
        form.addRow("Dirección:", self.direccion)
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

        if cliente_id is not None:
            self._load(cliente_id)
        else:
            self.btn_eliminar.setEnabled(False)

    def _load(self, cid: int):
        data = ux.get_cliente_by_id(cid)
        if not data:
            QMessageBox.warning(self, "Aviso", "Cliente no encontrado.")
            self.reject()
            return
        self._id = cid
        self.nombre.setText(str(data.get("nombre","")))
        self.dni.setText(str(data.get("dni","")))
        self.email.setText(str(data.get("email","")))
        self.telefono.setText(str(data.get("telefono","")))
        self.direccion.setText(str(data.get("direccion","")))

    def on_guardar(self):
        payload = {
            "id": self._id,
            "nombre": self.nombre.text().strip(),
            "dni": self.dni.text().strip(),
            "email": self.email.text().strip(),
            "telefono": self.telefono.text().strip(),
            "direccion": self.direccion.text().strip(),
        }
        cid = ux.save_cliente(payload)
        self._id = cid
        QMessageBox.information(self, "OK", "Guardado correctamente.")
        self.accept()

    def on_eliminar(self):
        if self._id is None:
            return
        ok = ux.delete_cliente(self._id)
        if ok:
            QMessageBox.information(self, "OK", "Cliente eliminado.")
            self.accept()
        else:
            QMessageBox.warning(self, "Aviso", "No se pudo eliminar.")
