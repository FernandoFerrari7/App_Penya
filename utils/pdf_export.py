"""
Utilidades principales para exportar datos a PDF
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
            
            # Construir ruta absoluta para el logo de Penya (eliminamos el de FFIB)
            penya_logo = base_path / "assets" / "logo_penya.png"
            
            # Verificar y convertir la imagen si es necesario
            # Reducir el tamaño del logo
            logo_width = 15  # Reducido de 25 a 15
            
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
                
            # Título centrado
            self.set_font('Arial', 'B', 15)
            self.set_xy(25, 8)  # Ajustado para que el título esté más a la izquierda
            self.cell(160, 10, self.title, 0, 1, 'C')
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
        # Pie de página vacío para eliminar el número de página
        pass

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
        background-color: #333333; /* Gris oscuro en lugar de negro puro */
        color: white !important; /* Forzar texto blanco siempre */
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        text-decoration: none;
        font-weight: normal; /* Cambiado de 600 a normal */
        margin: 0.5rem 0;
        border: none;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }
    .btn-download:hover {
        background-color: #444444; /* Gris más claro para hover */
        text-decoration: none;
        color: white !important; /* Mantener el texto en blanco en hover */
    }
    /* Asegurar que todos los elementos dentro del botón sean blancos */
    .btn-download span, .btn-download i, .btn-download svg {
        color: white !important;
    }
    /* Estilo para el icono de descarga */
    .btn-download .download-icon {
        background-color: #FF8C00; /* Color naranja del club */
        color: white !important;
        border-radius: 3px;
        padding: 2px 4px;
        margin-right: 5px;
        font-size: 0.9em;
    }
    </style>
    """, unsafe_allow_html=True)

    try:
        if page_type == 'home':
            # Importar la función específica para la página de inicio
            from utils.pdf_home import generate_home_pdf
            pdf = generate_home_pdf(data)
            st.markdown(
                get_pdf_download_link(pdf, "penya_independent_analisis_rendimiento.pdf"), 
                unsafe_allow_html=True
            )
        elif page_type == 'equipo' and equipo_seleccionado:
            # Asegurarse de que el equipo seleccionado es válido
            if equipo_seleccionado in data['actas']['equipo'].unique():
                try:
                    # Importar la función específica para la página de equipo
                    from utils.pdf_equipo import generate_equipo_pdf
                    pdf = generate_equipo_pdf(data, equipo_seleccionado)
                    # Limpiar el nombre del equipo para el archivo
                    nombre_archivo = equipo_seleccionado.replace(" ", "_").replace("/", "_").lower()
                    st.markdown(
                        get_pdf_download_link(pdf, f"analisis_equipo_{nombre_archivo}.pdf"), 
                        unsafe_allow_html=True
                    )
                except ImportError:
                    st.error("Módulo de generación de PDF para equipos no disponible")
            else:
                st.error("Por favor, selecciona un equipo válido")
        elif page_type == 'jugador' and jugador_seleccionado:
            try:
                # Importar la función específica para la página de jugador
                from utils.pdf_jugador import generate_jugador_pdf
                pdf = generate_jugador_pdf(data, jugador_seleccionado)
                st.markdown(
                    get_pdf_download_link(pdf, f"analisis_jugador_{jugador_seleccionado}.pdf"), 
                    unsafe_allow_html=True
                )
            except ImportError:
                st.error("Módulo de generación de PDF para jugadores no disponible")
        else:
            st.error("Tipo de página no válido o equipo/jugador no seleccionado")
    except ImportError as ie:
        st.error(f"No se pudo importar el módulo necesario: {str(ie)}")
        print(f"Error de importación: {ie}")
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
        
        # Generar el enlace de descarga sin icono
        b64_pdf = base64.b64encode(pdf_bytes).decode()
        href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{filename}" class="btn-download">Descargar PDF</a>'
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