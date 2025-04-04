"""
Utilidades para exportar datos a PDF
"""
import os
import pandas as pd
import streamlit as st
from fpdf import FPDF
import tempfile
import base64
import matplotlib.pyplot as plt
from pathlib import Path
import time
from PIL import Image
import io
from utils.constants import PENYA_PRIMARY_COLOR, PENYA_SECONDARY_COLOR, COLOR_TARJETAS_AMARILLAS, COLOR_TARJETAS_ROJAS
from calculos.calculo_minutos import obtener_minutos_por_jornada
from visualizaciones.minutos import graficar_minutos_por_jugador
from visualizaciones.jugadores import graficar_minutos_por_jornada, graficar_goles_por_tiempo, graficar_tarjetas_por_jornada

class PenyaPDF(FPDF):
    """
    Clase personalizada para generar PDFs con el estilo de Penya Independent
    """
    def __init__(self, title="Análisis Penya Independent"):
        super().__init__()
        self.title = title
        self.add_page()
        self.set_font('Arial', '', 12)
        
    def header(self):
        """
        Encabezado del PDF con logos y título
        """
        try:
            # Obtener la ruta base del proyecto
            base_path = Path(__file__).parent.parent
            
            # Construir rutas absolutas para los logos
            penya_logo = base_path / "assets" / "logo_penya.png"
            ffib_logo = base_path / "assets" / "logo_ffib.png"
            
            # Verificar y convertir las imágenes si es necesario
            logo_width = 25
            
            if penya_logo.exists():
                try:
                    # Abrir y verificar la imagen con PIL
                    with Image.open(str(penya_logo)) as img_penya:
                        # Convertir a RGB si es necesario
                        if img_penya.mode != 'RGB':
                            img_penya = img_penya.convert('RGB')
                        # Guardar en un buffer de memoria
                        img_buffer = io.BytesIO()
                        img_penya.save(img_buffer, format='PNG')
                        img_buffer.seek(0)
                        # Guardar temporalmente
                        temp_penya = os.path.join(tempfile.gettempdir(), f'penya_logo_{time.time_ns()}.png')
                        with open(temp_penya, 'wb') as f:
                            f.write(img_buffer.getvalue())
                        self.image(temp_penya, 10, 8, logo_width)
                        # Limpiar
                        os.unlink(temp_penya)
                except Exception as e:
                    print(f"Error al procesar logo_penya.png: {e}")
            
            if ffib_logo.exists():
                try:
                    # Abrir y verificar la imagen con PIL
                    with Image.open(str(ffib_logo)) as img_ffib:
                        # Convertir a RGB si es necesario
                        if img_ffib.mode != 'RGB':
                            img_ffib = img_ffib.convert('RGB')
                        # Guardar en un buffer de memoria
                        img_buffer = io.BytesIO()
                        img_ffib.save(img_buffer, format='PNG')
                        img_buffer.seek(0)
                        # Guardar temporalmente
                        temp_ffib = os.path.join(tempfile.gettempdir(), f'ffib_logo_{time.time_ns()}.png')
                        with open(temp_ffib, 'wb') as f:
                            f.write(img_buffer.getvalue())
                        self.image(temp_ffib, 175, 8, logo_width)
                        # Limpiar
                        os.unlink(temp_ffib)
                except Exception as e:
                    print(f"Error al procesar logo_ffib.png: {e}")
                
            # Título centrado
            self.set_font('Arial', 'B', 15)
            self.set_xy(35, 8)
            self.cell(140, 10, self.title, 0, 1, 'C')
            self.line(10, 25, 200, 25)
            self.ln(5)
            
        except Exception as e:
            print(f"Error en el encabezado: {e}")
            # Asegurar que al menos el título se muestre
            self.set_font('Arial', 'B', 15)
            self.cell(0, 10, self.title, 0, 1, 'C')
            self.line(10, 25, 200, 25)
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

    def add_metrics_row(self, metrics):
        """
        Añade una fila de métricas al PDF
        
        Args:
            metrics: Lista de tuplas (título, valor)
        """
        # Calcular ancho de cada métrica
        metric_width = 190 / len(metrics)
        
        # Añadir cada métrica
        for title, value in metrics:
            # Título
            self.set_font('Arial', '', 10)
            self.cell(metric_width, 6, title, 0, 0, 'C')
        self.ln()
        
        # Valores
        for title, value in metrics:
            self.set_font('Arial', 'B', 14)
            self.cell(metric_width, 8, str(value), 0, 0, 'C')
        self.ln(15)
    
    def add_plot(self, fig, x=10, y=None, w=None, h=None):
        """
        Añade un gráfico al PDF, soporta tanto figuras de matplotlib como de plotly
        
        Args:
            fig: Figura (matplotlib o plotly)
            x: Posición x
            y: Posición y (opcional)
            w: Ancho (opcional)
            h: Alto (opcional, se calcula automáticamente si no se especifica)
        """
        # Si la figura es None, no hacer nada
        if fig is None:
            return
        
        try:
            import tempfile
            import os
            
            # Crear un archivo temporal
            temp_fd, temp_path = tempfile.mkstemp(suffix='.png')
            os.close(temp_fd)
            
            try:
                # Detectar el tipo de figura y guardarla apropiadamente
                if 'plotly' in str(type(fig)):
                    # Es una figura de Plotly
                    fig.write_image(temp_path, format="png")
                else:
                    # Es una figura de matplotlib
                    fig.savefig(temp_path, format='png', bbox_inches='tight', dpi=300)
                    plt.close(fig)
                
                # Abrir la imagen para obtener sus dimensiones
                img = Image.open(temp_path)
                
                # Si no se especifica el alto, calcularlo manteniendo la proporción
                if h is None and w is not None:
                    aspect_ratio = img.height / img.width
                    h = w * aspect_ratio
                
                # Añadir la imagen al PDF
                if y is None:
                    y = self.get_y()
                self.image(temp_path, x=x, y=y, w=w, h=h)
                
                # Actualizar la posición Y
                if h:
                    self.set_y(y + h + 5)
                
            finally:
                # Limpiar: cerrar la imagen y eliminar el archivo temporal
                try:
                    img.close()
                except:
                    pass
                try:
                    os.unlink(temp_path)
                except:
                    pass
            
        except Exception as e:
            print(f"Error al añadir gráfico al PDF: {str(e)}")
            # No levantar la excepción para continuar con el resto del PDF
            pass


