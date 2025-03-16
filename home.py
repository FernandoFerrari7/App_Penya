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
from calculos.calculo_equipo import calcular_estadisticas_generales
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
    
    # Mostrar barra lateral
    show_sidebar()
    
    # Encabezado con logos y título
    col_logo_izq, col_titulo, col_logo_der = st.columns([1, 3, 1])
    
    with col_logo_izq:
        # Logo FFIB a la izquierda (tamaño aumentado)
        st.image("assets/logo_ffib.png", width=150)
    
    with col_titulo:
        # Diseño del título principal con subtítulo
        st.markdown("""
        <div style="text-align: center;">
            <h1 style="margin-bottom: 0px; padding-bottom: 0px;">Penya Independent</h1>
            <h4 style="margin-top: 0px; color: #636363; font-weight: 700;">Análisis de Rendimiento</h4>
        </div>
        """, unsafe_allow_html=True)
    
    with col_logo_der:
        # Logo Penya a la derecha
        st.image("assets/logo_penya.png", width=120)
    
    # Espacio para separar el título del contenido
    st.markdown("---")
    
    # Calcular estadísticas generales
    estadisticas_equipo = calcular_estadisticas_generales(
        data['actas_penya'], 
        data['goles_penya'], 
        data['partidos_penya']
    )
    
    # Goles en contra - mantener el valor actual hasta implementar el cálculo correcto
    goles_recibidos = 32
    
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
        # Top 5 jugadores con más minutos
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