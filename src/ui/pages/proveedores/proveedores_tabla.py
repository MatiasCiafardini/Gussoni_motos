from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableView, QAbstractItemView, QPushButton,
    QHBoxLayout, QHeaderView
)
from PySide6.QtCore import Signal, Qt
from .proveedores_model import ProveedoresModel
from src.data import util_excel as ux


class ProveedoresTabla(QWidget):
    perfil_clicked = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = ProveedoresModel()
        self._filtros = {}  # <-- Guarda los filtros actuales

        self.view = QTableView(self)
        self.view.setModel(self.model)
        self.view.setSelectionBehavior(QTableView.SelectRows)
        self.view.setSelectionMode(QTableView.SingleSelection)
        self.view.setAlternatingRowColors(True)
        self.view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.view.horizontalHeader().setStretchLastSection(False)

        lay = QVBoxLayout(self)
        lay.addWidget(self.view)

    # ---------- Recarga de datos ----------
    def cargar_datos(self, filtros=None):
        """Carga datos en la tabla aplicando filtros (si se pasan)."""
        if filtros is not None:
            self._filtros = filtros
        df = ux.load_proveedores(self._filtros)
        self.set_dataframe(df)

    def refrescar(self):
        """Recarga la tabla usando los filtros actuales."""
        self.cargar_datos(self._filtros)

    def set_dataframe(self, df):
        self.model.setDataFrame(df)
        self._configure_columns()
        self._install_perfil_buttons()

    # ---------- Helpers de UI ----------
    def _make_perfil_button(self):
        btn = QPushButton("🔍", self.view)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setToolTip("Ver perfil")
        btn.setFixedSize(30, 30)
        btn.setStyleSheet("QPushButton { padding: 0; font-size: 14px; border-radius: 6px; }")
        btn.setFocusPolicy(Qt.NoFocus)
        return btn

    def _perfil_col_width(self) -> int:
        tmp_btn = self._make_perfil_button()
        return tmp_btn.sizeHint().width() + 12

    def _configure_columns(self):
        header: QHeaderView = self.view.horizontalHeader()
        header.setStretchLastSection(False)
        header.setMinimumSectionSize(90)
        last_col = self.model.columnCount() - 1 if self.model.columnCount() else -1
        for c in range(self.model.columnCount()):
            if c == last_col:
                header.setSectionResizeMode(c, QHeaderView.Fixed)
                self.view.setColumnWidth(c, max(42, self._perfil_col_width()))
            else:
                header.setSectionResizeMode(c, QHeaderView.Stretch)
        vh = self.view.verticalHeader()
        vh.setDefaultSectionSize(max(vh.defaultSectionSize(), 36))

    def _install_perfil_buttons(self):
        last_col = self.model.columnCount() - 1
        if last_col < 0 or self.model.rowCount() == 0:
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
