"""
Página de análisis individual de jugadores
"""
import streamlit as st
import pandas as pd

# Importar módulos propios
from utils.data import cargar_datos
from utils.ui import show_sidebar
from calculos.jugadores import calcular_estadisticas_jugador, obtener_minutos_por_jornada
from utils.constants import PENYA_PRIMARY_COLOR, PENYA_SECONDARY_COLOR

# Cargar datos
data = cargar_datos()

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

def main():
    """Función principal que muestra el análisis de jugadores"""
    
    # Título principal
    st.title("Análisis Individual de Jugadores")
    st.markdown("Selecciona un jugador para ver sus estadísticas detalladas")
    
    # Mostrar barra lateral
    show_sidebar()
    
    # Obtener lista de jugadores de Penya Independent
    jugadores = data['actas_penya']['jugador'].unique()
    jugadores = sorted(jugadores)
    
    # Selector de jugador
    jugador_seleccionado = st.selectbox(
        "Selecciona un jugador",
        jugadores
    )
    
    # Calcular estadísticas del jugador seleccionado
    estadisticas = calcular_estadisticas_jugador(data['actas_penya'], jugador_seleccionado)
    
    # Mostrar tarjeta de jugador
    mostrar_tarjeta_jugador(estadisticas)
    
    # Espacio para separar secciones
    st.markdown("---")
    
    # Análisis de minutos por jornada
    st.header("Minutos por Jornada")
    minutos_jornada = obtener_minutos_por_jornada(data['actas_penya'], jugador_seleccionado)
    
    # Crear gráfico de barras para minutos por jornada
    if not minutos_jornada.empty:
        # Crear gráfico con Plotly
        import plotly.express as px
        
        fig = px.bar(
            minutos_jornada, 
            x='jornada', 
            y='minutos_jugados',
            color='es_titular',
            labels={'jornada': 'Jornada', 'minutos_jugados': 'Minutos Jugados', 'es_titular': 'Titular'},
            title='Minutos Jugados por Jornada',
            color_discrete_map={True: PENYA_PRIMARY_COLOR, False: '#666666'},
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
    else:
        st.warning("No hay datos de minutos para este jugador")
    
    # Mostrar tabla de participación por partido
    st.header("Detalle por Partido")
    
    # Preparar tabla con datos relevantes
    if not minutos_jornada.empty:
        tabla_partidos = minutos_jornada.copy()
        tabla_partidos['Condición'] = tabla_partidos['es_titular'].map({True: 'Titular', False: 'Suplente'})
        tabla_partidos = tabla_partidos[['jornada', 'rival', 'Condición', 'minutos_jugados']]
        tabla_partidos = tabla_partidos.rename(columns={
            'jornada': 'Jornada',
            'rival': 'Rival',
            'minutos_jugados': 'Minutos'
        })
        
        # Mostrar tabla
        st.dataframe(tabla_partidos, hide_index=True)
    else:
        st.warning("No hay datos de partidos para este jugador")
    
    # Análisis de goles (si los hay)
    if estadisticas and estadisticas['goles'] > 0:
        st.header("Goles Marcados")
        
        # Filtrar goles del jugador
        goles_jugador = data['goles_penya'][data['goles_penya']['jugador'] == jugador_seleccionado].copy()
        
        # Añadir información de rivales
        jugador_actas = data['actas_penya'][data['actas_penya']['jugador'] == jugador_seleccionado]
        jornada_rival = dict(zip(jugador_actas['jornada'], jugador_actas['rival']))
        goles_jugador['Rival'] = goles_jugador['Jornada'].map(jornada_rival)
        
        # Mostrar tabla de goles
        goles_tabla = goles_jugador[['Jornada', 'Minuto', 'Tipo de Gol', 'Rival']]
        goles_tabla = goles_tabla.sort_values('Jornada')
        
        st.dataframe(goles_tabla, hide_index=True)

if __name__ == "__main__":
    main()
