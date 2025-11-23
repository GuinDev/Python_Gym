import streamlit as st
import pandas as pd
from database import get_conn

st.set_page_config(page_title="Gerenciar Alunos",)
st.header('Gerenciar Alunos')

def carregar_alunos():
    conn = get_conn()
    query = "SELECT p.nome, p.cpf, p.email, p.telefone, a.historico_saude, a.objetivos FROM pessoa p INNER JOIN aluno a ON p.id_pessoa = a.id_pessoa"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

df = carregar_alunos()

if df.empty:
    st.warning('Nenhum aluno cadastrado ainda')
else:
    st.dataframe(df, width='stretch')

col1, col2 = st.columns(2)

@st.dialog('Adicionar Aluno', width='stretch')
def cadastrar_aluno():
    with st.form('adicionar_aluno'):
        st.subheader('Preencha com os dados do aluno')
        nome = st.text_input('Nome', placeholder='Nome')
        cpf = st.text_input('CPF', placeholder='000.000.000-00 ou 98765432100')
        email = st.text_input('E-Mail', placeholder='email@exemplo.com')
        telefone = st.text_input('Telefone', placeholder='00987654321')
        historico = st.text_input('Histórico de saúde', placeholder='Sem restrições')
        objetivo = st.text_input('Objetivo', placeholder='Ganho de massa')
        
        if st.form_submit_button('Cadastrar Aluno'):
            if not all([nome, cpf, email, telefone]):
                st.error('Nome, CPF, E-Mail e Telefone são obrigatórios!')
                return
            
            cpf_limpo = cpf.replace('.', '').replace('-', '').replace(' ', '')
            telefone_limpo = telefone.replace('(', '').replace(')', '').replace(' ', '')

            if len(cpf_limpo) != 11 or not cpf_limpo.isdigit():
                st.error('CPF inválido! Digite apenas números (11 dígitos).')
                return
            
            if telefone_limpo and (len(telefone_limpo) < 10 or not telefone_limpo.isdigit()):
                st.error('Telefone inválido!')
                return
            
            conn = get_conn()
            c = conn.cursor()

            try:
                c.execute('INSERT INTO pessoa (nome, cpf, email, telefone) VALUES (?, ?, ?, ?)', (nome, cpf_limpo, email, telefone_limpo))
                id_pessoa = c.lastrowid
                c.execute('INSERT INTO aluno (id_pessoa, historico_saude, objetivos) VALUES (?, ?, ?)', (id_pessoa, historico or None, objetivo or None))

                conn.commit()
                st.success(f'Aluno {nome} cadastrado com sucesso!')
                st.rerun()

            except Exception as e:
                conn.rollback()
                if 'cpf' in str(e):
                    st.error('Este CPF já está cadastrado!')
                elif 'email' in str(e):
                    st.error('Este E-Mail já está cadastrado!')
                else:
                    st.error(f'Erro ao cadastrar: {e}')
            finally:
                conn.close()



@st.dialog('Deletar Aluno')
def deletar_aluno():
    with st.form('deletar_aluno'):
        st.warning('Esta ação não pode ser desfeita!')
        cpf = st.text_input('CPF', placeholder='000.000.000-00 ou 98765432100')

        confirmar = st.checkbox('Sim, eu tenho certeza que quero deletar este aluno.')

        if st.form_submit_button('Deletar Aluno') and confirmar:
            if not cpf:
                st.error('Informe o CPF.')
                return
            
            cpf_limpo = cpf.replace('.', '').replace('-', '').replace(' ', '')

            if len(cpf_limpo) != 11 or not cpf_limpo.isdigit():
                st.error('CPF inválido.')
                return
            
            conn = get_conn()
            c = conn.cursor()

            try:
                c.execute('DELETE FROM pessoa WHERE cpf = ?', (cpf_limpo))
                if c.rowcount == 0:
                    st.error('Aluno não encontrado.')
                else:
                    conn.commit()
                    st.success('Aluno removido com sucesso.')
                    st.rerun()
            
            except Exception as e:
                st.error(f'Erro ao deletar: {e}')
            
            finally:
                conn.close()

with col1:
    if st.button('Cadastrar Aluno', width='stretch'):
        cadastrar_aluno()

with col2:
    if st.button('Deletar Aluno', width='stretch', type='primary'):
        deletar_aluno()