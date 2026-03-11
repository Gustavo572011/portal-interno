# ╔══════════════════════════════════════════════════════════════╗
# ║           PORTAL INTERNO — app.py (arquivo único)           ║
# ╚══════════════════════════════════════════════════════════════╝
#
# Dependências: pip install streamlit
# Rodar:        streamlit run app.py

import streamlit as st
import sqlite3
import hashlib
import os
from datetime import datetime, date
import pytz  # pip install pytz  (já vem com streamlit cloud)

# ══════════════════════════════════════════════════════════════
# ██  CONFIGURAÇÕES — EDITE AQUI  ██████████████████████████████
# ══════════════════════════════════════════════════════════════

# 🔗 ID da planilha Google Sheets com informações dos funcionários
# Como obter: abra a planilha → copie o ID da URL:
# https://docs.google.com/spreadsheets/d/ >>> COLE_O_ID_AQUI <<< /edit
GOOGLE_SHEETS_ID = "1bygdJMOHvuYyeieKRkMtmHY5jUz-JduhFx5umNQ_t6g"           # ← cole o ID da sua planilha aqui

# 📋 Nome da aba (sheet) dentro da planilha que contém os dados
GOOGLE_SHEETS_ABA = "DADOS"

# 💬 Link do WhatsApp para envio de documentos ao RH
WHATSAPP_LINK = "https://wa.link/ng5osg"

# 🏢 Nome da empresa (aparece no título e rodapé)
NOME_EMPRESA = "COMSTRUKASA"

# 🕐 Fuso horário da empresa
TIMEZONE = "America/Sao_Paulo"

# 🔒 Horários de funcionamento (acesso bloqueado fora desses horários)
# Formato: (hora_inicio, minuto_inicio, hora_fim, minuto_fim)
HORARIO_SEG_SEX = (7, 45, 19, 0)   # Seg–Sex: 07:45 às 19:00
HORARIO_SAB     = (7, 45, 13, 0)   # Sábado:  07:45 às 13:00
# Domingo: acesso bloqueado o dia todo

# ══════════════════════════════════════════════════════════════
# CONFIGURAÇÕES TÉCNICAS
# ══════════════════════════════════════════════════════════════
DB_PATH = "portal.db"

TIPOS_DOC = [
    "Atestado Médico", "Declaração", "Comprovante de Endereço",
    "Documento Pessoal (RG/CPF)", "Comprovante de Escolaridade",
    "Contrato", "Outros",
]

CAMPOS_PONTO = [
    ("entrada",        "🟢 Entrada",        "Registrar Entrada"),
    ("saida_almoco",   "🍽️ Saída Almoço",   "Saída Almoço"),
    ("retorno_almoco", "↩️ Retorno Almoço", "Retorno Almoço"),
    ("saida_cafe",     "☕ Saída Café",      "Saída Café"),
    ("retorno_cafe",   "↩️ Retorno Café",   "Retorno Café"),
    ("saida",          "🔴 Saída",           "Registrar Saída"),
]

DIAS_PT  = ["Segunda","Terça","Quarta","Quinta","Sexta","Sábado","Domingo"]
MESES_PT = ["janeiro","fevereiro","março","abril","maio","junho",
            "julho","agosto","setembro","outubro","novembro","dezembro"]

# ══════════════════════════════════════════════════════════════
# CONFIGURAÇÃO DA PÁGINA
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title=Portal-interno,
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="auto"
)

# ══════════════════════════════════════════════════════════════
# CSS — DESIGN SYSTEM + MOBILE + BOTTOM NAV
# ══════════════════════════════════════════════════════════════
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');

:root {
    --bg0:     #080c14;
    --bg1:     #0e1420;
    --bg2:     #131929;
    --bg3:     #1a2236;
    --border:  rgba(255,255,255,0.07);
    --border2: rgba(255,255,255,0.12);
    --accent:  #4f8ef7;
    --accent2: #7eb3ff;
    --green:   #34d399;
    --amber:   #fbbf24;
    --red:     #f87171;
    --txt0:    #f0f4ff;
    --txt1:    #8b9ab8;
    --txt2:    #4a5568;
    --r:       12px;
    --r2:      18px;
    --font:    'Plus Jakarta Sans', sans-serif;
    --mono:    'DM Mono', monospace;
}

html, body, [class*="css"] {
    font-family: var(--font) !important;
    background: var(--bg0) !important;
    color: var(--txt0) !important;
}
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton, [data-testid="stToolbar"] { display: none !important; }

/* ── Container ──────────────────────────── */
.main .block-container {
    padding: 1.5rem 1.5rem 5rem !important;
    max-width: 1100px !important;
}

/* ── Sidebar desktop ────────────────────── */
[data-testid="stSidebar"] {
    background: var(--bg1) !important;
    border-right: 1px solid var(--border) !important;
    min-width: 230px !important;
    max-width: 230px !important;
}
[data-testid="stSidebar"] > div { padding-top: 0 !important; }

