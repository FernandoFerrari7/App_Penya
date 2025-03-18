"""
Página de análisis de equipos y partidos
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Importar módulos propios
from utils.data import cargar_datos
from utils.ui import page_config  # Solo importar page_config
from calculos.calculo_equipo import obtener_rivales_con_goles, analizar_tarjetas_por_jornada, analizar_tipos_goles, calcular_metricas_avanzadas
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

# Configurar la página
page_config()

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
    
    # CAMBIO: Quitar el título principal para ahorrar espacio
    # st.title("Análisis de Equipo")
    
    # Eliminada la llamada a show_sidebar
    
    # Calcular métricas avanzadas
    try:
        metricas_avanzadas = calcular_metricas_avanzadas(
            data['partidos_penya'], 
            data['goles_penya'], 
            data['actas_penya'], 
            data['actas']
        )
        
        # Actualizar métricas con datos calculados dinámicamente
        metricas = [
            {
                'titulo': 'Partidos Jugados',
                'valor': metricas_avanzadas['general'][1]['valor'],
                'referencia': None,
                'color': PENYA_SECONDARY_COLOR  # Negro
            },
            {
                'titulo': 'Num. Jugadores',
                'valor': metricas_avanzadas['general'][0]['valor'],
                'referencia': metricas_avanzadas['general'][0]['referencia'],
                'color': PENYA_SECONDARY_COLOR  # Negro
            },
            {
                'titulo': 'Goles a favor',
                'valor': metricas_avanzadas['goles'][0]['valor'],
                'referencia': metricas_avanzadas['goles'][0]['referencia'],
                'color': '#FF8C00'  # Se determinará dinámicamente
            },
            {
                'titulo': 'Goles en contra',
                'valor': metricas_avanzadas['goles'][1]['valor'],
                'referencia': 30,  # Media de la liga
                'color': '#FF4136'  # Se determinará dinámicamente
            },
            {
                'titulo': 'Tarjetas Amarillas',
                'valor': metricas_avanzadas['tarjetas'][0]['valor'],
                'referencia': metricas_avanzadas['tarjetas'][0]['referencia'],
                'color': '#FFD700'  # Amarillo
            },
            {
                'titulo': 'TA Rival',
                'valor': metricas_avanzadas['tarjetas'][1]['valor'],
                'referencia': 45,  # Media de la liga
                'color': '#FFD700'  # Amarillo
            },
            {
                'titulo': 'Tarjetas Rojas',
                'valor': metricas_avanzadas['tarjetas'][2]['valor'],
                'referencia': metricas_avanzadas['tarjetas'][2]['referencia'],
                'color': '#FF4136'  # Rojo
            },
            {
                'titulo': 'TR Rival',
                'valor': metricas_avanzadas['tarjetas'][3]['valor'],
                'referencia': 1.8,  # Media de la liga
                'color': '#FF4136'  # Rojo
            }
        ]
    except:
        # Si no se pueden calcular, usar valores predeterminados
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
                'titulo': 'TA Rival',
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
                'titulo': 'TR Rival',
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
        # CAMBIO: Agregar título "Goles"
        st.subheader("Goles")
        
        # Tabs para diferentes visualizaciones de goles en el orden solicitado
        gol_tab1, gol_tab2, gol_tab3 = st.tabs([
            "Goles por Jugador",
            "Goles por Minuto", 
            "Tipos de Goles"
        ])
        
        with gol_tab1:
            # Goles por jugador - CAMBIO: Quitar título del gráfico
            goles_jugador = analizar_goles_por_jugador(data['goles_penya'], data['actas_penya'])
            fig = px.bar(
                goles_jugador,
                y='jugador',
                x='goles',
                orientation='h',
                labels={'jugador': 'Jugador', 'goles': 'Goles'},
                color_discrete_sequence=[PENYA_PRIMARY_COLOR]
            )
            
            fig.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                xaxis_title='Goles',
                yaxis_title='',
                showlegend=False,
                height=max(400, len(goles_jugador) * 25)
            )
            
            fig.update_traces(
                hovertemplate='Goles: %{x}<extra></extra>'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with gol_tab2:
            # Distribución de goles por minuto - CAMBIO: Quitar título del gráfico y usar solo valores enteros en eje Y
            goles_tiempo = analizar_goles_por_tiempo(data['goles_penya'])
            df = goles_tiempo.reset_index()
            df.columns = ['Rango', 'Goles']
            
            fig = px.bar(
                df,
                x='Rango',
                y='Goles',
                labels={'Rango': 'Rango de Minutos', 'Goles': 'Número de Goles'},
                color_discrete_sequence=[PENYA_PRIMARY_COLOR]
            )
            
            fig.update_layout(
                xaxis_title='Rango de Minutos',
                yaxis_title='Número de Goles',
                showlegend=False,
                # CAMBIO: Forzar valores enteros en el eje Y
                yaxis=dict(
                    tickmode='linear',
                    tick0=0,
                    dtick=1
                )
            )
            
            fig.update_traces(
                hovertemplate='<b>%{x}</b><br>Goles: %{y}<extra></extra>'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with gol_tab3:
            # Tipos de goles - CAMBIO: Quitar título del gráfico y referencias (ya están en el gráfico)
            tipos_goles = analizar_tipos_goles(data['goles_penya'])
            df = tipos_goles.reset_index()
            df.columns = ['Tipo', 'Cantidad']
            
            fig = px.pie(
                df,
                values='Cantidad',
                names='Tipo',
                color_discrete_sequence=[PENYA_PRIMARY_COLOR, PENYA_SECONDARY_COLOR, "#555555", "#777777"]
            )
            
            fig.update_layout(
                showlegend=False  # CAMBIO: Quitar leyenda ya que la información ya está en las etiquetas
            )
            
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hole=0.4,
                hovertemplate='<b>%{label}</b><br>Cantidad: %{value}<br>(%{percent})<extra></extra>'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Sección de Visualizaciones de Tarjetas
    with col_tarjetas:
        # CAMBIO: Agregar título "Tarjetas"
        st.subheader("Tarjetas")
        
        # Tabs para diferentes visualizaciones de tarjetas en el orden solicitado
        tarjeta_tab1, tarjeta_tab2 = st.tabs([
            "Tarjetas por Jugador",
            "Tarjetas por Jornada"
        ])
        
        with tarjeta_tab1:
            # Análisis de tarjetas por jugador (todos los jugadores) - CAMBIO: Quitar título y invertir orden de referencias
            tarjetas_jugador = analizar_tarjetas_por_jugador(data['actas_penya'])
            
            # Crear gráfico de barras apiladas con orden invertido de las leyendas
            fig = go.Figure()
            
            # CAMBIO: Invertir orden - Primero rojas, luego amarillas
            fig.add_trace(go.Bar(
                y=tarjetas_jugador['jugador'],
                x=tarjetas_jugador['Tarjetas Rojas'],
                name='Rojas',
                orientation='h',
                marker=dict(color='#FF4136')  # Color rojo
            ))
            
            fig.add_trace(go.Bar(
                y=tarjetas_jugador['jugador'],
                x=tarjetas_jugador['Tarjetas Amarillas'],
                name='Amarillas',
                orientation='h',
                marker=dict(color='#FFD700')  # Color amarillo
            ))
            
            fig.update_layout(
                xaxis_title='Número de Tarjetas',
                yaxis_title='',
                barmode='stack',
                yaxis={'categoryorder': 'total ascending'},
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                height=max(400, len(tarjetas_jugador) * 25)
            )
            
            fig.update_traces(
                hovertemplate='Tarjetas: %{x}<extra></extra>'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tarjeta_tab2:
            # Análisis de tarjetas por jornada - CAMBIO: Quitar título
            tarjetas_jornada = analizar_tarjetas_por_jornada(data['actas_penya'])
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=tarjetas_jornada['jornada'],
                y=tarjetas_jornada['Tarjetas Amarillas'],
                mode='lines+markers',
                name='Amarillas',
                line=dict(color='#FFD700', width=2),
                marker=dict(size=8)
            ))
            
            fig.add_trace(go.Scatter(
                x=tarjetas_jornada['jornada'],
                y=tarjetas_jornada['Tarjetas Rojas'],
                mode='lines+markers',
                name='Rojas',
                line=dict(color='#FF4136', width=2),
                marker=dict(size=8)
            ))
            
            fig.update_layout(
                xaxis_title='Jornada',
                yaxis_title='Número de Tarjetas',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            fig.update_traces(
                hovertemplate='<b>Jornada %{x}</b><br>Tarjetas: %{y}<extra></extra>'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Separador
    st.markdown("---")
    
    # CAMBIO: Colocar en la misma fila "Minutos por Jugador" y "Distribución de Sustituciones"
    col_minutos, col_sustituciones = st.columns(2)
    
    # Sección de Análisis de Minutos (columna izquierda)
    with col_minutos:
        # CAMBIO: Actualizar título de "Análisis de Minutos por Jugador" a "Minutos por Jugador"
        st.subheader("Minutos por Jugador")
        
        # Calcular datos de minutos
        minutos_jugador = analizar_minutos_por_jugador(data['actas_penya'])
        
        # Pestañas para los diferentes análisis de minutos (solo dos pestañas)
        minutos_tab1, minutos_tab2 = st.tabs([
            "Local vs Visitante", 
            "Titular vs Suplente"
        ])
        
        with minutos_tab1:
            # CAMBIO: Quitar título del gráfico e invertir barras pero manteniendo orden de las referencias (Local, Visitante)
            # Desglose local vs visitante
            df = minutos_jugador.copy()
            
            # Crear figura
            fig = go.Figure()
            
            # CAMBIO: Primero local (naranja), luego visitante, pero manteniendo mismo orden de referencias
            fig.add_trace(go.Bar(
                y=df['jugador'],
                x=df['minutos_local'],
                name='Local',
                orientation='h',
                marker=dict(color=PENYA_PRIMARY_COLOR)
            ))
            
            fig.add_trace(go.Bar(
                y=df['jugador'],
                x=df['minutos_visitante'],
                name='Visitante',
                orientation='h',
                marker=dict(color='#36A2EB' if PENYA_SECONDARY_COLOR is None else PENYA_SECONDARY_COLOR)
            ))
            
            fig.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                xaxis_title='Minutos Jugados',
                yaxis_title='',
                barmode='stack',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with minutos_tab2:
            # CAMBIO: Quitar título del gráfico e invertir barras pero manteniendo orden de las referencias (Titular, Suplente)
            # Desglose titular vs suplente
            df = minutos_jugador.copy()
            
            # Crear figura
            fig = go.Figure()
            
            # CAMBIO: Primero titular (naranja), luego suplente, pero manteniendo mismo orden de referencias
            fig.add_trace(go.Bar(
                y=df['jugador'],
                x=df['minutos_titular'],
                name='Como Titular',
                orientation='h',
                marker=dict(color=PENYA_PRIMARY_COLOR)
            ))
            
            fig.add_trace(go.Bar(
                y=df['jugador'],
                x=df['minutos_suplente'],
                name='Como Suplente',
                orientation='h',
                marker=dict(color='#888888' if PENYA_SECONDARY_COLOR is None else PENYA_SECONDARY_COLOR)
            ))
            
            fig.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                xaxis_title='Minutos Jugados',
                yaxis_title='',
                barmode='stack',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Sección de Distribución de Sustituciones (columna derecha)
    with col_sustituciones:
        st.subheader("Distribución de Sustituciones")
        
        # Comprobar si hay datos de sustituciones
        if 'sustituciones_penya' in data:
            # Calcular distribución de sustituciones con un rango de 5 minutos
            sustituciones_data = analizar_distribucion_sustituciones(data['sustituciones_penya'], rango_minutos=5)
            
            # Pasar el trabajo al archivo minutos.py (función actualizada)
            graficar_distribucion_sustituciones(sustituciones_data)
        else:
            st.warning("No hay datos disponibles para el análisis de sustituciones")

if __name__ == "__main__":
    main()