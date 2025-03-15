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

def graficar_distribucion_sustituciones(sustituciones_data):
    """
    Crea visualizaciones para el análisis de sustituciones
    
    Args:
        sustituciones_data: Diccionario con datos de sustituciones
    """
    if not sustituciones_data:
        st.warning("No hay datos de sustituciones")
        return
    
    # Crear pestañas para las diferentes visualizaciones
    tab1, tab2, tab3 = st.tabs([
        "Distribución por Minuto", 
        "Sustituciones por Jornada",
        "Estadísticas de Sustituciones"
    ])
    
    # Pestaña 1: Distribución por Minuto
    with tab1:
        # Crear gráfico de barras para distribución por minuto
        fig = px.bar(
            sustituciones_data['distribucion_minutos'],
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
    
    # Pestaña 2: Sustituciones por Jornada
    with tab2:
        # Crear gráfico de líneas para sustituciones por jornada
        fig = px.line(
            sustituciones_data['sustituciones_jornada'],
            x='Jornada',
            y='cantidad',
            title='Sustituciones por Jornada',
            labels={'cantidad': 'Número de Sustituciones'},
            markers=True,
            color_discrete_sequence=[PENYA_PRIMARY_COLOR]
        )
        
        # Personalizar el gráfico
        fig.update_layout(
            xaxis_title='Jornada',
            yaxis_title='Número de Sustituciones',
            showlegend=False
        )
        
        # Personalizar tooltip
        fig.update_traces(
            hovertemplate='<b>Jornada %{x}</b><br>Sustituciones: %{y}<extra></extra>'
        )
        
        # Mostrar el gráfico
        st.plotly_chart(fig, use_container_width=True)
        
    # Pestaña 3: Estadísticas de Sustituciones
    with tab3:
        # Crear sub-pestañas para diferentes estadísticas
        subtab1, subtab2, subtab3 = st.tabs([
            "Sustituciones Más Repetidas",
            "Jugadores Más Sustituidos",
            "Minutos desde el Banquillo"
        ])
        
        # Sub-pestaña 1: Sustituciones más repetidas
        with subtab1:
            st.subheader("Top 5 Sustituciones más Repetidas")
            st.dataframe(
                sustituciones_data['top_sustituciones'],
                hide_index=True,
                use_container_width=True
            )
        
        # Sub-pestaña 2: Jugadores más sustituidos
        with subtab2:
            st.subheader("Top 5 Jugadores más Sustituidos")
            st.dataframe(
                sustituciones_data['top_sustituidos'],
                hide_index=True,
                use_container_width=True
            )
        
        # Sub-pestaña 3: Jugadores con más minutos desde el banquillo
        with subtab3:
            st.subheader("Top 5 Jugadores con más Minutos desde el Banquillo")
            st.dataframe(
                sustituciones_data['top_suplentes'],
                hide_index=True,
                use_container_width=True
            )
    
    # Crear una fila para las métricas de sustituciones
    col1, col2, col3, col4 = st.columns(4)
    
    # Minuto medio de sustitución
    with col1:
        st.markdown(
            f"""
            <div style="
                border-radius: 4px;
                border: 1px solid #ddd;
                padding: 10px;
                text-align: center;
                background-color: white;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                height: 100%;
            ">
                <p style="
                    font-size: 0.9rem;
                    margin: 0;
                    color: #333;
                    font-weight: 600;
                ">Minuto Medio por Sustitución</p>
                <p style="
                    font-size: 1.8rem;
                    font-weight: 700;
                    color: {PENYA_PRIMARY_COLOR};
                    margin: 5px 0;
                ">{sustituciones_data['minuto_medio']:.1f}'</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Minuto medio de primera sustitución
    with col2:
        st.markdown(
            f"""
            <div style="
                border-radius: 4px;
                border: 1px solid #ddd;
                padding: 10px;
                text-align: center;
                background-color: white;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                height: 100%;
            ">
                <p style="
                    font-size: 0.9rem;
                    margin: 0;
                    color: #333;
                    font-weight: 600;
                ">Primera Sustitución</p>
                <p style="
                    font-size: 1.8rem;
                    font-weight: 700;
                    color: {PENYA_PRIMARY_COLOR};
                    margin: 5px 0;
                ">{sustituciones_data['primera_sustitucion']:.1f}'</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Minuto medio de última sustitución
    with col3:
        st.markdown(
            f"""
            <div style="
                border-radius: 4px;
                border: 1px solid #ddd;
                padding: 10px;
                text-align: center;
                background-color: white;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                height: 100%;
            ">
                <p style="
                    font-size: 0.9rem;
                    margin: 0;
                    color: #333;
                    font-weight: 600;
                ">Última Sustitución</p>
                <p style="
                    font-size: 1.8rem;
                    font-weight: 700;
                    color: {PENYA_PRIMARY_COLOR};
                    margin: 5px 0;
                ">{sustituciones_data['ultima_sustitucion']:.1f}'</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Número medio de sustituciones
    with col4:
        st.markdown(
            f"""
            <div style="
                border-radius: 4px;
                border: 1px solid #ddd;
                padding: 10px;
                text-align: center;
                background-color: white;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                height: 100%;
            ">
                <p style="
                    font-size: 0.9rem;
                    margin: 0;
                    color: #333;
                    font-weight: 600;
                ">Núm. Medio Sustituciones</p>
                <p style="
                    font-size: 1.8rem;
                    font-weight: 700;
                    color: {PENYA_PRIMARY_COLOR};
                    margin: 5px 0;
                ">{sustituciones_data['num_medio_sustituciones']:.1f}</p>
            </div>
            """,
            unsafe_allow_html=True
        )