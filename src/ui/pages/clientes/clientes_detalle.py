from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFormLayout, QPushButton,
    QHBoxLayout, QGroupBox, QTableView
)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
import pandas as pd
from src.data import util_excel as ux
from src.data.settings import DATA_DIR
from .clientes_editar import ClienteEditar


class PandasModel(QAbstractTableModel):
    def __init__(self, df: pd.DataFrame | None = None, parent=None):
        super().__init__(parent)
        self._df = df.copy() if df is not None else pd.DataFrame()

    def setDataFrame(self, df: pd.DataFrame):
        self.beginResetModel(); self._df = df.copy(); self.endResetModel()

    def rowCount(self, parent=QModelIndex()): return 0 if parent.isValid() else len(self._df)
    def columnCount(self, parent=QModelIndex()): return 0 if parent.isValid() else len(self._df.columns)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return (str(self._df.columns[section]).capitalize() if orientation == Qt.Horizontal else str(section + 1))
        return None

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid(): return None
        if role == Qt.DisplayRole:
            val = self._df.iat[index.row(), index.column()]
            return "" if pd.isna(val) else str(val)
        return None


class ClienteDetalle(QWidget):
    """Perfil del cliente. 'Editar' debajo de Datos (derecha). 'Volver' abajo centrado."""
    def __init__(self, parent=None, cliente_id: int | None = None, notify=None, navigate=None, navigate_back=None):
        super().__init__(parent)
        self._id = cliente_id
        self._notify = notify or (lambda msg: None)
        self._navigate = navigate or (lambda w: None)
        self._navigate_back = navigate_back or (lambda: None)

        root = QVBoxLayout(self)

        # Título
        title = QLabel("Perfil del Cliente")
        title.setStyleSheet("font-size:16px; font-weight:600;")
        root.addWidget(title)

        # --- Datos del cliente ---
        self.gb_datos = QGroupBox("Datos")
        form = QFormLayout()
        self.lbl_id = QLabel(""); self.lbl_nombre = QLabel(""); self.lbl_dni = QLabel("")
        self.lbl_email = QLabel(""); self.lbl_tel = QLabel(""); self.lbl_dir = QLabel(""); self.lbl_estado = QLabel("")
        for w in [self.lbl_id, self.lbl_nombre, self.lbl_dni, self.lbl_email, self.lbl_tel, self.lbl_dir, self.lbl_estado]:
            w.setTextInteractionFlags(Qt.TextSelectableByMouse)
        form.addRow("ID:", self.lbl_id)
        form.addRow("Nombre:", self.lbl_nombre)
        form.addRow("DNI:", self.lbl_dni)
        form.addRow("Email:", self.lbl_email)
        form.addRow("Teléfono:", self.lbl_tel)
        form.addRow("Dirección:", self.lbl_dir)
        form.addRow("Estado:", self.lbl_estado)
        self.gb_datos.setLayout(form)
        root.addWidget(self.gb_datos)

        # Botón Editar debajo de la caja de Datos, alineado a la derecha
        row_edit = QHBoxLayout()
        self.btn_editar = QPushButton("Editar"); self.btn_editar.setObjectName("Primary")
        row_edit.addStretch(1); row_edit.addWidget(self.btn_editar)
        root.addLayout(row_edit)

        # --- Vehículos comprados ---
        self.gb_vehiculos = QGroupBox("Vehículos comprados")
        vlay = QVBoxLayout()
        self.tbl_vehiculos = QTableView(); self.tbl_vehiculos.setAlternatingRowColors(True)
        self.tbl_vehiculos.horizontalHeader().setStretchLastSection(True)
        self.model_veh = PandasModel(pd.DataFrame(columns=["id","marca","modelo","anio","vin","precio","estado"]))
        self.tbl_vehiculos.setModel(self.model_veh)
        vlay.addWidget(self.tbl_vehiculos); self.gb_vehiculos.setLayout(vlay)
        root.addWidget(self.gb_vehiculos)

        # --- Facturas del cliente ---
        self.gb_facturas = QGroupBox("Facturas")
        flay = QVBoxLayout()
        self.tbl_facturas = QTableView(); self.tbl_facturas.setAlternatingRowColors(True)
        self.tbl_facturas.horizontalHeader().setStretchLastSection(True)
        self.model_fac = PandasModel(pd.DataFrame(columns=["id","fecha","vehiculo_id","total","estado"]))
        self.tbl_facturas.setModel(self.model_fac)
        flay.addWidget(self.tbl_facturas); self.gb_facturas.setLayout(flay)
        root.addWidget(self.gb_facturas)

        # ---- Empujar el botón Volver hacia abajo (centrado) ----
        root.addStretch(1)
        bottom = QHBoxLayout()
        self.btn_volver = QPushButton("Volver")
        bottom.addStretch(1); bottom.addWidget(self.btn_volver); bottom.addStretch(1)
        root.addLayout(bottom)

        # Eventos
        self.btn_volver.clicked.connect(self._navigate_back)
        self.btn_editar.clicked.connect(self._on_editar)

        # Cargar datos
        if cliente_id is not None: self._load(cliente_id)
        else: self.btn_editar.setEnabled(False)

    def _on_editar(self):
        # Navega a la página de edición interna. Al guardar, se recarga este perfil.
        editor = ClienteEditar(
            cliente_id=self._id,
            notify=self._notify,
            navigate=self._navigate,
            navigate_back=self._navigate_back,
            on_saved=self._after_edit_saved,
            back_steps_after_delete=2
        )
        self._navigate(editor)

    def _after_edit_saved(self, cid: int):
        self._load(cid)

    def _load(self, cid: int):
        data = ux.get_cliente_by_id(cid)
        if not data:
            self._notify("Cliente no encontrado."); self.btn_editar.setEnabled(False); return
        self._id = cid
        self.lbl_id.setText(str(data.get("id",""))); self.lbl_nombre.setText(str(data.get("nombre","")))
        self.lbl_dni.setText(str(data.get("dni",""))); self.lbl_email.setText(str(data.get("email","")))
        self.lbl_tel.setText(str(data.get("telefono",""))); self.lbl_dir.setText(str(data.get("direccion","")))
        self.lbl_estado.setText(str(data.get("estado","Activo")))

        # Vehículos comprados por el cliente
        dfv = ux.load_vehiculos({})
        dfv_norm = dfv.copy()
        dfv_norm["cliente_id_norm"] = dfv_norm["cliente_id"].fillna(-1).astype(int)
        dfv_cli = dfv_norm[dfv_norm["cliente_id_norm"] == int(cid)][["id","marca","modelo","anio","vin","precio","estado"]]
        self.model_veh.setDataFrame(dfv_cli.reset_index(drop=True))

        # Facturas (si existe data/facturas.xlsx)
        fac_path = DATA_DIR / "facturas.xlsx"
        if fac_path.exists():
            try:
                dff = pd.read_excel(fac_path)
                if "cliente_id" in dff.columns:
                    dff["cliente_id_norm"] = dff["cliente_id"].fillna(-1).astype(int)
                    dff = dff[dff["cliente_id_norm"] == int(cid)]
                cols = [c for c in ["id","fecha","vehiculo_id","total","estado"] if c in dff.columns]
                if not cols: cols = dff.columns.tolist()
                self.model_fac.setDataFrame(dff[cols].reset_index(drop=True))
            except Exception:
                self.model_fac.setDataFrame(pd.DataFrame(columns=["id","fecha","vehiculo_id","total","estado"]))
        else:
            self.model_fac.setDataFrame(pd.DataFrame(columns=["id","fecha","vehiculo_id","total","estado"]))
