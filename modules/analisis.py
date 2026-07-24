# ==========================================
# MOTOR ANALÍTICO
# Dashboard MacroFin
# ==========================================

import pandas as pd
from modules.config import CUADRANTES
def clasificar_cuadrantes(
    df,
    eje_x,
    eje_y,
    nombre="dispersion_mora"
):
    promedio_x = df[eje_x].mean()
    
    promedio_y = df[eje_y].mean()
    
    df = df.copy()

    # ----------------------------------
    # Columna cuadrante
    # ----------------------------------
    
    df["Cuadrante"] = ""

    # ----------------------------------
    # Riesgo
    # ----------------------------------
    
    mask = (
    
        (df[eje_x] < promedio_x)
    
        &
    
        (df[eje_y] >= promedio_y)
    
    )
    
    df.loc[mask, "Cuadrante"] = (
    
        CUADRANTES[nombre]["Q1"]
    
    )

    # ----------------------------------
    # Crecimiento con Riesgo
    # ----------------------------------
    
    mask = (
    
        (df[eje_x] >= promedio_x)
    
        &
    
        (df[eje_y] >= promedio_y)
    
    )
    
    df.loc[mask, "Cuadrante"] = (
    
        CUADRANTES[nombre]["Q2"]
    
    )

    # ----------------------------------
    # Conservador
    # ----------------------------------
    
    mask = (
    
        (df[eje_x] < promedio_x)
    
        &
    
        (df[eje_y] < promedio_y)
    
    )
    
    df.loc[mask, "Cuadrante"] = (
    
        CUADRANTES[nombre]["Q3"]
    
    )

    # ----------------------------------
    # Liderazgo
    # ----------------------------------
    
    mask = (
    
        (df[eje_x] >= promedio_x)
    
        &
    
        (df[eje_y] < promedio_y)
    
    )
    
    df.loc[mask, "Cuadrante"] = (
    
        CUADRANTES[nombre]["Q4"]
    
    )
    
    return df

def resumen_periodo(df):

    conteo = (
        df["Cuadrante"]
        .value_counts()
    )

    total = len(df)

    resumen = []

    for estado, cantidad in conteo.items():

        porcentaje = cantidad / total * 100

        resumen.append({

            "Estado": estado,

            "Cantidad": cantidad,

            "Porcentaje": porcentaje

        })

    return resumen

def analizar_situacion_general(df):

    resumen = resumen_periodo(df)

    favorables = 0
    riesgo = 0

    for fila in resumen:

        if fila["Estado"] in [
            "Liderazgo",
            "Conservador"
        ]:
            favorables += fila["Cantidad"]

        else:
            riesgo += fila["Cantidad"]

    total = favorables + riesgo

    return {

        "tipo": "general",

        "titulo": "Situación General",

        "mensaje":

        f"El {favorables/total*100:.1f}% de las entidades "
        f"se ubica en estados favorables, mientras "
        f"que el {riesgo/total*100:.1f}% presenta "
        f"niveles de riesgo superiores al promedio."

    }

def generar_hallazgos(df):

    hallazgos = []

    hallazgos.append(
        analizar_situacion_general(df)
    )

    return hallazgos































    