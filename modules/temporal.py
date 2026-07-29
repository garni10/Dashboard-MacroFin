# ==========================================
# MOTOR TEMPORAL
# ==========================================
import pandas as pd

def obtener_periodos_validos(df, columna_clave="Crecimiento Cartera"):
    """
    Devuelve únicamente las fechas donde existen datos calculados válidos.
    Evita los primeros 12 meses (2023) que quedan en NaN por el cálculo de variación anual.
    """
    if df.empty or "Fecha" not in df.columns:
        return []
    
    # Filtrar registros donde la columna clave no sea NaN
    if columna_clave in df.columns:
        df_valid = df.dropna(subset=[columna_clave])
    else:
        df_valid = df

    return sorted(df_valid["Fecha"].unique())

def obtener_periodo(df, fecha):
    """
    Devuelve únicamente la información correspondiente al período seleccionado.
    """
    if fecha is None:
        return df.iloc[0:0]
    return df[df["Fecha"] == fecha].copy()

class EstadoTemporal:
    def __init__(self, df):
        self.df = df
        # Solo incluir períodos que arrancan desde el primer mes observable (Enero 2024)
        self.periodos = obtener_periodos_validos(df)
        self.indice = 0

    @property
    def periodo_actual(self):
        if not self.periodos:
            return None
        return self.periodos[self.indice]

    def datos_actuales(self):
        return obtener_periodo(self.df, self.periodo_actual)

    def avanzar(self):
        if self.indice < len(self.periodos) - 1:
            self.indice += 1
        return self.periodo_actual

    def retroceder(self):
        if self.indice > 0:
            self.indice -= 1
        return self.periodo_actual

    def ir_al_inicio(self):
        self.indice = 0
        return self.periodo_actual

    def ir_al_final(self):
        self.indice = max(0, len(self.periodos) - 1)
        return self.periodo_actual

class EstadoTemporalDiario:
    def __init__(self, df):
        self.df = df
        
        if not df.empty and "Fecha" in df.columns:
            # Obtener únicamente las fechas de 2026 que tienen datos calculados válidos
            todas_las_fechas = sorted(df["Fecha"].dropna().unique())
            self.periodos = [f for f in todas_las_fechas if f.year == 2026]
        else:
            self.periodos = []
            
        self.indice = 0

    @property
    def periodo_actual(self):
        if not self.periodos:
            return None
        return self.periodos[self.indice]

    def datos_actuales(self):
        if self.periodo_actual is None:
            return self.df.iloc[0:0]
        return self.df[self.df["Fecha"] == self.periodo_actual].copy()





































    