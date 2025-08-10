from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableView, QAbstractItemView, QPushButton,
    QHBoxLayout, QHeaderView
)
from PySide6.QtCore import Signal, Qt
from .vehiculos_model import VehiculosModel

class VehiculosTabla(QWidget):
    perfil_clicked = Signal(int)  # row

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = VehiculosModel()

        self.view = QTableView(self)
        self.view.setModel(self.model)
        self.view.setSelectionBehavior(QTableView.SelectRows)
        self.view.setSelectionMode(QTableView.SingleSelection)
        self.view.setAlternatingRowColors(True)
        self.view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.view.horizontalHeader().setStretchLastSection(False)

        lay = QVBoxLayout(self)
        lay.addWidget(self.view)

    def set_dataframe(self, df):
        self.model.setDataFrame(df)
        self._configure_columns()
        self._install_perfil_buttons()

    # Helpers
    def _make_perfil_button(self):
        btn = QPushButton("🔍", self.view)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setToolTip("Ver perfil")
        btn.setFixedSize(30, 30)
        btn.setStyleSheet("QPushButton { padding: 0; font-size: 14px; border-radius: 6px; }")
        btn.setFocusPolicy(Qt.NoFocus)
        return btn

    def _perfil_col_width(self) -> int:
        tmp = self._make_perfil_button()
        return tmp.sizeHint().width() + 12

    def _configure_columns(self):
        header: QHeaderView = self.view.horizontalHeader()
        header.setStretchLastSection(False)
        header.setMinimumSectionSize(100)  # “Nº ...” necesitan algo más de ancho

        col_id = self.model.column_index("id")
        col_perfil = self.model.column_index("perfil")

        for c in range(self.model.columnCount()):
            if c == col_perfil:
                header.setSectionResizeMode(c, QHeaderView.Fixed)
                self.view.setColumnWidth(c, max(42, self._perfil_col_width()))
            elif c == col_id and col_id >= 0:
                # ocultar ID interno
                self.view.setColumnHidden(c, True)
            else:
                header.setSectionResizeMode(c, QHeaderView.Stretch)

        vh = self.view.verticalHeader()
        vh.setDefaultSectionSize(max(vh.defaultSectionSize(), 36))

    def _install_perfil_buttons(self):
        col_perfil = self.model.column_index("perfil")
        if col_perfil < 0 or self.model.rowCount() == 0:
            return
        for row in range(self.model.rowCount()):
            index = self.model.index(row, col_perfil)
            container = QWidget(self.view)
            hbox = QHBoxLayout(container)
            hbox.setContentsMargins(6, 2, 6, 2)
            hbox.setSpacing(0)
            btn = self._make_perfil_button()
            btn.clicked.connect(lambda _, r=row: self.perfil_clicked.emit(r))
            hbox.addStretch(1); hbox.addWidget(btn); hbox.addStretch(1)
            self.view.setIndexWidget(index, container)
