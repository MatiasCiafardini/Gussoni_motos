from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
import pandas as pd

class ClientesModel(QAbstractTableModel):
    def __init__(self, df: pd.DataFrame | None = None, parent=None):
        super().__init__(parent)
        base_cols = ["id", "nombre", "dni", "email", "telefono", "direccion", "estado"]
        if df is None:
            self._df = pd.DataFrame(columns=base_cols)
        else:
            for c in base_cols:
                if c not in df.columns:
                    df[c] = ""
            self._df = df[base_cols].copy()
        self._columns = list(self._df.columns) + ["perfil"]

    def setDataFrame(self, df: pd.DataFrame):
        self.beginResetModel()
        base_cols = ["id", "nombre", "dni", "email", "telefono", "direccion", "estado"]
        for c in base_cols:
            if c not in df.columns:
                df[c] = ""
        self._df = df[base_cols].copy()
        self._columns = list(self._df.columns) + ["perfil"]
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self._df)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self._columns)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        row = index.row()
        colname = self._columns[index.column()]

        if role == Qt.DisplayRole:
            if colname == "perfil":
                return ""  # sin texto; ahí va el botón
            val = self._df.iloc[row].get(colname)
            return "" if pd.isna(val) else str(val)
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            colname = self._columns[section]
            if colname == "perfil":
                return "Perfil"  # título visible
            pretty = {
                "id": "ID",
                "nombre": "Nombre",
                "dni": "DNI",
                "email": "Email",
                "telefono": "Teléfono",
                "direccion": "Dirección",
                "estado": "Estado",
            }
            return pretty.get(colname, colname.capitalize())
        # Por si algún tema intenta poner iconos en headers:
        if role == Qt.DecorationRole and orientation == Qt.Horizontal:
            return None
        return super().headerData(section, orientation, role)

    def get_row_id(self, row: int) -> int | None:
        try:
            return int(self._df.iloc[row]["id"])
        except Exception:
            return None
