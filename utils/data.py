"""
Utilidades para cargar y procesar datos
"""
import os
import pandas as pd
import streamlit as st

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
    jornadas = pd.read_csv(os.path.join(data_path, "Jornadas_unificado.csv"))
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
    
    return {
        'actas': actas,
        'actas_penya': actas_penya,
        'goles': goles,
        'goles_penya': goles_penya,
        'jornadas': jornadas,
        'partidos_penya': partidos_penya,
        'sustituciones': sustituciones,
        'sustituciones_penya': sustituciones_penya
    }