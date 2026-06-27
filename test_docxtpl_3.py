import docx
from docx import Document
from docxtpl import DocxTemplate

def main():
    doc = Document()
    table = doc.add_table(rows=1, cols=2)
    row = table.rows[0]
    row.cells[0].text = '{%tr for dest in destinatarios %}\n{{ dest.nome }}\n{%tr endfor %}'
    row.cells[1].text = '{{ dest.empresa }}'
    doc.save('test_in3.docx')

    tpl = DocxTemplate('test_in3.docx')
    context = {"destinatarios": [{"nome": "A", "empresa": "B"}]}
    try:
        tpl.render(context)
        tpl.save('test_out3.docx')
        print("SUCCESS 3")
    except Exception as e:
        print("FAILED 3:", e)

if __name__ == '__main__':
    main()
