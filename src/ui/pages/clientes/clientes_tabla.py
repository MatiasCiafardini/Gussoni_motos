from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableView, QAbstractItemView
from .clientes_model import ClientesModel
from .clientes_delegate import PerfilButtonDelegate

class ClientesTabla(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = ClientesModel()
        self.view = QTableView(self)
        self.view.setModel(self.model)
        self.view.setSelectionBehavior(QTableView.SelectRows)
        self.view.setSelectionMode(QTableView.SingleSelection)
        self.view.setAlternatingRowColors(True)
        self.view.horizontalHeader().setStretchLastSection(True)

        # Evitar que la vista entre en modo edición (así no intenta crear editores)
        self.view.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Delegate para botón Perfil (última columna)
        self.delegate = PerfilButtonDelegate(self.view)
        self.view.setItemDelegateForColumn(self.model.columnCount()-1, self.delegate)

        lay = QVBoxLayout(self)
        lay.addWidget(self.view)

    def set_dataframe(self, df):
        self.model.setDataFrame(df)
        # re-asignar delegate a la última columna por si cambió
        self.view.setItemDelegateForColumn(self.model.columnCount()-1, self.delegate)
        self.view.resizeColumnsToContents()
