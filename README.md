# 🏢 Portal Interno — Streamlit

Sistema interno para gestão de equipe com dashboard, ponto eletrônico e envio de documentos.

## 📁 Estrutura do Projeto

```
portal-interno/
├── app.py                  # Ponto de entrada principal
├── requirements.txt        # Dependências
├── .env.example            # Template de variáveis de ambiente
├── .env                    # Suas variáveis (não versionar!)
├── .gitignore
│
├── assets/
│   └── style.css           # Design system completo
│
├── auth/
│   └── login.py            # Tela de login (email + Google)
│
├── database/
│   └── db.py               # SQLite — todas as queries
│
├── pages/
│   ├── dashboard.py        # Metas e avisos
│   ├── ponto.py            # Registro de ponto
│   └── documentos.py       # Envio de documentos
│
└── data/                   # Criado automaticamente
    ├── portal.db           # Banco de dados SQLite
    └── documentos/         # Arquivos enviados
```

## 🚀 Como Rodar

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/portal-interno.git
cd portal-interno
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Configure o ambiente
```bash
cp .env.example .env
# Edite o .env com suas credenciais
```

### 4. Rode o app
```bash
streamlit run app.py
```

Acesse: http://localhost:8501

---

## 🔐 Usuários de Teste

| E-mail | Senha | Cargo |
|--------|-------|-------|
| admin@empresa.com | admin123 | Gerente |
| joao@empresa.com | 123456 | Vendedor |

---

## ⚙️ Configurações Opcionais

### Login com Google OAuth
1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um projeto → APIs & Services → Credentials
3. OAuth 2.0 Client ID → Web Application
4. Redirect URI: `http://localhost:8501`
5. Copie Client ID e Secret para o `.env`

### WhatsApp Business API
1. Acesse [Meta for Developers](https://developers.facebook.com/)
2. Crie um App → WhatsApp → Cloud API
3. Configure número de teste
4. Copie Token e Phone Number ID para o `.env`
5. Define `WHATSAPP_DEST_NUMBER` com o número do RH

---

## 🌐 Deploy no Streamlit Cloud (com GitHub)

1. Faça push para o GitHub
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Conecte o repositório
4. Em **Advanced Settings → Secrets**, adicione as variáveis do `.env`
5. Deploy! ✅

### .gitignore recomendado
```
.env
data/
__pycache__/
*.pyc
.DS_Store
```

---

## 📦 Funcionalidades

- ✅ Login com e-mail e senha
- ✅ Login com Google OAuth
- ✅ Dashboard com metas de vendas e barra de progresso
- ✅ Avisos da empresa
- ✅ Registro de ponto (entrada, almoço, café, saída)
- ✅ Histórico de ponto
- ✅ Envio de documentos (PDF, imagem, Word)
- ✅ Notificação WhatsApp Business API para o RH
- ✅ Histórico de documentos enviados
- ✅ Interface dark premium responsiva
