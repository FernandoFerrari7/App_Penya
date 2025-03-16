"""
Módulo para el menú de navegación de la aplicación
"""
import streamlit as st

def crear_menu():
    """
    Crea un menú de navegación horizontal en la parte superior de la aplicación
    
    Returns:
        str: La opción seleccionada por el usuario
    """
    # Opciones del menú con iconos (orden cambiado y nuevos iconos)
    opciones = [
        {"nombre": "Inicio", "icono": "📌"},
        {"nombre": "Equipo", "icono": "🧍🧍"},
        {"nombre": "Jugadores", "icono": "🧍"}
    ]
    
    # Crear un contenedor para el menú
    menu_container = st.container()
    
    with menu_container:
        # Crear columnas para cada opción del menú
        cols = st.columns(len(opciones))
        
        # Inicializar la selección actual
        if 'pagina_actual' not in st.session_state:
            st.session_state.pagina_actual = "Inicio"
        
        # Crear botones para cada opción
        for i, opcion in enumerate(opciones):
            with cols[i]:
                # Estilo diferente para la página actual
                if st.session_state.pagina_actual == opcion["nombre"]:
                    st.button(
                        f"{opcion['icono']} {opcion['nombre']}",
                        key=f"menu_{opcion['nombre']}",
                        use_container_width=True,
                        disabled=True
                    )
                else:
                    if st.button(
                        f"{opcion['icono']} {opcion['nombre']}",
                        key=f"menu_{opcion['nombre']}",
                        use_container_width=True
                    ):
                        st.session_state.pagina_actual = opcion["nombre"]
                        st.rerun()
    
    # Separador después del menú
    st.markdown("---")
    
    return st.session_state.pagina_actual

def mostrar_pagina_actual():
    """
    Muestra la página correspondiente según la selección del menú
    
    Returns:
        None
    """
    from home import main as main_home
    from pages.jugadores import main as main_jugadores
    from pages.equipos import main as main_equipos
    
    pagina = st.session_state.pagina_actual
    
    if pagina == "Inicio":
        main_home()
    elif pagina == "Jugadores":
        main_jugadores()
    elif pagina == "Equipo":
        main_equipos()
    else:
        st.error(f"Página no encontrada: {pagina}")