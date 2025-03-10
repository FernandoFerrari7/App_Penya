"""
Visualizaciones relacionadas con estadísticas del equipo
"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

def mostrar_resumen_equipo(estadisticas):
    """
    Muestra un resumen de estadísticas del equipo
    
    Args:
        estadisticas: Diccionario con estadísticas generales
    """
    # Crear las columnas para las métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Partidos Jugados", estadisticas['partidos_jugados'])
    
    with col2:
        st.metric("Goles Marcados", estadisticas['goles_marcados'])
    
    with col3:
        st.metric("Tarjetas Amarillas", estadisticas['tarjetas_amarillas'])
    
    with col4:
        st.metric("Tarjetas Rojas", estadisticas['tarjetas_rojas'])
    
    # Mostrar promedio de goles por partido
    st.metric("Promedio Goles/Partido", estadisticas['promedio_goles'])

def graficar_tarjetas_por_jornada(tarjetas_df):
    """
    Crea un gráfico de tarjetas por jornada
    
    Args:
        tarjetas_df: DataFrame con tarjetas por jornada
    """
    if tarjetas_df.empty:
        st.warning("No hay datos de tarjetas por jornada")
        return
    
    # Crear gráfico de líneas
    fig = go.Figure()
    
    # Añadir línea para tarjetas amarillas
    fig.add_trace(go.Scatter(
        x=tarjetas_df['jornada'],
        y=tarjetas_df['Tarjetas Amarillas'],
        mode='lines+markers',
        name='Amarillas',
        line=dict(color='#FFD700', width=2),
        marker=dict(size=8)
    ))
    
    # Añadir línea para tarjetas rojas
    fig.add_trace(go.Scatter(
        x=tarjetas_df['jornada'],
        y=tarjetas_df['Tarjetas Rojas'],
        mode='lines+markers',
        name='Rojas',
        line=dict(color='#FF4136', width=2),
        marker=dict(size=8)
    ))
    
    # Personalizar el gráfico
    fig.update_layout(
        title='Tarjetas por Jornada',
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
    
    # Mostrar el gráfico
    st.plotly_chart(fig, use_container_width=True)

def graficar_goles_por_tiempo(goles_por_tiempo):
    """
    Crea un gráfico de distribución de goles por minuto
    
    Args:
        goles_por_tiempo: Series con distribución de goles por rango de minutos
    """
    if goles_por_tiempo.empty:
        st.warning("No hay datos de goles por tiempo")
        return
    
    # Convertir a DataFrame para usar con Plotly
    df = goles_por_tiempo.reset_index()
    df.columns = ['Rango', 'Goles']
    
    # Crear gráfico de barras
    fig = px.bar(
        df,
        x='Rango',
        y='Goles',
        title='Distribución de Goles por Minuto',
        labels={'Rango': 'Rango de Minutos', 'Goles': 'Número de Goles'},
        color='Goles',
        color_continuous_scale='Greens'
    )
    
    # Personalizar el gráfico
    fig.update_layout(
        xaxis_title='Rango de Minutos',
        yaxis_title='Número de Goles',
        showlegend=False
    )
    
    # Mostrar el gráfico
    st.plotly_chart(fig, use_container_width=True)

def graficar_tipos_goles(tipos_goles):
    """
    Crea un gráfico de tipos de goles marcados
    
    Args:
        tipos_goles: Series con conteo de tipos de goles
    """
    if tipos_goles.empty:
        st.warning("No hay datos de tipos de goles")
        return
    
    # Convertir a DataFrame para usar con Plotly
    df = tipos_goles.reset_index()
    df.columns = ['Tipo', 'Cantidad']
    
    # Crear gráfico de pastel
    fig = px.pie(
        df,
        values='Cantidad',
        names='Tipo',
        title='Tipos de Goles Marcados',
        color_discrete_sequence=px.colors.sequential.Greens
    )
    
    # Personalizar el gráfico
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hole=0.4
    )
    
    # Mostrar el gráfico
    st.plotly_chart(fig, use_container_width=True)

def graficar_goles_por_rival(goles_rival_df, top_n=10):
    """
    Crea un gráfico de goles marcados por rival
    
    Args:
        goles_rival_df: DataFrame con goles por rival
        top_n: Número de rivales a mostrar
    """
    if goles_rival_df.empty:
        st.warning("No hay datos de goles por rival")
        return
    
    # Limitar a los top_n rivales
    df = goles_rival_df.head(top_n)
    
    # Crear gráfico de barras horizontales
    fig = px.bar(
        df,
        y='rival',
        x='goles',
        orientation='h',
        title=f'Goles Marcados por Rival',
        labels={'rival': 'Equipo Rival', 'goles': 'Goles'},
        color='goles',
        color_continuous_scale='Blues'
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