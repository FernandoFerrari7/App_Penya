"""
Cálculos relacionados con estadísticas de jugadores
"""
import pandas as pd
import numpy as np

def calcular_estadisticas_jugador(actas_df, jugador_nombre):
    """
    Calcula estadísticas generales para un jugador específico
    
    Args:
        actas_df: DataFrame con los datos de actas
        jugador_nombre: Nombre del jugador
        
    Returns:
        dict: Diccionario con las estadísticas del jugador
    """
    # Filtrar datos del jugador
    datos_jugador = actas_df[actas_df['jugador'] == jugador_nombre]
    
    if datos_jugador.empty:
        return None
    
    # Cálculos básicos
    goles = datos_jugador['goles'].sum()
    tarjetas_amarillas = datos_jugador['Tarjetas Amarillas'].sum()
    tarjetas_rojas = datos_jugador['Tarjetas Rojas'].sum()
    minutos_jugados = datos_jugador['minutos_jugados'].sum()
    partidos_jugados = len(datos_jugador)
    
    # Calcular titularidades y suplencias
    titularidades = datos_jugador[datos_jugador['status'] == 'Titular'].shape[0]
    suplencias = partidos_jugados - titularidades
    
    # Minutos por partido
    minutos_por_partido = minutos_jugados / partidos_jugados if partidos_jugados > 0 else 0
    
    # Recopilar resultados
    estadisticas = {
        'nombre': jugador_nombre,
        'goles': int(goles),
        'tarjetas_amarillas': int(tarjetas_amarillas),
        'tarjetas_rojas': int(tarjetas_rojas),
        'minutos_jugados': int(minutos_jugados),
        'partidos_jugados': partidos_jugados,
        'titularidades': titularidades,
        'suplencias': suplencias,
        'minutos_por_partido': round(minutos_por_partido, 1)
    }
    
    return estadisticas

def obtener_minutos_por_jornada(actas_df, jugador_nombre):
    """
    Obtiene los minutos jugados por jornada para un jugador específico
    
    Args:
        actas_df: DataFrame con los datos de actas
        jugador_nombre: Nombre del jugador
        
    Returns:
        DataFrame: DataFrame con los minutos por jornada
    """
    # Filtrar datos del jugador
    datos_jugador = actas_df[actas_df['jugador'] == jugador_nombre]
    
    if datos_jugador.empty:
        return pd.DataFrame()
    
    # Seleccionar columnas relevantes
    minutos_por_jornada = datos_jugador[['jornada', 'minutos_jugados', 'rival', 'status']]
    
    # Agregar columna booleana para titular
    minutos_por_jornada['es_titular'] = minutos_por_jornada['status'] == 'Titular'
    
    # Ordenar por jornada
    minutos_por_jornada = minutos_por_jornada.sort_values('jornada')
    
    return minutos_por_jornada

def obtener_top_goleadores(actas_df, top_n=10):
    """
    Obtiene los jugadores con más goles
    
    Args:
        actas_df: DataFrame con los datos de actas
        top_n: Número de jugadores a mostrar
        
    Returns:
        DataFrame: DataFrame con los goleadores
    """
    # Agrupar por jugador y sumar goles
    goles_por_jugador = actas_df.groupby('jugador')['goles'].sum().reset_index()
    
    # Filtrar jugadores con al menos 1 gol
    goles_por_jugador = goles_por_jugador[goles_por_jugador['goles'] > 0]
    
    # Ordenar por goles (descendente)
    goles_por_jugador = goles_por_jugador.sort_values('goles', ascending=False)
    
    # Limitar al número especificado
    return goles_por_jugador.head(top_n)

def obtener_top_amonestados(actas_df, top_n=10):
    """
    Obtiene los jugadores con más tarjetas
    
    Args:
        actas_df: DataFrame con los datos de actas
        top_n: Número de jugadores a mostrar
        
    Returns:
        DataFrame: DataFrame con los jugadores más amonestados
    """
    # Agrupar por jugador y sumar tarjetas
    tarjetas_por_jugador = actas_df.groupby('jugador').agg({
        'Tarjetas Amarillas': 'sum',
        'Tarjetas Rojas': 'sum'
    }).reset_index()
    
    # Calcular un puntaje total (1 punto por amarilla, 3 por roja)
    tarjetas_por_jugador['total_puntos'] = (
        tarjetas_por_jugador['Tarjetas Amarillas'] + 
        3 * tarjetas_por_jugador['Tarjetas Rojas']
    )
    
    # Filtrar jugadores con al menos 1 tarjeta
    tarjetas_por_jugador = tarjetas_por_jugador[tarjetas_por_jugador['total_puntos'] > 0]
    
    # Ordenar por puntos totales (descendente)
    tarjetas_por_jugador = tarjetas_por_jugador.sort_values('total_puntos', ascending=False)
    
    # Limitar al número especificado
    return tarjetas_por_jugador.head(top_n)

def obtener_jugadores_mas_minutos(actas_df, top_n=10):
    """
    Obtiene los jugadores con más minutos jugados
    
    Args:
        actas_df: DataFrame con los datos de actas
        top_n: Número de jugadores a mostrar
        
    Returns:
        DataFrame: DataFrame con los jugadores con más minutos
    """
    # Agrupar por jugador y sumar minutos
    minutos_por_jugador = actas_df.groupby('jugador')['minutos_jugados'].sum().reset_index()
    
    # Ordenar por minutos (descendente)
    minutos_por_jugador = minutos_por_jugador.sort_values('minutos_jugados', ascending=False)
    
    # Limitar al número especificado
    return minutos_por_jugador.head(top_n)

def analizar_goles_por_tiempo(goles_df):
    """
    Analiza la distribución de goles por rango de minutos
    
    Args:
        goles_df: DataFrame con los datos de goles
        
    Returns:
        Series: Serie con conteo de goles por rango de minutos
    """
    # Crear rangos de minutos para agrupar
    goles_df = goles_df.copy()
    goles_df['rango_minuto'] = pd.cut(
        goles_df['Minuto'], 
        bins=[0, 15, 30, 45, 60, 75, 90, 105],
        labels=['0-15', '16-30', '31-45', '46-60', '61-75', '76-90', '91+']
    )
    
    # Contar goles por rango de minutos
    goles_por_minuto = goles_df['rango_minuto'].value_counts().sort_index()
    
    return goles_por_minuto