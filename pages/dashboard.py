import streamlit as st
from database.db import get_avisos
from datetime import date

def render_dashboard(user):
    st.markdown(f"""
    <div class="page-header">
        <h1>Bom dia, {user['nome'].split()[0]}! 👋</h1>
        <p class="page-date">{date.today().strftime('%A, %d de %B de %Y')}</p>
    </div>
    """, unsafe_allow_html=True)

    # ─── Metas ─────────────────────────────────────────────────
    st.markdown("### 🎯 Sua Meta do Mês")

    meta_atual = user.get("meta_atual", 0)
    meta_total = user.get("meta_total", 10000)
    pct = min(int((meta_atual / meta_total) * 100), 100) if meta_total > 0 else 0

    cor = "#22c55e" if pct >= 80 else "#f59e0b" if pct >= 50 else "#ef4444"

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Vendido até agora</div>
            <div class="metric-value" style="color:{cor}">R$ {meta_atual:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Meta total</div>
            <div class="metric-value">R$ {meta_total:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        restante = meta_total - meta_atual
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Falta para a meta</div>
            <div class="metric-value" style="color:#f59e0b">R$ {max(restante,0):,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    # Barra de progresso customizada
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-header">
            <span>Progresso</span>
            <span><strong>{pct}%</strong></span>
        </div>
        <div class="progress-bar-bg">
            <div class="progress-bar-fill" style="width:{pct}%; background:{cor}"></div>
        </div>
        <div class="progress-label">
            {'🔥 Excelente! Você está quase lá!' if pct >= 80 else '💪 Você está no caminho certo!' if pct >= 50 else '🚀 Vamos acelerar!'}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ─── Avisos ────────────────────────────────────────────────
    st.markdown("### 📢 Avisos da Empresa")

    avisos = get_avisos()
    if not avisos:
        st.info("Nenhum aviso no momento.")
    else:
        for aviso in avisos:
            tipo = aviso.get("tipo", "info")
            icone = "📌" if tipo == "info" else "⚠️" if tipo == "warning" else "🔴"
            cor_aviso = "#3b82f6" if tipo == "info" else "#f59e0b" if tipo == "warning" else "#ef4444"
            st.markdown(f"""
            <div class="aviso-card" style="border-left: 4px solid {cor_aviso}">
                <div class="aviso-titulo">{icone} {aviso['titulo']}</div>
                <div class="aviso-corpo">{aviso['corpo']}</div>
                <div class="aviso-data">🕐 {aviso['criado_em'][:10]}</div>
            </div>
            """, unsafe_allow_html=True)
