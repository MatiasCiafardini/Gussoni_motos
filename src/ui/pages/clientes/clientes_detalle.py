from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFrame, QHBoxLayout, QFormLayout
)
from PySide6.QtCore import Qt
from src.data import util_excel as ux
from .clientes_editar import ClienteEditar

class ClienteDetalle(QWidget):
    """
    Perfil del cliente (compacto):
    - QFormLayout (label–valor por fila), sin proporciones 1/3 ni columnas extra.
    - Botón Editar abajo a la derecha del card.
    - Botón Volver centrado abajo.
    """
    def __init__(self, cliente_id: int, notify=None, navigate=None, navigate_back=None):
        super().__init__()
        self._id = cliente_id
        self._notify = notify or (lambda m: None)
        self._navigate = navigate or (lambda w: None)
        self._navigate_back = navigate_back or (lambda: None)

        # Root
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        # Card
        self.card = QFrame(self)
        self.card.setObjectName("Card")
        card_lay = QVBoxLayout(self.card)
        card_lay.setContentsMargins(10, 10, 10, 10)
        card_lay.setSpacing(6)

        title = QLabel("Perfil del cliente")
        title.setStyleSheet("font-size: 16px; font-weight: 600; margin: 0; padding: 0;")
        card_lay.addWidget(title)

        # --- Form (sin 1/3) ---
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        form.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        form.setSpacing(6)

        def vlabel():
            lab = QLabel("")
            lab.setTextInteractionFlags(Qt.TextSelectableByMouse)
            lab.setWordWrap(True)
            return lab

        self._vals = {
            "nombre": vlabel(),
            "dni": vlabel(),
            "email": vlabel(),
            "telefono": vlabel(),
            "direccion": vlabel(),
            "estado": vlabel(),
        }

        form.addRow(QLabel("Nombre:"),    self._vals["nombre"])
        form.addRow(QLabel("DNI:"),       self._vals["dni"])
        form.addRow(QLabel("Email:"),     self._vals["email"])
        form.addRow(QLabel("Teléfono:"),  self._vals["telefono"])
        form.addRow(QLabel("Dirección:"), self._vals["direccion"])
        form.addRow(QLabel("Estado:"),    self._vals["estado"])

        card_lay.addLayout(form)

        # Acciones del card
        actions = QHBoxLayout()
        actions.setContentsMargins(0, 6, 0, 0)
        actions.addStretch(1)
        self.btn_editar = QPushButton("Editar")
        self.btn_editar.setObjectName("Primary")
        actions.addWidget(self.btn_editar)
        card_lay.addLayout(actions)

        root.addWidget(self.card)

        # Barra inferior (Volver centrado)
        bottom = QHBoxLayout()
        bottom.setContentsMargins(0, 6, 0, 0)
        bottom.addStretch(1)
        self.btn_volver = QPushButton("Volver")
        bottom.addWidget(self.btn_volver)
        bottom.addStretch(1)
        root.addLayout(bottom)

        # Conexiones
        self.btn_volver.clicked.connect(self._navigate_back)
        self.btn_editar.clicked.connect(self._open_editor)

        # Cargar datos
        self._load()

    # --------- Datos ---------
    def _load(self):
        try:
            data = ux.get_cliente_by_id(self._id) if hasattr(ux, "get_cliente_by_id") else {}
            if not data:
                df = ux.load_clientes({})
                row = df.loc[df["id"].astype(str) == str(self._id)]
                data = {} if row.empty else row.iloc[0].to_dict()
            if not data:
                self._notify("No se encontró el cliente.")
                return

            self._vals["nombre"].setText(str(data.get("nombre", "")))
            self._vals["dni"].setText(str(data.get("dni", "")))
            self._vals["email"].setText(str(data.get("email", "")))
            self._vals["telefono"].setText(str(data.get("telefono", "")))
            self._vals["direccion"].setText(str(data.get("direccion", "")))
            self._vals["estado"].setText(str(data.get("estado") or "Activo"))

        except Exception as e:
            self._notify(f"Error al cargar el cliente: {e}")

    def _open_editor(self):
        editor = ClienteEditar(
            cliente_id=self._id,
            notify=self._notify,
            navigate=self._navigate,
            navigate_back=self._navigate_back,
            on_saved=self._after_saved
        )
        self._navigate(editor)

    def _after_saved(self, cid: int):
        self._load()
        self._notify("Cliente actualizado.")
