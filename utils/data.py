"""
Utilidades para cargar y procesar datos
"""
import os
import pandas as pd
import streamlit as st

@st.cache_data
def calcular_medias_liga(actas_df):
    """
    Calcula las medias de la liga para todas las métricas relevantes.
    Se usa decorador cache_data para que solo se recalcule cuando los datos cambian.
    
    Args:
        actas_df: DataFrame con todas las actas
        
    Returns:
        dict: Diccionario con valores de referencia
    """
    # Primero necesitamos ajustar las tarjetas
    # Esta es una versión simplificada de ajustar_tarjetas_por_doble_amarilla para evitar dependencias circulares
    def ajustar_tarjetas(df):
        df_ajustado = df.copy()
        
        # Agrupar por jugador y jornada
        tarjetas_por_jugador_jornada = df_ajustado.groupby(['jugador', 'jornada']).agg({
            'Tarjetas Amarillas': 'sum',
            'Tarjetas Rojas': 'sum'
        }).reset_index()
        
        # Identificar jugadores con 2 o más amarillas en una jornada
        jugadores_doble_amarilla = tarjetas_por_jugador_jornada[
            (tarjetas_por_jugador_jornada['Tarjetas Amarillas'] >= 2)
        ]
        
        # Para cada caso de doble amarilla, ajustar
        for _, row in jugadores_doble_amarilla.iterrows():
            jugador = row['jugador']
            jornada = row['jornada']
            amarillas = row['Tarjetas Amarillas']
            
            # Calcular ajustes
            rojas_adicionales = amarillas // 2
            amarillas_restantes = amarillas % 2
            
            # Encontrar registros para ajustar
            mask = (df_ajustado['jugador'] == jugador) & (df_ajustado['jornada'] == jornada)
            
            if any(mask):
                # Ajustar primer registro
                primer_registro = df_ajustado[mask].index[0]
                df_ajustado.loc[primer_registro, 'Tarjetas Amarillas'] = amarillas_restantes
                df_ajustado.loc[primer_registro, 'Tarjetas Rojas'] += rojas_adicionales
                
                # Poner a cero los demás registros
                otros_registros = df_ajustado[mask].index[1:]
                if len(otros_registros) > 0:
                    df_ajustado.loc[otros_registros, 'Tarjetas Amarillas'] = 0
                    df_ajustado.loc[otros_registros, 'Tarjetas Rojas'] = 0
        
        return df_ajustado
    
    # Ajustar tarjetas para los cálculos
    actas_ajustadas = ajustar_tarjetas(actas_df)
    
    # Calcular medias por equipo
    goles_por_equipo = actas_df.groupby('equipo')['goles'].sum()
    tarjetas_amarillas_por_equipo = actas_ajustadas.groupby('equipo')['Tarjetas Amarillas'].sum()
    tarjetas_rojas_por_equipo = actas_ajustadas.groupby('equipo')['Tarjetas Rojas'].sum()
    jugadores_por_equipo = actas_df.groupby('equipo')['jugador'].nunique()
    
    # Calcular medias globales (valores de referencia)
    medias = {
        'ref_goles_favor': int(round(goles_por_equipo.mean())),
        'ref_goles_contra': int(round(goles_por_equipo.mean())),
        'ref_tarjetas_amarillas': int(round(tarjetas_amarillas_por_equipo.mean())),
        'ref_ta_rival': int(round(tarjetas_amarillas_por_equipo.mean())),
        'ref_tarjetas_rojas': round(tarjetas_rojas_por_equipo.mean(), 1),
        'ref_tr_rival': round(tarjetas_rojas_por_equipo.mean(), 1),
        'ref_num_jugadores': round(jugadores_por_equipo.mean(), 1)
    }
    
    return medias

@st.cache_data
def cargar_datos():
    """
    Carga todos los datasets y los devuelve como diccionario de DataFrames.
    Utiliza caché de Streamlit para mejorar el rendimiento.
    """
    # Ruta a los archivos de datos
    data_path = "data"
    
    # Cargar los archivos CSV
    actas = pd.read_csv(os.path.join(data_path, "Actas_unificado.csv"))
    goles = pd.read_csv(os.path.join(data_path, "Goles_unificado.csv"))
    jornadas = pd.read_csv(os.path.join(data_path, "Repositorio/Listado_Jornadas.csv"))
    sustituciones = pd.read_csv(os.path.join(data_path, "Sustituciones_unificado.csv"))
    
    # Filtrar solo datos de Penya Independent
    actas_penya = actas[actas['equipo'].str.contains('PENYA INDEPENDENT', na=False)]
    
    # Crear un mapa de jugador -> equipo para filtrar goles
    jugador_equipo = actas[['jugador', 'equipo']].drop_duplicates()
    jugador_equipo_dict = dict(zip(jugador_equipo['jugador'], jugador_equipo['equipo']))
    
    # Filtrar goles de Penya Independent usando el mapa de jugadores
    goles['equipo'] = goles['jugador'].map(jugador_equipo_dict)
    goles_penya = goles[goles['equipo'].str.contains('PENYA INDEPENDENT', na=False)].copy()
    
    # Filtrar partidos donde participa Penya Independent
    partidos_penya = jornadas[
        (jornadas['equipo_local'].str.contains('PENYA INDEPENDENT', na=False)) | 
        (jornadas['equipo_visitante'].str.contains('PENYA INDEPENDENT', na=False))
    ]
    
    # Filtrar sustituciones de Penya Independent
    sustituciones_penya = sustituciones[sustituciones['equipo'].str.contains('PENYA INDEPENDENT', na=False)]
    
    # Calcular las medias de la liga (se almacenarán en caché)
    medias_liga = calcular_medias_liga(actas)
    
    return {
        'actas': actas,
        'actas_penya': actas_penya,
        'goles': goles,
        'goles_penya': goles_penya,
        'jornadas': jornadas,
        'partidos_penya': partidos_penya,
        'sustituciones': sustituciones,
        'sustituciones_penya': sustituciones_penya,
        'medias_liga': medias_liga  # Agregar las medias al resultado
    }