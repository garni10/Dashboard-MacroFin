# ==========================================
# MODULO INDICADORES
# Dashboard MacroFin
# ==========================================

import pandas as pd
import streamlit as st

from modules.config import (
    ARCHIVO_EXCEL,
    HOJA_INDICADORES,
    CACHE_TTL,
    COLUMNAS
)

@st.cache_data(ttl=CACHE_TTL)
def cargar_indicadores():
    """
    Lee, limpia y prepara la hoja
    'Indicadores' del archivo Base MacroFin.
    """

    # --------------------------------------
    # Leer Excel
    # --------------------------------------
    df = pd.read_excel(
        ARCHIVO_EXCEL,
        sheet_name=HOJA_INDICADORES,
        header=4
    )
    
    # --------------------------------------
    # Completar valores faltantes
    # --------------------------------------
    df[COLUMNAS["fecha"]] = df[COLUMNAS["fecha"]].ffill()

    df[COLUMNAS["tipo_entidad"]] = (
        df[COLUMNAS["tipo_entidad"]].ffill()
    )

    # --------------------------------------
    # Fecha
    # --------------------------------------
    df[COLUMNAS["fecha"]] = pd.to_datetime(
        df[COLUMNAS["fecha"]]
    )

    # --------------------------------------
    # Depósitos
    # --------------------------------------
    print(COLUMNAS)
    print(COLUMNAS["depositos"])
    
    df[COLUMNAS["depositos"]] = (
        pd.to_numeric(
            df[COLUMNAS["depositos"]],
            errors="coerce"
        )
        .fillna(0)
    )

    # --------------------------------------
    # Variables numéricas
    # --------------------------------------
    columnas_numericas = [

        COLUMNAS["cartera"],
        COLUMNAS["activo"],
        COLUMNAS["mora"],
        COLUMNAS["depositos"],
        COLUMNAS["depositos_plazo"],
        COLUMNAS["caja_ahorro"],
        COLUMNAS["indice_mora"]

    ]

    for col in columnas_numericas:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # --------------------------------------
    # Ordenar
    # --------------------------------------
    df = df.sort_values(
        [
            COLUMNAS["sigla"],
            COLUMNAS["fecha"]
        ]
    )

    # --------------------------------------
    # Crecimiento anual cartera
    # --------------------------------------
    df[COLUMNAS["crecimiento_cartera"]] = (
        df.groupby(COLUMNAS["sigla"])[COLUMNAS["cartera"]]
          .pct_change(12)
          * 100
    )

    # --------------------------------------
    # Crecimiento anual depósitos
    # --------------------------------------
    df[COLUMNAS["crecimiento_depositos"]] = (
        df.groupby(COLUMNAS["sigla"])[COLUMNAS["depositos"]]
          .pct_change(12)
          * 100
    )

    # --------------------------------------
    # AñoMes
    # --------------------------------------
    df[COLUMNAS["anio_mes"]] = (
        df[COLUMNAS["fecha"]]
        .dt.strftime("%Y-%m")
    )

    return df