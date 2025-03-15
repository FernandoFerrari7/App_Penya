"""
Página de análisis de equipos y partidos
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Importar módulos propios
from utils.data import cargar_datos
from utils.ui import show_sidebar
from calculos.calculo_equipo import obtener_rivales_con_goles, analizar_tarjetas_por_jornada, analizar_tipos_goles
from calculos.calculo_jugadores import (
    analizar_goles_por_tiempo, 
    analizar_goles_por_jugador, 
    analizar_tarjetas_por_jugador,
    analizar_minutos_por_jugador,
    analizar_distribucion_sustituciones
)
from visualizaciones.equipo import (
    graficar_tarjetas_por_jornada, 
    graficar_tipos_goles, 
    graficar_goles_por_tiempo
)
from visualizaciones.jugadores import graficar_goles_por_jugador, graficar_tarjetas_por_jugador
from visualizaciones.minutos import (
    graficar_minutos_por_jugador,
    graficar_minutos_por_jugador_desglose,
    graficar_distribucion_sustituciones
)
from utils.constants import PENYA_PRIMARY_COLOR, PENYA_SECONDARY_COLOR

# Cargar datos
data = cargar_datos()

def mostrar_tarjeta_metrica_compacta(titulo, valor, valor_referencia=None, color_valor="#FF8C00"):
    """
    Muestra una tarjeta métrica compacta (versión reducida)
    """
    # Determinar color basado en comparación con media
    if valor_referencia is not None:
        if titulo == "Goles a favor" and valor < valor_referencia:
            color_valor = "#FF4136"  # Rojo (por debajo de la media)
        elif titulo == "Goles a favor" and valor >= valor_referencia:
            color_valor = "#4CAF50"  # Verde (por encima de la media)
        elif titulo == "Goles en contra" and valor > valor_referencia:
            color_valor = "#FF4136"  # Rojo (por encima de la media, es malo)
        elif titulo == "Goles en contra" and valor <= valor_referencia:
            color_valor = "#4CAF50"  # Verde (por debajo de la media, es bueno)
    
    # Aplicar estilos CSS más compactos
    st.markdown(
        f"""
        <div style="
            border-radius: 4px;
            border: 1px solid #ddd;
            padding: 8px 5px;
            margin: 2px 0;
            background-color: white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            text-align: center;
            height: 100%;
        ">
            <div style="
                font-size: 0.85rem;
                margin: 0;
                color: #333;
                font-weight: 600;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            ">{titulo}</div>
            <div style="
                font-size: 1.5rem;
                font-weight: 700;
                color: {color_valor};
                line-height: 1.2;
                margin-top: 4px;
            ">{valor} {f'<span style="font-size: 0.75rem; color: #777; font-weight: normal;">({valor_referencia})</span>' if valor_referencia else ''}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def main():
    """Función principal que muestra el análisis de equipos"""
    
    # Título principal
    st.title("Análisis de Equipo")
    
    # Mostrar barra lateral
    show_sidebar()
    
    # Definir las métricas en el orden solicitado
    metricas = [
        {
            'titulo': 'Partidos Jugados',
            'valor': 19,
            'referencia': None,
            'color': PENYA_SECONDARY_COLOR  # Negro
        },
        {
            'titulo': 'Num. Jugadores',
            'valor': 25,
            'referencia': 27.7,
            'color': PENYA_SECONDARY_COLOR  # Negro
        },
        {
            'titulo': 'Goles a favor',
            'valor': 18,
            'referencia': 28,
            'color': '#FF8C00'  # Se determinará dinámicamente
        },
        {
            'titulo': 'Goles en contra',
            'valor': 32,
            'referencia': 30,  # Media de la liga
            'color': '#FF4136'  # Se determinará dinámicamente
        },
        {
            'titulo': 'Tarjetas Amarillas',
            'valor': 33,
            'referencia': 42,
            'color': '#FFD700'  # Amarillo
        },
        {
            'titulo': 'Tarjetas Amarillas Rival',
            'valor': 40,
            'referencia': 45,  # Media de la liga
            'color': '#FFD700'  # Amarillo
        },
        {
            'titulo': 'Tarjetas Rojas',
            'valor': 2,
            'referencia': 1.6,
            'color': '#FF4136'  # Rojo
        },
        {
            'titulo': 'Tarjetas Rojas Rival',
            'valor': 1,
            'referencia': 1.8,  # Media de la liga
            'color': '#FF4136'  # Rojo
        }
    ]
    
    # Crear una fila para las tarjetas métricas (8 columnas)
    metric_cols = st.columns(8)
    for i, metrica in enumerate(metricas):
        with metric_cols[i]:
            mostrar_tarjeta_metrica_compacta(
                metrica['titulo'],
                metrica['valor'],
                metrica['referencia'],
                metrica['color']
            )
    
    # Crear dos columnas para las visualizaciones
    col_goles, col_tarjetas = st.columns(2)
    
    # Sección de Visualizaciones de Goles
    with col_goles:
        # Tabs para diferentes visualizaciones de goles en el orden solicitado
        gol_tab1, gol_tab2, gol_tab3 = st.tabs([
            "Goles por Jugador",
            "Goles por Minuto", 
            "Tipos de Goles"
        ])
        
        with gol_tab1:
            # Goles por jugador
            goles_jugador = analizar_goles_por_jugador(data['goles_penya'], data['actas_penya'])
            graficar_goles_por_jugador(goles_jugador)
        
        with gol_tab2:
            # Distribución de goles por minuto
            goles_tiempo = analizar_goles_por_tiempo(data['goles_penya'])
            graficar_goles_por_tiempo(goles_tiempo)
        
        with gol_tab3:
            # Tipos de goles
            tipos_goles = analizar_tipos_goles(data['goles_penya'])
            graficar_tipos_goles(tipos_goles)
    
    # Sección de Visualizaciones de Tarjetas
    with col_tarjetas:
        # Tabs para diferentes visualizaciones de tarjetas en el orden solicitado
        tarjeta_tab1, tarjeta_tab2 = st.tabs([
            "Tarjetas por Jugador",
            "Tarjetas por Jornada"
        ])
        
        with tarjeta_tab1:
            # Análisis de tarjetas por jugador (todos los jugadores)
            tarjetas_jugador = analizar_tarjetas_por_jugador(data['actas_penya'])
            graficar_tarjetas_por_jugador(tarjetas_jugador, top_n=None)
        
        with tarjeta_tab2:
            # Análisis de tarjetas por jornada
            tarjetas_jornada = analizar_tarjetas_por_jornada(data['actas_penya'])
            graficar_tarjetas_por_jornada(tarjetas_jornada)
    
    # Separador
    st.markdown("---")
    
    # CAMBIO: Colocar en la misma fila "Análisis de Minutos por Jugador" y "Distribución de Sustituciones"
    col_minutos, col_sustituciones = st.columns(2)
    
    # Sección de Análisis de Minutos (columna izquierda)
    with col_minutos:
        st.subheader("Análisis de Minutos por Jugador")
        
        # Calcular datos de minutos
        minutos_jugador = analizar_minutos_por_jugador(data['actas_penya'])
        
        # Pestañas para los diferentes análisis de minutos (solo dos pestañas)
        minutos_tab1, minutos_tab2 = st.tabs([
            "Local vs Visitante", 
            "Titular vs Suplente"
        ])
        
        with minutos_tab1:
            # Desglose local vs visitante (CAMBIO: usar colores de Penya y mostrar todos los jugadores)
            graficar_minutos_por_jugador_desglose(minutos_jugador, top_n=None, tipo_desglose='local_visitante', 
                                                  color_izquierda=PENYA_PRIMARY_COLOR, color_derecha=PENYA_SECONDARY_COLOR)
        
        with minutos_tab2:
            # Desglose titular vs suplente (CAMBIO: usar colores de Penya y mostrar todos los jugadores)
            graficar_minutos_por_jugador_desglose(minutos_jugador, top_n=None, tipo_desglose='titular_suplente',
                                                  color_izquierda=PENYA_PRIMARY_COLOR, color_derecha=PENYA_SECONDARY_COLOR)
    
    # Sección de Distribución de Sustituciones (columna derecha)
    with col_sustituciones:
        st.subheader("Distribución de Sustituciones")
        
        # Comprobar si hay datos de sustituciones
        if 'sustituciones_penya' in data:
            # Calcular distribución de sustituciones con un rango de 5 minutos
            sustituciones_data = analizar_distribucion_sustituciones(data['sustituciones_penya'], rango_minutos=5)
            
            # Mostrar gráfico de sustituciones con el nuevo formato
            graficar_distribucion_sustituciones(sustituciones_data)
        else:
            st.warning("No hay datos disponibles para el análisis de sustituciones")

if __name__ == "__main__":
    main()