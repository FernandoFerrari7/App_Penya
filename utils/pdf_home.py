"""
Funciones específicas para la generación de PDF de la página de inicio
"""
from utils.pdf_export import PenyaPDF

def generate_home_pdf(data):
    """
    Genera un PDF con el análisis general del equipo
    """
    try:
        from calculos.calculo_equipo import calcular_estadisticas_generales, calcular_goles_contra
        from calculos.calculo_jugadores import (
            obtener_top_goleadores,
            obtener_top_amonestados,
            obtener_jugadores_mas_minutos
        )
        from visualizaciones.jugadores_home import (
            graficar_top_goleadores_home,
            graficar_top_amonestados_home,
            graficar_minutos_jugados_home
        )

        # Inicializar PDF
        pdf = PenyaPDF(title="Análisis General - Penya Independent")
        pdf.set_auto_page_break(auto=True, margin=15)

        # Calcular estadísticas generales
        estadisticas = calcular_estadisticas_generales(
            data['actas_penya'],
            data['goles_penya'],
            data['partidos_penya'],
            "PENYA INDEPENDENT"
        )
        
        # Usar los goles recibidos que se pasaron desde home.py o calcularlos si no están
        if 'goles_recibidos' in data:
            goles_recibidos = data['goles_recibidos']
        else:
            # Calcular goles en contra como fallback
            equipo_objetivo = "PENYA INDEPENDENT A"
            try:
                goles_recibidos = calcular_goles_contra(
                    data['actas_penya'], 
                    data['partidos_penya'],
                    data['actas'],
                    equipo_seleccionado=equipo_objetivo
                )
            except Exception as e:
                print(f"Error al calcular goles en contra: {e}")
                goles_recibidos = 0

        # Añadir métricas básicas incluyendo goles recibidos
        metricas = [
            ('Partidos Jugados', estadisticas['partidos_jugados']),
            ('Goles Marcados', estadisticas['goles_marcados']),
            ('Goles Recibidos', goles_recibidos),
            ('Tarjetas Amarillas', estadisticas['tarjetas_amarillas']),
            ('Tarjetas Rojas', estadisticas['tarjetas_rojas'])
        ]
        
        # Posicionar después del encabezado
        pdf.set_y(35) 
        pdf.add_metrics_row(metricas)

        # Título de la sección de jugadores
        pdf.ln(10)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, "Análisis de Jugadores", 0, 1, 'L')
        pdf.ln(5)

        # Preparar los gráficos
        top_goleadores = obtener_top_goleadores(data['actas_penya'], top_n=5)
        top_amonestados = obtener_top_amonestados(data['actas_penya'], top_n=5)
        top_minutos = obtener_jugadores_mas_minutos(data['actas_penya'], top_n=5)
        
        # Primera fila de gráficos
        current_y = pdf.get_y()
        
        # Gráfico de goleadores (primera fila, izquierda)
        if not top_goleadores.empty:
            fig_goleadores = graficar_top_goleadores_home(top_goleadores, return_fig=True)
            if fig_goleadores:
                pdf.add_plot(fig_goleadores, x=15, y=current_y, w=90)  
        
        # Gráfico de amonestados (primera fila, derecha)
        if not top_amonestados.empty:
            fig_amonestados = graficar_top_amonestados_home(top_amonestados, return_fig=True)
            if fig_amonestados:
                pdf.add_plot(fig_amonestados, x=110, y=current_y, w=90) 
        
        # Segunda fila - Gráfico de minutos jugados
        current_y = pdf.get_y() + 15  
        
        if not top_minutos.empty:
            fig_minutos = graficar_minutos_jugados_home(top_minutos, return_fig=True)
            if fig_minutos:
                pdf.add_plot(fig_minutos, x=55, y=current_y, w=100)  # Gráfico centrado

        return pdf
    except Exception as e:
        print(f"Error al generar el PDF: {str(e)}")
        raise e