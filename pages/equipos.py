"""
Página de análisis de equipos y partidos
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Importar módulos propios
from utils.data import cargar_datos
from utils.ui import show_sidebar
from calculos.equipo import obtener_rivales_con_goles, analizar_tarjetas_por_jornada, analizar_tipos_goles
from calculos.jugadores import (
    analizar_goles_por_tiempo, 
    analizar_goles_por_jugador, 
    analizar_tarjetas_por_jugador,
    analizar_minutos_por_jugador,
    analizar_distribucion_sustituciones
)
from visualizaciones.equipo import graficar_tarjetas_por_jornada, graficar_tipos_goles, graficar_goles_por_tiempo
from visualizaciones.jugadores import graficar_goles_por_jugador, graficar_tarjetas_por_jugador
from visualizaciones.minutos import (
    graficar_minutos_por_jugador,
    graficar_minutos_por_jugador_desglose,
    graficar_porcentaje_minutos_jugador,
    graficar_distribucion_sustituciones
)
from utils.constants import PENYA_PRIMARY_COLOR, PENYA_SECONDARY_COLOR

# Cargar datos
data = cargar_datos()

def mostrar_tarjeta_metrica_compacta(titulo, valor, valor_referencia=None, color_valor="#FF8C00"):
    """
    Muestra una tarjeta métrica compacta (versión reducida)
    """
    # Determinar color basado en comparación con media
    if valor_referencia is not None:
        if titulo == "Goles a favor" and valor < valor_referencia:
            color_valor = "#FF4136"  # Rojo (por debajo de la media)
        elif titulo == "Goles a favor" and valor >= valor_referencia:
            color_valor = "#4CAF50"  # Verde (por encima de la media)
        elif titulo == "Goles en contra" and valor > valor_referencia:
            color_valor = "#FF4136"  # Rojo (por encima de la media, es malo)
        elif titulo == "Goles en contra" and valor <= valor_referencia:
            color_valor = "#4CAF50"  # Verde (por debajo de la media, es bueno)
    
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
            ">{valor} {f'<span style="font-size: 0.75rem; color: #777; font-weight: normal;">({valor_referencia})</span>' if valor_referencia else ''}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def main():
    """Función principal que muestra el análisis de equipos"""
    
    # Título principal
    st.title("Análisis de Equipo")
    
    # Mostrar barra lateral
    show_sidebar()
    
    # Definir las métricas en el orden solicitado
    metricas = [
        {
            'titulo': 'Partidos Jugados',
            'valor': 19,
            'referencia': None,
            'color': PENYA_SECONDARY_COLOR  # Negro
        },
        {
            'titulo': 'Num. Jugadores',
            'valor': 25,
            'referencia': 27.7,
            'color': PENYA_SECONDARY_COLOR  # Negro
        },
        {
            'titulo': 'Goles a favor',
            'valor': 18,
            'referencia': 28,
            'color': '#FF8C00'  # Se determinará dinámicamente
        },
        {
            'titulo': 'Goles en contra',
            'valor': 32,
            'referencia': 30,  # Media de la liga
            'color': '#FF4136'  # Se determinará dinámicamente
        },
        {
            'titulo': 'Tarjetas Amarillas',
            'valor': 33,
            'referencia': 42,
            'color': '#FFD700'  # Amarillo
        },
        {
            'titulo': 'Tarjetas Amarillas Rival',
            'valor': 40,
            'referencia': 45,  # Media de la liga
            'color': '#FFD700'  # Amarillo
        },
        {
            'titulo': 'Tarjetas Rojas',
            'valor': 2,
            'referencia': 1.6,
            'color': '#FF4136'  # Rojo
        },
        {
            'titulo': 'Tarjetas Rojas Rival',
            'valor': 1,
            'referencia': 1.8,  # Media de la liga
            'color': '#FF4136'  # Rojo
        }
    ]
    
    # Crear una fila para las tarjetas métricas (8 columnas)
    metric_cols = st.columns(8)
    for i, metrica in enumerate(metricas):
        with metric_cols[i]:
            mostrar_tarjeta_metrica_compacta(
                metrica['titulo'],
                metrica['valor'],
                metrica['referencia'],
                metrica['color']
            )
    
    # Crear dos columnas para las visualizaciones
    col_goles, col_tarjetas = st.columns(2)
    
    # Sección de Visualizaciones de Goles
    with col_goles:
        # Tabs para diferentes visualizaciones de goles en el orden solicitado
        gol_tab1, gol_tab2, gol_tab3 = st.tabs([
            "Goles por Jugador",
            "Goles por Minuto", 
            "Tipos de Goles"
        ])
        
        with gol_tab1:
            # Goles por jugador
            goles_jugador = analizar_goles_por_jugador(data['goles_penya'], data['actas_penya'])
            graficar_goles_por_jugador(goles_jugador)
        
        with gol_tab2:
            # Distribución de goles por minuto
            goles_tiempo = analizar_goles_por_tiempo(data['goles_penya'])
            graficar_goles_por_tiempo(goles_tiempo)
        
        with gol_tab3:
            # Tipos de goles
            tipos_goles = analizar_tipos_goles(data['goles_penya'])
            graficar_tipos_goles(tipos_goles)
    
    # Sección de Visualizaciones de Tarjetas
    with col_tarjetas:
        # Tabs para diferentes visualizaciones de tarjetas en el orden solicitado
        tarjeta_tab1, tarjeta_tab2 = st.tabs([
            "Tarjetas por Jugador",
            "Tarjetas por Jornada"
        ])
        
        with tarjeta_tab1:
            # Análisis de tarjetas por jugador (todos los jugadores)
            tarjetas_jugador = analizar_tarjetas_por_jugador(data['actas_penya'])
            graficar_tarjetas_por_jugador(tarjetas_jugador, top_n=None)
        
        with tarjeta_tab2:
            # Análisis de tarjetas por jornada
            tarjetas_jornada = analizar_tarjetas_por_jornada(data['actas_penya'])
            graficar_tarjetas_por_jornada(tarjetas_jornada)
    
    # Separador
    st.markdown("---")
    
    # CAMBIO: Colocar en la misma fila "Análisis de Minutos por Jugador" y "Partidos y Rivales"
    col_minutos, col_partidos = st.columns(2)
    
    # Sección de Análisis de Minutos (ahora en columna izquierda)
    with col_minutos:
        st.subheader("Análisis de Minutos por Jugador")
        
        # Calcular datos de minutos
        minutos_jugador = analizar_minutos_por_jugador(data['actas_penya'])
        
        # Pestañas para los diferentes análisis de minutos (solo dos pestañas)
        minutos_tab1, minutos_tab2 = st.tabs([
            "Local vs Visitante", 
            "Titular vs Suplente"
        ])
        
        with minutos_tab1:
            # Desglose local vs visitante (CAMBIO: usar colores de Penya y mostrar todos los jugadores)
            graficar_minutos_por_jugador_desglose(minutos_jugador, top_n=None, tipo_desglose='local_visitante', 
                                                  color_izquierda=PENYA_PRIMARY_COLOR, color_derecha=PENYA_SECONDARY_COLOR)
        
        with minutos_tab2:
            # Desglose titular vs suplente (CAMBIO: usar colores de Penya y mostrar todos los jugadores)
            graficar_minutos_por_jugador_desglose(minutos_jugador, top_n=None, tipo_desglose='titular_suplente',
                                                  color_izquierda=PENYA_PRIMARY_COLOR, color_derecha=PENYA_SECONDARY_COLOR)
    
    # Sección de Partidos y Rivales (ahora en columna derecha)
    with col_partidos:
        st.subheader("Partidos y Rivales")
        
        # Separar en pestañas
        partido_tab1, partido_tab2, partido_tab3 = st.tabs([
            "Calendario de Partidos", 
            "Rendimiento contra Rivales",
            "Local vs Visitante"
        ])
        
        with partido_tab1:
            # Mostrar tabla de partidos
            partidos = data['partidos_penya'].copy()
            
            # Determinar si Penya Independent jugó como local o visitante
            partidos['es_local'] = partidos['equipo_local'].str.contains('PENYA INDEPENDENT', na=False)
            
            # Crear columna con el rival
            partidos['rival'] = np.where(
                partidos['es_local'],
                partidos['equipo_visitante'],
                partidos['equipo_local']
            )
            
            # Calcular goles a favor por jornada basado en goles_penya
            goles_favor_por_jornada = data['goles_penya'].groupby('Jornada').size().to_dict()
            
            # Calcular goles en contra (necesitamos inferirlo de otra forma)
            # Podemos intentar obtenerlo de las actas agrupando por jornada y sumando los goles del rival
            # Este es un enfoque aproximado que depende de la estructura de los datos
            
            # Agregar goles a favor a la tabla de partidos
            partidos['goles_penya'] = partidos['jornada'].map(goles_favor_por_jornada).fillna(0).astype(int)
            
            # Formatear tabla para mostrar
            tabla_partidos = partidos[['jornada', 'equipo_local', 'equipo_visitante', 'rival', 'es_local']]
            tabla_partidos['Goles Marcados'] = tabla_partidos['jornada'].map(goles_favor_por_jornada).fillna(0).astype(int)
            tabla_partidos['Condición'] = tabla_partidos['es_local'].map({True: 'Local', False: 'Visitante'})
            tabla_partidos = tabla_partidos.rename(columns={
                'jornada': 'Jornada',
                'equipo_local': 'Local',
                'equipo_visitante': 'Visitante',
                'rival': 'Rival'
            })
            
            # Mostrar tabla
            st.dataframe(
                tabla_partidos[['Jornada', 'Local', 'Visitante', 'Rival', 'Goles Marcados', 'Condición']],
                hide_index=True,
                use_container_width=True
            )
        
        with partido_tab2:
            # Rendimiento contra rivales (goles marcados)
            
            # Obtener los rivales de cada jornada
            rivales_jornada = partidos.set_index('jornada')['rival'].to_dict()
            
            # Contar goles por jornada para obtener goles a favor
            goles_jornada = data['goles_penya'].groupby('Jornada').size().to_dict()
            
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
                    color_discrete_sequence=[PENYA_PRIMARY_COLOR]
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
                
                # Añadir el rival a la jornada para el eje X
                goles_tendencia['jornada_rival'] = goles_tendencia['jornada'].astype(str) + ' - ' + goles_tendencia['rival']
                
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
                    line_color=PENYA_PRIMARY_COLOR,
                    marker=dict(size=8, color=PENYA_PRIMARY_COLOR)
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
        
        with partido_tab3:
            # Análisis de rendimiento como local vs visitante
            
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
            st.dataframe(comparativa, hide_index=True, use_container_width=True)
            
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
            
            # CAMBIO: Usar colores de Penya para la comparativa Local vs Visitante
            fig = px.bar(
                comparativa_filtrada,
                x='Métrica',
                y='Valor',
                color='Condición',
                barmode='group',
                title='Comparativa Local vs Visitante',
                labels={'Valor': 'Cantidad', 'Métrica': ''},
                color_discrete_map={'Local': PENYA_PRIMARY_COLOR, 'Visitante': PENYA_SECONDARY_COLOR}
            )
            
            # Personalizar tooltip
            fig.update_traces(
                hovertemplate='<b>%{x}</b><br>%{data.name}: %{y}<extra></extra>'
            )
            
            # Mostrar gráfico
            st.plotly_chart(fig, use_container_width=True)
    
    # Separador
    st.markdown("---")
    
    # Sección de sustituciones (se mantiene al final)
    if 'sustituciones_penya' in data:
        # Calcular distribución de sustituciones
        sustituciones_data = analizar_distribucion_sustituciones(data['sustituciones_penya'])
        
        # Mostrar gráfico de sustituciones
        st.subheader("Distribución de Sustituciones")
        graficar_distribucion_sustituciones(sustituciones_data)

if __name__ == "__main__":
    main()