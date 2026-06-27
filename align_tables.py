from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

doc = Document("template.docx")

for table in doc.tables:
    table.autofit = True
    tbl = table._tbl
    tblPr = tbl.tblPr
    tblW = tblPr.xpath("w:tblW")
    if tblW:
        tblW = tblW[0]
    else:
        tblW = OxmlElement("w:tblW")
        tblPr.append(tblW)
    
    tblW.set(qn("w:w"), "5000")
    tblW.set(qn("w:type"), "pct")

doc.save("template.docx")
print("Tables aligned to 100% width.")
