from PySide6.QtWidgets import QMainWindow, QWidget, QStackedWidget, QFrame, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy
from PySide6.QtCore import Qt, QTimer
from .theme import load_theme
from .pages.dashboard import DashboardPage
from .pages.clientes.clientes_main import ClientesMain
from .pages.vehiculos.vehiculos_main import VehiculosMain
from .pages.facturacion import FacturacionPage
from .pages.reportes import ReportesPage
from .pages.configuracion import ConfiguracionPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Motos")
        self.resize(1100, 720)

        # central
        central = QWidget(self)
        self.setCentralWidget(central)
        root = QHBoxLayout(central)

        # Sidebar
        sidebar = QFrame(self)
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(220)
        sbl = QVBoxLayout(sidebar)
        sbl.setContentsMargins(12, 12, 12, 12)
        title = QLabel("Agencia Motos", sidebar)
        title.setStyleSheet("font-size:18px; font-weight:700;")
        sbl.addWidget(title)

        # Menú
        self.btn_inicio = QPushButton("Inicio")
        self.btn_clientes = QPushButton("Clientes")
        self.btn_vehiculos = QPushButton("Vehículos")
        self.btn_facturacion = QPushButton("Facturación")
        self.btn_reportes = QPushButton("Reportes")
        self.btn_config = QPushButton("Configuración")
        for b in [self.btn_inicio, self.btn_clientes, self.btn_vehiculos, self.btn_facturacion, self.btn_reportes, self.btn_config]:
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            sbl.addWidget(b)
        sbl.addStretch(1)

        # Stack de páginas
        self.stack = QStackedWidget(self)
        self._page_history = []  # historial para navegación interna (push/pop)

        # Páginas "fijas"
        self.page_inicio = DashboardPage()
        self.page_clientes = ClientesMain(notify=self.notify, navigate=self.navigate_to, navigate_back=self.navigate_back)
        self.page_vehiculos = VehiculosMain(notify=self.notify)
        self.page_facturacion = FacturacionPage()
        self.page_reportes = ReportesPage()
        self.page_config = ConfiguracionPage()
        for p in [self.page_inicio, self.page_clientes, self.page_vehiculos, self.page_facturacion, self.page_reportes, self.page_config]:
            self.stack.addWidget(p)

        root.addWidget(sidebar)
        root.addWidget(self.stack, 1)

        # connections (al usar el menú, limpiamos historial y vamos a la página fija)
        self.btn_inicio.clicked.connect(lambda: self.show_fixed_page(self.page_inicio))
        self.btn_clientes.clicked.connect(lambda: self.show_fixed_page(self.page_clientes))
        self.btn_vehiculos.clicked.connect(lambda: self.show_fixed_page(self.page_vehiculos))
        self.btn_facturacion.clicked.connect(lambda: self.show_fixed_page(self.page_facturacion))
        self.btn_reportes.clicked.connect(lambda: self.show_fixed_page(self.page_reportes))
        self.btn_config.clicked.connect(lambda: self.show_fixed_page(self.page_config))

        # notificación tipo "toast"
        self._toast = QLabel("", self)
        self._toast.setStyleSheet("background: #212529; color: white; padding: 8px 12px; border-radius: 8px;")
        self._toast.setVisible(False)
        self._toast.setAttribute(Qt.WA_TransparentForMouseEvents)
        self._toast.setAlignment(Qt.AlignCenter)

        self._toast_timer = QTimer(self)
        self._toast_timer.setSingleShot(True)
        self._toast_timer.timeout.connect(lambda: self._toast.setVisible(False))

    # =====================
    # Navegación interna
    # =====================
    def navigate_to(self, widget: QWidget):
        """Empuja una página temporal al stack y navega a ella."""
        self._page_history.append(self.stack.currentWidget())
        self.stack.addWidget(widget)
        self.stack.setCurrentWidget(widget)

    def navigate_back(self):
        """Vuelve a la página anterior y elimina la página temporal actual."""
        if not self._page_history:
            return
        current = self.stack.currentWidget()
        prev = self._page_history.pop()
        self.stack.setCurrentWidget(prev)
        # quitar la página temporal del stack
        current.setParent(None)
        current.deleteLater()

    def show_fixed_page(self, page: QWidget):
        """Limpia cualquier página temporal y muestra una de las páginas fijas."""
        # Si hay una página temporal activa, ir retrocediendo y eliminando
        while self._page_history:
            current = self.stack.currentWidget()
            prev = self._page_history.pop()
            self.stack.setCurrentWidget(prev)
            current.setParent(None)
            current.deleteLater()
        self.stack.setCurrentWidget(page)

    # =====================
    # Toast
    # =====================
    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        # posicionar toast bottom-center
        w = 300
        h = 34
        x = (self.width() - w)//2
        y = self.height() - h - 20
        self._toast.setGeometry(x, y, w, h)

    def notify(self, message: str, timeout_ms: int = 2000):
        self._toast.setText(message)
        self._toast.setVisible(True)
        self._toast.raise_()
        self._toast_timer.start(timeout_ms)
