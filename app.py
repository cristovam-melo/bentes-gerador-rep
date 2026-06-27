import streamlit as st
import pandas as pd
from datetime import datetime
from pdf_extractor import extract_data_from_pdf
from word_generator import generate_rep_word
import os

st.set_page_config(page_title="Gerador REP - Bentes", layout="wide")

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
uploaded_files = st.file_uploader("Selecione as plantas em formato PDF", type=['pdf'], accept_multiple_files=True)

if st.button("Gerar Relatório (Word)", type="primary"):
    if not remetente or not obra:
        st.warning("Preencha os campos 'De (Remetente)' e 'Obra'.")
    elif not uploaded_files:
        st.warning("Faça o upload de pelo menos um arquivo PDF.")
    else:
        with st.spinner("Processando PDFs e gerando documento..."):
            
            # Processar PDFs
            arquivos_extraidos = []
            for pdf_file in uploaded_files:
                dados = extract_data_from_pdf(pdf_file, pdf_file.name)
                if dados:
                    arquivos_extraidos.append(dados)
            
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
                "arquivos": arquivos_extraidos
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
