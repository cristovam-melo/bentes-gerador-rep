import docx
from docx import Document
from docx.oxml.ns import qn

doc = Document('template.docx')
for table in doc.tables:
    tbl = table._tbl
    for w in tbl.xpath('.//w:tblW'):
        w.set(qn('w:type'), 'pct')
        w.set(qn('w:w'), '5000')

doc.save('template_100pct.docx')
