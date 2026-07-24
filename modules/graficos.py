# ==========================================
# MÓDULO DE GRÁFICOS
# Dashboard MacroFin
# ==========================================
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from modules.config import (
    TAM_BURBUJA,
    POSICION_CUADRANTES,
    TRAYECTORIA,
    COLORES
)

# ==========================================
# ETIQUETAS DE CUADRANTES
# ==========================================

def agregar_cuadrantes(
    fig,
    xmin,
    xmax,
    ymin,
    ymax
):
    
    # ==========================================
    # FUNCIÓN AUXILIAR
    # ==========================================
        
    def calcular_posicion(rx, ry):
        
        x = xmin + (xmax - xmin) * rx
        y = ymin + (ymax - ymin) * ry
            
        return x, y

    x_riesgo, y_riesgo = calcular_posicion(
        *POSICION_CUADRANTES["Riesgo"]
    )
    
    x_crecimiento, y_crecimiento = calcular_posicion(
        *POSICION_CUADRANTES["Crecimiento con Riesgo"]
    )
    
    x_conservador, y_conservador = calcular_posicion(
        *POSICION_CUADRANTES["Conservador"]
    )
    
    x_liderazgo, y_liderazgo = calcular_posicion(
        *POSICION_CUADRANTES["Liderazgo"]
    )
    
    fig.add_annotation(
        x=x_riesgo,
        y=y_riesgo,
        text="<b>Riesgo</b>",
        showarrow=False,
        font=dict(size=18, color="rgba(255,255,255,0.20)")
    )

    fig.add_annotation(
        x=x_crecimiento,
        y=y_crecimiento,
        text="<b>Crecimiento<br>con Riesgo</b>",
        showarrow=False,
        font=dict(size=18, color="rgba(255,255,255,0.20)")
    )

    fig.add_annotation(
        x=x_conservador,
        y=y_conservador,
        text="<b>Conservador</b>",
        showarrow=False,
        font=dict(size=18, color="rgba(255,255,255,0.20)")
    )

    fig.add_annotation(
        x=x_liderazgo,
        y=y_liderazgo,
        text="<b>Liderazgo</b>",
        showarrow=False,
        font=dict(size=18, color="rgba(255,255,255,0.20)")
    )

    return fig

# ==========================================
# ESTILO DEL DASHBOARD
# ==========================================

def estilo_dashboard(fig):
    """
    Aplica el estilo institucional
    a todos los gráficos.
    """

    fig.update_layout(

        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",

        font=dict(
            family="Arial",
            size=14,
            color="white"
        ),

        title=dict(
            font=dict(
                size=22,
                color="white"
            ),
            x=0.02
        ),

        legend=dict(

            orientation="v",

            bgcolor="rgba(0,0,0,0)",

            borderwidth=0,

            title="Tipo de Entidad"

        ),

        margin=dict(
            l=30,
            r=20,
            t=70,
            b=30
        ),

        hovermode="closest"

    )

    fig.update_xaxes(

        showgrid=True,

        gridcolor="rgba(255,255,255,0.12)",

        zeroline=True,

        zerolinecolor="rgba(255,255,255,0.35)",

        title_font=dict(size=16)

    )

    fig.update_yaxes(

        showgrid=True,

        gridcolor="rgba(255,255,255,0.12)",

        zeroline=True,

        zerolinecolor="rgba(255,255,255,0.35)",

        title_font=dict(size=16)

    )

    return fig

# ==========================================
# COLOR DE TRAYECTORIAS
# ==========================================

def hex_a_rgba(color_hex, opacidad):

    color_hex = color_hex.lstrip("#")

    r = int(color_hex[0:2], 16)
    g = int(color_hex[2:4], 16)
    b = int(color_hex[4:6], 16)

    return f"rgba({r},{g},{b},{opacidad})"

