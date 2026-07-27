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

def agregar_cuadrantes(fig, xmin, xmax, ymin, ymax):
    def calcular_posicion(rx, ry):
        x = xmin + (xmax - xmin) * rx
        y = ymin + (ymax - ymin) * ry
        return x, y

    x_riesgo, y_riesgo = calcular_posicion(*POSICION_CUADRANTES["Riesgo"])
    x_crecimiento, y_crecimiento = calcular_posicion(*POSICION_CUADRANTES["Crecimiento con Riesgo"])
    x_conservador, y_conservador = calcular_posicion(*POSICION_CUADRANTES["Conservador"])
    x_liderazgo, y_liderazgo = calcular_posicion(*POSICION_CUADRANTES["Liderazgo"])
    
    fig.add_annotation(
        x=x_riesgo, y=y_riesgo, text="<b>Riesgo</b>", showarrow=False,
        font=dict(size=18, color="rgba(255,255,255,0.20)")
    )
    fig.add_annotation(
        x=x_crecimiento, y=y_crecimiento, text="<b>Crecimiento<br>con Riesgo</b>", showarrow=False,
        font=dict(size=18, color="rgba(255,255,255,0.20)")
    )
    fig.add_annotation(
        x=x_conservador, y=y_conservador, text="<b>Conservador</b>", showarrow=False,
        font=dict(size=18, color="rgba(255,255,255,0.20)")
    )
    fig.add_annotation(
        x=x_liderazgo, y=y_liderazgo, text="<b>Liderazgo</b>", showarrow=False,
        font=dict(size=18, color="rgba(255,255,255,0.20)")
    )

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
    fecha_actual,
    mostrar_promedios=True,
    mostrar_cuadrantes=True,
    mostrar_trayectorias=False
):
    df_validos_hist = df_historico.dropna(subset=[eje_x, eje_y])
    
    xmin, xmax = df_validos_hist[eje_x].min(), df_validos_hist[eje_x].max()
    ymin, ymax = df_validos_hist[eje_y].min(), df_validos_hist[eje_y].max()

    pad_x = (xmax - xmin) * 0.05 if xmax != xmin else 1.0
    pad_y = (ymax - ymin) * 0.05 if ymax != ymin else 1.0

    xmin_view, xmax_view = xmin - pad_x, xmax + pad_x
    ymin_view, ymax_view = ymin - pad_y, ymax + pad_y

    promedio_x = df[eje_x].mean()
    promedio_y = df[eje_y].mean()

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
        size_max=TAM_BURBUJA,
        template="plotly_white",
        title=titulo,
        range_x=[xmin_view, xmax_view],
        range_y=[ymin_view, ymax_view]
    )

    # MARCA DE AGUA FECHA ESTILO POWER BI (Esquina superior derecha)
    if fecha_actual is not None:
        fig.add_annotation(
            x=0.98,
            y=0.75,
            xref="paper",
            yref="paper",
            text=f"<b>{fecha_actual.strftime('%Y-%m')}</b>",
            showarrow=False,
            font=dict(size=44, color="rgba(255, 255, 255, 0.25)"),
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
        fig = agregar_cuadrantes(fig, xmin_view, xmax_view, ymin_view, ymax_view)

    fig.update_traces(
        mode="markers",
        marker=dict(opacity=0.8, line=dict(width=1, color="black"))
    )

    return estilo_dashboard(fig)

































    