def generate_home_pdf(data):
    """
    Genera un PDF con el análisis general del equipo
    """
    try:
        from calculos.calculo_equipo import calcular_estadisticas_generales
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

        # Añadir métricas básicas
        metricas = [
            ('Partidos Jugados', estadisticas['partidos_jugados']),
            ('Goles Marcados', estadisticas['goles_marcados']),
            ('Tarjetas Amarillas', estadisticas['tarjetas_amarillas']),
            ('Tarjetas Rojas', estadisticas['tarjetas_rojas'])
        ]
        pdf.add_metrics_row(metricas)

        # Título de la sección de jugadores
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, "Análisis de Jugadores", 0, 1, 'L')
        pdf.ln(2)

        # Preparar y añadir los gráficos
        current_y = pdf.get_y()

        # Gráfico de goleadores
        top_goleadores = obtener_top_goleadores(data['actas_penya'], top_n=5)
        if not top_goleadores.empty:
            fig_goleadores = graficar_top_goleadores_home(top_goleadores, return_fig=True)
            if fig_goleadores:
                pdf.add_plot(fig_goleadores, x=10, y=current_y, w=60)

        # Gráfico de amonestados
        top_amonestados = obtener_top_amonestados(data['actas_penya'], top_n=5)
        if not top_amonestados.empty:
            fig_amonestados = graficar_top_amonestados_home(top_amonestados, return_fig=True)
            if fig_amonestados:
                pdf.add_plot(fig_amonestados, x=75, y=current_y, w=60)

        # Gráfico de minutos jugados
        top_minutos = obtener_jugadores_mas_minutos(data['actas_penya'], top_n=5)
        if not top_minutos.empty:
            fig_minutos = graficar_minutos_jugados_home(top_minutos, return_fig=True)
            if fig_minutos:
                pdf.add_plot(fig_minutos, x=140, y=current_y, w=60)

        return pdf
    except Exception as e:
        print(f"Error al generar el PDF: {str(e)}")
        raise e


