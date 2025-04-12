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
    # Opciones del menú con iconos
    opciones = [
        {"nombre": "Inicio", "icono": "⚽"},
        {"nombre": "Equipo", "icono": "🧍🧍"},
        {"nombre": "Jugadores", "icono": "🧍"},
        {"nombre": "Análisis Comparativo", "icono": "🔍"}
    ]
    
    # Inicializar la selección actual
    if 'pagina_actual' not in st.session_state:
        st.session_state.pagina_actual = "Inicio"
    
    # Crear contenedor principal con tres columnas para la cabecera
    header_cols = st.columns([1, 4, 1])
    
    # Logo en la primera columna
    # Aumentamos el tamaño del logo de 70 a 100px para hacerlo más visible
    with header_cols[0]:
        st.image("assets/logo_penya.png", width=100)
    
    # Menú en la columna central
    with header_cols[1]:
        menu_cols = st.columns(len(opciones))
        
        # Crear botones para cada opción
        for i, opcion in enumerate(opciones):
            with menu_cols[i]:
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
    
    # Información de usuario en la tercera columna
    with header_cols[2]:
        if 'usuario_autenticado' in st.session_state and st.session_state.usuario_autenticado:
            st.write(f"Usuario: **{st.session_state.nombre_usuario}**")
            if st.button("Cerrar Sesión", key="btn_logout", type="primary", use_container_width=True):
                # Importamos la función aquí para evitar importaciones circulares
                from common.login import cerrar_sesion
                cerrar_sesion()
    
    # Separador después del menú
    st.markdown("---")
    
    return st.session_state.pagina_actual

def mostrar_pagina_actual():
    """
    Muestra la página correspondiente según la selección del menú
    """
    from home import main as main_home
    from pages.jugadores import main as main_jugadores
    from pages.equipos import main as main_equipos
    from pages.ml import main as main_ml  
    
    pagina = st.session_state.pagina_actual
    
    if pagina == "Inicio":
        main_home()
    elif pagina == "Jugadores":
        main_jugadores()
    elif pagina == "Equipo":
        main_equipos()
    elif pagina == "Análisis Comparativo":  
        main_ml()
    else:
        st.error(f"Página no encontrada: {pagina}")