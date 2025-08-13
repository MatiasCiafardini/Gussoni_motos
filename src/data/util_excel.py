from __future__ import annotations
import pandas as pd
from pathlib import Path
from typing import Dict, Any

# -------------------------------------------------------------------
# Rutas: intenta usar settings.py; si falla, usa /src/data/excel/
# -------------------------------------------------------------------
def _resolve_paths():
    try:
        from src.data import settings as app_settings  # <- tu settings
        base = Path(getattr(app_settings, "EXCEL_DIR", Path(__file__).resolve().parent / "excel"))
        clientes = Path(getattr(app_settings, "CLIENTES_XLSX", base / "clientes.xlsx"))
        vehiculos = Path(getattr(app_settings, "VEHICULOS_XLSX", base / "vehiculos.xlsx"))
        proveedores = Path(getattr(app_settings, "PROVEEDORES_XLSX", base / "proveedores.xlsx"))
    except Exception:
        base = Path(__file__).resolve().parent / "excel"
        clientes = base / "clientes.xlsx"
        vehiculos = base / "vehiculos.xlsx"
        proveedores = base / "proveedores.xlsx"
    return base, clientes, vehiculos, proveedores

EXCEL_DIR, CLIENTES_XLSX, VEHICULOS_XLSX, PROVEEDORES_XLSX = _resolve_paths()

# -------------------------------------------------------------------
# Normalización
# -------------------------------------------------------------------
def _norm_text(x: Any) -> str:
    if x is None:
        return ""
    return " ".join(str(x).strip().lower().split())

def _norm_estado(x: Any) -> str:
    return _norm_text(x)

