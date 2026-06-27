from docx import Document

doc = Document("template.docx")
table5 = doc.tables[5]
print("Table 5 Style:", table5.style.name)
