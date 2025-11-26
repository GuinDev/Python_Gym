import streamlit as st
import pandas as pd
from database import get_conn

def carregar_infos():
    conn = get_conn()
    query = '''
            SELECT 
                (SELECT COUNT(*) FROM aluno)        AS total_alunos,
                (SELECT COUNT(*) FROM instrutor)     AS total_instrutores,
                (SELECT COUNT(*) FROM pagamento)    AS total_pagamentos,
                (SELECT COUNT(*) FROM plano)        AS total_planos,
                (SELECT COUNT(*) FROM equipamento)  AS total_equipamentos,
                (SELECT COUNT(*) FROM treino)       AS total_treinos
            '''
    dados = pd.read_sql(query, conn).iloc[0]
    conn.close()
    return dados

dados = carregar_infos()

st.title('Dashboard', )

col1, col2 = st.columns(2)
with col1:
    with st.container(border=True, height='stretch'):
        st.header('Alunos', divider=True)
        st.markdown(f'<p style="font-size: 1.2em;">Alunos Cadastrados: {dados.total_alunos}</p>', unsafe_allow_html=True)
        if st.button('Gerenciar Alunos', width='stretch', type='primary'):
            st.switch_page('pages/gerencia_Alunos.py')

    with st.container(border=True, height='stretch'):
        st.header('Pagamentos', divider=True)
        st.markdown(f'<p style="font-size: 1.2em;">Pagamentos Feitos: {dados.total_pagamentos}</p>', unsafe_allow_html=True)
        if st.button('Gerenciar Pagamentos', width='stretch', type='primary'):
            st.switch_page('pages/gerencia_Pagamento.py')

    with st.container(border=True, height='stretch'):
        st.header('Planos', divider=True)
        st.markdown(f'<p style="font-size: 1.2em;">Planos Disponiveis: {dados.total_planos}</p>', unsafe_allow_html=True)
        if st.button('Gerenciar Planos', width='stretch', type='primary'):
            st.switch_page('pages/gerencia_Planos.py')

with col2:
    with st.container(border=True, height='stretch'):
        st.header('Instrutores', divider=True)
        st.markdown(f'<p style="font-size: 1.2em;">Instrutores Cadastrados: {dados.total_instrutores}</p>', unsafe_allow_html=True)
        if st.button('Gerenciar Instrutores', width='stretch', type='primary'):
            st.switch_page('pages/gerencia_Instrutor.py')

    with st.container(border=True, height='stretch'):
        st.header('Equipamentos', divider=True)
        st.markdown(f'<p style="font-size: 1.2em;">Equipamentos Cadastrados: {dados.total_equipamentos}</p>', unsafe_allow_html=True)
        if st.button('Gerenciar Equipamentos', width='stretch', type='primary'):
            st.switch_page('pages/gerencia_Equipamentos.py')

    with st.container(border=True, height='stretch'):
        st.header('Treinos', divider=True)
        st.markdown(f'<p style="font-size: 1.2em;">Treinos Agendados: {dados.total_treinos}</p>', unsafe_allow_html=True)
        if st.button('Gerenciar Treinos', width='stretch', type='primary'):
            st.switch_page('pages/gerencia_Treinos.py')

    