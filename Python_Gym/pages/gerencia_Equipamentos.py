import streamlit as st
import pandas as pd
import time
from database import get_conn

st.set_page_config( 
    page_title="Gerenciar Equipamentos",)

st.title("Gerenciar Equipamentos")

def carregar_equipamentos():
    conn = get_conn()
    df = pd.read_sql('SELECT nome as "None", tipo AS "Tipo", estado as "Estado", observacoes AS "Observações" FROM equipamento', conn)
    conn.close()
    return df

df = carregar_equipamentos()

if df.empty:
    st.info('Nenhum equipamento cadastrado ainda.')
else:
    st.dataframe(df, width='stretch')

def listar_equipamentos():
    conn = get_conn()
    lista = pd.read_sql('SELECT concat("(", id_equipamento, ") ", nome) AS "nome" FROM equipamento', conn)
    conn.close()
    return lista['nome'].tolist()

@st.dialog('Cadastrar Equipamento')
def cadastrar_equipamento():
    with st.form('cadastrar_equipamento'):
        st.subheader('Preencha com os dados do equipamento')
        nome = st.text_input('Nome', placeholder='Legpress 45')
        tipo = st.selectbox('Tipo', ['Cardio', 'Musculação', 'Funcional', 'Acessórios', 'Peso livre'])
        estado = st.selectbox('Estado', ['Disponivel', 'Em manutenção', 'Quebrado', 'Desativado'])
        observacoes = st.text_area('Observações', placeholder='Maquina da marca X, código X')

        if st.form_submit_button('Cadastrar Equipamento'):
            if not all([nome, tipo, estado]):
                st.error('Nome, tipo e estado são obrigatórios.')
                return
            
            conn = get_conn()
            c = conn.cursor()

            try:
                c.execute('INSERT INTO equipamento (nome, tipo, estado, observacoes) VALUES (?, ?, ?, ?)', (nome, tipo, estado, observacoes or None))
                conn.commit()

                st.success(f'Equipamento {nome} cadastrado com sucesso!')
                time.sleep(0.7)
                st.rerun()

            except Exception as e:
                st.error(f'Erro ao cadastrar: {e}')

            finally:
                conn.close()

@st.dialog('Editar Equipamento')
def editar_equipamento():
    if st.session_state.get('editar_equipamento_aberto') != id(st.session_state):
        if 'equipamento_encontrado' in st.session_state:
            del st.session_state.equipamento_encontrado
        st.session_state.editar_equipamento_aberto = id(st.session_state)

    if 'equipamento_encontrado' not in st.session_state:
        st.subheader('Busque um equipamento pelo nome')

        with st.form('buscar_equipamento_form'):
            
            nome = st.selectbox('Equipamento', listar_equipamentos()).split(') ')[1]

            col1, col2 = st.columns(2)
            with col1:
                buscar = st.form_submit_button('Procurar Equipamento', width='stretch')
            
            with col2:
                if st.form_submit_button('Cancelar', width='stretch'):
                    st.rerun()

            if buscar:
                if not nome:
                    st.error('Informe o nome do equipamento.')
                    return

                conn = get_conn()
                c = conn.cursor()

                try: 
                    c.execute('SELECT id_equipamento, nome, tipo, estado, observacoes FROM equipamento WHERE nome = ?', (nome,))
                    resultado = c.fetchone()
                    conn.close()
                    
                    if resultado:
                        st.session_state.equipamento_encontrado = {
                            'id_equipamento': resultado[0],
                            'nome': resultado[1],
                            'tipo': resultado[2],
                            'estado': resultado[3],
                            'observacoes': resultado[4] or '',
                        }

                        st.success(f'Equipamento encontrado: {resultado[1]} ({resultado[2]})')
                        time.sleep(0.7)
                        st.rerun()
                    
                    else:
                        st.error('Equipamento não encontrado com este nome.')
                except Exception as e:
                    st.error(f'Erro ao procurar equipamento: {e}')

    else:
        equipamento = st.session_state.equipamento_encontrado
        st.subheader(f'Editando: {equipamento['nome']}')

        with st.form('editar_equipamento_form'):
            novo_nome = st.text_input('Nome', equipamento['nome'])
            novo_tipo = st.selectbox('Tipo', ['Cardio', 'Musculação', 'Funcional', 'Acessórios', 'Peso livre'], ['Cardio', 'Musculação', 'Funcional', 'Acessórios', 'Peso livre'].index(equipamento['tipo']))
            novo_estado = st.selectbox('Estado', ['Disponivel', 'Em manutenção', 'Quebrado', 'Desativado'], ['Disponivel', 'Em manutenção', 'Quebrado', 'Desativado'].index(equipamento['estado']))
            nova_observacao = st.text_input('Observações', equipamento['observacoes'])

            col1, col2 = st.columns(2)

            with col1:
                salvar = st.form_submit_button('Salvar alterações', width='stretch', type='primary')
            
            with col2:
                cancelar = st.form_submit_button('Cancelar', width='stretch')

            if salvar:
                if not all([novo_nome, novo_tipo, novo_estado]):
                    st.error('Nome, tipo e estado são obrigatórios.')
                    return
                
                else:
                    conn = get_conn()
                    c = conn.cursor()

                    try:
                        c.execute('UPDATE equipamento SET nome = ?, tipo = ?, estado = ?, observacoes = ? WHERE id_equipamento = ?', (novo_nome, novo_tipo, novo_estado, nova_observacao, equipamento['id_equipamento']))
                        conn.commit()
                        conn.close()

                        st.success('Equipamento atualizado com sucesso!')
                        time.sleep(1)

                        del st.session_state.equipamento_encontrado
                        st.rerun()
                    
                    except Exception as e:
                        st.error(f'Erro ao salvar equipamento: {e}')
            
            if cancelar:
                del st.session_state.equipamento_encontrado
                st.rerun()

@st.dialog('Deletar Equipamento')
def deletar_equipamento():
    with st.form('deletar_equipamento'):
        st.warning('Esta ação não pode ser desfeita!')
        id_equipamento = st.selectbox('Equipamento', listar_equipamentos()).split(') ')[0].replace('(', '').replace(' ', '')

        confirmar = st.checkbox('Sim, eu tenho certeza que quero deletar este equipamento.')
        form_button = st.form_submit_button('Deletar equipamento', width='stretch')
        if form_button and confirmar:
            if not id_equipamento:
                st.error('Informe o nome do equipamento.')
                return
            
            conn = get_conn()
            c = conn.cursor()

            try:
                c.execute('DELETE FROM equipamento WHERE id_equipamento = ?', (id_equipamento,))
                if c.rowcount == 0:
                    st.error('Equipamento não encontrado.')
                else:
                    conn.commit()
                    st.success('Equipamento removido com sucesso. Recarregando pagina...')
                    time.sleep(2)
                    st.rerun()
            
            except Exception as e:
                st.error(f'Erro ao remover equipamento: {e}')
            
            finally:
                conn.close()
        
        if form_button and not confirmar:
            st.warning('É necessário confirmar antes de excluir.')
            return

col1, col2, col3 = st.columns(3)
with col1:
    if st.button('Cadastrar Equipamento', width='stretch'):
        cadastrar_equipamento()

with col2:
    if st.button('Editar Equipamento', width='stretch'):
        editar_equipamento()

with col3:
    if st.button('Deletar Equipamento', width='stretch', type='primary'):
        deletar_equipamento()