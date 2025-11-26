import streamlit as st
import pandas as pd
from database import init_db, get_conn

init_db()

def main():
    st.set_page_config(page_title="Gerenciamento de Academia")

pg = st.navigation([
    st.Page("pages/dashboard.py", title="Dashboard", icon=":material/home:"),
    st.Page("pages/gerencia_Alunos.py", title="Alunos", icon="🔥"),
    st.Page("pages/gerencia_Instrutor.py", title="Instrutores", icon="🏋️‍♂️"),
    st.Page("pages/gerencia_Pagamento.py", title="Pagamentos", icon="💰"),
    st.Page("pages/gerencia_Planos.py", title="Planos", icon="📋"),
    st.Page("pages/gerencia_Equipamentos.py", title="Equipamentos", icon="🏋️"),
    st.Page("pages/gerencia_Treinos.py", title="Treinos", icon="🤸‍♀️"),
    ], position="top",)

pg.run()






