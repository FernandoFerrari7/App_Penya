"""
Módulo para el menú de navegación de la aplicación
"""
import streamlit as st
import subprocess
import os
import datetime
import sys

def ejecutar_actualizacion():
    """
    Ejecuta el script de actualización de datos y muestra el resultado
    """
    try:
        # Mostrar spinner mientras se ejecuta el proceso
        with st.spinner('Actualizando datos desde el servidor...'):
            # Determinar la ruta al script actualizar_github.py
            script_path = os.path.join('data', 'actualizar_github.py')
            
            # Verificar que el script existe
            if not os.path.exists(script_path):
                st.error(f"No se encontró el script en la ruta: {script_path}")
                return False
            
            # Configurar entorno para usar codificación UTF-8 en Windows
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            
            # Cambiar al directorio data antes de ejecutar
            current_dir = os.getcwd()
            os.chdir('data')
            
            # Ejecutar el script
            process = subprocess.run(
                ["python", "actualizar_github.py"],
                capture_output=True,
                text=True,
                env=env,
                errors="replace"  # Reemplazar caracteres problemáticos
            )
            
            # Volver al directorio original
            os.chdir(current_dir)
        
        # Verificar el resultado
        if process.returncode == 0:
            st.success("✅ Datos actualizados correctamente")
            # Mostrar logs en un expander para no ocupar demasiado espacio
            with st.expander("Ver detalles de la actualización"):
                st.code(process.stdout)
            return True
        else:
            st.error("❌ Error al actualizar los datos")
            with st.expander("Ver detalles del error"):
                st.code(process.stderr)
            return False
            
    except Exception as e:
        st.error(f"Error al ejecutar la actualización: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return False

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
            
            # Crear dos columnas para los botones
            btn_cols = st.columns(2)
            
            # Botón de Actualizar Información
            with btn_cols[0]:
                # Estilo para hacer el botón más pequeño
                st.markdown("""
                <style>
                div[data-testid="column"]:nth-of-type(1) button {
                    font-size: 0.85em;
                    padding: 0.2em 0.5em;
                    height: auto;
                    min-height: 0;
                }
                </style>
                """, unsafe_allow_html=True)
                
                if st.button("🔄 Actualizar", key="btn_update", use_container_width=True):
                    # Ejecutar la actualización cuando se presiona el botón
                    actualizacion_exitosa = ejecutar_actualizacion()
                    
                    # Recargar la página después de la actualización para mostrar los nuevos datos
                    if actualizacion_exitosa:
                        st.rerun()
            
            # Botón de Cerrar Sesión
            with btn_cols[1]:
                # Estilo para hacer el botón más pequeño
                st.markdown("""
                <style>
                div[data-testid="column"]:nth-of-type(2) button {
                    font-size: 0.85em;
                    padding: 0.2em 0.5em;
                    height: auto;
                    min-height: 0;
                }
                </style>
                """, unsafe_allow_html=True)
                
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