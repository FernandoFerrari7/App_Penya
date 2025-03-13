"""
Visualizaciones relacionadas con minutos jugados
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.constants import PENYA_PRIMARY_COLOR, PENYA_SECONDARY_COLOR

def graficar_minutos_por_jugador(minutos_df, top_n=15):
    """
    Crea un gráfico de barras con los minutos jugados por cada jugador
    
    Args:
        minutos_df: DataFrame con minutos por jugador
        top_n: Número de jugadores a mostrar
    """
    if minutos_df.empty:
        st.warning("No hay datos de minutos por jugador")
        return
    
    # Limitar a los top_n jugadores
    df = minutos_df.head(top_n).copy()
    
    # Crear gráfico de barras horizontales
    fig = px.bar(
        df,
        y='jugador',
        x='minutos_totales',
        orientation='h',
        title=f'Top {top_n} Jugadores por Minutos Jugados',
        labels={'jugador': 'Jugador', 'minutos_totales': 'Minutos Jugados'},
        color_discrete_sequence=[PENYA_PRIMARY_COLOR]
    )
    
    # Personalizar el gráfico
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        xaxis_title='Minutos Jugados',
        yaxis_title='',
        showlegend=False,
        height=600
    )
    
    # Personalizar tooltip
    fig.update_traces(
        hovertemplate='<b>%{y}</b><br>Minutos: %{x}<extra></extra>'
    )
    
    # Mostrar el gráfico
    st.plotly_chart(fig, use_container_width=True)

def graficar_minutos_por_jugador_desglose(minutos_df, top_n=15, tipo_desglose='local_visitante', 
                                          color_izquierda=None, color_derecha=None):
    """
    Crea un gráfico de barras apiladas con el desglose de minutos por jugador
    
    Args:
        minutos_df: DataFrame con minutos por jugador
        top_n: Número de jugadores a mostrar
        tipo_desglose: Tipo de desglose ('local_visitante' o 'titular_suplente')
        color_izquierda: Color para la primera categoría (local o titular)
        color_derecha: Color para la segunda categoría (visitante o suplente)
    """
    if minutos_df.empty:
        st.warning("No hay datos de minutos por jugador")
        return
    
    # Limitar a los top_n jugadores si se especifica
    if top_n is not None:
        df = minutos_df.head(top_n).copy()
    else:
        df = minutos_df.copy()
    
    # Usar colores por defecto si no se especifican
    if color_izquierda is None:
        color_izquierda = PENYA_PRIMARY_COLOR
    
    # Configurar según el tipo de desglose
    if tipo_desglose == 'local_visitante':
        columnas = ['minutos_local', 'minutos_visitante']
        nombres = ['Local', 'Visitante']
        colores = [color_izquierda, color_derecha if color_derecha else '#36A2EB']  # Usar colores personalizados o los por defecto
        titulo = f'Minutos Jugados (Local vs Visitante)'
    else:  # titular_suplente
        columnas = ['minutos_titular', 'minutos_suplente']
        nombres = ['Como Titular', 'Como Suplente']
        colores = [color_izquierda, color_derecha if color_derecha else '#888888']  # Usar colores personalizados o los por defecto
        titulo = f'Minutos Jugados (Titular vs Suplente)'
    
    # Crear figura
    fig = go.Figure()
    
    # Añadir barras para el primer tipo
    fig.add_trace(go.Bar(
        y=df['jugador'],
        x=df[columnas[0]],
        name=nombres[0],
        orientation='h',
        marker=dict(color=colores[0])
    ))
    
    # Añadir barras para el segundo tipo
    fig.add_trace(go.Bar(
        y=df['jugador'],
        x=df[columnas[1]],
        name=nombres[1],
        orientation='h',
        marker=dict(color=colores[1])
    ))
    
    # Personalizar el gráfico
    fig.update_layout(
        title=titulo,
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
    
    # Mostrar el gráfico
    st.plotly_chart(fig, use_container_width=True)

def graficar_porcentaje_minutos_jugador(minutos_df, top_n=10):
    """
    Crea un gráfico de pastel con el porcentaje de minutos jugados por cada jugador
    
    Args:
        minutos_df: DataFrame con minutos por jugador
        top_n: Número de jugadores a mostrar individualmente (el resto se agrupa como "Otros")
    """
    if minutos_df.empty:
        st.warning("No hay datos de minutos por jugador")
        return
    
    # Preparar datos para el gráfico de pastel
    df = minutos_df.copy()
    
    # Separar los top_n jugadores y agrupar el resto como "Otros"
    top_jugadores = df.head(top_n).copy()
    otros_jugadores = df.iloc[top_n:].copy()
    
    if not otros_jugadores.empty:
        otros = pd.DataFrame({
            'jugador': ['Otros Jugadores'],
            'minutos_totales': [otros_jugadores['minutos_totales'].sum()],
            'porcentaje_del_total': [otros_jugadores['porcentaje_del_total'].sum()]
        })
        df_pastel = pd.concat([top_jugadores[['jugador', 'minutos_totales', 'porcentaje_del_total']], otros])
    else:
        df_pastel = top_jugadores[['jugador', 'minutos_totales', 'porcentaje_del_total']]
    
    # Crear gráfico de pastel
    fig = px.pie(
        df_pastel,
        values='porcentaje_del_total',
        names='jugador',
        title='Distribución de Minutos Jugados',
        hover_data=['minutos_totales'],
        color_discrete_sequence=px.colors.sequential.Oranges[::-1]  # Paleta de naranjas invertida
    )
    
    # Personalizar el gráfico
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Minutos: %{customdata[0]}<br>Porcentaje: %{percent}<extra></extra>'
    )
    
    # Mostrar el gráfico
    st.plotly_chart(fig, use_container_width=True)

def graficar_distribucion_sustituciones(sustituciones_df):
    """
    Crea un histograma con la distribución de sustituciones por minuto de juego
    
    Args:
        sustituciones_df: DataFrame con sustituciones agrupadas por rango de minutos
    """
    if sustituciones_df.empty:
        st.warning("No hay datos de sustituciones")
        return
    
    # Crear gráfico de barras
    fig = px.bar(
        sustituciones_df,
        x='rango',
        y='cantidad',
        title='Distribución de Sustituciones por Minuto',
        labels={'rango': 'Minuto', 'cantidad': 'Número de Sustituciones'},
        color_discrete_sequence=[PENYA_SECONDARY_COLOR]
    )
    
    # Personalizar el gráfico
    fig.update_layout(
        xaxis_title='Rango de Minutos',
        yaxis_title='Número de Sustituciones',
        showlegend=False
    )
    
    # Personalizar tooltip
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>Sustituciones: %{y}<extra></extra>'
    )
    
    # Mostrar el gráfico
    st.plotly_chart(fig, use_container_width=True)