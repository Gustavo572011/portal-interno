import sqlite3
import hashlib
import os

DB_PATH = "data/portal.db"

def get_conn():
    os.makedirs("data", exist_ok=True)
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()

    # Usuários
    c.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT,
            cargo TEXT DEFAULT 'Funcionário',
            google_id TEXT,
            meta_atual REAL DEFAULT 0,
            meta_total REAL DEFAULT 10000,
            ativo INTEGER DEFAULT 1,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Avisos
    c.execute("""
        CREATE TABLE IF NOT EXISTS avisos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            corpo TEXT NOT NULL,
            tipo TEXT DEFAULT 'info',
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
            ativo INTEGER DEFAULT 1
        )
    """)

    # Ponto
    c.execute("""
        CREATE TABLE IF NOT EXISTS ponto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            data TEXT NOT NULL,
            entrada TEXT,
            saida_almoco TEXT,
            retorno_almoco TEXT,
            saida_cafe TEXT,
            retorno_cafe TEXT,
            saida TEXT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)

    # Documentos
    c.execute("""
        CREATE TABLE IF NOT EXISTS documentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            descricao TEXT,
            arquivo_nome TEXT,
            status TEXT DEFAULT 'enviado',
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)

    # Seed: usuário admin de exemplo
    senha_hash = hashlib.sha256("admin123".encode()).hexdigest()
    c.execute("""
        INSERT OR IGNORE INTO usuarios (nome, email, senha, cargo, meta_atual, meta_total)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ("Admin", "admin@empresa.com", senha_hash, "Gerente", 7500, 10000))

    c.execute("""
        INSERT OR IGNORE INTO usuarios (nome, email, senha, cargo, meta_atual, meta_total)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ("João Silva", "joao@empresa.com", hashlib.sha256("123456".encode()).hexdigest(), "Vendedor", 4200, 8000))

    # Seed: avisos
    c.execute("""
        INSERT OR IGNORE INTO avisos (id, titulo, corpo, tipo)
        VALUES (1, '🎉 Reunião Mensal', 'Reunião de alinhamento na sexta-feira às 14h na sala de reuniões.', 'info')
    """)
    c.execute("""
        INSERT OR IGNORE INTO avisos (id, titulo, corpo, tipo)
        VALUES (2, '⚠️ Prazo de Metas', 'O fechamento do mês ocorre dia 30. Atenção ao cumprimento das metas!', 'warning')
    """)

    conn.commit()
    conn.close()

def get_user_by_email(email):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM usuarios WHERE email = ? AND ativo = 1", (email,))
    row = c.fetchone()
    conn.close()
    if row:
        cols = ["id","nome","email","senha","cargo","google_id","meta_atual","meta_total","ativo","criado_em"]
        return dict(zip(cols, row))
    return None

def get_user_by_google(google_id, email, nome):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM usuarios WHERE google_id = ? OR email = ?", (google_id, email))
    row = c.fetchone()
    if not row:
        c.execute("""
            INSERT INTO usuarios (nome, email, google_id, cargo)
            VALUES (?, ?, ?, 'Funcionário')
        """, (nome, email, google_id))
        conn.commit()
        c.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        row = c.fetchone()
    else:
        if not row[5]:  # google_id not set
            c.execute("UPDATE usuarios SET google_id = ? WHERE email = ?", (google_id, email))
            conn.commit()
    conn.close()
    cols = ["id","nome","email","senha","cargo","google_id","meta_atual","meta_total","ativo","criado_em"]
    return dict(zip(cols, row))

def get_avisos():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM avisos WHERE ativo = 1 ORDER BY criado_em DESC LIMIT 5")
    rows = c.fetchall()
    conn.close()
    cols = ["id","titulo","corpo","tipo","criado_em","ativo"]
    return [dict(zip(cols, r)) for r in rows]

def get_ponto_hoje(usuario_id):
    conn = get_conn()
    c = conn.cursor()
    hoje = date.today().isoformat()
    c.execute("SELECT * FROM ponto WHERE usuario_id = ? AND data = ?", (usuario_id, hoje))
    row = c.fetchone()
    conn.close()
    if row:
        cols = ["id","usuario_id","data","entrada","saida_almoco","retorno_almoco","saida_cafe","retorno_cafe","saida"]
        return dict(zip(cols, row))
    return None

def registrar_ponto(usuario_id, campo):
    conn = get_conn()
    c = conn.cursor()
    hoje = date.today().isoformat()
    agora = datetime.now().strftime("%H:%M:%S")

    existing = get_ponto_hoje(usuario_id)
    if existing:
        c.execute(f"UPDATE ponto SET {campo} = ? WHERE usuario_id = ? AND data = ?",
                  (agora, usuario_id, hoje))
    else:
        c.execute(f"INSERT INTO ponto (usuario_id, data, {campo}) VALUES (?, ?, ?)",
                  (usuario_id, hoje, agora))
    conn.commit()
    conn.close()
    return agora

def get_historico_ponto(usuario_id, limit=10):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM ponto WHERE usuario_id = ? ORDER BY data DESC LIMIT ?",
              (usuario_id, limit))
    rows = c.fetchall()
    conn.close()
    cols = ["id","usuario_id","data","entrada","saida_almoco","retorno_almoco","saida_cafe","retorno_cafe","saida"]
    return [dict(zip(cols, r)) for r in rows]

def salvar_documento(usuario_id, tipo, descricao, arquivo_nome):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO documentos (usuario_id, tipo, descricao, arquivo_nome)
        VALUES (?, ?, ?, ?)
    """, (usuario_id, tipo, descricao, arquivo_nome))
    conn.commit()
    conn.close()

def get_documentos_usuario(usuario_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM documentos WHERE usuario_id = ? ORDER BY criado_em DESC", (usuario_id,))
    rows = c.fetchall()
    conn.close()
    cols = ["id","usuario_id","tipo","descricao","arquivo_nome","status","criado_em"]
    return [dict(zip(cols, r)) for r in rows]
