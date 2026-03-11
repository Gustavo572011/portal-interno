# ╔══════════════════════════════════════════════════════════════╗
# ║           PORTAL INTERNO — app.py (arquivo único)           ║
# ║  Login · Dashboard · Ponto · Documentos                     ║
# ╚══════════════════════════════════════════════════════════════╝
#
# Dependências: pip install streamlit
# Rodar:        streamlit run app.py

import streamlit as st
import sqlite3
import hashlib
import os
from datetime import datetime, date

# ══════════════════════════════════════════════════════════════
# CONFIGURAÇÃO DA PÁGINA
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Portal Interno",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════
# CONSTANTES
# ══════════════════════════════════════════════════════════════
DB_PATH       = "portal.db"
WHATSAPP_LINK = "https://wa.link/ng5osg"

TIPOS_DOC = [
    "Atestado Médico",
    "Declaração",
    "Comprovante de Endereço",
    "Documento Pessoal (RG/CPF)",
    "Comprovante de Escolaridade",
    "Contrato",
    "Outros",
]

CAMPOS_PONTO = [
    ("entrada",        "🟢 Entrada",        "Registrar Entrada"),
    ("saida_almoco",   "🍽️ Saída Almoço",   "Saída Almoço"),
    ("retorno_almoco", "↩️ Retorno Almoço", "Retorno Almoço"),
    ("saida_cafe",     "☕ Saída Café",      "Saída Café"),
    ("retorno_cafe",   "↩️ Retorno Café",   "Retorno Café"),
    ("saida",          "🔴 Saída",           "Registrar Saída"),
]

# ══════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');

:root {
    --bg0:       #080c14;
    --bg1:       #0e1420;
    --bg2:       #131929;
    --bg3:       #1a2236;
    --border:    rgba(255,255,255,0.07);
    --border2:   rgba(255,255,255,0.12);
    --accent:    #4f8ef7;
    --accent2:   #7eb3ff;
    --green:     #34d399;
    --amber:     #fbbf24;
    --red:       #f87171;
    --wpp:       #25d366;
    --txt0:      #f0f4ff;
    --txt1:      #8b9ab8;
    --txt2:      #4a5568;
    --radius:    14px;
    --radius2:   20px;
    --font:      'Plus Jakarta Sans', sans-serif;
    --mono:      'DM Mono', monospace;
}

html, body, [class*="css"] {
    font-family: var(--font) !important;
    background: var(--bg0) !important;
    color: var(--txt0) !important;
}

/* Esconde elementos padrão */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton, [data-testid="stToolbar"] { display: none !important; }

/* Main container */
.main .block-container {
    padding: 2rem 2.5rem !important;
    max-width: 1100px !important;
}

/* ── Sidebar ───────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--bg1) !important;
    border-right: 1px solid var(--border) !important;
    min-width: 240px !important;
}
[data-testid="stSidebar"] > div { padding-top: 0 !important; }

.sb-top {
    background: linear-gradient(160deg, #1a2a4a 0%, var(--bg1) 100%);
    padding: 2rem 1.5rem 1.5rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 0.5rem;
}
.sb-avatar {
    width: 56px; height: 56px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--accent), #7c3aed);
    color: white;
    font-size: 1.5rem; font-weight: 800;
    display: flex; align-items: center; justify-content: center;
    margin-bottom: 0.75rem;
    box-shadow: 0 0 0 3px rgba(79,142,247,0.25), 0 8px 20px rgba(0,0,0,0.4);
}
.sb-name { font-size: 0.97rem; font-weight: 700; color: var(--txt0); margin-bottom: 0.25rem; }
.sb-role {
    font-size: 0.73rem; font-weight: 500;
    color: var(--accent2);
    background: rgba(79,142,247,0.12);
    border: 1px solid rgba(79,142,247,0.2);
    padding: 0.18rem 0.55rem;
    border-radius: 20px;
    display: inline-block;
    letter-spacing: 0.03em;
}

/* Radio nav buttons */
[data-testid="stSidebar"] [data-testid="stRadio"] > div { gap: 0.2rem !important; }
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    background: transparent !important;
    border: none !important;
    padding: 0.65rem 1.25rem !important;
    border-radius: 10px !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
    color: var(--txt1) !important;
    transition: all 0.18s !important;
    margin: 0.1rem 0.5rem !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: rgba(255,255,255,0.05) !important;
    color: var(--txt0) !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] [aria-checked="true"] + div label,
