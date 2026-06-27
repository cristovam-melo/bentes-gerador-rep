import re

cid_map = {
    "(cid:41)": "F", "(cid:50)": "O", "(cid:53)": "R", "(cid:48)": "M",
    "(cid:36)": "A", "(cid:40)": "E", "(cid:100)": "Ç", "(cid:173)": "Ã",
    "(cid:174)": "Õ", "(cid:11)": "(", "(cid:12)": ")", "(cid:91)": "x",
    "(cid:3)": " ", "(cid:20)": "1", "(cid:21)": "2", "(cid:22)": "3",
    "(cid:23)": "4", "(cid:24)": "5", "(cid:25)": "6", "(cid:26)": "7",
    "(cid:27)": "8", "(cid:28)": "9", "(cid:19)": "0"
}

def decode_cid(text):
    for cid, char in cid_map.items():
        text = text.replace(cid, char)
    return text

def test_heuristic_with_pdfplumber():
    # Simulando o text_normal gerado pelo pdfplumber do arquivo F1425
    text_normal = """TITULO OBRA N. FOLHA N. REVISÃO
00
25/013 F1425 APROVAÇÃO
PAINEL DE FECHAMENTO PL151F
RFB
(cid:41)(cid:50)(cid:53)(cid:48)(cid:36)(cid:3)(cid:40)(cid:3)(cid:36)(cid:53)(cid:48)(cid:36)(cid:100)(cid:173)(cid:50)(cid:3)(cid:11)(cid:20)(cid:91)(cid:12)"""

    text_normal = decode_cid(text_normal)
    lines = text_normal.split('\n')
    
    piece_name = "PL151F"
    best_line_idx = -1
    for i, line in enumerate(lines):
        if piece_name.upper() in line.upper():
            if best_line_idx == -1 or len(line) > len(lines[best_line_idx]):
                best_line_idx = i
                
    descricao = ""
    if best_line_idx != -1:
        titulo_principal = lines[best_line_idx].strip()
        descricao = titulo_principal
        
        for offset in [1, -1, 2, -2]:
            idx = best_line_idx + offset
            if 0 <= idx < len(lines):
                adj_line = lines[idx].strip()
                if len(adj_line) > 3 and adj_line != piece_name:
                    keywords = ["FORMA", "ARMA", "DETALHE", "PLANTA", "CORTE", "ELEVA", "MONTAGEM"]
                    if any(k in adj_line.upper() for k in keywords):
                        descricao = f"{titulo_principal} - {adj_line}"
                        break
                        
    print("FINAL DESC (PDFPlumber):", descricao)

test_heuristic_with_pdfplumber()
