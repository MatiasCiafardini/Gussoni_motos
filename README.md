# App_gestion (Agencia de Motos)

Aplicación de escritorio con PySide6. UI tipo Bootstrap con QSS.  
Carga datos desde Excel (por ahora) con filtros y tablas vacías por defecto.

## Ejecución
1. Crea un entorno e instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Ejecuta:
   ```bash
   python app/main.py
   ```

## Estructura
- `app/main.py` — arranque de la app y tema.
- `src/ui/main_window.py` — ventana principal con menú lateral y navegación.
- `src/ui/theme.py` — QSS estilo Bootstrap.
- `src/ui/pages/` — páginas (dashboard, clientes, vehículos, facturación, reportes, configuración).
- `src/data/` — helpers y rutas.
- `data/*.xlsx` — Excels de ejemplo (se crean al arrancar si no existen).

## Notas
- Solo hay una ventana emergente por flujo: el perfil (cliente o vehículo) para ver/agregar/editar/eliminar.
- Los listados comienzan vacíos; usa los filtros + botón "Buscar" para cargar desde Excel.
