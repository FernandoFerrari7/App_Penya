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
    # Contamos los partidos como la cantidad de jornadas únicas donde aparece la Penya
    jornadas_unicas = actas_df['jornada'].unique()
    total_partidos = len(jornadas_unicas)
    
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

def calcular_goles_contra(actas_df, partidos_df, actas_completas_df):
    """
    Calcula los goles en contra basado en los datos de las actas
    
    Args:
        actas_df: DataFrame con datos de actas de Penya
        partidos_df: DataFrame con datos de partidos
        actas_completas_df: DataFrame con todas las actas
        
    Returns:
        int: Total de goles en contra
    """
    # Enfoque 1: Buscar actas donde Penya aparece como rival
    actas_contra_penya = actas_completas_df[
        actas_completas_df['rival'].str.contains('PENYA INDEPENDENT', na=False)
    ]
    
    # Sumar los goles de esas actas
    goles_contra = actas_contra_penya['goles'].sum()
    
    # Si no encontramos resultados con este método, intentar otro enfoque
    if goles_contra == 0:
        # Enfoque 2: Usar las jornadas y partidos para identificar rivales
        
        # Identificar jornadas donde juega la Penya
        jornadas_penya = actas_df['jornada'].unique()
        
        # Filtrar partidos con la Penya
        partidos_penya = partidos_df[
            (partidos_df['equipo_local'].str.contains('PENYA INDEPENDENT', na=False)) | 
            (partidos_df['equipo_visitante'].str.contains('PENYA INDEPENDENT', na=False))
        ]
        
        # Mapear jornadas a rivales
        jornada_rival = {}
        for _, partido in partidos_penya.iterrows():
            if pd.isna(partido['jornada']):
                continue
                
            jornada = partido['jornada']
            if 'PENYA INDEPENDENT' in str(partido['equipo_local']):
                jornada_rival[jornada] = partido['equipo_visitante']
            else:
                jornada_rival[jornada] = partido['equipo_local']
        
        # Contar goles en contra (goles de los rivales)
        for jornada in jornadas_penya:
            if jornada in jornada_rival:
                rival = jornada_rival[jornada]
                if pd.isna(rival):
                    continue
                    
                # Buscar actas del rival en esta jornada
                actas_rival = actas_completas_df[
                    (actas_completas_df['jornada'] == jornada) & 
                    (actas_completas_df['equipo'].str.contains(str(rival), na=False))
                ]
                
                # Sumar goles del rival
                goles_contra += actas_rival['goles'].sum()

    return int(goles_contra)

def calcular_tarjetas_rivales(actas_completas_df, partidos_df):
    """
    Calcula las tarjetas de los equipos rivales
    
    Args:
        actas_completas_df: DataFrame con todas las actas
        partidos_df: DataFrame con datos de partidos
        
    Returns:
        dict: Diccionario con total de tarjetas amarillas y rojas de rivales
    """
    # Enfoque 1: Buscar actas donde Penya aparece como rival
    actas_rivales = actas_completas_df[
        actas_completas_df['rival'].str.contains('PENYA INDEPENDENT', na=False)
    ]
    
    # Sumar tarjetas de esas actas
    ta_rival = actas_rivales['Tarjetas Amarillas'].sum()
    tr_rival = actas_rivales['Tarjetas Rojas'].sum()
    
    # Si no encontramos resultados con este método, intentar enfoque alternativo
    if ta_rival == 0 and tr_rival == 0:
        # Filtrar partidos con la Penya
        partidos_penya = partidos_df[
            (partidos_df['equipo_local'].str.contains('PENYA INDEPENDENT', na=False)) | 
            (partidos_df['equipo_visitante'].str.contains('PENYA INDEPENDENT', na=False))
        ]
        
        # Mapear jornadas a rivales
        jornada_rival = {}
        for _, partido in partidos_penya.iterrows():
            if pd.isna(partido['jornada']):
                continue
                
            jornada = partido['jornada']
            if 'PENYA INDEPENDENT' in str(partido['equipo_local']):
                jornada_rival[jornada] = partido['equipo_visitante']
            else:
                jornada_rival[jornada] = partido['equipo_local']
        
        # Contar tarjetas de los rivales
        for jornada, rival in jornada_rival.items():
            if pd.isna(rival):
                continue
                
            # Buscar actas del rival en esta jornada
            actas_rival = actas_completas_df[
                (actas_completas_df['jornada'] == jornada) & 
                (actas_completas_df['equipo'].str.contains(str(rival), na=False))
            ]
            # Sumar tarjetas del rival
            ta_rival += actas_rival['Tarjetas Amarillas'].sum()
            tr_rival += actas_rival['Tarjetas Rojas'].sum()
    
    return {
        'amarillas': int(ta_rival),
        'rojas': int(tr_rival)
    }

