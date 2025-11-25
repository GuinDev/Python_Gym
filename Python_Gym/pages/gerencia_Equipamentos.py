import streamlit as st
import pandas as pd
from database import get_conn

st.set_page_config( 
    page_title="Gerenciar Equipamentos",)

st.write("# Gerenciar Equipamentos")

conn = get_conn()
c = conn.cursor()
c.execute('UPDATE plano SET preco = 20.99 WHERE id_plano = 4')
print('foi')
df = pd.read_sql('SELECT * FROM plano', conn)
conn.close()

st.dataframe(df)