"""
Componentes de UI reutilizables para la aplicación
"""
import streamlit as st

# Configuración de página global
def page_config():
    """
    Configura los parámetros generales de la página.
    Esta función debe llamarse solo una vez y al principio de cada script.
    """
    # Verificar si ya se ha configurado la página
    if "page_config_done" not in st.session_state:
        st.set_page_config(
            page_title="Dashboard Penya Independent",
            page_icon="⚽",
            layout="wide",
            initial_sidebar_state="collapsed"
        )
        st.session_state.page_config_done = True

# Función vacía que no hace nada
def show_sidebar():
    """
    Esta función ya no muestra elementos en la barra lateral
    """
    pass