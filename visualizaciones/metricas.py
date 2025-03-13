"""
Componentes para mostrar métricas y tarjetas de información
"""
import streamlit as st
from utils.constants import PENYA_PRIMARY_COLOR, PENYA_SECONDARY_COLOR

def tarjeta_metrica(titulo, valor, valor_referencia=None, color_valor="#FF8C00"):
    """
    Muestra una tarjeta métrica con un título, valor principal y opcionalmente un valor de referencia
    
    Args:
        titulo: Título de la métrica
        valor: Valor principal a mostrar
        valor_referencia: Valor de referencia (ej. media de la liga) para mostrar entre paréntesis
        color_valor: Color del valor principal
    """
    # Estilo CSS para la tarjeta (versión más compacta)
    tarjeta_style = f"""
    <style>
    .metric-card {{
        background-color: white;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 0.6rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        height: 100%;
        margin-bottom: 0.5rem;
    }}
    .metric-title {{
        font-size: 0.9rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 0.3rem;
    }}
    .metric-value {{
        font-size: 1.4rem;
        font-weight: 700;
        color: {color_valor};
        line-height: 1.2;
    }}
    .metric-reference {{
        font-size: 0.8rem;
        color: #777;
        font-style: italic;
    }}
    </style>
    """
    
    # HTML para la tarjeta
    valor_text = f'<span class="metric-value">{valor}</span>'
    if valor_referencia is not None:
        valor_text += f'<br><span class="metric-reference">({valor_referencia})</span>'
    
    tarjeta_html = f"""
    <div class="metric-card">
        <div class="metric-title">{titulo}</div>
        {valor_text}
    </div>
    """
    
    # Mostrar la tarjeta
    st.markdown(tarjeta_style + tarjeta_html, unsafe_allow_html=True)

def mostrar_metricas_equipo(metricas, cols_por_fila=4):
    """
    Muestra un conjunto de métricas del equipo en una cuadrícula
    
    Args:
        metricas: Lista de diccionarios con las métricas a mostrar. 
                 Cada métrica es un dict con 'titulo', 'valor', 'referencia' y opcionalmente 'color'
        cols_por_fila: Número de columnas por fila
    """
    # Calcular número de columnas
    num_metricas = len(metricas)
    
    # Mostrar métricas en filas
    cols = st.columns(cols_por_fila)
    for i, metrica in enumerate(metricas):
        with cols[i % cols_por_fila]:
            color = metrica.get('color', PENYA_PRIMARY_COLOR)
            tarjeta_metrica(
                metrica['titulo'], 
                metrica['valor'], 
                metrica.get('referencia'), 
                color
            )

def mostrar_metricas_y_grafico(metricas, grafico_func, *args, **kwargs):
    """
    Muestra métricas junto a un gráfico en un layout de 1:3
    
    Args:
        metricas: Lista de métricas a mostrar
        grafico_func: Función que genera el gráfico
        *args, **kwargs: Argumentos para la función del gráfico
    """
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Mostrar métricas en vertical
        for metrica in metricas:
            color = metrica.get('color', PENYA_PRIMARY_COLOR)
            tarjeta_metrica(
                metrica['titulo'], 
                metrica['valor'], 
                metrica.get('referencia'), 
                color
            )
    
    with col2:
        # Mostrar el gráfico
        grafico_func(*args, **kwargs)