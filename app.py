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
    generar_resumen_inteligente,
    resumen_periodo
)
from modules.temporal import EstadoTemporal, EstadoTemporalDiario
from modules.analisis import agregar_promedio_sistema
from modules.reproductor import dibujar_reproductor

st.set_page_config(
    page_title="Plataforma de Inteligencia para el Sistema Financiero",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>

/* Contenedor de pestañas */
div[data-baseweb="tab-list"] {
    gap: 24px !important;
}

/* Pestañas (Botón e hijos de texto) */
button[data-baseweb="tab"] {
    font-size: 26px !important; /* Puedes subirlo a 28px o 30px si lo quieres aún más grande */
    font-weight: 700 !important;
    padding: 14px 28px !important;
}

/* Forzar tamaño de texto interno en Streamlit Cloud (p, div, span) */
button[data-baseweb="tab"] p, 
button[data-baseweb="tab"] div, 
button[data-baseweb="tab"] span,
button[data-baseweb="tab"] [data-testid="stMarkdownContainer"] p {
    font-size: 26px !important;
    font-weight: 700 !important;
}

/* Pestaña seleccionada e indicador */
button[data-baseweb="tab"][aria-selected="true"] {
    color: #4FC3F7 !important;
}

div[data-baseweb="tab-highlight"] {
    height: 4px !important;
    background-color: #4FC3F7 !important;
}

/* Estilo para alineación del botón Play/Pausa con el Slider */
.stButton > button {
    margin-top: 0px !important;
    height: 42px !important;
    font-size: 20px !important;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# CARGA DE DATOS (MENSUAL Y DIARIO)
# ==========================================
df_ind_mensual = cargar_indicadores()
df_ind_diario = cargar_indicadores_diarios()

#st.write(df_ind_diario.shape)
#st.write(df_ind_diario["Fecha"].min())
#st.write(df_ind_diario["Fecha"].max())
#st.write(df_ind_diario.tail())

# ==========================================
# FILTROS LATERALES COMPARTIDOS (SIDEBAR)
# ==========================================
st.sidebar.markdown("### 🏢 Filtros de Entidades")

# 1. ORDEN JERÁRQUICO INSTITUCIONAL
ORDEN_TIPOS = [
    "BANCOS MULTIPLES",
    "ENTIDADES ESPECIALIZADAS EN MICROCRÉDITO",
    "INSTITUCIONES FINANCIERAS DE DESARROLLO",
    "COOPERATIVAS"
]

# 2. OBTENER TIPOS DE ENTIDAD EN ORDEN
# Usamos el DataFrame mensual cargado en app.py (df_ind_mensual)
if 'df_ind_mensual' in locals() and "Tipo Entidad" in df_ind_mensual.columns:
    tipos_en_data = df_ind_mensual["Tipo Entidad"].dropna().unique().tolist()
else:
    tipos_en_data = ORDEN_TIPOS

tipos_ordenados = [t for t in ORDEN_TIPOS if t in tipos_en_data]
tipos_ordenados += [t for t in tipos_en_data if t not in ORDEN_TIPOS]

# Selector 1: Tipo de entidad (Ordenado jerárquicamente)
tipos_sel = st.sidebar.multiselect(
    "Tipo de entidad",
    options=tipos_ordenados,
    default=tipos_ordenados
)

# 3. OBTENER LISTA DE SIGLAS
# Como vimos en filtros.py, la columna se llama "Sigla"
if 'df_ind_mensual' in locals() and "Sigla" in df_ind_mensual.columns:
    siglas_disponibles = sorted(df_ind_mensual["Sigla"].dropna().unique().tolist())
else:
    siglas_disponibles = []

# Selector 2: Siglas
siglas_sel = st.sidebar.multiselect(
    "Siglas",
    options=siglas_disponibles,
    default=siglas_disponibles
)

# En el Sidebar (sidebar.py o app.py según donde tengas tus controles)
st.sidebar.markdown("### 🎛️ Análisis de Ejes")

opciones_eje_y = {
    "Índice de Mora (%)": "Indice de mora",
    "Crecimiento Depósitos (%)": "Crecimiento Depósitos"
}

eje_y_label = st.sidebar.selectbox(
    "Seleccionar Variable Eje Y:",
    options=list(opciones_eje_y.keys()),
    index=0
)

# Variable técnica seleccionada para el gráfico
var_eje_y = opciones_eje_y[eje_y_label]
var_eje_x = "Crecimiento Cartera"  # Se mantiene fijo en el Eje X por ahora

# ==========================================
# TÍTULO PRINCIPAL
# ==========================================
st.title("📊 Plataforma de Inteligencia para el Sistema Financiero")
st.markdown("---")

# CREACIÓN DE PESTAÑAS (MENSUAL / DIARIO)
tab_mensual, tab_diario = st.tabs(["📅 Visión Mensual", "📆 Visión Diaria (2026)"])

if "idx_mensual" not in st.session_state:
    st.session_state.idx_mensual = 0

if "play_mensual" not in st.session_state:
    st.session_state.play_mensual = False

# ==========================================
# PESTAÑA 1: VISIÓN MENSUAL
# ==========================================
with tab_mensual:
    df_hist_m = aplicar_filtros(df=df_ind_mensual, fecha=None, tipo_entidad=tipos_sel, siglas=siglas_sel)
    estado_m = EstadoTemporal(df_hist_m)

    if estado_m.periodos:
        estado_m.indice = st.session_state.get(
            "idx_mensual",
            0
        )

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
        # Título dinámico para el gráfico
        titulo_m = f"Mensual: Crecimiento Anual de Cartera vs {eje_y_label}"

    # -------------------------------------------------------------------------
    # INICIALIZACIÓN DEL ESTADO DEL REPRODUCTOR
    # -------------------------------------------------------------------------
    
    if "idx_mensual" not in st.session_state:
        st.session_state.idx_mensual = 0
    
    if "play_mensual" not in st.session_state:
        st.session_state.play_mensual = False
    
    # -------------------------------------------------------------------------
    # B. REPRODUCTOR TEMPORAL + GRÁFICO
    # -------------------------------------------------------------------------
    
    run_every_m = (
        0.6
        if st.session_state.get("play_mensual", False)
        else None
    )
    
    
    @st.fragment(run_every=run_every_m)
    def vista_mensual():
    
        # --------------------------------------------------
        # 1. Actualizar el período actual
        # --------------------------------------------------
    
        estado_m.indice = st.session_state.idx_mensual
    
        # --------------------------------------------------
        # 2. Obtener datos del período
        # --------------------------------------------------
    
        df_filtrado_m_actual = estado_m.datos_actuales()
    
        # --------------------------------------------------
        # 3. Benchmark del sector
        # --------------------------------------------------
    
        if not df_filtrado_m_actual.empty:
    
            df_base_mes = df_ind_mensual[
                (df_ind_mensual["Fecha"] == estado_m.periodo_actual)
                &
                (df_ind_mensual["Tipo Entidad"].isin(tipos_sel))
            ]
    
            prom_x_m = (
                df_base_mes["Crecimiento Cartera"].mean()
                if not df_base_mes.empty
                else None
            )
    
            prom_y_m = (
                df_base_mes["Indice de mora"].mean()
                if not df_base_mes.empty
                else None
            )
    
        else:
    
            prom_x_m = None
            prom_y_m = None
    
        # --------------------------------------------------
        # 4. Clasificar cuadrantes
        # --------------------------------------------------
    
        df_analisis_m = clasificar_cuadrantes(
            df_filtrado_m_actual,
            eje_x="Crecimiento Cartera",
            eje_y=var_eje_y,
            prom_x=prom_x_m,
            prom_y=prom_y_m
        )
    
        # --------------------------------------------------
        # 5. Título
        # --------------------------------------------------
    
        titulo_m = (
            f"Mensual: Crecimiento Anual de Cartera "
            f"vs {eje_y_label}"
        )
    
        # --------------------------------------------------
        # 6. Crear gráfico
        # --------------------------------------------------
    
        fig_m = crear_dispersion(
            df=df_analisis_m,
            df_historico=df_hist_m,
            eje_x="Crecimiento Cartera",
            eje_y=var_eje_y,
            tamaño="10. Activo",
            color="Tipo Entidad",
            texto=COLUMNAS["sigla"],
            titulo=titulo_m,
            fecha_actual=estado_m.periodo_actual,
            mostrar_trayectorias=False,
            prom_x_custom=prom_x_m,
            prom_y_custom=prom_y_m
        )
    
        # --------------------------------------------------
        # 7. Mostrar gráfico
        # --------------------------------------------------
    
        st.plotly_chart(
            fig_m,
            use_container_width=True
        )
    
        # --------------------------------------------------
        # 8. Controles del reproductor
        # --------------------------------------------------
    
        c_play, c_slider = st.columns(
            [0.7, 11.3],
            vertical_alignment="center"
        )
    
        # --------------------------------------------------
        # 9. Botón Play / Pausa
        # --------------------------------------------------
    
        with c_play:
    
            etiqueta = (
                "❚❚"
                if st.session_state.get("play_mensual", False)
                else "►"
            )
    
            if st.button(
                etiqueta,
                key="play_m",
                use_container_width=True
            ):
    
                if st.session_state.get(
                    "play_mensual",
                    False
                ):
    
                    st.session_state.play_mensual = False
    
                else:
    
                    if (
                        st.session_state.idx_mensual
                        >= len(estado_m.periodos) - 1
                    ):
                        st.session_state.idx_mensual = 0
    
                    st.session_state.play_mensual = True
    
                # Necesitamos reconstruir el fragmento para
                # cambiar run_every entre None y 0.6
                st.rerun()
    
        # --------------------------------------------------
        # 10. Slider
        # --------------------------------------------------
    
        with c_slider:
    
            fecha_seleccionada = st.select_slider(
                "P_M",
                options=estado_m.periodos,
                value=estado_m.periodos[
                    st.session_state.idx_mensual
                ],
                format_func=lambda x: x.strftime("%Y-%m"),
                key="sl_m",
                label_visibility="collapsed"
            )
    
            nuevo_idx = estado_m.periodos.index(
                fecha_seleccionada
            )
    
            if (
                nuevo_idx != st.session_state.idx_mensual
                and not st.session_state.get(
                    "play_mensual",
                    False
                )
            ):
    
                st.session_state.idx_mensual = nuevo_idx
    
                st.rerun()

        # --------------------------------------------------
        # DIAGNÓSTICO DE RIESGO Y CRECIMIENTO
        # --------------------------------------------------
        
        resumen_texto_m = generar_resumen_inteligente(
            df_analisis_m,
            eje_y_label,
            var_eje_y
        )
        
        st.markdown(resumen_texto_m)
        
        
        # --------------------------------------------------
        # RESUMEN DEL PERÍODO
        # --------------------------------------------------
        
        st.markdown("### 🧠 Resumen del período")
        
        for fila in resumen_periodo(df_analisis_m):
            st.write(
                f"• {fila['Cantidad']} entidades "
                f"({fila['Porcentaje']:.1f}%) en "
                f"**{fila['Estado']}**."
            )
        
        # --------------------------------------------------
        # 11. Avance automático
        # --------------------------------------------------
    
        if st.session_state.get(
            "play_mensual",
            False
        ):
    
            if (
                st.session_state.idx_mensual
                < len(estado_m.periodos) - 1
            ):
    
                st.session_state.idx_mensual += 1
    
            else:
    
                # Llegamos al último período.
                # Detener reproducción.
                st.session_state.play_mensual = False
    
                # Reconstruir la aplicación para que
                # run_every pase nuevamente a None.
                st.rerun()
    
    
    vista_mensual()
  
# ==========================================
# PESTAÑA 2: VISIÓN DIARIA (2026)
# ==========================================
with tab_diario:
    df_hist_d = aplicar_filtros(df=df_ind_diario, fecha=None, tipo_entidad=tipos_sel, siglas=siglas_sel)
    estado_d = EstadoTemporalDiario(df_hist_d)

    if estado_d.periodos:
        estado_d.indice = st.session_state.get(
            "idx_diario",
            0
        )

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
        # Título dinámico para el gráfico
        titulo_d = f"Diario: Crecimiento Anual de Cartera vs {eje_y_label} (2026)"

    # -------------------------------------------------------------------------
    # B. CLASIFICACIÓN DE CUADRANTES
    # -------------------------------------------------------------------------
    df_analisis_d = clasificar_cuadrantes(
        df_filtrado_d, 
        eje_x="Crecimiento Cartera", 
        eje_y=var_eje_y, 
        prom_x=prom_x_d, 
        prom_y=prom_y_d
    )

    # -------------------------------------------------------------------------
    # C. CREACIÓN Y DESPLIEGUE DEL GRÁFICO
    # -------------------------------------------------------------------------
    fig_d = crear_dispersion(
        df=df_analisis_d,
        df_historico=df_hist_d,
        eje_x="Crecimiento Cartera",
        eje_y=var_eje_y,
        tamaño="10. Activo",
        color="Tipo Entidad",
        texto=COLUMNAS["sigla"],
        titulo=titulo_d,
        fecha_actual=estado_d.periodo_actual,
        mostrar_trayectorias=False,
        prom_x_custom=prom_x_d,
        prom_y_custom=prom_y_d
    )
    
    st.plotly_chart(fig_d, use_container_width=True)

    dibujar_reproductor(
        periodos=estado_d.periodos,
        play_key="play_diario",
        idx_key="idx_diario",
        slider_key="sl_d",
        formato="%d/%m/%Y",
        velocidad=0.6
    )

    # -------------------------------------------------------------------------
    # E. DIAGNÓSTICO INTELIGENTE Y RESUMEN DEL PERÍODO
    # -------------------------------------------------------------------------
    resumen_texto_d = generar_resumen_inteligente(df_analisis_d, eje_y_label, var_eje_y)
    st.markdown(resumen_texto_d)

    st.markdown("### 🧠 Resumen del período")
    for fila in resumen_periodo(df_analisis_d):
        st.write(f"• {fila['Cantidad']} entidades ({fila['Porcentaje']:.1f}%) en **{fila['Estado']}**.")






























































