import streamlit as st

def main():
    st.set_page_config(
        page_title="Academia Fit+",)
    
    st.write("# bem vindo a Academia Fit+!")
    st.write("Essa é a pagina inicial.")


pg = st.navigation([
    st.Page(main, title="Main", icon=":material/favorite:"),
    st.Page("gerencia_Alunos.py", title="Alunos", icon="🔥"),
    st.Page("gerencia_Instrutor.py", title="Instrutores", icon="🏋️‍♂️"),
    st.Page("gerencia_Pagamento.py", title="Pagamentos", icon="💰"),
    st.Page("gerencia_Planos.py", title="Planos", icon="📋"),
    st.Page("gerencia_Equipamentos.py", title="Equipamentos", icon="🏋️"),
    st.Page("gerencia_Treinos.py", title="Treinos", icon="🤸‍♀️"),] ,
    position="top",)

pg.run()




