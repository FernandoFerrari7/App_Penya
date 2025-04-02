"""
Utilidades para exportar datos a PDF
"""
import os
import pandas as pd
import streamlit as st
from fpdf import FPDF
import tempfile
import base64

class PenyaPDF(FPDF):
    """Clase personalizada de PDF para Penya Independent"""
    
    def __init__(self, title="Penya Independent - Análisis de Rendimiento", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = title
        self.add_page()
        self.set_title(title)
    
    def header(self):
        """Configurar el encabezado de cada página"""
        try:
            if os.path.exists("assets/logo_penya.png"):
                self.image("assets/logo_penya.png", 10, 8, 20)
        except Exception:
            pass
        try:
            if os.path.exists("assets/logo_ffib.png"):
                self.image("assets/logo_ffib.png", 180, 8, 20)
        except Exception:
            pass
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, self.title, 0, 1, 'C')
        self.line(10, 25, 200, 25)
        self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

    def add_metric(self, title, value, color=(0, 0, 0)):
        self.set_font('Arial', 'B', 12)
        self.set_text_color(*color)
        self.cell(40, 10, f'{title}: {value}', 0, 0, 'L')
        self.set_text_color(0, 0, 0)
        self.ln(10)


def generate_home_pdf(data):
    from calculos.calculo_equipo import calcular_estadisticas_generales, calcular_goles_contra

    pdf = PenyaPDF()

    actas_penya = data['actas_penya']
    goles_penya = data['goles_penya']
    partidos_penya = data['partidos_penya']

    estadisticas = calcular_estadisticas_generales(actas_penya, goles_penya, partidos_penya)

    pdf.add_metric("Partidos Jugados", estadisticas['partidos_jugados'], (0, 0, 0))
    pdf.add_metric("Goles Marcados", estadisticas['goles_marcados'], (0, 0, 0))

    try:
        goles_contra = calcular_goles_contra(actas_penya, partidos_penya, data['actas'])
    except:
        goles_contra = "-"
    pdf.add_metric("Goles Recibidos", goles_contra, (0, 0, 0))
    pdf.add_metric("Tarjetas Amarillas", estadisticas['tarjetas_amarillas'], (0, 0, 0))
    pdf.add_metric("Tarjetas Rojas", estadisticas['tarjetas_rojas'], (0, 0, 0))

    return pdf


def get_pdf_download_link(pdf, filename="informe.pdf"):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        pdf.output(tmp.name)
        tmp_path = tmp.name
    with open(tmp_path, 'rb') as file:
        pdf_bytes = file.read()
    os.unlink(tmp_path)
    b64_pdf = base64.b64encode(pdf_bytes).decode()
    href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{filename}" class="btn-download">⬇️ Descargar PDF</a>'
    return href


def show_download_button(data, page_type):
    st.markdown("""
    <style>
    .btn-download {
        display: inline-block;
        background-color: #FB8C00;
        color: white !important;
        padding: 8px 16px;
        text-align: center;
        text-decoration: none;
        font-size: 14px;
        border-radius: 4px;
        border: none;
        cursor: pointer;
        margin: 4px 0px;
        font-weight: bold;
    }
    .btn-download:hover {
        background-color: #F57C00;
        text-decoration: none;
    }
    </style>
    """, unsafe_allow_html=True)

    pdf = generate_home_pdf(data)
    st.markdown(get_pdf_download_link(pdf, "penya_independent_analisis_rendimiento.pdf"), unsafe_allow_html=True)

