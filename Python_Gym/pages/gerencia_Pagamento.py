import streamlit as st
import pandas as pd
import time
from database import get_conn

st.set_page_config(page_title="Gerenciar Pagamentos")

st.title("Gerenciar Pagamentos")

def carregar_dados():
    conn = get_conn()
    dados = pd.read_sql('''SELECT 
                            ps.nome, 
                            p.valor, 
                            p.metodo, 
                            p.data, 
                            p.status 
                        FROM pagamento p
                        INNER JOIN aluno a ON p.id_aluno = a.id_aluno 
                        INNER JOIN pessoa ps ON a.id_pessoa = ps.id_pessoa
                        ''', conn)
    conn.close()
    return dados

df = carregar_dados()

if df.empty:
    st.info('Nenhum pagamento foi registrado ainda.')
else:
    st.dataframe(df)

@st.dialog('Registrar Pagamento')
def registrar_pagamento():
    with st.form('registrar_pagamento'):
        cpf = st.text_input('CPF', placeholder='000.000.000-00 ou 98765432100')
        valor = st.number_input('Valor', 00.00, 99999.99, None, placeholder='99,99')
        metodo = st.selectbox('Método de pagamento', ['Débito', 'Crédito', 'Boleto', 'Dinheiro'])
        data_vencimento = st.date_input('Data do vencimento').isoformat()
        status = st.selectbox('Status', ['Pendente', 'Pago', 'Atrasado', 'Cancelado'])

        if st.form_submit_button('Registrar Pagamento', width='stretch'):
            if not all([cpf, valor, metodo, data_vencimento, status]):
                st.error('Todos os campos devem estar preenchidos.')
                return
            
            cpf_limpo = cpf.replace('.', '').replace('-', '').replace(' ', '')

            if len(cpf_limpo) != 11 or not cpf_limpo.isdigit():
                st.error('CPF inválido! O CPF precisa ter 11 dígitos.')
                return
            
            conn = get_conn()
            c = conn.cursor()

            try:
                c.execute('SELECT a.id_aluno FROM aluno a INNER JOIN pessoa p ON a.id_pessoa = p.id_pessoa WHERE p.cpf = ?', (cpf_limpo,))
                resultado = c.fetchone()

                if not resultado:
                    st.error('CPF não registrado.')
                    return
                
                id_aluno = resultado[0]
                print('Teste', resultado)

                c.execute('INSERT INTO pagamento (id_aluno, valor, metodo, data, status) VALUES (?, ?, ?, ?, ?)', (id_aluno, valor, metodo, data_vencimento, status))
                conn.commit()
                st.success('Pagamento registrado com sucesso!')
                time.sleep(0.7)
                st.rerun()

            except Exception as e:
                conn.rollback()
                st.error(f'Erro ao registrar pagamento: {e}')

            finally:
                conn.close()

@st.dialog('Editar Pagamento')
def editar_pagamento():
    if st.session_state.get('editar_pagamento_aberto') != id(st.session_state):
        for key in ['pagamentos_encontrados', 'pagamento_selecionado']:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.editar_pagamento_aberto = id(st.session_state)

    if 'pagamentos_encontrados' not in st.session_state:
        st.subheader('Busque um pagamento pelo CPF')

        with st.form('buscar_pagamento_form'):
            
            cpf = st.text_input('CPF', placeholder='000.000.000-00 ou 98765432100')

            col1, col2 = st.columns(2)
            with col1:
                buscar = st.form_submit_button('Procurar Pagamento', width='stretch')
            
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
                    c.execute('SELECT pg.id_pagamento, p.nome, p.cpf, pg.valor, pg.metodo, pg.data, pg.status FROM pagamento pg INNER JOIN aluno a ON pg.id_aluno = a.id_aluno INNER JOIN pessoa p ON a.id_pessoa = p.id_pessoa WHERE cpf = ?', (cpf_limpo,))
                    resultados = c.fetchall()
                    conn.close()
                    
                    if resultados:
                        st.session_state.pagamentos_encontrados = [
                            {
                                "id_pagamento": r[0],
                                "nome_aluno": r[1],
                                "cpf": r[2],
                                "valor": r[3],
                                "metodo": r[4],
                                "data": r[5],
                                "status": r[6] 
                            }
                            for r in resultados
                        ]

                        st.success(f'{len(resultados)} pagamento(s) encontrado(s) para este CPF.')
                        time.sleep(0.7)
                        st.rerun()
                    
                    else:
                        st.error('Nenhum pagamento encontrado para este CPF.')
                    
                except Exception as e:
                    st.error(f'Erro na busca: {e}')

    elif 'pagamento_selecionado' not in st.session_state:
        st.subheader(f"Pagamentos de {st.session_state.pagamentos_encontrados[0]['nome_aluno']}")

        opcoes = [
            f"ID {p['id_pagamento']} • {p['data']} • {p['valor']} • {p['metodo']} • {p['status']}"
            for p in st.session_state.pagamentos_encontrados
        ]
        escolha = st.radio("Selecione o pagamento para editar:", opcoes, index=None)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Editar selecionado", width='stretch', type="primary"):
                if not escolha:
                    st.error("Selecione um pagamento!")
                else:
                    idx = opcoes.index(escolha)
                    st.session_state.pagamento_selecionado = st.session_state.pagamentos_encontrados[idx]
                    st.rerun()
        with col2:
            if st.button("Voltar", width='stretch'):
                del st.session_state.pagamentos_encontrados
                st.rerun()
    
    else:
        pag = st.session_state.pagamento_selecionado
        st.subheader(f"Editando Pagamento ID {pag['id_pagamento']}")

        with st.form("form_editar_pagamento"):
            novo_valor = st.number_input("Valor (R$)", min_value=0.01, value=pag['valor'])
            novo_metodo = st.selectbox("Método", ['Débito', 'Crédito', 'Boleto', 'Dinheiro'], index=['Débito', 'Crédito', 'Boleto', 'Dinheiro'].index(pag['metodo']))
            nova_data = st.date_input("Data do pagamento", value=pd.to_datetime(pag['data']))
            novo_status = st.selectbox("Status", ["Pago", "Pendente", "Atrasado", "Cancelado"], index=["Pago", "Pendente", "Atrasado", "Cancelado"].index(pag['status']))

            col1, col2 = st.columns(2)
            with col1:
                salvar = st.form_submit_button("Salvar Alterações", width='stretch', type="primary")
            with col2:
                cancelar = st.form_submit_button("Cancelar", width='stretch')

            if salvar:
                conn = get_conn()
                c = conn.cursor()
                try:
                    c.execute("""
                        UPDATE pagamento SET valor=?, metodo=?, data=?, status=?
                        WHERE id_pagamento=?
                    """, (novo_valor, novo_metodo, nova_data, novo_status, pag['id_pagamento']))
                    conn.commit()
                    st.success("Pagamento atualizado com sucesso!")
                    time.sleep(1.5)
                    # Limpa tudo e volta pro início
                    for key in ['pagamentos_encontrados', 'pagamento_selecionado', 'editar_pagamento_aberto']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")
                finally:
                    conn.close()

            if cancelar:
                del st.session_state.pagamento_selecionado
                st.rerun()

