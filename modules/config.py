# ==========================================
# CONFIGURACIÓN GENERAL
# Dashboard MacroFin
# ==========================================

# Archivo principal de datos
ARCHIVO_EXCEL = "data/Base MacroFin.xlsx"

# Hoja de indicadores
HOJA_INDICADORES = "Indicadores"

# Tiempo de cache (segundos)
CACHE_TTL = 300

# Columnas del archivo Excel
COLUMNAS = {

    # Identificación
    "fecha": "Fecha",
    "tipo_entidad": "Tipo Entidad",
    "sigla": "Sigla",

    # Variables financieras
    "cartera": "1. Cartera Bruta",
    "activo": "10. Activo",
    "mora": "2. Mora",

    "depositos": "6. Depósitos del Público",
    "depositos_plazo": "6.1. Depósitos a Plazo Fijo",
    "caja_ahorro": "6.2. Depósitos en Caja de Ahorro",

    "indice_mora": "Indice de mora",

    "crecimiento_cartera": "Crecimiento Cartera",

    "crecimiento_depositos": "Crecimiento Depositos",

    "anio_mes": "AñoMes"

}

# ==========================================
# COLORES INSTITUCIONALES
# ==========================================

COLORES = {

    "BANCOS MULTIPLES": "#1f77b4",

    "ENTIDADES ESPECIALIZADAS EN MICROCRÉDITO": "#2ca02c",

    "INSTITUCIONES FINANCIERAS DE DESARROLLO": "#ff7f0e",

    "COOPERATIVAS": "#d62728"

}

# ==========================================
# TÍTULOS DEL DASHBOARD
# ==========================================

TITULOS = {

    "principal": "📊 Dashboard MacroFin",

    "dispersion_mora":
        "Análisis de Posicionamiento:\n"
        "Crecimiento Anual de Cartera vs Índice de Mora"

}

# ==========================================
# TAMAÑO DE BURBUJAS
# ==========================================

TAM_BURBUJA = 55

# ==========================================
# FORMATO DE HOVER
# ==========================================

HOVER = {

    "activo": ":,.0f",

    "cartera": ":,.0f",

    "depositos": ":,.0f",

    "crecimiento": ".2f",

    "mora": ".2f"

}

# ==========================================
# INTERPRETACIÓN CUADRANTES
# ==========================================

CUADRANTES = {

    "dispersion_mora": {

        "Q1": "Riesgo",

        "Q2": "Crecimiento con Riesgo",

        "Q3": "Conservador",

        "Q4": "Liderazgo"

    }

}

# ==========================================
# POSICIÓN RELATIVA DE LOS TÍTULOS
# ==========================================

POSICION_CUADRANTES = {

    "Riesgo": (0.18, 0.88),

    "Crecimiento con Riesgo": (0.82, 0.88),

    "Conservador": (0.18, 0.18),

    "Liderazgo": (0.88, 0.18)

}

# ==========================================
# TRAYECTORIAS
# ==========================================
TRAYECTORIA = {
    "MESES": 12,
    "ANCHO": 1.5,
    "OPACIDAD": 0.15,
    "COLOR": "rgba(180,180,180,0.20)"
}






























