# ==========================================
# TRAYECTORIAS HISTÓRICAS
# ==========================================
def agregar_trayectorias(
    fig,
    df,
    eje_x,
    eje_y,
    fecha_actual, # Recibe la fecha del marco actual
    entidad="Sigla"
):

    # ==========================================
    # ORDEN CRONOLÓGICO
    # ==========================================
    df = df.sort_values("Fecha")
    # Filtrar el histórico solo hasta la fecha que se está visualizando actualmente
    df = df[df["Fecha"] <= fecha_actual]
    # Tomar los últimos N meses respecto al marco actual
    fecha_inicio = fecha_actual - pd.DateOffset(months=TRAYECTORIA["MESES"])
    df = df[df["Fecha"] >= fecha_inicio]

    for nombre, datos in df.groupby(entidad): 
        if datos.empty:
            continue   
        tipo = datos["Tipo Entidad"].iloc[-1]
        color_hex = COLORES.get(tipo, "#808080")
        color = hex_a_rgba(color_hex, TRAYECTORIA["OPACIDAD"])

        fig.add_trace(
            go.Scatter(
                x=datos[eje_x],
                y=datos[eje_y],
                mode="lines+markers",
                marker=dict(size=3, color=color),
                line=dict(color=color, width=TRAYECTORIA["ANCHO"], shape="spline", smoothing=0.35),
                hoverinfo="skip",
                showlegend=False
            )
        )
    
    return fig        
    
    # ==========================================
    # ÚLTIMOS N MESES
    # ==========================================
    #ultimo_periodo = df["Fecha"].max()
    #fecha_inicio = ultimo_periodo - pd.DateOffset(
        #months=TRAYECTORIA["MESES"]
    #)
    #df = df[df["Fecha"] >= fecha_inicio]
    # ==========================================
    # RECORRER CADA ENTIDAD
    # ==========================================
    #for nombre, datos in df.groupby(entidad):    
        #tipo = datos["Tipo Entidad"].iloc[-1]
        #color_hex = COLORES.get(
            #tipo,
            #"#808080"
        #)
        #color = hex_a_rgba(
            #color_hex,
            #TRAYECTORIA["OPACIDAD"]
        #)
        #print(nombre)
        #fig.add_trace(
            #go.Scatter(
                #x=datos[eje_x],
                #y=datos[eje_y],
                #mode="lines+markers",
                #marker=dict(
                    #size=3,
                    #color=color
                #),
                #line=dict(
                    #color=color,
                    #width=TRAYECTORIA["ANCHO"],
                    #shape="spline",
                    #smoothing=0.35
                #),
                #hoverinfo="skip",
                #showlegend=False
            #)
        #)
    #return fig
    
# ==========================================
# GRÁFICO DE DISPERSIÓN
# ==========================================
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
    mostrar_cuadrantes=True
):
    # ==========================================
    # PROMEDIOS
    # ==========================================
    
    promedio_x = df[eje_x].mean()
    
    promedio_y = df[eje_y].mean()

    # Límites del gráfico
    xmin = df[eje_x].min()
    xmax = df[eje_x].max()
    
    ymin = df[eje_y].min()
    ymax = df[eje_y].max()
    
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
        title=titulo
    )
    
    # ==========================================
    # LÍNEAS DE REFERENCIA
    # ==========================================
    
    if mostrar_promedios:    
        fig.add_vline(    
            x=promedio_x,    
            line_width=2,
            line_dash="dot",
            line_color="#4FC3F7"
        )
    
        fig.add_hline(
            y=promedio_y,
            line_width=2,
            line_dash="dot",
            line_color="#4FC3F7"
        ) 

    if mostrar_cuadrantes:

        fig = agregar_cuadrantes(
            fig,
            xmin,
            xmax,
            ymin,
            ymax
        )    
    
    fig = agregar_trayectorias(
        fig,
        df_historico,
        eje_x,
        eje_y,
        fecha_actual=fecha_actual
    )
    
    fig.update_traces(
        mode="markers",
        marker=dict(
            opacity=0.8,
            line=dict(width=1, color="black")
        )
    )

    fig = estilo_dashboard(fig)

    return fig

#def crear_trayectorias(
    #df,
    #eje_x,
    #eje_y,
    #color,
    #texto,
    #titulo
#):

    # Ordenar cronológicamente
    #df = df.sort_values("Fecha")

    #fig = px.line(
        #df,
        #x=eje_x,
        #y=eje_y,
        #color=color,
        #line_group=texto,
        #hover_name=texto,
        #markers=True,
        #title=titulo
    #)

    #fig.update_traces(
        #mode="lines+markers"
    #)

    #return fig



































    