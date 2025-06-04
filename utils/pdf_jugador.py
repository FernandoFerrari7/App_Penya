"""
Funciones específicas para la generación de PDF de jugadores
"""
import io
from utils.pdf_export import PenyaPDF
from utils.constants import PENYA_PRIMARY_COLOR, PENYA_SECONDARY_COLOR, COLOR_TARJETAS_AMARILLAS, COLOR_TARJETAS_ROJAS

def generate_jugador_pdf(data, jugador_seleccionado):
    """
    Genera un PDF con el análisis del jugador seleccionado
    
    Args:
        data: Diccionario con todos los datos necesarios
        jugador_seleccionado: Nombre del jugador para análisis
        
    Returns:
        PenyaPDF: Objeto PDF generado
    """
    try:
        import pandas as pd
        import plotly.express as px
        import plotly.graph_objects as go
        import numpy as np
        from calculos.calculo_jugadores import calcular_estadisticas_jugador, ajustar_tarjetas_por_doble_amarilla, analizar_goles_por_tiempo
        from calculos.calculo_minutos import obtener_minutos_por_jornada
        
        # Inicializar PDF
        pdf = PenyaPDF(title=f"Análisis del Jugador - {jugador_seleccionado}")
        pdf.set_auto_page_break(auto=False, margin=15)  # Desactivamos auto page break para control preciso
        
        # Filtrar datos del jugador
        actas_df = data['actas_penya'] if 'actas_penya' in data else data['actas']
        goles_df = data['goles_penya'] if 'goles_penya' in data else data['goles']
        
        # Obtener estadísticas del jugador
        estadisticas = calcular_estadisticas_jugador(actas_df, jugador_seleccionado)
        
        if not estadisticas:
            # Si no hay datos, mostrar mensaje
            pdf.set_y(50)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, f"No se encontraron datos para el jugador {jugador_seleccionado}", 0, 1, 'C')
            return pdf
        
        # Obtener equipo del jugador
        jugador_actas = actas_df[actas_df['jugador'] == jugador_seleccionado]
        equipo_jugador = jugador_actas['equipo'].iloc[0] if not jugador_actas.empty else "Desconocido"
        
        # Posicionarse después del encabezado
        pdf.set_y(35)
        
        # Calcular métricas adicionales
        minutos_por_gol = estadisticas['minutos_jugados'] / estadisticas['goles'] if estadisticas['goles'] > 0 else float('inf')
        minutos_por_ta = estadisticas['minutos_jugados'] / estadisticas['tarjetas_amarillas'] if estadisticas['tarjetas_amarillas'] > 0 else float('inf')
        minutos_por_tr = estadisticas['minutos_jugados'] / estadisticas['tarjetas_rojas'] if estadisticas['tarjetas_rojas'] > 0 else float('inf')
        
        # Añadir la fila de métricas principales similar a la interfaz de la app
        metricas_row1 = [
            ('Minutos Jugados', f"{estadisticas['minutos_jugados']}"),
            ('Titular/Suplente', f"{estadisticas['titularidades']}/{estadisticas['suplencias']}"),
            ('Goles', f"{estadisticas['goles']}"),
            ('Minutos por Gol', f"{int(minutos_por_gol)}" if minutos_por_gol != float('inf') else "-")
        ]
        
        metricas_row2 = [
            ('Tarjetas Amarillas', f"{estadisticas['tarjetas_amarillas']}"),
            ('Minutos por TA', f"{int(minutos_por_ta)}" if minutos_por_ta != float('inf') else "-"),
            ('Tarjetas Rojas', f"{estadisticas['tarjetas_rojas']}"),
            ('Minutos por TR', f"{int(minutos_por_tr)}" if minutos_por_tr != float('inf') else "-")
        ]
        
        # Añadir las filas de métricas
        pdf.add_metrics_row(metricas_row1)
        pdf.add_metrics_row(metricas_row2)
        
        # Añadir separador
        pdf.ln(5)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)  
        
        # Configuración común para visualizaciones
        section_start_y = pdf.get_y()  # Y donde comienzan las secciones principales
        izq_x, der_x = 10, 105  # Coordenadas X para columnas izquierda y derecha
        
        # Altura máxima disponible para secciones (para mantener todo en una página)
        max_section_height = 230  # Ajustado para que quepa en una página
        
        # ----- SECCIÓN DE MINUTOS (IZQUIERDA) -----
        pdf.set_xy(izq_x, section_start_y)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(90, 8, "Minutos", 0, 1, 'L')
        
        # Obtener minutos por jornada para visualización
        minutos_jornada = obtener_minutos_por_jornada(actas_df, jugador_seleccionado)
        
        if not minutos_jornada.empty:
            # Crear columna de condición basada en si es titular
            minutos_jornada['Condición'] = minutos_jornada['es_titular'].map({True: 'Titular', False: 'Suplente'})
            
            # --- Pestaña 1: Minutos por Jornada ---
            minutos_y = section_start_y + 10
            pdf.set_xy(izq_x, minutos_y)
            pdf.set_font('Arial', 'B', 9)
            pdf.cell(90, 6, "Minutos por Jornada", 0, 1, 'L')
            
            # Crear gráfico de minutos por jornada
            fig_minutos = px.bar(
                minutos_jornada,
                x='jornada',
                y='minutos_jugados',
                color='es_titular',
                labels={'jornada': 'Jornada', 'minutos_jugados': 'Minutos', 'es_titular': 'Condición'},
                color_discrete_map={True: PENYA_PRIMARY_COLOR, False: PENYA_SECONDARY_COLOR},
                hover_data=['rival']
            )
            
            # Configurar aspecto del gráfico
            fig_minutos.update_layout(
                xaxis_title='Jornada',
                yaxis_title='Minutos',
                yaxis_range=[0, 100],
                legend_title="Condición",
                showlegend=True,
                margin=dict(l=40, r=10, t=20, b=30),  
                height=130,  
                width=350,
                font=dict(size=8) 
            )
            
            # Actualizar leyenda
            fig_minutos.for_each_trace(lambda t: t.update(name='Titular' if t.name == 'True' else 'Suplente'))
            
            # Añadir el gráfico al PDF
            pdf.add_plot(fig_minutos, x=izq_x, y=minutos_y + 7, w=85)
            
            # --- Pestaña 2: Desglose por participación ---
            # Calcular la posición Y para la siguiente pestaña (después del gráfico anterior)
            desglose_y = pdf.get_y()
            
            pdf.set_xy(izq_x, desglose_y)
            pdf.set_font('Arial', 'B', 9)
            pdf.cell(90, 6, "Desglose por participación", 0, 1, 'L')
            
            # Calcular diferentes tipos de participación
            titular_completo = sum((minutos_jornada['es_titular'] == True) & (minutos_jornada['minutos_jugados'] == 90))
            titular_sustituido = sum((minutos_jornada['es_titular'] == True) & (minutos_jornada['minutos_jugados'] < 90))
            suplente = sum(minutos_jornada['es_titular'] == False)
            
            # Calcular partidos en los que no participó
            partidos_totales = len(data['partidos_penya']) if 'partidos_penya' in data else 30  # Valor predeterminado si no hay datos
            partidos_jugados = len(minutos_jornada)
            no_participa = partidos_totales - partidos_jugados
            
            # Crear datos para el gráfico
            categorias = ['Titular todo el partido', 'Titular Sustituido', 'Participación Suplente', 'No Participa']
            valores = [titular_completo, titular_sustituido, suplente, no_participa]
            
            # Crear gráfico de barras simplificado para desglose
            fig_desglose = go.Figure()
            
            # Añadir barras (alternando naranja y negro)
            fig_desglose.add_trace(go.Bar(
                x=categorias,
                y=valores,
                marker_color=[PENYA_PRIMARY_COLOR, PENYA_SECONDARY_COLOR, PENYA_PRIMARY_COLOR, PENYA_SECONDARY_COLOR]
            ))
            
            # Personalizar el gráfico para hacerlo más compacto pero legible
            fig_desglose.update_layout(
                xaxis_title='',  # Quitar título del eje X
                yaxis_title='Partidos',
                yaxis=dict(
                    tickmode='linear',
                    tick0=0,
                    dtick=1,
                    range=[0, max(valores) + 1]  # Ajustar rango del eje Y
                ),
                margin=dict(l=40, r=10, t=10, b=50),  # Aumentar margen inferior para dar espacio a las etiquetas
                height=130,  # Aumentado para que se vea menos achatado
                width=350,
                font=dict(size=8)  # Reducir tamaño de fuente
            )
            
            # Ajustar el tamaño del texto en el eje X y reducir longitud de las etiquetas
            etiquetas_cortas = ['Titular compl.', 'Titular sust.', 'Suplente', 'No participa']
            fig_desglose.update_xaxes(
                ticktext=etiquetas_cortas,  # Usar etiquetas más cortas
                tickvals=list(range(len(categorias))),  # Mantener posición de las barras
                tickfont=dict(size=7),  # Texto ligeramente más grande
                tickangle=0  # Sin ángulo para mejor legibilidad
            )
            
            # Añadir el gráfico al PDF
            pdf.add_plot(fig_desglose, x=izq_x, y=desglose_y + 7, w=85)
            
            # --- Pestaña 3: Detalle por Partido ---
            # Calcular la posición Y para la siguiente pestaña
            detalles_y = pdf.get_y()
            
            pdf.set_xy(izq_x, detalles_y)
            pdf.set_font('Arial', 'B', 9)
            pdf.cell(90, 6, "Detalle por Partido", 0, 1, 'L')
            
            # Crear una tabla simple con los datos de participación
            tabla_partidos = minutos_jornada[['jornada', 'rival', 'Condición', 'minutos_jugados']].copy()
            tabla_partidos = tabla_partidos.rename(columns={
                'jornada': 'Jornada',
                'rival': 'Rival',
                'minutos_jugados': 'Minutos'
            })
            
            # Ordenar por jornada
            tabla_partidos = tabla_partidos.sort_values('Jornada')
            
            # Configurar la tabla
            pdf.set_xy(izq_x, detalles_y + 7)
            pdf.set_font('Arial', 'B', 8)
            
            # Definir anchos de columnas
            col_widths = [15, 34, 18, 18]  # Jornada, Rival, Condición, Minutos
            
            # Cabecera de la tabla
            x_pos = izq_x
            for idx, col in enumerate(['Jornada', 'Rival', 'Condición', 'Minutos']):
                pdf.set_xy(x_pos, pdf.get_y())
                pdf.cell(col_widths[idx], 6, col, 1, 0, 'C')
                x_pos += col_widths[idx]
            pdf.ln()
            
            # SOLUCIÓN: Calcular dinámicamente el alto de fila para que TODOS los partidos quepan
            pdf.set_font('Arial', '', 6)
            
            # Calcular altura disponible para la tabla
            remaining_space = 280 - pdf.get_y()  # Espacio hasta el final de la página
            num_partidos = len(tabla_partidos)
            
            # Si hay partidos, calcular el alto óptimo por fila
            if num_partidos > 0:
                # Calcular alto de fila dinámicamente para que quepan todos los partidos
                # Dejamos un pequeño margen de seguridad
                row_height = max(2.5, min(4.0, (remaining_space - 5) / num_partidos))
                
                # Datos de la tabla - MOSTRAR TODOS LOS PARTIDOS
                for idx, row in tabla_partidos.iterrows():
                    # Color de fondo según condición
                    if row['Condición'] == 'Titular':
                        pdf.set_fill_color(int(PENYA_PRIMARY_COLOR[1:3], 16), int(PENYA_PRIMARY_COLOR[3:5], 16), int(PENYA_PRIMARY_COLOR[5:7], 16))
                        fill = True
                        pdf.set_text_color(0, 0, 0)  # Texto negro sobre naranja
                    else:
                        pdf.set_fill_color(int(PENYA_SECONDARY_COLOR[1:3], 16), int(PENYA_SECONDARY_COLOR[3:5], 16), int(PENYA_SECONDARY_COLOR[5:7], 16))
                        fill = True
                        pdf.set_text_color(255, 255, 255)  # Texto blanco sobre negro
                    
                    x_pos = izq_x
                    pdf.set_xy(x_pos, pdf.get_y())
                    pdf.cell(col_widths[0], row_height, str(int(row['Jornada'])), 1, 0, 'C', fill)
                    x_pos += col_widths[0]
                    
                    pdf.set_xy(x_pos, pdf.get_y())
                    # Truncar rival si es muy largo para evitar problemas de espacio
                    rival_text = str(row['Rival'])
                    if len(rival_text) > 16:
                        rival_text = rival_text[:15] + "."
                    pdf.cell(col_widths[1], row_height, rival_text, 1, 0, 'L', fill)
                    x_pos += col_widths[1]
                    
                    pdf.set_xy(x_pos, pdf.get_y())
                    pdf.cell(col_widths[2], row_height, str(row['Condición']), 1, 0, 'C', fill)
                    x_pos += col_widths[2]
                    
                    pdf.set_xy(x_pos, pdf.get_y())
                    pdf.cell(col_widths[3], row_height, str(int(row['Minutos'])), 1, 0, 'C', fill)
                    pdf.ln(row_height)
                
                # Restaurar color de texto
                pdf.set_text_color(0, 0, 0)
        else:
            pdf.set_xy(izq_x, section_start_y + 40)
            pdf.set_font('Arial', '', 10)
            pdf.cell(85, 10, "No hay datos de minutos para este jugador", 0, 1, 'C')
        
        # ----- SECCIÓN DE GOLES/TARJETAS (DERECHA) -----
        pdf.set_xy(der_x, section_start_y)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(90, 8, "Goles/Tarjetas", 0, 1, 'L')
        
        # Verificar si hay goles o tarjetas
        tiene_goles = estadisticas['goles'] > 0
        tiene_tarjetas = estadisticas['tarjetas_amarillas'] > 0 or estadisticas['tarjetas_rojas'] > 0
        
        if tiene_goles or tiene_tarjetas:
            # Si hay goles, mostrar la tabla de goles
            if tiene_goles:
                # Posicionar para la tabla de goles
                pdf.set_xy(der_x, section_start_y + 10)
                pdf.set_font('Arial', 'B', 9)
                pdf.cell(90, 6, "Goles", 0, 1, 'L')
                
                # Filtrar goles del jugador
                goles_jugador = goles_df[goles_df['jugador'] == jugador_seleccionado].copy()
                
                # Añadir información de rivales
                jugador_actas = actas_df[actas_df['jugador'] == jugador_seleccionado]
                jornada_rival = dict(zip(jugador_actas['jornada'], jugador_actas['rival']))
                goles_jugador['Rival'] = goles_jugador['Jornada'].map(jornada_rival)
                
                # Crear tabla de goles
                if not goles_jugador.empty:
                    goles_tabla = goles_jugador[['Jornada', 'Minuto', 'Tipo de Gol', 'Rival']]
                    goles_tabla = goles_tabla.sort_values('Jornada')
                    
                    # Cabecera de la tabla
                    pdf.set_xy(der_x, section_start_y + 17)
                    pdf.set_font('Arial', 'B', 8)
                    cols_ancho = [15, 15, 30, 25]  # Ancho de las columnas
                    headers = ['Jornada', 'Minuto', 'Tipo de Gol', 'Rival']
                    
                    # Dibujar cabecera
                    x_pos = der_x
                    for i, header in enumerate(headers):
                        pdf.set_xy(x_pos, pdf.get_y())
                        pdf.cell(cols_ancho[i], 6, header, 1, 0, 'C')
                        x_pos += cols_ancho[i]
                    pdf.ln()
                    
                    # Contenido de la tabla - Mostrar todos los goles
                    pdf.set_font('Arial', '', 7)
                    for _, row in goles_tabla.iterrows():
                        x_pos = der_x
                        for i, col in enumerate(['Jornada', 'Minuto', 'Tipo de Gol', 'Rival']):
                            pdf.set_xy(x_pos, pdf.get_y())
                            # Asegurar que los valores de jornada y minuto sean enteros
                            valor = row[col]
                            if col in ['Jornada', 'Minuto'] and isinstance(valor, (int, float)):
                                valor = int(valor)
                            pdf.cell(cols_ancho[i], 6, str(valor), 1, 0, 'L')
                            x_pos += cols_ancho[i]
                        pdf.ln()
            
            # Si hay tarjetas, mostrar la tabla de tarjetas
            if tiene_tarjetas:
                # Determinar posición Y basada en si hay goles
                if tiene_goles:
                    # Posicionar debajo de la tabla de goles dejando espacio
                    tarjetas_y = pdf.get_y() + 5
                else:
                    tarjetas_y = section_start_y + 10
                
                pdf.set_xy(der_x, tarjetas_y)
                pdf.set_font('Arial', 'B', 9)
                pdf.cell(90, 6, "Tarjetas", 0, 1, 'L')
                
                # Aplicar ajuste de tarjetas
                actas_ajustadas = ajustar_tarjetas_por_doble_amarilla(actas_df)
                
                # Filtrar las actas del jugador
                actas_jugador = actas_ajustadas[actas_ajustadas['jugador'] == jugador_seleccionado].copy()
                
                # Crear una lista para almacenar las tarjetas
                tarjetas_temp = []
                
                # Procesar tarjetas amarillas (después del ajuste)
                for _, row in actas_jugador[actas_jugador['Tarjetas Amarillas'] > 0].iterrows():
                    tarjetas_temp.append({
                        'Jornada': int(row['jornada']),  # Convertir a entero
                        'Tipo': 'Amarilla',
                        'Rival': row['rival'],
                        'Doble Amarilla': '-'
                    })
                
                # Procesar tarjetas rojas
                for _, row in actas_jugador[actas_jugador['Tarjetas Rojas'] > 0].iterrows():
                    # Verificar si es una tarjeta roja directa o por doble amarilla
                    jornada = int(row['jornada'])  # Convertir a entero
                    
                    # Comprobar si esta roja proviene de una doble amarilla
                    actas_original = actas_df[
                        (actas_df['jugador'] == jugador_seleccionado) & 
                        (actas_df['jornada'] == jornada)
                    ]
                    
                    amarillas_originales = actas_original['Tarjetas Amarillas'].sum() if not actas_original.empty else 0
                    es_por_doble_amarilla = amarillas_originales >= 2 and row['Tarjetas Amarillas'] < amarillas_originales
                    
                    # Añadir tarjetas rojas a la lista
                    for i in range(int(row['Tarjetas Rojas'])):
                        doble_amarilla = 'Si' if (i == 0 and es_por_doble_amarilla) else 'No'
                        tarjetas_temp.append({
                            'Jornada': jornada,
                            'Tipo': 'Roja',
                            'Rival': row['rival'],
                            'Doble Amarilla': doble_amarilla
                        })
                
                # Crear DataFrame y tabla
                if tarjetas_temp:
                    tarjetas_df = pd.DataFrame(tarjetas_temp)
                    tarjetas_df = tarjetas_df.sort_values('Jornada')
                    
                    # Cabecera de la tabla
                    pdf.set_xy(der_x, tarjetas_y + 7)
                    pdf.set_font('Arial', 'B', 8)
                    cols_ancho = [15, 15, 25, 30]  # Ancho de las columnas
                    headers = ['Jornada', 'Tipo', 'Doble Amarilla', 'Rival']
                    
                    # Dibujar cabecera
                    x_pos = der_x
                    for i, header in enumerate(headers):
                        pdf.set_xy(x_pos, pdf.get_y())
                        pdf.cell(cols_ancho[i], 6, header, 1, 0, 'C')
                        x_pos += cols_ancho[i]
                    pdf.ln()
                    
                    # Contenido de la tabla - Mostrar todas las tarjetas
                    pdf.set_font('Arial', '', 7)
                    for _, row in tarjetas_df.iterrows():
                        x_pos = der_x
                        for i, col in enumerate(['Jornada', 'Tipo', 'Doble Amarilla', 'Rival']):
                            pdf.set_xy(x_pos, pdf.get_y())
                            # Formato especial para la columna Tipo
                            if col == 'Tipo':
                                # Determinar color según tipo de tarjeta
                                if row['Tipo'] == 'Amarilla':
                                    color_rgb = (int(COLOR_TARJETAS_AMARILLAS[1:3], 16), 
                                               int(COLOR_TARJETAS_AMARILLAS[3:5], 16), 
                                               int(COLOR_TARJETAS_AMARILLAS[5:7], 16))
                                    pdf.set_text_color(0, 0, 0)  # Texto negro para tarjeta amarilla
                                else:  # Roja
                                    color_rgb = (int(COLOR_TARJETAS_ROJAS[1:3], 16), 
                                               int(COLOR_TARJETAS_ROJAS[3:5], 16),
                                               int(COLOR_TARJETAS_ROJAS[5:7], 16))
                                    pdf.set_text_color(255, 255, 255)  # Texto blanco para tarjeta roja
                                
                                # Establecer color de fondo
                                pdf.set_fill_color(color_rgb[0], color_rgb[1], color_rgb[2])
                                pdf.cell(cols_ancho[i], 6, str(row[col]), 1, 0, 'C', 1)
                                
                                # Restaurar color de texto negro para las siguientes columnas
                                pdf.set_text_color(0, 0, 0)
                            else:
                                # Asegurar que los valores numéricos se muestran correctamente
                                valor = row[col]
                                if col == 'Jornada' and isinstance(valor, (int, float)):
                                    valor = int(valor)
                                pdf.cell(cols_ancho[i], 6, str(valor), 1, 0, 'L')
                            x_pos += cols_ancho[i]
                        pdf.ln()
        else:
            # Si no hay goles ni tarjetas, mostrar mensaje informativo
            pdf.set_xy(der_x, section_start_y + 40)
            pdf.set_font('Arial', '', 10)
            pdf.cell(85, 10, "Este jugador no ha marcado goles ni", 0, 1, 'C')
            pdf.set_xy(der_x, pdf.get_y())
            pdf.cell(85, 10, "recibido tarjetas en la temporada.", 0, 1, 'C')
        
        return pdf
    except Exception as e:
        print(f"Error al generar el PDF del jugador: {str(e)}")
        # Crear un PDF simple con mensaje de error
        pdf = PenyaPDF(title=f"Error al generar análisis - {jugador_seleccionado}")
        pdf.set_y(50)
        pdf.set_font('Arial', 'B', 12)
        pdf.multi_cell(0, 10, f"Se produjo un error al generar el PDF: {str(e)}", 0, 'C')
        return pdf