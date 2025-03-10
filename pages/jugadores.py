"""
Página de análisis individual de jugadores
"""
import streamlit as st
import pandas as pd

# Importar módulos propios
from utils.data import cargar_datos
from utils.ui import show_sidebar
from calculos.jugadores import calcular_estadisticas_jugador, obtener_minutos_por_jornada
from visualizaciones.jugadores import mostrar_tarjeta_jugador, graficar_minutos_por_jornada

# Cargar datos
data = cargar_datos()

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
    graficar_minutos_por_jornada(minutos_jornada)
    
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