def generate_equipo_pdf(data, equipo_seleccionado):
    """
    Genera un PDF con el análisis del equipo seleccionado
    """
    try:
        from calculos.calculo_equipo import (
            calcular_estadisticas_generales, calcular_metricas_avanzadas,
            obtener_rivales_con_goles, analizar_tarjetas_por_jornada,
            analizar_tipos_goles, calcular_goles_contra,
            calcular_tarjetas_rivales
        )
        from calculos.calculo_jugadores import (
            obtener_top_goleadores, obtener_top_amonestados,
            analizar_goles_por_tiempo, analizar_minutos_por_jugador
        )
        from visualizaciones.equipo import (
            graficar_tarjetas_por_jornada, graficar_tipos_goles,
            graficar_goles_por_tiempo
        )
        from visualizaciones.minutos import graficar_minutos_por_jugador

        # Inicializar PDF
        pdf = PenyaPDF(title=f"Análisis del Equipo - {equipo_seleccionado}")
        pdf.set_auto_page_break(auto=True, margin=15)

        # Filtrar datos del equipo
        datos_equipo = {}
        datos_equipo['actas'] = data['actas']
        datos_equipo['actas_penya'] = data['actas'][data['actas']['equipo'].str.contains(equipo_seleccionado, na=False)]
        datos_equipo['goles_penya'] = data['goles'][data['goles']['equipo'].str.contains(equipo_seleccionado, na=False)]
        datos_equipo['partidos_penya'] = data['jornadas'][
            (data['jornadas']['equipo_local'].str.contains(equipo_seleccionado, na=False)) | 
            (data['jornadas']['equipo_visitante'].str.contains(equipo_seleccionado, na=False))
        ]

        # Calcular estadísticas
        estadisticas = calcular_estadisticas_generales(
            datos_equipo['actas_penya'], 
            datos_equipo['goles_penya'], 
            datos_equipo['partidos_penya'],
            equipo_seleccionado
        )

        # Calcular métricas avanzadas
        metricas = []
        
        # Goles a favor
        metricas.append({
            'titulo': 'Goles a favor',
            'valor': estadisticas['goles_marcados'],
            'referencia': data['medias_liga']['ref_goles_favor']
        })
        
        # Goles en contra
        goles_contra = calcular_goles_contra(
            datos_equipo['actas_penya'], 
            datos_equipo['partidos_penya'],
            datos_equipo['actas'],
            equipo_seleccionado
        )
        metricas.append({
            'titulo': 'Goles en contra',
            'valor': goles_contra,
            'referencia': data['medias_liga']['ref_goles_contra']
        })
        
        # Tarjetas amarillas propias
        metricas.append({
            'titulo': 'TA Propias',
            'valor': estadisticas['tarjetas_amarillas'],
            'referencia': data['medias_liga']['ref_tarjetas_amarillas']
        })
        
        # Tarjetas rojas propias
        metricas.append({
            'titulo': 'TR Propias',
            'valor': estadisticas['tarjetas_rojas'],
            'referencia': data['medias_liga']['ref_tarjetas_rojas']
        })
        
        # Tarjetas rivales
        tarjetas_rivales = calcular_tarjetas_rivales(
            datos_equipo['actas'],
            datos_equipo['partidos_penya'],
            equipo_seleccionado
        )
        metricas.append({
            'titulo': 'TA Rival',
            'valor': tarjetas_rivales['amarillas'],
            'referencia': data['medias_liga']['ref_ta_rival']
        })
        metricas.append({
            'titulo': 'TR Rival',
            'valor': tarjetas_rivales['rojas'],
            'referencia': data['medias_liga']['ref_tr_rival']
        })

        # Añadir métricas al PDF
        pdf.set_y(30)
        for metrica in metricas:
            pdf.add_metrics_row([
                (metrica['titulo'], f"{metrica['valor']} ({metrica['referencia']})")
            ])

        # Título de la sección de gráficos
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, "Análisis de Rendimiento", 0, 1, 'L')
        pdf.ln(2)

        # Preparar y añadir los gráficos
        current_y = pdf.get_y()
        
        # Gráfico de tarjetas por jornada
        tarjetas_jornada = analizar_tarjetas_por_jornada(datos_equipo['actas_penya'])
        if not tarjetas_jornada.empty:
            fig_tarjetas = graficar_tarjetas_por_jornada(tarjetas_jornada, return_fig=True)
            if fig_tarjetas:
                pdf.add_plot(fig_tarjetas, x=10, y=current_y, w=85)

        # Gráfico de tipos de goles
        tipos_goles = analizar_tipos_goles(datos_equipo['goles_penya'])
        if not tipos_goles.empty:
            fig_tipos_goles = graficar_tipos_goles(tipos_goles, return_fig=True)
            if fig_tipos_goles:
                pdf.add_plot(fig_tipos_goles, x=105, y=current_y, w=85)

        # Nueva página para análisis de jugadores
        pdf.add_page()
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, "Análisis de Jugadores", 0, 1, 'L')
        pdf.ln(2)

        current_y = pdf.get_y()

        # Gráfico de minutos por jugador
        minutos_jugador = analizar_minutos_por_jugador(datos_equipo['actas_penya'])
        if not minutos_jugador.empty:
            fig_minutos = graficar_minutos_por_jugador(minutos_jugador.head(10), return_fig=True)
            if fig_minutos:
                pdf.add_plot(fig_minutos, x=10, y=current_y, w=190)

        return pdf
    except Exception as e:
        print(f"Error al generar el PDF: {str(e)}")
        raise e


