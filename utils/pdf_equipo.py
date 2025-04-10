"""
Funciones específicas para la generación de PDF de equipos
"""
import io
from utils.pdf_export import PenyaPDF
from utils.constants import PENYA_PRIMARY_COLOR, PENYA_SECONDARY_COLOR, COLOR_TARJETAS_AMARILLAS, COLOR_TARJETAS_ROJAS

def generate_equipo_pdf(data, equipo_seleccionado):
    """
    Genera un PDF con el análisis del equipo seleccionado
    
    Args:
        data: Diccionario con todos los datos necesarios
        equipo_seleccionado: Nombre del equipo para análisis
        
    Returns:
        PenyaPDF: Objeto PDF generado
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
        
        # Inicializar PDF con título mejorado
        pdf = PenyaPDF(title=f"Análisis del Equipo - {equipo_seleccionado}")
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Filtrar datos del equipo
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
        
        # Calcular métricas avanzadas con manejo de excepciones mejorado
        try:
            metricas_avanzadas = calcular_metricas_avanzadas(
                partidos_penya, 
                goles_penya, 
                actas_penya, 
                actas,
                equipo_seleccionado,
                data.get('medias_liga', {})
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
            print(f"Error en cálculo de métricas avanzadas: {str(e)}")
            # Si hay error, usar cálculos básicos pero mantener consistencia
            
            # Calcular número de jugadores
            num_jugadores = actas_penya['jugador'].nunique()
            
            # Calcular goles a favor de forma robusta
            goles_favor = len(goles_penya)
            
            # Calcular goles en contra de forma robusta
            try:
                goles_contra = calcular_goles_contra(actas_penya, partidos_penya, actas, equipo_seleccionado)
            except Exception as e2:
                print(f"Error al calcular goles en contra: {str(e2)}")
                goles_contra = 0
            
            # Calcular tarjetas de forma robusta
            try:
                ta_propias = actas_penya['Tarjetas Amarillas'].sum()
                tr_propias = actas_penya['Tarjetas Rojas'].sum()
                
                # Calcular tarjetas rivales
                tarjetas_rivales = calcular_tarjetas_rivales(actas, partidos_penya, equipo_seleccionado)
                ta_rival = tarjetas_rivales['amarillas']
                tr_rival = tarjetas_rivales['rojas']
            except Exception as e3:
                print(f"Error al calcular tarjetas: {str(e3)}")
                ta_propias = tr_propias = ta_rival = tr_rival = 0
            
            # Obtener referencias o valores predeterminados
            medias_liga = data.get('medias_liga', {})
            ref_num_jugadores = medias_liga.get('ref_num_jugadores', "N/A")
            ref_goles_favor = medias_liga.get('ref_goles_favor', "N/A")  
            ref_goles_contra = medias_liga.get('ref_goles_contra', "N/A")
            ref_ta_propias = medias_liga.get('ref_tarjetas_amarillas', "N/A")
            ref_ta_rival = medias_liga.get('ref_ta_rival', "N/A") 
            ref_tr_propias = medias_liga.get('ref_tarjetas_rojas', "N/A") 
            ref_tr_rival = medias_liga.get('ref_tr_rival', "N/A")
            
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
                    'referencia': ref_num_jugadores
                },
                {
                    'titulo': 'Goles a favor',
                    'valor': goles_favor,
                    'referencia': ref_goles_favor
                },
                {
                    'titulo': 'Goles en contra',
                    'valor': goles_contra,
                    'referencia': ref_goles_contra
                },
                {
                    'titulo': 'Tarjetas Amarillas',
                    'valor': ta_propias,
                    'referencia': ref_ta_propias
                },
                {
                    'titulo': 'TA Rival',
                    'valor': ta_rival,
                    'referencia': ref_ta_rival
                },
                {
                    'titulo': 'Tarjetas Rojas',
                    'valor': tr_propias,
                    'referencia': ref_tr_propias
                },
                {
                    'titulo': 'TR Rival',
                    'valor': tr_rival,
                    'referencia': ref_tr_rival
                }
            ]
        
        # Posicionar después del encabezado
        pdf.set_y(35)
        
        # Añadir métricas básicas en una sola fila (convertir a formato adecuado para add_metrics_row)
        metrics_row = []
        for metrica in metricas:
            if metrica['referencia'] is not None:
                metrics_row.append((
                    metrica['titulo'], 
                    f"{metrica['valor']} ({metrica['referencia']})"
                ))
            else:
                metrics_row.append((metrica['titulo'], f"{metrica['valor']}"))
        
        # Añadir la fila de métricas con tamaño optimizado
        pdf.set_font('Arial', '', 8)  # Tamaño más pequeño para los títulos
        
        # Calcular ancho de cada métrica
        metric_width = 190 / len(metrics_row)
        
        # Añadir cada título
        for title, _ in metrics_row:
            pdf.cell(metric_width, 6, title, 0, 0, 'C')
        pdf.ln()
        
        # Valores de métricas
        pdf.set_font('Arial', 'B', 12)
        for _, value in metrics_row:
            pdf.cell(metric_width, 8, str(value), 0, 0, 'C')
        pdf.ln(15)
        
        # Restaurar tamaño de fuente predeterminado
        pdf.set_font('Arial', '', 12)
        
        # ----- SECCIÓN DE VISUALIZACIONES -----
        # Mejorar distribución de gráficos:
        # 1. Goles y Tarjetas en la primera fila
        # 2. Minutos y Sustituciones en la segunda fila
        
        # Configuración de visualizaciones
        graph_width = 85  # Ancho estándar para los gráficos
        top_row_y = 60    # Primera fila de gráficos
        bottom_row_y = 170 # Segunda fila de gráficos
        
        # 1. SECCIÓN DE GOLES (izquierda superior)
        pdf.set_font('Arial', 'B', 11)
        pdf.set_xy(10, top_row_y)
        pdf.cell(graph_width, 10, "Goles", 0, 1, 'L')
        
        try:
            goles_jugador = analizar_goles_por_jugador(goles_penya, actas_penya)
            if not goles_jugador.empty:
                # Mostrar hasta 15 jugadores con goles
                df = goles_jugador.head(15).copy()
                
                # Crear gráfico de barras horizontales
                fig = px.bar(
                    df,
                    y='jugador',
                    x='goles',
                    orientation='h',
                    labels={'jugador': 'Jugador', 'goles': 'Goles'},
                    color_discrete_sequence=[PENYA_PRIMARY_COLOR]
                )
                
                # Optimizar diseño del gráfico
                fig.update_layout(
                    yaxis={'categoryorder': 'total ascending'},
                    xaxis_title='Goles',
                    yaxis_title='',
                    showlegend=False,
                    margin=dict(l=130, r=30, t=10, b=30),
                    width=300,
                    height=300,
                    autosize=False,
                    yaxis_tickfont=dict(size=8),
                    bargap=0.15,
                )
                
                # Mostrar valores en las barras
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
            pdf.cell(graph_width, 10, "Error al generar gráfico", 0, 1, 'C')
        
        # 2. SECCIÓN DE TARJETAS (derecha superior)
        pdf.set_xy(105, top_row_y)
        pdf.cell(graph_width, 10, "Tarjetas", 0, 1, 'L')
        
        try:
            tarjetas_jugador = analizar_tarjetas_por_jugador(actas_penya)
            if not tarjetas_jugador.empty:
                # Ordenar por total de tarjetas
                tarjetas_jugador['total_tarjetas'] = tarjetas_jugador['Tarjetas Amarillas'] + tarjetas_jugador['Tarjetas Rojas'] * 2
                tarjetas_jugador = tarjetas_jugador.sort_values('total_tarjetas', ascending=False)
                df = tarjetas_jugador.head(15).copy()
                
                # Gráfico de barras apiladas para tarjetas
                fig = go.Figure()
                
                # Primero rojas, luego amarillas
                fig.add_trace(go.Bar(
                    y=df['jugador'],
                    x=df['Tarjetas Rojas'],
                    name='Rojas',
                    orientation='h',
                    marker=dict(color=COLOR_TARJETAS_ROJAS),
                    text=df['Tarjetas Rojas'],
                    textposition='auto',
                    insidetextanchor='middle',
                    textangle=0
                ))
                
                fig.add_trace(go.Bar(
                    y=df['jugador'],
                    x=df['Tarjetas Amarillas'],
                    name='Amarillas',
                    orientation='h',
                    marker=dict(color=COLOR_TARJETAS_AMARILLAS),
                    text=df['Tarjetas Amarillas'],
                    textposition='auto',
                    insidetextanchor='middle',
                    textangle=0
                ))
                
                # Optimizar diseño
                fig.update_layout(
                    xaxis_title='Número de Tarjetas',
                    yaxis_title='',
                    barmode='stack',
                    yaxis={'categoryorder': 'total descending'},
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ),
                    margin=dict(l=130, r=30, t=30, b=30),
                    width=300,
                    height=300,
                    autosize=False,
                    yaxis_tickfont=dict(size=8),
                    bargap=0.15,
                )
                
                # Asegurar que los valores sean visibles
                fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
                
                pdf.add_plot(fig, x=105, y=top_row_y + 10, w=graph_width)
            else:
                pdf.set_xy(105, top_row_y + 40)
                pdf.cell(graph_width, 10, "No hay datos de tarjetas", 0, 1, 'C')
        except Exception as e:
            print(f"Error al generar gráfico de tarjetas: {e}")
            pdf.set_xy(105, top_row_y + 40)
            pdf.cell(graph_width, 10, "Error al generar gráfico", 0, 1, 'C')
        
        # 3. SECCIÓN DE MINUTOS (izquierda inferior)
        pdf.set_xy(10, bottom_row_y)
        pdf.cell(graph_width, 10, "Minutos por Jugador", 0, 1, 'L')
        
        try:
            minutos_jugador = analizar_minutos_por_jugador(actas_penya)
            if not minutos_jugador.empty:
                df = minutos_jugador.head(15).copy()
                
                # Gráfico de minutos jugados
                fig = go.Figure()
                
                # Minutos como local
                fig.add_trace(go.Bar(
                    y=df['jugador'],
                    x=df['minutos_local'],
                    name='Local',
                    orientation='h',
                    marker=dict(color=PENYA_PRIMARY_COLOR),
                    text=df['minutos_local'],
                    textposition='auto',
                    insidetextanchor='middle',
                    textangle=0
                ))
                
                # Minutos como visitante
                fig.add_trace(go.Bar(
                    y=df['jugador'],
                    x=df['minutos_visitante'],
                    name='Visitante',
                    orientation='h',
                    marker=dict(color='#36A2EB' if PENYA_SECONDARY_COLOR is None else PENYA_SECONDARY_COLOR),
                    text=df['minutos_visitante'],
                    textposition='auto',
                    insidetextanchor='middle',
                    textangle=0
                ))
                
                # Optimizar diseño
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
                    margin=dict(l=130, r=30, t=30, b=30),
                    width=300,
                    height=300,
                    autosize=False,
                    yaxis_tickfont=dict(size=8),
                    bargap=0.15,
                )
                
                # Asegurar que los valores sean visibles
                fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
                
                pdf.add_plot(fig, x=10, y=bottom_row_y + 10, w=graph_width)
            else:
                pdf.set_xy(10, bottom_row_y + 40)
                pdf.cell(graph_width, 10, "No hay datos de minutos jugados", 0, 1, 'C')
        except Exception as e:
            print(f"Error al generar gráfico de minutos: {e}")
            pdf.set_xy(10, bottom_row_y + 40)
            pdf.cell(graph_width, 10, "Error al generar gráfico", 0, 1, 'C')
        
        # 4. SECCIÓN DE SUSTITUCIONES (derecha inferior)
        pdf.set_xy(105, bottom_row_y)
        pdf.cell(graph_width, 10, "Distribución de Sustituciones", 0, 1, 'L')
        
        try:
            # Comprobar si hay datos de sustituciones
            if not sustituciones_penya.empty:
                # Calcular distribución de sustituciones
                sustituciones_data = analizar_distribucion_sustituciones(sustituciones_penya, rango_minutos=5)
                
                # Gráfico de distribución de sustituciones
                fig = px.bar(
                    sustituciones_data['distribucion_minutos'],
                    x='rango',
                    y='cantidad',
                    labels={'rango': 'Minuto', 'cantidad': 'Número de Sustituciones'},
                    color_discrete_sequence=[PENYA_SECONDARY_COLOR]
                )
                
                # Optimizar diseño
                fig.update_layout(
                    xaxis_title='',
                    yaxis_title='Número de Sustituciones',
                    showlegend=False,
                    margin=dict(l=40, r=10, t=10, b=60),
                    width=300,
                    height=150,
                    autosize=False,
                )
                
                # Título del eje X con espacio adicional
                fig.update_xaxes(
                    title_text="Rango de Minutos",
                    title_standoff=25
                )
                
                # Mostrar valores en barras
                fig.update_traces(
                    texttemplate='%{y}', 
                    textposition='outside',
                    textfont=dict(size=10)
                )
                
                pdf.add_plot(fig, x=105, y=bottom_row_y + 10, w=graph_width)
                
                # Calcular posición Y para métricas de sustituciones
                sust_metrics_y = pdf.get_y() + 5
                
                # Métricas de sustituciones en una fila
                sust_metrics = [
                    ('Minuto Medio', f"{sustituciones_data['minuto_medio']:.1f}'"),
                    ('Primera Sust.', f"{sustituciones_data['primera_sustitucion']:.1f}'"),
                    ('Última Sust.', f"{sustituciones_data['ultima_sustitucion']:.1f}'"),
                    ('Núm. Medio', f"{sustituciones_data['num_medio_sustituciones']:.1f}")
                ]
                
                # Añadir métricas de sustituciones
                pdf.set_y(sust_metrics_y)
                pdf.set_x(105)
                
                # Usar tamaño de letra más pequeño
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
                pdf.cell(graph_width, 10, "No hay datos de sustituciones", 0, 1, 'C')
        except Exception as e:
            print(f"Error al generar análisis de sustituciones: {e}")
            pdf.set_xy(105, bottom_row_y + 40)
            pdf.cell(graph_width, 10, "Error al generar análisis", 0, 1, 'C')
        
        return pdf
    except Exception as e:
        print(f"Error general al generar el PDF de equipo: {str(e)}")
        # Crear un PDF simple con mensaje de error
        pdf = PenyaPDF(title=f"Error al generar análisis - {equipo_seleccionado}")
        pdf.set_y(50)
        pdf.set_font('Arial', 'B', 12)
        pdf.multi_cell(0, 10, f"Se produjo un error al generar el PDF: {str(e)}", 0, 'C')
        return pdf