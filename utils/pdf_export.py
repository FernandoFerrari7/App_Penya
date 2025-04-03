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

class PenyaPDF(FPDF):
    """Clase personalizada de PDF para Penya Independent"""
    
    def __init__(self, title="Penya Independent - Análisis de Rendimiento", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = title
        self.add_page()
        
    def header(self):
        """Configurar el encabezado de cada página"""
        try:
            # Obtener la ruta base del proyecto
            base_path = Path(__file__).parent.parent
            
            # Construir rutas absolutas a los logos
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
                
            # Título centrado entre los logos
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

    def add_metrics_row(self, metrics, y_position=None):
        """Añade una fila de métricas en disposición horizontal"""
        if y_position:
            self.set_y(y_position)
            
        # Calcular el ancho disponible y el ancho por métrica
        page_width = 190
        metric_width = page_width / len(metrics)
        
        self.set_font('Arial', 'B', 11)
        for title, value in metrics:
            # Crear un rectángulo con borde suave
            x = self.get_x()
            y = self.get_y()
            
            # Título centrado arriba
            self.set_font('Arial', '', 9)
            self.set_xy(x, y)
            self.cell(metric_width, 6, title, 0, 0, 'C')
            
            # Valor en negrita abajo
            self.set_font('Arial', 'B', 12)
            self.set_xy(x, y + 6)
            self.cell(metric_width, 8, str(value), 0, 0, 'C')
            
            # Mover a la siguiente posición
            self.set_xy(x + metric_width, y)
            
        self.ln(16)  # Espacio después de la fila de métricas
        
    def add_plot(self, fig, x=None, y=None, w=None):
        """Añade un gráfico matplotlib al PDF"""
        try:
            # Crear un nombre único para el archivo temporal
            temp_filename = f'plot_{time.time_ns()}.png'
            temp_path = os.path.join(tempfile.gettempdir(), temp_filename)
            
            # Guardar la figura
            fig.savefig(temp_path, bbox_inches='tight', dpi=300, facecolor='white')
            plt.close(fig)  # Cerrar la figura inmediatamente
            
            # Si no se especifica el ancho, usar un tercio del ancho de página
            if w is None:
                w = 63  # Un tercio de 190
            
            # Calcular posición si no se especifica
            if x is None and y is None:  # Usar posición actual
                x = self.get_x()
                y = self.get_y()
            
            # Añadir la imagen al PDF
            self.image(temp_path, x=x, y=y, w=w)
            
            # Intentar eliminar el archivo temporal
            try:
                os.unlink(temp_path)
            except Exception as e:
                print(f"No se pudo eliminar el archivo temporal {temp_path}: {e}")
                
        except Exception as e:
            print(f"Error al añadir gráfico al PDF: {e}")


def generate_home_pdf(data):
    from calculos.calculo_equipo import calcular_estadisticas_generales, calcular_metricas_avanzadas, calcular_goles_contra
    from calculos.calculo_jugadores import obtener_top_goleadores, obtener_top_amonestados, obtener_jugadores_mas_minutos
    from visualizaciones.jugadores_home import graficar_top_goleadores_home, graficar_top_amonestados_home, graficar_minutos_jugados_home

    # Inicializar PDF
    pdf = PenyaPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Preparar datos
    actas_penya = data['actas_penya']
    goles_penya = data['goles_penya']
    partidos_penya = data['partidos_penya']
    actas_completas = data['actas']

    # Calcular estadísticas
    estadisticas = calcular_estadisticas_generales(
        actas_penya, 
        goles_penya, 
        partidos_penya, 
        equipo_seleccionado="PENYA INDEPENDENT A"
    )

    # Calcular goles recibidos
    try:
        metricas_avanzadas = calcular_metricas_avanzadas(
            partidos_penya, goles_penya, actas_penya, actas_completas,
            equipo_seleccionado="PENYA INDEPENDENT A"
        )
        goles_recibidos = metricas_avanzadas['goles'][1]['valor']
    except Exception:
        try:
            goles_recibidos = calcular_goles_contra(
                actas_penya, partidos_penya, actas_completas,
                equipo_seleccionado="PENYA INDEPENDENT A"
            )
        except Exception as e:
            print(f"Error al calcular goles en contra: {e}")
            goles_recibidos = "-"

    # Añadir métricas en dos filas
    pdf.set_y(30)
    pdf.add_metrics_row([
        ("PARTIDOS JUGADOS", estadisticas['partidos_jugados']),
        ("GOLES MARCADOS", estadisticas['goles_marcados']),
        ("GOLES RECIBIDOS", goles_recibidos)
    ])
    
    pdf.add_metrics_row([
        ("TARJETAS AMARILLAS", estadisticas['tarjetas_amarillas']),
        ("TARJETAS ROJAS", estadisticas['tarjetas_rojas']),
        ("", "")  # Espacio vacío para alineación
    ])

    # Título de la sección de gráficos
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "Análisis de Jugadores", 0, 1, 'L')
    pdf.ln(2)

    # Preparar y añadir los tres gráficos en una fila
    current_y = pdf.get_y()
    
    # Gráfico de goleadores
    top_goleadores = obtener_top_goleadores(actas_penya, top_n=5)
    fig_goleadores = graficar_top_goleadores_home(top_goleadores, return_fig=True)
    if fig_goleadores:
        pdf.add_plot(fig_goleadores, x=10, y=current_y)

    # Gráfico de amonestados
    top_amonestados = obtener_top_amonestados(actas_penya, top_n=5)
    fig_amonestados = graficar_top_amonestados_home(top_amonestados, return_fig=True)
    if fig_amonestados:
        pdf.add_plot(fig_amonestados, x=73, y=current_y)

    # Gráfico de minutos jugados
    top_minutos = obtener_jugadores_mas_minutos(actas_penya, top_n=5)
    fig_minutos = graficar_minutos_jugados_home(top_minutos, return_fig=True)
    if fig_minutos:
        pdf.add_plot(fig_minutos, x=136, y=current_y)

    return pdf


