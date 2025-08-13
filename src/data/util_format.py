import locale

# Intentar configurar la localización del sistema para formato de moneda
try:
    locale.setlocale(locale.LC_ALL, '')
except locale.Error:
    pass

def format_currency(value) -> str:
    """
    Devuelve el valor formateado como moneda local.
    Si no es numérico, lo devuelve como string.
    """
    try:
        return locale.currency(float(value), grouping=True, symbol=True)
    except (ValueError, TypeError):
        return str(value)
