import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = "data/database.db"

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    c = conn.cursor()

    #Tabelas sem chave estrangeira
    c.execute('''CREATE TABLE IF NOT EXISTS pessoa (
              id_pessoa INTEGER PRIMARY KEY AUTOINCREMENT,
              nome TEXT NOT NULL,
              cpf TEXT UNIQUE NOT NULL,
              telefone TEXT,
              email TEXT UNIQUE
              )''')

    c.execute('''CREATE TABLE IF NOT EXISTS plano (
              id_plano INTEGER PRIMARY KEY AUTOINCREMENT,
              nome TEXT NOT NULL,
              preco DECIMAL(10, 2) NOT NULL,
              duracao_meses INTEGER NOT NULL,
              beneficios TEXT
              )''')

    c.execute('''CREATE TABLE IF NOT EXISTS horario (
              id_horario INTEGER PRIMARY KEY AUTOINCREMENT,
              data_inicio DATETIME NOT NULL,
              data_fim DATETIME NOT NULL,
              sala TEXT
              )''')

    c.execute('''CREATE TABLE IF NOT EXISTS equipamento (
              id_equipamento INTEGER PRIMARY KEY AUTOINCREMENT,
              nome TEXT NOT NULL,
              tipo TEXT,
              estado TEXT NOT NULL,
              manual TEXT
              )''')

    c.execute('''CREATE TABLE IF NOT EXISTS exercicio (
              id_exercicio INTEGER PRIMARY KEY AUTOINCREMENT,
              nome TEXT NOT NULL,
              repeticoes INTEGER,
              series INTEGER
              )''')

    #Tabelas com chave estrangeira
    c.execute('''CREATE TABLE IF NOT EXISTS aluno (
              id_aluno INTEGER PRIMARY KEY AUTOINCREMENT,
              id_pessoa INTEGER UNIQUE NOT NULL,
              historico_saude TEXT,
              objetivos TEXT,
              id_plano INTEGER,
              FOREIGN KEY (id_pessoa) REFERENCES pessoa(id_pessoa)
                ON DELETE CASCADE ON UPDATE CASCADE,
              FOREIGN KEY (id_plano) REFERENCES plano(id_plano)
                ON DELETE SET NULL ON UPDATE CASCADE
              )''')

    c.execute('''CREATE TABLE IF NOT EXISTS instrutor (
              id_instrutor INTEGER PRIMARY KEY AUTOINCREMENT,
              id_pessoa INTEGER UNIQUE NOT NULL,
              especialidades TEXT,
              FOREIGN KEY (id_pessoa) REFERENCES pessoa(id_pessoa)
                ON DELETE CASCADE ON UPDATE CASCADE
              )''')

    c.execute('''CREATE TABLE IF NOT EXISTS pagamento (
              id_pagamento INTEGER PRIMARY KEY AUTOINCREMENT,
              id_aluno INTEGER NOT NULL,
              valor DECIMAL(10, 2) NOT NULL,
              metodo TEXT NOT NULL,
              data DATE NOT NULL,
              status TEXT NOT NULL,
              FOREIGN KEY (id_aluno) REFERENCES aluno(id_aluno)
                ON DELETE CASCADE ON UPDATE CASCADE
            )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS treino (
              id_treino INTEGER PRIMARY KEY AUTOINCREMENT,
              id_aluno INTEGER NOT NULL,
              id_instrutor INTEGER NOT NULL,
              id_horario INTEGER NOT NULL,
              status TEXT NOT NULL,
              FOREIGN KEY (id_aluno) REFERENCES aluno(id_aluno)
                ON DELETE CASCADE ON UPDATE CASCADE,
              FOREIGN KEY (id_instrutor) REFERENCES instrutor(id_instrutor)
                ON DELETE CASCADE ON UPDATE CASCADE,
              FOREIGN KEY (id_horario) REFERENCES horario(id_horario)
                ON DELETE CASCADE ON UPDATE CASCADE
              )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS frequencia (
              id_frequencia INTEGER PRIMARY KEY AUTOINCREMENT,
              id_aluno INTEGER NOT NULL,
              data DATE NOT NULL,
              tipo_aula TEXT,
              status TEXT NOT NULL,
              FOREIGN KEY (id_aluno) REFERENCES aluno(id_aluno)
                ON DELETE CASCADE ON UPDATE CASCADE
              )''')
    
    #Tabelas de relacionamento
    c.execute('''CREATE TABLE IF NOT EXISTS treino_equipamento (
              id_treino INTEGER NOT NULL,
              id_equipamento INTEGER NOT NULL,
              PRIMARY KEY (id_treino, id_equipamento),
              FOREIGN KEY (id_treino) REFERENCES treino(id_treino)
                ON DELETE CASCADE ON UPDATE CASCADE,
              FOREIGN KEY (id_equipamento) REFERENCES equipamento(id_equipamento)
                ON DELETE CASCADE ON UPDATE CASCADE
              )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS treino_exercicio (
              id_treino INTEGER NOT NULL,
              id_exercicio INTEGER NOT NULL,
              PRIMARY KEY (id_treino, id_exercicio),
              FOREIGN KEY (id_treino) REFERENCES treino(id_treino)
                ON DELETE CASCADE ON UPDATE CASCADE,
              FOREIGN KEY (id_exercicio) REFERENCES exercicio(id_exercicio)
                ON DELETE CASCADE ON UPDATE CASCADE
              )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS horario_disponivel (
              id_instrutor INTEGER NOT NULL,
              id_horario INTEGER NOT NULL,
              PRIMARY KEY (id_instrutor, id_horario),
              FOREIGN KEY (id_instrutor) REFERENCES instrutor(id_instrutor)
                ON DELETE CASCADE ON UPDATE CASCADE
              FOREIGN KEY (id_horario) REFERENCES horario(id_horario)
                ON DELETE CASCADE ON UPDATE CASCADE
              )''')
    
    #Indexes
    c.execute("CREATE INDEX IF NOT EXISTS idx_cpf ON pessoa(cpf)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_email ON pessoa(email)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_nome_plano ON plano(nome)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_data_inicio ON horario(data_inicio)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_nome_equip ON equipamento(nome)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_nome_ex ON exercicio(nome)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_data_pagamento ON pagamento(data)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_status_pag ON pagamento(status)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_data_freq ON frequencia(data)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_status_freq ON frequencia(status)")

    # índices compostos das tabelas de relacionamento
    c.execute("CREATE INDEX IF NOT EXISTS idx_treino_equip ON treino_equipamento(id_treino, id_equipamento)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_treino_ex ON treino_exercicio(id_treino, id_exercicio)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_horario_disp ON horario_disponivel(id_instrutor, id_horario)")

    conn.commit()
    conn.close()

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    return conn