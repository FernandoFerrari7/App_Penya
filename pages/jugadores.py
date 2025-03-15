"""
Página de análisis individual de jugadores
"""
import streamlit as st
import pandas as pd

# Importar módulos propios
from utils.data import cargar_datos
from utils.ui import show_sidebar
from calculos.calculo_jugadores import calcular_estadisticas_jugador
from utils.constants import PENYA_PRIMARY_COLOR, PENYA_SECONDARY_COLOR, COLOR_TARJETAS_AMARILLAS, COLOR_TARJETAS_ROJAS

# Cargar datos
data = cargar_datos()

def obtener_minutos_por_jornada(actas_df, jugador_nombre):
    """
    Obtiene los minutos jugados por jornada para un jugador específico
    
    Args:
        actas_df: DataFrame con los datos de actas
        jugador_nombre: Nombre del jugador
        
    Returns:
        DataFrame: DataFrame con los minutos por jornada
    """
    # Filtrar datos del jugador
    datos_jugador = actas_df[actas_df['jugador'] == jugador_nombre]
    
    if datos_jugador.empty:
        return pd.DataFrame()
    
    # Seleccionar columnas relevantes
    minutos_por_jornada = datos_jugador[['jornada', 'minutos_jugados', 'rival', 'status']]
    
    # Agregar columna booleana para titular
    minutos_por_jornada['es_titular'] = minutos_por_jornada['status'] == 'Titular'
    
    # Ordenar por jornada
    minutos_por_jornada = minutos_por_jornada.sort_values('jornada')
    
    return minutos_por_jornada

def mostrar_tarjeta_jugador(estadisticas):
    """
    Muestra la tarjeta de estadísticas de un jugador
    
    Args:
        estadisticas: Diccionario con estadísticas del jugador
    """
    if not estadisticas:
        st.warning("No se encontraron datos para este jugador")
        return
    
    # Calcular métricas adicionales
    minutos_por_gol = estadisticas['minutos_jugados'] / estadisticas['goles'] if estadisticas['goles'] > 0 else float('inf')
    minutos_por_ta = estadisticas['minutos_jugados'] / estadisticas['tarjetas_amarillas'] if estadisticas['tarjetas_amarillas'] > 0 else float('inf')
    minutos_por_tr = estadisticas['minutos_jugados'] / estadisticas['tarjetas_rojas'] if estadisticas['tarjetas_rojas'] > 0 else float('inf')
    
    # Definir las métricas en tarjetas
    metricas = [
        {
            'titulo': 'Minutos Jugados',
            'valor': estadisticas['minutos_jugados'],
            'color': PENYA_PRIMARY_COLOR
        },
        {
            'titulo': 'Titular/Suplente',
            'valor': f"{estadisticas['titularidades']}/{estadisticas['suplencias']}",
            'color': PENYA_SECONDARY_COLOR
        },
        {
            'titulo': 'Goles',
            'valor': estadisticas['goles'],
            'color': PENYA_PRIMARY_COLOR
        },
        {
            'titulo': 'Minutos por Gol',
            'valor': f"{int(minutos_por_gol)}" if minutos_por_gol != float('inf') else "-",
            'color': PENYA_SECONDARY_COLOR
        },
        {
            'titulo': 'Tarjetas Amarillas',
            'valor': estadisticas['tarjetas_amarillas'],
            'color': COLOR_TARJETAS_AMARILLAS
        },
        {
            'titulo': 'Minutos por TA',
            'valor': f"{int(minutos_por_ta)}" if minutos_por_ta != float('inf') else "-",
            'color': PENYA_PRIMARY_COLOR
        },
        {
            'titulo': 'Tarjetas Rojas',
            'valor': estadisticas['tarjetas_rojas'],
            'color': COLOR_TARJETAS_ROJAS
        },
        {
            'titulo': 'Minutos por TR',
            'valor': f"{int(minutos_por_tr)}" if minutos_por_tr != float('inf') else "-",
            'color': PENYA_SECONDARY_COLOR
        }
    ]
    
    # Mostrar tarjetas de métricas en 8 columnas (una al lado de otra)
    cols = st.columns(8)
    
    for i, metrica in enumerate(metricas):
        with cols[i]:
            mostrar_tarjeta_metrica_compacta(
                metrica['titulo'],
                metrica['valor'],
                metrica['color']
            )

