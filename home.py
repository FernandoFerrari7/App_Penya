"""
Página principal del dashboard de Penya Independent
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Importar módulos propios
from utils.data import cargar_datos
from utils.ui import page_config  # Solo importar page_config
from common.menu import crear_menu, mostrar_pagina_actual
from calculos.calculo_equipo import calcular_estadisticas_generales, calcular_metricas_avanzadas, calcular_goles_contra
from calculos.calculo_jugadores import obtener_top_goleadores, obtener_top_amonestados, obtener_jugadores_mas_minutos

# Importar funciones de visualización especiales para la página Home
from visualizaciones.jugadores_home import (
    graficar_top_goleadores_home,
    graficar_top_amonestados_home,
    graficar_minutos_jugados_home
)

# Configurar la página
page_config()

# Cargar datos
data = cargar_datos()

def main():
    """Función principal que muestra el dashboard"""
    
    # SOLUCIÓN EXTREMADAMENTE SIMPLE: SÓLO 3 COLUMNAS CON MENOS ESPACIO
    c1, c2, c3 = st.columns([2, 3, 2], gap="small")
    
    with c1:
        # Logo de Penya mucho más cerca
        st.image("assets/logo_penya.png", width=110) 
    
    with c2:
        # Título con mucho menos espacio
        st.write("# Penya Independent")
        st.write("#### Análisis de Rendimiento")
    
    with c3:
        # Logo FFIB
        st.write("")  # Añadir un único espacio para alinearlo
        st.image("assets/logo_ffib.png", width=140)
    
    # Espacio para separar el título del contenido
    st.markdown("---")
    
    # Calcular estadísticas generales
    estadisticas_equipo = calcular_estadisticas_generales(
        data['actas_penya'], 
        data['goles_penya'], 
        data['partidos_penya']
    )
    
    # Calcular goles en contra de manera dinámica
    try:
        # Intentar calcular con la función metricas_avanzadas
        metricas_avanzadas = calcular_metricas_avanzadas(
            data['partidos_penya'], 
            data['goles_penya'], 
            data['actas_penya'], 
            data['actas']
        )
        goles_recibidos = metricas_avanzadas['goles'][1]['valor']
    except Exception as e:
        # Si falla, intentar directamente con calcular_goles_contra
        try:
            goles_recibidos = calcular_goles_contra(
                data['actas_penya'], 
                data['partidos_penya'], 
                data['actas']
            )
        except Exception as e2:
            # Si todo falla, mostrar error
            st.error(f"Error al calcular goles en contra: {e2}")
            goles_recibidos = 0
    
    # Mostrar métricas de resumen en una sola fila con 5 columnas
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Partidos Jugados", estadisticas_equipo['partidos_jugados'])
    
    with col2:
        st.metric("Goles Marcados", estadisticas_equipo['goles_marcados'])
    
    with col3:
        st.metric("Goles Recibidos", goles_recibidos)
    
    with col4:
        st.metric("Tarjetas Amarillas", estadisticas_equipo['tarjetas_amarillas'])
    
    with col5:
        st.metric("Tarjetas Rojas", estadisticas_equipo['tarjetas_rojas'])
    
    # Espacio para separar secciones
    st.markdown("---")
    
    # Dividir en dos columnas
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 5 goleadores
        top_goleadores = obtener_top_goleadores(data['actas_penya'], top_n=5)
        graficar_top_goleadores_home(top_goleadores)
    
    with col2:
        # Top 5 jugadores con más tarjetas
        top_amonestados = obtener_top_amonestados(data['actas_penya'], top_n=5)
        graficar_top_amonestados_home(top_amonestados)
    
    # Nueva fila para más estadísticas
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 5 jugadores con más minutos (barras negras)
        top_minutos = obtener_jugadores_mas_minutos(data['actas_penya'], top_n=5)
        graficar_minutos_jugados_home(top_minutos)
    
    with col2:
        # Información sobre navegación
        st.info(
            """
            Este dashboard muestra un resumen general del equipo Penya Independent.
            
            Para análisis más detallados:
            
            - **🧍 Jugadores**: Estadísticas individuales de cada jugador
            - **🧍🧍 Equipo**: Análisis de partidos, goles y tarjetas
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


