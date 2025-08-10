from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
import pandas as pd

class ClientesModel(QAbstractTableModel):
    def __init__(self, df: pd.DataFrame | None = None, parent=None):
        super().__init__(parent)
        self._df = df if df is not None else pd.DataFrame(columns=["id","nombre","dni","email","telefono","direccion"])
        self._columns = list(self._df.columns) + ["perfil"]  # columna de acción

    def setDataFrame(self, df: pd.DataFrame):
        self.beginResetModel()
        self._df = df.copy()
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
        col = index.column()
        colname = self._columns[col]
        if role == Qt.DisplayRole:
            if colname == "perfil":
                return "Perfil"
            val = self._df.iloc[row].get(colname)
            return "" if pd.isna(val) else str(val)
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._columns[section].capitalize()
        return super().headerData(section, orientation, role)

    def get_row_id(self, row: int) -> int | None:
        try:
            return int(self._df.iloc[row]["id"])
        except Exception:
            return None
