import streamlit as st
import pandas as pd
import time
from database import get_conn

st.set_page_config(page_title="Gerenciar Instrutor")
st.title('Gerenciar Instrutores')

def carregar_instrutores():
    conn = get_conn()
    query = "SELECT p.nome, p.cpf, p.email, i.especialidades FROM pessoa p INNER JOIN instrutor i ON p.id_pessoa = i.id_pessoa"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

df = carregar_instrutores()

if df.empty:
    st.warning('Nenhum instrutor cadastrado ainda.')
else:
    st.dataframe(df, width='stretch')

@st.dialog('Cadastrar Instrutor')
def cadastrar_instrutor():
    with st.form('cadastrar_instrutor'):
        st.subheader('Preencha com os dados do instrutor')
        nome = st.text_input('Nome', placeholder='Nome')
        cpf = st.text_input('CPF', placeholder='000.000.000-00 ou 98765432100')
        email = st.text_input('E-Mail', placeholder='email@exemplo.com')
        telefone = st.text_input('Telefone', placeholder='(00) 98765-4321')
        especialidades = st.text_input('Especialidades', placeholder='Musculação, Crossfit')

        if st.form_submit_button('Cadastrar Instrutor', width='stretch'):
            if not all([nome, cpf, email]):
                st.error('Nome, CPF e E-Mail são obrigatórios!')
                return
            
            cpf_limpo = cpf.replace('.', '').replace('-', '').replace(' ', '')
            telefone_limpo = telefone.replace('(', '').replace(')', '').replace('-', '').replace(' ', '')

            if len(cpf_limpo) != 11 or not cpf_limpo.isdigit():
                st.error('CPF inválido')
                return
            
            if len(telefone_limpo) < 10 or not telefone_limpo.isdigit():
                st.error('Telefone inválido.')
                return
            
            conn = get_conn()
            c = conn.cursor()

            try:
                c.execute('INSERT INTO pessoa (nome, cpf, email, telefone) VALUES (?, ?, ?, ?)', (nome, cpf_limpo, email, telefone_limpo))
                id_pessoa = c.lastrowid
                c.execute('INSERT INTO instrutor (id_pessoa, especialidades) VALUES (?, ?)', (id_pessoa, especialidades))

                conn.commit()
                st.success(f'Instrutor {nome} cadastrado com sucesso!')
                time.sleep(0.7)
                st.rerun()

            except Exception as e:
                conn.rollback()
                if 'cpf' in str(e):
                    st.error('Este CPF já está cadastrado!')
                elif 'email' in str(e):
                    st.error('Este email ja está cadastrado!')
                else:
                    st.error(f'Erro ao cadastrar: {e}')

            finally:
                conn.close()

