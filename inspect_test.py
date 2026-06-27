from docx import Document
try:
    doc = Document("test_output2.docx")
    for table in doc.tables:
        for row in table.rows:
            row_text = []
            for cell in row.cells:
                row_text.append(cell.text.replace('\n', ' '))
            print(" | ".join(row_text))
except Exception as e:
    print("Error:", e)