# -------------------------------------------------------------------
# Utilidades DataFrame
# -------------------------------------------------------------------
def _ensure_cols(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    d = df.copy()
    for c in cols:
        if c not in d.columns:
            d[c] = ""
    return d[cols]

# ======================= CLIENTES ==========================
# Incluimos 'cliente_id' por compatibilidad
_CLIENTES_BASE_COLS = ["id","cliente_id","nombre","dni","email","telefono","direccion","estado"]

def load_clientes(filters: Dict[str, Any] | None = None) -> pd.DataFrame:
    filters = filters or {}
    if CLIENTES_XLSX.exists():
        df = pd.read_excel(CLIENTES_XLSX, sheet_name=0, dtype=object)
        # Compatibilidad: si viene 'cliente_id' y no 'id', renombro
        if "cliente_id" in df.columns and "id" not in df.columns:
            df = df.rename(columns={"cliente_id": "id"})
    else:
        df = pd.DataFrame(columns=_CLIENTES_BASE_COLS)

    # Aseguro columnas y creo alias cliente_id = id
    df = _ensure_cols(df, _CLIENTES_BASE_COLS)
    try:
        empties = df["cliente_id"].isna() | (df["cliente_id"].astype(str).str.strip() == "")
        df.loc[empties, "cliente_id"] = df.loc[empties, "id"]
    except Exception:
        df["cliente_id"] = df.get("id", "")

    # Estado vacío -> "Activo" (en memoria)
    try:
        s = df["estado"].astype(str)
        df.loc[s.str.strip().isin(["", "nan", "None"]), "estado"] = "Activo"
    except Exception:
        df["estado"] = "Activo"

    # Filtros
    def contains(col: str, val: str):
        nonlocal df
        if not val:
            return
        v = _norm_text(val)
        s = df[col].astype(str).map(_norm_text)
        mask = s.str.contains(v, regex=False, na=False)
        df = df[mask]

    def by_estado(val: str):
        nonlocal df
        if not val:
            return
        tgt = _norm_estado(val)
        col = df["estado"].astype(str).map(_norm_estado)
        df = df[col.eq(tgt)]

    contains("nombre", filters.get("nombre", ""))
    contains("dni",    filters.get("dni", ""))
    contains("email",  filters.get("email", ""))
    if filters.get("estado") is not None:
        by_estado(filters["estado"])

    return _ensure_cols(df, _CLIENTES_BASE_COLS).reset_index(drop=True)

def write_clientes_df(df: pd.DataFrame):
    EXCEL_DIR.mkdir(parents=True, exist_ok=True)
    # Garantizo que cliente_id refleje id antes de escribir
    df = df.copy()
    if "cliente_id" in df.columns and "id" in df.columns:
        empties = df["cliente_id"].isna() | (df["cliente_id"].astype(str).str.strip() == "")
        df.loc[empties, "cliente_id"] = df.loc[empties, "id"]
    df = _ensure_cols(df, _CLIENTES_BASE_COLS)
    with pd.ExcelWriter(CLIENTES_XLSX, engine="xlsxwriter") as w:
        df.to_excel(w, index=False, sheet_name="clientes")

def get_cliente_by_id(cid: Any) -> Dict[str, Any]:
    df = load_clientes({})
    try:
        cid_int = int(str(cid).strip())
    except Exception:
        cid_int = None

    # Busco por id y por cliente_id (compatibilidad)
    ids1 = pd.to_numeric(df["id"], errors="coerce")
    row = df.loc[ids1.eq(cid_int)] if cid_int is not None else df.loc[df["id"].astype(str) == str(cid)]
    if row.empty and "cliente_id" in df.columns:
        ids2 = pd.to_numeric(df["cliente_id"], errors="coerce")
        row = df.loc[ids2.eq(cid_int)] if cid_int is not None else df.loc[df["cliente_id"].astype(str) == str(cid)]
    return {} if row.empty else row.iloc[0].to_dict()

def upsert_cliente(data: Dict[str, Any]) -> int:
    """
    Inserta/actualiza un cliente.
    - Si no trae id/cliente_id => asigna uno nuevo (max+1).
    - Actualiza por coincidencia en id o cliente_id.
    Devuelve el id (int).
    """
    df = load_clientes({})
    d = {k: data.get(k, "") for k in _CLIENTES_BASE_COLS}  # normalizo claves

    # Resolver id
    raw_id = d.get("id") or d.get("cliente_id")
    try:
        cid = int(str(raw_id).strip()) if raw_id not in (None, "", 0) else None
    except Exception:
        cid = None

    if cid is None:
        new_id = int(pd.to_numeric(df["id"], errors="coerce").max() or 0) + 1
        d["id"] = new_id
        d["cliente_id"] = new_id
        # Estado por defecto si viene vacío
        if not str(d.get("estado", "")).strip():
            d["estado"] = "Activo"
        df = pd.concat([df, pd.DataFrame([d])], ignore_index=True)
        cid = new_id
    else:
        # Buscar fila por id o cliente_id
        idx = df.index[
            (pd.to_numeric(df["id"], errors="coerce") == cid) |
            (pd.to_numeric(df.get("cliente_id", pd.Series([None]*len(df))), errors="coerce") == cid)
        ]
        if len(idx):
            # Actualizar columnas conocidas
            for col in _CLIENTES_BASE_COLS:
                if col in d and d[col] != "":
                    df.loc[idx, col] = d[col]
            # Mantener alias en sync
            df.loc[idx, "id"] = cid
            df.loc[idx, "cliente_id"] = cid
        else:
            # No existe: lo agrego
            d["id"] = cid
            d["cliente_id"] = cid
            if not str(d.get("estado", "")).strip():
                d["estado"] = "Activo"
            df = pd.concat([df, pd.DataFrame([d])], ignore_index=True)

    write_clientes_df(df)
    return int(cid)

def save_cliente(data: Dict[str, Any]) -> int:
    """Alias de upsert_cliente para compatibilidad con la UI."""
    return upsert_cliente(data)

# ======================= VEHICULOS ==========================
_VEHICULOS_BASE_COLS = [
    "id", "marca", "modelo", "anio",
    "nro_certificado", "nro_dnrpa", "nro_cuadro", "nro_motor",
    "precio", "remito", "factura", "estado"
]

def load_vehiculos(filters: Dict[str, Any] | None = None) -> pd.DataFrame:
    filters = filters or {}
    if VEHICULOS_XLSX.exists():
        df = pd.read_excel(VEHICULOS_XLSX, sheet_name=0, dtype=object)
        # Compatibilidad: por si el Excel trae 'vehiculo_id'
        if "vehiculo_id" in df.columns and "id" not in df.columns:
            df = df.rename(columns={"vehiculo_id": "id"})
    else:
        df = pd.DataFrame(columns=_VEHICULOS_BASE_COLS)

    df = _ensure_cols(df, _VEHICULOS_BASE_COLS)

    def contains(col: str, val: str):
        nonlocal df
        if not val:
            return
        v = _norm_text(val)
        s = df[col].astype(str).map(_norm_text)
        mask = s.str.contains(v, regex=False, na=False)
        df = df[mask]

    def by_anio(val: Any):
        nonlocal df
        if val in (None, ""):
            return
        try:
            an = int(str(val).strip())
        except Exception:
            return
        col = pd.to_numeric(df["anio"], errors="coerce")
        df = df[col.eq(an)]

    def by_estado(val: str):
        nonlocal df
        if not val:
            return
        tgt = _norm_estado(val)
        col = df["estado"].astype(str).map(_norm_estado)
        df = df[col.eq(tgt)]

    contains("marca",      filters.get("marca", ""))
    contains("modelo",     filters.get("modelo", ""))
    by_anio(filters.get("anio", ""))
    contains("nro_cuadro", filters.get("nro_cuadro", ""))
    contains("nro_motor",  filters.get("nro_motor", ""))
    if filters.get("estado") is not None:
        by_estado(filters["estado"])

    return _ensure_cols(df, _VEHICULOS_BASE_COLS).reset_index(drop=True)

def write_vehiculos_df(df: pd.DataFrame):
    EXCEL_DIR.mkdir(parents=True, exist_ok=True)
    df = _ensure_cols(df, _VEHICULOS_BASE_COLS)
    with pd.ExcelWriter(VEHICULOS_XLSX, engine="xlsxwriter") as w:
        df.to_excel(w, index=False, sheet_name="vehiculos")

def get_vehiculo_by_id(vid: Any) -> Dict[str, Any]:
    df = load_vehiculos({})
    try:
        vid_int = int(str(vid).strip())
    except Exception:
        vid_int = None
    ids = pd.to_numeric(df["id"], errors="coerce")
    row = df.loc[ids.eq(vid_int)] if vid_int is not None else df.loc[df["id"].astype(str) == str(vid)]
    return {} if row.empty else row.iloc[0].to_dict()

def upsert_vehiculo(data: Dict[str, Any]) -> int:
    df = load_vehiculos({})
    if "id" not in data or data["id"] in (None, "", 0):
        new_id = int(pd.to_numeric(df["id"], errors="coerce").max() or 0) + 1
        data["id"] = new_id
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
        vid = new_id
    else:
        vid = int(data["id"])
        idx = df.index[pd.to_numeric(df["id"], errors="coerce") == vid]
        if len(idx):
            for k, v in data.items():
                if k in df.columns:
                    df.loc[idx, k] = v
        else:
            df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    write_vehiculos_df(df)
    return int(vid)

# ======================= PROVEEDORES ==========================
# Incluimos 'proveedor_id' por compatibilidad
_PROVEEDORES_BASE_COLS = ["id","proveedor_id","nombre","cuit","email","telefono","direccion","estado"]

def load_proveedores(filters: Dict[str, Any] | None = None) -> pd.DataFrame:
    filters = filters or {}
    if PROVEEDORES_XLSX.exists():
        df = pd.read_excel(PROVEEDORES_XLSX, sheet_name=0, dtype=object)
        # Compatibilidad: si viene 'proveedor_id' y no 'id', renombro
        if "proveedor_id" in df.columns and "id" not in df.columns:
            df = df.rename(columns={"proveedor_id": "id"})
    else:
        df = pd.DataFrame(columns=_PROVEEDORES_BASE_COLS)

    # Aseguro columnas y creo alias proveedor_id = id
    df = _ensure_cols(df, _PROVEEDORES_BASE_COLS)
    try:
        empties = df["proveedor_id"].isna() | (df["proveedor_id"].astype(str).str.strip() == "")
        df.loc[empties, "proveedor_id"] = df.loc[empties, "id"]
    except Exception:
        df["proveedor_id"] = df.get("id", "")

    # Estado vacío -> "Activo" (en memoria)
    try:
        s = df["estado"].astype(str)
        df.loc[s.str.strip().isin(["", "nan", "None"]), "estado"] = "Activo"
    except Exception:
        df["estado"] = "Activo"

    # Filtros
    def contains(col: str, val: str):
        nonlocal df
        if not val:
            return
        v = _norm_text(val)
        s = df[col].astype(str).map(_norm_text)
        mask = s.str.contains(v, regex=False, na=False)
        df = df[mask]

    def by_estado(val: str):
        nonlocal df
        if not val:
            return
        tgt = _norm_estado(val)
        col = df["estado"].astype(str).map(_norm_estado)
        df = df[col.eq(tgt)]

    contains("nombre", filters.get("nombre", ""))
    contains("cuit",   filters.get("cuit", ""))
    contains("email",  filters.get("email", ""))
    if filters.get("estado") is not None:
        by_estado(filters["estado"])

    return _ensure_cols(df, _PROVEEDORES_BASE_COLS).reset_index(drop=True)


def write_proveedores_df(df: pd.DataFrame):
    EXCEL_DIR.mkdir(parents=True, exist_ok=True)
    # Garantizo que proveedor_id refleje id antes de escribir
    df = df.copy()
    if "proveedor_id" in df.columns and "id" in df.columns:
        empties = df["proveedor_id"].isna() | (df["proveedor_id"].astype(str).str.strip() == "")
        df.loc[empties, "proveedor_id"] = df.loc[empties, "id"]
    df = _ensure_cols(df, _PROVEEDORES_BASE_COLS)
    with pd.ExcelWriter(PROVEEDORES_XLSX, engine="xlsxwriter") as w:
        df.to_excel(w, index=False, sheet_name="proveedores")


def get_proveedor_by_id(pid: Any) -> Dict[str, Any]:
    df = load_proveedores({})
    try:
        pid_int = int(str(pid).strip())
    except Exception:
        pid_int = None

    # Busco por id y por proveedor_id (compatibilidad)
    ids1 = pd.to_numeric(df["id"], errors="coerce")
    row = df.loc[ids1.eq(pid_int)] if pid_int is not None else df.loc[df["id"].astype(str) == str(pid)]
    if row.empty and "proveedor_id" in df.columns:
        ids2 = pd.to_numeric(df["proveedor_id"], errors="coerce")
        row = df.loc[ids2.eq(pid_int)] if pid_int is not None else df.loc[df["proveedor_id"].astype(str) == str(pid)]
    return {} if row.empty else row.iloc[0].to_dict()


def upsert_proveedor(data: Dict[str, Any]) -> int:
    """
    Inserta/actualiza un proveedor.
    - Si no trae id/proveedor_id => asigna uno nuevo (max+1).
    - Actualiza por coincidencia en id o proveedor_id.
    Devuelve el id (int).
    """
    df = load_proveedores({})
    d = {k: data.get(k, "") for k in _PROVEEDORES_BASE_COLS}  # normalizo claves

    # Resolver id
    raw_id = d.get("id") or d.get("proveedor_id")
    try:
        pid = int(str(raw_id).strip()) if raw_id not in (None, "", 0) else None
    except Exception:
        pid = None

    if pid is None:
        new_id = int(pd.to_numeric(df["id"], errors="coerce").max() or 0) + 1
        d["id"] = new_id
        d["proveedor_id"] = new_id
        d["estado"] = "Activo"  # siempre activo en alta
        df = pd.concat([df, pd.DataFrame([d])], ignore_index=True)
        pid = new_id
    else:
        # Buscar fila por id o proveedor_id
        idx = df.index[
            (pd.to_numeric(df["id"], errors="coerce") == pid) |
            (pd.to_numeric(df.get("proveedor_id", pd.Series([None]*len(df))), errors="coerce") == pid)
        ]
        if len(idx):
            # Actualizar columnas conocidas
            for col in _PROVEEDORES_BASE_COLS:
                if col in d and d[col] != "":
                    df.loc[idx, col] = d[col]
            # Mantener alias en sync
            df.loc[idx, "id"] = pid
            df.loc[idx, "proveedor_id"] = pid
        else:
            # No existe: lo agrego
            d["id"] = pid
            d["proveedor_id"] = pid
            if not str(d.get("estado", "")).strip():
                d["estado"] = "Activo"
            df = pd.concat([df, pd.DataFrame([d])], ignore_index=True)

    write_proveedores_df(df)
    return int(pid)


def save_proveedor(data: Dict[str, Any]) -> int:
    """Alias de upsert_proveedor para compatibilidad con la UI."""
    return upsert_proveedor(data)
