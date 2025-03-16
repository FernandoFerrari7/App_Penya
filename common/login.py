import streamlit as st
import pandas as pd
import os
import common.menu as menu

# Validación simple de usuario y clave con un archivo csv

def validarUsuario(usuario, clave):    
    """Permite la validación de usuario y clave

    Args:
        usuario (str): usuario a validar
        clave (str): clave del usuario

    Returns:
        bool: True usuario valido, False usuario invalido
    """    
    # Construir la ruta relativa al archivo usuarios.csv desde el archivo login.py
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'usuarios.csv')

    # Convertir a ruta absoluta
    csv_path = os.path.abspath(csv_path)

    # Imprimir la ruta para depuración
    # st.write(f"Ruta construida para el CSV: {csv_path}")

    # Verificar si la ruta existe
    if not os.path.exists(csv_path):
        st.error(f"El archivo no se encuentra en la ruta especificada: {csv_path}")
        return False

    # Leer el archivo CSV
    try:
        dfusuarios = pd.read_csv(csv_path)
    except Exception as e:
        st.error(f"Error al intentar leer el archivo CSV: {e}")
        return False

    # Validación del usuario y la clave
    if len(dfusuarios[(dfusuarios['usuario'] == usuario) & (dfusuarios['clave'] == clave)]) > 0:
        return True
    else:
        return False



def generarLogin():
    """Genera la ventana de login o muestra el menú si el login es valido
    """    
    # Validamos si el usuario ya fue ingresado    
    if 'usuario' in st.session_state:
        menu.generarMenu(st.session_state['usuario']) # Si ya hay usuario cargamos el menu        
    else: 
        # Cargamos el formulario de login       
        with st.form('frmLogin'):
            parUsuario = st.text_input('Usuario')
            parPassword = st.text_input('Password',type='password')
            btnLogin=st.form_submit_button('Ingresar',type='primary')
            if btnLogin:
                if validarUsuario(parUsuario,parPassword):
                    st.session_state['usuario'] =parUsuario
                    # Si el usuario es correcto reiniciamos la app para que se cargue el menú
                    st.rerun()
                else:
                    # Si el usuario es invalido, mostramos el mensaje de error
                    st.error("Usuario o clave inválidos",icon=":material/gpp_maybe:")        

                                