[data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"] {
    background: rgba(79,142,247,0.12) !important;
    color: var(--accent2) !important;
}

/* ── Botões Streamlit ─────────────────────────────────── */
.stButton > button {
    background: var(--accent) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius) !important;
    font-family: var(--font) !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 0.55rem 1.2rem !important;
    transition: all 0.18s !important;
    box-shadow: 0 4px 14px rgba(79,142,247,0.25) !important;
}
.stButton > button:hover {
    background: var(--accent2) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(79,142,247,0.4) !important;
}
.stButton > button:disabled {
    background: var(--bg3) !important;
    color: var(--txt2) !important;
    box-shadow: none !important;
    transform: none !important;
}
.btn-logout .stButton > button {
    background: transparent !important;
    border: 1px solid var(--border2) !important;
    color: var(--txt1) !important;
    box-shadow: none !important;
    font-size: 0.83rem !important;
}
.btn-logout .stButton > button:hover {
    background: rgba(248,113,113,0.08) !important;
    border-color: var(--red) !important;
    color: var(--red) !important;
    transform: none !important;
    box-shadow: none !important;
}

/* ── Inputs ───────────────────────────────────────────── */
.stTextInput input,
.stTextArea textarea,
.stSelectbox > div > div {
    background: var(--bg2) !important;
    border: 1px solid var(--border2) !important;
    border-radius: var(--radius) !important;
    color: var(--txt0) !important;
    font-family: var(--font) !important;
    font-size: 0.9rem !important;
}
.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(79,142,247,0.15) !important;
}
.stTextInput label, .stTextArea label, .stSelectbox label,
.stFileUploader label { color: var(--txt1) !important; font-size: 0.83rem !important; font-weight: 500 !important; }

/* ── Tabs ─────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg2) !important;
    border-radius: var(--radius) !important;
    border: 1px solid var(--border) !important;
    padding: 4px !important; gap: 2px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--txt1) !important;
    border-radius: 10px !important;
    font-family: var(--font) !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
}
.stTabs [aria-selected="true"] {
    background: var(--accent) !important;
    color: white !important;
}

/* ── Alertas ──────────────────────────────────────────── */
.stSuccess > div { background: rgba(52,211,153,0.1) !important; border: 1px solid rgba(52,211,153,0.3) !important; border-radius: var(--radius) !important; }
.stError   > div { background: rgba(248,113,113,0.1) !important; border: 1px solid rgba(248,113,113,0.3) !important; border-radius: var(--radius) !important; }
.stInfo    > div { background: rgba(79,142,247,0.1)  !important; border: 1px solid rgba(79,142,247,0.3)  !important; border-radius: var(--radius) !important; }
.stWarning > div { background: rgba(251,191,36,0.1)  !important; border: 1px solid rgba(251,191,36,0.3)  !important; border-radius: var(--radius) !important; }

/* ── File Uploader ────────────────────────────────────── */
[data-testid="stFileUploader"] > div {
    background: var(--bg2) !important;
    border: 1.5px dashed var(--border2) !important;
    border-radius: var(--radius) !important;
}

/* ── Expander ─────────────────────────────────────────── */
.streamlit-expanderHeader {
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--txt1) !important;
    font-size: 0.88rem !important;
}

/* ══════════════════════════════════
   COMPONENTES DE CONTEÚDO
   ══════════════════════════════════ */

