import streamlit as st
from datetime import datetime
import time

# Configuração da página
st.set_page_config(page_title="Portal COMSTRUKASA", page_icon="🏗️", layout="centered")

# Estilização Customizada (CSS para animações e botões)
st.markdown("""
    <style>
    .main { opacity: 0; animation: fadeIn 1.5s forwards; }
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    .stButton>button { width: 100%; border-radius: 20px; transition: 0.3s; }
    .stButton>button:hover { transform: scale(1.02); }
    </style>
""", unsafe_allow_html=True)

# Banco de dados simulado
users = {
    "stein25": {"nome": "Karen", "tipo": "adm", "cargo": "Gerente", "salario": "R$ 5.500", "meta": "N/A"},
    "soares": {"nome": "Valdinei", "tipo": "adm", "cargo": "Supervisor de Pátio", "salario": "R$ 4.200", "meta": "N/A"},
    "572011": {"nome": "Gustavo", "tipo": "adm", "cargo": "Assist. Administrativo", "salario": "R$ 2.800", "meta": "N/A"},
    "maria1819": {"nome": "Sueli", "tipo": "user", "cargo": "Vendedora", "salario": "R$ 2.500", "meta": "R$ 50.000"},
    "camila": {"nome": "Leiliane", "tipo": "user", "cargo": "Vendedora", "salario": "R$ 2.500", "meta": "R$ 50.000"},
    "riquele24": {"nome": "Riquele", "tipo": "user", "cargo": "Zeladora", "salario": "R$ 1.800", "meta": "N/A"},
    "wagner007": {"nome": "Wagner", "tipo": "user", "cargo": "Assist. Administrativo", "salario": "R$ 2.500", "meta": "N/A"},
    "99551264": {"nome": "Agnaldo", "tipo": "user", "cargo": "Aux. de Produção", "salario": "R$ 2.100", "meta": "N/A"},
    "290580": {"nome": "Rogério", "tipo": "user", "cargo": "Motorista", "salario": "R$ 2.600", "meta": "N/A"},
    "sophia2710": {"nome": "Samuel", "tipo": "user", "cargo": "Serrador", "salario": "R$ 2.300", "meta": "N/A"},
}

def verificar_horario():
    agora = datetime.now()
    dia_semana = agora.weekday() # 0=Segunda, 5=Sábado, 6=Domingo
    hora_atual = agora.time()
    
    inicio = datetime.strptime("07:45", "%H:%M").time()
    fim_semana = datetime.strptime("19:00", "%H:%M").time()
    fim_sabado = datetime.strptime("13:00", "%H:%M").time()

    if dia_semana < 5: # Seg a Sex
        return inicio <= hora_atual <= fim_semana
    elif dia_semana == 5: # Sábado
        return inicio <= hora_atual <= fim_sabado
    return False

# Lógica de Login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_data = None

def login():
    st.image("https://cdn-icons-png.flaticon.com/512/4090/4090434.png", width=100)
    st.title("COMSTRUKASA")
    st.subheader("Madeireira e Materiais para Construção")
    
    usuario = st.text_input("Usuário (Senha)")
    if st.button("Entrar"):
        if usuario in users:
            user_info = users[usuario]
            dentro_horario = verificar_horario()
            
            if user_info['tipo'] == 'adm' or dentro_horario:
                st.session_state.logged_in = True
                st.session_state.user_data = user_info
                st.success(f"Bem-vindo(a), {user_info['nome']}!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Portal fechado. Horário de acesso: Seg-Sex (07:45-19:00) e Sáb (07:45-13:00).")
        else:
            st.error("Usuário não encontrado.")

def portal_funcionario():
    user = st.session_state.user_data
    st.title(f"Olá, {user['nome']} 👋")
    st.info(f"**Cargo:** {user['cargo']} | **Acesso:** {user['tipo'].upper()}")

    # Abas do Portal
    tab1, tab2, tab3 = st.tabs(["📊 Meus Dados", "🕒 Ponto Digital", "🛠️ Administração" if user['tipo'] == 'adm' else "📞 Suporte"])

    with tab1:
        col1, col2 = st.columns(2)
        col1.metric("Salário Base", user['salario'])
        if user['cargo'] == "Vendedora":
            col2.metric("Meta Mensal", user['meta'])
        else:
            col2.write("**Informação:** Metas aplicadas apenas ao setor comercial.")

    with tab2:
        st.write("### Registro de Ponto")
        st.write(f"Horário atual: {datetime.now().strftime('%H:%M:%S')}")
        if st.button("Registrar Entrada/Saída"):
            st.toast("Ponto registrado com sucesso!", icon="✅")

    with tab3:
        if user['tipo'] == 'adm':
            st.write("### Painel Geral (Acesso Restrito)")
            st.table(users)
        else:
            st.write("### Precisa de ajuda?")
            link_whatsapp = "https://wa.me/5541999013074?text=Olá,%20preciso%20de%20suporte%20no%20portal%20COMSTRUKASA"
            st.markdown(f'''
                <a href="{link_whatsapp}" target="_blank">
                    <button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 10px; cursor: pointer; width: 100%;">
                        Falar com Suporte no WhatsApp
                    </button>
                </a>
            ''', unsafe_allow_html=True)

    if st.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()

# Controle de Navegação
if not st.session_state.logged_in:
    login()
else:
    portal_funcionario()
