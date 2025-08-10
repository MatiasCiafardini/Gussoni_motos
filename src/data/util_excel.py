from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional
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
    estado: str  # "Activo" | "Inactivo"

@dataclass
class Vehiculo:
    id: int
    marca: str
    modelo: str
    anio: int
    vin: str
    precio: float
    estado: str  # "Disponible" | "Reservado" | "Vendido" | "No disponible"
    cliente_id: Optional[int] = None

# ----------------- Helpers Excel -----------------
def ensure_excel_files_exist():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not CLIENTES_XLSX.exists():
        df = pd.DataFrame([
            {"id": 1, "nombre": "Ana Pérez", "dni": "12345678A", "email": "ana@example.com", "telefono": "600111222", "direccion": "Calle Sol 123", "estado": "Activo"},
            {"id": 2, "nombre": "Bruno Díaz", "dni": "98765432B", "email": "bruno@example.com", "telefono": "600333444", "direccion": "Av. Luna 45", "estado": "Activo"},
        ])
        df.to_excel(CLIENTES_XLSX, index=False)
    if not VEHICULOS_XLSX.exists():
        df = pd.DataFrame([
            {"id": 1, "marca": "Yamaha",  "modelo": "MT-07",  "anio": 2023, "vin": "VIN0001", "precio": 7200.0, "estado": "Disponible",    "cliente_id": None},
            {"id": 2, "marca": "Honda",   "modelo": "CB500F", "anio": 2022, "vin": "VIN0002", "precio": 6200.0, "estado": "Vendido",       "cliente_id": 1},
            {"id": 3, "marca": "Kawasaki","modelo": "Z650",   "anio": 2024, "vin": "VIN0003", "precio": 7900.0, "estado": "Reservado",     "cliente_id": 2},
            {"id": 4, "marca": "Suzuki",  "modelo": "SV650",  "anio": 2020, "vin": "VIN0004", "precio": 5200.0, "estado": "No disponible", "cliente_id": None},
        ])
        df.to_excel(VEHICULOS_XLSX, index=False)

# --- Clientes ---
def _normalize_clientes(df: pd.DataFrame) -> pd.DataFrame:
    if "estado" not in df.columns:
        df["estado"] = "Activo"
    else:
        df["estado"] = df["estado"].fillna("Activo").replace({"": "Activo"})
        df.loc[~df["estado"].isin(["Activo", "Inactivo"]), "estado"] = "Activo"
    ordered = ["id", "nombre", "dni", "email", "telefono", "direccion", "estado"]
    cols = [c for c in ordered if c in df.columns] + [c for c in df.columns if c not in ordered]
    return df[cols]

def load_clientes(filters: Dict[str, Any] | None = None) -> pd.DataFrame:
    ensure_excel_files_exist()
    df = pd.read_excel(CLIENTES_XLSX)
    df = _normalize_clientes(df)
    if filters:
        if v := filters.get("nombre"):
            df = df[df["nombre"].str.contains(str(v), case=False, na=False)]
        if v := filters.get("dni"):
            df = df[df["dni"].astype(str).str.contains(str(v), case=False, na=False)]
        if v := filters.get("email"):
            df = df[df["email"].str.contains(str(v), case=False, na=False)]
        if v := filters.get("estado"):
            df = df[df["estado"] == str(v)]
    return df.reset_index(drop=True)

def get_cliente_by_id(cid: int) -> Optional[dict]:
    df = load_clientes({})
    row = df[df["id"] == cid]
    return None if row.empty else row.iloc[0].to_dict()