/* Page header */
.ph { margin-bottom: 2rem; padding-bottom: 1.25rem; border-bottom: 1px solid var(--border); }
.ph h1 { font-size: 1.85rem !important; font-weight: 800 !important; color: var(--txt0) !important; margin: 0 0 0.2rem !important; letter-spacing: -0.02em; }
.ph-sub { color: var(--txt1); font-size: 0.88rem; }

/* Metric card */
.mc {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: var(--radius2);
    padding: 1.4rem 1.5rem;
    transition: transform 0.2s, box-shadow 0.2s;
}
.mc:hover { transform: translateY(-3px); box-shadow: 0 8px 30px rgba(0,0,0,0.3); }
.mc-label { font-size: 0.75rem; font-weight: 600; color: var(--txt2); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.5rem; }
.mc-value { font-size: 1.6rem; font-weight: 800; font-family: var(--mono); color: var(--txt0); }

/* Progress bar */
.prog-wrap {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: var(--radius2);
    padding: 1.5rem;
    margin: 0.5rem 0 1.5rem;
}
.prog-head { display: flex; justify-content: space-between; color: var(--txt1); font-size: 0.85rem; margin-bottom: 0.75rem; }
.prog-head strong { color: var(--txt0); font-family: var(--mono); }
.prog-bg { height: 10px; background: var(--bg0); border-radius: 100px; overflow: hidden; }
.prog-fill { height: 100%; border-radius: 100px; transition: width 1.2s cubic-bezier(.4,0,.2,1); }
.prog-msg { margin-top: 0.75rem; font-size: 0.83rem; color: var(--txt1); text-align: center; }

/* Aviso card */
.av {
    background: var(--bg2);
    border-radius: var(--radius);
    padding: 1.1rem 1.4rem;
    margin-bottom: 0.65rem;
    border-left: 3px solid var(--accent);
    transition: transform 0.15s;
}
.av:hover { transform: translateX(5px); }
.av-title { font-weight: 700; font-size: 0.95rem; margin-bottom: 0.3rem; }
.av-body { color: var(--txt1); font-size: 0.875rem; line-height: 1.55; }
.av-date { margin-top: 0.45rem; font-size: 0.75rem; color: var(--txt2); }

/* Login */
.login-wrap { max-width: 420px; margin: 3rem auto; }
.login-card {
    background: var(--bg1);
    border: 1px solid var(--border2);
    border-radius: 24px;
    padding: 2.5rem 2.2rem 2rem;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5);
}
.login-logo { text-align: center; margin-bottom: 2rem; }
.login-icon { font-size: 2.8rem; display: block; margin-bottom: 0.5rem; }
.login-title { font-size: 1.7rem !important; font-weight: 800 !important; color: var(--txt0) !important; letter-spacing: -0.03em; margin: 0 0 0.2rem !important; }
.login-sub { color: var(--txt1); font-size: 0.87rem; }

/* Ponto */
.ponto-head {
    display: flex; gap: 2rem; align-items: center;
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: var(--radius2);
    padding: 1.1rem 1.5rem;
    margin-bottom: 1.5rem;
}
.ponto-data { font-size: 0.92rem; font-weight: 600; color: var(--txt1); }
.ponto-hora { font-size: 1.3rem; font-weight: 700; font-family: var(--mono); color: var(--accent2); }

.pk {
    border-radius: var(--radius);
    padding: 1.1rem;
    text-align: center;
    border: 1px solid var(--border);
    margin-bottom: 0.5rem;
}
.pk.done { background: rgba(52,211,153,0.07); border-color: rgba(52,211,153,0.25); }
.pk.pend { background: var(--bg2); }
.pk-lbl { font-size: 0.75rem; color: var(--txt2); text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.35rem; font-weight: 600; }
.pk-time { font-size: 1.1rem; font-weight: 700; font-family: var(--mono); color: var(--txt0); }

