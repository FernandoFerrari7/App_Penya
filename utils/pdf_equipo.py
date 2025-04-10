"""
Funciones específicas para la generación de PDF de equipos
"""
import io
from utils.pdf_export import PenyaPDF
from utils.constants import PENYA_PRIMARY_COLOR, PENYA_SECONDARY_COLOR, COLOR_TARJETAS_AMARILLAS, COLOR_TARJETAS_ROJAS

def generate_equipo_pdf(data, equipo_seleccionado):
    """
    Genera un PDF con el análisis del equipo seleccionado
    """
    try:
        from calculos.calculo_equipo import (
            calcular_estadisticas_generales, calcular_metricas_avanzadas,
            obtener_rivales_con_goles, analizar_tarjetas_por_jornada,
            analizar_tipos_goles, calcular_goles_contra,
            calcular_tarjetas_rivales, normalizar_nombre_equipo
        )
        from calculos.calculo_jugadores import (
            obtener_top_goleadores, obtener_top_amonestados,
            analizar_goles_por_tiempo, analizar_minutos_por_jugador,
            analizar_goles_por_jugador, analizar_tarjetas_por_jugador,
            analizar_distribucion_sustituciones
        )
        from visualizaciones.equipo import (
            graficar_tarjetas_por_jornada, graficar_tipos_goles,
            graficar_goles_por_tiempo
        )
        from visualizaciones.jugadores import (
            graficar_goles_por_jugador, graficar_tarjetas_por_jugador
        )
        from visualizaciones.minutos import (
            graficar_minutos_por_jugador,
            graficar_minutos_por_jugador_desglose
        )
        import plotly.express as px
        import plotly.graph_objects as go
        
        # Inicializar PDF
        pdf = PenyaPDF(title=f"Análisis del Equipo - {equipo_seleccionado}")
        # Establecer auto_page_break en False para mantener todo en una página
        pdf.set_auto_page_break(auto=False, margin=15)
        
        # Filtrar datos del equipo (similar a filtrar_datos_equipo en equipos.py)
        equipo_normalizado = normalizar_nombre_equipo(equipo_seleccionado)
        
        # Función para filtrar por equipo normalizado
        def filtrar_por_equipo(campo):
            return campo.apply(lambda x: normalizar_nombre_equipo(x)).str.contains(equipo_normalizado, na=False)
        
        # Filtrar actas
        actas = data['actas']
        actas_penya = data['actas'][filtrar_por_equipo(data['actas']['equipo'])]
        
        # Crear un mapa de jugador -> equipo para filtrar goles específicos del equipo
        jugador_equipo = data['actas'][['jugador', 'equipo']].drop_duplicates()
        jugador_equipo_dict = dict(zip(jugador_equipo['jugador'], jugador_equipo['equipo']))
        
        # Filtrar goles
        goles_con_equipo = data['goles'].copy()
        goles_con_equipo['equipo'] = goles_con_equipo['jugador'].map(jugador_equipo_dict)
        goles_penya = goles_con_equipo[filtrar_por_equipo(goles_con_equipo['equipo'])].copy()
        
        # Filtrar partidos
        partidos_filtrados = data['jornadas'][
            (filtrar_por_equipo(data['jornadas']['equipo_local'])) | 
            (filtrar_por_equipo(data['jornadas']['equipo_visitante']))
        ].copy()
        
        # Añadir columna es_local para facilitar cálculos posteriores
        partidos_filtrados['es_local'] = filtrar_por_equipo(partidos_filtrados['equipo_local'])
        partidos_penya = partidos_filtrados
        
        # Filtrar sustituciones
        sustituciones_penya = data['sustituciones'][filtrar_por_equipo(data['sustituciones']['equipo'])]
        
        # Recopilar los datos filtrados en un diccionario
        datos_equipo = {
            'actas': actas,
            'actas_penya': actas_penya,
            'goles_penya': goles_penya,
            'partidos_penya': partidos_penya,
            'sustituciones_penya': sustituciones_penya
        }
        
        # Calcular número de partidos jugados
        partidos_jugados = partidos_penya[
            partidos_penya['link_acta'].notna() & 
            (partidos_penya['link_acta'] != '')
        ].shape[0]
        
        # Calcular métricas avanzadas
        try:
            metricas_avanzadas = calcular_metricas_avanzadas(
                partidos_penya, 
                goles_penya, 
                actas_penya, 
                actas,
                equipo_seleccionado,  # Pasar el equipo seleccionado como parámetro
                data['medias_liga']   # Pasar las medias precalculadas
            )
            
            # Crear lista de métricas para mostrar
            metricas = [
                {
                    'titulo': 'Partidos Jugados',
                    'valor': partidos_jugados,
                    'referencia': None
                },
                {
                    'titulo': 'Num. Jugadores',
                    'valor': metricas_avanzadas['general'][0]['valor'],
                    'referencia': metricas_avanzadas['general'][0]['referencia']
                },
                {
                    'titulo': 'Goles a favor',
                    'valor': metricas_avanzadas['goles'][0]['valor'],
                    'referencia': metricas_avanzadas['goles'][0]['referencia']
                },
                {
                    'titulo': 'Goles en contra',
                    'valor': metricas_avanzadas['goles'][1]['valor'],
                    'referencia': metricas_avanzadas['goles'][1]['referencia']
                },
                {
                    'titulo': 'Tarjetas Amarillas',
                    'valor': metricas_avanzadas['tarjetas'][0]['valor'],
                    'referencia': metricas_avanzadas['tarjetas'][0]['referencia']
                },
                {
                    'titulo': 'TA Rival',
                    'valor': metricas_avanzadas['tarjetas'][1]['valor'],
                    'referencia': metricas_avanzadas['tarjetas'][1]['referencia']
                },
                {
                    'titulo': 'Tarjetas Rojas',
                    'valor': metricas_avanzadas['tarjetas'][2]['valor'],
                    'referencia': metricas_avanzadas['tarjetas'][2]['referencia']
                },
                {
                    'titulo': 'TR Rival',
                    'valor': metricas_avanzadas['tarjetas'][3]['valor'],
                    'referencia': metricas_avanzadas['tarjetas'][3]['referencia']
                }
            ]
        except Exception as e:
            # Si no se pueden calcular, usar valores predeterminados pero mantener partidos jugados correcto
            print(f"No se pudieron calcular algunas métricas para el equipo seleccionado: {str(e)}")
            
            # Calcular número de jugadores
            num_jugadores = actas_penya['jugador'].nunique()
            
            # Calcular goles a favor
            goles_favor = len(goles_penya)
            
            # Calcular goles en contra
            goles_contra = calcular_goles_contra(actas_penya, partidos_penya, actas, equipo_seleccionado)
            
            # Calcular tarjetas amarillas propias
            ta_propias = actas_penya['Tarjetas Amarillas'].sum()
            
            # Calcular tarjetas rojas propias
            tr_propias = actas_penya['Tarjetas Rojas'].sum()
            
            # Calcular tarjetas rivales
            tarjetas_rivales = calcular_tarjetas_rivales(actas, partidos_penya, equipo_seleccionado)
            ta_rival = tarjetas_rivales['amarillas']
            tr_rival = tarjetas_rivales['rojas']
            
            # Crear lista de métricas para mostrar
            metricas = [
                {
                    'titulo': 'Partidos Jugados',
                    'valor': partidos_jugados,
                    'referencia': None
                },
                {
                    'titulo': 'Num. Jugadores',
                    'valor': num_jugadores,
                    'referencia': data['medias_liga']['ref_num_jugadores']
                },
                {
                    'titulo': 'Goles a favor',
                    'valor': goles_favor,
                    'referencia': data['medias_liga']['ref_goles_favor']
                },
                {
                    'titulo': 'Goles en contra',
                    'valor': goles_contra,
                    'referencia': data['medias_liga']['ref_goles_contra']
                },
                {
                    'titulo': 'Tarjetas Amarillas',
                    'valor': ta_propias,
                    'referencia': data['medias_liga']['ref_tarjetas_amarillas']
                },
                {
                    'titulo': 'TA Rival',
                    'valor': ta_rival,
                    'referencia': data['medias_liga']['ref_ta_rival']
                },
                {
                    'titulo': 'Tarjetas Rojas',
                    'valor': tr_propias,
                    'referencia': data['medias_liga']['ref_tarjetas_rojas']
                },
                {
                    'titulo': 'TR Rival',
                    'valor': tr_rival,
                    'referencia': data['medias_liga']['ref_tr_rival']
                }
            ]
        
        # Posicionar después del encabezado
        pdf.set_y(35)
        
        # Añadir métricas básicas en una sola fila (convertir a formato adecuado para add_metrics_row)
        metrics_row = []
        for metrica in metricas:
            if metrica['referencia'] is not None:
                metrics_row.append((metrica['titulo'], f"{metrica['valor']} ({metrica['referencia']})"))
            else:
                metrics_row.append((metrica['titulo'], f"{metrica['valor']}"))
                
        # Modificar la función add_metrics_row para usar tamaño de fuente más pequeño en esta primera fila
        current_font_size = pdf.font_size_pt
        pdf.set_font('Arial', '', 8)  # Tamaño más pequeño para los títulos
        
        # Calcular ancho de cada métrica
        metric_width = 190 / len(metrics_row)
        
        # Añadir cada título
        for title, _ in metrics_row:
            pdf.cell(metric_width, 6, title, 0, 0, 'C')
        pdf.ln()
        
        # Valores
        pdf.set_font('Arial', 'B', 12)  # Tamaño más pequeño para los valores
        for _, value in metrics_row:
            pdf.cell(metric_width, 8, str(value), 0, 0, 'C')
        pdf.ln(15)
        
        # Restaurar tamaño de fuente
        pdf.set_font('Arial', '', current_font_size)
        
        # ----- SECCIÓN DE GRÁFICOS -----
        # Ajustar tamaños para que aprovechen mejor el espacio
        graph_width = 85  # Ancho de los gráficos
        
        # Mejor distribución vertical de gráficos en la página
        # Dejamos un margen superior menor y espaciamos más los gráficos
        top_row_y = 60  # Primera fila de gráficos
        bottom_row_y = 170  # Segunda fila de gráficos
        
        # 1. Gráfico de Goles por Jugador (cuadrante superior izquierdo)
        pdf.set_font('Arial', 'B', 11)
        pdf.set_xy(10, top_row_y)
        pdf.cell(graph_width, 10, "Goles", 0, 1, 'L')
        
        try:
            goles_jugador = analizar_goles_por_jugador(goles_penya, actas_penya)
            if not goles_jugador.empty:
                # Mostrar todos los jugadores que tienen al menos un gol (hasta un máx de 15)
                df = goles_jugador.head(15).copy()
                
                # Crear un gráfico más alto que ancho
                fig = px.bar(
                    df,
                    y='jugador',
                    x='goles',
                    orientation='h',
                    labels={'jugador': 'Jugador', 'goles': 'Goles'},
                    color_discrete_sequence=[PENYA_PRIMARY_COLOR]
                )
                
                # Configurar el gráfico para que sea más alto que ancho y con mejor margen para nombres
                fig.update_layout(
                    yaxis={'categoryorder': 'total ascending'},
                    xaxis_title='Goles',
                    yaxis_title='',
                    showlegend=False,
                    margin=dict(l=130, r=30, t=10, b=30),  # Aumentar aún más el margen izquierdo para nombres
                    width=300,  # Ancho fijo
                    height=300,  # Aumentar la altura para acomodar más jugadores
                    autosize=False,  # Desactivar autosize
                    # Mostrar nombres completos
                    yaxis_tickfont=dict(size=8),  # Texto más pequeño para acomodar nombres completos
                    # Controlar altura de barras para que sean más altas
                    bargap=0.15,  # Reducir aún más el espacio entre barras
                )
                
                # Mostrar los valores en las barras
                fig.update_traces(
                    texttemplate='%{x}', 
                    textposition='outside',
                    textfont=dict(size=9)
                )
                
                pdf.add_plot(fig, x=10, y=top_row_y + 10, w=graph_width)
            else:
                pdf.set_xy(10, top_row_y + 40)
                pdf.cell(graph_width, 10, "No hay datos de goles", 0, 1, 'C')
        except Exception as e:
            print(f"Error al generar gráfico de goles por jugador: {e}")
            pdf.set_xy(10, top_row_y + 40)
            pdf.cell(graph_width, 10, "Error al generar gráfico de goles", 0, 1, 'C')
        
        # 2. Gráfico de Tarjetas por Jugador (cuadrante superior derecho)
        pdf.set_xy(105, top_row_y)
        pdf.cell(graph_width, 10, "Tarjetas", 0, 1, 'L')
        
        try:
            tarjetas_jugador = analizar_tarjetas_por_jugador(actas_penya)
            if not tarjetas_jugador.empty:
                # Mostrar más jugadores (15 en lugar de 10)
                # Ordenar por el total de tarjetas (rojas + amarillas) para mostrar los más relevantes
                tarjetas_jugador['total_tarjetas'] = tarjetas_jugador['Tarjetas Amarillas'] + tarjetas_jugador['Tarjetas Rojas'] * 2
                tarjetas_jugador = tarjetas_jugador.sort_values('total_tarjetas', ascending=False)
                df = tarjetas_jugador.head(15).copy()
                
                fig = go.Figure()
                
                # Primero rojas, luego amarillas
                fig.add_trace(go.Bar(
                    y=df['jugador'],
                    x=df['Tarjetas Rojas'],
                    name='Rojas',
                    orientation='h',
                    marker=dict(color=COLOR_TARJETAS_ROJAS),
                    text=df['Tarjetas Rojas'],  # Añadir valores
                    textposition='auto',  # Posicionar automáticamente
                    insidetextanchor='middle',  # Anclar en el medio
                    textangle=0  # Forzar texto horizontal dentro de las barras
                ))
                
                fig.add_trace(go.Bar(
                    y=df['jugador'],
                    x=df['Tarjetas Amarillas'],
                    name='Amarillas',
                    orientation='h',
                    marker=dict(color=COLOR_TARJETAS_AMARILLAS),
                    text=df['Tarjetas Amarillas'],  # Añadir valores
                    textposition='auto',  # Posicionar automáticamente
                    insidetextanchor='middle',  # Anclar en el medio
                    textangle=0  # Forzar texto horizontal dentro de las barras
                ))
                
                # Configurar el gráfico para que sea más alto que ancho y con mejor margen para nombres
                fig.update_layout(
                    xaxis_title='Número de Tarjetas',
                    yaxis_title='',
                    barmode='stack',
                    yaxis={'categoryorder': 'total descending'},  # Reordenar de mayor a menor
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ),
                    margin=dict(l=130, r=30, t=30, b=30),  # Aumentar aún más el margen izquierdo para nombres
                    width=300,  # Ancho fijo
                    height=300,  # Aumentar la altura para acomodar más jugadores
                    autosize=False,  # Desactivar autosize
                    # Mostrar nombres completos
                    yaxis_tickfont=dict(size=8),  # Texto más pequeño para acomodar nombres completos
                    # Controlar altura de barras para que sean más altas
                    bargap=0.15,  # Reducir aún más el espacio entre barras
                )
                
                # Asegurar que los valores sean visibles
                fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
                
                pdf.add_plot(fig, x=105, y=top_row_y + 10, w=graph_width)
            else:
                pdf.set_xy(105, top_row_y + 40)
                pdf.cell(graph_width, 10, "No hay datos de tarjetas", 0, 1, 'C')
        except Exception as e:
            print(f"Error al generar gráfico de tarjetas por jugador: {e}")
            pdf.set_xy(105, top_row_y + 40)
            pdf.cell(graph_width, 10, "Error al generar gráfico de tarjetas", 0, 1, 'C')
        
        # 3. Gráfico de Minutos por Jugador - Local vs Visitante (cuadrante inferior izquierdo)
        pdf.set_xy(10, bottom_row_y)
        pdf.cell(graph_width, 10, "Minutos por Jugador", 0, 1, 'L')
        
        try:
            minutos_jugador = analizar_minutos_por_jugador(actas_penya)
            if not minutos_jugador.empty:
                # Mostrar más jugadores (15 en lugar de 10)
                df = minutos_jugador.head(15).copy()
                
                fig = go.Figure()
                
                # Minutos como local
                fig.add_trace(go.Bar(
                    y=df['jugador'],
                    x=df['minutos_local'],
                    name='Local',
                    orientation='h',
                    marker=dict(color=PENYA_PRIMARY_COLOR),
                    text=df['minutos_local'],  # Añadir valores
                    textposition='auto',  # Posicionar automáticamente
                    insidetextanchor='middle',  # Anclar en el medio
                    textangle=0  # Forzar texto horizontal dentro de las barras
                ))
                
                # Minutos como visitante
                fig.add_trace(go.Bar(
                    y=df['jugador'],
                    x=df['minutos_visitante'],
                    name='Visitante',
                    orientation='h',
                    marker=dict(color='#36A2EB' if PENYA_SECONDARY_COLOR is None else PENYA_SECONDARY_COLOR),
                    text=df['minutos_visitante'],  # Añadir valores
                    textposition='auto',  # Posicionar automáticamente
                    insidetextanchor='middle',  # Anclar en el medio
                    textangle=0  # Forzar texto horizontal dentro de las barras
                ))
                
                fig.update_layout(
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
                    margin=dict(l=130, r=30, t=30, b=30),  # Aumentar aún más el margen izquierdo para nombres
                    width=300,  # Ancho fijo
                    height=300,  # Aumentar la altura para acomodar más jugadores
                    autosize=False,  # Desactivar autosize
                    # Mostrar nombres completos
                    yaxis_tickfont=dict(size=8),  # Texto más pequeño para acomodar nombres completos
                    # Controlar altura de barras para que sean más altas
                    bargap=0.15,  # Reducir aún más el espacio entre barras
                )
                
                # Asegurar que los valores sean visibles
                fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
                
                pdf.add_plot(fig, x=10, y=bottom_row_y + 10, w=graph_width)
            else:
                pdf.set_xy(10, bottom_row_y + 40)
                pdf.cell(graph_width, 10, "No hay datos de minutos jugados", 0, 1, 'C')
        except Exception as e:
            print(f"Error al generar gráfico de minutos por jugador: {e}")
            pdf.set_xy(10, bottom_row_y + 40)
            pdf.cell(graph_width, 10, "Error al generar gráfico de minutos", 0, 1, 'C')
        
        # 4. Distribución de Sustituciones (cuadrante inferior derecho)
        pdf.set_xy(105, bottom_row_y)
        pdf.cell(graph_width, 10, "Distribución de Sustituciones", 0, 1, 'L')
        
        try:
            # Comprobar si hay datos de sustituciones
            if not sustituciones_penya.empty:
                # Calcular distribución de sustituciones con un rango de 5 minutos
                sustituciones_data = analizar_distribucion_sustituciones(sustituciones_penya, rango_minutos=5)
                
                # Gráfico de distribución de sustituciones por minuto
                fig = px.bar(
                    sustituciones_data['distribucion_minutos'],
                    x='rango',
                    y='cantidad',
                    labels={'rango': 'Minuto', 'cantidad': 'Número de Sustituciones'},
                    color_discrete_sequence=[PENYA_SECONDARY_COLOR]
                )
                
                # Configurar el gráfico con una altura apropiada
                fig.update_layout(
                    xaxis_title='',  # Quitar el título del eje X para evitar sobreposición
                    yaxis_title='Número de Sustituciones',
                    showlegend=False,
                    margin=dict(l=40, r=10, t=10, b=60),  # Aumentar el margen inferior para el título del eje X
                    width=300,  # Ancho fijo
                    height=150,  # Altura reducida para dejar espacio a las métricas
                    autosize=False,
                )
                
                # Mover el título de "Rango de Minutos" hacia abajo
                fig.update_xaxes(
                    title_text="Rango de Minutos",
                    title_standoff=25  # Distancia entre el eje y el título
                )
                
                # Mostrar los valores en las barras
                fig.update_traces(
                    texttemplate='%{y}', 
                    textposition='outside',
                    textfont=dict(size=10)
                )
                
                pdf.add_plot(fig, x=105, y=bottom_row_y + 10, w=graph_width)
                
                # Calcular la posición Y después del gráfico
                sust_metrics_y = pdf.get_y() + 5
                
                # Métricas de sustituciones en una fila debajo del gráfico
                sust_metrics = [
                    ('Minuto Medio', f"{sustituciones_data['minuto_medio']:.1f}'"),
                    ('Primera Sust.', f"{sustituciones_data['primera_sustitucion']:.1f}'"),
                    ('Última Sust.', f"{sustituciones_data['ultima_sustitucion']:.1f}'"),
                    ('Núm. Medio', f"{sustituciones_data['num_medio_sustituciones']:.1f}")
                ]
                
                # Añadir las métricas de sustituciones debajo del gráfico correspondiente
                pdf.set_y(sust_metrics_y)
                pdf.set_x(105)
                
                # Usar tamaño de letra más pequeño para las métricas de sustituciones
                current_font_size = pdf.font_size_pt
                pdf.set_font('Arial', '', 8)
                
                # Calcular ancho para cada métrica
                sust_metric_width = graph_width / len(sust_metrics)
                
                # Añadir títulos
                for title, _ in sust_metrics:
                    pdf.cell(sust_metric_width, 5, title, 0, 0, 'C')
                pdf.ln()
                
                # Añadir valores
                pdf.set_x(105)
                pdf.set_font('Arial', 'B', 10)
                for _, value in sust_metrics:
                    pdf.cell(sust_metric_width, 6, value, 0, 0, 'C')
                    
                # Restaurar tamaño de fuente
                pdf.set_font('Arial', '', current_font_size)
            else:
                pdf.set_xy(105, bottom_row_y + 40)
                pdf.cell(graph_width, 10, "No hay datos de sustituciones disponibles", 0, 1, 'C')
        except Exception as e:
            print(f"Error al generar análisis de sustituciones: {e}")
            pdf.set_xy(105, bottom_row_y + 40)
            pdf.cell(graph_width, 10, f"Error al generar análisis de sustituciones", 0, 1, 'C')
        
        return pdf
    except Exception as e:
        print(f"Error al generar el PDF: {str(e)}")
        raise e