.sb-top {
    background: linear-gradient(160deg,#1a2a4a 0%,var(--bg1) 100%);
    padding: 1.75rem 1.25rem 1.25rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 0.4rem;
}
.sb-avatar {
    width: 52px; height: 52px; border-radius: 50%;
    background: linear-gradient(135deg, var(--accent), #7c3aed);
    color: white; font-size: 1.4rem; font-weight: 800;
    display: flex; align-items: center; justify-content: center;
    margin-bottom: 0.65rem;
    box-shadow: 0 0 0 3px rgba(79,142,247,0.2), 0 6px 16px rgba(0,0,0,0.4);
}
.sb-name { font-size: 0.92rem; font-weight: 700; color: var(--txt0); margin-bottom: 0.2rem; }
.sb-role {
    font-size: 0.7rem; font-weight: 600; color: var(--accent2);
    background: rgba(79,142,247,0.12); border: 1px solid rgba(79,142,247,0.2);
    padding: 0.15rem 0.5rem; border-radius: 20px; display: inline-block;
}

/* Relógio na sidebar */
.sb-clock {
    margin-top: 1rem;
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: var(--r);
    padding: 0.7rem 1rem;
    text-align: center;
}
.sb-clock-time {
    font-family: var(--mono);
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--accent2);
    letter-spacing: 0.05em;
}
.sb-clock-date {
    font-size: 0.72rem;
    color: var(--txt1);
    margin-top: 0.2rem;
}

/* Nav radio */
[data-testid="stSidebar"] [data-testid="stRadio"] > div { gap: 0.15rem !important; }
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    background: transparent !important; border: none !important;
    padding: 0.6rem 1.1rem !important; border-radius: 10px !important;
    font-size: 0.9rem !important; font-weight: 500 !important;
    color: var(--txt1) !important; transition: all 0.15s !important;
    margin: 0.05rem 0.4rem !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: rgba(255,255,255,0.05) !important; color: var(--txt0) !important;
}

/* ── Botões ─────────────────────────────── */
.stButton > button {
    background: var(--accent) !important; color: white !important;
    border: none !important; border-radius: var(--r) !important;
    font-family: var(--font) !important; font-weight: 600 !important;
    font-size: 0.88rem !important; padding: 0.55rem 1.1rem !important;
    transition: all 0.18s !important;
    box-shadow: 0 3px 12px rgba(79,142,247,0.22) !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: var(--accent2) !important; transform: translateY(-1px) !important;
    box-shadow: 0 5px 18px rgba(79,142,247,0.38) !important;
}
.stButton > button:disabled {
    background: var(--bg3) !important; color: var(--txt2) !important;
    box-shadow: none !important; transform: none !important;
}
.btn-logout .stButton > button {
    background: transparent !important; border: 1px solid var(--border2) !important;
    color: var(--txt1) !important; box-shadow: none !important; font-size: 0.82rem !important;
}
.btn-logout .stButton > button:hover {
    background: rgba(248,113,113,0.08) !important;
    border-color: var(--red) !important; color: var(--red) !important;
    transform: none !important; box-shadow: none !important;
}

/* ── Inputs ─────────────────────────────── */
.stTextInput input, .stTextArea textarea, .stSelectbox > div > div {
    background: var(--bg2) !important; border: 1px solid var(--border2) !important;
    border-radius: var(--r) !important; color: var(--txt0) !important;
    font-family: var(--font) !important; font-size: 0.9rem !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(79,142,247,0.15) !important;
}
.stTextInput label, .stTextArea label, .stSelectbox label, .stFileUploader label {
    color: var(--txt1) !important; font-size: 0.82rem !important; font-weight: 500 !important;
}

/* ── Alertas ────────────────────────────── */
.stSuccess > div { background: rgba(52,211,153,0.1) !important; border: 1px solid rgba(52,211,153,0.3) !important; border-radius: var(--r) !important; }
.stError   > div { background: rgba(248,113,113,0.1) !important; border: 1px solid rgba(248,113,113,0.3) !important; border-radius: var(--r) !important; }
.stInfo    > div { background: rgba(79,142,247,0.1)  !important; border: 1px solid rgba(79,142,247,0.3)  !important; border-radius: var(--r) !important; }
.stWarning > div { background: rgba(251,191,36,0.1)  !important; border: 1px solid rgba(251,191,36,0.3)  !important; border-radius: var(--r) !important; }

[data-testid="stFileUploader"] > div {
    background: var(--bg2) !important;
    border: 1.5px dashed var(--border2) !important; border-radius: var(--r) !important;
}
.streamlit-expanderHeader {
    background: var(--bg2) !important; border: 1px solid var(--border) !important;
    border-radius: var(--r) !important; color: var(--txt1) !important; font-size: 0.87rem !important;
}

/* ════════════════════════════════════
   COMPONENTES
   ════════════════════════════════════ */

