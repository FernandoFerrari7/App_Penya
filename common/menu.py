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
            # Determinar la ruta al script actualizar_datos.py
            script_path = os.path.join('data', 'actualizar_datos.py')
            
            # Verificar que el script existe
            if not os.path.exists(script_path):
                st.error(f"No se encontró el script en la ruta: {script_path}")
                print(f"Error: No se encontró el script en la ruta: {script_path}")
                return False
            
            # Ejecutar el script de Python
            process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=os.environ.copy()
            )
            
            # Esperar a que termine el proceso
            stdout, stderr = process.communicate()
            return_code = process.returncode
            
            # Mostrar resumen del proceso en la terminal
            print("RESUMEN DE LA ACTUALIZACIÓN:")
            print(stdout)
            
            if stderr:
                print("ERRORES DURANTE LA ACTUALIZACIÓN:")
                print(stderr)
            
            # Verificar el resultado
            if return_code == 0:
                st.success("Datos actualizados correctamente")
                st.info("Se ha iniciado un nuevo despliegue en Render. Los cambios estarán disponibles en unos minutos.")
                return True
            else:
                st.error("Error al actualizar los datos")
                print("Error en la actualización. Revisa la terminal para más detalles.")
                return False
            
    except Exception as e:
        st.error("Error al ejecutar la actualización")
        print(f"Error al ejecutar la actualización: {str(e)}")
        import traceback
        traceback.print_exc()  # Imprime la traza del error en la terminal
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
    
    # Aplicar CSS para alinear los botones del menú
    st.markdown("""
    <style>
    /* Estilo para asegurar que todos los botones del menú tengan la misma altura */
    div[data-testid="stHorizontalBlock"] button {
        height: 40px !important;
        line-height: 1.2 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0.5em !important;
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        vertical-align: middle !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
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
            
            # Aplicar estilos consistentes para los botones de actualizar y cerrar sesión
            st.markdown("""
            <style>
            /* Estilo para el botón de Actualizar */
            div[data-testid="column"]:nth-of-type(1) button {
                font-size: 0.9em !important;
                padding: 0.5em !important;
                height: 43px !important;
                min-height: 43px !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                width: 100% !important;
                box-sizing: border-box !important;
            }
            
            /* Estilo para el botón de Cerrar Sesión */
            div[data-testid="column"]:nth-of-type(2) button {
                font-size: 0.9em !important;
                padding: 0.5em !important;
                height: 43px !important;
                min-height: 43px !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                width: 100% !important;
                box-sizing: border-box !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Botón de Actualizar Información
            with btn_cols[0]:
                if st.button("🔄 Actualizar", key="btn_update", use_container_width=True):
                    # Ejecutar la actualización cuando se presiona el botón
                    actualizacion_exitosa = ejecutar_actualizacion()
                    
                    # Recargar la página después de la actualización para mostrar los nuevos datos
                    if actualizacion_exitosa:
                        st.rerun()
            
            # Botón de Cerrar Sesión
            with btn_cols[1]:
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