@st.dialog('Editar Instrutor')
def editar_instrutor():
    if st.session_state.get('editar_instrutor_aberto') != id(st.session_state):
        if 'instrutor_encontrado' in st.session_state:
            del st.session_state.instrutor_encontrado
        st.session_state.editar_instrutor_aberto = id(st.session_state)

    if 'instrutor_encontrado' not in st.session_state:
        st.subheader('Busque um instrutor por CPF')

        with st.form('buscar_instrutor_form'):
            cpf = st.text_input('CPF', placeholder='000.000.000-00 or 98765432100')

            col1, col2 = st.columns(2)
            with col1:
                buscar = st.form_submit_button('Procurar Instrutor', width='stretch')
            
            with col2:
                if st.form_submit_button('Cancelar', width='stretch'):
                    st.rerun()

            if buscar:
                cpf_limpo = cpf.replace('.', '').replace('-', '').replace(' ', '')
                
                if not cpf:
                    st.error('Informe o CPF.')
                    return

                elif len(cpf_limpo) != 11 or not cpf_limpo.isdigit():
                    st.error('CPF inválido.')
                    return
                
                conn = get_conn()
                c = conn.cursor()

                try:
                    c.execute('SELECT p.id_pessoa, p.nome, p.cpf, p.email, p.telefone, i.especialidades FROM pessoa p INNER JOIN instrutor i ON p.id_pessoa = i.id_pessoa WHERE cpf = ?', (cpf_limpo,))
                    resultado = c.fetchone()
                    conn.close()

                    if resultado:
                        st.session_state.instrutor_encontrado = {
                            'id_pessoa': resultado[0],
                            'nome': resultado[1],
                            'cpf': resultado[2],
                            'email': resultado[3],
                            'telefone': resultado[4],
                            'especialidades': resultado[5]
                        }

                        st.success(f'Instrutor encontrado: {resultado[1]} ({resultado[2]})')
                        time.sleep(0.7)
                        st.rerun()
                    
                    else:
                        st.error('Instrutor não encontrado com este CPF.')
                
                except Exception as e:
                    st.error(f'Erro ao procurar instrutor: {e}')
    
    else:
        instrutor = st.session_state.instrutor_encontrado
        st.subheader(f'Editando: {instrutor['nome']}')

        with st.form('editar_instrutor_form'):
            novo_nome = st.text_input('Nome', instrutor['nome'])
            novo_cpf = st.text_input('CPF', instrutor['cpf'])
            novo_email = st.text_input('E-Mail', instrutor['email'])
            novo_telefone = st.text_input('Telefone', instrutor['telefone'])
            nova_especialidade = st.text_input('Especialidades', instrutor['especialidades'])

            col1, col2 = st.columns(2)
            with col1:
                salvar = st.form_submit_button('Salvar alterações', width='stretch')

            with col2:
                cancelar = st.form_submit_button('Cancelar', width='stretch')

            if salvar:
                novo_cpf_limpo = novo_cpf.replace('.', '').replace('-', '').replace(' ', '')

                if not all([novo_nome, novo_email, novo_cpf_limpo]):
                    st.error('Nome, CPF e E-Mail são obrigatórios.')
                    return

                elif len(novo_cpf_limpo) != 11 or not novo_cpf_limpo.isdigit():
                    st.error('CPF inválido.')
                    return
                
                else:
                    conn = get_conn()
                    c = conn.cursor()

                    try:
                        c.execute('UPDATE pessoa SET nome = ?, cpf = ?, email = ?, telefone = ? WHERE id_pessoa = ?', (novo_nome, novo_cpf_limpo, novo_email, novo_telefone or None, instrutor['id_pessoa']))
                        c.execute('UPDATE instrutor SET especialidades = ? WHERE id_pessoa = ?', (nova_especialidade, instrutor['id_pessoa']))
                        conn.commit()
                        conn.close()

                        st.success('Instrutor atualizado com sucesso!')
                        time.sleep(0.7)
                        
                        del st.session_state.instrutor_encontrado
                        st.rerun()

                    except Exception as e:
                        st.error(f'Erro ao salvar instrutor: {e}')

            if cancelar:
                del st.session_state.instrutor_encontrado
                st.rerun()

@st.dialog('Deletar Instrutor')
def deletar_instrutor():
    with st.form('deletar_instrutor'):
        st.warning('Esta ação não pode ser desfeita!')
        cpf = st.text_input('CPF', placeholder='000.000.000-00 oiu 98765432100')

        confirmar = st.checkbox('Sim, tenho certeza que quero deletar este instrutor.')
        form_button = st.form_submit_button('Deletar Instrutor', width='stretch')

        if form_button and confirmar:
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
                c.execute('DELETE FROM pessoa WHERE cpf = ?', (cpf_limpo,))
                if c.rowcount == 0:
                    st.error('Instrutor não encontrado.')
                else:
                    conn.commit()
                    st.success('Instrutor removido com sucesso. Recarregando página...')
                    time.sleep(1)
                    st.rerun()
            
            except Exception as e:
                st.error(f'Erro ao remover instrutor: {e}')

            finally:
                conn.close()
            
        if form_button and not confirmar:
            st.warning('É necessário confirmar antes de excluir.')
            return

col1, col2, col3 = st.columns(3)
with col1:
    if st.button('Cadastrar Instrutor', width='stretch'):
        cadastrar_instrutor()

with col2:
    if st.button('Editar Instrutor', width='stretch'):
        editar_instrutor()

with col3:
    if st.button('Deletar Instrutor', width='stretch', type='primary'):
        deletar_instrutor()
