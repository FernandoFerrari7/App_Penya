"""
Visualizaciones relacionadas con estadísticas de jugadores
"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

def mostrar_tarjeta_jugador(estadisticas):
    """
    Muestra la tarjeta de estadísticas de un jugador
    
    Args:
        estadisticas: Diccionario con estadísticas del jugador
    """
    if not estadisticas:
        st.warning("No se encontraron datos para este jugador")
        return
    
    # Crear columnas para la tarjeta
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Avatar placeholder (se podría reemplazar con foto real del jugador)
        st.image("https://via.placeholder.com/150", width=150)
    
    with col2:
        # Nombre del jugador
        st.title(estadisticas['nombre'])
        
        # Estadísticas principales
        col_a, col_b, col_c, col_d = st.columns(4)
        
        with col_a:
            st.metric("Goles", estadisticas['goles'])
        
        with col_b:
            st.metric("Tarjetas", f"{estadisticas['tarjetas_amarillas']}🟨 / {estadisticas['tarjetas_rojas']}🟥")
        
        with col_c:
            st.metric("Minutos", estadisticas['minutos_jugados'])
        
        with col_d:
            st.metric("Partidos", estadisticas['partidos_jugados'])
    
    # Más detalles
    st.subheader("Participación")
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.metric("Titular", estadisticas['titularidades'])
    
    with col_b:
        st.metric("Suplente", estadisticas['suplencias'])
    
    with col_c:
        st.metric("Min/Partido", estadisticas['minutos_por_partido'])

def graficar_minutos_por_jornada(minutos_df):
    """
    Crea un gráfico de minutos jugados por jornada
    
    Args:
        minutos_df: DataFrame con minutos por jornada
    """
    if minutos_df.empty:
        st.warning("No hay datos de minutos para este jugador")
        return

    # Crear gráfico de barras usando Plotly
    fig = px.bar(
        minutos_df, 
        x='jornada', 
        y='minutos_jugados',
        color='es_titular',
        labels={'jornada': 'Jornada', 'minutos_jugados': 'Minutos Jugados', 'es_titular': 'Titular'},
        title='Minutos Jugados por Jornada',
        color_discrete_map={True: 'green', False: 'orange'},
        hover_data=['rival']
    )
    
    # Personalizar el gráfico
    fig.update_layout(
        xaxis_title='Jornada',
        yaxis_title='Minutos',
        yaxis_range=[0, 100],
        legend_title="Condición"
    )
    
    # Mostrar el gráfico
    st.plotly_chart(fig, use_container_width=True)

def graficar_top_goleadores(goleadores_df, top_n=10):
    """
    Crea un gráfico de los mejores goleadores
    
    Args:
        goleadores_df: DataFrame con goleadores
        top_n: Número de jugadores a mostrar
    """
    if goleadores_df.empty:
        st.warning("No hay datos de goleadores")
        return
    
    # Limitar a los top_n jugadores
    df = goleadores_df.head(top_n).copy()
    
    # Crear gráfico de barras horizontales
    fig = px.bar(
        df,
        y='jugador',
        x='goles',
        orientation='h',
        title=f'Top {top_n} Goleadores',
        labels={'jugador': 'Jugador', 'goles': 'Goles'},
        color='goles',
        color_continuous_scale='Greens'
    )
    
    # Personalizar el gráfico
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        xaxis_title='Goles',
        yaxis_title='',
        showlegend=False
    )
    
    # Mostrar el gráfico
    st.plotly_chart(fig, use_container_width=True)

def graficar_top_amonestados(amonestados_df, top_n=10):
    """
    Crea un gráfico de los jugadores más amonestados
    
    Args:
        amonestados_df: DataFrame con jugadores amonestados
        top_n: Número de jugadores a mostrar
    """
    if amonestados_df.empty:
        st.warning("No hay datos de amonestaciones")
        return
    
    # Limitar a los top_n jugadores
    df = amonestados_df.head(top_n).copy()
    
    # Crear gráfico de barras apiladas
    fig = go.Figure()
    
    # Añadir barras para tarjetas amarillas
    fig.add_trace(go.Bar(
        y=df['jugador'],
        x=df['Tarjetas Amarillas'],
        name='Amarillas',
        orientation='h',
        marker=dict(color='#FFD700')  # Color amarillo
    ))
    
    # Añadir barras para tarjetas rojas
    fig.add_trace(go.Bar(
        y=df['jugador'],
        x=df['Tarjetas Rojas'],
        name='Rojas',
        orientation='h',
        marker=dict(color='#FF4136')  # Color rojo
    ))
    
    # Personalizar el gráfico
    fig.update_layout(
        title=f'Top {top_n} Jugadores con Más Tarjetas',
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
        )
    )
    
    # Mostrar el gráfico
    st.plotly_chart(fig, use_container_width=True)

def graficar_minutos_jugados(minutos_df, top_n=10):
    """
    Crea un gráfico de los jugadores con más minutos
    
    Args:
        minutos_df: DataFrame con minutos por jugador
        top_n: Número de jugadores a mostrar
    """
    if minutos_df.empty:
        st.warning("No hay datos de minutos jugados")
        return
    
    # Limitar a los top_n jugadores
    df = minutos_df.head(top_n).copy()
    
    # Crear gráfico de barras horizontales
    fig = px.bar(
        df,
        y='jugador',
        x='minutos_jugados',
        orientation='h',
        title=f'Top {top_n} Jugadores con Más Minutos',
        labels={'jugador': 'Jugador', 'minutos_jugados': 'Minutos Jugados'},
        color='minutos_jugados',
        color_continuous_scale='Blues'
    )
    
    # Personalizar el gráfico
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        xaxis_title='Minutos Jugados',
        yaxis_title='',
        showlegend=False
    )
    
    # Mostrar el gráfico
    st.plotly_chart(fig, use_container_width=True)