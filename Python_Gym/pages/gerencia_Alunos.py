import streamlit as st
import pandas as pd

st.set_page_config( 
    page_title="Gerenciar Alunos",)

st.write("# Gerenciar Alunos")

st.write(pd.DataFrame({
    'ID': [1, 2,],
    'Nome': ['joao silva','maria oliveira'],
    'CPF': [12345678900, 98765432100],
    }))