from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
import pandas as pd

class VehiculosModel(QAbstractTableModel):
    def __init__(self, df: pd.DataFrame | None = None, parent=None):
        super().__init__(parent)
        base_cols = ["id","marca","modelo","anio","vin","precio","estado"]
        if df is None:
            self._df = pd.DataFrame(columns=base_cols)
        else:
            for c in base_cols:
                if c not in df.columns:
                    df[c] = "" if c not in ("anio","precio") else None
            self._df = df[base_cols].copy()
        self._columns = list(self._df.columns) + ["perfil"]

    def setDataFrame(self, df: pd.DataFrame):
        self.beginResetModel()
        base_cols = ["id","marca","modelo","anio","vin","precio","estado"]
        for c in base_cols:
            if c not in df.columns:
                df[c] = "" if c not in ("anio","precio") else None
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
                return ""  # sin texto; se coloca un botón en la tabla
            val = self._df.iloc[row].get(colname)
            return "" if pd.isna(val) else str(val)
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            colname = self._columns[section]
            if colname == "perfil":
                return "Perfil"
            pretty = {
                "id": "ID",
                "marca": "Marca",
                "modelo": "Modelo",
                "anio": "Año",
                "vin": "VIN",
                "precio": "Precio",
                "estado": "Estado",
            }
            return pretty.get(colname, colname.capitalize())
        if role == Qt.DecorationRole and orientation == Qt.Horizontal:
            return None
        return super().headerData(section, orientation, role)

    def get_row_id(self, row: int) -> int | None:
        try:
            return int(self._df.iloc[row]["id"])
        except Exception:
            return None
