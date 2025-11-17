import streamlit as st
import pandas as pd

st.set_page_config( 
    page_title="Gerenciar Pagamentos",)

st.write("# Gerenciar Pagamentos")

st.write(pd.DataFrame({
    'ID': [1, 2,],
    'Nome': ['joao silva','maria oliveira'],
    'valor': [150.00, 200.00],
    'data': ['2024-01-15', '2024-01-20'],
    'Estado': ['pago', 'pendente'],
    }))