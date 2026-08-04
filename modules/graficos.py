# ==========================================
# MÓDULO DE GRÁFICOS
# Dashboard MacroFin
# ==========================================
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from modules.config import (
    TAM_BURBUJA,
    POSICION_CUADRANTES,
    COLORES
)

def agregar_cuadrantes(fig, xmin, xmax, ymin, ymax, eje_y="Indice de mora"):
    """
    Agrega las marcas de agua con los nombres de los cuadrantes en las esquinas.
    """
    # Lógica para definir las etiquetas según el Eje Y
    if eje_y == "Indice de mora":
        label_q1 = "Crecimiento con Riesgo"  # Superior Derecho
        label_q2 = "Riesgo"                 # Superior Izquierdo
        label_q3 = "Conservador"            # Inferior Izquierdo
        label_q4 = "Liderazgo"              # Inferior Derecho
    else:
        label_q1 = "Liderazgo"              # Superior Derecho
        label_q2 = "Captador / Expansivo"   # Superior Izquierdo
        label_q3 = "Rezago / Estancado"     # Inferior Izquierdo
        label_q4 = "Otorgador / Descalce"   # Inferior Derecho

    # Usamos directamente xmax, xmin, ymax, ymin (sin '_view')
    fig.add_annotation(x=xmax, y=ymax, text=f"<b>{label_q1}</b>", showarrow=False, opacity=0.25, font=dict(size=18, color="white"))
    fig.add_annotation(x=xmin, y=ymax, text=f"<b>{label_q2}</b>", showarrow=False, opacity=0.25, font=dict(size=18, color="white"))
    fig.add_annotation(x=xmin, y=ymin, text=f"<b>{label_q3}</b>", showarrow=False, opacity=0.25, font=dict(size=18, color="white"))
    fig.add_annotation(x=xmax, y=ymin, text=f"<b>{label_q4}</b>", showarrow=False, opacity=0.25, font=dict(size=18, color="white"))

    return fig

def estilo_dashboard(fig):
    fig.update_layout(
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        font=dict(family="Arial", size=14, color="white"),
        title=dict(font=dict(size=22, color="white"), x=0.02),
        legend=dict(orientation="v", bgcolor="rgba(0,0,0,0)", borderwidth=0, title="Tipo de Entidad"),
        margin=dict(l=30, r=40, t=70, b=30),
        hovermode="closest"
    )

    fig.update_xaxes(
        showgrid=True, gridcolor="rgba(255,255,255,0.12)",
        zeroline=True, zerolinecolor="rgba(255,255,255,0.35)", title_font=dict(size=16)
    )

    fig.update_yaxes(
        showgrid=True, gridcolor="rgba(255,255,255,0.12)",
        zeroline=True, zerolinecolor="rgba(255,255,255,0.35)", title_font=dict(size=16)
    )

    return fig

