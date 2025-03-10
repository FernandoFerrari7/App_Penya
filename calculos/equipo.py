"""
Cálculos relacionados con estadísticas del equipo
"""
import pandas as pd
import numpy as np

def calcular_estadisticas_generales(actas_df, goles_df, partidos_df):
    """
    Calcula estadísticas generales del equipo
    
    Args:
        actas_df: DataFrame con datos de actas
        goles_df: DataFrame con datos de goles
        partidos_df: DataFrame con datos de partidos
        
    Returns:
        dict: Diccionario con estadísticas generales
    """
    # Estadísticas básicas
    total_partidos = len(partidos_df)
    total_goles = len(goles_df)
    total_tarjetas_amarillas = actas_df['Tarjetas Amarillas'].sum()
    total_tarjetas_rojas = actas_df['Tarjetas Rojas'].sum()
    
    # Minutos jugados por todos los jugadores
    total_minutos = actas_df['minutos_jugados'].sum()
    
    # Calculamos el promedio de goles por partido
    promedio_goles = total_goles / total_partidos if total_partidos > 0 else 0
    
    # Recopilar resultados
    estadisticas = {
        'partidos_jugados': total_partidos,
        'goles_marcados': int(total_goles),
        'tarjetas_amarillas': int(total_tarjetas_amarillas),
        'tarjetas_rojas': int(total_tarjetas_rojas),
        'promedio_goles': round(promedio_goles, 2),
        'total_minutos': int(total_minutos)
    }
    
    return estadisticas

def analizar_tarjetas_por_jornada(actas_df):
    """
    Analiza la distribución de tarjetas por jornada
    
    Args:
        actas_df: DataFrame con los datos de actas
        
    Returns:
        DataFrame: DataFrame con tarjetas por jornada
    """
    # Agrupar por jornada y sumar tarjetas
    tarjetas_por_jornada = actas_df.groupby('jornada').agg({
        'Tarjetas Amarillas': 'sum',
        'Tarjetas Rojas': 'sum'
    }).reset_index()
    
    return tarjetas_por_jornada

def obtener_rivales_con_goles(actas_df, goles_df):
    """
    Obtiene los rivales contra los que se marcaron goles
    
    Args:
        actas_df: DataFrame con datos de actas
        goles_df: DataFrame con datos de goles
        
    Returns:
        DataFrame: DataFrame con goles por rival
    """
    # Mapear jornadas a rivales
    jornada_rival = {}
    
    # Para cada jornada única en los datos de goles
    for jornada in goles_df['Jornada'].unique():
        # Encontrar el rival en esa jornada
        rival_jornada = actas_df[actas_df['jornada'] == jornada]['rival'].iloc[0] if any(actas_df['jornada'] == jornada) else 'Desconocido'
        jornada_rival[jornada] = rival_jornada
    
    # Agregar columna de rival a los datos de goles
    goles_df_con_rival = goles_df.copy()
    goles_df_con_rival['rival'] = goles_df_con_rival['Jornada'].map(jornada_rival)
    
    # Contar goles por rival
    goles_por_rival = goles_df_con_rival.groupby('rival').size().reset_index(name='goles')
    
    # Ordenar por número de goles (descendente)
    goles_por_rival = goles_por_rival.sort_values('goles', ascending=False)
    
    return goles_por_rival

def analizar_tipos_goles(goles_df):
    """
    Analiza los tipos de goles marcados
    
    Args:
        goles_df: DataFrame con datos de goles
        
    Returns:
        Series: Serie con conteo de goles por tipo
    """
    # Contar goles por tipo
    tipos_goles = goles_df['Tipo de Gol'].value_counts()
    
    return tipos_goles