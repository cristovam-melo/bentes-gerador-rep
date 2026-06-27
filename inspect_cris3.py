from docx import Document
import os

def print_table_data(doc_path):
    print(f"\n========================================")
    print(f"FILE: {doc_path}")
    print(f"========================================")
    if not os.path.exists(doc_path):
        print("File not found!")
        return
    doc = Document(doc_path)
    table = doc.tables[4] # Table with drawing details
    for r_idx, row in enumerate(table.rows):
        row_text = [cell.text.strip().replace('\n', ' ') for cell in row.cells]
        if any(row_text):
            print(f"Row {r_idx:02d}: {row_text[0]:<25} | {row_text[1]:<8} | {row_text[2]:<30} | {row_text[3]}")

print_table_data("cris4.docx")
