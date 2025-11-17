import streamlit as st
import pandas as pd

st.set_page_config( 
    page_title="Gerenciar Treinos",)

st.write("# Gerenciar Treinos")

st.write(pd.DataFrame({
    'ID': [1, 2,],
    'Nome': ['joao silva','maria oliveira'],
    'instrutor': ['carlos alves','ana souza'],
    'CPF': [12345678900, 98765432100],
    }))