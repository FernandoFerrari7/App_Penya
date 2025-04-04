"""
Visualizaciones específicas para el análisis individual de jugadores
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from utils.constants import PENYA_PRIMARY_COLOR, PENYA_SECONDARY_COLOR, COLOR_TARJETAS_AMARILLAS, COLOR_TARJETAS_ROJAS

def graficar_minutos_por_jornada(minutos_df, return_fig=False):
    """
    Crea un gráfico de minutos jugados por jornada para un jugador
    """
    if minutos_df.empty:
        if not return_fig:
            st.warning("No hay datos de minutos jugados")
        return None

    # Crear gráfico con Plotly
    fig = px.bar(
        minutos_df,
        x='jornada',
        y='minutos_jugados',
        color='es_titular',
        labels={
            'jornada': 'Jornada',
            'minutos_jugados': 'Minutos',
            'es_titular': 'Condición'
        },
        color_discrete_map={True: PENYA_PRIMARY_COLOR, False: PENYA_SECONDARY_COLOR},
        hover_data=['rival']
    )

    # Personalizar el gráfico
    fig.update_layout(
        xaxis_title='Jornada',
        yaxis_title='Minutos',
        yaxis_range=[0, 100],
        legend_title="Condición",
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )

    # Actualizar las etiquetas de la leyenda
    fig.for_each_trace(lambda t: t.update(name='Titular' if t.name == 'True' else 'Suplente'))

    if return_fig:
        return fig
    else:
        st.plotly_chart(fig, use_container_width=True)

def graficar_goles_por_tiempo(goles_df, return_fig=False):
    """
    Crea un gráfico de goles por tiempo para un jugador
    """
    if goles_df.empty:
        if not return_fig:
            st.warning("No hay datos de goles")
        return None

    # Crear gráfico de barras
    fig = px.bar(
        goles_df,
        x='rango_tiempo',
        y='goles',
        labels={
            'rango_tiempo': 'Minuto',
            'goles': 'Goles'
        },
        color_discrete_sequence=[PENYA_PRIMARY_COLOR]
    )

    # Personalizar el gráfico
    fig.update_layout(
        xaxis_title='Minuto del Partido',
        yaxis_title='Goles',
        showlegend=False
    )

    if return_fig:
        return fig
    else:
        st.plotly_chart(fig, use_container_width=True)

def graficar_tarjetas_por_jornada(tarjetas_df, return_fig=False):
    """
    Crea un gráfico de tarjetas por jornada para un jugador
    """
    if tarjetas_df.empty:
        if not return_fig:
            st.warning("No hay datos de tarjetas")
        return None

    # Crear gráfico de barras
    fig = px.bar(
        tarjetas_df,
        x='Jornada',
        y=[1] * len(tarjetas_df),  # Una tarjeta por registro
        color='Tipo',
        labels={
            'Jornada': 'Jornada',
            'y': 'Tarjetas',
            'Tipo': 'Tipo de Tarjeta'
        },
        color_discrete_map={
            'Amarilla': COLOR_TARJETAS_AMARILLAS,
            'Roja': COLOR_TARJETAS_ROJAS
        }
    )

    # Personalizar el gráfico
    fig.update_layout(
        xaxis_title='Jornada',
        yaxis_title='Tarjetas',
        showlegend=True,
        legend_title="Tipo de Tarjeta",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    if return_fig:
        return fig
    else:
        st.plotly_chart(fig, use_container_width=True)
