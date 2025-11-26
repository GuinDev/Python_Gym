import streamlit as st
import pandas as pd
import time
from database import get_conn

st.set_page_config(page_title="Gerenciar Treinos")
st.title("Gerenciar Treinos")

def carregar_treinos():
    conn = get_conn()
    query = """
        SELECT 
            t.id_treino,
            p_aluno.nome AS aluno,
            p_instrutor.nome AS instrutor,
            h.data_inicio,
            t.status
        FROM treino t
        INNER JOIN aluno a ON t.id_aluno = a.id_aluno
        INNER JOIN pessoa p_aluno ON a.id_pessoa = p_aluno.id_pessoa
        INNER JOIN instrutor i ON t.id_instrutor = i.id_instrutor
        INNER JOIN pessoa p_instrutor ON i.id_pessoa = p_instrutor.id_pessoa
        INNER JOIN horario h ON t.id_horario = h.id_horario
        ORDER BY h.data_inicio DESC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

df = carregar_treinos()

if df.empty:
    st.info("Nenhum treino cadastrado ainda.")
else:
    st.dataframe(df, use_container_width=True)

def listar_alunos():
    conn = get_conn()
    df = pd.read_sql("""
        SELECT a.id_aluno, '(' || a.id_aluno || ') ' || p.nome AS nome_com_id
        FROM aluno a
        INNER JOIN pessoa p ON a.id_pessoa = p.id_pessoa
        ORDER BY p.nome
    """, conn)
    conn.close()
    return df["nome_com_id"].tolist()

def listar_instrutores():
    conn = get_conn()
    df = pd.read_sql("""
        SELECT i.id_instrutor, '(' || i.id_instrutor || ') ' || p.nome AS nome_com_id
        FROM instrutor i
        INNER JOIN pessoa p ON i.id_pessoa = p.id_pessoa
        ORDER BY p.nome
    """, conn)
    conn.close()
    return df["nome_com_id"].tolist()

def listar_horarios_disponiveis():
    conn = get_conn()
    df = pd.read_sql("""
        SELECT 
            h.id_horario,
            CONCAT(p.nome, '(', h.data_inicio, ' - ', h.data_fim, ')') AS instrutor,       
            h.sala,
            i.id_instrutor
        FROM horario h
        INNER JOIN horario_disponivel hd ON h.id_horario = hd.id_horario
        INNER JOIN instrutor i ON hd.id_instrutor = i.id_instrutor
        INNER JOIN pessoa p ON i.id_pessoa = p.id_pessoa
        ORDER BY h.data_inicio
    """, conn)
    conn.close()
    return df

def criar_horario_fim(horario_inicio_str):
    try:
        hora = int(horario_inicio_str.split(':')[0])  # pega só a hora
        hora_fim = (hora + 1) % 24  # 23 + 1 = 0 (meia-noite)
        return f"{hora_fim:02d}:00:00"  # sempre 2 dígitos: 09:00:00
    except:
        raise ValueError("Formato de horário inválido. Use HH:00:00")

def get_aluno_treino():
    conn = get_conn()
    ids = pd.read_sql('SELECT CONCAT("(", t.id_treino, ") ", p.nome) AS treino FROM treino t INNER JOIN aluno a ON t.id_aluno = a.id_aluno INNER JOIN pessoa p ON a.id_pessoa = p.id_pessoa', conn)
    conn.close()
    return ids
    
df = st.dataframe(get_aluno_treino())

@st.dialog("Cadastrar Treino")
def cadastrar_treino():
    st.subheader("Novo Treino Personal")

    with st.form("form_cadastrar_treino"):
        aluno_str = st.selectbox("Aluno", ["Selecione..."] + listar_alunos())
        horario_dados = listar_horarios_disponiveis()
        instrutor_str = st.selectbox("Instrutor", ["Selecione..."] + horario_dados['instrutor'].tolist())
        horario_str = st.time_input("Horário", '00', step=3600).isoformat()

        if st.form_submit_button("Cadastrar Treino", type="primary", width='stretch'):
            if "Selecione..." in [aluno_str, instrutor_str, horario_str]:
                st.error("Preencha todos os campos!")
                return

            conn = get_conn()
            c = conn.cursor()

            try:
                id_aluno = int(aluno_str.split(")")[0].replace("(", ""))

                c.execute('INSERT INTO horario (data_inicio, data_fim) VALUES (?, ?)', (horario_str, criar_horario_fim(horario_str)))
                id_horario = c.lastrowid

                instrutor_str = str(instrutor_str.split('(')[0])
                c.execute('SELECT i.id_instrutor FROM instrutor i INNER JOIN pessoa p ON i.id_pessoa = p.id_pessoa WHERE p.nome = ?', (instrutor_str,))
                id_instrutor = c.fetchone()[0]

                status = 'Agendado'
                c.execute('INSERT INTO treino (id_aluno, id_instrutor, id_horario, status) VALUES (?, ?, ?, ?)', (id_aluno, id_instrutor, id_horario, status))
                
                conn.commit()
                st.success('Treino cadastrado com sucesso!')
                time.sleep(0.7)
                st.rerun()

            except Exception as e:
                st.error(f'Erro ao cadastrar: {e}')

            finally:
                conn.close()

@st.dialog("Deletar Treino")
def deletar_treino():
    with st.form("form_deletar_treino"):
        st.warning("Esta ação não pode ser desfeita!")
        treinos = get_aluno_treino()
        treino = st.selectbox("Treino", treinos['treino'].tolist())
        confirmar = st.checkbox("Sim, eu tenho certeza")

        if st.form_submit_button("Deletar Permanentemente", width='stretch', type="primary"):
            if not confirmar:
                st.error("Você precisa confirmar a exclusão.")
            else:
                conn = get_conn()
                c = conn.cursor()
                try:
                    id_treino = str(treino).split(' ')[0].replace('(', '').replace(')', '')
                    c.execute("DELETE FROM treino WHERE id_treino = ?", (id_treino,))
                    if c.rowcount > 0:
                        conn.commit()
                        st.success("Treino removido com sucesso!")
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        st.error("Treino não encontrado.")
                except Exception as e:
                    st.error(f"Erro: {e}")
                finally:
                    conn.close()

col1, col2 = st.columns(2)
with col1:
    if st.button("Cadastrar Treino", use_container_width=True):
        cadastrar_treino()

with col2:
    if st.button("Deletar Treino", use_container_width=True, type='primary'):
        deletar_treino()