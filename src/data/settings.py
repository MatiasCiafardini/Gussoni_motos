from __future__ import annotations

from pathlib import Path
import os

# ================== Rutas ==================
ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"

# Carpeta Excel (por defecto, data/ ; si preferís otra, cambiá EXCEL_DIR)
EXCEL_DIR = Path(os.getenv("APP_EXCEL_DIR", DATA_DIR))

CLIENTES_XLSX    = EXCEL_DIR / "clientes.xlsx"
VEHICULOS_XLSX   = EXCEL_DIR / "vehiculos.xlsx"
PROVEEDORES_XLSX = EXCEL_DIR / "proveedores.xlsx"
FACTURAS_XLSX    = EXCEL_DIR / "facturas.xlsx"

# ================== Negocio ==================
# Punto de venta para la numeración “PPPP-NNNNNNNN”
PUNTO_VENTA: str = os.getenv("APP_PUNTO_VENTA", "0001").zfill(4)

# Alícuota de IVA por defecto (21% = 0.21)
try:
    ALICUOTA_IVA: float = float(os.getenv("APP_ALICUOTA_IVA", "0.21"))
except Exception:
    ALICUOTA_IVA = 0.21

# Tipos de comprobante disponibles en la UI
TIPOS_FACTURA = [
    "Factura A",
    "Factura B",
    "Factura C",
    "Nota de Crédito A",
    "Nota de Crédito B",
    "Nota de Crédito C",
]

# Condiciones de pago que mostramos en la UI
CONDICIONES_PAGO = [
    "Contado",
    "Transferencia",
    "Financiado",
]
