"""
Aplicación principal de Penya Independent con autenticación
"""
import streamlit as st
from common import login
import home
from utils.ui import page_config

def main():
    """
    Función principal que ejecuta la aplicación con autenticación
    """
    # Configurar la página
    page_config()
    
    # Verificar si el usuario está autenticado
    if login.mostrar_login():
        # Ejecutar la aplicación principal
        home.main()

if __name__ == "__main__":
    main()