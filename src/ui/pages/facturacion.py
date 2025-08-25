from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QGridLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QMessageBox, QCompleter,
    QListView, QStyledItemDelegate
)
from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtGui import QFont, QFontMetrics, QPainter, QColor
from src.data import util_excel as ux
from src.data import settings as app_settings
import unicodedata
import pandas as pd
import math
import random
from datetime import date, timedelta

LABEL_STRETCH = 1
FIELD_STRETCH = 3


def normalizar(texto: str) -> str:
    if not texto:
        return ""
    return ''.join(
        c for c in unicodedata.normalize('NFD', str(texto))
        if unicodedata.category(c) != 'Mn'
    ).lower().strip()


def _fmt(val) -> str:
    """Formatea números a 2 decimales, vacío si None/NaN."""
    if val is None:
        return ""
    try:
        f = float(val)
        if math.isnan(f):
            return ""
        return f"{f:,.2f}"
    except Exception:
        return str(val or "")


# ----------------------------
# Delegate para estilizar ítems del completer
# ----------------------------
class CompleterItemDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.secondary_color = QColor("#6b7280")  # gris
        self.primary_color = QColor("#111827")    # casi negro

    def sizeHint(self, option, index):
        text = index.data(Qt.DisplayRole) or ""
        primary, secondary = self._split_text(text)
        fm = option.fontMetrics
        h = fm.height() + int(fm.height() * 0.95) + 10
        w = max(fm.horizontalAdvance(primary + " " + secondary) + 20, 120)
        return QSize(w, h)

    def paint(self, option, index):
        painter = QPainter(option.widget.viewport())
        rect = option.rect.adjusted(10, 6, -10, -6)

        if option.state & QStyledItemDelegate.State_Selected:
            painter.fillRect(option.rect, QColor("#e8f0fe"))
        elif option.state & QStyledItemDelegate.State_MouseOver:
            painter.fillRect(option.rect, QColor("#f5f7ff"))

        text = index.data(Qt.DisplayRole) or ""
        primary, secondary = self._split_text(text)

        f_primary = QFont(option.font)
        f_primary.setBold(True)
        painter.setFont(f_primary)
        painter.setPen(self.primary_color)
        fm_primary = QFontMetrics(f_primary)
        line1 = fm_primary.elidedText(primary, Qt.ElideRight, rect.width())
        painter.drawText(QRect(rect.left(), rect.top(), rect.width(), fm_primary.height()),
                         Qt.AlignVCenter | Qt.AlignLeft, line1)

        f_secondary = QFont(option.font)
        f_secondary.setPointSizeF(max(8.0, option.font.pointSizeF() * 0.95))
        painter.setFont(f_secondary)
        painter.setPen(self.secondary_color)
        fm_secondary = QFontMetrics(f_secondary)
        y2 = rect.top() + fm_primary.height() + 2
        line2 = fm_secondary.elidedText(secondary, Qt.ElideRight, rect.width())
        painter.drawText(QRect(rect.left(), y2, rect.width(), fm_secondary.height()),
                         Qt.AlignVCenter | Qt.AlignLeft, line2)

    def _split_text(self, text: str):
        if " - " in text:
            first, rest = text.split(" - ", 1)
            secondary = rest.replace(" - ", "  •  ")
            return first.strip(), secondary.strip()
        return text.strip(), ""


class CompleterListView(QListView):
    """Popup del QCompleter que se ajusta al ancho del QLineEdit asociado."""
    def __init__(self, target_widget):
        super().__init__()
        self._target = target_widget

    def showEvent(self, event):
        try:
            if self._target is not None:
                self.setFixedWidth(self._target.width())
        except Exception:
            pass
        super().showEvent(event)


