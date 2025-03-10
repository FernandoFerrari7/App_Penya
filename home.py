"""
Página principal del dashboard de Penya Independent
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Importar módulos propios
from utils.data import cargar_datos
from utils.ui import show_sidebar, page_config
from common.menu import crear_menu, mostrar_pagina_actual
from calculos.equipo import calcular_estadisticas_generales
from calculos.jugadores import obtener_top_goleadores, obtener_top_amonestados, obtener_jugadores_mas_minutos
from visualizaciones.jugadores import graficar_top_goleadores, graficar_top_amonestados, graficar_minutos_jugados

# Configurar la página
page_config()

# Cargar datos
data = cargar_datos()

def main():
    """Función principal que muestra el dashboard"""
    
    # Título principal
    st.title("Dashboard Penya Independent")
    
    # Mostrar barra lateral
    show_sidebar()
    
    # Sección de resumen general
    st.header("Resumen General")
    
    # Calcular estadísticas generales
    estadisticas_equipo = calcular_estadisticas_generales(
        data['actas_penya'], 
        data['goles_penya'], 
        data['partidos_penya']
    )
    
    # Mostrar métricas de resumen (sin el tiempo total de juego)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Partidos Jugados", estadisticas_equipo['partidos_jugados'])
    
    with col2:
        st.metric("Goles Marcados", estadisticas_equipo['goles_marcados'])
    
    with col3:
        st.metric("Tarjetas Amarillas", estadisticas_equipo['tarjetas_amarillas'])
    
    with col4:
        st.metric("Tarjetas Rojas", estadisticas_equipo['tarjetas_rojas'])
    
    # Añadir solo el promedio de goles por partido
    st.metric("Promedio Goles/Partido", estadisticas_equipo['promedio_goles'])
    
    # Espacio para separar secciones
    st.markdown("---")
    
    # Sección de jugadores destacados
    st.header("Jugadores Destacados")
    
    # Dividir en dos columnas
    col1, col2 = st.columns(2)
    
    with col1:
        # Top goleadores
        st.subheader("Top Goleadores")
        top_goleadores = obtener_top_goleadores(data['actas_penya'], top_n=8)
        graficar_top_goleadores(top_goleadores)
    
    with col2:
        # Jugadores con más tarjetas
        st.subheader("Jugadores con Más Tarjetas")
        top_amonestados = obtener_top_amonestados(data['actas_penya'], top_n=8)
        graficar_top_amonestados(top_amonestados)
    
    # Nueva fila para más estadísticas
    col1, col2 = st.columns(2)
    
    with col1:
        # Jugadores con más minutos
        st.subheader("Jugadores con Más Minutos")
        top_minutos = obtener_jugadores_mas_minutos(data['actas_penya'], top_n=8)
        graficar_minutos_jugados(top_minutos)
    
    with col2:
        # Información sobre navegación
        st.subheader("Navegación")
        st.info(
            """
            Este dashboard muestra un resumen general del equipo Penya Independent.
            
            Para análisis más detallados:
            
            - **👤 Jugadores**: Estadísticas individuales de cada jugador
            - **⚽ Equipo**: Análisis de partidos, goles y tarjetas
            """
        )
    
    # Nota informativa al final
    st.markdown("---")
    st.caption("Datos actualizados. Dashboard desarrollado con Streamlit.")

if __name__ == "__main__":
    # Crear el menú de navegación
    pagina_seleccionada = crear_menu()
    
    # Mostrar la página correspondiente
    if pagina_seleccionada == "Inicio":
        main()
    else:
        mostrar_pagina_actual()