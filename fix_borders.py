from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

doc = Document("template.docx")
table5 = doc.tables[5]
tblBorders = table5._tbl.tblPr.xpath("w:tblBorders")[0]

ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

# Remove left, right, insideV, insideH
for name in ['left', 'right', 'insideV', 'insideH']:
    el = tblBorders.xpath(f"w:{name}", namespaces=ns)
    if el:
        tblBorders.remove(el[0])

# Ensure top and bottom are present and correct size
for name in ['top', 'bottom']:
    el = tblBorders.xpath(f"w:{name}", namespaces=ns)
    if not el:
        border = OxmlElement(f"w:{name}")
        tblBorders.append(border)
    else:
        border = el[0]
    border.set(qn("w:val"), "single")
    border.set(qn("w:sz"), "12") # Thicker border to match top
    border.set(qn("w:space"), "0")
    border.set(qn("w:color"), "auto")

doc.save("template.docx")
print("Removed vertical/side borders and enforced top/bottom borders on Table 5")
