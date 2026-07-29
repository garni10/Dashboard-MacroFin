import streamlit as st
import pandas as pd
import numpy as np
import time

from modules.indicadores import cargar_indicadores, cargar_indicadores_diarios
from modules.graficos import crear_dispersion
from modules.filtros import aplicar_filtros
from modules.config import COLUMNAS
from modules.analisis import (
    clasificar_cuadrantes,
    resumen_periodo,
)
from modules.temporal import EstadoTemporal, EstadoTemporalDiario
from modules.analisis import agregar_promedio_sistema


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
button[data-baseweb="tab"]{ font-size:22px !important; font-weight:700 !important; padding:12px 24px !important; }
button[data-baseweb="tab"] p{ font-size:22px !important; font-weight:700 !important; }
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
# CARGA DE DATOS (MENSUAL Y DIARIO)
# ==========================================
df_ind_mensual = cargar_indicadores()
df_ind_diario = cargar_indicadores_diarios()

# ==========================================
# FILTROS LATERALES COMPARTIDOS (SIDEBAR)
# ==========================================
# Se obtienen tipos y siglas combinados de ambos datasets
tipos = sorted(list(set(df_ind_mensual["Tipo Entidad"].dropna().unique()).union(set(df_ind_diario["Tipo Entidad"].dropna().unique()))))
tipos_sel = st.sidebar.multiselect("🏦 Tipo de entidad", options=tipos, default=tipos)

siglas_m = df_ind_mensual[df_ind_mensual["Tipo Entidad"].isin(tipos_sel)]["Sigla"].dropna().unique()
siglas_d = df_ind_diario[df_ind_diario["Tipo Entidad"].isin(tipos_sel)]["Sigla"].dropna().unique()
siglas = sorted(list(set(siglas_m).union(set(siglas_d))))

siglas_sel = st.sidebar.multiselect("🏦 Siglas", options=siglas, default=siglas)

# ==========================================
# TÍTULO PRINCIPAL
# ==========================================
st.title("📊 Plataforma de Inteligencia para el Sistema Financiero")
st.markdown("---")

# CREACIÓN DE PESTAÑAS (MENSUAL / DIARIO)
tab_mensual, tab_diario = st.tabs(["📅 Visión Mensual", "📆 Visión Diaria (2026)"])

# ==========================================
# PESTAÑA 1: VISIÓN MENSUAL
# ==========================================
with tab_mensual:
    df_hist_m = aplicar_filtros(df=df_ind_mensual, fecha=None, tipo_entidad=tipos_sel, siglas=siglas_sel)
    estado_m = EstadoTemporal(df_hist_m)

    if "idx_mensual" not in st.session_state:
        st.session_state.idx_mensual = 0
    if "play_mensual" not in st.session_state:
        st.session_state.play_mensual = False

    if estado_m.periodos:
        st.session_state.idx_mensual = max(0, min(st.session_state.idx_mensual, len(estado_m.periodos) - 1))
        estado_m.indice = st.session_state.idx_mensual

    # KPIs Mensual
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Registros", len(df_hist_m))
    with col2: st.metric("Entidades", df_hist_m["Sigla"].nunique())
    with col3: st.metric("Tipos de entidad", len(tipos_sel))
    with col4: st.metric("Meses", len(estado_m.periodos))
    st.markdown("---")

    df_filtrado_m = estado_m.datos_actuales()

    if not df_filtrado_m.empty:
        # 1. Obtener datos completos del mes para los tipos de entidad seleccionados (benchmark del sector)
        df_base_mes = df_ind_mensual[
            (df_ind_mensual["Fecha"] == estado_m.periodo_actual) & 
            (df_ind_mensual["Tipo Entidad"].isin(tipos_sel))
        ]
        
        # 2. Calcular los promedios del sector para posicionar las líneas de los ejes
        prom_x_m = df_base_mes["Crecimiento Cartera"].mean() if not df_base_mes.empty else None
        prom_y_m = df_base_mes["Indice de mora"].mean() if not df_base_mes.empty else None

        # 3. Clasificar entidades filtradas y crear el gráfico
        df_analisis_m = clasificar_cuadrantes(df_filtrado_m, eje_x="Crecimiento Cartera", eje_y="Indice de mora")
        
        fig_m = crear_dispersion(
            df=df_analisis_m, 
            df_historico=df_hist_m,
            eje_x="Crecimiento Cartera", 
            eje_y="Indice de mora",
            tamaño="10. Activo", 
            color="Tipo Entidad", 
            texto=COLUMNAS["sigla"],
            titulo="Mensual: Crecimiento Anual de Cartera vs Índice de Mora",
            fecha_actual=estado_m.periodo_actual, 
            mostrar_trayectorias=False,
            # Pasamos los promedios del sector para las líneas cruzadas:
            prom_x_custom=prom_x_m,
            prom_y_custom=prom_y_m
        )
        st.plotly_chart(fig_m, use_container_width=True)

        # Reproductor Mensual
        c_play, c_slider = st.columns([1, 11])
        with c_play:
            btn_lbl = "⏸" if st.session_state.play_mensual else "▶"
            if st.button(btn_lbl, key="play_m", use_container_width=True):
                if st.session_state.play_mensual:
                    st.session_state.play_mensual = False
                else:
                    if st.session_state.idx_mensual >= len(estado_m.periodos) - 1:
                        st.session_state.idx_mensual = 0
                    st.session_state.play_mensual = True
                st.rerun()

        with c_slider:
            if estado_m.periodos:
                f_sl = st.select_slider(
                    "P_M", options=estado_m.periodos,
                    value=estado_m.periodos[st.session_state.idx_mensual],
                    format_func=lambda x: x.strftime("%Y-%m"),
                    key="sl_m", label_visibility="collapsed"
                )
                idx_s = estado_m.periodos.index(f_sl)
                if idx_s != st.session_state.idx_mensual and not st.session_state.play_mensual:
                    st.session_state.idx_mensual = idx_s
                    st.rerun()

        st.subheader("🧠 Resumen del período")
        for fila in resumen_periodo(df_analisis_m):
            st.write(f"• {fila['Cantidad']} entidades ({fila['Porcentaje']:.1f}%) en **{fila['Estado']}**.")
    else:
        st.warning("No hay datos mensuales para los filtros seleccionados.")

    if st.session_state.play_mensual:
        time.sleep(0.3)
        if st.session_state.idx_mensual < len(estado_m.periodos) - 1:
            st.session_state.idx_mensual += 1
            st.rerun()
        else:
            st.session_state.play_mensual = False
            st.rerun()


