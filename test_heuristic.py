def test_heuristic():
    lines = [
        "FORMA",
        "PL151F (1x)",
        "PAINEL DE FECHAMENTO PL151F",
        ")250$ ( $50$d2   ["
    ]
    
    # Simula decodificação
    char_map = {
        chr(41): 'F', chr(50): 'O', chr(53): 'R', chr(48): 'M',
        chr(36): 'A', chr(40): 'E', chr(100): 'Ç', chr(173): 'Ã',
        chr(174): 'Õ', chr(11): '(', chr(12): ')', chr(91): 'x',
        chr(3): ' ', chr(20): '1', chr(21): '2', chr(22): '3',
        chr(23): '4', chr(24): '5', chr(25): '6', chr(26): '7',
        chr(27): '8', chr(28): '9', chr(19): '0'
    }
    def decode(text):
        return "".join(char_map.get(c, c) for c in text)
        
    lines = [decode(l) for l in lines]
    print(lines)
    
    best_line_idx = 2
    titulo_principal = lines[best_line_idx].strip()
    descricao = titulo_principal
    
    # Checa -1, +1, -2, +2
    for offset in [1, -1, 2, -2]:
        idx = best_line_idx + offset
        if 0 <= idx < len(lines):
            adj_line = lines[idx].strip()
            if len(adj_line) > 3 and " (1x)" not in adj_line and " (2x)" not in adj_line:
                # wait, " (1x)" is what we WANT!
                pass
            
            # actually, let's just look for FORMA or ARMA
            if "FORMA" in adj_line.upper() or "ARMA" in adj_line.upper() or "DETALHE" in adj_line.upper() or "ARMADURA" in adj_line.upper():
                descricao = f"{titulo_principal} - {adj_line}"
                break
                
    print("FINAL DESC:", descricao)

test_heuristic()
