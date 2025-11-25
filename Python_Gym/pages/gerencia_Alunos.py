import streamlit as st
import pandas as pd
import time
from database import get_conn

st.set_page_config(page_title="Gerenciar Alunos",)
st.title('Gerenciar Alunos')

def carregar_alunos():
    conn = get_conn()
    query = "SELECT p.nome AS 'Nome', p.cpf AS 'CPF', p.email AS 'E-Mail', p.telefone AS 'Telefone', pl.nome AS 'Plano Atual', a.historico_saude AS 'Histórico de Saúde', a.objetivos AS 'Objetivos' FROM pessoa p INNER JOIN aluno a ON p.id_pessoa = a.id_pessoa INNER JOIN plano pl ON a.id_plano = pl.id_plano"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

df = carregar_alunos()

if df.empty:
    st.warning('Nenhum aluno cadastrado ainda.')
else:
    st.dataframe(df, width='stretch')

def lista_planos():
    conn = get_conn()
    planos = pd.read_sql("SELECT concat(nome, ' - R$ ', preco) AS 'nome' FROM plano", conn)
    conn.close()
    return planos['nome'].tolist()

@st.dialog('Cadastrar Aluno')
def cadastrar_aluno():
    with st.form('cadastrar_aluno'):
        st.subheader('Preencha com os dados do aluno')
        nome = st.text_input('Nome', placeholder='Nome')
        cpf = st.text_input('CPF', placeholder='000.000.000-00 ou 98765432100')
        email = st.text_input('E-Mail', placeholder='email@exemplo.com')
        telefone = st.text_input('Telefone', placeholder='(00) 98765-4321')
        historico = st.text_input('Histórico de saúde', placeholder='Sem restrições')
        objetivo = st.text_input('Objetivo', placeholder='Ganho de massa')
        plano = st.selectbox('Plano', lista_planos()).split(' - ')[0]
        
        if st.form_submit_button('Cadastrar Aluno', width='stretch'):
            if not all([nome, cpf, email]):
                st.error('Nome, CPF e E-Mail são obrigatórios!')
                return
            
            cpf_limpo = cpf.replace('.', '').replace('-', '').replace(' ', '')
            telefone_limpo = telefone.replace('(', '').replace(')', '').replace('-', '').replace(' ', '')

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
                c.execute('SELECT id_plano FROM plano WHERE nome = ?', (plano,))
                plano_escolhido = c.fetchone()[0]
                c.execute('INSERT INTO aluno (id_pessoa, historico_saude, objetivos, id_plano) VALUES (?, ?, ?, ?)', (id_pessoa, historico or None, objetivo or None, plano_escolhido))

                conn.commit()
                st.success(f'Aluno {nome} cadastrado com sucesso!')
                time.sleep(0.7)
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