def crear_dispersion(
    df, 
    df_historico, 
    eje_x, 
    eje_y, 
    tamaño, 
    color, 
    texto, 
    titulo, 
    fecha_actual=None, 
    mostrar_trayectorias=False,
    mostrar_promedios=True,       # Parámetro para las líneas del promedio
    mostrar_cuadrantes=True,      # Parámetro para las etiquetas de los cuadrantes
    prom_x_custom=None,
    prom_y_custom=None
):
    
    df_validos_hist = df_historico.dropna(subset=[eje_x, eje_y])
    
    xmin, xmax = df_validos_hist[eje_x].min(), df_validos_hist[eje_x].max()
    ymin, ymax = df_validos_hist[eje_y].min(), df_validos_hist[eje_y].max()

    pad_x = (xmax - xmin) * 0.05 if xmax != xmin else 1.0
    pad_y = (ymax - ymin) * 0.05 if ymax != ymin else 1.0

    xmin_view, xmax_view = xmin - pad_x, xmax + pad_x
    ymin_view, ymax_view = ymin - pad_y, ymax + pad_y

    promedio_x = prom_x_custom if prom_x_custom is not None else df[eje_x].mean()
    promedio_y = prom_y_custom if prom_y_custom is not None else df[eje_y].mean()

    # Mapa de colores fijo por Tipo de Entidad para evitar cambios en la leyenda al animar
    MAPA_COLORES = {
        "BANCOS MULTIPLES": "#5C6BC0",                         # Azul / Morado
        "ENTIDADES ESPECIALIZADAS EN MICROCRÉDITO": "#FF7043", # Naranja / Coral
        "INSTITUCIONES FINANCIERAS DE DESARROLLO": "#26A69A", # Verde Agua
        "COOPERATIVAS": "#AB47BC"                              # Púrpura / Violeta
    }

    ORDEN_TIPOS = [
        "BANCOS MULTIPLES",
        "ENTIDADES ESPECIALIZADAS EN MICROCRÉDITO",
        "INSTITUCIONES FINANCIERAS DE DESARROLLO",
        "COOPERATIVAS"
    ]

    # Convertimos a tipo Categorical para forzar el orden interno
    if "Tipo Entidad" in df.columns:
        df["Tipo Entidad"] = pd.Categorical(df["Tipo Entidad"], categories=ORDEN_TIPOS, ordered=True)
        df = df.sort_values("Tipo Entidad")
    
    fig = px.scatter(
        data_frame=df,
        x=eje_x,
        y=eje_y,
        size=tamaño,
        color=color,
        hover_name=texto,
        hover_data={
            "Fecha": True,
            "Tipo Entidad": True,
            "Sigla": False,
            "10. Activo": ":,.0f",
            "1. Cartera Bruta": ":,.0f",
            "6. Depósitos del Público": ":,.0f",
            "Crecimiento Cartera": ":.2f",
            "Indice de mora": ":.2f"
        },
        # --- AJUSTES DE COLOR Y ORDEN FIJO ---
        color_discrete_map=MAPA_COLORES,
        category_orders={"Tipo Entidad": ORDEN_TIPOS},
        # -----------------------------------
        size_max=TAM_BURBUJA,
        template="plotly_white",
        title=titulo,
        range_x=[xmin_view, xmax_view],
        range_y=[ymin_view, ymax_view]
    )

    # MARCA DE AGUA FECHA ESTILO POWER BI
    if fecha_actual is not None:
        # Formato de la fecha según el tipo
        if isinstance(fecha_actual, (pd.Timestamp, str)):
            fecha_str = str(fecha_actual)[:10]
        else:
            # Es un objeto datetime.date
            fecha_str = fecha_actual.strftime("%d/%m/%Y")

        fig.add_annotation(
            x=0.98,
            y=0.70,
            xref="paper",
            yref="paper",
            xanchor="right",
            yanchor="top",
            text=f"<b>{fecha_str}</b>",
            showarrow=False,
            font=dict(size=40, color="rgba(255, 255, 255, 0.22)"),
            align="right"
        )

    # Líneas de promedios con etiquetas numéricas
    if mostrar_promedios and not np.isnan(promedio_x) and not np.isnan(promedio_y):
        fig.add_vline(x=promedio_x, line_width=1.5, line_dash="dot", line_color="#4FC3F7")
        fig.add_annotation(
            x=promedio_x, y=ymax_view, text=f"<b>{promedio_x:.2f}%</b>",
            showarrow=False, yshift=10, font=dict(size=12, color="#4FC3F7"), bgcolor="#0E1117"
        )

        fig.add_hline(y=promedio_y, line_width=1.5, line_dash="dot", line_color="#4FC3F7")
        fig.add_annotation(
            x=xmax_view, y=promedio_y, text=f"<b>{promedio_y:.2f}%</b>",
            showarrow=False, xshift=15, font=dict(size=12, color="#4FC3F7"), bgcolor="#0E1117"
        )

    if mostrar_cuadrantes:
        fig = agregar_cuadrantes(fig, xmin_view, xmax_view, ymin_view, ymax_view, eje_y=eje_y)

    fig.update_traces(
        mode="markers",
        marker=dict(opacity=0.8, line=dict(width=1, color="black"))
    )
    
    return estilo_dashboard(fig)

































    