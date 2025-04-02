"""
Módulo para el sistema de login de la aplicación Penya Independent
"""
import streamlit as st
import pandas as pd
import os

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
    
    # Configuramos el diseño de la página de login
    st.markdown("<h1 style='text-align: center;'>⚽ Penya Independent</h1>", unsafe_allow_html=True)
    
    # Centramos el formulario
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Añadimos logo si existe
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'logo_penya.png')
        if os.path.exists(logo_path):
            st.image(logo_path, width=150)
        
        # Formulario de login
        with st.form("formulario_login"):
            st.subheader("Iniciar Sesión")
            usuario = st.text_input("Usuario")
            clave = st.text_input("Contraseña", type="password")
            boton_login = st.form_submit_button("Iniciar Sesión", use_container_width=True)
            
            if boton_login:
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