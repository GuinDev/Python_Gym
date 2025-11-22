import streamlit as st
import pandas as pd

st.set_page_config( 
    page_title="Gerenciar Pagamentos",)

st.write("# Gerenciar Pagamentos")


# Your query
conn = st.connection('gym_db', type='sql')
st.dataframe(conn.query('SELECT * FROM pagamentos').set_index('id'))

