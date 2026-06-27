from docxtpl import DocxTemplate
import io

def generate_rep_word(template_path, context):
    try:
        doc = DocxTemplate(template_path)
        doc.render(context)
        
        doc.save('test_output.docx')
        print("Success")
    except Exception as e:
        print(f"Erro ao gerar: {e}")

context = {
    "numero_rep": "001",
    "data_atual": "02/06/2026",
    "remetente": "Cristovam",
    "cliente": "Inbrac",
    "obra": "Centro",
    "destinatarios": [
        {"nome": "FULANO", "empresa": "EMPRESA A"},
        {"nome": "BELTRANO", "empresa": "PRODUZ NUM SEI QUE"}
    ],
    "arquivos": []
}

generate_rep_word('template.docx', context)