/* Relógio em tempo real — topo do conteúdo */
.realtime-bar {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 1rem;
    padding: 0.5rem 0 1.25rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.5rem;
}
.rt-date { font-size: 0.83rem; color: var(--txt1); }
.rt-time {
    font-family: var(--mono);
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--accent2);
    background: rgba(79,142,247,0.1);
    border: 1px solid rgba(79,142,247,0.2);
    padding: 0.25rem 0.7rem;
    border-radius: 8px;
    letter-spacing: 0.04em;
}

/* Page header */
.ph { margin-bottom: 1.5rem; }
.ph h1 { font-size: 1.75rem !important; font-weight: 800 !important; color: var(--txt0) !important; margin: 0 0 0.15rem !important; letter-spacing: -0.02em; }
.ph-sub { color: var(--txt1); font-size: 0.86rem; }

/* Metric cards */
.mc-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 0.75rem; margin-bottom: 0.75rem; }
.mc {
    background: var(--bg2); border: 1px solid var(--border);
    border-radius: var(--r2); padding: 1.2rem 1.3rem;
    transition: transform 0.2s, box-shadow 0.2s;
}
.mc:hover { transform: translateY(-2px); box-shadow: 0 6px 24px rgba(0,0,0,0.3); }
.mc-label { font-size: 0.72rem; font-weight: 600; color: var(--txt2); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.4rem; }
.mc-value { font-size: 1.5rem; font-weight: 800; font-family: var(--mono); color: var(--txt0); }

/* Progress */
.prog-wrap {
    background: var(--bg2); border: 1px solid var(--border);
    border-radius: var(--r2); padding: 1.3rem 1.4rem; margin: 0.25rem 0 1.25rem;
}
.prog-head { display: flex; justify-content: space-between; color: var(--txt1); font-size: 0.83rem; margin-bottom: 0.65rem; }
.prog-head strong { color: var(--txt0); font-family: var(--mono); }
.prog-bg { height: 9px; background: var(--bg0); border-radius: 100px; overflow: hidden; }
.prog-fill { height: 100%; border-radius: 100px; transition: width 1.2s cubic-bezier(.4,0,.2,1); }
.prog-msg { margin-top: 0.65rem; font-size: 0.82rem; color: var(--txt1); text-align: center; }

/* Aviso */
.av {
    background: var(--bg2); border-radius: var(--r); padding: 1rem 1.3rem;
    margin-bottom: 0.6rem; border-left: 3px solid var(--accent); transition: transform 0.15s;
}
.av:hover { transform: translateX(4px); }
.av-title { font-weight: 700; font-size: 0.93rem; margin-bottom: 0.25rem; }
.av-body  { color: var(--txt1); font-size: 0.85rem; line-height: 1.5; }
.av-date  { margin-top: 0.4rem; font-size: 0.73rem; color: var(--txt2); }

/* Login */
.login-wrap { max-width: 400px; margin: 2rem auto; padding: 0 0.5rem; }
.login-card {
    background: var(--bg1); border: 1px solid var(--border2);
    border-radius: 22px; padding: 2.2rem 2rem 1.8rem;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5);
}
.login-logo { text-align: center; margin-bottom: 1.75rem; }
.login-icon { font-size: 2.6rem; display: block; margin-bottom: 0.4rem; }
.login-title { font-size: 1.6rem !important; font-weight: 800 !important; color: var(--txt0) !important; letter-spacing: -0.03em; margin: 0 0 0.15rem !important; }
.login-sub { color: var(--txt1); font-size: 0.85rem; }

/* Ponto */
.ponto-head {
    display: flex; flex-wrap: wrap; gap: 1rem 2rem; align-items: center;
    background: var(--bg2); border: 1px solid var(--border);
    border-radius: var(--r2); padding: 1rem 1.4rem; margin-bottom: 1.25rem;
}
.ponto-data { font-size: 0.9rem; font-weight: 600; color: var(--txt1); }
.ponto-hora { font-size: 1.25rem; font-weight: 700; font-family: var(--mono); color: var(--accent2); }

.pk-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 0.6rem; margin-bottom: 0.5rem; }
.pk {
    border-radius: var(--r); padding: 0.9rem 0.75rem;
    text-align: center; border: 1px solid var(--border);
}
.pk.done { background: rgba(52,211,153,0.07); border-color: rgba(52,211,153,0.22); }
.pk.pend { background: var(--bg2); }
.pk-lbl  { font-size: 0.7rem; color: var(--txt2); text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.3rem; font-weight: 600; }
.pk-time { font-size: 1rem; font-weight: 700; font-family: var(--mono); color: var(--txt0); }

.hist-row {
    display: flex; flex-wrap: wrap; gap: 0.5rem 1rem; align-items: center;
    padding: 0.65rem 1rem; background: var(--bg2); border-radius: var(--r);
    margin-bottom: 0.35rem; font-size: 0.82rem; color: var(--txt1);
    border: 1px solid var(--border);
}
.hist-row b { color: var(--txt0); }

