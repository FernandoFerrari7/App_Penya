"""
Funciones específicas para la generación de PDF del análisis comparativo
"""
from utils.pdf_export import PenyaPDF
from utils.constants import PENYA_PRIMARY_COLOR, PENYA_SECONDARY_COLOR

def generate_ml_pdf(data, equipo_seleccionado, datos_clustered, caracteristicas_clusters, mapa_fig, comparativa_fig=None):
    """
    Genera un PDF con el análisis comparativo de equipos
    
    Args:
        data: Diccionario con todos los datos necesarios
        equipo_seleccionado: Nombre del equipo seleccionado para análisis
        datos_clustered: DataFrame con los datos clusterizados
        caracteristicas_clusters: Diccionario con las características de cada cluster
        mapa_fig: Figura de plotly con el mapa de equipos
        comparativa_fig: Figura de plotly con la comparativa (puede ser None)
        
    Returns:
        PenyaPDF: Objeto PDF generado
    """
    try:
        # Inicializar PDF
        pdf = PenyaPDF(title=f"Análisis Comparativo - {equipo_seleccionado}")
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Obtener datos del equipo seleccionado
        equipo_data = datos_clustered[datos_clustered['equipo_limpio'] == equipo_seleccionado].iloc[0]
        cluster_id = int(equipo_data['cluster'])
        
        # Datos del cluster al que pertenece el equipo
        cluster_info = caracteristicas_clusters[cluster_id]
        
        # Encontrar Penya Independent para comparación
        penya_data = datos_clustered[datos_clustered['equipo_limpio'].str.contains('PENYA INDEPENDENT', case=False)]
        
        if not penya_data.empty:
            penya_row = penya_data.iloc[0]
            penya_nombre = penya_row['equipo_limpio']
            penya_cluster = int(penya_row['cluster'])
        else:
            penya_nombre = "PENYA INDEPENDENT"
            penya_cluster = 0
        
        # Posicionarse después del encabezado
        pdf.set_y(35)
        
        # Sección 1: Mapa de equipos
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, "Análisis de similitud de equipos", 0, 1, 'L')
        
        # NUEVA SECCIÓN: Asegurarse de preservar los colores en el mapa
        # Si los colores de cluster están disponibles en data, aplicarlos a la figura
        if 'cluster_colors' in data:
            # Definir colores para cada cluster
            colores_cluster = data['cluster_colors']
            
            # Asegurarse de que cada trace tenga el color correspondiente
            for trace in mapa_fig.data:
                # Si el nombre del trace incluye "Grupo X", asignar el color correspondiente
                for i, color in enumerate(colores_cluster):
                    if f"Grupo {i+1}" in trace.name:
                        if hasattr(trace, 'marker'):
                            trace.marker.color = color
                
                # Asegurarse de que Penya Independent tenga el color naranja característico
                if trace.name == 'Penya Independent':
                    if hasattr(trace, 'marker'):
                        trace.marker.color = PENYA_PRIMARY_COLOR
                        trace.marker.symbol = "star"
        
        # Agregar el gráfico de dispersión con dimensiones ampliadas para mejor legibilidad
        pdf.add_plot(mapa_fig, x=10, y=None, w=180, h=120) 
        
        # Añadir separador
        pdf.ln(5)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        
        # Sección 2: Análisis del equipo seleccionado
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, f"Análisis de {equipo_seleccionado}", 0, 1, 'L')
        
        # Información del equipo y cluster
        pdf.set_font('Arial', 'B', 10)
        pdf.multi_cell(0, 6, f"{equipo_seleccionado} pertenece al Grupo {cluster_id}", 0, 'L')
        pdf.ln(3)
        
        # Crear dos columnas para la información
        col_width = 90
        left_column_x = 10
        right_column_x = 105
        
        # Columna izquierda: Características del grupo y equipos similares
        pdf.set_xy(left_column_x, pdf.get_y())
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(col_width, 6, "Características del grupo:", 0, 1, 'L')
        
        pdf.set_xy(left_column_x, pdf.get_y())
        pdf.set_font('Arial', '', 9)
        
        # Mostrar características del cluster
        if cluster_info['descripcion']:
            for desc in cluster_info['descripcion']:
                pdf.set_x(left_column_x + 5)  # Sangría para los bullets
                pdf.multi_cell(col_width - 5, 5, f"- {desc}", 0, 'L')  # Reemplazado • por -
        else:
            pdf.set_x(left_column_x + 5)
            pdf.multi_cell(col_width - 5, 5, "No se identificaron características distintivas", 0, 'L')
        
        # Equipos similares
        pdf.ln(3)
        pdf.set_x(left_column_x)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(col_width, 6, "Equipos similares:", 0, 1, 'L')
        
        pdf.set_font('Arial', '', 9)
        equipos_similares = [e for e in cluster_info['equipos'] if e != equipo_seleccionado][:5]  # Mostrar solo 5
        
        if equipos_similares:
            for equipo in equipos_similares:
                pdf.set_x(left_column_x + 5)  # Sangría para los bullets
                pdf.multi_cell(col_width - 5, 5, f"- {equipo}", 0, 'L')  # Reemplazado • por -
        else:
            pdf.set_x(left_column_x + 5)
            pdf.multi_cell(col_width - 5, 5, "No se encontraron otros equipos en el mismo grupo", 0, 'L')
        
        # Columna derecha: Comparativa con Penya Independent
        current_y = pdf.get_y()
        if 'PENYA INDEPENDENT' not in equipo_seleccionado.upper():
            pdf.set_xy(right_column_x, current_y - 65)  # Ajustar según sea necesario
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(col_width, 6, "Comparativa con Penya Independent:", 0, 1, 'L')
            
            pdf.set_xy(right_column_x, pdf.get_y())
            pdf.set_font('Arial', '', 9)
            
            # Indicar si están en el mismo grupo
            if penya_cluster == cluster_id:
                pdf.multi_cell(col_width, 5, f"{equipo_seleccionado} y {penya_nombre} pertenecen al mismo grupo táctico (Grupo {cluster_id})", 0, 'L')
            else:
                pdf.multi_cell(col_width, 5, f"{equipo_seleccionado} (Grupo {cluster_id}) y {penya_nombre} (Grupo {penya_cluster}) pertenecen a diferentes grupos tácticos", 0, 'L')
            
            # Diferencias clave
            pdf.ln(3)
            pdf.set_x(right_column_x)
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(col_width, 6, "Diferencias clave:", 0, 1, 'L')
            
            pdf.set_font('Arial', '', 9)
            
            diferencias = []
            for metrica, col in [('Goles a favor', 'goles'), ('Goles en contra', 'goles_contra'), 
                               ('Tarjetas', 'Tarjetas Amarillas'), ('Jugadores', 'jugador'), 
                               ('Sustituciones', 'total_sustituciones')]:
                if col in equipo_data and col in penya_row:
                    valor1 = equipo_data[col]
                    valor2 = penya_row[col]
                    
                    if valor2 != 0:
                        diff_pct = ((valor1 - valor2) / valor2) * 100
                    else:
                        diff_pct = 0 if valor1 == 0 else 100
                    
                    if abs(diff_pct) > 15:  # Solo mostrar diferencias significativas
                        if diff_pct > 0:
                            diferencias.append(f"{metrica}: {abs(diff_pct):.1f}% más")
                        else:
                            diferencias.append(f"{metrica}: {abs(diff_pct):.1f}% menos")
            
            if diferencias:
                for diff in diferencias:
                    pdf.set_x(right_column_x + 5)  # Sangría para los bullets
                    pdf.multi_cell(col_width - 5, 5, f"- {diff}", 0, 'L')  
            else:
                pdf.set_x(right_column_x + 5)
                pdf.multi_cell(col_width - 5, 5, "No se encontraron diferencias significativas", 0, 'L')
            
            # Gráfico comparativo
            if comparativa_fig is not None:
                pdf.ln(5)
                pdf.add_plot(comparativa_fig, x=right_column_x, y=None, w=col_width)
        else:
            # Si el equipo seleccionado es Penya, mostrar un mensaje
            pdf.set_xy(right_column_x, current_y - 65)  
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(col_width, 6, "Información:", 0, 1, 'L')
            
            pdf.set_xy(right_column_x, pdf.get_y())
            pdf.set_font('Arial', '', 9)
            pdf.multi_cell(col_width, 5, "Este es el análisis de Penya Independent, por lo que no se realiza comparación consigo mismo.", 0, 'L')
        
        return pdf
    except Exception as e:
        print(f"Error al generar el PDF del análisis comparativo: {str(e)}")
        # Crear un PDF simple con mensaje de error
        pdf = PenyaPDF(title=f"Error al generar análisis - {equipo_seleccionado}")
        pdf.set_y(50)
        pdf.set_font('Arial', 'B', 12)
        pdf.multi_cell(0, 10, f"Se produjo un error al generar el PDF: {str(e)}", 0, 'C')
        return pdf