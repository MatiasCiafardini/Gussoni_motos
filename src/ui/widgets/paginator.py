# src/ui/widgets/paginator.py
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QComboBox
from PySide6.QtCore import Qt
import pandas as pd


class TablePaginator(QWidget):
    def __init__(self, table_widget, on_page_change=None, parent=None):
        super().__init__(parent)
        self.table = table_widget
        self.on_page_change = on_page_change or (lambda: None)

        self.df_full = pd.DataFrame()
        self.current_page = 1
        self.rows_per_page = 10

        # --- Layout ---
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(12)

        # --- Combo filas ---
        self.cmb_rows = QComboBox()
        self.cmb_rows.addItems(["10", "25", "50"])
        self.cmb_rows.setCurrentText("10")
        self.cmb_rows.setFixedWidth(70)
        self.cmb_rows.setFixedHeight(28)
        self.cmb_rows.setStyleSheet("""
            QComboBox {
                padding: 4px;
                border: 1px solid #ccc;
                border-radius: 6px;
                background: white;
            }
            QComboBox:hover {
                border-color: #999;
            }
        """)

        # --- Botones ---
        self.btn_prev = QPushButton("<")
        self.btn_next = QPushButton(">")
        for btn in (self.btn_prev, self.btn_next):
            btn.setFixedSize(32, 28)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1a1a2e;  /* Color igual al menú y botón Buscar */
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #151521;
                }
                QPushButton:disabled {
                    background-color: #555;
                    color: #ccc;
                }
            """)

        # --- Info página ---
        self.lbl_info = QLabel("Página 0/0")
        self.lbl_info.setAlignment(Qt.AlignCenter)
        self.lbl_info.setStyleSheet("color: #444; font-weight: 500;")

        # --- Agregar widgets ---
        layout.addWidget(QLabel("Mostrar:"))
        layout.addWidget(self.cmb_rows)
        layout.addStretch(1)
        layout.addWidget(self.btn_prev)
        layout.addWidget(self.lbl_info)
        layout.addWidget(self.btn_next)

        # --- Conexiones ---
        self.btn_prev.clicked.connect(self.prev_page)
        self.btn_next.clicked.connect(self.next_page)
        self.cmb_rows.currentIndexChanged.connect(self.change_rows_per_page)

    def set_dataframe(self, df: pd.DataFrame):
        if df is None or df.empty:
            self.df_full = pd.DataFrame()
            self.current_page = 1
            self._update_table()
            return
        self.df_full = df.reset_index(drop=True)
        self.current_page = 1
        self._update_table()

    def _update_table(self):
        total_rows = len(self.df_full)
        if total_rows == 0:
            self.table.set_dataframe(pd.DataFrame(columns=self.df_full.columns))
            self.lbl_info.setText("Página 0/0")
            self.btn_prev.setEnabled(False)
            self.btn_next.setEnabled(False)
            return

        total_pages = max(1, -(-total_rows // self.rows_per_page))
        start = (self.current_page - 1) * self.rows_per_page
        end = start + self.rows_per_page
        page_df = self.df_full.iloc[start:end]

        self.table.set_dataframe(page_df)
        self.lbl_info.setText(f"Página {self.current_page}/{total_pages}")

        self.btn_prev.setEnabled(self.current_page > 1)
        self.btn_next.setEnabled(self.current_page < total_pages)

        self.on_page_change()

    def change_rows_per_page(self):
        self.rows_per_page = int(self.cmb_rows.currentText())
        self.current_page = 1
        self._update_table()

    def next_page(self):
        total_pages = max(1, -(-len(self.df_full) // self.rows_per_page))
        if self.current_page < total_pages:
            self.current_page += 1
            self._update_table()

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self._update_table()