.hist-row {
    display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: center;
    padding: 0.7rem 1rem;
    background: var(--bg2);
    border-radius: var(--radius);
    margin-bottom: 0.4rem;
    font-size: 0.83rem;
    color: var(--txt1);
    border: 1px solid var(--border);
}
.hist-row b { color: var(--txt0); }

/* Docs */
.doc-card {
    display: flex; justify-content: space-between; align-items: flex-start;
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.1rem 1.4rem;
    margin-bottom: 0.6rem;
    transition: transform 0.15s;
}
.doc-card:hover { transform: translateX(4px); }
.doc-tipo { font-weight: 700; font-size: 0.9rem; display: block; margin-bottom: 0.2rem; }
.doc-arq { font-size: 0.8rem; color: var(--txt1); font-family: var(--mono); }
.doc-desc { font-size: 0.78rem; color: var(--txt2); margin-top: 0.15rem; display: block; }
.doc-status { font-size: 0.82rem; font-weight: 700; }
.doc-date { font-size: 0.75rem; color: var(--txt2); margin-top: 0.3rem; }

.wpp-hint {
    background: rgba(37,211,102,0.07);
    border: 1px solid rgba(37,211,102,0.2);
    border-radius: var(--radius);
    padding: 1rem 1.4rem;
    font-size: 0.84rem;
    color: var(--txt1);
    line-height: 1.75;
    margin: 0.75rem 0 1.5rem;
}
.wpp-hint strong { color: var(--txt0); }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# BANCO DE DADOS
# ══════════════════════════════════════════════════════════════

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS usuarios (
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
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS avisos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        corpo TEXT NOT NULL,
        tipo TEXT DEFAULT 'info',
        criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
        ativo INTEGER DEFAULT 1
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS ponto (
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
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS documentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        tipo TEXT NOT NULL,
        descricao TEXT,
        arquivo_nome TEXT,
        status TEXT DEFAULT 'enviado',
        criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    )""")

    # Usuários de exemplo
    for nome, email, senha, cargo, m_atual, m_total in [
        ("Gustavo", "gustavo.venturini.soares@gmail.com", "senha572011",  "Assistente Administrativo",  0, 0),
        ("Agnaldo", "admin@empresa.com", "99551264",  "Ajudante de Entrega",  0, 0),
        ("Leiliane", "admin@empresa.com", "camila",  "Vendedora",  7500, 10000),
        ("Brenda", "admin@empresa.com", "2007",  "Operador de Caixa",  0, 0),
        ("Riquele", "admin@empresa.com", "riquele24",  "Zeladora",  0, 0),
        ("Rogério", "admin@empresa.com", "290580",  "Motorista",  0, 0),
        ("Wagner", "admin@empresa.com", "wagner007",  "Assistente Administrativo",  0, 0),
        ("Samuel", "admin@empresa.com", "Sophia2710",  "Serrador",  0, 0),
        ("Sueli", "admin@empresa.com",  "maria1819",    "Vendedora", 4200,  8000),
        ("Valdinei", "admin@empresa.com",  "123456",    "Surpevisor de Pátio", 0,  0),
        ("Paulo", "admin@empresa.com",  "123456",    "Auxiliar de Produção", 0,  0),
        ("Karen", "admin@empresa.com",  "123456",    "Gerente", 0,  0),
    ]:
        h = hashlib.sha256(senha.encode()).hexdigest()
        c.execute("INSERT OR IGNORE INTO usuarios (nome,email,senha,cargo,meta_atual,meta_total) VALUES (?,?,?,?,?,?)",
                  (nome, email, h, cargo, m_atual, m_total))

    # Avisos de exemplo
    c.execute("INSERT OR IGNORE INTO avisos (id,titulo,corpo,tipo) VALUES (1,'🎉 Reunião Mensal','Reunião de alinhamento na sexta-feira às 14h na sala de reuniões.','info')")
    c.execute("INSERT OR IGNORE INTO avisos (id,titulo,corpo,tipo) VALUES (2,'⚠️ Prazo de Metas','O fechamento do mês ocorre dia 30. Atenção ao cumprimento das metas!','warning')")

    conn.commit()
    conn.close()

def db_get_user(email):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM usuarios WHERE email=? AND ativo=1", (email,))
    row = c.fetchone()
    conn.close()
    if row:
        cols = ["id","nome","email","senha","cargo","google_id","meta_atual","meta_total","ativo","criado_em"]
        return dict(zip(cols, row))
    return None

def db_get_avisos():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM avisos WHERE ativo=1 ORDER BY criado_em DESC LIMIT 5")
    rows = c.fetchall()
    conn.close()
    cols = ["id","titulo","corpo","tipo","criado_em","ativo"]
    return [dict(zip(cols, r)) for r in rows]

def db_get_ponto_hoje(uid):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM ponto WHERE usuario_id=? AND data=?", (uid, date.today().isoformat()))
    row = c.fetchone()
    conn.close()
    if row:
        cols = ["id","usuario_id","data","entrada","saida_almoco","retorno_almoco","saida_cafe","retorno_cafe","saida"]
        return dict(zip(cols, row))
    return None

def db_registrar_ponto(uid, campo):
    conn = get_conn()
    c = conn.cursor()
    hoje  = date.today().isoformat()
    agora = datetime.now().strftime("%H:%M:%S")
    if db_get_ponto_hoje(uid):
        c.execute(f"UPDATE ponto SET {campo}=? WHERE usuario_id=? AND data=?", (agora, uid, hoje))
    else:
        c.execute(f"INSERT INTO ponto (usuario_id,data,{campo}) VALUES (?,?,?)", (uid, hoje, agora))
    conn.commit()
    conn.close()
    return agora

def db_historico_ponto(uid, limit=10):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM ponto WHERE usuario_id=? ORDER BY data DESC LIMIT ?", (uid, limit))
    rows = c.fetchall()
    conn.close()
    cols = ["id","usuario_id","data","entrada","saida_almoco","retorno_almoco","saida_cafe","retorno_cafe","saida"]
    return [dict(zip(cols, r)) for r in rows]

def db_salvar_doc(uid, tipo, descricao, nome_arquivo):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO documentos (usuario_id,tipo,descricao,arquivo_nome) VALUES (?,?,?,?)",
              (uid, tipo, descricao, nome_arquivo))
    conn.commit()
    conn.close()

def db_get_docs(uid):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM documentos WHERE usuario_id=? ORDER BY criado_em DESC", (uid,))
    rows = c.fetchall()
    conn.close()
    cols = ["id","usuario_id","tipo","descricao","arquivo_nome","status","criado_em"]
    return [dict(zip(cols, r)) for r in rows]

# ── Inicializa banco ──────────────────────────────────────────
init_db()

# ══════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None

# ══════════════════════════════════════════════════════════════
# TELA DE LOGIN
# ══════════════════════════════════════════════════════════════
def render_login():
    st.markdown('<div class="login-wrap">', unsafe_allow_html=True)
    st.markdown("""
    <div class="login-card">
        <div class="login-logo">
            <span class="login-icon">🏢</span>
            <div class="login-title">Portal Interno</div>
            <div class="login-sub">Acesse sua área de trabalho</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📧  E-mail & Senha", "🔵  Google"])

    with tab1:
        email = st.text_input("E-mail", placeholder="seu@empresa.com", key="l_email")
        senha = st.text_input("Senha", type="password", placeholder="••••••••", key="l_senha")

        if st.button("Entrar →", use_container_width=True, key="btn_entrar"):
            if not email or not senha:
                st.error("Preencha e-mail e senha.")
            else:
                user = db_get_user(email)
                if user and user.get("senha") == hashlib.sha256(senha.encode()).hexdigest():
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("E-mail ou senha incorretos.")

    with tab2:
        st.markdown("""
        <div style="background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius);
                    padding:1.1rem 1.3rem;font-size:0.85rem;color:var(--txt1);line-height:1.75;">
            Para ativar o login com Google, instale o pacote e configure as credenciais OAuth 2.0:<br><br>
            <code style="background:rgba(79,142,247,0.12);color:var(--accent2);padding:0.1rem 0.4rem;border-radius:5px;font-family:var(--mono)">
            pip install streamlit-google-auth</code><br><br>
            Em seguida adicione ao seu <code style="background:rgba(79,142,247,0.12);color:var(--accent2);padding:0.1rem 0.4rem;border-radius:5px;font-family:var(--mono)">.env</code>:<br>
            <code style="background:rgba(79,142,247,0.12);color:var(--accent2);padding:0.1rem 0.4rem;border-radius:5px;font-family:var(--mono)">
            GOOGLE_CLIENT_ID</code> e
            <code style="background:rgba(79,142,247,0.12);color:var(--accent2);padding:0.1rem 0.4rem;border-radius:5px;font-family:var(--mono)">
            GOOGLE_CLIENT_SECRET</code>
        </div>
        """, unsafe_allow_html=True)

        try:
            from streamlit_google_auth import Authenticate
            cid = os.getenv("GOOGLE_CLIENT_ID", "")
            csecret = os.getenv("GOOGLE_CLIENT_SECRET", "")
            if cid and csecret:
                auth = Authenticate(
                    secret_credentials_path=None,
                    cookie_name="portal_interno",
                    cookie_key=os.getenv("SECRET_KEY", "secret"),
                    redirect_uri=os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8501"),
                )
                auth.check_authentification()
                if st.session_state.get("connected"):
                    info = st.session_state.get("user_info", {})
                    user = db_get_user(info.get("email"))
                    if not user:
                        st.warning("E-mail não cadastrado. Fale com o administrador.")
                    else:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.rerun()
                else:
                    auth.login()
        except ImportError:
            pass

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center;margin-top:2rem;color:var(--txt2);font-size:0.78rem;">
        © 2025 Portal Interno
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════
def render_dashboard(user):
    dias_pt = ["Segunda","Terça","Quarta","Quinta","Sexta","Sábado","Domingo"]
    meses_pt = ["janeiro","fevereiro","março","abril","maio","junho",
                "julho","agosto","setembro","outubro","novembro","dezembro"]
    hoje = date.today()
    data_fmt = f"{dias_pt[hoje.weekday()]}, {hoje.day} de {meses_pt[hoje.month-1]} de {hoje.year}"

    st.markdown(f"""
    <div class="ph">
        <h1>Olá, {user['nome'].split()[0]}! 👋</h1>
        <div class="ph-sub">{data_fmt}</div>
    </div>
    """, unsafe_allow_html=True)

    # Metas
    st.markdown("#### 🎯 Sua Meta do Mês")
    meta_atual = float(user.get("meta_atual") or 0)
    meta_total = float(user.get("meta_total") or 10000)
    pct = min(int((meta_atual / meta_total) * 100), 100) if meta_total > 0 else 0
    cor = "#34d399" if pct >= 80 else "#fbbf24" if pct >= 50 else "#f87171"
    restante = max(meta_total - meta_atual, 0)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="mc">
            <div class="mc-label">Vendido</div>
            <div class="mc-value" style="color:{cor}">R$ {meta_atual:,.2f}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="mc">
            <div class="mc-label">Meta Total</div>
            <div class="mc-value">R$ {meta_total:,.2f}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="mc">
            <div class="mc-label">Falta para a Meta</div>
            <div class="mc-value" style="color:#fbbf24">R$ {restante:,.2f}</div>
        </div>""", unsafe_allow_html=True)

    msg = "🔥 Excelente! Você está quase lá!" if pct >= 80 else "💪 Você está no caminho certo!" if pct >= 50 else "🚀 Vamos acelerar!"
    st.markdown(f"""
    <div class="prog-wrap">
        <div class="prog-head"><span>Progresso da meta</span><strong>{pct}%</strong></div>
        <div class="prog-bg">
            <div class="prog-fill" style="width:{pct}%;background:{cor};box-shadow:0 0 12px {cor}66"></div>
        </div>
        <div class="prog-msg">{msg}</div>
    </div>
    """, unsafe_allow_html=True)

    # Avisos
    st.markdown("#### 📢 Avisos da Empresa")
    avisos = db_get_avisos()
    if not avisos:
        st.info("Nenhum aviso no momento.")
    for av in avisos:
        cor_av = "#4f8ef7" if av["tipo"]=="info" else "#fbbf24" if av["tipo"]=="warning" else "#f87171"
        st.markdown(f"""
        <div class="av" style="border-left-color:{cor_av}">
            <div class="av-title">{av['titulo']}</div>
            <div class="av-body">{av['corpo']}</div>
            <div class="av-date">🕐 {av['criado_em'][:10]}</div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# PONTO
# ══════════════════════════════════════════════════════════════
def render_ponto(user):
    st.markdown("""
    <div class="ph">
        <h1>🕐 Registro de Ponto</h1>
        <div class="ph-sub">Registre seus horários de trabalho</div>
    </div>
    """, unsafe_allow_html=True)

    hoje = date.today()
    agora = datetime.now().strftime("%H:%M:%S")
    ponto = db_get_ponto_hoje(user["id"])

    st.markdown(f"""
    <div class="ponto-head">
        <span class="ponto-data">📅 {hoje.strftime('%d/%m/%Y')}</span>
        <span class="ponto-hora">{agora}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### Marcações de hoje")
    c1, c2, c3 = st.columns(3)
    cols_map = [c1, c2, c3, c1, c2, c3]

    for i, (campo, label, btn_label) in enumerate(CAMPOS_PONTO):
        horario = ponto.get(campo) if ponto else None
        with cols_map[i]:
            css_cls = "done" if horario else "pend"
            st.markdown(f"""
            <div class="pk {css_cls}">
                <div class="pk-lbl">{label}</div>
                <div class="pk-time">{"✅ " + horario if horario else "—"}</div>
            </div>
            """, unsafe_allow_html=True)

            if not horario:
                idx_anterior = i - 1
                anterior_ok = True
                if idx_anterior >= 0:
                    campo_ant = CAMPOS_PONTO[idx_anterior][0]
                    anterior_ok = bool(ponto.get(campo_ant)) if ponto else False

                if st.button(btn_label, key=f"ponto_{campo}", use_container_width=True, disabled=not anterior_ok):
                    hr = db_registrar_ponto(user["id"], campo)
                    st.success(f"{label} às {hr}")
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📋 Histórico de ponto"):
        hist = db_historico_ponto(user["id"])
        if not hist:
            st.info("Nenhum registro encontrado.")
        for reg in hist:
            campos_disp = [
                ("🟢", reg["entrada"]),
                ("🍽️", reg["saida_almoco"]),
                ("↩️", reg["retorno_almoco"]),
                ("☕", reg["saida_cafe"]),
                ("↩️", reg["retorno_cafe"]),
                ("🔴", reg["saida"]),
            ]
            marcacoes = "  ".join(f"{ic} {h or '—'}" for ic, h in campos_disp)
            st.markdown(f"""
            <div class="hist-row">
                <b>📅 {reg['data']}</b>
                <span style="color:var(--txt1);font-family:var(--mono);font-size:0.8rem">{marcacoes}</span>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# DOCUMENTOS
# ══════════════════════════════════════════════════════════════
def render_documentos(user):
    st.markdown("""
    <div class="ph">
        <h1>📄 Envio de Documentos</h1>
        <div class="ph-sub">Envie atestados e documentos para o RH</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 📤 Novo Documento")

    tipo      = st.selectbox("Tipo de Documento", TIPOS_DOC, key="doc_tipo")
    descricao = st.text_area("Descrição (opcional)", placeholder="Ex: Atestado médico do dia 10/01 por gripe...", key="doc_desc")
    arquivo   = st.file_uploader("Selecione o arquivo", type=["pdf","jpg","jpeg","png","doc","docx"], key="doc_arq")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Salvar no Portal", use_container_width=True, key="btn_salvar"):
            if not arquivo:
                st.error("Selecione um arquivo para salvar.")
            else:
                pasta = f"docs_enviados/{user['id']}"
                os.makedirs(pasta, exist_ok=True)
                with open(f"{pasta}/{arquivo.name}", "wb") as f:
                    f.write(arquivo.getbuffer())
                db_salvar_doc(user["id"], tipo, descricao, arquivo.name)
                st.success("✅ Documento salvo no portal!")
                st.rerun()

    with col2:
        st.markdown(f"""
        <a href="{WHATSAPP_LINK}" target="_blank" style="text-decoration:none;display:block;margin-top:0.15rem">
            <button style="
                width:100%; background:#25d366; color:white; border:none;
                border-radius:14px; padding:0.56rem 1rem;
                font-size:0.88rem; font-weight:700; cursor:pointer;
                display:flex; align-items:center; justify-content:center; gap:8px;
                font-family:'Plus Jakarta Sans',sans-serif;
                box-shadow:0 4px 16px rgba(37,211,102,0.3);
                transition:all 0.2s;
            ">
                <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24" fill="white">
                    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
                </svg>
                Enviar pelo WhatsApp
            </button>
        </a>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="wpp-hint">
        💡 <strong>Como usar:</strong><br>
        1. Preencha o tipo e a descrição, depois clique em <strong>Salvar no Portal</strong><br>
        2. Clique em <strong>Enviar pelo WhatsApp</strong> para abrir o chat do RH e anexar o arquivo
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 📋 Documentos Enviados")
    docs = db_get_docs(user["id"])
    if not docs:
        st.info("Nenhum documento enviado ainda.")
    for doc in docs:
        cor_s = "#34d399" if doc["status"]=="aprovado" else "#fbbf24" if doc["status"]=="enviado" else "#f87171"
        ic_s  = "✅" if doc["status"]=="aprovado" else "⏳" if doc["status"]=="enviado" else "❌"
        st.markdown(f"""
        <div class="doc-card">
            <div>
                <span class="doc-tipo">📄 {doc['tipo']}</span>
                <span class="doc-arq">{doc['arquivo_nome'] or '—'}</span>
                <span class="doc-desc">{doc['descricao'] or ''}</span>
            </div>
            <div style="text-align:right">
                <div class="doc-status" style="color:{cor_s}">{ic_s} {doc['status'].capitalize()}</div>
                <div class="doc-date">🕐 {doc['criado_em'][:10]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# ROTEAMENTO PRINCIPAL
# ══════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    render_login()
else:
    user = st.session_state.user

    with st.sidebar:
        st.markdown(f"""
        <div class="sb-top">
            <div class="sb-avatar">{user['nome'][0].upper()}</div>
            <div class="sb-name">{user['nome']}</div>
            <div class="sb-role">{user['cargo']}</div>
        </div>
        """, unsafe_allow_html=True)

        page = st.radio("", ["🏠  Dashboard", "🕐  Ponto", "📄  Documentos"],
                        label_visibility="collapsed", key="nav")

        st.markdown("<br>" * 8, unsafe_allow_html=True)
        st.markdown('<div class="btn-logout">', unsafe_allow_html=True)
        if st.button("Sair", use_container_width=True, key="logout"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    if "Dashboard" in page:
        render_dashboard(user)
    elif "Ponto" in page:
        render_ponto(user)
    elif "Documentos" in page:
        render_documentos(user)