def generate_jugador_pdf(data, jugador_seleccionado):
    """
    Genera un PDF con el análisis del jugador seleccionado
    """
    try:
        from calculos.calculo_jugadores import (
            calcular_estadisticas_jugador,
            analizar_goles_por_tiempo
        )
        from visualizaciones.jugadores import (
            graficar_minutos_por_jornada,
            graficar_goles_por_tiempo,
            graficar_tarjetas_por_jornada
        )

        # Inicializar PDF
        pdf = PenyaPDF(title=f"Análisis del Jugador - {jugador_seleccionado}")
        pdf.set_auto_page_break(auto=True, margin=15)

        # Filtrar datos del jugador
        actas_jugador = data['actas_penya'][data['actas_penya']['jugador'] == jugador_seleccionado]
        goles_jugador = data['goles_penya'][data['goles_penya']['jugador'] == jugador_seleccionado]

        # Calcular estadísticas del jugador
        estadisticas = calcular_estadisticas_jugador(
            data['actas_penya'],
            jugador_seleccionado
        )

        # Añadir métricas básicas
        metricas = [
            ('Partidos Jugados', estadisticas['partidos_jugados']),
            ('Minutos Jugados', estadisticas['minutos_jugados']),
            ('Goles Marcados', estadisticas['goles']),
            ('Tarjetas Amarillas', estadisticas['tarjetas_amarillas']),
            ('Tarjetas Rojas', estadisticas['tarjetas_rojas'])
        ]
        pdf.set_y(30)
        pdf.add_metrics_row(metricas[:3])  # Primera fila
        pdf.add_metrics_row(metricas[3:])  # Segunda fila

        # Título de la sección de gráficos
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, "Análisis de Rendimiento", 0, 1, 'L')
        pdf.ln(2)

        # Preparar y añadir los gráficos
        current_y = pdf.get_y()

        # Gráfico de minutos por jornada
        minutos_jornada = obtener_minutos_por_jornada(actas_jugador, jugador_seleccionado)
        if not minutos_jornada.empty:
            fig_minutos = graficar_minutos_por_jornada(minutos_jornada, return_fig=True)
            if fig_minutos:
                pdf.add_plot(fig_minutos, x=10, y=current_y, w=85)

        # Gráfico de goles por tiempo
        if not goles_jugador.empty:
            goles_tiempo = analizar_goles_por_tiempo(goles_jugador)
            if not goles_tiempo.empty:
                fig_goles = graficar_goles_por_tiempo(goles_tiempo, return_fig=True)
                if fig_goles:
                    pdf.add_plot(fig_goles, x=105, y=current_y, w=85)

        # Nueva página para más gráficos si es necesario
        pdf.add_page()

        # Gráfico de tarjetas
        tarjetas_temp = []
        for _, partido in actas_jugador.iterrows():
            jornada = partido['jornada']
            # Procesar tarjetas amarillas
            if partido['Tarjetas Amarillas'] > 0:
                tarjetas_temp.append({
                    'Jornada': jornada,
                    'Tipo': 'Amarilla',
                    'Color': COLOR_TARJETAS_AMARILLAS
                })
            # Procesar tarjetas rojas
            if partido['Tarjetas Rojas'] > 0:
                tarjetas_temp.append({
                    'Jornada': jornada,
                    'Tipo': 'Roja',
                    'Color': COLOR_TARJETAS_ROJAS
                })

        if tarjetas_temp:
            import pandas as pd
            tarjetas_df = pd.DataFrame(tarjetas_temp)
            tarjetas_df = tarjetas_df.sort_values('Jornada')
            fig_tarjetas = graficar_tarjetas_por_jornada(tarjetas_df, return_fig=True)
            if fig_tarjetas:
                pdf.add_plot(fig_tarjetas, x=10, y=30, w=190)

        return pdf
    except Exception as e:
        print(f"Error al generar el PDF: {str(e)}")
        raise e


