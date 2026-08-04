# ==========================================
# MODULO INDICADORES
# Dashboard MacroFin
# ==========================================

import pandas as pd
import numpy as np
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

    # CÁLCULO DE CRECIMIENTO ANUAL DE DEPÓSITOS (MENSUAL)
    # Detectamos el nombre de la columna de depósitos
    col_dep = "6. Depósitos del Público" if "6. Depósitos del Público" in df.columns else "Depósitos del Público"

    if col_dep in df.columns:
        # Ordenamos por entidad y fecha
        df = df.sort_values(["Sigla", "Fecha"]).reset_index(drop=True)
    
        # Calculamos la variación porcentual respecto al mismo mes del año anterior (shift de 12 meses)
        df["Crecimiento Depósitos"] = df.groupby("Sigla")[col_dep].pct_change(12) * 100
        df["Crecimiento Depósitos"] = df["Crecimiento Depósitos"].fillna(0.0)
    else:
        df["Crecimiento Depósitos"] = 0.0

    # --------------------------------------
    # AñoMes
    # --------------------------------------
    df[COLUMNAS["anio_mes"]] = (
        df[COLUMNAS["fecha"]]
        .dt.strftime("%Y-%m")
    )

    return df

@st.cache_data
def cargar_indicadores_diarios():
    """
    Carga, limpia y calcula indicadores diarios alineando las fechas de 2026 
    con su día correspondiente de 2025.
    """
    ruta_excel = "data/Base MacroFin.xlsx"
    
    # 1. Cargar desde la fila 5 (header=4)
    df = pd.read_excel(ruta_excel, sheet_name="Indicadores dia", header=4)
    df.columns = [str(col).strip() for col in df.columns]

    # 2. Rellenar celdas combinadas/vacías hacia abajo
    if "Fecha" in df.columns:
        df["Fecha"] = df["Fecha"].ffill()
    if "Tipo Entidad" in df.columns:
        df["Tipo Entidad"] = df["Tipo Entidad"].ffill()
        
    # Convertir a datetime.date
    df["Fecha"] = pd.to_datetime(df["Fecha"]).dt.date
    
    # Convertir columnas numéricas a float por si vienen formateadas como texto
    cols_numericas = [c for c in df.columns if c not in ["Fecha", "Tipo Entidad", "Sigla"]]
    for col in cols_numericas:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # 3. Validar / Asegurar el Índice de Mora
    if "Indice de mora" not in df.columns or df["Indice de mora"].sum() == 0:
        col_mora = "2. Mora" if "2. Mora" in df.columns else "Cartera En Mora"
        if col_mora in df.columns and "1. Cartera Bruta" in df.columns:
            df["Indice de mora"] = np.where(
                df["1. Cartera Bruta"] > 0,
                (df[col_mora] / df["1. Cartera Bruta"]) * 100,
                0
            )

    # 4. CÁLCULO DE VARIACIÓN ANUAL (Mismo orden diario de 2026 vs 2025)
    # Separamos 2025 y 2026 para cada Entidad
    dfs_procesados = []
        
    for sigla, df_grupo in df.groupby("Sigla"):
        df_grupo = df_grupo.sort_values("Fecha").copy()
            
        # Filtramos por año
        df_2025 = df_grupo[df_grupo["Fecha"].apply(lambda x: getattr(x, "year", None) == 2025)].reset_index(drop=True)
        df_2026 = df_grupo[df_grupo["Fecha"].apply(lambda x: getattr(x, "year", None) == 2026)].reset_index(drop=True)
            
        if not df_2026.empty:
            # Inicializamos las columnas de variación en 0.0
            df_2026["Crecimiento Cartera"] = 0.0
            df_2026["Crecimiento Depósitos"] = 0.0
                
            if not df_2025.empty:
                n_min = min(len(df_2026), len(df_2025))
                    
                if n_min > 0:
                    # --- 1. CARTERA BRUTA ---
                    v_cart_2026 = df_2026.loc[:n_min - 1, "1. Cartera Bruta"].values
                    v_cart_2025 = df_2025.loc[:n_min - 1, "1. Cartera Bruta"].values
                    mask_cart = v_cart_2025 > 0
                        
                    var_cart = np.zeros(n_min)
                    var_cart[mask_cart] = ((v_cart_2026[mask_cart] - v_cart_2025[mask_cart]) / v_cart_2025[mask_cart]) * 100
                    df_2026.loc[:n_min - 1, "Crecimiento Cartera"] = var_cart

                    # --- 2. DEPÓSITOS DEL PÚBLICO ---
                    # Ajusta el nombre exacto de la columna en tu Excel si difiere (ej. "6. Depósitos del Público")
                    col_dep = "6. Depósitos del Público" if "6. Depósitos del Público" in df_2026.columns else "Depósitos del Público"
                        
                    if col_dep in df_2026.columns:
                        v_dep_2026 = df_2026.loc[:n_min - 1, col_dep].values
                        v_dep_2025 = df_2025.loc[:n_min - 1, col_dep].values
                        mask_dep = v_dep_2025 > 0
                            
                        var_dep = np.zeros(n_min)
                        var_dep[mask_dep] = ((v_dep_2026[mask_dep] - v_dep_2025[mask_dep]) / v_dep_2025[mask_dep]) * 100
                        df_2026.loc[:n_min - 1, "Crecimiento Depósitos"] = var_dep
                    else:
                        df_2026["Crecimiento Depósitos"] = 0.0
            
        dfs_procesados.append(pd.concat([df_2025, df_2026]))

    if dfs_procesados:
        df_final = pd.concat(dfs_procesados, ignore_index=True)
    else:
        df_final = df

    df_final = df_final.sort_values("Fecha").reset_index(drop=True)
    return df_final
































    