# ==========================================
# FILTROS
# Dashboard MacroFin
# ==========================================

import pandas as pd


def aplicar_filtros(
    df,
    fecha=None,
    tipo_entidad=None,
    siglas=None
):
    """
    Aplica todos los filtros del Dashboard.
    """

    df_filtrado = df.copy()

    # ------------------------
    # Fecha
    # ------------------------

    if fecha is not None:

        df_filtrado = df_filtrado[
            df_filtrado["Fecha"] == fecha
        ]

    # ----------------------------------
    # Tipo de entidad
    # ----------------------------------
    
    if tipo_entidad:
    
        df_filtrado = df_filtrado[
    
            df_filtrado["Tipo Entidad"]
    
            .isin(tipo_entidad)
    
        ]
    
    # ------------------------
    # Siglas
    # ------------------------

    if siglas:

        df_filtrado = df_filtrado[
            df_filtrado["Sigla"].isin(siglas)
        ]

    return df_filtrado