import sqlite3
from datetime import datetime, date
import hashlib
import os

# ─── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Portal Interno",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS Global ────────────────────────────────────────────────
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ─── Database ──────────────────────────────────────────────────
from database.db import init_db
init_db()

# ─── Auth ──────────────────────────────────────────────────────
from auth.login import render_login
from pages.dashboard import render_dashboard
from pages.ponto import render_ponto
from pages.documentos import render_documentos

# ─── Session State ─────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None

# ─── Routing ───────────────────────────────────────────────────
if not st.session_state.logged_in:
    render_login()
else:
    user = st.session_state.user

    # Sidebar
    with st.sidebar:
        st.markdown(f"""
        <div class="sidebar-profile">
            <div class="avatar">{user['nome'][0].upper()}</div>
            <div class="user-name">{user['nome']}</div>
            <div class="user-role">{user['cargo']}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='sidebar-nav'>", unsafe_allow_html=True)
        page = st.radio(
            "",
            ["🏠  Dashboard", "🕐  Ponto", "📄  Documentos"],
            label_visibility="collapsed"
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='sidebar-footer'>", unsafe_allow_html=True)
        if st.button("Sair", key="logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # Pages
    if "Dashboard" in page:
        render_dashboard(user)
    elif "Ponto" in page:
        render_ponto(user)
    elif "Documentos" in page:
        render_documentos(user)
