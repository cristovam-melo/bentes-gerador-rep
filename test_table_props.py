import docx
from docx import Document
from docx.shared import Cm
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def set_cell_valign(cell, align='center'):
    tcPr = cell._tc.get_or_add_tcPr()
    vAlign = tcPr.first_child_found_in('w:vAlign')
    if vAlign is None:
        vAlign = OxmlElement('w:vAlign')
        tcPr.append(vAlign)
    vAlign.set(qn('w:val'), align)

def set_table_width_pct(table, pct, indent_cm=0):
    tbl = table._tbl
    tblPr = tbl.tblPr
    tblW = tblPr.first_child_found_in('w:tblW')
    if tblW is None:
        tblW = OxmlElement('w:tblW')
        tblPr.append(tblW)
    tblW.set(qn('w:type'), 'pct')
    tblW.set(qn('w:w'), str(int(pct * 50)))
    
    if indent_cm > 0:
        tblInd = tblPr.first_child_found_in('w:tblInd')
        if tblInd is None:
            tblInd = OxmlElement('w:tblInd')
            tblPr.append(tblInd)
        tblInd.set(qn('w:type'), 'dxa')
        tblInd.set(qn('w:w'), str(int(indent_cm * 567)))

doc = Document()
table = doc.add_table(rows=2, cols=4)
set_table_width_pct(table, 97.2, 0.04)

for row in table.rows:
    row.cells[0].width = Cm(4.18)
    for cell in row.cells:
        set_cell_valign(cell, 'center')
        cell.text = "test"

doc.save("test_props.docx")
print("SUCCESS")
