from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
import pandas as pd

class ProveedoresModel(QAbstractTableModel):
    """
    Columnas internas:
    - id (entero)
    - nombre
    - cuit
    - email
    - telefono
    - direccion
    - estado
    - perfil (columna de acción)
    """
    BASE_COLS = ["id", "nombre", "cuit", "email", "telefono", "direccion", "estado"]

    def __init__(self, df: pd.DataFrame | None = None, parent=None):
        super().__init__(parent)
        if df is None:
            self._df = pd.DataFrame(columns=self.BASE_COLS)
        else:
            d = df.copy()
            # Compatibilidad: si viene 'proveedor_id', lo mapeamos a 'id'
            if "proveedor_id" in d.columns and "id" not in d.columns:
                d = d.rename(columns={"proveedor_id": "id"})
            for c in self.BASE_COLS:
                if c not in d.columns:
                    d[c] = ""
            self._df = d[self.BASE_COLS]
        self._columns = list(self._df.columns) + ["perfil"]

    # util
    def columns(self):
        return list(self._columns)

    def column_index(self, name: str) -> int:
        try:
            return self._columns.index(name)
        except ValueError:
            return -1

    def setDataFrame(self, df: pd.DataFrame):
        self.beginResetModel()
        d = df.copy()
        if "proveedor_id" in d.columns and "id" not in d.columns:
            d = d.rename(columns={"proveedor_id": "id"})
        for c in self.BASE_COLS:
            if c not in d.columns:
                d[c] = ""
        self._df = d[self.BASE_COLS]
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
                return ""  # botón se coloca con setIndexWidget
            val = self._df.iloc[row].get(colname)
            if pd.isna(val):
                return ""
            if colname == "id":
                try:
                    return str(int(val))
                except Exception:
                    return str(val)
            return str(val)

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            colname = self._columns[section]
            pretty = {
                "id": "ID",
                "nombre": "Nombre",
                "cuit": "CUIT",
                "email": "Email",
                "telefono": "Teléfono",
                "direccion": "Dirección",
                "estado": "Estado",
                "perfil": "Perfil",
            }
            return pretty.get(colname, colname.capitalize())
        return super().headerData(section, orientation, role)

    def get_row_id(self, row: int) -> int | None:
        try:
            return int(self._df.iloc[row]["id"])
        except Exception:
            return None
