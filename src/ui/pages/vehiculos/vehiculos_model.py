from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
import pandas as pd

class VehiculosModel(QAbstractTableModel):
    """
    Columnas (en este orden):
    - id (oculta en la vista, solo interna)
    - marca
    - modelo
    - anio (int)
    - nro_certificado
    - nro_dnrpa
    - nro_cuadro
    - nro_motor
    - precio (moneda $)
    - remito
    - factura
    - estado
    - perfil (acción con 🔍)
    """
    BASE_COLS = [
        "id", "marca", "modelo", "anio",
        "nro_certificado", "nro_dnrpa", "nro_cuadro", "nro_motor",
        "precio", "remito", "factura", "estado"
    ]

    # 👉 columnas alineadas a la derecha
    RIGHT_ALIGNED = {"anio", "precio"}

    def __init__(self, df: pd.DataFrame | None = None, parent=None):
        super().__init__(parent)
        if df is None:
            self._df = pd.DataFrame(columns=self.BASE_COLS)
        else:
            df = df.copy()
            for c in self.BASE_COLS:
                if c not in df.columns:
                    df[c] = ""
            self._df = df[self.BASE_COLS]
        self._columns = list(self._df.columns) + ["perfil"]

    # utilidades
    def columns(self):
        return list(self._columns)

    def column_index(self, name: str) -> int:
        try:
            return self._columns.index(name)
        except ValueError:
            return -1

    def setDataFrame(self, df: pd.DataFrame):
        self.beginResetModel()
        df = df.copy()
        for c in self.BASE_COLS:
            if c not in df.columns:
                df[c] = ""
        self._df = df[self.BASE_COLS]
        self._columns = list(self._df.columns) + ["perfil"]
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self._df)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self._columns)

    def _format_currency(self, val):
        # Devuelve "$ 1.234,56" si es numérico
        try:
            num = float(val)
            s = f"{num:,.2f}"              # 1,234.56
            s = s.replace(",", "X").replace(".", ",").replace("X", ".")
            return f"$ {s}"
        except Exception:
            text = str(val)
            return text if text.startswith("$") else (f"$ {text}" if text else "")

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        row = index.row()
        colname = self._columns[index.column()]

        if role == Qt.DisplayRole:
            if colname == "perfil":
                return ""  # el botón se coloca con setIndexWidget
            val = self._df.iloc[row].get(colname)
            if pd.isna(val):
                return ""
            if colname == "anio":
                try:
                    return str(int(val))
                except Exception:
                    return str(val)
            if colname == "precio":
                return self._format_currency(val)
            return str(val)

        if role == Qt.TextAlignmentRole:
            # Alineación: derecha para año y precio; resto izquierda
            if colname in self.RIGHT_ALIGNED:
                return int(Qt.AlignRight | Qt.AlignVCenter)
            else:
                return int(Qt.AlignLeft | Qt.AlignVCenter)

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            colname = self._columns[section]
            pretty = {
                "id": "ID",
                "marca": "Marca",
                "modelo": "MODELO",
                "anio": "Año",
                "nro_certificado": "Nº CERTIFICADO",
                "nro_dnrpa": "Nº DNRPA",
                "nro_cuadro": "Nº CUADRO",
                "nro_motor": "Nº MOTOR",
                "precio": "Precio",
                "remito": "REMITO",
                "factura": "FACTURA",
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
