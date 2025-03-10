"""
Página de análisis de equipos y partidos
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Importar módulos propios
from utils.data import cargar_datos
from utils.ui import show_sidebar
from calculos.equipo import obtener_rivales_con_goles, analizar_tarjetas_por_jornada, analizar_tipos_goles
from calculos.jugadores import analizar_goles_por_tiempo
from visualizaciones.equipo import graficar_tarjetas_por_jornada, graficar_tipos_goles, graficar_goles_por_tiempo

# Cargar datos
data = cargar_datos()

def main():
    """Función principal que muestra el análisis de equipos"""
    
    # Título principal
    st.title("Análisis de Equipo")
    
    # Mostrar barra lateral
    show_sidebar()
    
    # Sección con las visualizaciones de goles y tarjetas en dos columnas
    # Crear dos columnas para separar goles y tarjetas
    col_goles, col_tarjetas = st.columns(2)
    
    with col_goles:
        # Usar pestañas para elegir entre visualizaciones de goles
        tab_minutos, tab_tipos = st.tabs(["Goles por Minuto", "Tipos de Goles"])
        
        with tab_minutos:
            # Distribución de goles por minuto
            goles_tiempo = analizar_goles_por_tiempo(data['goles_penya'])
            graficar_goles_por_tiempo(goles_tiempo)
        
        with tab_tipos:
            # Tipos de goles
            tipos_goles = analizar_tipos_goles(data['goles_penya'])
            graficar_tipos_goles(tipos_goles)
    
    with col_tarjetas:
        # Análisis de tarjetas por jornada
        tarjetas_jornada = analizar_tarjetas_por_jornada(data['actas_penya'])
        graficar_tarjetas_por_jornada(tarjetas_jornada)
    
    # Separador
    st.markdown("---")
    
    # Mostrar tabla de partidos
    st.header("Calendario de Partidos")
    
    # Preparar tabla de partidos
    partidos = data['partidos_penya'].copy()
    
    # Determinar si Penya Independent jugó como local o visitante
    partidos['es_local'] = partidos['equipo_local'].str.contains('PENYA INDEPENDENT', na=False)
    
    # Crear columna con el rival
    partidos['rival'] = np.where(
        partidos['es_local'],
        partidos['equipo_visitante'],
        partidos['equipo_local']
    )
    
    # Formatear tabla para mostrar
    tabla_partidos = partidos[['jornada', 'equipo_local', 'equipo_visitante', 'rival', 'es_local']]
    tabla_partidos['Condición'] = tabla_partidos['es_local'].map({True: 'Local', False: 'Visitante'})
    tabla_partidos = tabla_partidos.rename(columns={
        'jornada': 'Jornada',
        'equipo_local': 'Local',
        'equipo_visitante': 'Visitante',
        'rival': 'Rival'
    })
    
    # Mostrar tabla
    st.dataframe(
        tabla_partidos[['Jornada', 'Local', 'Visitante', 'Condición']],
        hide_index=True
    )
    
    # Análisis de rendimiento por rival
    st.header("Rendimiento contra Rivales")
    
    # Goles contra rivales
    goles_por_rival = obtener_rivales_con_goles(data['actas_penya'], data['goles_penya'])
    
    # Crear gráfico
    if not goles_por_rival.empty:
        fig = px.bar(
            goles_por_rival,
            x='rival',
            y='goles',
            title='Goles Marcados por Rival',
            labels={'rival': 'Equipo Rival', 'goles': 'Goles'},
            color='goles',
            color_continuous_scale='Greens'
        )
        
        # Personalizar el gráfico
        fig.update_layout(
            xaxis_title='Rival',
            yaxis_title='Goles',
            xaxis={'categoryorder': 'total descending'},
            showlegend=False
        )
        
        # Mostrar el gráfico
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No hay datos disponibles para este análisis")
    
    # Análisis de rendimiento como local vs visitante
    st.header("Rendimiento Local vs Visitante")
    
    # Crear tablas para cada jornada con el rol (local/visitante)
    jornadas_local = partidos[partidos['es_local']]['jornada'].tolist()
    jornadas_visitante = partidos[~partidos['es_local']]['jornada'].tolist()
    
    # Contar goles como local y visitante
    goles_local = data['goles_penya'][data['goles_penya']['Jornada'].isin(jornadas_local)].shape[0]
    goles_visitante = data['goles_penya'][data['goles_penya']['Jornada'].isin(jornadas_visitante)].shape[0]
    
    # Contar tarjetas como local y visitante
    tarjetas_local_amarillas = data['actas_penya'][data['actas_penya']['jornada'].isin(jornadas_local)]['Tarjetas Amarillas'].sum()
    tarjetas_local_rojas = data['actas_penya'][data['actas_penya']['jornada'].isin(jornadas_local)]['Tarjetas Rojas'].sum()
    
    tarjetas_visitante_amarillas = data['actas_penya'][data['actas_penya']['jornada'].isin(jornadas_visitante)]['Tarjetas Amarillas'].sum()
    tarjetas_visitante_rojas = data['actas_penya'][data['actas_penya']['jornada'].isin(jornadas_visitante)]['Tarjetas Rojas'].sum()
    
    # Crear DataFrame para comparativa
    comparativa = pd.DataFrame({
        'Métrica': ['Partidos', 'Goles', 'Tarjetas Amarillas', 'Tarjetas Rojas'],
        'Local': [len(jornadas_local), goles_local, int(tarjetas_local_amarillas), int(tarjetas_local_rojas)],
        'Visitante': [len(jornadas_visitante), goles_visitante, int(tarjetas_visitante_amarillas), int(tarjetas_visitante_rojas)]
    })
    
    # Mostrar tabla comparativa
    st.dataframe(comparativa, hide_index=True)
    
    # Gráfico de comparación
    comparativa_melt = pd.melt(
        comparativa, 
        id_vars=['Métrica'], 
        value_vars=['Local', 'Visitante'],
        var_name='Condición', 
        value_name='Valor'
    )
    
    # Filtrar solo para goles y tarjetas
    comparativa_filtrada = comparativa_melt[comparativa_melt['Métrica'] != 'Partidos']
    
    # Crear gráfico de barras agrupadas
    fig = px.bar(
        comparativa_filtrada,
        x='Métrica',
        y='Valor',
        color='Condición',
        barmode='group',
        title='Comparativa Local vs Visitante',
        labels={'Valor': 'Cantidad', 'Métrica': ''},
        color_discrete_map={'Local': '#36A2EB', 'Visitante': '#FF6384'}
    )
    
    # Mostrar gráfico
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
