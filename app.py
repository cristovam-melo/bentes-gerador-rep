import streamlit as st
import pandas as pd
from datetime import datetime
from pdf_extractor import extract_data_from_pdf
from word_generator import generate_rep_word
import os

st.set_page_config(page_title="Gerador REP - Bentes", layout="wide")

# Inicializar o estado de sessão para acumular os arquivos carregados
if "arquivos_acumulados" not in st.session_state:
    st.session_state.arquivos_acumulados = []
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

st.title("Gerador de Registro de Envio de Projetos (REP)")
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
# Tabela de destinatários
default_destinatarios = pd.DataFrame(
    [
        {"nome": "", "empresa": ""},
        {"nome": "", "empresa": ""}
    ]
)

# Usa o editor de dados do Streamlit, permitindo adicionar linhas
edited_destinatarios = st.data_editor(
    default_destinatarios,
    num_rows="dynamic",
    column_config={
        "nome": st.column_config.TextColumn("Nome / Destinatário", required=True),
        "empresa": st.column_config.TextColumn("Empresa")
    },
    hide_index=True
)

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
st.markdown("""
<style>
button[aria-label="Limpar Seleção"] {
    background-color: #f5f5f5 !important;
    color: #5f6368 !important;
    border: 1px solid #dadce0 !important;
    transition: background-color 0.2s, color 0.2s !important;
}
button[aria-label="Limpar Seleção"]:hover {
    background-color: #faeedb !important;
    color: #b06000 !important;
    border: 1px solid #ff9800 !important;
}
button[aria-label="Fazer Outro Upload"] {
    background-color: #e8f0fe !important;
    color: #1a73e8 !important;
    border: 1px solid #d2e3fc !important;
    transition: background-color 0.2s, color 0.2s !important;
}
button[aria-label="Fazer Outro Upload"]:hover {
    background-color: #1a73e8 !important;
    color: white !important;
    border: 1px solid #1a73e8 !important;
}
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
            # Processar destinatários (remover linhas vazias e lidar com NaNs)
            destinatarios = []
            for _, row in edited_destinatarios.iterrows():
                nome_val = str(row['nome']).strip() if pd.notna(row['nome']) else ""
                emp_val = str(row['empresa']).strip() if pd.notna(row['empresa']) else ""
                if nome_val and nome_val.lower() != "nan":
                    destinatarios.append({"nome": nome_val, "empresa": emp_val})
                    
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
