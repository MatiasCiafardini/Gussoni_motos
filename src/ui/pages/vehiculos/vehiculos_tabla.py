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
        self.view.horizontalHeader().setStretchLastSection(False)  # la última NO se estira
        self.view.setEditTriggers(QAbstractItemView.NoEditTriggers)

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
        btn.setStyleSheet("""
            QPushButton {
                padding: 0;
                font-size: 14px;
                border-radius: 6px;
            }
        """)
        btn.setFocusPolicy(Qt.NoFocus)
        return btn

    def _perfil_col_width(self) -> int:
        tmp = self._make_perfil_button()
        return tmp.sizeHint().width() + 12  # márgenes (6+6)

    def _configure_columns(self):
        header: QHeaderView = self.view.horizontalHeader()
        header.setStretchLastSection(False)
        last_col = self.model.columnCount() - 1 if self.model.columnCount() else -1
        for c in range(self.model.columnCount()):
            if c == last_col:
                header.setSectionResizeMode(c, QHeaderView.Fixed)
                self.view.setColumnWidth(c, max(42, self._perfil_col_width()))
            else:
                header.setSectionResizeMode(c, QHeaderView.Stretch)

        vh = self.view.verticalHeader()
        btn_h = self._make_perfil_button().sizeHint().height()
        vh.setDefaultSectionSize(max(vh.defaultSectionSize(), btn_h + 8))

    def _install_perfil_buttons(self):
        last_col = self.model.columnCount() - 1
        if last_col < 0:
            return
        for row in range(self.model.rowCount()):
            index = self.model.index(row, last_col)
            container = QWidget(self.view)
            hbox = QHBoxLayout(container)
            hbox.setContentsMargins(6, 2, 6, 2)
            hbox.setSpacing(0)

            btn = self._make_perfil_button()
            btn.clicked.connect(lambda _, r=row: self.perfil_clicked.emit(r))

            hbox.addStretch(1)
            hbox.addWidget(btn)
            hbox.addStretch(1)

            self.view.setIndexWidget(index, container)
