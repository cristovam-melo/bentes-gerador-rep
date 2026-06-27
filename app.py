import streamlit as st
import pandas as pd
from datetime import datetime
from pdf_extractor import extract_data_from_pdf
from word_generator import generate_rep_word
import os

st.set_page_config(page_title="Gerador REP - Bentes", layout="wide")

st.sidebar.title("Configurações")
tema_escuro = st.sidebar.toggle("Tema Escuro", value=True)

if tema_escuro:
    bg_color = "#0e1117"
    text_color = "rgb(23, 154, 73)"
    input_text_color = "#808495"
    input_bg = "rgba(23, 154, 73, 0.05)"
    input_border = "rgba(23, 154, 73, 0.3)"
    btn_primary_bg = "rgb(23, 154, 73)"
    btn_primary_text = "white"
else:
    bg_color = "#ffffff"
    text_color = "#000000"
    input_text_color = "#000000"
    input_bg = "#f9f9f9"
    input_border = "#cccccc"
    btn_primary_bg = "rgb(23, 154, 73)"
    btn_primary_text = "white"


# Inicializar o estado de sessão para acumular os arquivos carregados
if "arquivos_acumulados" not in st.session_state:
    st.session_state.arquivos_acumulados = []
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0
if "num_destinatarios" not in st.session_state:
    st.session_state.num_destinatarios = 1

import os
import base64

if os.path.exists("logo.png"):
    with open("logo.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px;">
            <img src="data:image/png;base64,{encoded_string}" style="width: 350px; border-radius: 0px;">
            <h1 style="margin: 0; padding: 0; font-size: 2.2rem;">Relatório de Envio de Projeto (REP)</h1>
        </div>
        """, 
        unsafe_allow_html=True
    )
else:
    st.title("Relatório de Envio de Projeto (REP)")
st.subheader("Preencha as informações e faça upload das plantas (PDFs)")

# Form layout
col1, col2, col3 = st.columns(3)

with col1:
    numero_rep = st.text_input("Número REP", value="001", help="Número sequencial. Edite se necessário.")
    data_atual = st.text_input("Data do Documento", value=datetime.today().strftime("%d/%m/%Y"))

with col2:
    remetente = st.text_input("De (Remetente)", placeholder="Ex: Maurício Sant'Anna")
    cliente = st.text_input("Cliente", placeholder="Ex: Inbrac")

with col3:
    obra = st.text_input("Obra", placeholder="Ex: Centro de Eventos Cuiabá")

st.markdown("---")
st.subheader("Destinatários")

destinatarios_list = []
for i in range(st.session_state.num_destinatarios):
    c1, c2 = st.columns(2)
    with c1:
        n = st.text_input(f"Nome / Destinatário {i+1}", key=f"dest_nome_{i}", placeholder="Ex: João Silva")
    with c2:
        e = st.text_input(f"Empresa {i+1}", key=f"dest_emp_{i}", placeholder="Ex: Construtora Alfa")
    
    if n.strip():
        destinatarios_list.append({"nome": n.strip(), "empresa": e.strip()})

if st.button("➕ Adicionar outro destinatário", key="add_dest", type="secondary"):
    st.session_state.num_destinatarios += 1
    st.rerun()

st.markdown("---")
st.subheader("Plantas / Projetos (Upload de PDFs)")

# File uploader com chave dinâmica baseada no estado de sessão para permitir limpeza
uploaded_files = st.file_uploader(
    "Selecione as plantas em formato PDF", 
    type=['pdf'], 
    accept_multiple_files=True,
    key=f"uploader_{st.session_state.uploader_key}"
)

# Se arquivos novos foram selecionados, processa e acumula em session_state
if uploaded_files:
    for pdf_file in uploaded_files:
        # Evita duplicados na lista de acumulados
        if not any(item["arquivo"] == pdf_file.name for item in st.session_state.arquivos_acumulados):
            dados = extract_data_from_pdf(pdf_file, pdf_file.name)
            if dados:
                st.session_state.arquivos_acumulados.append(dados)

# Mostra a lista dos arquivos atualmente acumulados em uma tabela estilizada
if st.session_state.arquivos_acumulados:
    st.markdown(f"**Arquivos adicionados ({len(st.session_state.arquivos_acumulados)}):**")
    df_files = pd.DataFrame([
        {
            "Arquivo": item["arquivo"], 
            "Nº Folha": item["numero_folha"], 
            "Descrição Folha": item["descricao"], 
            "Data Folha": item["data_folha"]
        } for item in st.session_state.arquivos_acumulados
    ])
    st.dataframe(df_files, use_container_width=True, hide_index=True)

# Grid de botões: Gerar Relatório, Limpar Seleção, Fazer Outro Upload
# Ajustado para 3 colunas de igual tamanho (1:1:1) para alinhar perfeitamente com os campos acima
st.markdown(f"""
<style>
    /* Base Background */
    .stApp {{
        background-color: {bg_color} !important;
    }}
    
    /* Global Text Color */
    h1, h2, h3, p, span, div, label, .stMarkdown, .stText {{
        color: {text_color} !important;
    }}

    /* Inputs & data editor panels */
    .stTextInput>div>div>input {{
        background-color: {input_bg} !important;
        border: 1px solid {input_border} !important;
        border-radius: 8px !important;
        color: {input_text_color} !important;
        box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }}
    .stTextInput>div>div>input:focus {{
        border-color: {btn_primary_bg} !important;
        box-shadow: 0 0 0 1px {btn_primary_bg} !important;
    }}
    
    /* Upload Box */
    .stFileUploader>div>div>div>div>div {{
        border: 2px dashed {input_border} !important;
        border-radius: 12px !important;
        background-color: {input_bg} !important;
        transition: all 0.3s ease;
    }}
    .stFileUploader>div>div>div>div>div:hover {{
        border-color: {btn_primary_bg} !important;
    }}

    /* Primary Button (Gerar Relatório) */
    button[kind="primary"] {{
        background: {btn_primary_bg} !important;
        color: {btn_primary_text} !important;
        border: none !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }}
    button[kind="primary"]:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(23, 154, 73, 0.4) !important;
    }}
    
    /* ALL Buttons Typography */
    div[data-testid="stButton"] button p {{
        text-transform: uppercase !important;
        font-weight: bold !important;
        letter-spacing: 1px !important;
    }}
    
    /* Secondary Buttons Styling */
    button[kind="secondary"] {{
        background-color: transparent !important;
        border: 1px solid {input_border} !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }}
    button[kind="secondary"]:hover {{
        background-color: {input_bg} !important;
        transform: translateY(-1px);
    }}
    
    /* DataFrame */
    .stDataFrame {{
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid {input_border};
    }}
    
    /* Placeholder-like color for DataFrame */
    [data-testid="stDataFrame"] div, [data-testid="stDataFrame"] span {{
        color: #808495 !important;
    }}