@st.dialog('Deletar Pagamento')
def deletar_pagamento():
    if st.session_state.get('deletar_pagamento_aberto') != id(st.session_state):
        if 'pagamentos_encontrados_delete' in st.session_state:
            del st.session_state.pagamentos_encontrados_delete
        st.session_state.deletar_pagamento_aberto = id(st.session_state)

    if 'pagamentos_encontrados_delete' not in st.session_state:
        st.subheader('Busque um pagamento pelo CPF')

        with st.form('buscar_pagamento_form'):
            
            cpf = st.text_input('CPF', placeholder='000.000.000-00 ou 98765432100')

            col1, col2 = st.columns(2)
            with col1:
                buscar = st.form_submit_button('Procurar Pagamento', width='stretch')
            
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
                    c.execute('SELECT pg.id_pagamento, p.nome, p.cpf, pg.valor, pg.metodo, pg.data, pg.status FROM pagamento pg INNER JOIN aluno a ON pg.id_aluno = a.id_aluno INNER JOIN pessoa p ON a.id_pessoa = p.id_pessoa WHERE cpf = ?', (cpf_limpo,))
                    resultados = c.fetchall()
                    conn.close()
                    
                    if resultados:
                        st.session_state.pagamentos_encontrados_delete = [
                            {
                                "id_pagamento": r[0],
                                "nome_aluno": r[1],
                                "cpf": r[2],
                                "valor": r[3],
                                "metodo": r[4],
                                "data": r[5],
                                "status": r[6] 
                            }
                            for r in resultados
                        ]

                        st.success(f'{len(resultados)} pagamento(s) encontrado(s) para este CPF.')
                        time.sleep(0.7)
                        st.rerun()
                    
                    else:
                        st.error('Nenhum pagamento encontrado para este CPF.')
                    
                except Exception as e:
                    st.error(f'Erro na busca: {e}')

    else:
        st.subheader(f"Pagamentos de {st.session_state.pagamentos_encontrados_delete[0]['nome_aluno']}")

        opcoes = [
            f"ID {p['id_pagamento']} • {p['data']} • {p['valor']} • {p['metodo']} • {p['status']}"
            for p in st.session_state.pagamentos_encontrados_delete
        ]
        escolha = st.radio("Selecione o pagamento para deletar:", opcoes, index=None)
        st.warning('Esta ação não pode ser desfeita!')
        confirmar = st.checkbox('Sim, eu tenho certeza que quero deletar este pagamento.')

        col1, col2 = st.columns(2)
        with col1:
            form_button = st.button("Deletar selecionado", width='stretch', type="primary")
            
            if form_button and confirmar:
                if not escolha:
                    st.error("Selecione um pagamento!")
                else:
                    idx = opcoes.index(escolha)
                    escolhido = st.session_state.pagamentos_encontrados_delete[idx]

                    conn = get_conn()
                    c = conn.cursor()

                    try:
                        c.execute('DELETE FROM pagamento WHERE id_pagamento = ?', (escolhido['id_pagamento'],))
                        conn.commit()

                        st.success('Pagamento removido com sucesso. Recarregando página.')
                        time.sleep(0.7)
                        st.rerun()
                    
                    except Exception as e:
                        conn.rollback()
                        st.error(f'Erro ao deletar: {e}')

                    finally:
                        conn.close()
            
        with col2:
            if st.button("Voltar", width='stretch'):
                del st.session_state.pagamentos_encontrados_delete
                st.rerun()

        if form_button and not confirmar:
                st.warning('É necessário confirmar antes de excluir.', width='stretch')
                return

col1, col2, col3 = st.columns(3)
with col1:
    if st.button('Registrar Pagamento', width='stretch'):
        registrar_pagamento()

with col2:
    if st.button('Editar Pagamento', width='stretch'):
        editar_pagamento()

with col3:
    if st.button('Deletar Pagamento', width='stretch', type='primary'):
        deletar_pagamento()

