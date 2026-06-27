from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL

doc = Document("template.docx")
for i, table in enumerate(doc.tables):
    print(f"\nTable {i}:")
    for j, row in enumerate(table.rows):
        cells_text = [c.text.strip().replace('\n', ' ')[:30] for c in row.cells]
        print(f"  Row {j}: {cells_text}")