def show_download_button(data, page_type, equipo_seleccionado=None, jugador_seleccionado=None):
    """
    Muestra un botón para descargar el PDF según el tipo de página y la selección
    """
    st.markdown("""
    <style>
    .btn-download {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background-color: #FF8C00;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        text-decoration: none;
        font-weight: 600;
        margin: 0.5rem 0;
        border: none;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }
    .btn-download:hover {
        background-color: #FF6B00;
        text-decoration: none;
    }
    </style>
    """, unsafe_allow_html=True)

    try:
        if page_type == 'home':
            pdf = generate_home_pdf(data)
            st.markdown(
                get_pdf_download_link(pdf, "penya_independent_analisis_rendimiento.pdf"), 
                unsafe_allow_html=True
            )
        elif page_type == 'equipo' and equipo_seleccionado:
            # Asegurarse de que el equipo seleccionado es válido
            if equipo_seleccionado in data['actas']['equipo'].unique():
                pdf = generate_equipo_pdf(data, equipo_seleccionado)
                # Limpiar el nombre del equipo para el archivo
                nombre_archivo = equipo_seleccionado.replace(" ", "_").replace("/", "_").lower()
                st.markdown(
                    get_pdf_download_link(pdf, f"analisis_equipo_{nombre_archivo}.pdf"), 
                    unsafe_allow_html=True
                )
            else:
                st.error("Por favor, selecciona un equipo válido")
        elif page_type == 'jugador' and jugador_seleccionado:
            pdf = generate_jugador_pdf(data, jugador_seleccionado)
            st.markdown(
                get_pdf_download_link(pdf, f"analisis_jugador_{jugador_seleccionado}.pdf"), 
                unsafe_allow_html=True
            )
        else:
            st.error("Tipo de página no válido o equipo/jugador no seleccionado")
    except Exception as e:
        st.error(f"Error al generar el PDF: {str(e)}")
        print(f"Error detallado: {e}")


def get_pdf_download_link(pdf, filename="informe.pdf"):
    temp_path = None
    try:
        # Crear archivo temporal para el PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            temp_path = tmp.name
        
        # Guardar el PDF
        pdf.output(temp_path)
        
        # Leer el archivo y convertirlo a base64
        with open(temp_path, 'rb') as file:
            pdf_bytes = file.read()
        
        # Generar el enlace de descarga
        b64_pdf = base64.b64encode(pdf_bytes).decode()
        href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{filename}" class="btn-download">⬇️ Descargar PDF</a>'
        return href
        
    except Exception as e:
        raise Exception(f"Error al generar el enlace de descarga: {str(e)}")
        
    finally:
        # Limpiar el archivo temporal
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception as e:
                print(f"No se pudo eliminar el archivo temporal {temp_path}: {e}")
