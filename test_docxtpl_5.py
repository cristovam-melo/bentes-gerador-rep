import docx
from docx import Document
from docxtpl import DocxTemplate

def main():
    doc = Document()
    table = doc.add_table(rows=3, cols=2)
    table.rows[0].cells[0].text = '{%tr for dest in destinatarios %}'
    table.rows[1].cells[0].text = '{{ dest.nome }}'
    table.rows[1].cells[1].text = '{{ dest.empresa }}'
    table.rows[2].cells[0].text = '{%tr endfor %}'
    doc.save('test_in5.docx')

    tpl = DocxTemplate('test_in5.docx')
    context = {"destinatarios": [{"nome": "A", "empresa": "B"}]}
    try:
        tpl.render(context)
        tpl.save('test_out5.docx')
        print("SUCCESS 5")
    except Exception as e:
        print("FAILED 5:", e)

if __name__ == '__main__':
    main()
