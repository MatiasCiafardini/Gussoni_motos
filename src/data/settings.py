from pathlib import Path

# Rutas por defecto (relativas al proyecto)
ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"

CLIENTES_XLSX = DATA_DIR / "clientes.xlsx"
VEHICULOS_XLSX = DATA_DIR / "vehiculos.xlsx"
PROVEEDORES_XLSX = DATA_DIR / "proveedores.xlsx"