import streamlit as st
import common.login as login


login.generarLogin()
if 'usuario' in st.session_state:
    st.header('Página 3')