</style>
""", unsafe_allow_html=True)

col_btn1, col_btn2, col_btn3 = st.columns(3)

with col_btn1:
    btn_generate = st.button("Gerar Relatório (Word)", type="primary", use_container_width=True)

with col_btn2:
    btn_clear = st.button("Limpar Seleção", use_container_width=True)

with col_btn3:
    btn_more = st.button("Fazer Outro Upload", use_container_width=True)

# Ação do botão de Limpar
if btn_clear:
    st.session_state.arquivos_acumulados = []
    st.session_state.uploader_key += 1
    st.rerun()

# Ação do botão de Fazer Outro Upload (reinicia o uploader na tela para liberar o botão principal)
if btn_more:
    st.session_state.uploader_key += 1
    st.rerun()

if btn_generate:
    if not remetente or not obra:
        st.warning("Preencha os campos 'De (Remetente)' e 'Obra'.")
    elif not st.session_state.arquivos_acumulados:
        st.warning("Faça o upload de pelo menos um arquivo PDF.")
    else:
        with st.spinner("Processando PDFs e gerando documento..."):
            # Os destinatários já foram coletados nos inputs dinâmicos
            destinatarios = destinatarios_list
                    
            # Contexto para o template
            context = {
                "numero_rep": numero_rep,
                "data_atual": data_atual,
                "remetente": remetente,
                "cliente": cliente,
                "obra": obra,
                "destinatarios": destinatarios,
                "arquivos": st.session_state.arquivos_acumulados
            }
            
            # Gerar Word
            template_path = os.path.join(os.path.dirname(__file__), "template.docx")
            if not os.path.exists(template_path):
                st.error("Erro: Arquivo 'template.docx' não encontrado. Por favor, certifique-se de que o script auxiliar gerou o template.")
            else:
                docx_buffer = generate_rep_word(template_path, context)
                
                if docx_buffer:
                    st.success("Relatório gerado com sucesso!")
                    
                    import unicodedata
                    clean_obra = unicodedata.normalize('NFKD', obra).encode('ascii', 'ignore').decode('ascii')
                    file_name_out = f"REP_{numero_rep}_{clean_obra}.docx".replace(" ", "_")
                    
                    st.download_button(
                        label="⬇️ Baixar Arquivo Word (.docx)",
                        data=docx_buffer,
                        file_name=file_name_out,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                else:
                    st.error("Falha ao gerar o documento Word.")
