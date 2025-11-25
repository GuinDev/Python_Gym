# popular_db.py
import sqlite3
import random
from datetime import datetime, timedelta
import os

DB_PATH = "data/database.db"

# Cria a pasta se não existir
os.makedirs("data", exist_ok=True)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# -------------------------------------------------------------------------
# 1. PLANOS
# -------------------------------------------------------------------------
planos = [
    ("Mensal Básico", 89.90, 1, "Acesso das 6h às 22h"),
    ("Mensal Premium", 129.90, 1, "Acesso 24h + todas as aulas coletivas"),
    ("Trimestral", 239.70, 3, "Desconto de 10% + brinde"),
    ("Anual", 899.90, 12, "Melhor custo-benefício + 1 mês grátis"),
]

for p in planos:
    c.execute("INSERT OR IGNORE INTO plano (nome, preco, duracao_meses, beneficios) VALUES (?, ?, ?, ?)", p)

# -------------------------------------------------------------------------
# 2. PESSOAS + ALUNOS e INSTRUTORES
# -------------------------------------------------------------------------
alunos_nomes = [
    ("Ana Silva", "11122233344", "ana@email.com", "21999887766"),
    ("Bruno Costa", "22233344455", "bruno@email.com", "21988776655"),
    ("Carla Oliveira", "33344455566", "carla@email.com", "21977665544"),
    ("Diego Santos", "44455566677", "diego@email.com", "21966554433"),
    ("Eduarda Lima", "55566677788", "eduarda@email.com", "21955443322"),
    ("Felipe Almeida", "66677788899", "felipe@email.com", "21944332211"),
    ("Gabriela Rocha", "77788899900", "gabi@email.com", "21933221100"),
    ("Henrique Mendes", "88899900011", "henrique@email.com", "21922110099"),
]

instrutores_nomes = [
    ("Prof. Marcos", "99900011122", "marcos@academia.com", "21988774433"),
    ("Profª. Juliana", "00011122233", "juliana@academia.com", "21977443322"),
]

historicos = [
    "Sem restrições", "Dor no joelho esquerdo", "Hipertensão controlada", 
    "Asma leve", "Recuperação de lesão no ombro"
]
objetivos = [
    "Hipertrofia", "Emagrecimento", "Condicionamento físico", 
    "Ganho de força", "Melhora da mobilidade"
]

# Inserir alunos
aluno_ids = []
for nome, cpf, email, tel in alunos_nomes:
    c.execute("INSERT INTO pessoa (nome, cpf, email, telefone) VALUES (?, ?, ?, ?)", 
              (nome, cpf, email, tel))
    id_pessoa = c.lastrowid
    
    plano_id = random.choice([1, 2, 3, 4])  # id dos planos inseridos acima
    historico = random.choice(historicos)
    objetivo = random.choice(objetivos)
    
    c.execute("""INSERT INTO aluno (id_pessoa, historico_saude, objetivos, id_plano) 
                 VALUES (?, ?, ?, ?)""", (id_pessoa, historico, objetivo, plano_id))
    aluno_ids.append(c.lastrowid)

# Inserir instrutores
instrutor_ids = []
for nome, cpf, email, tel in instrutores_nomes:
    c.execute("INSERT INTO pessoa (nome, cpf, email, telefone) VALUES (?, ?, ?, ?)", 
              (nome, cpf, email, tel))
    id_pessoa = c.lastrowid
    
    especialidades = "Musculação, Crossfit" if "Marcos" in nome else "Funcional, Pilates, Yoga"
    c.execute("INSERT INTO instrutor (id_pessoa, especialidades) VALUES (?, ?)", 
              (id_pessoa, especialidades))
    instrutor_ids.append(c.lastrowid)

# -------------------------------------------------------------------------
# 3. PAGAMENTOS
# -------------------------------------------------------------------------
metodos = ["Pix", "Cartão de Crédito", "Dinheiro"]
status_pag = ["Pago", "Pendente", "Atrasado"]

for aluno_id in aluno_ids:
    for _ in range(random.randint(1, 4)):
        valor = round(random.uniform(80, 150), 2)
        metodo = random.choice(metodos)
        status = random.choice(status_pag)
        data = (datetime.now() - timedelta(days=random.randint(0, 180))).strftime("%Y-%m-%d")
        
        c.execute("""INSERT INTO pagamento (id_aluno, valor, metodo, data, status) 
                     VALUES (?, ?, ?, ?, ?)""", (aluno_id, valor, metodo, data, status))

# -------------------------------------------------------------------------
# 4. HORÁRIOS (aulas coletivas e treinos)
# -------------------------------------------------------------------------
horarios = [
    ("2025-01-10 07:00:00", "2025-01-10 08:00:00", "Sala 1 - Musculação"),
    ("2025-01-10 18:00:00", "2025-01-10 19:00:00", "Sala 2 - Funcional"),
    ("2025-01-11 08:00:00", "2025-01-11 09:00:00", "Sala 1 - Musculação"),
    ("2025-01-11 19:00:00", "2025-01-11 20:00:00", "Sala 3 - Pilates"),
]

horario_ids = []
for h in horarios:
    c.execute("INSERT INTO horario (data_inicio, data_fim, sala) VALUES (?, ?, ?)", h)
    horario_ids.append(c.lastrowid)

# Associar instrutores aos horários
for instr_id in instrutor_ids:
    for hor_id in random.sample(horario_ids, k=2):
        c.execute("INSERT OR IGNORE INTO horario_disponivel (id_instrutor, id_horario) VALUES (?, ?)", 
                  (instr_id, hor_id))

# -------------------------------------------------------------------------
# 5. TREINOS
# -------------------------------------------------------------------------
for aluno_id in aluno_ids:
    instr_id = random.choice(instrutor_ids)
    hor_id = random.choice(horario_ids)
    status_treino = random.choice(["Agendado", "Concluído", "Cancelado"])
    
    c.execute("""INSERT INTO treino (id_aluno, id_instrutor, id_horario, status) 
                 VALUES (?, ?, ?, ?)""", (aluno_id, instr_id, hor_id, status_treino))

# -------------------------------------------------------------------------
# 6. FREQUÊNCIA (algumas entradas aleatórias)
# -------------------------------------------------------------------------
for aluno_id in aluno_ids:
    for _ in range(random.randint(5, 20)):
        data = (datetime.now() - timedelta(days=random.randint(0, 60))).strftime("%Y-%m-%d")
        tipo = random.choice(["Musculação", "Aula Coletiva", "Treino Personal"])
        status = random.choice(["Presente", "Falta"])
        c.execute("""INSERT INTO frequencia (id_aluno, data, tipo_aula, status) 
                     VALUES (?, ?, ?, ?)""", (aluno_id, data, tipo, status))

# -------------------------------------------------------------------------
# FINALIZA
# -------------------------------------------------------------------------
conn.commit()
conn.close()

print("Banco populado com sucesso!")
print(f"→ {len(alunos_nomes)} alunos")
print(f"→ {len(instrutores_nomes)} instrutores")
print("→ Planos, pagamentos, treinos e frequência criados")
print("Agora pode rodar o Streamlit que vai aparecer tudo!")