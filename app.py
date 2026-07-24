import streamlit as st
import pandas as pd
import numpy as np
import time

from modules.indicadores import cargar_indicadores
from modules.graficos import crear_dispersion
from modules.filtros import aplicar_filtros
from modules.config import COLUMNAS
from modules.analisis import (
    clasificar_cuadrantes,
    resumen_periodo,
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
div[data-baseweb="tab-list"]{ gap:20px; }

/* Pestañas */
button[data-baseweb="tab"]{ font-size:26px !important; font-weight:700 !important; padding:14px 28px !important; height:60px !important; }
button[data-baseweb="tab"] p{ font-size:26px !important; font-weight:700 !important; }
button[data-baseweb="tab"][aria-selected="true"]{ color:#4FC3F7 !important; }
div[data-baseweb="tab-highlight"]{ height:4px; }

/* Estilo para alineación del botón Play/Pausa con el Slider */
.stButton > button {
    margin-top: 18px;
    height: 48px !important;
    font-size: 20px !important;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# CARGA DE DATOS
# ==========================================
df_ind = cargar_indicadores()

# ==========================================
# FILTROS LATERALES (SIDEBAR)
# ==========================================
tipos = sorted(df_ind["Tipo Entidad"].dropna().unique())
tipos_sel = st.sidebar.multiselect("🏦 Tipo de entidad", options=tipos, default=tipos)

siglas = sorted(df_ind[df_ind["Tipo Entidad"].isin(tipos_sel)]["Sigla"].dropna().unique())
siglas_sel = st.sidebar.multiselect("🏦 Siglas", options=siglas, default=siglas)

# Histórico filtrado
df_historico = aplicar_filtros(
    df=df_ind,
    fecha=None,
    tipo_entidad=tipos_sel,
    siglas=siglas_sel
)

estado = EstadoTemporal(df_historico)

# ==========================================
# CONTROL DE ESTADO EN SESSION
# ==========================================
if "indice_periodo" not in st.session_state:
    st.session_state.indice_periodo = 0

if "reproduciendo" not in st.session_state:
    st.session_state.reproduciendo = False

# Ajustar índice dentro de rangos válidos
if estado.periodos:
    st.session_state.indice_periodo = max(0, min(st.session_state.indice_periodo, len(estado.periodos) - 1))
    estado.indice = st.session_state.indice_periodo

# ==========================================
# TÍTULO E KPIs
# ==========================================
st.title("📊 Plataforma de Inteligencia para el Sistema Financiero")
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Registros", len(df_ind))
with col2:
    st.metric("Entidades", df_ind["Sigla"].nunique())
with col3:
    st.metric("Tipos de entidad", df_ind["Tipo Entidad"].nunique())
with col4:
    st.metric("Meses", len(estado.periodos))

st.markdown("---")

# ==========================================
# DATOS DEL PERÍODO ACTUAL
# ==========================================
df_filtrado = estado.datos_actuales()

# ==========================================
# CÁLCULOS Y GRÁFICOS DINÁMICOS
# ==========================================
if not df_filtrado.empty:
    df_analisis = clasificar_cuadrantes(
        df_filtrado,
        eje_x="Crecimiento Cartera",
        eje_y="Indice de mora"
    )

    resumen = resumen_periodo(df_analisis)

    # Gráfico de dispersión
    fig = crear_dispersion(
        df=df_analisis,
        df_historico=df_historico,
        eje_x="Crecimiento Cartera",
        eje_y="Indice de mora",
        tamaño="10. Activo",
        color="Tipo Entidad",
        texto=COLUMNAS["sigla"],
        titulo="Crecimiento Anual de Cartera vs Índice de Mora",
        fecha_actual=estado.periodo_actual,
        mostrar_trayectorias=False
    )

    st.plotly_chart(fig, use_container_width=True)

    # ==========================================
    # EJE DE REPRODUCCIÓN POWER BI (PLAY + SLIDER)
    # ==========================================
    col_play, col_slider = st.columns([1, 11])

    with col_play:
        btn_label = "⏸" if st.session_state.reproduciendo else "▶"
        if st.button(btn_label, use_container_width=True, key="btn_play_pbi"):
            if st.session_state.reproduciendo:
                st.session_state.reproduciendo = False
            else:
                # Si llega al final y le da Play, inicia desde el primer dato
                if st.session_state.indice_periodo >= len(estado.periodos) - 1:
                    st.session_state.indice_periodo = 0
                st.session_state.reproduciendo = True
            st.rerun()

    with col_slider:
        if estado.periodos:
            # Slider para manipular exactamente el punto del tiempo
            fecha_slider = st.select_slider(
                "Periodo",
                options=estado.periodos,
                value=estado.periodos[st.session_state.indice_periodo],
                format_func=lambda x: x.strftime("%Y-%m"),
                key="slider_eje_reproduccion",
                label_visibility="collapsed"
            )

            # Si el usuario desplaza el slider manualmente
            idx_slider = estado.periodos.index(fecha_slider)
            if idx_slider != st.session_state.indice_periodo and not st.session_state.reproduciendo:
                st.session_state.indice_periodo = idx_slider
                st.rerun()

    # ==========================================
    # RESUMEN DEL PERÍODO
    # ==========================================
    st.subheader("🧠 Resumen del período")
    for fila in resumen:
        st.write(
            f"• {fila['Cantidad']} entidades "
            f"({fila['Porcentaje']:.1f}%) "
            f"se encuentran en **{fila['Estado']}**."
        )
else:
    st.warning("No hay datos suficientes para mostrar en este período.")

# ==========================================
# CICLO AUTO-AVANCE (ANIMACIÓN)
# ==========================================
if st.session_state.reproduciendo:
    time.sleep(0.3)
    if st.session_state.indice_periodo < len(estado.periodos) - 1:
        st.session_state.indice_periodo += 1
        st.rerun()
    else:
        st.session_state.reproduciendo = False
        st.rerun()




























































