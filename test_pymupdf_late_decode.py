def decode_pymupdf_garbage(text):
    char_map = {
        chr(41): 'F', chr(50): 'O', chr(53): 'R', chr(48): 'M',
        chr(36): 'A', chr(40): 'E', chr(100): 'Ç', chr(173): 'Ã',
        chr(174): 'Õ', chr(11): '(', chr(12): ')', chr(91): 'x',
        chr(3): ' ', chr(20): '1', chr(21): '2', chr(22): '3',
        chr(23): '4', chr(24): '5', chr(25): '6', chr(26): '7',
        chr(27): '8', chr(28): '9', chr(19): '0'
    }
    decoded = ""
    for c in text:
        decoded += char_map.get(c, c)
    return decoded

def test():
    # raw_text simulando PyMuPDF
    raw_lines = [
        "FORMA",
        "PL151F (1x)",
        "PAINEL DE FECHAMENTO PL151F",
        ")250$ ( $50$d\xad2\x0b\x14[\x0c"
    ]
    
    piece_name = "PL151F"
    best_line_idx = -1
    for i, line in enumerate(raw_lines):
        if piece_name.upper() in line.upper():
            if best_line_idx == -1 or len(line) > len(raw_lines[best_line_idx]):
                best_line_idx = i
                
    if best_line_idx != -1:
        titulo_principal = raw_lines[best_line_idx].strip()
        descricao = titulo_principal
        
        for offset in [1, -1, 2, -2]:
            idx = best_line_idx + offset
            if 0 <= idx < len(raw_lines):
                adj_line = raw_lines[idx].strip()
                # Aqui decodificamos a linha adjacente!
                adj_decoded = decode_pymupdf_garbage(adj_line)
                
                if len(adj_decoded) > 3 and adj_decoded != piece_name:
                    keywords = ["FORMA", "ARMA", "DETALHE", "PLANTA", "CORTE", "ELEVA", "MONTAGEM"]
                    if any(k in adj_decoded.upper() for k in keywords):
                        descricao = f"{titulo_principal} - {adj_decoded}"
                        break
                        
        print("RESULT:", descricao)

test()
