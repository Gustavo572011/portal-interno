# ╔══════════════════════════════════════════════════════════════╗
# ║           PORTAL INTERNO — COMSTRUKASA                      ║
# ╚══════════════════════════════════════════════════════════════╝
# Dependências: pip install streamlit
# Rodar:        streamlit run app.py

import streamlit as st
import sqlite3
import hashlib
import os
from datetime import datetime, date
import streamlit.components.v1 as components

try:
    import pytz
    _HAS_PYTZ = True
except ImportError:
    _HAS_PYTZ = False

# ══════════════════════════════════════════════════════════════
# ██  CONFIGURAÇÕES — EDITE AQUI  ██████████████████████████████
# ══════════════════════════════════════════════════════════════

GOOGLE_SHEETS_ID  = "1TbyUlf9wZGbQ3jyhj-QdpnHlNSd6GXHVYZCfdmVGXnM"                # ← ID da planilha Google Sheets
GOOGLE_SHEETS_ABA = "usuario"
WHATSAPP_LINK     = "https://wa.link/ng5osg"
NOME_EMPRESA      = "COMSTRUKASA"
TIMEZONE          = "America/Sao_Paulo"

# 🔒 Horários de funcionamento (hora_ini, min_ini, hora_fim, min_fim)
HORARIO_SEG_SEX = (7, 45, 19, 0)
HORARIO_SAB     = (7, 45, 13, 0)

# ══════════════════════════════════════════════════════════════
# CONFIGURAÇÕES TÉCNICAS
# ══════════════════════════════════════════════════════════════
DB_PATH  = "portal.db"
DIAS_PT  = ["Segunda","Terça","Quarta","Quinta","Sexta","Sábado","Domingo"]
MESES_PT = ["janeiro","fevereiro","março","abril","maio","junho",
            "julho","agosto","setembro","outubro","novembro","dezembro"]
TIPOS_DOC = ["Atestado Médico","Declaração","Comprovante de Endereço",
             "Documento Pessoal (RG/CPF)","Comprovante de Escolaridade","Contrato","Outros"]
CAMPOS_PONTO = [
    ("entrada",        "🟢 Entrada",        "Registrar Entrada"),
    ("saida_almoco",   "🍽️ Saída Almoço",   "Saída Almoço"),
    ("retorno_almoco", "↩️ Retorno Almoço", "Retorno Almoço"),
    ("saida_cafe",     "☕ Saída Café",      "Saída Café"),
    ("retorno_cafe",   "↩️ Retorno Café",   "Retorno Café"),
    ("saida",          "🔴 Saída",           "Registrar Saída"),
]

# ══════════════════════════════════════════════════════════════
# PÁGINA
# ══════════════════════════════════════════════════════════════
st.set_page_config(page_title=NOME_EMPRESA, page_icon="🏗️",
                   layout="wide", initial_sidebar_state="auto")

# ══════════════════════════════════════════════════════════════
# HELPERS DE TEMPO
# ══════════════════════════════════════════════════════════════
def agora_local():
    try:
        if _HAS_PYTZ:
            return datetime.now(pytz.timezone(TIMEZONE))
    except Exception:
        pass
    return datetime.now()

def verificar_horario():
    now = agora_local()
    dow = now.weekday()
    hm  = now.hour * 60 + now.minute

    def prox_str(d, h):
        return f"{DIAS_PT[d]} às {h[0]:02d}:{h[1]:02d}"

    if dow < 5:
        ini = HORARIO_SEG_SEX[0]*60 + HORARIO_SEG_SEX[1]
        fim = HORARIO_SEG_SEX[2]*60 + HORARIO_SEG_SEX[3]
        if ini <= hm <= fim:
            return True, "", ""
        if hm < ini:
            return False, "antes", f"hoje às {HORARIO_SEG_SEX[0]:02d}:{HORARIO_SEG_SEX[1]:02d}"
        nd = (dow+1)%7
        if nd < 5:
            return False, "depois", prox_str(nd, HORARIO_SEG_SEX)
        elif nd == 5:
            return False, "depois", prox_str(nd, HORARIO_SAB)
        else:
            return False, "depois", f"Segunda-feira às {HORARIO_SEG_SEX[0]:02d}:{HORARIO_SEG_SEX[1]:02d}"
    elif dow == 5:
        ini = HORARIO_SAB[0]*60 + HORARIO_SAB[1]
        fim = HORARIO_SAB[2]*60 + HORARIO_SAB[3]
        if ini <= hm <= fim:
            return True, "", ""
        if hm < ini:
            return False, "antes", f"hoje às {HORARIO_SAB[0]:02d}:{HORARIO_SAB[1]:02d}"
        return False, "depois", f"Segunda-feira às {HORARIO_SEG_SEX[0]:02d}:{HORARIO_SEG_SEX[1]:02d}"
    else:
        return False, "domingo", f"Segunda-feira às {HORARIO_SEG_SEX[0]:02d}:{HORARIO_SEG_SEX[1]:02d}"

# ══════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');
:root{
  --bg0:#080c14;--bg1:#0e1420;--bg2:#131929;--bg3:#1a2236;
  --border:rgba(255,255,255,0.07);--border2:rgba(255,255,255,0.12);
  --accent:#4f8ef7;--accent2:#7eb3ff;
  --green:#34d399;--amber:#fbbf24;--red:#f87171;
  --txt0:#f0f4ff;--txt1:#8b9ab8;--txt2:#4a5568;
  --r:12px;--r2:18px;
  --font:'Plus Jakarta Sans',sans-serif;--mono:'DM Mono',monospace;
}
html,body,[class*="css"]{font-family:var(--font)!important;background:var(--bg0)!important;color:var(--txt0)!important;}
#MainMenu,footer,header{visibility:hidden;}
.stDeployButton,[data-testid="stToolbar"]{display:none!important;}
.main .block-container{padding:1.5rem 1.5rem 5.5rem!important;max-width:1100px!important;}

