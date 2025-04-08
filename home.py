"""
Página principal del dashboard de Penya Independent
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re

# Importar módulos propios
from utils.data import cargar_datos
from utils.ui import page_config
from common.menu import crear_menu, mostrar_pagina_actual
from calculos.calculo_equipo import calcular_estadisticas_generales, calcular_metricas_avanzadas, calcular_goles_contra
from calculos.calculo_jugadores import obtener_top_goleadores, obtener_top_amonestados, obtener_jugadores_mas_minutos
from utils.pdf_export import show_download_button

# Importar funciones de visualización especiales para la página Home
from visualizaciones.jugadores_home import (
    graficar_top_goleadores_home,
    graficar_top_amonestados_home,
    graficar_minutos_jugados_home
)

def normalizar_nombre_equipo(nombre):
    if pd.isna(nombre):
        return ""
    nombre = str(nombre).replace('"', '').replace('\\', '')
    nombre = re.sub(r'\s+', '', nombre)  # Elimina todos los espacios internos
    return nombre.upper().strip()

def dashboard_principal():
    """Función que muestra el dashboard principal"""
    
    # Cargar datos
    data = cargar_datos()
    
    equipo_objetivo = "PENYA INDEPENDENT A"
    equipo_normalizado = normalizar_nombre_equipo(equipo_objetivo)

    # Filtrar los datos para PENYA INDEPENDENT A usando coincidencia exacta y normalizada
    actas_penya = data['actas'][data['actas']['equipo'].apply(normalizar_nombre_equipo) == equipo_normalizado]
    goles_penya = data['goles'][data['goles']['equipo'].apply(normalizar_nombre_equipo) == equipo_normalizado]
    partidos_penya = data['jornadas'][
        (data['jornadas']['equipo_local'].apply(normalizar_nombre_equipo) == equipo_normalizado) |
        (data['jornadas']['equipo_visitante'].apply(normalizar_nombre_equipo) == equipo_normalizado)
    ]
    
    # Calcular estadísticas generales
    estadisticas_equipo = calcular_estadisticas_generales(
        actas_penya, goles_penya, partidos_penya, equipo_seleccionado=equipo_objetivo
    )
    
    # Calcular goles recibidos de forma robusta
    try:
        metricas_avanzadas = calcular_metricas_avanzadas(
            partidos_penya, goles_penya, actas_penya, data['actas'],
            equipo_seleccionado=equipo_objetivo
        )
        goles_recibidos = metricas_avanzadas['goles'][1]['valor']
    except Exception as e:
        try:
            goles_recibidos = calcular_goles_contra(
                actas_penya, partidos_penya, data['actas'], equipo_seleccionado=equipo_objetivo
            )
        except Exception as e2:
            st.error(f"Error al calcular goles en contra: {e2}")
            goles_recibidos = 0

    # Crear un diccionario con los datos filtrados para el botón PDF
    datos_filtrados = {
        'actas_penya': actas_penya,
        'goles_penya': goles_penya,
        'partidos_penya': partidos_penya,
        'actas': data['actas'],  # Datos completos necesarios para cálculos
        'goles_recibidos': goles_recibidos  # Añadir goles recibidos al diccionario para el PDF
    }
    
    # Métricas resumen con el botón de PDF en la misma línea
    col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])
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
    with col6:
        # Añadir un espacio para alinear verticalmente con las métricas
        st.write("")
        show_download_button(datos_filtrados, 'home')
    
    st.markdown("---")

    # Visualizaciones
    col1, col2 = st.columns(2)
    with col1:
        top_goleadores = obtener_top_goleadores(actas_penya, top_n=5)
        graficar_top_goleadores_home(top_goleadores)
    with col2:
        top_amonestados = obtener_top_amonestados(actas_penya, top_n=5)
        graficar_top_amonestados_home(top_amonestados)
    
    col1, col2 = st.columns(2)
    with col1:
        top_minutos = obtener_jugadores_mas_minutos(actas_penya, top_n=5)
        graficar_minutos_jugados_home(top_minutos)
    with col2:
        st.info(
            """
            Este dashboard muestra un resumen general del equipo Penya Independent.
            
            Para análisis más detallados:
            
            - **🧍 Jugadores**: Estadísticas individuales de cada jugador
            - **🧍🧍 Equipo**: Análisis de partidos, goles y tarjetas
            """
        )
    
    st.markdown("---")
    st.caption("Datos actualizados. Dashboard desarrollado con Streamlit.")

def main():
    """Función principal que muestra el dashboard"""
    
    # Configurar estilos CSS para maquetar la cabecera similar a la imagen
    st.markdown("""
    <style>
    .header-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0;
        margin-bottom: 10px;
    }
    .logo-small {
        width: 70px;
        height: auto;
    }
    .menu-container {
        width: 100%;
        margin-top: 0;
        padding-top: 0;
    }
    .user-container {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        gap: 10px;
    }
    div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] {
        align-items: center;
    }
    /* Estilo para centrar verticalmente el botón de descarga */
    div[data-testid="stVerticalBlock"] > div:has(> div.btn-download) {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Crear el menú de navegación
    pagina_seleccionada = crear_menu()
    
    # Mostrar la página correspondiente
    if pagina_seleccionada == "Inicio":
        dashboard_principal()
    else:
        mostrar_pagina_actual()


if __name__ == "__main__":
    # Configurar la página
    page_config()
    
    # Ejecutar la función principal
    main()