def save_cliente(data: Dict[str, Any]) -> int:
    ensure_excel_files_exist()
    df = pd.read_excel(CLIENTES_XLSX)
    df = _normalize_clientes(df)
    estado_in = data.get("estado", None)
    if not estado_in or estado_in not in ("Activo", "Inactivo"):
        data["estado"] = "Activo"

    if "id" in data and pd.notna(data["id"]) and int(data["id"]) in df["id"].tolist():
        idx = df.index[df["id"] == int(data["id"])][0]
        for k in ["nombre","dni","email","telefono","direccion","estado"]:
            if k in data:
                df.loc[idx, k] = data.get(k, df.loc[idx, k])
        cid = int(df.loc[idx, "id"])
    else:
        cid = (df["id"].max() if not df.empty else 0) + 1
        data["id"] = int(cid)
        for k in ["nombre","dni","email","telefono","direccion","estado"]:
            data.setdefault(k, "" if k != "estado" else "Activo")
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)

    df = _normalize_clientes(df)
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
_ALLOWED_ESTADOS_V = {"Disponible","Reservado","Vendido","No disponible"}

def _normalize_vehiculos(df: pd.DataFrame) -> pd.DataFrame:
    if "estado" not in df.columns:
        df["estado"] = "Disponible"
    else:
        df["estado"] = df["estado"].fillna("Disponible").replace({"": "Disponible"})
        # Normalizar variantes comunes a la forma canónica
        df["estado"] = df["estado"].str.strip().str.capitalize().replace({
            "No disponible": "No disponible",
            "Disponible": "Disponible",
            "Reservado": "Reservado",
            "Vendido": "Vendido",
        })
        df.loc[~df["estado"].isin(_ALLOWED_ESTADOS_V), "estado"] = "Disponible"
    ordered = ["id","marca","modelo","anio","vin","precio","estado","cliente_id"]
    cols = [c for c in ordered if c in df.columns] + [c for c in df.columns if c not in ordered]
    return df[cols]

def load_vehiculos(filters: Dict[str, Any] | None = None) -> pd.DataFrame:
    ensure_excel_files_exist()
    df = pd.read_excel(VEHICULOS_XLSX)
    df = _normalize_vehiculos(df)
    if filters:
        if v := filters.get("marca"):
            df = df[df["marca"].str.contains(str(v), case=False, na=False)]
        if v := filters.get("modelo"):
            df = df[df["modelo"].str.contains(str(v), case=False, na=False)]
        if v := filters.get("anio"):
            try:
                anio = int(v); df = df[df["anio"] == anio]
            except Exception:
                pass
        if v := filters.get("vin"):
            df = df[df["vin"].str.contains(str(v), case=False, na=False)]
        if v := filters.get("estado") and v != "Todos":
            df = df[df["estado"] == v]
    return df.reset_index(drop=True)

def get_vehiculo_by_id(vid: int) -> Optional[dict]:
    df = load_vehiculos({})
    row = df[df["id"] == vid]
    return None if row.empty else row.iloc[0].to_dict()

def save_vehiculo(data: Dict[str, Any]) -> int:
    ensure_excel_files_exist()
    df = pd.read_excel(VEHICULOS_XLSX)
    df = _normalize_vehiculos(df)

    estado = str(data.get("estado","")).strip()
    if estado not in _ALLOWED_ESTADOS_V:
        data["estado"] = "Disponible"

    if "id" in data and pd.notna(data["id"]) and int(data["id"]) in df["id"].tolist():
        idx = df.index[df["id"] == int(data["id"])][0]
        for k in ["marca","modelo","anio","vin","precio","estado","cliente_id"]:
            if k in data:
                df.loc[idx, k] = data[k]
        vid = int(df.loc[idx, "id"])
    else:
        vid = (df["id"].max() if not df.empty else 0) + 1
        data["id"] = int(vid)
        for k in ["marca","modelo","anio","vin","precio","estado","cliente_id"]:
            data.setdefault(k, None)
        data["estado"] = data.get("estado","Disponible") or "Disponible"
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)

    df = _normalize_vehiculos(df)
    df.to_excel(VEHICULOS_XLSX, index=False)
    return int(vid)

def delete_vehiculo(vid: int) -> bool:
    ensure_excel_files_exist()
    df = pd.read_excel(VEHICULOS_XLSX)
    before = len(df)
    df = df[df["id"] != int(vid)]
    df.to_excel(VEHICULOS_XLSX, index=False)
    return len(df) < before
