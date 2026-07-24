import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import time
#from modules.graficos import crear_trayectorias
from modules.indicadores import cargar_indicadores
from modules.graficos import crear_dispersion
from modules.filtros import aplicar_filtros
from modules.config import COLUMNAS
from modules.analisis import (
    clasificar_cuadrantes,
    resumen_periodo,
    generar_hallazgos,
)
from modules.temporal import EstadoTemporal

st.set_page_config(
    page_title="Plataforma de Inteligencia para el Sistema Financiero",
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

df_ind = cargar_indicadores()
#periodos = sorted(df_original["AñoMes"].unique())

# ==========================================
# FILTRO FECHA
# ==========================================

#fechas = sorted(
    #df_ind["Fecha"].unique()
#)

#fecha_sel = st.sidebar.selectbox(

    #"📅 Fecha",

    #options=fechas,

    #index=len(fechas)-1,

    #format_func=lambda x: x.strftime("%d/%m/%Y")

#)

# ==========================================
# FILTRO TIPO ENTIDAD
# ==========================================

tipos = sorted(

    df_ind["Tipo Entidad"]

    .dropna()

    .unique()

)

tipos_sel = st.sidebar.multiselect(

    "🏦 Tipo de entidad",

    options=tipos,

    default=tipos

)

# ==========================================
# SIGLAS DISPONIBLES EN LA FECHA
# ==========================================

siglas = sorted(

    df_ind[
        df_ind["Tipo Entidad"].isin(tipos_sel)
    ]["Sigla"]
    .dropna()
    .unique()

)
siglas_sel = st.sidebar.multiselect(

    "🏦 Siglas",

    options=siglas,

    default=siglas

)

# ==========================================
# TÍTULO
# ==========================================

st.title("📊 Plataforma de Inteligencia para el Sistema Financiero")
st.markdown("---")

#st.subheader("Validación de la carga de datos")


# ==========================================
# DATAFRAME ANÁLISIS
# ==========================================

# ==========================================
# HISTÓRICO (SIN FILTRAR POR FECHA)
# ==========================================

df_historico = aplicar_filtros(
    df=df_ind,
    fecha=None,
    tipo_entidad=tipos_sel,
    siglas=siglas_sel
)

# ==========================================
# ESTADO Y SESIÓN TEMPORAL
# ==========================================
if "indice_periodo" not in st.session_state:
    st.session_state.indice_periodo = 0

if "reproduciendo" not in st.session_state:
    st.session_state.reproduciendo = False

estado = EstadoTemporal(df_historico)

estado.indice = min(
    st.session_state.indice_periodo,
    len(estado.periodos) - 1
)

# ==========================================
# KPIs
# ==========================================

col1, col2, col3, col4 = st.columns(4)

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
        "Tipos de entidad",
        df_ind["Tipo Entidad"].nunique()
    )

with col4:
    st.metric(
        "Meses",
        df_ind["Fecha"].dt.to_period("M").nunique()
    )

st.markdown("---")

# ==========================================
# PRIMERAS FILAS
# ==========================================
#st.subheader("Primeras filas")
#st.dataframe(
    #df_ind.head(15),
    #use_container_width=True,
    #hide_index=True
#)

# ==========================================
# ÚLTIMAS FILAS
# ==========================================
#st.subheader("Últimas filas")
#st.dataframe(
    #df_ind.tail(15),
    #use_container_width=True,
    #hide_index=True
#)

# ==========================================
# INFORMACIÓN DEL DATAFRAME
# ==========================================
#with st.expander("Información del DataFrame"):
    #st.write("Dimensiones:")
    #st.write(df_ind.shape)
    #st.write("Columnas:")
    #st.write(df_ind.columns.tolist())
    #st.write("Tipos de datos:")
    #st.write(df_ind.dtypes)

        
# ==========================================
# PRIMER GRÁFICO
# ==========================================

# ==========================================
# PANEL TEMPORAL
# ==========================================

col1, col2, col3, col4, col5 = st.columns([1, 1, 4, 1, 1])

with col1:
    btn_inicio = st.button("⏮", use_container_width=True)

with col2:
    btn_anterior = st.button("◀", use_container_width=True)

with col3:
    st.markdown(
        f"<h3 style='text-align:center;'>📅 {estado.periodo_actual.strftime('%d/%m/%Y')}</h3>",
        unsafe_allow_html=True
    )

with col4:
    btn_siguiente = st.button("▶", use_container_width=True)

with col5:
    btn_final = st.button("⏭", use_container_width=True)

# ==========================================
# EVENTOS PANEL TEMPORAL
# ==========================================

if btn_inicio:
    estado.ir_al_inicio()
    st.session_state.indice_periodo = estado.indice
    st.rerun()

if btn_anterior:
    estado.retroceder()
    st.session_state.indice_periodo = estado.indice
    st.rerun()

if btn_siguiente:
    st.session_state.indice_periodo = 0
    st.session_state.reproduciendo = True
    st.rerun()
#st.write(st.session_state.reproduciendo)

if btn_final:
    estado.ir_al_final()
    st.session_state.indice_periodo = estado.indice
    st.rerun()

# ==========================================
# REPRODUCCIÓN AUTOMÁTICA
# ==========================================

if st.session_state.reproduciendo:
    time.sleep(0.5)  # Ajusta la velocidad

    if estado.indice < len(estado.periodos) - 1:
        estado.avanzar()
        st.session_state.indice_periodo = estado.indice
        st.rerun()

    else:
        st.session_state.reproduciendo = False
        st.rerun()
        
df_filtrado = estado.datos_actuales()

#temporal
print(df_historico["Fecha"].unique())

df_analisis = clasificar_cuadrantes(
    df_filtrado,
    eje_x="Crecimiento Cartera",
    eje_y="Indice de mora"
)
resumen = resumen_periodo(df_analisis)
hallazgos = generar_hallazgos(df_analisis)
st.subheader("🧠 Panel del Analista")

for h in hallazgos:

    st.info(

        f"**{h['titulo']}**\n\n"

        f"{h['mensaje']}"

    )

fig = crear_dispersion(
    df=df_analisis,
    df_historico=df_historico,
    eje_x="Crecimiento Cartera",
    eje_y="Indice de mora",
    tamaño="10. Activo",
    color="Tipo Entidad",
    texto=COLUMNAS["sigla"],
    titulo="Crecimiento Anual de Cartera vs Índice de Mora",
    fecha_actual=estado.periodo_actual  # Se envía la fecha seleccionada
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.subheader("📌 Resumen del período")

#st.write(type(resumen))
#st.write(resumen)

for fila in resumen:

    st.write(

        f"• {fila['Cantidad']} entidades "

        f"({fila['Porcentaje']:.1f}%) "

        f"se encuentran en "

        f"**{fila['Estado']}**."

    )

#st.markdown("---")

#st.subheader("📈 Evolución Histórica de las Entidades")

#fig_tray = crear_trayectorias(
    #df=df_ind,
    #eje_x="Crecimiento Cartera",
    #eje_y="Indice de mora",
    #color="Sigla",
    #texto="Sigla",
    #titulo=""
#)

#st.plotly_chart(
    #fig_tray,
    #use_container_width=True
#)

# ==========================================
# TEMPORAL
# ==========================================
#st.subheader("Validación gráfico")

#st.write(df_ind[
    #[
        #"Sigla",
        #"Crecimiento Cartera",
        #"Indice de mora",
        #"10. Activo"
    #]
#].tail(20))





























