[data-testid="stSidebar"]{background:var(--bg1)!important;border-right:1px solid var(--border)!important;min-width:230px!important;max-width:230px!important;}
[data-testid="stSidebar"]>div{padding-top:0!important;}
.sb-top{background:linear-gradient(160deg,#1a2a4a 0%,var(--bg1) 100%);padding:1.75rem 1.25rem 1rem;border-bottom:1px solid var(--border);margin-bottom:.4rem;}
.sb-avatar{width:52px;height:52px;border-radius:50%;background:linear-gradient(135deg,var(--accent),#7c3aed);color:white;font-size:1.4rem;font-weight:800;display:flex;align-items:center;justify-content:center;margin-bottom:.65rem;box-shadow:0 0 0 3px rgba(79,142,247,.2),0 6px 16px rgba(0,0,0,.4);}
.sb-name{font-size:.92rem;font-weight:700;color:var(--txt0);margin-bottom:.2rem;}
.sb-role{font-size:.7rem;font-weight:600;color:var(--accent2);background:rgba(79,142,247,.12);border:1px solid rgba(79,142,247,.2);padding:.15rem .5rem;border-radius:20px;display:inline-block;}
[data-testid="stSidebar"] [data-testid="stRadio"]>div{gap:.15rem!important;}
[data-testid="stSidebar"] [data-testid="stRadio"] label{background:transparent!important;border:none!important;padding:.6rem 1.1rem!important;border-radius:10px!important;font-size:.9rem!important;font-weight:500!important;color:var(--txt1)!important;transition:all .15s!important;margin:.05rem .4rem!important;}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover{background:rgba(255,255,255,.05)!important;color:var(--txt0)!important;}

.stButton>button{background:var(--accent)!important;color:white!important;border:none!important;border-radius:var(--r)!important;font-family:var(--font)!important;font-weight:600!important;font-size:.88rem!important;padding:.55rem 1.1rem!important;transition:all .18s!important;box-shadow:0 3px 12px rgba(79,142,247,.22)!important;width:100%!important;}
.stButton>button:hover{background:var(--accent2)!important;transform:translateY(-1px)!important;box-shadow:0 5px 18px rgba(79,142,247,.38)!important;}
.stButton>button:disabled{background:var(--bg3)!important;color:var(--txt2)!important;box-shadow:none!important;transform:none!important;}
.btn-logout .stButton>button{background:transparent!important;border:1px solid var(--border2)!important;color:var(--txt1)!important;box-shadow:none!important;}
.btn-logout .stButton>button:hover{background:rgba(248,113,113,.08)!important;border-color:var(--red)!important;color:var(--red)!important;transform:none!important;box-shadow:none!important;}

.stTextInput input,.stTextArea textarea,.stSelectbox>div>div{background:var(--bg2)!important;border:1px solid var(--border2)!important;border-radius:var(--r)!important;color:var(--txt0)!important;font-family:var(--font)!important;font-size:.9rem!important;}
.stTextInput input:focus,.stTextArea textarea:focus{border-color:var(--accent)!important;box-shadow:0 0 0 3px rgba(79,142,247,.15)!important;}
.stTextInput label,.stTextArea label,.stSelectbox label,.stFileUploader label{color:var(--txt1)!important;font-size:.82rem!important;font-weight:500!important;}
.stSuccess>div{background:rgba(52,211,153,.1)!important;border:1px solid rgba(52,211,153,.3)!important;border-radius:var(--r)!important;}
.stError>div{background:rgba(248,113,113,.1)!important;border:1px solid rgba(248,113,113,.3)!important;border-radius:var(--r)!important;}
.stInfo>div{background:rgba(79,142,247,.1)!important;border:1px solid rgba(79,142,247,.3)!important;border-radius:var(--r)!important;}
.stWarning>div{background:rgba(251,191,36,.1)!important;border:1px solid rgba(251,191,36,.3)!important;border-radius:var(--r)!important;}
[data-testid="stFileUploader"]>div{background:var(--bg2)!important;border:1.5px dashed var(--border2)!important;border-radius:var(--r)!important;}
.streamlit-expanderHeader{background:var(--bg2)!important;border:1px solid var(--border)!important;border-radius:var(--r)!important;color:var(--txt1)!important;}

.ph{margin-bottom:1.5rem;}
.ph h1{font-size:1.75rem!important;font-weight:800!important;color:var(--txt0)!important;margin:0 0 .15rem!important;letter-spacing:-.02em;}
.ph-sub{color:var(--txt1);font-size:.86rem;}
.mc-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:.75rem;margin-bottom:.75rem;}
.mc{background:var(--bg2);border:1px solid var(--border);border-radius:var(--r2);padding:1.2rem 1.3rem;transition:transform .2s,box-shadow .2s;}
.mc:hover{transform:translateY(-2px);box-shadow:0 6px 24px rgba(0,0,0,.3);}
.mc-label{font-size:.72rem;font-weight:600;color:var(--txt2);text-transform:uppercase;letter-spacing:.08em;margin-bottom:.4rem;}
.mc-value{font-size:1.5rem;font-weight:800;font-family:var(--mono);color:var(--txt0);}
.prog-wrap{background:var(--bg2);border:1px solid var(--border);border-radius:var(--r2);padding:1.3rem 1.4rem;margin:.25rem 0 1.25rem;}
.prog-head{display:flex;justify-content:space-between;color:var(--txt1);font-size:.83rem;margin-bottom:.65rem;}
.prog-head strong{color:var(--txt0);font-family:var(--mono);}
.prog-bg{height:9px;background:var(--bg0);border-radius:100px;overflow:hidden;}
.prog-fill{height:100%;border-radius:100px;transition:width 1.2s cubic-bezier(.4,0,.2,1);}
.prog-msg{margin-top:.65rem;font-size:.82rem;color:var(--txt1);text-align:center;}
.av{background:var(--bg2);border-radius:var(--r);padding:1rem 1.3rem;margin-bottom:.6rem;border-left:3px solid var(--accent);transition:transform .15s;}
.av:hover{transform:translateX(4px);}
.av-title{font-weight:700;font-size:.93rem;margin-bottom:.25rem;}
.av-body{color:var(--txt1);font-size:.85rem;line-height:1.5;}
.av-date{margin-top:.4rem;font-size:.73rem;color:var(--txt2);}
.login-wrap{max-width:400px;margin:1.5rem auto;padding:0 .5rem;}
.login-card{background:var(--bg1);border:1px solid var(--border2);border-radius:22px;padding:2.2rem 2rem 1.8rem;box-shadow:0 20px 60px rgba(0,0,0,.5);}
.login-logo{text-align:center;margin-bottom:1.75rem;}
.login-icon{font-size:2.6rem;display:block;margin-bottom:.4rem;}
.login-title{font-size:1.6rem!important;font-weight:800!important;color:var(--txt0)!important;letter-spacing:-.03em;margin:0 0 .15rem!important;}
.login-sub{color:var(--txt1);font-size:.85rem;}
.ponto-head{display:flex;flex-wrap:wrap;gap:1rem 2rem;align-items:center;background:var(--bg2);border:1px solid var(--border);border-radius:var(--r2);padding:1rem 1.4rem;margin-bottom:1.25rem;}
.ponto-data{font-size:.9rem;font-weight:600;color:var(--txt1);}
.pk-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:.6rem;margin-bottom:.5rem;}
.pk{border-radius:var(--r);padding:.9rem .75rem;text-align:center;border:1px solid var(--border);}
.pk.done{background:rgba(52,211,153,.07);border-color:rgba(52,211,153,.22);}
.pk.pend{background:var(--bg2);}
.pk-lbl{font-size:.7rem;color:var(--txt2);text-transform:uppercase;letter-spacing:.06em;margin-bottom:.3rem;font-weight:600;}
.pk-time{font-size:1rem;font-weight:700;font-family:var(--mono);color:var(--txt0);}
.hist-row{display:flex;flex-wrap:wrap;gap:.5rem 1rem;align-items:center;padding:.65rem 1rem;background:var(--bg2);border-radius:var(--r);margin-bottom:.35rem;font-size:.82rem;color:var(--txt1);border:1px solid var(--border);}
.hist-row b{color:var(--txt0);}
.doc-card{display:flex;justify-content:space-between;align-items:flex-start;background:var(--bg2);border:1px solid var(--border);border-radius:var(--r);padding:1rem 1.3rem;margin-bottom:.55rem;transition:transform .15s;}
.doc-card:hover{transform:translateX(3px);}
.doc-tipo{font-weight:700;font-size:.88rem;display:block;margin-bottom:.18rem;}
.doc-arq{font-size:.78rem;color:var(--txt1);font-family:var(--mono);}
.doc-desc{font-size:.76rem;color:var(--txt2);margin-top:.12rem;display:block;}
.doc-status{font-size:.8rem;font-weight:700;}
.doc-date{font-size:.73rem;color:var(--txt2);margin-top:.25rem;}
.wpp-hint{background:rgba(37,211,102,.07);border:1px solid rgba(37,211,102,.2);border-radius:var(--r);padding:.9rem 1.3rem;font-size:.83rem;color:var(--txt1);line-height:1.75;margin:.6rem 0 1.25rem;}
.wpp-hint strong{color:var(--txt0);}

/* Mobile nav buttons estilizados */
.mobile-nav-bar{display:none;}
@media(max-width:768px){
  [data-testid="stSidebar"]{display:none!important;}
  [data-testid="collapsedControl"]{display:none!important;}
  .main .block-container{padding:1rem .85rem 5.5rem!important;margin-left:0!important;}
  .ph h1{font-size:1.3rem!important;}
  .mc-grid{grid-template-columns:repeat(2,1fr)!important;}
  .pk-grid{grid-template-columns:repeat(2,1fr)!important;}
  .doc-card{flex-direction:column;gap:.4rem;}
  /* Fixa os botões de nav no rodapé */
  [data-testid="stHorizontalBlock"].mobile-nav-bar{
    position:fixed!important;bottom:0!important;left:0!important;right:0!important;
    z-index:9999!important;background:rgba(14,20,32,.97)!important;
    border-top:1px solid rgba(255,255,255,.12)!important;
    padding:6px 8px calc(6px + env(safe-area-inset-bottom))!important;
    backdrop-filter:blur(16px)!important;gap:6px!important;margin:0!important;
  }
}
@media(max-width:480px){
  .main .block-container{padding:.75rem .6rem 5.5rem!important;}
  .ph h1{font-size:1.15rem!important;}
  .mc-grid{grid-template-columns:1fr!important;gap:.5rem!important;}
  .pk-grid{grid-template-columns:1fr 1fr!important;}
  .login-card{padding:1.5rem 1.2rem;border-radius:18px;}
  .login-title{font-size:1.35rem!important;}
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SNIPPETS DE RELÓGIO (components.html — iframe próprio → JS funciona)
# ══════════════════════════════════════════════════════════════
def clock_bar():
    """Barra de relógio para topo das páginas."""
    components.html("""
    <style>
    *{margin:0;padding:0;box-sizing:border-box;}
    body{background:transparent;font-family:'Plus Jakarta Sans',sans-serif;}
    .bar{display:flex;align-items:center;justify-content:flex-end;gap:12px;
         padding:4px 0 16px;border-bottom:1px solid rgba(255,255,255,.07);margin-bottom:4px;}
    #dt{font-size:.83rem;color:#8b9ab8;}
    #tm{font-family:'DM Mono',monospace;font-size:1.1rem;font-weight:700;color:#7eb3ff;
        background:rgba(79,142,247,.1);border:1px solid rgba(79,142,247,.2);
        padding:3px 12px;border-radius:8px;letter-spacing:.04em;min-width:92px;text-align:center;}
    </style>
    <div class="bar"><span id="dt"></span><span id="tm"></span></div>
    <script>
    var dias=['Domingo','Segunda','Terça','Quarta','Quinta','Sexta','Sábado'];
    var meses=['janeiro','fevereiro','março','abril','maio','junho','julho','agosto','setembro','outubro','novembro','dezembro'];
    function pad(n){return String(n).padStart(2,'0');}
    function tick(){
      var n=new Date();
      document.getElementById('tm').textContent=pad(n.getHours())+':'+pad(n.getMinutes())+':'+pad(n.getSeconds());
      document.getElementById('dt').textContent=dias[n.getDay()]+', '+n.getDate()+' de '+meses[n.getMonth()]+' de '+n.getFullYear();
    }
    tick();setInterval(tick,1000);
    </script>
    """, height=52)

def clock_login():
    """Relógio grande para tela de login."""
    components.html("""
    <style>
    *{margin:0;padding:0;box-sizing:border-box;}
    body{background:transparent;font-family:'Plus Jakarta Sans',sans-serif;text-align:center;}
    #lt{font-family:'DM Mono',monospace;font-size:2.2rem;font-weight:800;color:#7eb3ff;letter-spacing:.06em;display:block;}
    #ld{font-size:.82rem;color:#8b9ab8;margin-top:5px;display:block;}
    </style>
    <span id="lt"></span><span id="ld"></span>
    <script>
    var dias=['Domingo','Segunda','Terça','Quarta','Quinta','Sexta','Sábado'];
    var meses=['janeiro','fevereiro','março','abril','maio','junho','julho','agosto','setembro','outubro','novembro','dezembro'];
    function pad(n){return String(n).padStart(2,'0');}
    function tick(){
      var n=new Date();
      document.getElementById('lt').textContent=pad(n.getHours())+':'+pad(n.getMinutes())+':'+pad(n.getSeconds());
      document.getElementById('ld').textContent=dias[n.getDay()]+', '+n.getDate()+' de '+meses[n.getMonth()]+' de '+n.getFullYear();
    }
    tick();setInterval(tick,1000);
    </script>
    """, height=72)

def clock_sidebar():
    """Relógio compacto para sidebar."""
    components.html("""
    <style>
    *{margin:0;padding:0;box-sizing:border-box;}
    body{background:transparent;font-family:'Plus Jakarta Sans',sans-serif;}
    .wrap{background:#131929;border:1px solid rgba(255,255,255,.07);border-radius:12px;padding:10px 14px;text-align:center;margin:10px 0 4px;}
    #st{font-family:'DM Mono',monospace;font-size:1.35rem;font-weight:700;color:#7eb3ff;letter-spacing:.05em;display:block;}
    #sd{font-size:.7rem;color:#8b9ab8;margin-top:3px;display:block;}
    </style>
    <div class="wrap"><span id="st"></span><span id="sd"></span></div>
    <script>
    var dias=['Dom','Seg','Ter','Qua','Qui','Sex','Sáb'];
    function pad(n){return String(n).padStart(2,'0');}
    function tick(){
      var n=new Date();
      document.getElementById('st').textContent=pad(n.getHours())+':'+pad(n.getMinutes())+':'+pad(n.getSeconds());
      document.getElementById('sd').textContent=dias[n.getDay()]+' '+pad(n.getDate())+'/'+pad(n.getMonth()+1)+'/'+n.getFullYear();
    }
    tick();setInterval(tick,1000);
    </script>
    """, height=68)

def clock_ponto():
    """Relógio em tempo real para a aba de ponto."""
    components.html("""
    <style>
    *{margin:0;padding:0;box-sizing:border-box;}
    body{background:transparent;font-family:'Plus Jakarta Sans',sans-serif;}
    .wrap{background:#131929;border:1px solid rgba(255,255,255,.07);border-radius:18px;
          padding:12px 18px;display:flex;align-items:center;gap:10px;}
    .lbl{font-size:.85rem;font-weight:600;color:#8b9ab8;}
    #pt{font-family:'DM Mono',monospace;font-size:1.3rem;font-weight:700;color:#7eb3ff;letter-spacing:.04em;}
    </style>
    <div class="wrap"><span class="lbl">⏱️ Agora:</span><span id="pt"></span></div>
    <script>
    function pad(n){return String(n).padStart(2,'0');}
    function tick(){
      var n=new Date();
      document.getElementById('pt').textContent=pad(n.getHours())+':'+pad(n.getMinutes())+':'+pad(n.getSeconds());
    }
    tick();setInterval(tick,1000);
    </script>
    """, height=56)

def clock_bloqueio():
    """Relógio grande vermelho para tela de bloqueio."""
    components.html("""
    <style>
    *{margin:0;padding:0;box-sizing:border-box;}
    body{background:transparent;font-family:'DM Mono',monospace;text-align:center;}
    #bt{font-size:3rem;font-weight:800;color:rgba(248,113,113,.35);letter-spacing:.08em;display:block;}
    </style>
    <span id="bt"></span>
    <script>
    function pad(n){return String(n).padStart(2,'0');}
    function tick(){
      var n=new Date();
      document.getElementById('bt').textContent=pad(n.getHours())+':'+pad(n.getMinutes())+':'+pad(n.getSeconds());
    }
    tick();setInterval(tick,1000);
    </script>
    """, height=60)

# ══════════════════════════════════════════════════════════════
# BANCO DE DADOS
# ══════════════════════════════════════════════════════════════
def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn=get_conn();c=conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS usuarios(
        id INTEGER PRIMARY KEY AUTOINCREMENT,nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,senha TEXT,cargo TEXT DEFAULT 'Funcionário',
        meta_atual REAL DEFAULT 0,meta_total REAL DEFAULT 10000,
        ativo INTEGER DEFAULT 1,criado_em TEXT DEFAULT CURRENT_TIMESTAMP)""")
    c.execute("""CREATE TABLE IF NOT EXISTS avisos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,titulo TEXT NOT NULL,corpo TEXT NOT NULL,
        tipo TEXT DEFAULT 'info',criado_em TEXT DEFAULT CURRENT_TIMESTAMP,ativo INTEGER DEFAULT 1)""")
    c.execute("""CREATE TABLE IF NOT EXISTS ponto(
        id INTEGER PRIMARY KEY AUTOINCREMENT,usuario_id INTEGER NOT NULL,data TEXT NOT NULL,
        entrada TEXT,saida_almoco TEXT,retorno_almoco TEXT,saida_cafe TEXT,retorno_cafe TEXT,saida TEXT,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id))""")
    c.execute("""CREATE TABLE IF NOT EXISTS documentos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,usuario_id INTEGER NOT NULL,tipo TEXT NOT NULL,
        descricao TEXT,arquivo_nome TEXT,status TEXT DEFAULT 'enviado',
        criado_em TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(usuario_id) REFERENCES usuarios(id))""")
    for nome,email,senha,cargo,ma,mt in [
        ("Admin","admin@empresa.com","admin123","Gerente",7500,10000),
        ("João Silva","joao@empresa.com","123456","Vendedor",4200,8000),
    ]:
        h=hashlib.sha256(senha.encode()).hexdigest()
        c.execute("INSERT OR IGNORE INTO usuarios(nome,email,senha,cargo,meta_atual,meta_total) VALUES(?,?,?,?,?,?)",(nome,email,h,cargo,ma,mt))
    c.execute("INSERT OR IGNORE INTO avisos(id,titulo,corpo,tipo) VALUES(1,'🎉 Reunião Mensal','Reunião de alinhamento na sexta-feira às 14h na sala de reuniões.','info')")
    c.execute("INSERT OR IGNORE INTO avisos(id,titulo,corpo,tipo) VALUES(2,'⚠️ Prazo de Metas','O fechamento do mês ocorre dia 30. Atenção ao cumprimento das metas!','warning')")
    conn.commit();conn.close()

def db_get_user(email):
    conn=get_conn();c=conn.cursor()
    c.execute("SELECT * FROM usuarios WHERE email=? AND ativo=1",(email,))
    row=c.fetchone();conn.close()
    if row: return dict(zip(["id","nome","email","senha","cargo","meta_atual","meta_total","ativo","criado_em"],row))
    return None

def db_get_avisos():
    conn=get_conn();c=conn.cursor()
    c.execute("SELECT * FROM avisos WHERE ativo=1 ORDER BY criado_em DESC LIMIT 5")
    rows=c.fetchall();conn.close()
    return [dict(zip(["id","titulo","corpo","tipo","criado_em","ativo"],r)) for r in rows]

def db_get_ponto_hoje(uid):
    conn=get_conn();c=conn.cursor()
    c.execute("SELECT * FROM ponto WHERE usuario_id=? AND data=?",(uid,date.today().isoformat()))
    row=c.fetchone();conn.close()
    if row: return dict(zip(["id","usuario_id","data","entrada","saida_almoco","retorno_almoco","saida_cafe","retorno_cafe","saida"],row))
    return None

def db_registrar_ponto(uid,campo):
    conn=get_conn();c=conn.cursor()
    hoje=date.today().isoformat();agora=datetime.now().strftime("%H:%M:%S")
    if db_get_ponto_hoje(uid): c.execute(f"UPDATE ponto SET {campo}=? WHERE usuario_id=? AND data=?",(agora,uid,hoje))
    else: c.execute(f"INSERT INTO ponto(usuario_id,data,{campo}) VALUES(?,?,?)",(uid,hoje,agora))
    conn.commit();conn.close();return agora

def db_historico_ponto(uid,limit=10):
    conn=get_conn();c=conn.cursor()
    c.execute("SELECT * FROM ponto WHERE usuario_id=? ORDER BY data DESC LIMIT ?",(uid,limit))
    rows=c.fetchall();conn.close()
    return [dict(zip(["id","usuario_id","data","entrada","saida_almoco","retorno_almoco","saida_cafe","retorno_cafe","saida"],r)) for r in rows]

def db_salvar_doc(uid,tipo,descricao,nome_arquivo):
    conn=get_conn();c=conn.cursor()
    c.execute("INSERT INTO documentos(usuario_id,tipo,descricao,arquivo_nome) VALUES(?,?,?,?)",(uid,tipo,descricao,nome_arquivo))
    conn.commit();conn.close()

def db_get_docs(uid):
    conn=get_conn();c=conn.cursor()
    c.execute("SELECT * FROM documentos WHERE usuario_id=? ORDER BY criado_em DESC",(uid,))
    rows=c.fetchall();conn.close()
    return [dict(zip(["id","usuario_id","tipo","descricao","arquivo_nome","status","criado_em"],r)) for r in rows]

init_db()

# ══════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════
for k,v in [("logged_in",False),("user",None),("page","dashboard")]:
    if k not in st.session_state:
        st.session_state[k]=v

# ══════════════════════════════════════════════════════════════
# 🔒 TELA DE BLOQUEIO
# ══════════════════════════════════════════════════════════════
def render_bloqueio(motivo, prox):
    now = agora_local()
    dia_nome = DIAS_PT[now.weekday()]
    h_seg = f"{HORARIO_SEG_SEX[0]:02d}:{HORARIO_SEG_SEX[1]:02d} – {HORARIO_SEG_SEX[2]:02d}:{HORARIO_SEG_SEX[3]:02d}"
    h_sab = f"{HORARIO_SAB[0]:02d}:{HORARIO_SAB[1]:02d} – {HORARIO_SAB[2]:02d}:{HORARIO_SAB[3]:02d}"

    if motivo == "domingo":
        titulo    = "Domingo — Portal Fechado"
        subtitulo = "Aproveite o descanso! O portal não funciona aos domingos."
        emoji     = "😴"
    elif motivo == "antes":
        titulo    = "Ainda não é hora de trabalhar!"
        subtitulo = f"O expediente começa às {prox.split('às')[-1].strip()}. Aguarde um pouco!"
        emoji     = "🌅"
    else:
        titulo    = "Expediente Encerrado"
        subtitulo = f"O período de hoje foi encerrado. Descanse bem!"
        emoji     = "🌙"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=DM+Mono:wght@400;700&display=swap');
    html,body,[class*="css"]{{background:#06080f!important;font-family:'Plus Jakarta Sans',sans-serif!important;}}
    .blk-outer{{
        min-height:95vh;display:flex;flex-direction:column;align-items:center;
        justify-content:center;
        background:radial-gradient(ellipse 90% 55% at 50% 0%,rgba(248,113,113,.09) 0%,transparent 65%),
                   radial-gradient(ellipse 60% 40% at 50% 100%,rgba(79,142,247,.05) 0%,transparent 60%),
                   #06080f;
        padding:2rem 1rem;
    }}
    .blk-card{{
        max-width:480px;width:100%;
        background:linear-gradient(145deg,#100808,#0c1220);
        border:1px solid rgba(248,113,113,.18);
        border-radius:28px;
        padding:2.75rem 2.5rem 2.25rem;
        box-shadow:0 0 0 1px rgba(248,113,113,.06),
                   0 32px 80px rgba(0,0,0,.65),
                   inset 0 1px 0 rgba(255,255,255,.04);
        text-align:center;
        position:relative;overflow:hidden;
    }}
    .blk-card::before{{
        content:'';position:absolute;top:-80px;left:50%;transform:translateX(-50%);
        width:300px;height:300px;border-radius:50%;
        background:radial-gradient(circle,rgba(248,113,113,.07) 0%,transparent 70%);
        pointer-events:none;
    }}
    .blk-badge{{
        display:inline-flex;align-items:center;gap:6px;
        background:rgba(248,113,113,.1);border:1px solid rgba(248,113,113,.22);
        color:#f87171;font-size:.72rem;font-weight:700;
        padding:.28rem .85rem;border-radius:20px;letter-spacing:.07em;text-transform:uppercase;
        margin-bottom:1.5rem;
    }}
    .blk-emoji{{font-size:3.8rem;display:block;margin-bottom:.75rem;line-height:1;}}
    .blk-title{{
        font-size:1.65rem;font-weight:800;color:#f0f4ff;
        letter-spacing:-.03em;margin-bottom:.5rem;line-height:1.2;
    }}
    .blk-sub{{color:#8b9ab8;font-size:.9rem;line-height:1.65;margin-bottom:1.75rem;}}
    .blk-prox{{
        background:rgba(79,142,247,.07);border:1px solid rgba(79,142,247,.16);
        border-radius:14px;padding:.9rem 1.3rem;margin-bottom:1.5rem;
        font-size:.86rem;color:#8b9ab8;line-height:1.8;
    }}
    .blk-prox strong{{color:#7eb3ff;font-size:1rem;}}
    .blk-table{{
        background:#0d1118;border:1px solid rgba(255,255,255,.07);
        border-radius:14px;padding:1rem 1.4rem;text-align:left;
        font-size:.84rem;color:#8b9ab8;
    }}
    .blk-table-title{{
        font-size:.72rem;font-weight:700;color:#4a5568;
        text-transform:uppercase;letter-spacing:.08em;
        display:block;margin-bottom:.7rem;
    }}
    .blk-row{{display:flex;justify-content:space-between;align-items:center;padding:.3rem 0;border-bottom:1px solid rgba(255,255,255,.04);}}
    .blk-row:last-child{{border-bottom:none;}}
    .blk-row-label{{color:#c8d4e8;font-weight:500;}}
    .blk-row-value{{font-family:'DM Mono',monospace;font-size:.82rem;color:#7eb3ff;}}
    .blk-row-closed{{color:#f87171!important;}}
    .blk-footer{{margin-top:1.75rem;color:#2d3748;font-size:.74rem;}}
    .blk-empresa{{color:#4a5568;font-size:.8rem;font-weight:600;letter-spacing:.05em;margin-top:.3rem;}}
    </style>
    <div class="blk-outer">
      <div class="blk-card">
        <div class="blk-badge">🔒 Portal Indisponível</div>
        <span class="blk-emoji">{emoji}</span>
        <div class="blk-title">{titulo}</div>
        <div class="blk-sub">{subtitulo}</div>
    """, unsafe_allow_html=True)

    clock_bloqueio()

    st.markdown(f"""
        <div style="color:#4a5568;font-size:.78rem;margin-bottom:1.5rem;">
            {dia_nome} · {now.strftime('%d/%m/%Y')}
        </div>
        <div class="blk-prox">
            🕐 Próxima abertura<br>
            <strong>{prox}</strong>
        </div>
        <div class="blk-table">
          <span class="blk-table-title">Horário de Funcionamento</span>
          <div class="blk-row">
            <span class="blk-row-label">Segunda a Sexta</span>
            <span class="blk-row-value">{h_seg}</span>
          </div>
          <div class="blk-row">
            <span class="blk-row-label">Sábado</span>
            <span class="blk-row-value">{h_sab}</span>
          </div>
          <div class="blk-row">
            <span class="blk-row-label">Domingo</span>
            <span class="blk-row-value blk-row-closed">Fechado</span>
          </div>
        </div>
      </div>
      <div class="blk-footer">© 2025 <span class="blk-empresa">{NOME_EMPRESA}</span></div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TELA DE LOGIN
# ══════════════════════════════════════════════════════════════
def render_login():
    clock_login()
    st.markdown('<div class="login-wrap">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="login-card">
      <div class="login-logo">
        <span class="login-icon">🏗️</span>
        <div class="login-title">{NOME_EMPRESA}</div>
        <div class="login-sub">Acesse sua área de trabalho</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    email=st.text_input("E-mail",placeholder="seu@empresa.com",key="l_email")
    senha=st.text_input("Senha",type="password",placeholder="••••••••",key="l_senha")
    if st.button("Entrar →",key="btn_entrar"):
        if not email or not senha: st.error("Preencha e-mail e senha.")
        else:
            user=db_get_user(email)
            if user and user.get("senha")==hashlib.sha256(senha.encode()).hexdigest():
                st.session_state.logged_in=True;st.session_state.user=user;st.rerun()
            else: st.error("E-mail ou senha incorretos.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center;margin-top:1.5rem;color:#4a5568;font-size:.76rem;">© 2025 {NOME_EMPRESA}</div>',unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# NAVEGAÇÃO MOBILE — botões Streamlit nativos, sem reload
# ══════════════════════════════════════════════════════════════
def render_mobile_nav():
    page = st.session_state.page
    items = [("🏠","Dashboard","dashboard"),("🕐","Ponto","ponto"),("📄","Docs","docs")]
    c1,c2,c3 = st.columns(3)
    for col,(icon,label,key) in zip([c1,c2,c3],items):
        with col:
            is_active = (page == key)
            btn_style = "primary" if is_active else "secondary"
            if st.button(f"{icon}\n{label}", key=f"mnav_{key}",
                         use_container_width=True, type=btn_style):
                st.session_state.page = key
                st.rerun()

    # CSS para fixar no rodapé apenas em mobile
    st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"]:has(button[data-testid*="mnav_"]) {
      position:fixed!important;bottom:0!important;left:0!important;right:0!important;
      z-index:9999!important;
      background:rgba(14,20,32,.97)!important;
      border-top:1px solid rgba(255,255,255,.12)!important;
      padding:6px 10px calc(8px + env(safe-area-inset-bottom))!important;
      backdrop-filter:blur(16px)!important;
      gap:6px!important;margin:0!important;
    }
    @media(min-width:769px){
      div[data-testid="stHorizontalBlock"]:has(button[data-testid*="mnav_"]){
        display:none!important;
      }
    }
    div[data-testid="stHorizontalBlock"]:has(button[data-testid*="mnav_"]) .stButton>button{
      border-radius:12px!important;font-size:.72rem!important;
      padding:.45rem .3rem!important;font-weight:700!important;
      line-height:1.4!important;white-space:pre!important;
    }
    div[data-testid="stHorizontalBlock"]:has(button[data-testid*="mnav_"]) .stButton>button[kind="primary"]{
      background:rgba(79,142,247,.18)!important;
      border:1px solid rgba(79,142,247,.35)!important;
      color:#7eb3ff!important;box-shadow:none!important;
    }
    div[data-testid="stHorizontalBlock"]:has(button[data-testid*="mnav_"]) .stButton>button[kind="secondary"]{
      background:transparent!important;
      border:1px solid rgba(255,255,255,.07)!important;
      color:#4a5568!important;box-shadow:none!important;
    }
    </style>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# PÁGINAS
# ══════════════════════════════════════════════════════════════
def render_dashboard(user):
    clock_bar()
    st.markdown(f'<div class="ph"><h1>Olá, {user["nome"].split()[0]}! 👋</h1></div>', unsafe_allow_html=True)
    if not GOOGLE_SHEETS_ID:
        st.markdown("""<div style="background:rgba(251,191,36,.08);border:1px solid rgba(251,191,36,.25);
            border-radius:12px;padding:.7rem 1.2rem;margin-bottom:1rem;font-size:.82rem;color:#8b9ab8;line-height:1.6;">
            🔗 <strong style="color:#f0f4ff">Google Sheets não configurado.</strong>
            Edite o topo do <code style="background:rgba(79,142,247,.12);color:#7eb3ff;padding:.1rem .3rem;border-radius:4px">app.py</code>
            e preencha <code style="background:rgba(79,142,247,.12);color:#7eb3ff;padding:.1rem .3rem;border-radius:4px">GOOGLE_SHEETS_ID</code>.
            </div>""", unsafe_allow_html=True)
    st.markdown("#### 🎯 Meta do Mês")
    ma=float(user.get("meta_atual") or 0);mt=float(user.get("meta_total") or 10000)
    pct=min(int((ma/mt)*100),100) if mt>0 else 0
    cor="#34d399" if pct>=80 else "#fbbf24" if pct>=50 else "#f87171"
    restante=max(mt-ma,0)
    msg="🔥 Excelente! Quase lá!" if pct>=80 else "💪 No caminho certo!" if pct>=50 else "🚀 Vamos acelerar!"
    st.markdown(f"""
    <div class="mc-grid">
      <div class="mc"><div class="mc-label">Vendido</div><div class="mc-value" style="color:{cor}">R$ {ma:,.2f}</div></div>
      <div class="mc"><div class="mc-label">Meta Total</div><div class="mc-value">R$ {mt:,.2f}</div></div>
      <div class="mc"><div class="mc-label">Falta</div><div class="mc-value" style="color:#fbbf24">R$ {restante:,.2f}</div></div>
    </div>
    <div class="prog-wrap">
      <div class="prog-head"><span>Progresso</span><strong>{pct}%</strong></div>
      <div class="prog-bg"><div class="prog-fill" style="width:{pct}%;background:{cor};box-shadow:0 0 10px {cor}55"></div></div>
      <div class="prog-msg">{msg}</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("#### 📢 Avisos")
    for av in db_get_avisos():
        ca="#4f8ef7" if av["tipo"]=="info" else "#fbbf24" if av["tipo"]=="warning" else "#f87171"
        st.markdown(f'<div class="av" style="border-left-color:{ca}"><div class="av-title">{av["titulo"]}</div><div class="av-body">{av["corpo"]}</div><div class="av-date">🕐 {av["criado_em"][:10]}</div></div>',unsafe_allow_html=True)

def render_ponto(user):
    clock_bar()
    st.markdown('<div class="ph"><h1>🕐 Registro de Ponto</h1><div class="ph-sub">Registre seus horários de trabalho</div></div>',unsafe_allow_html=True)
    hoje=date.today();ponto=db_get_ponto_hoje(user["id"])
    col_d,col_h=st.columns(2)
    with col_d:
        st.markdown(f'<div class="ponto-head"><span class="ponto-data">📅 {hoje.strftime("%d/%m/%Y")}</span></div>',unsafe_allow_html=True)
    with col_h:
        clock_ponto()
    st.markdown("#### Marcações de hoje")
    cards="<div class='pk-grid'>"
    for campo,label,_ in CAMPOS_PONTO:
        h=ponto.get(campo) if ponto else None
        cards+=f'<div class="pk {"done" if h else "pend"}"><div class="pk-lbl">{label}</div><div class="pk-time">{"✅ "+h if h else "—"}</div></div>'
    st.markdown(cards+"</div>",unsafe_allow_html=True)
    st.markdown("#### Registrar")
    c1,c2,c3=st.columns(3);cm=[c1,c2,c3,c1,c2,c3]
    for i,(campo,label,btn) in enumerate(CAMPOS_PONTO):
        h=ponto.get(campo) if ponto else None
        if not h:
            ok=True
            if i>0: ok=bool(ponto.get(CAMPOS_PONTO[i-1][0])) if ponto else False
            with cm[i]:
                if st.button(btn,key=f"ponto_{campo}",disabled=not ok):
                    hr=db_registrar_ponto(user["id"],campo);st.success(f"{label} às {hr}");st.rerun()
    st.markdown("<br>",unsafe_allow_html=True)
    with st.expander("📋 Histórico de ponto"):
        hist=db_historico_ponto(user["id"])
        if not hist: st.info("Nenhum registro.")
        for reg in hist:
            mc="  ".join(f"{ic} {h or '—'}" for ic,h in [("🟢",reg["entrada"]),("🍽️",reg["saida_almoco"]),("↩️",reg["retorno_almoco"]),("☕",reg["saida_cafe"]),("↩️",reg["retorno_cafe"]),("🔴",reg["saida"])])
            st.markdown(f'<div class="hist-row"><b>📅 {reg["data"]}</b><span style="font-family:var(--mono);font-size:.79rem">{mc}</span></div>',unsafe_allow_html=True)

def render_documentos(user):
    clock_bar()
    st.markdown('<div class="ph"><h1>📄 Envio de Documentos</h1><div class="ph-sub">Envie atestados e documentos para o RH</div></div>',unsafe_allow_html=True)
    st.markdown("#### 📤 Novo Documento")
    tipo=st.selectbox("Tipo de Documento",TIPOS_DOC,key="doc_tipo")
    descricao=st.text_area("Descrição (opcional)",placeholder="Ex: Atestado médico do dia 10/01...",key="doc_desc")
    arquivo=st.file_uploader("Selecione o arquivo",type=["pdf","jpg","jpeg","png","doc","docx"],key="doc_arq")
    c1,c2=st.columns(2)
    with c1:
        if st.button("💾 Salvar no Portal",key="btn_salvar"):
            if not arquivo: st.error("Selecione um arquivo.")
            else:
                pasta=f"docs_enviados/{user['id']}";os.makedirs(pasta,exist_ok=True)
                with open(f"{pasta}/{arquivo.name}","wb") as f: f.write(arquivo.getbuffer())
                db_salvar_doc(user["id"],tipo,descricao,arquivo.name);st.success("✅ Documento salvo!");st.rerun()
    with c2:
        st.markdown(f"""<a href="{WHATSAPP_LINK}" target="_blank" style="text-decoration:none;display:block;margin-top:.12rem">
        <button style="width:100%;background:#25d366;color:white;border:none;border-radius:12px;
            padding:.56rem .8rem;font-size:.88rem;font-weight:700;cursor:pointer;
            display:flex;align-items:center;justify-content:center;gap:7px;
            font-family:'Plus Jakarta Sans',sans-serif;box-shadow:0 3px 14px rgba(37,211,102,.28);">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="white">
        <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
        </svg>Enviar pelo WhatsApp</button></a>""", unsafe_allow_html=True)
    st.markdown('<div class="wpp-hint">💡 <strong>Como usar:</strong><br>1. Preencha e clique em <strong>Salvar no Portal</strong><br>2. Clique em <strong>Enviar pelo WhatsApp</strong> e anexe o arquivo no chat do RH</div>',unsafe_allow_html=True)
    st.markdown("#### 📋 Documentos Enviados")
    docs=db_get_docs(user["id"])
    if not docs: st.info("Nenhum documento enviado ainda.")
    for doc in docs:
        cs="#34d399" if doc["status"]=="aprovado" else "#fbbf24" if doc["status"]=="enviado" else "#f87171"
        ic="✅" if doc["status"]=="aprovado" else "⏳" if doc["status"]=="enviado" else "❌"
        st.markdown(f'<div class="doc-card"><div><span class="doc-tipo">📄 {doc["tipo"]}</span><span class="doc-arq">{doc["arquivo_nome"] or "—"}</span><span class="doc-desc">{doc["descricao"] or ""}</span></div><div style="text-align:right;flex-shrink:0;margin-left:1rem"><div class="doc-status" style="color:{cs}">{ic} {doc["status"].capitalize()}</div><div class="doc-date">🕐 {doc["criado_em"][:10]}</div></div></div>',unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# ROTEAMENTO PRINCIPAL
# ══════════════════════════════════════════════════════════════

# 1️⃣ Verifica horário
permitido, motivo, prox = verificar_horario()
if not permitido:
    render_bloqueio(motivo, prox)
    st.stop()

# 2️⃣ Login
if not st.session_state.logged_in:
    render_login()
    st.stop()

# 3️⃣ App autenticado
user = st.session_state.user

# Sidebar desktop
with st.sidebar:
    st.markdown(f"""
    <div class="sb-top">
      <div class="sb-avatar">{user['nome'][0].upper()}</div>
      <div class="sb-name">{user['nome']}</div>
      <div class="sb-role">{user['cargo']}</div>
    </div>""", unsafe_allow_html=True)
    clock_sidebar()
    PAGE_MAP     = {"dashboard":"🏠  Dashboard","ponto":"🕐  Ponto","docs":"📄  Documentos"}
    PAGE_MAP_REV = {v:k for k,v in PAGE_MAP.items()}
    cur = PAGE_MAP.get(st.session_state.page,"🏠  Dashboard")
    labels = list(PAGE_MAP.values())
    sel = st.radio("", labels, label_visibility="collapsed", key="nav",
                   index=labels.index(cur) if cur in labels else 0)
    st.session_state.page = PAGE_MAP_REV[sel]
    st.markdown("<br>"*5, unsafe_allow_html=True)
    st.markdown('<div class="btn-logout">', unsafe_allow_html=True)
    if st.button("Sair", key="logout"):
        st.session_state.logged_in=False; st.session_state.user=None; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Bottom nav mobile (botões Streamlit nativos — sem reload)
render_mobile_nav()

# Renderiza página
page = st.session_state.page
if page=="dashboard":   render_dashboard(user)
elif page=="ponto":     render_ponto(user)
elif page=="docs":      render_documentos(user)