@st.dialog('Editar Aluno')
def editar_aluno():
    if st.session_state.get('editar_aluno_aberto') != id(st.session_state):
        if 'aluno_encontrado' in st.session_state:
            del st.session_state.aluno_encontrado
        st.session_state.editar_aluno_aberto = id(st.session_state)

    if 'aluno_encontrado' not in st.session_state:
        st.subheader('Busque um aluno pelo CPF')

        with st.form('buscar_aluno_form'):
            
            cpf = st.text_input('CPF', placeholder='000.000.000-00 ou 98765432100')

            col1, col2 = st.columns(2)
            with col1:
                buscar = st.form_submit_button('Procurar Aluno', width='stretch')
            
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
                    c.execute('SELECT p.id_pessoa, p.nome, p.cpf, p.email, p.telefone, a.historico_saude, a.objetivos, a.id_plano FROM pessoa p INNER JOIN aluno a ON p.id_pessoa = a.id_pessoa WHERE p.cpf = ?', (cpf_limpo,))
                    resultado = c.fetchone()
                    conn.close()
                    
                    if resultado:
                        st.session_state.aluno_encontrado = {
                            'id_pessoa': resultado[0],
                            'nome': resultado[1],
                            'cpf': resultado[2],
                            'email': resultado[3],
                            'telefone': resultado[4],
                            'historico': resultado[5] or '',
                            'objetivo': resultado[6] or '',
                            'plano': resultado[7]
                        }

                        st.success(f'Aluno encontrado: {resultado[1]} ({resultado[2]})')
                        time.sleep(0.7)
                        st.rerun()
                    
                    else:
                        st.error('Aluno não encontrado com este CPF.')
                except Exception as e:
                    st.error(f'Erro ao procurar aluno: {e}')

    else:
        aluno = st.session_state.aluno_encontrado
        st.subheader(f'Editando: {aluno['nome']}')

        with st.form('editar_aluno_form'):
            novo_nome = st.text_input('Nome', aluno['nome'])
            novo_cpf = st.text_input('CPF', aluno['cpf'])
            novo_email = st.text_input('E-Mail', aluno['email'])
            novo_telefone = st.text_input('Telefone', aluno['telefone'])
            novo_historico = st.text_input('Histórico de Saúde', aluno['historico'])
            novo_objetivo = st.text_input('Objetivo', aluno['objetivo'])
            novo_plano = st.selectbox(('Plano'), lista_planos(), aluno['plano'] - 1).split(' - ')[0]

            col1, col2 = st.columns(2)

            with col1:
                salvar = st.form_submit_button('Salvar alterações', width='stretch', type='primary')
            
            with col2:
                cancelar = st.form_submit_button('Cancelar', width='stretch')

            if salvar:
                novo_cpf_limpo = novo_cpf.replace('.', '').replace('-', '').replace(' ', '')

                if not all([novo_nome, novo_cpf_limpo, novo_email]):
                    st.error('Nome, CPF e E-Mail são obrigatórios.')
                    return

                elif len(novo_cpf_limpo) != 11 or not novo_cpf_limpo.isdigit():
                    st.error('CPF inválido.')
                    return
                
                else:
                    conn = get_conn()
                    c = conn.cursor()

                    try:
                        c.execute('UPDATE pessoa SET nome = ?, cpf = ?, email = ?, telefone = ? WHERE id_pessoa = ?', (novo_nome, novo_cpf_limpo, novo_email, novo_telefone or None, aluno['id_pessoa']))
                        c.execute('UPDATE aluno SET historico_saude = ?, objetivos = ?, id_plano = (SELECT id_plano FROM plano WHERE nome = ?) WHERE id_pessoa = ?', (novo_historico, novo_objetivo, novo_plano, aluno['id_pessoa']))
                        conn.commit()
                        conn.close()

                        st.success('Aluno atualizado com sucesso!')
                        time.sleep(1)

                        del st.session_state.aluno_encontrado
                        st.rerun()
                    
                    except Exception as e:
                        st.error(f'Erro ao salvar aluno: {e}')
            
            if cancelar:
                del st.session_state.aluno_encontrado
                st.rerun()

@st.dialog('Deletar Aluno')
def deletar_aluno():
    with st.form('deletar_aluno'):
        st.warning('Esta ação não pode ser desfeita!')
        cpf = st.text_input('CPF', placeholder='000.000.000-00 ou 98765432100')

        confirmar = st.checkbox('Sim, eu tenho certeza que quero deletar este aluno.')
        form_button = st.form_submit_button('Deletar Aluno', width='stretch')
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
                    st.error('Aluno não encontrado.')
                else:
                    conn.commit()
                    st.success('Aluno removido com sucesso. Recarregando pagina...')
                    time.sleep(2)
                    st.rerun()
            
            except Exception as e:
                st.error(f'Erro ao remover aluno: {e}')
            
            finally:
                conn.close()
        
        if form_button and not confirmar:
            st.warning('É necessário confirmar antes de excluir.')
            return

col1, col2, col3 = st.columns(3)

with col1:
    if st.button('Cadastrar Aluno', width='stretch'):
        cadastrar_aluno()

with col2:
    if st.button('Editar Aluno', width='stretch'):
        editar_aluno()

with col3:
    if st.button('Deletar Aluno', width='stretch', type='primary'):
        deletar_aluno()