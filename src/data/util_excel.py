from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional
import pandas as pd
from pathlib import Path
from .settings import CLIENTES_XLSX, VEHICULOS_XLSX, DATA_DIR

# ----------------- Modelos simples -----------------
@dataclass
class Cliente:
    id: int
    nombre: str
    dni: str
    email: str
    telefono: str
    direccion: str

@dataclass
class Vehiculo:
    id: int
    marca: str
    modelo: str
    anio: int
    vin: str
    precio: float
    estado: str  # Disponible, Vendido, Reservado
    cliente_id: Optional[int] = None  # relacion si se vendió

# ----------------- Helpers Excel -----------------
def ensure_excel_files_exist():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not CLIENTES_XLSX.exists():
        df = pd.DataFrame([
            {"id": 1, "nombre": "Ana Pérez", "dni": "12345678A", "email": "ana@example.com", "telefono": "600111222", "direccion": "Calle Sol 123"},
            {"id": 2, "nombre": "Bruno Díaz", "dni": "98765432B", "email": "bruno@example.com", "telefono": "600333444", "direccion": "Av. Luna 45"},
        ])
        df.to_excel(CLIENTES_XLSX, index=False)
    if not VEHICULOS_XLSX.exists():
        df = pd.DataFrame([
            {"id": 1, "marca": "Yamaha", "modelo": "MT-07", "anio": 2023, "vin": "VIN0001", "precio": 7200.0, "estado": "Disponible", "cliente_id": None},
            {"id": 2, "marca": "Honda", "modelo": "CB500F", "anio": 2022, "vin": "VIN0002", "precio": 6200.0, "estado": "Vendido", "cliente_id": 1},
            {"id": 3, "marca": "Kawasaki", "modelo": "Z650", "anio": 2024, "vin": "VIN0003", "precio": 7900.0, "estado": "Reservado", "cliente_id": 2},
        ])
        df.to_excel(VEHICULOS_XLSX, index=False)

# --- Clientes ---
def load_clientes(filters: Dict[str, Any] | None = None) -> pd.DataFrame:
    ensure_excel_files_exist()
    df = pd.read_excel(CLIENTES_XLSX)
    if filters:
        if v := filters.get("nombre"):
            df = df[df["nombre"].str.contains(str(v), case=False, na=False)]
        if v := filters.get("dni"):
            df = df[df["dni"].str.contains(str(v), case=False, na=False)]
        if v := filters.get("email"):
            df = df[df["email"].str.contains(str(v), case=False, na=False)]
    return df.reset_index(drop=True)

def get_cliente_by_id(cid: int) -> Optional[dict]:
    df = load_clientes()
    row = df[df["id"] == cid]
    return None if row.empty else row.iloc[0].to_dict()

def save_cliente(data: Dict[str, Any]) -> int:
    """Crea o actualiza. Devuelve id del cliente."""
    ensure_excel_files_exist()
    df = pd.read_excel(CLIENTES_XLSX)
    if "id" in data and pd.notna(data["id"]) and int(data["id"]) in df["id"].tolist():
        idx = df.index[df["id"] == int(data["id"])][0]
        for k in ["nombre","dni","email","telefono","direccion"]:
            df.loc[idx, k] = data.get(k, df.loc[idx, k])
        cid = int(df.loc[idx, "id"])
    else:
        cid = (df["id"].max() if not df.empty else 0) + 1
        data["id"] = int(cid)
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_excel(CLIENTES_XLSX, index=False)
    return int(cid)

def delete_cliente(cid: int) -> bool:
    ensure_excel_files_exist()
    df = pd.read_excel(CLIENTES_XLSX)
    before = len(df)
    df = df[df["id"] != int(cid)]
    df.to_excel(CLIENTES_XLSX, index=False)
    return len(df) < before

# --- Vehículos ---
def load_vehiculos(filters: Dict[str, Any] | None = None) -> pd.DataFrame:
    ensure_excel_files_exist()
    df = pd.read_excel(VEHICULOS_XLSX)
    if filters:
        if v := filters.get("marca"):
            df = df[df["marca"].str.contains(str(v), case=False, na=False)]
        if v := filters.get("modelo"):
            df = df[df["modelo"].str.contains(str(v), case=False, na=False)]
        if v := filters.get("anio"):
            try:
                anio = int(v)
                df = df[df["anio"] == anio]
            except Exception:
                pass
        if v := filters.get("vin"):
            df = df[df["vin"].str.contains(str(v), case=False, na=False)]
        if v := filters.get("estado"):
            df = df[df["estado"].str.contains(str(v), case=False, na=False)]
    return df.reset_index(drop=True)

def get_vehiculo_by_id(vid: int) -> Optional[dict]:
    df = load_vehiculos()
    row = df[df["id"] == vid]
    return None if row.empty else row.iloc[0].to_dict()

def save_vehiculo(data: Dict[str, Any]) -> int:
    ensure_excel_files_exist()
    df = pd.read_excel(VEHICULOS_XLSX)
    if "id" in data and pd.notna(data["id"]) and int(data["id"]) in df["id"].tolist():
        idx = df.index[df["id"] == int(data["id"])][0]
        for k in ["marca","modelo","anio","vin","precio","estado","cliente_id"]:
            if k in data:
                df.loc[idx, k] = data[k]
        vid = int(df.loc[idx, "id"])
    else:
        vid = (df["id"].max() if not df.empty else 0) + 1
        data["id"] = int(vid)
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_excel(VEHICULOS_XLSX, index=False)
    return int(vid)

def delete_vehiculo(vid: int) -> bool:
    ensure_excel_files_exist()
    df = pd.read_excel(VEHICULOS_XLSX)
    before = len(df)
    df = df[df["id"] != int(vid)]
    df.to_excel(VEHICULOS_XLSX, index=False)
    return len(df) < before