# ==========================================
# PESTAÑA 2: VISIÓN DIARIA (2026)
# ==========================================
with tab_diario:
    df_hist_d = aplicar_filtros(df=df_ind_diario, fecha=None, tipo_entidad=tipos_sel, siglas=siglas_sel)
    estado_d = EstadoTemporalDiario(df_hist_d)

    if "idx_diario" not in st.session_state:
        st.session_state.idx_diario = 0
    if "play_diario" not in st.session_state:
        st.session_state.play_diario = False

    if estado_d.periodos:
        st.session_state.idx_diario = max(0, min(st.session_state.idx_diario, len(estado_d.periodos) - 1))
        estado_d.indice = st.session_state.idx_diario

    # KPIs Diario
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Registros", len(df_hist_d))
    with col2: st.metric("Entidades", df_hist_d["Sigla"].nunique())
    with col3: st.metric("Tipos de entidad", len(tipos_sel))
    with col4: st.metric("Días (2026)", len(estado_d.periodos))
    st.markdown("---")

    df_filtrado_d = estado_d.datos_actuales()

    if not df_filtrado_d.empty:
        # 1. Obtener datos completos del día para los tipos de entidad seleccionados (benchmark del sector)
        df_base_dia = df_ind_diario[
            (df_ind_diario["Fecha"] == estado_d.periodo_actual) & 
            (df_ind_diario["Tipo Entidad"].isin(tipos_sel))
        ]
        
        # 2. Calcular los promedios del sector para posicionar las líneas de los ejes
        prom_x_d = df_base_dia["Crecimiento Cartera"].mean() if not df_base_dia.empty else None
        prom_y_d = df_base_dia["Indice de mora"].mean() if not df_base_dia.empty else None

        # 3. Clasificar entidades filtradas y crear el gráfico
        df_analisis_d = clasificar_cuadrantes(df_filtrado_d, eje_x="Crecimiento Cartera", eje_y="Indice de mora")
        
        fig_d = crear_dispersion(
            df=df_analisis_d, 
            df_historico=df_hist_d,
            eje_x="Crecimiento Cartera", 
            eje_y="Indice de mora",
            tamaño="10. Activo", 
            color="Tipo Entidad", 
            texto=COLUMNAS["sigla"],
            titulo="Diario: Crecimiento Anual de Cartera vs Índice de Mora (2026)",
            fecha_actual=estado_d.periodo_actual, 
            mostrar_trayectorias=False,
            # Pasamos los promedios del sector para las líneas cruzadas:
            prom_x_custom=prom_x_d,
            prom_y_custom=prom_y_d
        )
        st.plotly_chart(fig_d, use_container_width=True)

        # Reproductor Diario
        c_play_d, c_slider_d = st.columns([1, 11])
        with c_play_d:
            btn_lbl_d = "⏸" if st.session_state.play_diario else "▶"
            if st.button(btn_lbl_d, key="play_d", use_container_width=True):
                if st.session_state.play_diario:
                    st.session_state.play_diario = False
                else:
                    if st.session_state.idx_diario >= len(estado_d.periodos) - 1:
                        st.session_state.idx_diario = 0
                    st.session_state.play_diario = True
                st.rerun()

        with c_slider_d:
            if estado_d.periodos:
                f_sl_d = st.select_slider(
                    "P_D", options=estado_d.periodos,
                    value=estado_d.periodos[st.session_state.idx_diario],
                    format_func=lambda x: x.strftime("%d/%m/%Y"),
                    key="sl_d", label_visibility="collapsed"
                )
                idx_s_d = estado_d.periodos.index(f_sl_d)
                if idx_s_d != st.session_state.idx_diario and not st.session_state.play_diario:
                    st.session_state.idx_diario = idx_s_d
                    st.rerun()

        st.subheader("🧠 Resumen del período")
        for fila in resumen_periodo(df_analisis_d):
            st.write(f"• {fila['Cantidad']} entidades ({fila['Porcentaje']:.1f}%) en **{fila['Estado']}**.")
    else:
        st.warning("No hay datos diarios para los filtros seleccionados o el período activo.")

    if st.session_state.play_diario:
        time.sleep(0.08)  # Velocidad ajustada a iteración diaria
        if st.session_state.idx_diario < len(estado_d.periodos) - 1:
            st.session_state.idx_diario += 1
            st.rerun()
        else:
            st.session_state.play_diario = False
            st.rerun()




























































