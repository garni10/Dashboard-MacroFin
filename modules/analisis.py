# ==========================================
# MOTOR ANALÍTICO
# Dashboard MacroFin
# ==========================================

import pandas as pd
from modules.config import CUADRANTES
def clasificar_cuadrantes(df, eje_x="Crecimiento Cartera", eje_y="Indice de mora"):
    """
    Clasifica cada entidad en un cuadrante en función de los promedios de los ejes X e Y.
    Soporta lógica adaptativa según la variable elegida para el eje Y.
    """
    if df.empty or eje_x not in df.columns or eje_y not in df.columns:
        return df

    prom_x = df[eje_x].mean()
    prom_y = df[eje_y].mean()

    def determinar_cuadrante(row):
        val_x = row[eje_x]
        val_y = row[eje_y]

        if pd.isna(val_x) or pd.isna(val_y):
            return "Sin datos"

        # MATRIZ 1: Cartera vs Índice de Mora
        if eje_y == "Indice de mora":
            if val_x >= prom_x and val_y < prom_y:
                return "Liderazgo"            # Q4: Alto Crecimiento, Baja Mora
            elif val_x >= prom_x and val_y >= prom_y:
                return "Crecimiento con Riesgo" # Q1: Alto Crecimiento, Alta Mora
            elif val_x < prom_x and val_y >= prom_y:
                return "Riesgo"               # Q2: Bajo Crecimiento, Alta Mora
            else:
                return "Conservador"          # Q3: Bajo Crecimiento, Baja Mora

        # MATRIZ 2: Cartera vs Crecimiento Depósitos (u otras tasas de crecimiento)
        else:
            if val_x >= prom_x and val_y >= prom_y:
                return "Liderazgo"            # Q1: Alto Crec. Cartera, Alto Crec. Depósitos
            elif val_x < prom_x and val_y >= prom_y:
                return "Captador / Expansivo" # Q2: Bajo Crec. Cartera, Alto Crec. Depósitos
            elif val_x < prom_x and val_y < prom_y:
                return "Rezago / Estancado"   # Q3: Bajo Crec. Cartera, Bajo Crec. Depósitos
            else:
                return "Otorgador / Descalce" # Q4: Alto Crec. Cartera, Bajo Crec. Depósitos

    df["Cuadrante"] = df.apply(determinar_cuadrante, axis=1)
    return df

def generar_resumen_inteligente(df_analisis, eje_y_label, variable_y):
    """
    Genera un texto analítico dinámico según la distribución en los cuadrantes.
    """
    if df_analisis.empty or "Cuadrante" not in df_analisis.columns:
        return "No hay suficientes datos para generar el resumen del período."

    total_entidades = len(df_analisis)
    conteo_cuadrantes = df_analisis["Cuadrante"].value_counts()
    
    # Entidades en la mejor posición (Liderazgo)
    lideres = df_analisis[df_analisis["Cuadrante"] == "Liderazgo"]["Sigla"].tolist()
    str_lideres = ", ".join(lideres[:4]) if lideres else "Ninguna"
    if len(lideres) > 4:
        str_lideres += f" y {len(lideres)-4} más"

    if variable_y == "Indice de mora":
        resumen = f"""
        > **📌 Diagnóstico de Riesgo y Crecimiento:**  
        > Se analizaron **{total_entidades} entidades**. De ellas, **{len(lideres)}** se posicionan en el cuadrante de **Liderazgo** ({str_lideres}), 
        > logrando una expansión de cartera superior al promedio del sector con niveles de morosidad bajo control. 
        """
    else:
        resumen = f"""
        > **📌 Diagnóstico de Liquidez y Expansión:**  
        > En la relación Cartera vs Depósitos, **{len(lideres)} entidades** figuran en **Liderazgo** ({str_lideres}), 
        > respaldando eficientemente la colocación de créditos con un sólido crecimiento en la captación de depósitos del público.
        """

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

# ----------------------------------
# SISTEMA FINANCIERO
# ----------------------------------

import numpy as np

def agregar_promedio_sistema(df_actual, df_base_tipos):
    """
    Calcula el promedio del sistema considerando los 'Tipos de entidad' seleccionados
    (ignora el filtro de Siglas para reflejar la media real del sector).
    """
    if df_base_tipos.empty:
        return df_actual

    # Columnas numéricas a promediar
    cols_num = df_base_tipos.select_dtypes(include=["number"]).columns
    
    # Promedio ponderado o simple de las variables clave del día
    promedios = df_base_tipos[cols_num].mean().to_dict()
    
    # Creamos la fila del Promedio del Sistema
    fila_promedio = {
        "Fecha": df_actual["Fecha"].iloc[0] if not df_actual.empty else None,
        "Tipo Entidad": "PROMEDIO SISTEMA",
        "Sigla": "SISTEMA",
        **promedios
    }
    
    df_prom = pd.DataFrame([fila_promedio])
    
    # Concatenamos la fila al dataset actual
    return pd.concat([df_actual, df_prom], ignore_index=True)


def resumen_periodo(df_analisis):
    """
    Genera la estructura de resumen por cuadrante con Cantidad y Porcentaje.
    """
    if df_analisis.empty or "Cuadrante" not in df_analisis.columns:
        return []
        
    total = len(df_analisis)
    
    # Agrupamos por el nombre del Cuadrante
    resumen_df = (
        df_analisis.groupby("Cuadrante")
        .size()
        .reset_index(name="Cantidad")
    )
    
    # Calculamos el porcentaje
    resumen_df["Porcentaje"] = (resumen_df["Cantidad"] / total) * 100
    resumen_df.rename(columns={"Cuadrante": "Estado"}, inplace=True)
    
    # Ordenamos de mayor a menor cantidad
    resumen_df = resumen_df.sort_values("Cantidad", ascending=False)
    
    return resumen_df.to_dict("records")


























    