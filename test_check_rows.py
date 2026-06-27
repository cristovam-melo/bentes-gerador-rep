import docx
doc = docx.Document('test_out5.docx')
print("Rows in out.docx:", len(doc.tables[0].rows))
