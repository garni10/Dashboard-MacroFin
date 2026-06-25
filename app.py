import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="Dashboard MacroFin",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>

/* Contenedor de pestañas */
div[data-baseweb="tab-list"]{
    gap:20px;
}

/* Pestañas */
button[data-baseweb="tab"]{
    font-size:26px !important;
    font-weight:700 !important;
    padding:14px 28px !important;
    height:60px !important;
    border-radius:8px 8px 0px 0px;
}

/* Texto */
button[data-baseweb="tab"] p{
    font-size:26px !important;
    font-weight:700 !important;
}

/* Pestaña activa */
button[data-baseweb="tab"][aria-selected="true"]{
    color:#4FC3F7 !important;
}

/* Línea inferior */
div[data-baseweb="tab-highlight"]{
    height:4px;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# CARGA DE DATOS
# ==========================================

@st.cache_data(ttl=300)
def cargar_indicadores():

    df = pd.read_excel(
        "data/Base MacroFin.xlsx",
        sheet_name="Indicadores",
        header=4
    )

    
    # LIMPIEZA DE DATOS
   
    #Rellenar fecha
    df["Fecha"] = df["Fecha"].ffill()
    #Rellenar fecha
    df["Tipo Entidad"] = df["Tipo Entidad"].ffill()
    #Remplazar depòsitos vacíos
    df["Depósitos"] = (
        pd.to_numeric(
            df["Depósitos"],
            errors="coerce"
        )
        .fillna(0)
    )
    #Convertir fecha
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    #Convertir todas las variables numérica
    columnas = [
        "Cartera Bruta",
        "Activo",
        "Mora",
        "Depósitos",
        "Depósitos a Plazo",
        "Caja de Ahorro",
        "Indice de mora"
    ]
    
    for col in columnas:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )
    #Ordenar
    df = df.sort_values(
        ["Sigla","Fecha"]
    )
    #Tasas de crecimiento
    df["Crecimiento Cartera"] = (
        df.groupby("Sigla")["Cartera Bruta"]
          .pct_change(12)
    )

    df["Crecimiento Depositos"] = (
        df.groupby("Sigla")["Depósitos"]
          .pct_change(12)
    )
    #Crear año mes
    df["AñoMes"] = (
        df["Fecha"]
        .dt.strftime("%Y-%m")
    )

    return df

# ==========================================
# FUNCIONES AUXILIARES
# ==========================================

def fin_filtrar_indicadores(
        df,
        fecha=None,
        tipo_entidad=None,
        siglas=None):

    datos = df.copy()

    if fecha is not None:
        datos = datos[
            datos["Fecha"] == fecha
        ]

    if tipo_entidad is not None:
        datos = datos[
            datos["Tipo Entidad"].isin(tipo_entidad)
        ]

    if siglas is not None:
        datos = datos[
            datos["Sigla"].isin(siglas)
        ]

    return datos

# ==========================================
# DATAFRAME
# ==========================================

df_ind = cargar_indicadores()

# ==========================================
# TITULO
# ==========================================

st.title("📊 Dashboard MacroFin")

st.markdown("---")

# ==========================================
# Posicionamiento
# ==========================================

#Pestañas
tab1 = st.tabs(
    [
        "🏦 Indicadores Financieros"
    ]
)[0]

#Contenido
with tab1:

    st.header("🏦 Indicadores Financieros")

    #KPIs
    col1,col2,col3,col4 = st.columns(4)
    with col1:
        st.metric(
            "Registros",
            len(df_ind)
        )
    
    with col2:
        st.metric(
            "Entidades",
            df_ind["Sigla"].nunique()
        )
    
    with col3:
        st.metric(
            "Tipos de Entidad",
            df_ind["Tipo Entidad"].nunique()
        )
    
    with col4:
        st.metric(
            "Meses",
            df_ind["Fecha"].dt.to_period("M").nunique()
        )

    #Mostrar último mes
    ultimo_mes = df_ind["Fecha"].max()
    
    df_mes = fin_filtrar_indicadores(
        df_ind,
        fecha=ultimo_mes
    )

    st.markdown("---")

    st.subheader(
        f"Información correspondiente a {ultimo_mes:%m/%Y}"
    )
    
    st.dataframe(
        df_mes,
        use_container_width=True,
        hide_index=True
    )


























