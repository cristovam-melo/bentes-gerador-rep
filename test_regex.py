import os, re
import pdfplumber

for f in os.listdir('.'):
    if f.endswith('.PDF'):
        with pdfplumber.open(f) as pdf:
            text = pdf.pages[0].extract_text()
            
            # regex test
            match = re.search(r'TITULO\s+OBRA N\.\s+FOLHA N\.\s+REVIS[ÃA]O\s*\n.*?\n(.*?)\s+([\w/]+)\s+([A-Z0-9]+)\s*\n.*?\n(.*?)\s+[A-Z]+\s*$', text, re.MULTILINE | re.IGNORECASE)
            if match:
                titulo1 = match.group(1).strip()
                obra_n = match.group(2).strip()
                folha_n = match.group(3).strip()
                titulo2 = match.group(4).strip()
                
                descricao = f"{titulo1} - {titulo2}"
                print(f"{f}: OK -> {folha_n} | {descricao}")
            else:
                print(f"{f}: FAIL")
