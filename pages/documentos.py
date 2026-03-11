import streamlit as st
from database.db import salvar_documento, get_documentos_usuario
import os
import requests

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID", "")
WHATSAPP_DEST = os.getenv("WHATSAPP_DEST_NUMBER", "")  # Número do RH ex: 5511999999999

TIPOS_DOC = [
    "Atestado Médico",
    "Declaração",
    "Comprovante de Endereço",
    "Documento Pessoal (RG/CPF)",
    "Comprovante de Escolaridade",
    "Contrato",
    "Outros",
]

def enviar_whatsapp_notificacao(nome_funcionario, tipo_doc, descricao, numero_destino):
    """Envia notificação via WhatsApp Business API Cloud."""
    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_ID:
        return False, "Token ou Phone ID não configurado."

    url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    body = {
        "messaging_product": "whatsapp",
        "to": numero_destino,
        "type": "text",
        "text": {
            "body": (
                f"📄 *Novo Documento Enviado*\n\n"
                f"👤 *Funcionário:* {nome_funcionario}\n"
                f"📋 *Tipo:* {tipo_doc}\n"
                f"📝 *Descrição:* {descricao or 'Sem descrição'}\n\n"
                f"Acesse o portal para visualizar o arquivo."
            )
        }
    }
    try:
        resp = requests.post(url, headers=headers, json=body, timeout=10)
        if resp.status_code == 200:
            return True, "Notificação enviada com sucesso!"
        else:
            return False, f"Erro API: {resp.text}"
    except Exception as e:
        return False, str(e)

def render_documentos(user):
    st.markdown("""
    <div class="page-header">
        <h1>📄 Envio de Documentos</h1>
    </div>
    """, unsafe_allow_html=True)

    # ─── Formulário de envio ───────────────────────────────────
    st.markdown("### 📤 Enviar Novo Documento")

    with st.container():
        st.markdown("<div class='doc-form'>", unsafe_allow_html=True)

        tipo = st.selectbox("Tipo de Documento", TIPOS_DOC, key="doc_tipo")
        descricao = st.text_area("Descrição (opcional)", placeholder="Ex: Atestado do dia 10/01 por gripe...", key="doc_desc")
        arquivo = st.file_uploader(
            "Selecione o arquivo",
            type=["pdf", "jpg", "jpeg", "png", "doc", "docx"],
            key="doc_arquivo"
        )

        if st.button("📤 Enviar Documento", type="primary", use_container_width=True, key="btn_enviar_doc"):
            if not arquivo:
                st.error("Selecione um arquivo para enviar.")
            else:
                # Salva arquivo localmente
                pasta = f"data/documentos/{user['id']}"
                os.makedirs(pasta, exist_ok=True)
                caminho = f"{pasta}/{arquivo.name}"
                with open(caminho, "wb") as f:
                    f.write(arquivo.getbuffer())

                # Salva no banco
                salvar_documento(user["id"], tipo, descricao, arquivo.name)

                # Envia notificação WhatsApp
                if WHATSAPP_TOKEN and WHATSAPP_DEST:
                    ok, msg = enviar_whatsapp_notificacao(
                        user["nome"], tipo, descricao, WHATSAPP_DEST
                    )
                    if ok:
                        st.success(f"✅ Documento enviado e RH notificado via WhatsApp!")
                    else:
                        st.warning(f"✅ Documento salvo! (WhatsApp: {msg})")
                else:
                    st.success("✅ Documento enviado com sucesso!")
                    st.info("💡 Configure `WHATSAPP_TOKEN`, `WHATSAPP_PHONE_ID` e `WHATSAPP_DEST_NUMBER` no `.env` para ativar notificações.")

                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # Configuração WhatsApp (aviso se não configurado)
    if not WHATSAPP_TOKEN:
        with st.expander("⚙️ Como configurar o WhatsApp Business API"):
            st.markdown("""
            1. Acesse [Meta for Developers](https://developers.facebook.com/)
            2. Crie um app > WhatsApp > Cloud API
            3. Copie o **Token de Acesso** e o **Phone Number ID**
            4. Crie o arquivo `.env` na raiz do projeto:
            ```
            WHATSAPP_TOKEN=seu_token_aqui
            WHATSAPP_PHONE_ID=seu_phone_id
            WHATSAPP_DEST_NUMBER=5511999999999
            ```
            5. Reinicie o Streamlit
            """)

    st.markdown("<br>", unsafe_allow_html=True)

    # ─── Histórico de documentos ───────────────────────────────
    st.markdown("### 📋 Meus Documentos Enviados")

    docs = get_documentos_usuario(user["id"])
    if not docs:
        st.info("Nenhum documento enviado ainda.")
    else:
        for doc in docs:
            status_cor = "#22c55e" if doc["status"] == "aprovado" else "#f59e0b" if doc["status"] == "enviado" else "#ef4444"
            status_emoji = "✅" if doc["status"] == "aprovado" else "⏳" if doc["status"] == "enviado" else "❌"
            st.markdown(f"""
            <div class="doc-card">
                <div class="doc-info">
                    <span class="doc-tipo">📄 {doc['tipo']}</span>
                    <span class="doc-nome">{doc['arquivo_nome']}</span>
                    <span class="doc-desc">{doc['descricao'] or ''}</span>
                </div>
                <div class="doc-meta">
                    <span class="doc-status" style="color:{status_cor}">{status_emoji} {doc['status'].capitalize()}</span>
                    <span class="doc-data">🕐 {doc['criado_em'][:10]}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
