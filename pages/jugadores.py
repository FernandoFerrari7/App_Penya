"""
Página de análisis individual de jugadores
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Importar módulos propios
from utils.data import cargar_datos
from utils.ui import page_config  # Solo importar page_config, no show_sidebar
from calculos.calculo_jugadores import calcular_estadisticas_jugador, ajustar_tarjetas_por_doble_amarilla, analizar_goles_por_tiempo
from utils.constants import PENYA_PRIMARY_COLOR, PENYA_SECONDARY_COLOR, COLOR_TARJETAS_AMARILLAS, COLOR_TARJETAS_ROJAS
from utils.pdf_export import show_download_button
from visualizaciones.jugadores import graficar_minutos_por_jornada, graficar_goles_por_tiempo
from calculos.calculo_minutos import obtener_minutos_por_jornada

# Configurar la página
page_config()

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
    
    # Eliminada la llamada a show_sidebar
    
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
                    # Aplicar ajuste de tarjetas
                    actas_ajustadas = ajustar_tarjetas_por_doble_amarilla(data['actas_penya'])
                    
                    # Filtrar las actas del jugador
                    actas_jugador = actas_ajustadas[actas_ajustadas['jugador'] == jugador_seleccionado].copy()
                    
                    # Crear una lista para almacenar las tarjetas
                    tarjetas_temp = []
                    
                    # Procesar tarjetas amarillas (después del ajuste)
                    for _, row in actas_jugador[actas_jugador['Tarjetas Amarillas'] > 0].iterrows():
                        tarjetas_temp.append({
                            'Jornada': row['jornada'],
                            'Tipo': 'Amarilla',
                            'Rival': row['rival'],
                            'Doble Amarilla': '-'
                        })
                    
                    # Procesar tarjetas rojas
                    for _, row in actas_jugador[actas_jugador['Tarjetas Rojas'] > 0].iterrows():
                        # Verificar si es una tarjeta roja directa o por doble amarilla
                        jornada = row['jornada']
                        
                        # Comprobar si esta roja proviene de una doble amarilla
                        # Verificamos comparando con las actas originales
                        actas_original = data['actas_penya'][
                            (data['actas_penya']['jugador'] == jugador_seleccionado) & 
                            (data['actas_penya']['jornada'] == jornada)
                        ]
                        
                        amarillas_originales = actas_original['Tarjetas Amarillas'].sum()
                        rojas_originales = actas_original['Tarjetas Rojas'].sum()
                        
                        # Si en las actas originales hay 2+ amarillas y en las ajustadas hay menos,
                        # es una roja por doble amarilla
                        es_por_doble_amarilla = amarillas_originales >= 2 and row['Tarjetas Amarillas'] < amarillas_originales
                        
                        # Añadir tarjetas rojas a la lista
                        for i in range(int(row['Tarjetas Rojas'])):
                            # Si es la primera roja y proviene de doble amarilla
                            if i == 0 and es_por_doble_amarilla:
                                doble_amarilla = 'Si'
                            else:
                                doble_amarilla = 'No'
                                
                            tarjetas_temp.append({
                                'Jornada': jornada,
                                'Tipo': 'Roja',
                                'Rival': row['rival'],
                                'Doble Amarilla': doble_amarilla
                            })
                    
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

    # Mostrar botón de exportación a PDF
    c1, c2, c3 = st.columns([6, 2, 6])
    with c2:
        # Crear un diccionario con los datos filtrados
        datos_filtrados = {
            'actas_penya': data['actas_penya'],
            'goles_penya': data['goles_penya'],
            'partidos_penya': data['partidos_penya'],
            'actas': data['actas']  # Datos completos necesarios para cálculos
        }
        show_download_button(datos_filtrados, 'jugador', jugador_seleccionado=jugador_seleccionado)

if __name__ == "__main__":
    main()