# ==========================================
# MOTOR TEMPORAL
# ==========================================

def obtener_periodo(df, fecha):

    """
    Devuelve únicamente la información
    correspondiente al período seleccionado.
    """

    return df[df["Fecha"] == fecha].copy()

# ==========================================
# ÚLTIMO PERÍODO
# ==========================================

def obtener_ultimo_periodo(df):

    """
    Devuelve el período más reciente
    disponible en la base de datos.
    """

    periodos = obtener_periodos(df)

    if len(periodos) == 0:
        return None

    return periodos[-1]

# ==========================================
# SIGUIENTE PERÍODO
# ==========================================

def siguiente_periodo(df, fecha_actual):

    """
    Devuelve el período siguiente al actual.
    Si el período actual es el último,
    devuelve nuevamente el último.
    """

    periodos = obtener_periodos(df)

    if fecha_actual not in periodos:
        return None

    indice = periodos.index(fecha_actual)

    if indice == len(periodos) - 1:
        return fecha_actual

    return periodos[indice + 1]

# ==========================================
# PERÍODO ANTERIOR
# ==========================================

def periodo_anterior(df, fecha_actual):

    """
    Devuelve el período anterior al actual.
    Si ya es el primero,
    devuelve nuevamente el primero.
    """

    periodos = obtener_periodos(df)

    if fecha_actual not in periodos:
        return None

    indice = periodos.index(fecha_actual)

    if indice == 0:
        return fecha_actual

    return periodos[indice - 1]

# ==========================================
# LISTA DE PERÍODOS
# ==========================================

def obtener_periodos(df):

    """
    Devuelve todos los períodos disponibles
    ordenados cronológicamente.
    """

    return sorted(df["Fecha"].dropna().unique())

# ==========================================
# ESTADO TEMPORAL
# ==========================================

class EstadoTemporal:

    def __init__(self, df):

        self.df = df

        df_valido = df.dropna(
            subset=[
                "Crecimiento Cartera",
                "Indice de mora"
            ]
        )

        self.periodos = obtener_periodos(df_valido)

        self.indice = len(self.periodos) - 1

    @property
    def periodo_actual(self):

        """
        Devuelve el período actualmente seleccionado.
        """

        return self.periodos[self.indice]


    def datos_actuales(self):

        """
        Devuelve los datos correspondientes
        al período actual.
        """

        return obtener_periodo(
            self.df,
            self.periodo_actual
        )

    def avanzar(self):
    
        """
        Avanza un período si existe uno posterior.
        """
    
        if self.indice < len(self.periodos) - 1:
            self.indice += 1
    
        return self.periodo_actual

    def retroceder(self):

        """
        Retrocede un período si existe uno anterior.
        """
    
        if self.indice > 0:
            self.indice -= 1
    
        return self.periodo_actual

    def ir_al_inicio(self):
    
        """
        Posiciona el estado temporal
        en el primer período disponible.
        """
    
        self.indice = 0
    
        return self.periodo_actual

    def ir_al_final(self):

        """
        Posiciona el estado temporal
        en el último período disponible.
        """
    
        self.indice = len(self.periodos) - 1
    
        return self.periodo_actual

    def ir_a(self, fecha):

        """
        Posiciona el estado temporal
        en la fecha indicada.
        """
    
        if fecha in self.periodos:
            self.indice = self.periodos.index(fecha)
    
        return self.periodo_actual







































    