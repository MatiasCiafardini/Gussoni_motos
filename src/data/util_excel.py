from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import pandas as pd

# ============================================================================
# Rutas: intenta usar settings.py; si falla, usa /src/data/excel/
# ============================================================================
def _resolve_paths() -> Tuple[Path, Path, Path, Path, Path]:
    try:
        from src.data import settings as app_settings  # <- tu settings
        base = Path(getattr(app_settings, "EXCEL_DIR", Path(__file__).resolve().parent / "excel"))
        clientes = Path(getattr(app_settings, "CLIENTES_XLSX", base / "clientes.xlsx"))
        vehiculos = Path(getattr(app_settings, "VEHICULOS_XLSX", base / "vehiculos.xlsx"))
        proveedores = Path(getattr(app_settings, "PROVEEDORES_XLSX", base / "proveedores.xlsx"))
        facturas = Path(getattr(app_settings, "FACTURAS_XLSX", base / "facturas.xlsx"))
    except Exception:
        base = Path(__file__).resolve().parent / "excel"
        clientes = base / "clientes.xlsx"
        vehiculos = base / "vehiculos.xlsx"
        proveedores = base / "proveedores.xlsx"
        facturas = base / "facturas.xlsx"
    return base, clientes, vehiculos, proveedores, facturas

EXCEL_DIR, CLIENTES_XLSX, VEHICULOS_XLSX, PROVEEDORES_XLSX, FACTURAS_XLSX = _resolve_paths()

# ============================================================================
# Helpers generales
# ============================================================================
def _norm_text(x: Any) -> str:
    if x is None:
        return ""
    return " ".join(str(x).strip().lower().split())

def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

