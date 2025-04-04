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
from utils.constants import PENYA_PRIMARY_COLOR, PENYA_SECONDARY_COLOR, COLOR_TARJETAS_AMARILLAS, COLOR_TARJETAS_ROJAS

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

def graficar_tarjetas_por_jornada(tarjetas_df, return_fig=False):
    """
    Crea un gráfico de tarjetas por jornada
    
    Args:
        tarjetas_df: DataFrame con tarjetas por jornada
        return_fig: Si es True, devuelve la figura en lugar de mostrarla
    """
    if tarjetas_df.empty:
        if not return_fig:
            st.warning("No hay datos de tarjetas por jornada")
        return None
    
    # Crear gráfico de líneas
    fig = go.Figure()
    
    # Añadir línea para tarjetas amarillas
    fig.add_trace(go.Scatter(
        x=tarjetas_df['jornada'],
        y=tarjetas_df['Tarjetas Amarillas'],
        name='Amarillas',
        line=dict(color='#FFD700', width=2),
        mode='lines+markers'
    ))
    
    # Añadir línea para tarjetas rojas
    fig.add_trace(go.Scatter(
        x=tarjetas_df['jornada'],
        y=tarjetas_df['Tarjetas Rojas'],
        name='Rojas',
        line=dict(color='#FF4136', width=2),
        mode='lines+markers'
    ))
    
    # Personalizar el diseño
    fig.update_layout(
        xaxis_title='Jornada',
        yaxis_title='Número de Tarjetas',
        margin=dict(l=10, r=10, t=10, b=10),  # Márgenes más pequeños para PDF
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
        hovertemplate='<b>Jornada %{x}</b><br>Tarjetas: %{y}<extra></extra>'
    )
    
    if return_fig:
        return fig
        
    # Mostrar el gráfico
    st.plotly_chart(fig, use_container_width=True)

def graficar_goles_por_tiempo(goles_por_tiempo, return_fig=False):
    """
    Crea un gráfico de distribución de goles por minuto
    
    Args:
        goles_por_tiempo: Series con distribución de goles por rango de minutos
        return_fig: Si es True, devuelve la figura en lugar de mostrarla
    """
    if goles_por_tiempo.empty:
        if not return_fig:
            st.warning("No hay datos de goles por tiempo")
        return None
    
    # Convertir a DataFrame para usar con Plotly
    df = goles_por_tiempo.reset_index()
    df.columns = ['Rango', 'Goles']
    
    # Crear gráfico de barras
    fig = px.bar(
        df,
        x='Rango',
        y='Goles',
        color_discrete_sequence=[PENYA_PRIMARY_COLOR]  # Color naranja del Penya
    )
    
    # Personalizar el gráfico
    fig.update_layout(
        xaxis_title='Rango de Minutos',
        yaxis_title='Número de Goles',
        showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10)  # Márgenes más pequeños para PDF
    )
    
    # Personalizar tooltip
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>Goles: %{y}<extra></extra>'
    )
    
    if return_fig:
        return fig
        
    # Mostrar el gráfico
    st.plotly_chart(fig, use_container_width=True)

def graficar_tipos_goles(tipos_goles, return_fig=False):
    """
    Crea un gráfico de tipos de goles marcados
    
    Args:
        tipos_goles: Series con conteo de tipos de goles
        return_fig: Si es True, devuelve la figura en lugar de mostrarla
    """
    if tipos_goles.empty:
        if not return_fig:
            st.warning("No hay datos de tipos de goles")
        return None
    
    # Convertir a DataFrame para usar con Plotly
    df = tipos_goles.reset_index()
    df.columns = ['Tipo', 'Cantidad']
    
    # Crear gráfico de pastel con colores del Penya
    fig = px.pie(
        df,
        values='Cantidad',
        names='Tipo',
        color_discrete_sequence=[PENYA_PRIMARY_COLOR, PENYA_SECONDARY_COLOR, "#555555", "#777777"]
    )
    
    # Personalizar el gráfico
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hole=0.4,
        hovertemplate='<b>%{label}</b><br>Cantidad: %{value}<br>(%{percent})<extra></extra>'
    )
    
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),  # Márgenes más pequeños para PDF
        showlegend=False
    )
    
    if return_fig:
        return fig
        
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
        color_discrete_sequence=[PENYA_PRIMARY_COLOR]  # Color naranja del Penya
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

