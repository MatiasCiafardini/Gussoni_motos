from PySide6.QtWidgets import QLabel, QVBoxLayout, QDialog
from PySide6.QtCore import Qt, QTimer


class NotifyPopup(QDialog):
    def __init__(self, text, tipo="info", parent=None, duration=1500):
        super().__init__(parent)

        # Configuración de ventana flotante
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint
        )
        self.setModal(False)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Contenido
        self.label = QLabel(text)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(self._get_style(tipo))
        self.label.setAutoFillBackground(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)

        # Tamaño mínimo y ajuste automático
        self.adjustSize()
        self.setMinimumSize(400, 90)

        # Cierre automático
        QTimer.singleShot(duration, self.close)

    def _get_style(self, tipo):
        base = """
            QLabel {
                padding: 20px 30px;
                border-radius: 12px;
                color: white;
                font-size: 18px;
                font-weight: bold;
                background-color: #45180D;
            }
        """
        colores = {
            "info": "background-color: #3498db;",
            "success": "background-color: #2ecc71;",
            "warning": "background-color: #f39c12;",
            "error": "background-color: #45180D;",
        }
        return base + colores.get(tipo, colores["info"])

    def show_centered(self):
        """Muestra el popup centrado en la ventana padre."""
        self.adjustSize()

        if self.parent() and hasattr(self.parent(), "frameGeometry"):
            # Centrar en la ventana padre
            parent_geom = self.parent().frameGeometry()
            x = parent_geom.x() + (parent_geom.width() - self.width()) // 2
            y = parent_geom.y() + (parent_geom.height() - self.height()) // 2
            print(f"Centrando en ventana padre: {x},{y}")  # Debug
            self.move(x, y)
        else:
            # Fallback: centrar en pantalla
            screen = self.screen().availableGeometry()
            x = (screen.width() - self.width()) // 2
            y = (screen.height() - self.height()) // 2
            print(f"Centrando en pantalla: {x},{y}")  # Debug
            self.move(x, y)

        self.show()
        self.raise_()
        self.activateWindow()