def _ensure_cols(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    """Agrega columnas faltantes y devuelve un DF con al menos 'cols'."""
    d = df.copy()
    for c in cols:
        if c not in d.columns:
            d[c] = ""
    # Reordeno poniendo las base primero, mantengo extras al final
    extras = [c for c in d.columns if c not in cols]
    return d[cols + extras]

def _read_xlsx(path: Path, base_cols: Iterable[str]) -> pd.DataFrame:
    """
    Lee un Excel como dtype=object. Si no existe, devuelve DF vacío con columnas base.
    Si existe pero faltan columnas, las agrega.
    """
    _ensure_parent(path)
    if not path.exists():
        return pd.DataFrame(columns=list(base_cols))
    try:
        df = pd.read_excel(path, sheet_name=0, dtype=object)
    except Exception:
        # En caso de corrupción o error de engine, devuelvo vacío consistente
        return pd.DataFrame(columns=list(base_cols))
    # Normalizo nombres
    df.columns = [str(c).strip() for c in df.columns]
    return _ensure_cols(df, list(base_cols))

def _write_xlsx(path: Path, df: pd.DataFrame, sheet_name: str) -> None:
    """Escritura atómica y limpia."""
    _ensure_parent(path)
    # write to temp and replace to reduce risk of corruption
    tmp = path.with_suffix(".tmp.xlsx")
    with pd.ExcelWriter(tmp, engine="xlsxwriter") as w:
        df.to_excel(w, index=False, sheet_name=sheet_name)
    if path.exists():
        path.unlink(missing_ok=True)
    tmp.rename(path)

def _to_int(val) -> int | None:
    try:
        if pd.isna(val):
            return None
    except Exception:
        pass
    try:
        return int(str(val).strip())
    except Exception:
        return None

def _to_float(val) -> float:
    try:
        if isinstance(val, str):
            # tolerante a formatos: 1.234,56 -> 1234.56
            val = val.replace(".", "").replace(",", ".")
        return float(val)
    except Exception:
        return 0.0

# ============================================================================
# CLIENTES
# ============================================================================
# Incluimos 'apellido' por la UI de facturación y alias 'cliente_id'
_CLIENTES_BASE_COLS: List[str] = [
    "id", "cliente_id", "nombre", "apellido", "dni", "cuit",
    "email", "telefono", "direccion", "estado"
]

def load_clientes(filters: Dict[str, Any] | None = None) -> pd.DataFrame:
    filters = filters or {}
    df = _read_xlsx(CLIENTES_XLSX, _CLIENTES_BASE_COLS)

    # Compatibilidad: si viene 'cliente_id' y no 'id', renombro
    if "cliente_id" in df.columns and "id" not in df.columns:
        df = df.rename(columns={"cliente_id": "id"})
    # Sincronizo alias (si falta cliente_id, lo lleno con id)
    try:
        empties = df["cliente_id"].isna() | (df["cliente_id"].astype(str).str.strip() == "")
        df.loc[empties, "cliente_id"] = df.loc[empties, "id"]
    except Exception:
        df["cliente_id"] = df.get("id", "")

    # Estado por defecto
    try:
        s = df["estado"].astype(str)
        df.loc[s.str.strip().isin(["", "nan", "none", "None"]), "estado"] = "Activo"
    except Exception:
        df["estado"] = "Activo"

    # Filtros
    def contains(col: str, val: str):
        nonlocal df
        if not val:
            return
        v = _norm_text(val)
        s = df[col].astype(str).map(_norm_text)
        df = df[s.str.contains(v, regex=False, na=False)]

    def by_estado(val: str):
        nonlocal df
        if not val:
            return
        tgt = _norm_text(val)
        s = df["estado"].astype(str).map(_norm_text)
        df = df[s.eq(tgt)]

    contains("nombre", filters.get("nombre", ""))
    contains("apellido", filters.get("apellido", ""))
    contains("dni", filters.get("dni", ""))
    contains("cuit", filters.get("cuit", ""))
    contains("email", filters.get("email", ""))
    if filters.get("estado") is not None:
        by_estado(filters["estado"])

    return _ensure_cols(df, _CLIENTES_BASE_COLS).reset_index(drop=True)

def write_clientes_df(df: pd.DataFrame) -> None:
    d = df.copy()
    # Garantizo alias
    if "cliente_id" in d.columns and "id" in d.columns:
        empties = d["cliente_id"].isna() | (d["cliente_id"].astype(str).str.strip() == "")
        d.loc[empties, "cliente_id"] = d.loc[empties, "id"]
    d = _ensure_cols(d, _CLIENTES_BASE_COLS)
    _write_xlsx(CLIENTES_XLSX, d, "clientes")

def get_cliente_by_id(cid: Any) -> Dict[str, Any]:
    df = load_clientes({})
    cid_int = _to_int(cid)
    # Busco por id o cliente_id (compat)
    idx = (
        (pd.to_numeric(df["id"], errors="coerce") == cid_int)
        if cid_int is not None else (df["id"].astype(str) == str(cid))
    )
    row = df.loc[idx]
    if row.empty and "cliente_id" in df.columns:
        idx2 = (
            (pd.to_numeric(df["cliente_id"], errors="coerce") == cid_int)
            if cid_int is not None else (df["cliente_id"].astype(str) == str(cid))
        )
        row = df.loc[idx2]
    return {} if row.empty else row.iloc[0].to_dict()

def upsert_cliente(data: Dict[str, Any]) -> int:
    """
    Inserta/actualiza un cliente.
    - Si no trae id/cliente_id => asigna uno nuevo (max+1).
    - Actualiza por coincidencia en id o cliente_id.
    Devuelve el id (int).
    """
    df = load_clientes({})
    d = {k: data.get(k, "") for k in _CLIENTES_BASE_COLS}

    raw_id = d.get("id") or d.get("cliente_id")
    cid = _to_int(raw_id)

    if cid is None:
        new_id = int(pd.to_numeric(df["id"], errors="coerce").max() or 0) + 1
        d["id"] = new_id
        d["cliente_id"] = new_id
        if not str(d.get("estado", "")).strip():
            d["estado"] = "Activo"
        df = pd.concat([df, pd.DataFrame([d])], ignore_index=True)
        cid = new_id
    else:
        idx = df.index[
            (pd.to_numeric(df["id"], errors="coerce") == cid) |
            (pd.to_numeric(df.get("cliente_id", pd.Series([None]*len(df))), errors="coerce") == cid)
        ]
        if len(idx):
            for col in _CLIENTES_BASE_COLS:
                if col in d and d[col] != "":
                    df.loc[idx, col] = d[col]
            df.loc[idx, "id"] = cid
            df.loc[idx, "cliente_id"] = cid
        else:
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

# ============================================================================
# VEHICULOS
# ============================================================================
# Mantengo tus campos; agrego 'cliente_id' si existe en tus datos, pero no es obligatorio
_VEHICULOS_BASE_COLS: List[str] = [
    "id", "cliente_id",
    "marca", "modelo", "anio",
    "nro_certificado", "nro_dnrpa", "nro_cuadro", "nro_motor",
    "precio", "remito", "factura", "estado"
]

def load_vehiculos(filters: Dict[str, Any] | None = None) -> pd.DataFrame:
    filters = filters or {}
    df = _read_xlsx(VEHICULOS_XLSX, _VEHICULOS_BASE_COLS)

    # Compat: si viniera 'vehiculo_id'
    if "vehiculo_id" in df.columns and "id" not in df.columns:
        df = df.rename(columns={"vehiculo_id": "id"})

    # precio a float tolerante
    if "precio" in df.columns:
        df["precio"] = df["precio"].apply(_to_float)

    # Filtros
    def contains(col: str, val: str):
        nonlocal df
        if not val:
            return
        v = _norm_text(val)
        s = df[col].astype(str).map(_norm_text)
        df = df[s.str.contains(v, regex=False, na=False)]

    def by_anio(val: Any):
        nonlocal df
        if val in (None, ""):
            return
        an = _to_int(val)
        if an is None:
            return
        col = pd.to_numeric(df["anio"], errors="coerce")
        df = df[col.eq(an)]

    def by_estado(val: str):
        nonlocal df
        if not val:
            return
        tgt = _norm_text(val)
        s = df["estado"].astype(str).map(_norm_text)
        df = df[s.eq(tgt)]

    contains("marca", filters.get("marca", ""))
    contains("modelo", filters.get("modelo", ""))
    by_anio(filters.get("anio", ""))
    contains("nro_cuadro", filters.get("nro_cuadro", ""))
    contains("nro_motor", filters.get("nro_motor", ""))
    if filters.get("estado") is not None:
        by_estado(filters["estado"])

    return _ensure_cols(df, _VEHICULOS_BASE_COLS).reset_index(drop=True)

def write_vehiculos_df(df: pd.DataFrame) -> None:
    d = _ensure_cols(df, _VEHICULOS_BASE_COLS).copy()
    # precio como número
    if "precio" in d.columns:
        d["precio"] = d["precio"].apply(_to_float)
    _write_xlsx(VEHICULOS_XLSX, d, "vehiculos")

def get_vehiculo_by_id(vid: Any) -> Dict[str, Any]:
    df = load_vehiculos({})
    vid_int = _to_int(vid)
    idx = (
        (pd.to_numeric(df["id"], errors="coerce") == vid_int)
        if vid_int is not None else (df["id"].astype(str) == str(vid))
    )
    row = df.loc[idx]
    return {} if row.empty else row.iloc[0].to_dict()

def upsert_vehiculo(data: Dict[str, Any]) -> int:
    df = load_vehiculos({})
    d = _ensure_cols(pd.DataFrame([data]), _VEHICULOS_BASE_COLS).iloc[0].to_dict()

    if "id" not in d or d["id"] in (None, "", 0):
        new_id = int(pd.to_numeric(df["id"], errors="coerce").max() or 0) + 1
        d["id"] = new_id
        df = pd.concat([df, pd.DataFrame([d])], ignore_index=True)
        vid = new_id
    else:
        vid = _to_int(d["id"]) or 0
        idx = df.index[pd.to_numeric(df["id"], errors="coerce") == vid]
        if len(idx):
            for k, v in d.items():
                if k in df.columns:
                    df.loc[idx, k] = v
        else:
            df = pd.concat([df, pd.DataFrame([d])], ignore_index=True)
    write_vehiculos_df(df)
    return int(vid)

# ============================================================================
# PROVEEDORES
# ============================================================================
# Incluyo 'proveedor_id' como alias
_PROVEEDORES_BASE_COLS: List[str] = [
    "id", "proveedor_id", "nombre", "cuit", "email", "telefono", "direccion", "estado"
]

def load_proveedores(filters: Dict[str, Any] | None = None) -> pd.DataFrame:
    filters = filters or {}
    df = _read_xlsx(PROVEEDORES_XLSX, _PROVEEDORES_BASE_COLS)

    # Compat: si viene 'proveedor_id' y no 'id', renombro
    if "proveedor_id" in df.columns and "id" not in df.columns:
        df = df.rename(columns={"proveedor_id": "id"})

    # Alias proveedor_id
    try:
        empties = df["proveedor_id"].isna() | (df["proveedor_id"].astype(str).str.strip() == "")
        df.loc[empties, "proveedor_id"] = df.loc[empties, "id"]
    except Exception:
        df["proveedor_id"] = df.get("id", "")

    # Estado por defecto
    try:
        s = df["estado"].astype(str)
        df.loc[s.str.strip().isin(["", "nan", "none", "None"]), "estado"] = "Activo"
    except Exception:
        df["estado"] = "Activo"

    # Filtros
    def contains(col: str, val: str):
        nonlocal df
        if not val:
            return
        v = _norm_text(val)
        s = df[col].astype(str).map(_norm_text)
        df = df[s.str.contains(v, regex=False, na=False)]

    def by_estado(val: str):
        nonlocal df
        if not val:
            return
        tgt = _norm_text(val)
        s = df["estado"].astype(str).map(_norm_text)
        df = df[s.eq(tgt)]

    contains("nombre", filters.get("nombre", ""))
    contains("cuit", filters.get("cuit", ""))
    contains("email", filters.get("email", ""))
    if filters.get("estado") is not None:
        by_estado(filters["estado"])

    return _ensure_cols(df, _PROVEEDORES_BASE_COLS).reset_index(drop=True)

def write_proveedores_df(df: pd.DataFrame) -> None:
    d = df.copy()
    if "proveedor_id" in d.columns and "id" in d.columns:
        empties = d["proveedor_id"].isna() | (d["proveedor_id"].astype(str).str.strip() == "")
        d.loc[empties, "proveedor_id"] = d.loc[empties, "id"]
    d = _ensure_cols(d, _PROVEEDORES_BASE_COLS)
    _write_xlsx(PROVEEDORES_XLSX, d, "proveedores")

def get_proveedor_by_id(pid: Any) -> Dict[str, Any]:
    df = load_proveedores({})
    pid_int = _to_int(pid)
    idx = (
        (pd.to_numeric(df["id"], errors="coerce") == pid_int)
        if pid_int is not None else (df["id"].astype(str) == str(pid))
    )
    row = df.loc[idx]
    if row.empty and "proveedor_id" in df.columns:
        idx2 = (
            (pd.to_numeric(df["proveedor_id"], errors="coerce") == pid_int)
            if pid_int is not None else (df["proveedor_id"].astype(str) == str(pid))
        )
        row = df.loc[idx2]
    return {} if row.empty else row.iloc[0].to_dict()

def upsert_proveedor(data: Dict[str, Any]) -> int:
    df = load_proveedores({})
    d = {k: data.get(k, "") for k in _PROVEEDORES_BASE_COLS}

    raw_id = d.get("id") or d.get("proveedor_id")
    pid = _to_int(raw_id)

    if pid is None:
        new_id = int(pd.to_numeric(df["id"], errors="coerce").max() or 0) + 1
        d["id"] = new_id
        d["proveedor_id"] = new_id
        d["estado"] = "Activo"
        df = pd.concat([df, pd.DataFrame([d])], ignore_index=True)
        pid = new_id
    else:
        idx = df.index[
            (pd.to_numeric(df["id"], errors="coerce") == pid) |
            (pd.to_numeric(df.get("proveedor_id", pd.Series([None]*len(df))), errors="coerce") == pid)
        ]
        if len(idx):
            for col in _PROVEEDORES_BASE_COLS:
                if col in d and d[col] != "":
                    df.loc[idx, col] = d[col]
            df.loc[idx, "id"] = pid
            df.loc[idx, "proveedor_id"] = pid
        else:
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

# ============================================================================
# FACTURAS
# ============================================================================
# Extiendo tu base con fecha/CAE/vto_cae para integración con ARCA
_FACTURAS_BASE_COLS: List[str] = [
    "numero", "fecha",
    "cliente", "cuit_dni_cliente",
    "vehiculo", "patente",
    "tipo", "pago",
    "subtotal", "iva", "total",
    "cae", "vto_cae",
]

def load_facturas(filters: Dict[str, Any] | None = None) -> pd.DataFrame:
    filters = filters or {}
    df = _read_xlsx(FACTURAS_XLSX, _FACTURAS_BASE_COLS)

    # Aseguro tipos numéricos tolerantes
    for col in ["subtotal", "iva", "total"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    # Filtros básicos
    def contains(col: str, val: str):
        nonlocal df
        if not val:
            return
        v = _norm_text(val)
        s = df[col].astype(str).map(_norm_text)
        df = df[s.str.contains(v, regex=False, na=False)]

    contains("cliente", filters.get("cliente", ""))
    contains("vehiculo", filters.get("vehiculo", ""))

    return _ensure_cols(df, _FACTURAS_BASE_COLS).reset_index(drop=True)

def write_facturas_df(df: pd.DataFrame) -> None:
    d = _ensure_cols(df, _FACTURAS_BASE_COLS).copy()
    for col in ["subtotal", "iva", "total"]:
        if col in d.columns:
            d[col] = d[col].apply(_to_float)
    _write_xlsx(FACTURAS_XLSX, d, "facturas")

def append_factura(data: Dict[str, Any]) -> None:
    """
    Agrega una fila a facturas.xlsx garantizando columnas mínimas.
    Si faltan columnas nuevas (cae/vto_cae/fecha), se crean.
    """
    df = load_facturas({})
    # normalizo claves a minúscula para mapear
    normalized = {str(k).lower(): v for k, v in data.items()}
    # garantizo columnas
    for col in _FACTURAS_BASE_COLS:
        if col not in df.columns:
            df[col] = None
    # importes a float
    for k in ("subtotal", "iva", "total"):
        if k in normalized:
            normalized[k] = _to_float(normalized[k])

    new_row = {col: normalized.get(col, None) for col in _FACTURAS_BASE_COLS}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    write_facturas_df(df)

def _parse_numero(numero: str) -> Tuple[str, int] | None:
    """
    Devuelve (pto_venta, nro) si el patrón es 'PPPP-NNNNNNNN', si no None.
    """
    try:
        s = str(numero).strip()
        if "-" not in s:
            return None
        pv, nn = s.split("-", 1)
        if len(pv) != 4 or len(nn) != 8:
            return None
        return pv, int(nn)
    except Exception:
        return None

def get_ultimo_numero_factura(punto_venta: str = "0001") -> str:
    """
    Devuelve el próximo número correlativo 'PPPP-NNNNNNNN' para el punto de venta dado.
    - Si el Excel está vacío, arranca en 'PPPP-00000001'.
    - Si hay números en otro formato, los ignora para el cómputo.
    - Calcula el máximo por pto. de venta (no solo el último row).
    """
    df = load_facturas({})
    pv = str(punto_venta).zfill(4)

    if df.empty or df["numero"].isna().all():
        return f"{pv}-00000001"

    # Filtra por punto de venta y toma máximo numérico válido
    candidatos = []
    for n in df["numero"].astype(str).tolist():
        parsed = _parse_numero(n)
        if parsed and parsed[0] == pv:
            candidatos.append(parsed[1])

    if not candidatos:
        # no hay números para ese PV todavía
        return f"{pv}-00000001"

    nxt = max(candidatos) + 1
    return f"{pv}-{str(nxt).zfill(8)}"