/* Docs */
.doc-card {
    display: flex; justify-content: space-between; align-items: flex-start;
    background: var(--bg2); border: 1px solid var(--border); border-radius: var(--r);
    padding: 1rem 1.3rem; margin-bottom: 0.55rem; transition: transform 0.15s;
}
.doc-card:hover { transform: translateX(3px); }
.doc-tipo  { font-weight: 700; font-size: 0.88rem; display: block; margin-bottom: 0.18rem; }
.doc-arq   { font-size: 0.78rem; color: var(--txt1); font-family: var(--mono); }
.doc-desc  { font-size: 0.76rem; color: var(--txt2); margin-top: 0.12rem; display: block; }
.doc-status{ font-size: 0.8rem; font-weight: 700; }
.doc-date  { font-size: 0.73rem; color: var(--txt2); margin-top: 0.25rem; }

.wpp-hint {
    background: rgba(37,211,102,0.07); border: 1px solid rgba(37,211,102,0.2);
    border-radius: var(--r); padding: 0.9rem 1.3rem;
    font-size: 0.83rem; color: var(--txt1); line-height: 1.75; margin: 0.6rem 0 1.25rem;
}
.wpp-hint strong { color: var(--txt0); }

/* Tela de bloqueio */
.bloqueio-wrap {
    max-width: 480px; margin: 3rem auto; padding: 0 1rem; text-align: center;
}
.bloqueio-card {
    background: var(--bg1); border: 1px solid rgba(248,113,113,0.25);
    border-radius: 24px; padding: 3rem 2.5rem;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5), 0 0 0 1px rgba(248,113,113,0.1);
}
.bloqueio-icon { font-size: 3.5rem; display: block; margin-bottom: 1rem; }
.bloqueio-title { font-size: 1.5rem; font-weight: 800; color: var(--txt0); margin-bottom: 0.5rem; }
.bloqueio-msg   { color: var(--txt1); font-size: 0.9rem; line-height: 1.65; margin-bottom: 1.5rem; }
.bloqueio-horarios {
    background: var(--bg2); border: 1px solid var(--border);
    border-radius: var(--r); padding: 1rem 1.4rem; text-align: left;
    font-size: 0.85rem; color: var(--txt1); line-height: 1.9;
}
.bloqueio-horarios strong { color: var(--txt0); }

/* ════════════════════════════════════
   📱 BOTTOM NAV BAR — MOBILE
   ════════════════════════════════════ */
.bottom-nav {
    display: none;
    position: fixed;
    bottom: 0; left: 0; right: 0;
    z-index: 9999;
    background: var(--bg1);
    border-top: 1px solid var(--border2);
    padding: 0.4rem 0 calc(0.4rem + env(safe-area-inset-bottom));
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
}
.bnav-inner {
    display: flex;
    justify-content: space-around;
    align-items: center;
    max-width: 500px;
    margin: 0 auto;
}
.bnav-item {
    display: flex; flex-direction: column; align-items: center;
    gap: 0.2rem; padding: 0.4rem 1rem; border-radius: 12px;
    cursor: pointer; transition: all 0.18s;
    text-decoration: none; border: none; background: transparent;
    font-family: var(--font); min-width: 64px;
}
.bnav-item:active { transform: scale(0.93); }
.bnav-item.active .bnav-icon { color: var(--accent2); }
.bnav-item.active .bnav-label { color: var(--accent2); }
.bnav-item.active { background: rgba(79,142,247,0.1); }
.bnav-icon  { font-size: 1.4rem; line-height: 1; color: var(--txt2); transition: color 0.15s; }
.bnav-label { font-size: 0.65rem; font-weight: 600; color: var(--txt2); letter-spacing: 0.03em; text-transform: uppercase; transition: color 0.15s; }

/* ════════════════════════════════════
   📱 RESPONSIVIDADE
   ════════════════════════════════════ */

@media (max-width: 768px) {
    /* Esconde sidebar no mobile */
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }

    /* Mostra bottom nav */
    .bottom-nav { display: block !important; }

    .main .block-container {
        padding: 1rem 0.85rem 5.5rem !important;
        margin-left: 0 !important;
    }
    .ph h1 { font-size: 1.35rem !important; }
    .mc-grid { grid-template-columns: repeat(2,1fr) !important; }
    .mc-value { font-size: 1.2rem !important; }
    .pk-grid { grid-template-columns: repeat(2,1fr) !important; }
    .doc-card { flex-direction: column; gap: 0.4rem; }
    .realtime-bar { justify-content: space-between; }
}

