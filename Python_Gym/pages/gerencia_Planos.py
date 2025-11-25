import streamlit as st
import pandas as pd
from database import get_conn

st.set_page_config( 
    page_title="Gerenciar Planos",)

st.title("Gerenciar Planos")

def carregar_planos():
    conn = get_conn()
    query = 'SELECT nome, preco, duracao_meses, beneficios FROM plano'
    df = pd.read_sql(query, conn)
    conn.close()
    return df

df = carregar_planos()

if df.empty:
    st.warning('Nenhum plano foi cadastrado ainda.')
else:
    st.dataframe(df, width='stretch')