def generate_equipo_pdf(data, equipo_seleccionado):
    """
    Genera un PDF con el análisis del equipo seleccionado
    """
    from calculos.calculo_equipo import (
        calcular_estadisticas_generales, calcular_metricas_avanzadas,
        obtener_rivales_con_goles, analizar_tarjetas_por_jornada,
        analizar_tipos_goles, calcular_goles_contra
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
    actas_equipo = data['actas_penya'][data['actas_penya']['equipo'].str.contains(equipo_seleccionado, na=False)]
    goles_equipo = data['goles_penya'][data['goles_penya']['equipo'].str.contains(equipo_seleccionado, na=False)]
    partidos_equipo = data['partidos_penya'][data['partidos_penya']['equipo_local'].str.contains(equipo_seleccionado, na=False) | 
                                            data['partidos_penya']['equipo_visitante'].str.contains(equipo_seleccionado, na=False)]
    actas_completas = data['actas']

    # Calcular estadísticas
    estadisticas = calcular_estadisticas_generales(
        actas_equipo, 
        goles_equipo, 
        partidos_equipo, 
        equipo_seleccionado=equipo_seleccionado
    )

    # Calcular métricas avanzadas
    try:
        metricas_avanzadas = calcular_metricas_avanzadas(
            partidos_equipo, goles_equipo, actas_equipo, actas_completas,
            equipo_seleccionado=equipo_seleccionado
        )
        goles_recibidos = metricas_avanzadas['goles'][1]['valor']
    except Exception:
        try:
            goles_recibidos = calcular_goles_contra(
                actas_equipo, partidos_equipo, actas_completas,
                equipo_seleccionado=equipo_seleccionado
            )
        except Exception as e:
            print(f"Error al calcular goles en contra: {e}")
            goles_recibidos = "-"

    # Añadir métricas en dos filas
    pdf.set_y(30)
    pdf.add_metrics_row([
        ("PARTIDOS JUGADOS", estadisticas['partidos_jugados']),
        ("GOLES MARCADOS", estadisticas['goles_marcados']),
        ("GOLES RECIBIDOS", goles_recibidos)
    ])
    
    pdf.add_metrics_row([
        ("TARJETAS AMARILLAS", estadisticas['tarjetas_amarillas']),
        ("TARJETAS ROJAS", estadisticas['tarjetas_rojas']),
        ("JUGADORES USADOS", len(actas_equipo['jugador'].unique()))
    ])

    # Título de la sección de gráficos
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "Análisis de Rendimiento", 0, 1, 'L')
    pdf.ln(2)

    # Preparar y añadir los gráficos en una fila
    current_y = pdf.get_y()
    
    # Gráfico de goles por tiempo
    goles_tiempo = analizar_goles_por_tiempo(goles_equipo)
    fig_goles_tiempo = graficar_goles_por_tiempo(goles_tiempo, return_fig=True)
    if fig_goles_tiempo:
        pdf.add_plot(fig_goles_tiempo, x=10, y=current_y)

    # Gráfico de tipos de goles
    tipos_goles = analizar_tipos_goles(goles_equipo)
    fig_tipos_goles = graficar_tipos_goles(tipos_goles, return_fig=True)
    if fig_tipos_goles:
        pdf.add_plot(fig_tipos_goles, x=73, y=current_y)

    # Gráfico de tarjetas por jornada
    tarjetas_jornada = analizar_tarjetas_por_jornada(actas_equipo)
    fig_tarjetas = graficar_tarjetas_por_jornada(tarjetas_jornada, return_fig=True)
    if fig_tarjetas:
        pdf.add_plot(fig_tarjetas, x=136, y=current_y)

    # Nueva página para análisis de jugadores
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "Análisis de Jugadores", 0, 1, 'L')
    pdf.ln(2)

    current_y = pdf.get_y()

    # Gráfico de minutos por jugador
    minutos_jugador = analizar_minutos_por_jugador(actas_equipo)
    fig_minutos = graficar_minutos_por_jugador(minutos_jugador.head(10), return_fig=True)
    if fig_minutos:
        pdf.add_plot(fig_minutos, x=10, y=current_y, w=190)

    return pdf


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
        else:
            st.error("Tipo de página no válido o equipo no seleccionado")
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
