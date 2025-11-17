import streamlit as st
import pandas as pd

st.set_page_config( 
    page_title="Gerenciar Equipamentos",)

st.write("# Gerenciar Equipamentos")

st.write(pd.DataFrame({
    'ID': [10, 20,],
    'Nome': ['cadeira extensora','esteira'],
    'data da compra': ['20/10/2024', '05/11/2023'],
    }))