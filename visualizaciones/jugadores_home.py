"""
Visualizaciones relacionadas con estadísticas de jugadores - Versión para Home
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.constants import PENYA_PRIMARY_COLOR, PENYA_SECONDARY_COLOR, COLOR_TARJETAS_AMARILLAS, COLOR_TARJETAS_ROJAS

def graficar_top_goleadores_home(goleadores_df, top_n=5):
    """
    Versión especial para la página Home que muestra Top 5
    
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
        title=f'Top {top_n} Goleadores',  # Título reflejando top_n exacto
        labels={'jugador': 'Jugador', 'goles': 'Goles'},
        color_discrete_sequence=[PENYA_PRIMARY_COLOR]
    )
    
    # Personalizar el gráfico
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        xaxis_title='Goles',
        yaxis_title='',
        showlegend=False
    )
    
    # Personalizar tooltip
    fig.update_traces(
        hovertemplate='Goles: %{x}<extra></extra>'
    )
    
    # Mostrar el gráfico
    st.plotly_chart(fig, use_container_width=True)

def graficar_top_amonestados_home(amonestados_df, top_n=5):
    """
    Versión especial para la página Home que muestra Top 5
    
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
        marker=dict(color=COLOR_TARJETAS_AMARILLAS)  # Color amarillo
    ))
    
    # Añadir barras para tarjetas rojas
    fig.add_trace(go.Bar(
        y=df['jugador'],
        x=df['Tarjetas Rojas'],
        name='Rojas',
        orientation='h',
        marker=dict(color=COLOR_TARJETAS_ROJAS)  # Color rojo
    ))
    
    # Personalizar el gráfico
    fig.update_layout(
        title=f'Top {top_n} Jugadores con Más Tarjetas',  # Título reflejando top_n exacto
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
    
    # Personalizar tooltip
    fig.update_traces(
        hovertemplate='Tarjetas: %{x}<extra></extra>'
    )
    
    # Mostrar el gráfico
    st.plotly_chart(fig, use_container_width=True)

def graficar_minutos_jugados_home(minutos_df, top_n=5):
    """
    Versión especial para la página Home que muestra Top 5
    
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
        title=f'Top {top_n} Jugadores con Más Minutos',  # Título reflejando top_n exacto
        labels={'jugador': 'Jugador', 'minutos_jugados': 'Minutos Jugados'},
        color_discrete_sequence=[PENYA_PRIMARY_COLOR]
    )
    
    # Personalizar el gráfico
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        xaxis_title='Minutos Jugados',
        yaxis_title='',
        showlegend=False
    )
    
    # Personalizar tooltip
    fig.update_traces(
        hovertemplate='Minutos: %{x}<extra></extra>'
    )
    
    # Mostrar el gráfico
    st.plotly_chart(fig, use_container_width=True)