def graficar_calendario_partidos(partidos_df, goles_favor_dict, primary_color, secondary_color):
    """
    Crea un gráfico tipo timeline para visualizar el calendario de partidos y goles marcados.
    
    Args:
        partidos_df: DataFrame con los partidos jugados
        goles_favor_dict: Diccionario con los goles a favor por jornada
        primary_color: Color primario para equipos locales
        secondary_color: Color secundario para equipos visitantes
    """
    # Preparar datos para la visualización
    calendario_data = []
    for _, partido in partidos_df.iterrows():
        goles = goles_favor_dict.get(partido['jornada'], 0)
        calendario_data.append({
            'jornada': partido['jornada'],
            'rival': partido['rival'],
            'condicion': 'Local' if partido['es_local'] else 'Visitante',
            'goles_favor': goles,
            'color': primary_color if partido['es_local'] else secondary_color
        })
    
    calendario_df = pd.DataFrame(calendario_data)
    calendario_df = calendario_df.sort_values('jornada')
    
    # Crear visualización tipo timeline
    fig = go.Figure()
    
    # Añadir barras horizontales para cada partido
    for i, row in calendario_df.iterrows():
        fig.add_trace(go.Bar(
            y=[row['jornada']],
            x=[row['goles_favor']],
            name=f"{row['rival']} ({row['condicion']})",
            orientation='h',
            marker=dict(
                color=row['color'],
                line=dict(color='rgba(0,0,0,0.5)', width=1)
            ),
            text=f"{row['rival']} - {row['goles_favor']} goles",
            textposition='auto',
            hoverinfo='text',
            hovertext=f"Jornada {row['jornada']}<br>{row['condicion']} vs {row['rival']}<br>Goles a favor: {row['goles_favor']}",
            showlegend=False
        ))
    
    # Añadir etiquetas de rivales
    for i, row in calendario_df.iterrows():
        fig.add_annotation(
            x=row['goles_favor'] + 0.2,
            y=row['jornada'],
            text=f"{row['rival']} ({row['condicion'][0]})",
            showarrow=False,
            font=dict(
                size=10,
                color="black"
            ),
            xanchor="left"
        )
    
    # Añadir iconos de local/visitante
    for i, row in calendario_df.iterrows():
        fig.add_shape(
            type="circle",
            xref="x", yref="y",
            x0=row['goles_favor'] - 0.2,
            y0=row['jornada'] - 0.3,
            x1=row['goles_favor'] + 0.2,
            y1=row['jornada'] + 0.3,
            fillcolor=row['color'],
            line_color="rgba(0,0,0,0.5)",
        )
    
    # Personalizar el gráfico
    max_goles = max(calendario_df['goles_favor']) if not calendario_df.empty and max(calendario_df['goles_favor']) > 0 else 1
    
    fig.update_layout(
        title="Calendario de Partidos y Goles",
        xaxis_title="Goles a favor",
        yaxis_title="Jornada",
        yaxis=dict(
            autorange="reversed",
            tickmode="array",
            tickvals=calendario_df['jornada'].tolist(),
            ticktext=[f"J{j}" for j in calendario_df['jornada'].tolist()]
        ),
        xaxis=dict(
            range=[0, max_goles + 4]
        ),
        height=600,
        margin=dict(l=10, r=150, t=50, b=50),
        barmode='group',
        bargap=0.15,
        plot_bgcolor='rgba(240,240,240,0.3)'
    )
    
    # Mostrar el gráfico
    st.plotly_chart(fig, use_container_width=True)
    
    # Mostrar también la tabla como referencia
    with st.expander("Ver tabla de partidos"):
        tabla_partidos = calendario_df.rename(columns={
            'jornada': 'Jornada',
            'rival': 'Rival',
            'condicion': 'Condición',
            'goles_favor': 'Goles a Favor'
        })[['Jornada', 'Rival', 'Condición', 'Goles a Favor']]
        
        st.dataframe(
            tabla_partidos,
            hide_index=True,
            use_container_width=True
        )

def graficar_rendimiento_rivales(partidos_df, goles_df, primary_color):
    """
    Crea gráficos para visualizar el rendimiento contra rivales.
    
    Args:
        partidos_df: DataFrame con los partidos jugados
        goles_df: DataFrame con los goles marcados
        primary_color: Color primario para los gráficos
    """
    # Obtener los rivales de cada jornada
    rivales_jornada = partidos_df.set_index('jornada')['rival'].to_dict()
    
    # Contar goles por jornada para obtener goles a favor
    goles_jornada = goles_df.groupby('Jornada').size().to_dict()
    
    # Crear un DataFrame para almacenar goles por rival
    goles_por_rival = []
    for jornada, rival in rivales_jornada.items():
        if jornada in goles_jornada:
            goles_por_rival.append({
                'rival': rival,
                'jornada': jornada,
                'goles': goles_jornada[jornada]
            })
    
    goles_rival_df = pd.DataFrame(goles_por_rival)
    
    # Agrupar por rival y sumar goles
    if not goles_rival_df.empty:
        goles_por_rival_agrupado = goles_rival_df.groupby('rival')['goles'].sum().reset_index()
        
        # Ordenar por nombre del rival
        goles_por_rival_agrupado = goles_por_rival_agrupado.sort_values('rival')
        
        # Crear gráfico
        fig = px.bar(
            goles_por_rival_agrupado,
            x='rival',
            y='goles',
            title='Goles Marcados por Rival',
            labels={'rival': 'Equipo Rival', 'goles': 'Goles'},
            color_discrete_sequence=[primary_color]
        )
        
        # Personalizar el gráfico
        fig.update_layout(
            xaxis_title='Rival',
            yaxis_title='Goles',
            xaxis={'categoryorder': 'total descending'},
            showlegend=False
        )
        
        # Personalizar tooltip
        fig.update_traces(
            hovertemplate='<b>%{x}</b><br>Goles: %{y}<extra></extra>'
        )
        
        # Mostrar el gráfico
        st.plotly_chart(fig, use_container_width=True)
        
        # Crear una visualización de tendencia de goles por jornada
        st.subheader("Tendencia de Goles por Jornada")
        
        # Ordenar por jornada
        goles_tendencia = goles_rival_df.sort_values('jornada')
        
        # Crear gráfico de línea
        fig_tendencia = px.line(
            goles_tendencia,
            x='jornada',
            y='goles',
            markers=True,
            title='Tendencia de Goles Marcados por Jornada',
            labels={'jornada': 'Jornada', 'goles': 'Goles Marcados'},
            hover_data=['rival']
        )
        
        # Personalizar el gráfico
        fig_tendencia.update_traces(
            line_color=primary_color,
            marker=dict(size=8, color=primary_color)
        )
        
        fig_tendencia.update_layout(
            xaxis_title='Jornada',
            yaxis_title='Goles',
            hovermode='x unified'
        )
        
        # Mostrar el gráfico
        st.plotly_chart(fig_tendencia, use_container_width=True)
    else:
        st.warning("No hay datos disponibles para este análisis")