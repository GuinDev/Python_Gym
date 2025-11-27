import streamlit as st
import pandas as pd
import time
from database import get_conn

st.set_page_config( 
    page_title="Gerenciar Planos",)

st.title("Gerenciar Planos")

def carregar_planos():
    conn = get_conn()
    query = 'SELECT nome AS "Nome", preco AS "Preço", duracao_meses AS "Duração (meses)", beneficios AS "Benefícios" FROM plano'
    df = pd.read_sql(query, conn)
    conn.close()
    return df

df = carregar_planos()

if df.empty:
    st.info('Nenhum plano foi cadastrado ainda.')
else:
    st.dataframe(df, width='stretch')

def listar_planos():
    conn = get_conn()
    planos = pd.read_sql('SELECT nome FROM plano', conn)
    conn.close()
    return planos['nome'].tolist()

@st.dialog('Cadastrar Plano')
def cadastrar_plano():
    with st.form('cadastrar_plano'):
        st.subheader('Preencha com os dados do novo plano')
        nome = st.text_input('Nome', placeholder='Plano Mensal')
        preco = st.number_input('Preço', 0.00, 99999.99, None, placeholder='99,99')
        duracao = st.number_input('Duração (meses)', 0, 60, None, placeholder='12 <- 1 ano')
        beneficios = st.text_input('Benefícios', placeholder='Acesso a área de natação')

        if st.form_submit_button('Cadastrar Plano', width='stretch'):
            if not all([nome, preco, duracao, beneficios]):
                st.error('Todas as informações devem ser fornecidas.')
                return

            conn = get_conn()
            c = conn.cursor()

            try:
                c.execute('INSERT INTO plano (nome, preco, duracao_meses, beneficios) VALUES (?, ?, ?, ?)', (nome, preco, duracao, beneficios))
                conn.commit()

                st.success(f'Plano {nome} cadastrado com sucesso!')
                time.sleep(0.7)
                st.rerun()
            
            except Exception as e:
                conn.rollback()
                st.error(f'Erro ao cadastrar plano: {e}')

            finally:
                conn.close()

@st.dialog('Editar Plano')
def editar_plano():
    if st.session_state.get('editar_plano_aberto') != id(st.session_state):
        if 'plano_encontrado' in st.session_state:
            del st.session_state.plano_encontrado
        st.session_state.editar_plano_aberto = id(st.session_state)

    if 'plano_encontrado' not in st.session_state:
        st.subheader('Busque um plano pelo nome')

        with st.form('buscar_plano_form'):
            
            nome = st.selectbox('Nome', listar_planos())

            col1, col2 = st.columns(2)
            with col1:
                buscar = st.form_submit_button('Procurar Plano', width='stretch')
            
            with col2:
                if st.form_submit_button('Cancelar', width='stretch'):
                    st.rerun()

            if buscar:
                if not nome:
                    st.error('Informe o nome do plano.')
                    return
                
                conn = get_conn()
                c = conn.cursor()

                try:
                    c.execute('SELECT id_plano, nome, preco, duracao_meses, beneficios FROM plano WHERE nome = ?', (nome,))
                    resultado = c.fetchone()
                    conn.close()

                    if resultado:
                        st.session_state.plano_encontrado = {
                            'id_plano': resultado[0],
                            'nome': resultado[1],
                            'preco': resultado[2],
                            'duracao': resultado[3],
                            'beneficios': resultado[4]
                        }

                        st.success(f'Plano encontrado: {resultado[1]} (R$ {resultado[2]})')
                        time.sleep(0.7)
                        st.rerun()

                    else:
                        st.error('Plano não encontrado ou nome incorreto.')

                except Exception as e:
                    st.error(f'Erro ao procurar plano: {e}')
    else:
        plano = st.session_state.plano_encontrado
        st.subheader(f'Editando: {plano['nome']}')

        with st.form('editar_aluno_form'):
            novo_nome = st.text_input('Nome', plano['nome'], placeholder='Mensal Básico')
            novo_preco = st.number_input('Preço', 0.00, 99999.99, plano['preco'], placeholder='99,99')
            nova_duracao = st.number_input('Duração (meses)', 0, 60, plano['duracao'], placeholder='12 <- 1 ano')
            novo_beneficio = st.text_input('Benefícios', plano['beneficios'], placeholder='Acesso a área de natação')

            col1, col2 = st.columns(2)
            with col1:
                salvar = st.form_submit_button('Salvar Alterações', width='stretch')
            
            with col2:
                cancelar = st.form_submit_button('Cancelar', width='stretch')

            if salvar:
                if not all([novo_nome, novo_preco, nova_duracao, novo_beneficio]):
                    st.error('Todos os campos devem estar preenchidos')
                    return
                
                else:
                    conn = get_conn()
                    c = conn.cursor()

                    try:
                        c.execute('UPDATE plano SET nome = ?, preco = ?, duracao_meses = ?, beneficios = ? WHERE id_plano = ?', (novo_nome, novo_preco, nova_duracao, novo_beneficio, plano['id_plano']))
                        conn.commit()
                        conn.close()

                        st.success('Plano atualizado com sucesso!')
                        time.sleep(0.7)
                        
                        del st.session_state.plano_encontrado
                        st.rerun()

                    except Exception as e:
                        st.error(f'Erro ao salvar plano: {e}')
            
            if cancelar:
                del st.session_state.plano_encontrado
                st.rerun()

@st.dialog('Deletar Plano')
def deletar_plano():
    with st.form('deletar_aluno'):
        st.warning('Esta ação não pode ser desfeita!')
        nome = st.text_input('Nome do Plano', placeholder='Mensal Básico')

        confirmar = st.checkbox('Sim, eu tenho certeza que quero deletar este plano.')
        form_button = st.form_submit_button('Deletar Plano', width='stretch')

        if form_button and confirmar:
            if not nome:
                st.error('Informe o nome do plano.')
                return
            
            conn = get_conn()
            c  = conn.cursor()

            try:
                c.execute('DELETE FROM plano WHERE nome = ?', (nome,))
                if c.rowcount == 0:
                    st.error('Plano não encontrado.')
                else:
                    conn.commit()
                    st.success('Plano removido com sucesso. Recarregando página...')
                    time.sleep(0.7)
                    st.rerun()

            except Exception as e:
                st.error(f'Erro ao remover plano: {e}')

            finally:
                conn.close()

        if form_button and not confirmar:
            st.warning('É necessário confirmar antes de excluir.')
            return

col1, col2, col3 = st.columns(3)
with col1:
    if st.button('Cadastrar Plano', width='stretch'):
        cadastrar_plano()

with col2:
    if st.button('Editar Plano', width='stretch'):
        editar_plano()

with col3:
    if st.button('Deletar Plano', width='stretch', type='primary'):
        deletar_plano()