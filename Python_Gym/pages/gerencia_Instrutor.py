import streamlit as st
import pandas as pd

st.set_page_config( 
    page_title="Gerenciar Instrutor",)

st.write("# Gerenciar Instrutor")

st.write(pd.DataFrame({
    'ID': [10, 20,],
    'Nome': ['carlos alves','ana souza'],
    'CPF': [12345678900, 98765432100],
    }))