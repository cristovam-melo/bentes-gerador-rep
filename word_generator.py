from docxtpl import DocxTemplate
import io

def generate_rep_word(template_path, context):
    """
    Gera o documento Word preenchido.
    
    template_path: caminho para o template.docx
    context: dicionário com os dados. Ex:
        {
            "numero_rep": "001",
            "data_atual": "29/05/2026",
            "remetente": "Maurício Sant'Anna",
            "cliente": "Inbrac",
            "obra": "Centro de Eventos Cuiabá",
            "destinatarios": [
                {"nome": "Gabriel Carbonera", "empresa": "Inbrac"},
                {"nome": "Wilton Andrade", "empresa": "OCC PARTICIPAÇÕES"}
            ],
            "arquivos": [
                {
                    "arquivo": "F217-CEC-PVS5-V106-R0.pdf",
                    "numero_folha": "F217",
                    "descricao": "PAVILHÃO DE SERVIÇOS 5 - V106 - FORMA E ARMAÇÃO (1x)",
                    "data_folha": "28/05/2026"
                }
            ]
        }
    """
    try:
        doc = DocxTemplate(template_path)
        doc.render(context)
        
        # Salva em memória para o Streamlit fazer download sem precisar salvar no disco
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer
    except Exception as e:
        print(f"Erro ao gerar documento Word: {e}")
        return None
