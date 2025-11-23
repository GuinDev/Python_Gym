import streamlit as st
from database import init_db

init_db()

def main():
    st.set_page_config(
        page_title="Academia Fit+",)
    
    st.write("# bem vindo a Academia Fit+!")
    st.write("Essa é a pagina inicial.")


pg = st.navigation([
    st.Page(main, title="Main", icon=":material/favorite:"),
    st.Page("./pages/gerencia_Alunos.py", title="Alunos", icon="🔥"),
    st.Page("./pages/gerencia_Instrutor.py", title="Instrutores", icon="🏋️‍♂️"),
    st.Page("./pages/gerencia_Pagamento.py", title="Pagamentos", icon="💰"),
    st.Page("./pages/gerencia_Planos.py", title="Planos", icon="📋"),
    st.Page("./pages/gerencia_Equipamentos.py", title="Equipamentos", icon="🏋️"),
    st.Page("./pages/gerencia_Treinos.py", title="Treinos", icon="🤸‍♀️"),] ,
    position="top",)

pg.run()