def mostrar_tarjeta_metrica_compacta(titulo, valor, color_valor="#FF8C00"):
    """
    Muestra una tarjeta métrica compacta (versión reducida)
    """
    # Aplicar estilos CSS más compactos
    st.markdown(
        f"""
        <div style="
            border-radius: 4px;
            border: 1px solid #ddd;
            padding: 8px 5px;
            margin: 2px 0;
            background-color: white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            text-align: center;
            height: 100%;
        ">
            <div style="
                font-size: 0.85rem;
                margin: 0;
                color: #333;
                font-weight: 600;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            ">{titulo}</div>
            <div style="
                font-size: 1.5rem;
                font-weight: 700;
                color: {color_valor};
                line-height: 1.2;
                margin-top: 4px;
            ">{valor}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def main():
    """Función principal que muestra el análisis de jugadores"""
    
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
    
    # Obtener minutos por jornada para la visualización
    minutos_jornada = obtener_minutos_por_jornada(data['actas_penya'], jugador_seleccionado)
    
    # Crear 2 columnas para visualizaciones
    col_izq, col_der = st.columns(2)
    
    # Columna izquierda: Minutos
    with col_izq:
        st.subheader("Minutos")
        
        if not minutos_jornada.empty:
            # Crear columna "Condición" basada en status
            minutos_jornada['Condición'] = minutos_jornada['es_titular'].map({True: 'Titular', False: 'Suplente'})
            
            # Crear pestañas para los diferentes análisis de minutos
            min_tab1, min_tab2, min_tab3 = st.tabs([
                "Minutos por Jornada",
                "Desglose por participación",
                "Detalle por Partido"
            ])
            
            # Pestaña 1: Minutos por Jornada
            with min_tab1:
                # Crear gráfico con Plotly
                import plotly.express as px
                
                # Hacer una copia del DataFrame para modificar los valores
                minutos_plot = minutos_jornada.copy()
                minutos_plot['condicion'] = minutos_plot['es_titular'].map({True: 'Titular', False: 'Suplente'})
                
                fig = px.bar(
                    minutos_plot, 
                    x='jornada', 
                    y='minutos_jugados',
                    color='condicion',
                    labels={'jornada': 'Jornada', 'minutos_jugados': 'Minutos Jugados', 'condicion': 'Condición'},
                    color_discrete_map={'Titular': PENYA_PRIMARY_COLOR, 'Suplente': PENYA_SECONDARY_COLOR},
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
            
            # Pestaña 2: Desglose por participación
            with min_tab2:
                import plotly.graph_objects as go
                
                # Calcular diferentes tipos de participación
                titular_completo = sum((minutos_jornada['es_titular'] == True) & (minutos_jornada['minutos_jugados'] == 90))
                titular_sustituido = sum((minutos_jornada['es_titular'] == True) & (minutos_jornada['minutos_jugados'] < 90))
                suplente = sum(minutos_jornada['es_titular'] == False)
                
                # Calcular partidos en los que no participó
                partidos_totales = len(data['partidos_penya'])
                partidos_jugados = len(minutos_jornada)
                no_participa = partidos_totales - partidos_jugados
                
                # Crear datos para la tabla/gráfico
                categorias = ['Titular todo el partido', 'Titular Sustituido', 'Participación Suplente', 'No Participa']
                valores = [titular_completo, titular_sustituido, suplente, no_participa]
                
                # Crear gráfico de barras
                fig = go.Figure()
                
                # Añadir barras (alternando naranja y negro)
                fig.add_trace(go.Bar(
                    x=categorias,
                    y=valores,
                    marker_color=[PENYA_PRIMARY_COLOR, PENYA_SECONDARY_COLOR, PENYA_PRIMARY_COLOR, PENYA_SECONDARY_COLOR]
                ))
                
                # Personalizar el gráfico
                fig.update_layout(
                    xaxis_title='Tipo de Participación',
                    yaxis_title='Partidos',
                    yaxis=dict(
                        tickmode='linear',
                        tick0=0,
                        dtick=1
                    )
                )
                
                # Mostrar el gráfico
                st.plotly_chart(fig, use_container_width=True)
            
            # Pestaña 3: Detalle por partido
            with min_tab3:
                # Mostrar directamente la tabla con los datos
                st.write("Detalle de participación por partidos:")
                
                # Hacer una copia y renombrar columnas para mostrar
                tabla_partidos = minutos_jornada[['jornada', 'rival', 'Condición', 'minutos_jugados']].copy()
                tabla_partidos = tabla_partidos.rename(columns={
                    'jornada': 'Jornada',
                    'rival': 'Rival',
                    'minutos_jugados': 'Minutos'
                })
                
                # Mostrar la tabla
                st.table(tabla_partidos)
        else:
            st.warning("No hay datos de minutos para este jugador")
    
    # Columna derecha: Goles y Tarjetas
    with col_der:
        st.subheader("Goles/Tarjetas")
        
        # Crear pestañas para goles y tarjetas
        if estadisticas and (estadisticas['goles'] > 0 or estadisticas['tarjetas_amarillas'] > 0 or estadisticas['tarjetas_rojas'] > 0):
            gt_tab1, gt_tab2 = st.tabs(["Goles", "Tarjetas"])
            
            # Pestaña de Goles
            with gt_tab1:
                if estadisticas['goles'] > 0:
                    # Filtrar goles del jugador
                    goles_jugador = data['goles_penya'][data['goles_penya']['jugador'] == jugador_seleccionado].copy()
                    
                    # Añadir información de rivales
                    jugador_actas = data['actas_penya'][data['actas_penya']['jugador'] == jugador_seleccionado]
                    jornada_rival = dict(zip(jugador_actas['jornada'], jugador_actas['rival']))
                    goles_jugador['Rival'] = goles_jugador['Jornada'].map(jornada_rival)
                    
                    # Mostrar tabla de goles
                    goles_tabla = goles_jugador[['Jornada', 'Minuto', 'Tipo de Gol', 'Rival']]
                    goles_tabla = goles_tabla.sort_values('Jornada')
                    
                    st.dataframe(goles_tabla, hide_index=True, use_container_width=True)
                else:
                    st.info("Este jugador no ha marcado goles en la temporada.")
            
            # Pestaña de Tarjetas
            with gt_tab2:
                if estadisticas['tarjetas_amarillas'] > 0 or estadisticas['tarjetas_rojas'] > 0:
                    # Crear tabla de tarjetas (similar a la de goles)
                    # Primero buscar todas las actas donde el jugador ha recibido tarjetas
                    tarjetas_temp = []
                    seen = set()  # Para registrar las tarjetas ya procesadas
                    
                    for _, row in data['actas_penya'][(data['actas_penya']['jugador'] == jugador_seleccionado) & 
                                                    ((data['actas_penya']['Tarjetas Amarillas'] > 0) | 
                                                      (data['actas_penya']['Tarjetas Rojas'] > 0))].iterrows():
                        # Clave única para identificar tarjetas
                        jornada = row['jornada']
                        rival = row['rival']
                        
                        # Por cada tarjeta amarilla, añadir una fila evitando duplicados
                        if row['Tarjetas Amarillas'] > 0:
                            key = f"{jornada}-{rival}-Amarilla"
                            if key not in seen:
                                tarjetas_temp.append({
                                    'Jornada': jornada,
                                    'Tipo': 'Amarilla',
                                    'Rival': rival
                                })
                                seen.add(key)
                        
                        # Por cada tarjeta roja, añadir una fila evitando duplicados
                        if row['Tarjetas Rojas'] > 0:
                            key = f"{jornada}-{rival}-Roja"
                            if key not in seen:
                                tarjetas_temp.append({
                                    'Jornada': jornada,
                                    'Tipo': 'Roja',
                                    'Rival': rival
                                })
                                seen.add(key)
                    
                    # Crear DataFrame
                    if tarjetas_temp:
                        tarjetas_df = pd.DataFrame(tarjetas_temp)
                        tarjetas_df = tarjetas_df.sort_values('Jornada')
                        
                        # Mostrar tabla
                        st.dataframe(tarjetas_df, hide_index=True, use_container_width=True)
                    else:
                        st.info("No se encontraron datos detallados de las tarjetas.")
                else:
                    st.info("Este jugador no ha recibido tarjetas en la temporada.")
        else:
            st.info("Este jugador no ha marcado goles ni recibido tarjetas en la temporada.")

if __name__ == "__main__":
    main()