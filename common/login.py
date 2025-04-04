"""
Módulo para el sistema de login de la aplicación Penya Independent
"""
import streamlit as st
import pandas as pd
import os
from base64 import b64encode

def get_image_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = b64encode(image_file.read()).decode('utf-8')
        return encoded_string

def validar_usuario(usuario, clave):
    """
    Valida el usuario y clave contra el archivo usuarios.csv
    
    Args:
        usuario (str): Usuario a validar
        clave (str): Clave del usuario
    
    Returns:
        tuple: (es_valido, rol) - (True, rol) si es válido, (False, None) si no lo es
    """
    # Construir la ruta al archivo usuarios.csv
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'usuarios.csv')
    
    # Verificar si el archivo existe
    if not os.path.exists(csv_path):
        st.error(f"El archivo de usuarios no se encuentra en: {csv_path}")
        return False, None
    
    try:
        # Leer el archivo CSV
        df_usuarios = pd.read_csv(csv_path)
        
        # Validar el usuario y la clave
        usuario_valido = df_usuarios[(df_usuarios['usuario'] == usuario) & 
                                    (df_usuarios['clave'] == clave)]
        
        if not usuario_valido.empty:
            # Si encontramos el usuario, también guardamos su rol
            rol = usuario_valido.iloc[0]['rol'] if 'rol' in usuario_valido.columns else 'usuario'
            return True, rol
        else:
            return False, None
            
    except Exception as e:
        st.error(f"Error al leer el archivo de usuarios: {e}")
        return False, None

def mostrar_login():
    """
    Muestra el formulario de login y maneja la autenticación
    
    Returns:
        bool: True si el usuario está autenticado, False si no lo está
    """
    # Si el usuario ya está autenticado, retornamos True
    if 'usuario_autenticado' in st.session_state and st.session_state.usuario_autenticado:
        return True
    
    # Centramos todo el contenido
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Primera fila con los logos
        st.markdown("""
            <div style='display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;'>
                <div style='display: flex; align-items: center; transform: scale(1.2); transform-origin: left center;'>
                    <span style='font-size: 38px; margin-right: 10px;'>⚽</span>
                    <span style='font-size: 42px; font-weight: bold;'>Penya Independent</span>
                </div>
                <img src='data:image/png;base64,{}' style='width: 100px;'>
            </div>
        """.format(get_image_base64(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'logo_penya.png'))), unsafe_allow_html=True)
        
        # Formulario de login
        st.subheader("Iniciar Sesión")
        usuario = st.text_input("Usuario")
        clave = st.text_input("Contraseña", type="password")
        
        if st.button("Iniciar Sesión", use_container_width=True):
            if usuario and clave:  # Verificamos que no estén vacíos
                es_valido, rol = validar_usuario(usuario, clave)
                if es_valido:
                    # Guardamos los datos en session_state
                    st.session_state.usuario_autenticado = True
                    st.session_state.nombre_usuario = usuario
                    st.session_state.rol_usuario = rol
                    st.rerun()  # Recargamos la página
                else:
                    st.error("Usuario o contraseña incorrectos")
            else:
                st.warning("Por favor, ingresa tu usuario y contraseña")
    
    return False

def cerrar_sesion():
    """
    Cierra la sesión del usuario
    """
    for key in ['usuario_autenticado', 'nombre_usuario', 'rol_usuario', 'pagina_actual']:
        if key in st.session_state:
            del st.session_state[key]
    
    st.rerun()  # Recargamos la página

def mostrar_info_usuario():
    """
    Muestra la información del usuario y el botón de cierre de sesión
    """
    if 'usuario_autenticado' in st.session_state and st.session_state.usuario_autenticado:
        col1, col2 = st.columns([8, 2])
        with col2:
            st.write(f"Usuario: **{st.session_state.nombre_usuario}**")
            if st.button("Cerrar Sesión", key="btn_logout", type="primary", use_container_width=True):
                cerrar_sesion()