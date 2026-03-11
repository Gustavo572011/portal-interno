import streamlit as st
import hashlib
from database.db import get_user_by_email, get_user_by_google
import os

# Google OAuth (via streamlit-google-auth ou manual)
# Para produção, configure as variáveis de ambiente:
# GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def render_login():
    st.markdown("""
    <div class="login-bg">
        <div class="login-card">
            <div class="login-logo">
                <span class="logo-icon">🏢</span>
                <h1 class="logo-title">Portal Interno</h1>
                <p class="logo-sub">Acesse sua área de trabalho</p>
            </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📧  E-mail & Senha", "🔵  Google"])

    with tab1:
        st.markdown("<div class='form-group'>", unsafe_allow_html=True)
        email = st.text_input("E-mail", placeholder="seu@empresa.com", key="login_email")
        senha = st.text_input("Senha", type="password", placeholder="••••••••", key="login_senha")

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Entrar", use_container_width=True, type="primary", key="btn_login"):
                if not email or not senha:
                    st.error("Preencha e-mail e senha.")
                else:
                    user = get_user_by_email(email)
                    if user and user.get("senha") == hash_senha(senha):
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.success(f"Bem-vindo, {user['nome']}! 🎉")
                        st.rerun()
                    else:
                        st.error("E-mail ou senha incorretos.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown("""
        <div class='google-info'>
            <p>Para usar o login com Google, configure as credenciais OAuth 2.0 no arquivo <code>.env</code>:</p>
            <ul>
                <li><code>GOOGLE_CLIENT_ID</code></li>
                <li><code>GOOGLE_CLIENT_SECRET</code></li>
            </ul>
            <p>Depois instale: <code>pip install streamlit-google-auth</code></p>
        </div>
        """, unsafe_allow_html=True)

        # Exemplo de implementação com streamlit-google-auth
        try:
            from streamlit_google_auth import Authenticate
            client_id = os.getenv("GOOGLE_CLIENT_ID", "")
            client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")

            if client_id and client_secret:
                authenticator = Authenticate(
                    secret_credentials_path=None,
                    cookie_name="portal_interno",
                    cookie_key=os.getenv("SECRET_KEY", "minha_chave_secreta"),
                    redirect_uri=os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8501"),
                )
                authenticator.check_authentification()
                if st.session_state.get("connected"):
                    user_info = st.session_state.get("user_info", {})
                    user = get_user_by_google(
                        user_info.get("sub"),
                        user_info.get("email"),
                        user_info.get("name")
                    )
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.rerun()
                else:
                    authenticator.login()
            else:
                st.info("🔧 Configure as variáveis de ambiente para ativar o Google Login.")
        except ImportError:
            st.warning("📦 Instale `streamlit-google-auth` para ativar o login com Google.")

    st.markdown("</div></div>", unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div class="login-footer">
        <p>© 2025 Portal Interno — Desenvolvido com ❤️</p>
    </div>
    """, unsafe_allow_html=True)
