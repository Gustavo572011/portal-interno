import streamlit as st
from database.db import get_ponto_hoje, registrar_ponto, get_historico_ponto
from datetime import datetime, date

CAMPOS = [
    ("entrada",         "🟢 Entrada",          "Registrar Entrada"),
    ("saida_almoco",    "🍽️ Saída Almoço",      "Registrar Saída Almoço"),
    ("retorno_almoco",  "↩️ Retorno Almoço",    "Registrar Retorno"),
    ("saida_cafe",      "☕ Saída Café",         "Registrar Saída Café"),
    ("retorno_cafe",    "↩️ Retorno Café",       "Registrar Retorno Café"),
    ("saida",           "🔴 Saída",              "Registrar Saída"),
]

def render_ponto(user):
    st.markdown("""
    <div class="page-header">
        <h1>🕐 Registro de Ponto</h1>
    </div>
    """, unsafe_allow_html=True)

    hoje = date.today()
    agora = datetime.now().strftime("%H:%M:%S")
    ponto = get_ponto_hoje(user["id"])

    st.markdown(f"""
    <div class="ponto-header">
        <div class="ponto-data">📅 {hoje.strftime('%d/%m/%Y')}</div>
        <div class="ponto-hora">🕐 {agora}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Marcações de Hoje")

    cols = st.columns(3)
    for i, (campo, label, btn_label) in enumerate(CAMPOS):
        col = cols[i % 3]
        horario = ponto.get(campo) if ponto else None
        with col:
            if horario:
                st.markdown(f"""
                <div class="ponto-card done">
                    <div class="ponto-card-label">{label}</div>
                    <div class="ponto-card-time">✅ {horario}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="ponto-card pending">
                    <div class="ponto-card-label">{label}</div>
                    <div class="ponto-card-time">—</div>
                </div>
                """, unsafe_allow_html=True)
                # Lógica de ordem: só libera se anterior foi marcado
                idx = [c[0] for c in CAMPOS].index(campo)
                anterior_ok = True
                if idx > 0:
                    campo_anterior = CAMPOS[idx - 1][0]
                    anterior_ok = bool(ponto.get(campo_anterior)) if ponto else False

                if anterior_ok or idx == 0:
                    if st.button(btn_label, key=f"btn_{campo}", use_container_width=True):
                        horario_reg = registrar_ponto(user["id"], campo)
                        st.success(f"{label} registrada às {horario_reg}!")
                        st.rerun()
                else:
                    st.button(btn_label, key=f"btn_{campo}", disabled=True, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ─── Histórico ─────────────────────────────────────────────
    with st.expander("📋 Ver Histórico de Ponto"):
        historico = get_historico_ponto(user["id"])
        if not historico:
            st.info("Nenhum registro encontrado.")
        else:
            for reg in historico:
                st.markdown(f"""
                <div class="historico-row">
                    <strong>📅 {reg['data']}</strong>
                    <span>🟢 {reg['entrada'] or '—'}</span>
                    <span>🍽️ {reg['saida_almoco'] or '—'}</span>
                    <span>↩️ {reg['retorno_almoco'] or '—'}</span>
                    <span>☕ {reg['saida_cafe'] or '—'}</span>
                    <span>↩️ {reg['retorno_cafe'] or '—'}</span>
                    <span>🔴 {reg['saida'] or '—'}</span>
                </div>
                """, unsafe_allow_html=True)
