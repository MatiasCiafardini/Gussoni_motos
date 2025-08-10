from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableView
from .vehiculos_model import VehiculosModel
from .vehiculos_delegate import PerfilButtonDelegate

class VehiculosTabla(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = VehiculosModel()
        self.view = QTableView(self)
        self.view.setModel(self.model)
        self.view.setSelectionBehavior(QTableView.SelectRows)
        self.view.setSelectionMode(QTableView.SingleSelection)
        self.view.setAlternatingRowColors(True)
        self.view.horizontalHeader().setStretchLastSection(True)

        self.delegate = PerfilButtonDelegate(self.view)
        self.view.setItemDelegateForColumn(self.model.columnCount()-1, self.delegate)

        lay = QVBoxLayout(self)
        lay.addWidget(self.view)

    def set_dataframe(self, df):
        self.model.setDataFrame(df)
        self.view.setItemDelegateForColumn(self.model.columnCount()-1, self.delegate)
        self.view.resizeColumnsToContents()