class FacturacionMain(QWidget):
    def __init__(self, parent=None, notify=None, navigate=None, navigate_back=None):
        super().__init__(parent)
        self._notify = notify or (lambda msg: None)
        self._navigate = navigate or (lambda w: None)
        self._navigate_back = navigate_back or (lambda: None)

        # Datos (en memoria)
        self._clientes_df = pd.DataFrame()
        self._vehiculos_df = pd.DataFrame()
        self._clientes_map = {}     # texto_normalizado -> id
        self._vehiculos_map = {}    # texto_normalizado -> id

        lay = QVBoxLayout(self)
        lay.setSpacing(20)

        # --- Tipo y Condición ---
        self.gb_tipo = QGroupBox("Tipo y Condición")
        self.gb_tipo.setStyleSheet("QGroupBox { font-weight: bold; margin-top: 10px; }")
        self.grid_tipo = QGridLayout()
        self._build_tipo_condicion()
        self.gb_tipo.setLayout(self.grid_tipo)
        lay.addWidget(self.gb_tipo)

        # --- Cliente ---
        self.gb_cliente = QGroupBox("Cliente")
        self.gb_cliente.setStyleSheet("QGroupBox { font-weight: bold; margin-top: 10px; }")
        self.grid_cliente = QGridLayout()
        self._build_cliente()
        self.gb_cliente.setLayout(self.grid_cliente)
        lay.addWidget(self.gb_cliente)

        # --- Vehículo ---
        self.gb_vehiculo = QGroupBox("Vehículo")
        self.gb_vehiculo.setStyleSheet("QGroupBox { font-weight: bold; margin-top: 10px; }")
        self.grid_vehiculo = QGridLayout()
        self._build_vehiculo()
        self.gb_vehiculo.setLayout(self.grid_vehiculo)
        lay.addWidget(self.gb_vehiculo)

        # --- Resumen ---
        self.gb_resumen = QGroupBox("Resumen de Factura")
        self.gb_resumen.setStyleSheet("QGroupBox { font-weight: bold; margin-top: 10px; }")
        self.grid_resumen = QGridLayout()
        self._build_resumen()
        self.gb_resumen.setLayout(self.grid_resumen)
        lay.addWidget(self.gb_resumen)

        # --- Botón Emitir ---
        self.btn_emitir = QPushButton("Emitir Factura")
        self.btn_emitir.setObjectName("Primary")
        lay.addWidget(self.btn_emitir, alignment=Qt.AlignRight)

        # Eventos de UI
        self.btn_limpiar_cliente.clicked.connect(self._limpiar_cliente)
        self.btn_limpiar_vehiculo.clicked.connect(self._limpiar_vehiculo)
        self.btn_emitir.clicked.connect(self._emitir_factura)

        # Cargar datos iniciales
        self.cargar_clientes()
        self.cargar_vehiculos_todos()  # <<< ahora hay autocompletado de vehículos sin elegir cliente

        # Abrir popup al tipear (mejora UX)
        self.f_cliente.textEdited.connect(lambda _: self._abrir_popup(self.f_cliente))
        self.f_vehiculo.textEdited.connect(lambda _: self._abrir_popup(self.f_vehiculo))

    # ----------------------------
    # Sección Tipo y Condición
    # ----------------------------
    def _build_tipo_condicion(self):
        self.f_tipo = QComboBox()
        tipos = app_settings.TIPOS_FACTURA or ["Factura A", "Factura B", "Factura C"]
        self.f_tipo.addItems(tipos)

        self.f_pago = QComboBox()
        pagos = app_settings.CONDICIONES_PAGO or ["Contado", "Transferencia", "Financiado"]
        self.f_pago.addItems(pagos)

        self.f_pv = self._readonly_field()
        self.f_pv.setText(app_settings.PUNTO_VENTA)

        self._arrange_fields(self.grid_tipo, [
            ("Tipo Factura:", self.f_tipo),
            ("Cond. Pago:", self.f_pago),
            ("Punto de Venta:", self.f_pv),
        ], cols=3)

    # ----------------------------
    # Sección Cliente
    # ----------------------------
    def _build_cliente(self):
        self.f_cliente = QLineEdit()
        self.f_cliente.setPlaceholderText("Buscar cliente...")
        self.btn_limpiar_cliente = QPushButton("Limpiar")
        self.f_nombre = self._readonly_field()
        self.f_apellido = self._readonly_field()
        self.f_cuit = self._readonly_field()
        self.f_direccion = self._readonly_field()

        self._arrange_fields(self.grid_cliente, [
            ("Buscar:", self.f_cliente),
            ("", self.btn_limpiar_cliente),
            ("Nombre:", self.f_nombre),
            ("Apellido:", self.f_apellido),
            ("CUIT/DNI:", self.f_cuit),
            ("Dirección:", self.f_direccion)
        ], cols=3)

    # ----------------------------
    # Sección Vehículo
    # ----------------------------
    def _build_vehiculo(self):
        self.f_vehiculo = QLineEdit()
        self.f_vehiculo.setPlaceholderText("Buscar vehículo...")
        self.btn_limpiar_vehiculo = QPushButton("Limpiar")
        self.f_marca = self._readonly_field()
        self.f_modelo = self._readonly_field()
        self.f_nro_cuadro = self._readonly_field()
        self.f_patente = self._readonly_field()
        self.f_precio = self._readonly_field()

        self._arrange_fields(self.grid_vehiculo, [
            ("Buscar:", self.f_vehiculo),
            ("", self.btn_limpiar_vehiculo),
            ("Marca:", self.f_marca),
            ("Modelo:", self.f_modelo),
            ("Nº Cuadro:", self.f_nro_cuadro),
            ("Patente:", self.f_patente),
            ("Precio:", self.f_precio)
        ], cols=3)

    # ----------------------------
    # Sección Resumen
    # ----------------------------
    def _build_resumen(self):
        self.f_subtotal = self._readonly_field()
        self.f_iva = self._readonly_field()
        self.f_total = self._readonly_field(bold=True)
        self.lbl_cae = QLabel("CAE: ---")
        self.lbl_venc = QLabel("Vencimiento: ---")

        self._arrange_fields(self.grid_resumen, [
            ("Subtotal:", self.f_subtotal),
            ("IVA:", self.f_iva),
            ("Total:", self.f_total)
        ], cols=3)

        self.grid_resumen.addWidget(self.lbl_cae, 2, 0, 1, 2)
        self.grid_resumen.addWidget(self.lbl_venc, 3, 0, 1, 2)

    # ----------------------------
    # Utilidades de UI
    # ----------------------------
    def _readonly_field(self, bold=False):
        field = QLineEdit()
        style = """
            QLineEdit {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                color: #333;
            }
        """
        if bold:
            style += "QLineEdit { font-weight: bold; font-size: 14px; }"
        field.setReadOnly(True)
        field.setStyleSheet(style)
        return field

    def _arrange_fields(self, layout, pairs, cols=3):
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setHorizontalSpacing(16)
        layout.setVerticalSpacing(10)
        for i, (label_text, widget) in enumerate(pairs):
            row = i // cols
            col = (i % cols) * 2
            if label_text:
                label = QLabel(label_text)
                label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                layout.addWidget(label, row, col)
            else:
                layout.addWidget(QWidget(), row, col)
            layout.addWidget(widget, row, col + 1)
            layout.setColumnStretch(col, LABEL_STRETCH)
            layout.setColumnStretch(col + 1, FIELD_STRETCH)

    def _abrir_popup(self, line_edit: QLineEdit):
        comp = line_edit.completer()
        if comp is not None:
            comp.complete()

    # ----------------------------
    # Lógica de datos / Completers
    # ----------------------------
    def _crear_completer(self, lista, callback_on_select, line_edit=None):
        completer = QCompleter(lista, self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.activated.connect(callback_on_select)

        view = CompleterListView(line_edit)
        view.setItemDelegate(CompleterItemDelegate(view))
        view.setMouseTracking(True)
        view.setVerticalScrollMode(QListView.ScrollPerPixel)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        view.setUniformItemSizes(False)
        view.setSpacing(0)
        view.setStyleSheet("""
            QListView {
                background: #ffffff;
                border: 1px solid #c9cdd5;
                border-radius: 8px;
                padding: 4px;
                outline: 0;
            }
            QListView::item {
                padding: 6px 8px;
                border-radius: 6px;
            }
            QListView::item:selected {
                background: #e8f0fe;
                color: #111827;
            }
            QListView::item:hover {
                background: #f5f7ff;
            }
        """)
        completer.setPopup(view)
        completer.setMaxVisibleItems(8)
        return completer

    # ---- Clientes ----
    def cargar_clientes(self):
        try:
            self._clientes_df = ux.load_clientes()
            self._clientes_map.clear()
            lista_clientes = []

            for _, row in self._clientes_df.iterrows():
                nombre = str(row.get("nombre", "")).strip()
                apellido = str(row.get("apellido", "")).strip()
                dni = str(row.get("dni", row.get("cuit", "")) or "").strip()

                if not apellido and nombre and " " in nombre:
                    partes = nombre.split()
                    nombre, apellido = " ".join(partes[:-1]), partes[-1]

                display = f"{nombre} {apellido} {f'({dni})' if dni else ''}".strip()
                key = normalizar(display)
                self._clientes_map[key] = row.get("id")
                lista_clientes.append(display)

            comp = self._crear_completer(lista_clientes, self._on_cliente_selected, self.f_cliente)
            self.f_cliente.setCompleter(comp)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar clientes: {e}")

    def _on_cliente_selected(self, texto):
        self.f_cliente.setText(texto)
        key = normalizar(texto)
        cliente_id = self._clientes_map.get(key)

        if cliente_id is None:
            try:
                dentro = texto.split("(")[-1].replace(")", "").strip()
                if dentro:
                    row = self._clientes_df[self._clientes_df.get("dni", pd.Series(dtype=object)).astype(str) == dentro]
                    if not row.empty:
                        cliente_id = row.iloc[0].get("id")
            except Exception:
                pass

        if cliente_id is None:
            mask = self._clientes_df["nombre"].astype(str).str.lower().str.contains(normalizar(texto))
            if mask.any():
                cliente_id = self._clientes_df[mask].iloc[0].get("id")

        if cliente_id is None:
            self._notify("No se pudo identificar el cliente seleccionado.")
            return

        try:
            row = self._clientes_df[self._clientes_df["id"] == cliente_id].iloc[0]
        except Exception:
            self._notify("Cliente no encontrado en la base.")
            return

        nombre = str(row.get("nombre", "") or "").strip()
        apellido = str(row.get("apellido", "") or "").strip()
        if not apellido and nombre and " " in nombre:
            partes = nombre.split()
            nombre, apellido = " ".join(partes[:-1]), partes[-1]

        self.f_nombre.setText(nombre)
        self.f_apellido.setText(apellido)
        self.f_cuit.setText(str(row.get("dni", row.get("cuit", "")) or ""))
        self.f_direccion.setText(str(row.get("direccion", "") or ""))

        # Actualizo el completer de vehículos filtrando por cliente (si existe cliente_id)
        self.cargar_vehiculos_cliente(cliente_id)

    def _limpiar_cliente(self):
        self.f_cliente.clear()
        self.f_nombre.clear()
        self.f_apellido.clear()
        self.f_cuit.clear()
        self.f_direccion.clear()
        # Volver a mostrar todos los vehículos
        self.cargar_vehiculos_todos()

    # ---- Vehículos ----
    def _vehiculo_display(self, row: pd.Series) -> str:
        marca = str(row.get("marca", "") or "").strip()
        modelo = str(row.get("modelo", "") or "").strip()
        patente = str(row.get("patente", "") or "").strip()
        nro_cuadro = str(row.get("nro_cuadro", "") or "").strip()
        precio = row.get("precio", 0)

        partes = [p for p in [marca, modelo] if p]
        principal = " ".join(partes) if partes else "Vehículo"
        det_patente = f" - Patente: {patente}" if patente else ""
        det_cuadro = f" - Nº Cuadro: {nro_cuadro}" if nro_cuadro else ""
        det_precio = f" - Precio: ${_fmt(precio)}" if precio not in (None, "", 0) else ""
        return f"{principal}{det_patente}{det_cuadro}{det_precio}"

    def _aplicar_completer_vehiculo(self, df: pd.DataFrame):
        self._vehiculos_map.clear()
        lista_vehiculos = []
        for _, row in df.iterrows():
            display = self._vehiculo_display(row)
            key = normalizar(display)
            self._vehiculos_map[key] = row.get("id")
            lista_vehiculos.append(display)
        comp = self._crear_completer(lista_vehiculos, self._on_vehiculo_selected, self.f_vehiculo)
        self.f_vehiculo.setCompleter(comp)

    def cargar_vehiculos_todos(self):
        """Carga el autocompletado de vehículos con TODOS los vehículos (inicio o limpiar cliente)."""
        try:
            self._vehiculos_df = ux.load_vehiculos()
            self._aplicar_completer_vehiculo(self._vehiculos_df)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar vehículos: {e}")

    def cargar_vehiculos_cliente(self, cliente_id: int | str):
        """Carga el autocompletado de vehículos filtrado por cliente si existe 'cliente_id' en el Excel."""
        try:
            self._vehiculos_df = ux.load_vehiculos()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar vehículos: {e}")
            return

        df = self._vehiculos_df.copy()
        if "cliente_id" in df.columns and pd.notna(cliente_id):
            try:
                df = df[df["cliente_id"] == cliente_id]
            except Exception:
                df = df[df["cliente_id"].astype(str) == str(cliente_id)]

        self._aplicar_completer_vehiculo(df)

    def _on_vehiculo_selected(self, texto):
        self.f_vehiculo.setText(texto)
        vehiculo_texto = normalizar(texto)
        vehiculo_id = self._vehiculos_map.get(vehiculo_texto)

        if vehiculo_id is None and not self._vehiculos_df.empty:
            t = normalizar(texto)
            mask = (
                self._vehiculos_df.get("marca", pd.Series(dtype=object)).astype(str).str.lower().apply(normalizar).str.contains(t)
                | self._vehiculos_df.get("modelo", pd.Series(dtype=object)).astype(str).str.lower().apply(normalizar).str.contains(t)
                | self._vehiculos_df.get("patente", pd.Series(dtype=object)).astype(str).str.lower().apply(normalizar).str.contains(t)
                | self._vehiculos_df.get("nro_cuadro", pd.Series(dtype=object)).astype(str).str.lower().apply(normalizar).str.contains(t)
            )
            if mask.any():
                vehiculo_id = self._vehiculos_df[mask].iloc[0].get("id")

        if vehiculo_id is None:
            self._notify("No se pudo identificar el vehículo seleccionado.")
            return

        try:
            row = self._vehiculos_df[self._vehiculos_df["id"] == vehiculo_id].iloc[0]
        except Exception:
            self._notify("Vehículo no encontrado en la base.")
            return

        self.f_marca.setText(str(row.get("marca", "") or ""))
        self.f_modelo.setText(str(row.get("modelo", "") or ""))
        self.f_nro_cuadro.setText(str(row.get("nro_cuadro", "") or ""))
        self.f_patente.setText(str(row.get("patente", "") or ""))

        precio = float(row.get("precio", 0) or 0)
        self.f_precio.setText(_fmt(precio))
        self._actualizar_totales(precio)

    def _limpiar_vehiculo(self):
        self.f_vehiculo.clear()
        self.f_marca.clear()
        self.f_modelo.clear()
        self.f_nro_cuadro.clear()
        self.f_patente.clear()
        self.f_precio.clear()
        self.f_subtotal.clear()
        self.f_iva.clear()
        self.f_total.clear()

    def _actualizar_totales(self, precio):
        subtotal = float(precio or 0)
        iva = subtotal * float(app_settings.ALICUOTA_IVA)
        total = subtotal + iva
        self.f_subtotal.setText(_fmt(subtotal))
        self.f_iva.setText(_fmt(iva))
        self.f_total.setText(_fmt(total))

    # ----------------------------
    # Emisión y “vinculación” ARCA (simulado)
    # ----------------------------
    def _emitir_factura(self):
        try:
            if not self.f_nombre.text().strip():
                QMessageBox.warning(self, "Faltan datos", "Seleccioná un cliente.")
                return
            if not (self.f_marca.text().strip() or self.f_modelo.text().strip()):
                QMessageBox.warning(self, "Faltan datos", "Seleccioná un vehículo.")
                return
            try:
                subtotal = float((self.f_subtotal.text() or "0").replace(",", ""))
                iva = float((self.f_iva.text() or "0").replace(",", ""))
                total = float((self.f_total.text() or "0").replace(",", ""))
            except Exception:
                QMessageBox.warning(self, "Importes inválidos", "Los importes no son válidos.")
                return

            pv = app_settings.PUNTO_VENTA
            numero = ux.get_ultimo_numero_factura(pv)

            payload = {
                "numero": numero,
                "fecha": date.today().isoformat(),
                "tipo": self.f_tipo.currentText(),
                "pago": self.f_pago.currentText(),
                "punto_venta": pv,
                "cliente": {
                    "nombre": self.f_nombre.text().strip(),
                    "apellido": self.f_apellido.text().strip(),
                    "cuit_dni": self.f_cuit.text().strip(),
                    "direccion": self.f_direccion.text().strip(),
                },
                "detalle": {
                    "vehiculo": f"{self.f_marca.text().strip()} {self.f_modelo.text().strip()}".strip(),
                    "patente": self.f_patente.text().strip(),
                    "nro_cuadro": self.f_nro_cuadro.text().strip(),
                    "precio": subtotal,
                },
                "totales": {"subtotal": subtotal, "iva": iva, "total": total},
            }

            resp = self._arca_emit(payload)
            cae = resp.get("cae", "---")
            venc = resp.get("vencimiento", "---")

            ux.append_factura({
                "numero": numero,
                "fecha": payload["fecha"],
                "cliente": f"{payload['cliente']['nombre']} {payload['cliente']['apellido']}".strip(),
                "cuit_dni_cliente": payload["cliente"]["cuit_dni"],
                "vehiculo": payload["detalle"]["vehiculo"],
                "patente": payload["detalle"]["patente"],
                "tipo": payload["tipo"],
                "pago": payload["pago"],
                "subtotal": subtotal,
                "iva": iva,
                "total": total,
                "cae": cae,
                "vto_cae": venc,
            })

            self.lbl_cae.setText(f"CAE: {cae}")
            self.lbl_venc.setText(f"Vencimiento: {venc}")
            self._notify(f"Factura {numero} emitida (CAE {cae}).")

        except Exception as e:
            QMessageBox.critical(self, "Error al emitir", f"Ocurrió un error al emitir la factura:\n{e}")

    def _arca_emit(self, payload: dict) -> dict:
        """Simulación de integración con ARCA. En producción: reemplazar por cliente homologado."""
        if not payload.get("cliente", {}).get("cuit_dni"):
            raise ValueError("El cliente debe tener CUIT/DNI para emitir.")
        cae = "".join(str(random.randint(0, 9)) for _ in range(14))
        venc = (date.today() + timedelta(days=10)).strftime("%d/%m/%Y")
        return {"cae": cae, "vencimiento": venc}