@media (max-width: 480px) {
    .main .block-container { padding: 0.75rem 0.6rem 5.5rem !important; }
    .ph h1 { font-size: 1.2rem !important; }
    .mc-grid { grid-template-columns: 1fr !important; gap: 0.5rem !important; }
    .mc { padding: 1rem 1.1rem; }
    .mc-value { font-size: 1.15rem !important; }
    .pk-grid { grid-template-columns: 1fr 1fr !important; }
    .prog-wrap { padding: 1rem 1.1rem; }
    .login-card { padding: 1.5rem 1.2rem; border-radius: 18px; }
    .login-title { font-size: 1.35rem !important; }
    .rt-time { font-size: 1rem; }
    .rt-date { font-size: 0.76rem; }
    .stButton > button { font-size: 0.84rem !important; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# RELÓGIO EM TEMPO REAL (JavaScript)
# ══════════════════════════════════════════════════════════════
RELOGIO_JS = """
<script>
(function() {
    function pad(n) { return String(n).padStart(2,'0'); }
    const DIAS   = ['Domingo','Segunda','Terça','Quarta','Quinta','Sexta','Sábado'];
    const MESES  = ['janeiro','fevereiro','março','abril','maio','junho',
                    'julho','agosto','setembro','outubro','novembro','dezembro'];

    function tick() {
        const now  = new Date();
        const hh   = pad(now.getHours());
        const mm   = pad(now.getMinutes());
        const ss   = pad(now.getSeconds());
        const dia  = DIAS[now.getDay()];
        const d    = now.getDate();
        const mes  = MESES[now.getMonth()];
        const ano  = now.getFullYear();

        const timeStr = hh + ':' + mm + ':' + ss;
        const dateStr = dia + ', ' + d + ' de ' + mes + ' de ' + ano;

        // Atualiza todos os elementos de relógio na página
        document.querySelectorAll('.rt-time').forEach(el => el.textContent = timeStr);
        document.querySelectorAll('.rt-date').forEach(el => el.textContent = dateStr);
        document.querySelectorAll('.ponto-hora').forEach(el => el.textContent = timeStr);
        document.querySelectorAll('.sb-clock-time').forEach(el => el.textContent = timeStr);
        document.querySelectorAll('.sb-clock-date').forEach(el => el.textContent = dateStr);
    }
    tick();
    setInterval(tick, 1000);
})();
</script>
"""

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
        nome TEXT NOT NULL, email TEXT UNIQUE NOT NULL, senha TEXT,
        cargo TEXT DEFAULT 'Funcionário', meta_atual REAL DEFAULT 0,
        meta_total REAL DEFAULT 10000, ativo INTEGER DEFAULT 1,
        criado_em TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS avisos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL, corpo TEXT NOT NULL,
        tipo TEXT DEFAULT 'info', criado_em TEXT DEFAULT CURRENT_TIMESTAMP, ativo INTEGER DEFAULT 1
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS ponto (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL, data TEXT NOT NULL,
        entrada TEXT, saida_almoco TEXT, retorno_almoco TEXT,
        saida_cafe TEXT, retorno_cafe TEXT, saida TEXT,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS documentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL, tipo TEXT NOT NULL,
        descricao TEXT, arquivo_nome TEXT, status TEXT DEFAULT 'enviado',
        criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    )""")
    for nome, email, senha, cargo, ma, mt in [
        ("Admin",      "admin@empresa.com", "admin123", "Gerente",  7500, 10000),
        ("João Silva", "joao@empresa.com",  "123456",   "Vendedor", 4200,  8000),
    ]:
        h = hashlib.sha256(senha.encode()).hexdigest()
        c.execute("INSERT OR IGNORE INTO usuarios (nome,email,senha,cargo,meta_atual,meta_total) VALUES (?,?,?,?,?,?)",
                  (nome, email, h, cargo, ma, mt))
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
        cols = ["id","nome","email","senha","cargo","meta_atual","meta_total","ativo","criado_em"]
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

init_db()

# ══════════════════════════════════════════════════════════════
# 🔒 VERIFICAÇÃO DE HORÁRIO DE SERVIÇO
# ══════════════════════════════════════════════════════════════
def verificar_horario_servico():
    """Retorna (permitido: bool, motivo: str)"""
    try:
        tz  = pytz.timezone(TIMEZONE)
        now = datetime.now(tz)
    except Exception:
        now = datetime.now()

    dow = now.weekday()   # 0=Seg … 6=Dom
    h, m = now.hour, now.minute
    total_min = h * 60 + m  # minutos desde meia-noite

    if dow < 5:  # Seg–Sex
        ini = HORARIO_SEG_SEX[0] * 60 + HORARIO_SEG_SEX[1]
        fim = HORARIO_SEG_SEX[2] * 60 + HORARIO_SEG_SEX[3]
        if ini <= total_min <= fim:
            return True, ""
        return False, "seg_sex"
    elif dow == 5:  # Sábado
        ini = HORARIO_SAB[0] * 60 + HORARIO_SAB[1]
        fim = HORARIO_SAB[2] * 60 + HORARIO_SAB[3]
        if ini <= total_min <= fim:
            return True, ""
        return False, "sab"
    else:  # Domingo
        return False, "dom"

def render_bloqueio(motivo):
    msgs = {
        "seg_sex": f"O portal está disponível de <strong>Segunda a Sexta das {HORARIO_SEG_SEX[0]:02d}:{HORARIO_SEG_SEX[1]:02d} às {HORARIO_SEG_SEX[2]:02d}:{HORARIO_SEG_SEX[3]:02d}</strong>.",
        "sab":     f"Hoje é sábado. O portal funciona das <strong>{HORARIO_SAB[0]:02d}:{HORARIO_SAB[1]:02d} às {HORARIO_SAB[2]:02d}:{HORARIO_SAB[3]:02d}</strong>.",
        "dom":     "Hoje é domingo. O portal não está disponível aos domingos.",
    }
    st.markdown(f"""
    <div class="bloqueio-wrap">
        <div class="bloqueio-card">
            <span class="bloqueio-icon">🔒</span>
            <div class="bloqueio-title">Acesso Restrito</div>
            <div class="bloqueio-msg">
                O portal está fora do horário de funcionamento.<br>
                {msgs.get(motivo,'')}
            </div>
            <div class="bloqueio-horarios">
                <strong>Horários de funcionamento:</strong><br>
                🗓️ Segunda a Sexta — {HORARIO_SEG_SEX[0]:02d}:{HORARIO_SEG_SEX[1]:02d} às {HORARIO_SEG_SEX[2]:02d}:{HORARIO_SEG_SEX[3]:02d}<br>
                🗓️ Sábado — {HORARIO_SAB[0]:02d}:{HORARIO_SAB[1]:02d} às {HORARIO_SAB[2]:02d}:{HORARIO_SAB[3]:02d}<br>
                🚫 Domingo — Fechado
            </div>
        </div>
        <div style="text-align:center;margin-top:1.5rem;color:var(--txt2);font-size:0.75rem;">
            © 2025 {NOME_EMPRESA}
        </div>
    </div>
    """, unsafe_allow_html=True)
    # Relógio na tela de bloqueio
    st.markdown(f"""
    <div style="text-align:center;margin-top:1rem;">
        <span class="rt-time" style="font-family:var(--mono);font-size:2rem;font-weight:800;color:var(--txt2);letter-spacing:0.06em">--:--:--</span>
    </div>
    {RELOGIO_JS}
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "🏠  Dashboard"

# ══════════════════════════════════════════════════════════════
# TELA DE LOGIN
# ══════════════════════════════════════════════════════════════
def render_login():
    try:
        tz  = pytz.timezone(TIMEZONE)
        now = datetime.now(tz)
    except Exception:
        now = datetime.now()

    data_fmt = f"{DIAS_PT[now.weekday()]}, {now.day} de {MESES_PT[now.month-1]} de {now.year}"

    st.markdown(f"""
    <div style="text-align:center;padding:1rem 0 0.5rem;">
        <span class="rt-time" style="font-family:var(--mono);font-size:1.8rem;font-weight:800;
              color:var(--accent2);letter-spacing:0.05em;">--:--:--</span><br>
        <span class="rt-date" style="font-size:0.82rem;color:var(--txt1);">{data_fmt}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-wrap">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="login-card">
        <div class="login-logo">
            <span class="login-icon">🏢</span>
            <div class="login-title">{NOME_EMPRESA}</div>
            <div class="login-sub">Acesse sua área de trabalho</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    email = st.text_input("E-mail", placeholder="seu@empresa.com", key="l_email")
    senha = st.text_input("Senha", type="password", placeholder="••••••••", key="l_senha")

    if st.button("Entrar →", key="btn_entrar"):
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

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="text-align:center;margin-top:1.5rem;color:var(--txt2);font-size:0.76rem;">
        © 2025 {NOME_EMPRESA}
    </div>
    {RELOGIO_JS}
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# BARRA DE RELÓGIO EM TEMPO REAL (topo do conteúdo)
# ══════════════════════════════════════════════════════════════
def render_relogio_bar():
    try:
        tz  = pytz.timezone(TIMEZONE)
        now = datetime.now(tz)
    except Exception:
        now = datetime.now()

    data_fmt = f"{DIAS_PT[now.weekday()]}, {now.day} de {MESES_PT[now.month-1]} de {now.year}"
    hora_fmt = now.strftime("%H:%M:%S")

    st.markdown(f"""
    <div class="realtime-bar">
        <span class="rt-date">{data_fmt}</span>
        <span class="rt-time">{hora_fmt}</span>
    </div>
    {RELOGIO_JS}
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# BOTTOM NAV BAR (mobile)
# ══════════════════════════════════════════════════════════════
def render_bottom_nav(page_atual):
    paginas = [
        ("🏠", "Dashboard", "🏠  Dashboard"),
        ("🕐", "Ponto",     "🕐  Ponto"),
        ("📄", "Docs",      "📄  Documentos"),
    ]
    items_html = ""
    for icon, label, key in paginas:
        ativo = "active" if key in page_atual else ""
        items_html += f"""
        <button class="bnav-item {ativo}" onclick="window.parent.postMessage({{type:'streamlit:setComponentValue', key:'bnav_click', value:'{key}'}}, '*')">
            <span class="bnav-icon">{icon}</span>
            <span class="bnav-label">{label}</span>
        </button>"""

    st.markdown(f"""
    <div class="bottom-nav">
        <div class="bnav-inner">{items_html}</div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════
def render_dashboard(user):
    render_relogio_bar()
    st.markdown(f"""
    <div class="ph">
        <h1>Olá, {user['nome'].split()[0]}! 👋</h1>
    </div>
    """, unsafe_allow_html=True)

    if not GOOGLE_SHEETS_ID:
        st.markdown("""
        <div style="background:rgba(251,191,36,0.08);border:1px solid rgba(251,191,36,0.25);
                    border-radius:12px;padding:0.75rem 1.2rem;margin-bottom:1rem;
                    font-size:0.82rem;color:#8b9ab8;line-height:1.6;">
            🔗 <strong style="color:#f0f4ff">Google Sheets não configurado.</strong>
            Edite o topo do <code style="background:rgba(79,142,247,0.12);color:#7eb3ff;
            padding:0.1rem 0.3rem;border-radius:4px">app.py</code> e preencha
            <code style="background:rgba(79,142,247,0.12);color:#7eb3ff;
            padding:0.1rem 0.3rem;border-radius:4px">GOOGLE_SHEETS_ID</code>.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("#### 🎯 Meta do Mês")
    meta_atual = float(user.get("meta_atual") or 0)
    meta_total = float(user.get("meta_total") or 10000)
    pct        = min(int((meta_atual / meta_total) * 100), 100) if meta_total > 0 else 0
    cor        = "#34d399" if pct >= 80 else "#fbbf24" if pct >= 50 else "#f87171"
    restante   = max(meta_total - meta_atual, 0)

    st.markdown(f"""
    <div class="mc-grid">
        <div class="mc">
            <div class="mc-label">Vendido</div>
            <div class="mc-value" style="color:{cor}">R$ {meta_atual:,.2f}</div>
        </div>
        <div class="mc">
            <div class="mc-label">Meta Total</div>
            <div class="mc-value">R$ {meta_total:,.2f}</div>
        </div>
        <div class="mc">
            <div class="mc-label">Falta</div>
            <div class="mc-value" style="color:#fbbf24">R$ {restante:,.2f}</div>
        </div>
    </div>
    <div class="prog-wrap">
        <div class="prog-head"><span>Progresso</span><strong>{pct}%</strong></div>
        <div class="prog-bg">
            <div class="prog-fill" style="width:{pct}%;background:{cor};box-shadow:0 0 10px {cor}55"></div>
        </div>
        <div class="prog-msg">{"🔥 Excelente! Quase lá!" if pct>=80 else "💪 No caminho certo!" if pct>=50 else "🚀 Vamos acelerar!"}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 📢 Avisos")
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
    render_relogio_bar()
    st.markdown("""
    <div class="ph">
        <h1>🕐 Registro de Ponto</h1>
        <div class="ph-sub">Registre seus horários de trabalho</div>
    </div>
    """, unsafe_allow_html=True)

    hoje  = date.today()
    ponto = db_get_ponto_hoje(user["id"])

    st.markdown(f"""
    <div class="ponto-head">
        <span class="ponto-data">📅 {hoje.strftime('%d/%m/%Y')}</span>
        <span class="ponto-hora">--:--:--</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### Marcações de hoje")
    cards_html = '<div class="pk-grid">'
    for campo, label, _ in CAMPOS_PONTO:
        horario = ponto.get(campo) if ponto else None
        css_cls = "done" if horario else "pend"
        time_txt = f"✅ {horario}" if horario else "—"
        cards_html += f"""
        <div class="pk {css_cls}">
            <div class="pk-lbl">{label}</div>
            <div class="pk-time">{time_txt}</div>
        </div>"""
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)

    st.markdown("#### Registrar")
    col1, col2, col3 = st.columns(3)
    cols_map = [col1, col2, col3, col1, col2, col3]
    for i, (campo, label, btn_label) in enumerate(CAMPOS_PONTO):
        horario = ponto.get(campo) if ponto else None
        if not horario:
            anterior_ok = True
            if i > 0:
                campo_ant   = CAMPOS_PONTO[i - 1][0]
                anterior_ok = bool(ponto.get(campo_ant)) if ponto else False
            with cols_map[i]:
                if st.button(btn_label, key=f"ponto_{campo}", disabled=not anterior_ok):
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
                ("🟢", reg["entrada"]), ("🍽️", reg["saida_almoco"]),
                ("↩️", reg["retorno_almoco"]), ("☕", reg["saida_cafe"]),
                ("↩️", reg["retorno_cafe"]), ("🔴", reg["saida"]),
            ]
            marcacoes = "  ".join(f"{ic} {h or '—'}" for ic, h in campos_disp)
            st.markdown(f"""
            <div class="hist-row">
                <b>📅 {reg['data']}</b>
                <span style="font-family:var(--mono);font-size:0.79rem">{marcacoes}</span>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# DOCUMENTOS
# ══════════════════════════════════════════════════════════════
def render_documentos(user):
    render_relogio_bar()
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
        if st.button("💾 Salvar no Portal", key="btn_salvar"):
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
        <a href="{WHATSAPP_LINK}" target="_blank" style="text-decoration:none;display:block;margin-top:0.12rem">
            <button style="width:100%;background:#25d366;color:white;border:none;
                border-radius:12px;padding:0.56rem 0.8rem;font-size:0.88rem;font-weight:700;
                cursor:pointer;display:flex;align-items:center;justify-content:center;gap:7px;
                font-family:'Plus Jakarta Sans',sans-serif;box-shadow:0 3px 14px rgba(37,211,102,0.28);">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="white">
                    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
                </svg>
                Enviar pelo WhatsApp
            </button>
        </a>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="wpp-hint">
        💡 <strong>Como usar:</strong><br>
        1. Preencha o tipo e descrição, clique em <strong>Salvar no Portal</strong><br>
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
            <div style="text-align:right;flex-shrink:0;margin-left:1rem">
                <div class="doc-status" style="color:{cor_s}">{ic_s} {doc['status'].capitalize()}</div>
                <div class="doc-date">🕐 {doc['criado_em'][:10]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# ROTEAMENTO PRINCIPAL
# ══════════════════════════════════════════════════════════════

# 1️⃣  Verifica horário de serviço
permitido, motivo = verificar_horario_servico()
if not permitido:
    render_bloqueio(motivo)
    st.stop()

# 2️⃣  Login
if not st.session_state.logged_in:
    render_login()
    st.stop()

# 3️⃣  App principal
user = st.session_state.user

# ── Sidebar (desktop) ──────────────────────────────────────
with st.sidebar:
    try:
        tz  = pytz.timezone(TIMEZONE)
        now = datetime.now(tz)
    except Exception:
        now = datetime.now()
    hora_fmt = now.strftime("%H:%M:%S")
    data_fmt = f"{DIAS_PT[now.weekday()]}, {now.day}/{now.month:02d}/{now.year}"

    st.markdown(f"""
    <div class="sb-top">
        <div class="sb-avatar">{user['nome'][0].upper()}</div>
        <div class="sb-name">{user['nome']}</div>
        <div class="sb-role">{user['cargo']}</div>
        <div class="sb-clock">
            <div class="sb-clock-time">{hora_fmt}</div>
            <div class="sb-clock-date">{data_fmt}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio("", ["🏠  Dashboard", "🕐  Ponto", "📄  Documentos"],
                    label_visibility="collapsed", key="nav",
                    index=["🏠  Dashboard","🕐  Ponto","📄  Documentos"].index(st.session_state.page)
                          if st.session_state.page in ["🏠  Dashboard","🕐  Ponto","📄  Documentos"] else 0)
    st.session_state.page = page

    st.markdown("<br>" * 6, unsafe_allow_html=True)
    st.markdown('<div class="btn-logout">', unsafe_allow_html=True)
    if st.button("Sair", key="logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ── Navegação mobile via query param ──────────────────────
qp = st.query_params.get("nav", None)
if qp:
    mapa = {"dashboard": "🏠  Dashboard", "ponto": "🕐  Ponto", "docs": "📄  Documentos"}
    if qp in mapa:
        st.session_state.page = mapa[qp]
    st.query_params.clear()

page = st.session_state.page

# ── Bottom nav bar HTML (mobile) ──────────────────────────
nav_items = [
    ("🏠", "Dashboard", "dashboard"),
    ("🕐", "Ponto",     "ponto"),
    ("📄", "Docs",      "docs"),
]
itens_html = ""
for icon, label, key in nav_items:
    mapa_rev = {"dashboard":"🏠  Dashboard","ponto":"🕐  Ponto","docs":"📄  Documentos"}
    ativo = "active" if mapa_rev[key] == page else ""
    itens_html += f"""
    <a href="?nav={key}" style="text-decoration:none;">
        <div class="bnav-item {ativo}">
            <span class="bnav-icon">{icon}</span>
            <span class="bnav-label">{label}</span>
        </div>
    </a>"""

st.markdown(f"""
<div class="bottom-nav">
    <div class="bnav-inner">{itens_html}</div>
</div>
""", unsafe_allow_html=True)

# ── Renderiza página ──────────────────────────────────────
if "Dashboard" in page:
    render_dashboard(user)
elif "Ponto" in page:
    render_ponto(user)
elif "Documentos" in page:
    render_documentos(user)