def calcular_metricas_avanzadas(partidos_df, goles_df, actas_df, actas_completas_df):
    """
    Calcula métricas avanzadas para mostrar en tarjetas
    
    Args:
        partidos_df: DataFrame con datos de partidos
        goles_df: DataFrame con datos de goles
        actas_df: DataFrame con datos de actas de Penya
        actas_completas_df: DataFrame con todas las actas (todos los equipos)
        
    Returns:
        list: Lista de diccionarios con métricas para mostrar
    """
    # Determinar partidos locales y visitantes
    partidos_df = partidos_df.copy()
    partidos_df['es_local'] = partidos_df['equipo_local'].str.contains('PENYA INDEPENDENT', na=False)
    
    # Filtrar partidos de la Penya
    partidos_penya = partidos_df[
        (partidos_df['equipo_local'].str.contains('PENYA INDEPENDENT', na=False)) | 
        (partidos_df['equipo_visitante'].str.contains('PENYA INDEPENDENT', na=False))
    ]
    
    # Crear listas de jornadas por condición
    jornadas_local = partidos_penya[partidos_penya['es_local']]['jornada'].tolist()
    jornadas_visitante = partidos_penya[~partidos_penya['es_local']]['jornada'].tolist()
    
    # Contar goles a favor (total de goles marcados por Penya)
    goles_favor = len(goles_df)
    
    # Calcular los goles en contra
    goles_contra = calcular_goles_contra(actas_df, partidos_df, actas_completas_df)
    
    # Calcular tarjetas del equipo
    tarjetas_amarillas = int(actas_df['Tarjetas Amarillas'].sum())
    tarjetas_rojas = int(actas_df['Tarjetas Rojas'].sum())
    
    # Calcular tarjetas de los rivales
    tarjetas_rivales = calcular_tarjetas_rivales(actas_completas_df, partidos_df)
    ta_rival = tarjetas_rivales['amarillas']
    tr_rival = tarjetas_rivales['rojas']
    
    # Calcular número de jugadores y partidos
    num_jugadores = actas_df['jugador'].nunique()
    partidos_jugados = len(partidos_penya)
    
    # Calcular valores de referencia (medias de la liga)
    # Calculamos la media de goles de todos los otros equipos
    goles_por_equipo = actas_completas_df.groupby('equipo')['goles'].sum()
    # Excluir a Penya Independent para calcular la media
    goles_otros_equipos = goles_por_equipo[~goles_por_equipo.index.str.contains('PENYA INDEPENDENT')]
    ref_goles_favor = int(round(goles_otros_equipos.mean()))
    
    # Media de goles en contra (goles a favor de los otros equipos)
    ref_goles_contra = int(round(goles_otros_equipos.mean()))
    
    # Media de tarjetas amarillas de la liga
    tarjetas_por_equipo = actas_completas_df.groupby('equipo')['Tarjetas Amarillas'].sum()
    tarjetas_otros_equipos = tarjetas_por_equipo[~tarjetas_por_equipo.index.str.contains('PENYA INDEPENDENT')]
    ref_tarjetas_amarillas = int(round(tarjetas_otros_equipos.mean()))
    
    # Media de tarjetas amarillas de la liga para rivales
    ref_ta_rival = int(round(tarjetas_otros_equipos.mean()))
    
    # Media de tarjetas rojas de la liga
    rojas_por_equipo = actas_completas_df.groupby('equipo')['Tarjetas Rojas'].sum()
    rojas_otros_equipos = rojas_por_equipo[~rojas_por_equipo.index.str.contains('PENYA INDEPENDENT')]
    ref_tarjetas_rojas = round(rojas_otros_equipos.mean(), 1)
    
    # Media de tarjetas rojas de la liga para rivales
    ref_tr_rival = round(rojas_otros_equipos.mean(), 1)
    
    # Media de jugadores por equipo
    jugadores_por_equipo = actas_completas_df.groupby('equipo')['jugador'].nunique()
    jugadores_otros_equipos = jugadores_por_equipo[~jugadores_por_equipo.index.str.contains('PENYA INDEPENDENT')]
    ref_num_jugadores = round(jugadores_otros_equipos.mean(), 1)
    
    # Crear métricas para sección de goles
    metricas_goles = [
        {
            'titulo': 'Goles a favor',
            'valor': goles_favor,
            'referencia': ref_goles_favor,
            'color': '#FF8C00'  # Naranja
        },
        {
            'titulo': 'Goles en contra',
            'valor': goles_contra,
            'referencia': ref_goles_contra,
            'color': '#FF4136'  # Rojo
        }
    ]
    
    # Crear métricas para sección de tarjetas
    metricas_tarjetas = [
        {
            'titulo': 'Tarjetas Amarillas',
            'valor': tarjetas_amarillas,
            'referencia': ref_tarjetas_amarillas,
            'color': '#FFD700'  # Amarillo
        },
        {
            'titulo': 'TA Rival',
            'valor': ta_rival,
            'referencia': ref_ta_rival,
            'color': '#FFD700'  # Amarillo
        },
        {
            'titulo': 'Tarjetas Rojas',
            'valor': tarjetas_rojas,
            'referencia': ref_tarjetas_rojas,
            'color': '#FF4136'  # Rojo
        },
        {
            'titulo': 'TR Rival',
            'valor': tr_rival,
            'referencia': ref_tr_rival,
            'color': '#FF4136'  # Rojo
        }
    ]
    
    # Crear métricas para sección general
    metricas_general = [
        {
            'titulo': 'Num. Jugadores',
            'valor': num_jugadores,
            'referencia': ref_num_jugadores,
            'color': '#000000'  # Negro
        },
        {
            'titulo': 'Partidos Jugados',
            'valor': partidos_jugados,
            'referencia': None,
            'color': '#000000'  # Negro
        }
    ]
    
    return {
        'goles': metricas_goles,
        'tarjetas': metricas_tarjetas,
        'general': metricas_general
    }