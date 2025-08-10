from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableView, QAbstractItemView, QPushButton,
    QHBoxLayout, QHeaderView
)
from PySide6.QtCore import Signal, Qt
from .clientes_model import ClientesModel

class ClientesTabla(QWidget):
    # Señal propia: emite el número de fila cuando se hace clic en el icono "lupa"
    perfil_clicked = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = ClientesModel()
        self.view = QTableView(self)
        self.view.setModel(self.model)
        self.view.setSelectionBehavior(QTableView.SelectRows)
        self.view.setSelectionMode(QTableView.SingleSelection)
        self.view.setAlternatingRowColors(True)
        # La última columna NO se estira (fija para el botón-ícono)
        self.view.horizontalHeader().setStretchLastSection(False)
        # Evitar modo edición
        self.view.setEditTriggers(QAbstractItemView.NoEditTriggers)

        lay = QVBoxLayout(self)
        lay.addWidget(self.view)

    def set_dataframe(self, df):
        self.model.setDataFrame(df)
        self._configure_columns()
        self._install_perfil_buttons()

    # ---------- Helpers de UI ----------
    def _make_perfil_button(self):
        """Botón-ícono 🔍 tamaño intermedio, sin texto, con tooltip accesible."""
        btn = QPushButton("🔍", self.view)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setToolTip("Ver perfil")
        # Tamaño intermedio: cuadrado compacto
        btn.setFixedSize(30, 30)
        # Estilo minimal, con algo de radio para verse “pill”
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
        """Ancho fijo de la columna Perfil basado en el sizeHint del botón + márgenes."""
        tmp_btn = self._make_perfil_button()
        w = tmp_btn.sizeHint().width()
        # márgenes del contenedor (6 izq + 6 der) para no pegar al borde
        return w + 12

    def _configure_columns(self):
        """Fija la última columna al ancho del botón y hace que el resto sea elástico."""
        header: QHeaderView = self.view.horizontalHeader()
        header.setStretchLastSection(False)

        last_col = self.model.columnCount() - 1 if self.model.columnCount() else -1
        for c in range(self.model.columnCount()):
            if c == last_col:
                header.setSectionResizeMode(c, QHeaderView.Fixed)
                self.view.setColumnWidth(c, max(42, self._perfil_col_width()))
            else:
                header.setSectionResizeMode(c, QHeaderView.Stretch)

        # Ajustar alto de fila para que el botón entre cómodo
        vh = self.view.verticalHeader()
        btn_h = self._make_perfil_button().sizeHint().height()
        vh.setDefaultSectionSize(max(vh.defaultSectionSize(), btn_h + 8))

    def _install_perfil_buttons(self):
        """Inserta el botón-ícono centrado en cada celda de la última columna."""
        last_col = self.model.columnCount() - 1
        if last_col < 0:
            return

        for row in range(self.model.rowCount()):
            index = self.model.index(row, last_col)

            # Contenedor con margen y botón centrado
            container = QWidget(self.view)
            hbox = QHBoxLayout(container)
            hbox.setContentsMargins(6, 2, 6, 2)  # separa del borde de la celda
            hbox.setSpacing(0)

            btn = self._make_perfil_button()
            # Capturamos 'row' para emitir la fila correcta
            btn.clicked.connect(lambda _, r=row: self.perfil_clicked.emit(r))

            # Centrado del botón dentro de la celda
            hbox.addStretch(1)
            hbox.addWidget(btn)
            hbox.addStretch(1)

            self.view.setIndexWidget(index, container)
