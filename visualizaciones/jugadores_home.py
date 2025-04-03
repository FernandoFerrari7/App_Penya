"""
Visualizaciones relacionadas con estadísticas de jugadores - Versión para Home
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
from utils.constants import PENYA_PRIMARY_COLOR, PENYA_SECONDARY_COLOR, COLOR_TARJETAS_AMARILLAS, COLOR_TARJETAS_ROJAS

def graficar_top_goleadores_home(goleadores_df, top_n=5, return_fig=False):
    """
    Versión especial para la página Home que muestra Top 5
    
    Args:
        goleadores_df: DataFrame con goleadores
        top_n: Número de jugadores a mostrar
        return_fig: Si es True, retorna la figura en lugar de mostrarla
    """
    if goleadores_df.empty:
        st.warning("No hay datos de goleadores")
        return None
    
    # Limitar a los top_n jugadores y ordenar de mayor a menor
    df = goleadores_df.head(top_n).sort_values('goles', ascending=True).copy()
    
    if return_fig:
        # Crear gráfico con matplotlib para PDF
        fig, ax = plt.subplots(figsize=(8, 4))
        bars = ax.barh(df['jugador'], df['goles'], color=PENYA_PRIMARY_COLOR)
        ax.set_title('Top Goleadores', fontsize=12, pad=10)
        ax.set_xlabel('Goles', fontsize=10)
        
        # Ajustar tamaño de las etiquetas
        ax.tick_params(axis='both', which='major', labelsize=10)
        
        # Añadir valores en las barras
        for i, v in enumerate(df['goles']):
            ax.text(v, i, str(v), va='center', fontsize=10)
        
        # Ajustar márgenes
        plt.tight_layout()
        return fig
    else:
        # Crear gráfico de barras horizontales con plotly para web
        fig = px.bar(
            df,
            y='jugador',
            x='goles',
            orientation='h',
            title=f'Top {top_n} Goleadores',
            labels={'jugador': 'Jugador', 'goles': 'Goles'},
            color_discrete_sequence=[PENYA_PRIMARY_COLOR]
        )
        
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            xaxis_title='Goles',
            yaxis_title='',
            showlegend=False
        )
        
        fig.update_traces(
            hovertemplate='Goles: %{x}<extra></extra>'
        )
        
        st.plotly_chart(fig, use_container_width=True)

def graficar_top_amonestados_home(amonestados_df, top_n=5, return_fig=False):
    """
    Versión especial para la página Home que muestra Top 5
    
    Args:
        amonestados_df: DataFrame con jugadores amonestados
        top_n: Número de jugadores a mostrar
        return_fig: Si es True, retorna la figura en lugar de mostrarla
    """
    if amonestados_df.empty:
        st.warning("No hay datos de amonestaciones")
        return None
    
    # Limitar a los top_n jugadores y ordenar por total de tarjetas de mayor a menor
    df = amonestados_df.head(top_n).copy()
    df['total_tarjetas'] = df['Tarjetas Amarillas'] + df['Tarjetas Rojas']
    df = df.sort_values('total_tarjetas', ascending=True)
    
    if return_fig:
        # Crear gráfico con matplotlib para PDF
        fig, ax = plt.subplots(figsize=(8, 4))
        
        # Crear barras apiladas horizontalmente
        ax.barh(df['jugador'], df['Tarjetas Amarillas'], 
                color=COLOR_TARJETAS_AMARILLAS, label='Amarillas')
        ax.barh(df['jugador'], df['Tarjetas Rojas'], 
                left=df['Tarjetas Amarillas'], 
                color=COLOR_TARJETAS_ROJAS, label='Rojas')
        
        ax.set_title('Top Tarjetas', fontsize=12, pad=10)
        ax.set_xlabel('Tarjetas', fontsize=10)
        
        # Ajustar tamaño de las etiquetas
        ax.tick_params(axis='both', which='major', labelsize=10)
        
        # Añadir valores en las barras
        for i, (amarillas, rojas) in enumerate(zip(df['Tarjetas Amarillas'], df['Tarjetas Rojas'])):
            # Texto para tarjetas amarillas
            if amarillas > 0:
                ax.text(amarillas/2, i, str(int(amarillas)), va='center', ha='center', color='black', fontsize=10)
            # Texto para tarjetas rojas
            if rojas > 0:
                ax.text(amarillas + rojas/2, i, str(int(rojas)), va='center', ha='center', color='white', fontsize=10)
        
        # Ajustar la leyenda
        ax.legend(fontsize=10, loc='lower right')
        
        # Ajustar márgenes
        plt.tight_layout()
        return fig
    else:
        # Crear gráfico de barras apiladas con plotly para web
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=df['jugador'],
            x=df['Tarjetas Amarillas'],
            name='Amarillas',
            orientation='h',
            marker=dict(color=COLOR_TARJETAS_AMARILLAS)
        ))
        
        fig.add_trace(go.Bar(
            y=df['jugador'],
            x=df['Tarjetas Rojas'],
            name='Rojas',
            orientation='h',
            marker=dict(color=COLOR_TARJETAS_ROJAS)
        ))
        
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
        
        fig.update_traces(
            hovertemplate='Tarjetas: %{x}<extra></extra>'
        )
        
        st.plotly_chart(fig, use_container_width=True)

def graficar_minutos_jugados_home(minutos_df, top_n=5, return_fig=False):
    """
    Versión especial para la página Home que muestra Top 5
    
    Args:
        minutos_df: DataFrame con minutos por jugador
        top_n: Número de jugadores a mostrar
        return_fig: Si es True, retorna la figura en lugar de mostrarla
    """
    if minutos_df.empty:
        st.warning("No hay datos de minutos jugados")
        return None
    
    # Limitar a los top_n jugadores y ordenar de mayor a menor
    df = minutos_df.head(top_n).sort_values('minutos_jugados', ascending=True).copy()
    
    if return_fig:
        # Crear gráfico con matplotlib para PDF
        fig, ax = plt.subplots(figsize=(8, 4))
        bars = ax.barh(df['jugador'], df['minutos_jugados'], color='black')
        ax.set_title('Top Minutos Jugados', fontsize=12, pad=10)
        ax.set_xlabel('Minutos', fontsize=10)
        
        # Ajustar tamaño de las etiquetas
        ax.tick_params(axis='both', which='major', labelsize=10)
        
        # Añadir valores en las barras
        for i, v in enumerate(df['minutos_jugados']):
            ax.text(v, i, str(v), va='center', fontsize=10)
        
        # Ajustar márgenes
        plt.tight_layout()
        return fig
    else:
        # Crear gráfico de barras horizontales con plotly para web
        fig = px.bar(
            df,
            y='jugador',
            x='minutos_jugados',
            orientation='h',
            title=f'Top {top_n} Jugadores con Más Minutos',
            labels={'jugador': 'Jugador', 'minutos_jugados': 'Minutos Jugados'},
            color_discrete_sequence=["#000000"]
        )
        
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            xaxis_title='Minutos Jugados',
            yaxis_title='',
            showlegend=False
        )
        
        fig.update_traces(
            hovertemplate='Minutos: %{x}<extra></extra>'
        )
        
        st.plotly_chart(fig, use_container_width=True)