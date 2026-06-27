from docx import Document

doc = Document("template.docx")
table5 = doc.tables[5]
print(table5._tbl.tblPr.xml)
