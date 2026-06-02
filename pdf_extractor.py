import pdfplumber
import fitz
import re
import os

def decode_cid_text(text):
    if not text: return ""
    cid_map = {
        "(cid:41)": "F", "(cid:50)": "O", "(cid:53)": "R", "(cid:48)": "M",
        "(cid:36)": "A", "(cid:40)": "E", "(cid:100)": "Ç", "(cid:173)": "Ã",
        "(cid:174)": "Õ", "(cid:11)": "(", "(cid:12)": ")", "(cid:91)": "x",
        "(cid:3)": " ", "(cid:20)": "1", "(cid:21)": "2", "(cid:22)": "3",
        "(cid:23)": "4", "(cid:24)": "5", "(cid:25)": "6", "(cid:26)": "7",
        "(cid:27)": "8", "(cid:28)": "9", "(cid:19)": "0"
    }
    for cid, char in cid_map.items():
        text = text.replace(cid, char)
    return text

def parse_pdf_date(date_str):
    if not date_str:
        return ""
    match = re.search(r"D:(\d{4})(\d{2})(\d{2})", date_str)
    if match:
        year, month, day = match.groups()
        return f"{day}/{month}/{year}"
    return ""

def extract_data_from_pdf(file_stream, filename):
    """
    Extrai informações (Folha, Data, Descrição) de um arquivo PDF de planta.
    """
    file_stream.seek(0)
    pdf_bytes = file_stream.read()
    
    # --- TENTATIVA 1: pdfplumber ---
    text_normal = ""
    text_layout = ""
    try:
        import io
        temp_stream = io.BytesIO(pdf_bytes)
        with pdfplumber.open(temp_stream) as pdf:
            first_page = pdf.pages[0]
            text_normal = first_page.extract_text() or ""
            text_layout = first_page.extract_text(layout=True) or ""
            
            # Decodifica fontes CAD que caem como (cid:xxx)
            text_normal = decode_cid_text(text_normal)
            text_layout = decode_cid_text(text_layout)
    except Exception as e:
        print(f"Erro ao ler PDF {filename} com pdfplumber: {e}")

    arquivo = filename
    numero_folha = ""
    descricao = ""
    data_folha = ""
    
    clean_filename = re.sub(r'\.pdf$', '', filename, flags=re.IGNORECASE)
    parts = clean_filename.split('-')
    if parts:
        numero_folha = parts[0]
        
    # Busca pela data em textos
    date_pattern = r"\b(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/(\d{4}|\d{2})\b"
    match_data = re.search(date_pattern, text_normal + "\n" + text_layout)
    if match_data:
        data_folha = match_data.group(0)

    # Tenta o regex padrão do Bentes para o título
    match_titulo = re.search(r'TITULO\s+OBRA N\.\s+FOLHA N\.\s+REVIS[ÃA]O\s*\n[^\n]{0,100}\n(.*?)\s+([\w/]+)\s+([A-Z0-9]+)\s*\n[^\n]{0,100}\n(.*?)\s+[A-Z]+\s*$', text_normal, re.MULTILINE | re.IGNORECASE)
    if match_titulo:
        titulo1 = match_titulo.group(1).strip()
        folha_n = match_titulo.group(3).strip()
        titulo2 = match_titulo.group(4).strip()
        
        if not numero_folha or len(numero_folha) < 2:
            numero_folha = folha_n
            
        descricao = f"{titulo1} - {titulo2}"
        if clean_filename in descricao or len(descricao) < 5:
            descricao = ""

    # Se ainda não encontrou descrição, usa heurística no próprio text_normal
    if not descricao or "TITULO" not in descricao:
        piece_name = ""
        if len(parts) >= 2:
            if parts[-1].startswith('R') and parts[-1][1:].isdigit():
                piece_name = parts[-2]
            else:
                piece_name = parts[-1]
            
        if piece_name:
            lines = text_normal.split('\n')
            best_line_idx = -1
            for i, line in enumerate(lines):
                if piece_name.upper() in line.upper():
                    if best_line_idx == -1 or len(line) > len(lines[best_line_idx]):
                        best_line_idx = i
                        
            if best_line_idx != -1:
                titulo_principal = lines[best_line_idx].strip()
                descricao = titulo_principal
                
                # Busca nas linhas adjacentes o complemento (Regra A - B)
                for offset in [1, -1, 2, -2]:
                    idx = best_line_idx + offset
                    if 0 <= idx < len(lines):
                        adj_line = lines[idx].strip()
                        if len(adj_line) > 3 and adj_line != piece_name:
                            keywords = ["FORMA", "ARMA", "DETALHE", "PLANTA", "CORTE", "ELEVA", "MONTAGEM"]
                            if any(k in adj_line.upper() for k in keywords):
                                descricao = f"{titulo_principal} - {adj_line}"
                                break

    # --- TENTATIVA 2: PyMuPDF (fitz) APENAS PARA DATA SE FALTAR ---
    if not data_folha:
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            page = doc[0]
            fitz_text = page.get_text("text")
            
            match_data_fitz = re.search(date_pattern, fitz_text)
            if match_data_fitz:
                data_folha = match_data_fitz.group(0)
            
            if not data_folha:
                mod_date = doc.metadata.get("modDate") or doc.metadata.get("creationDate")
                data_folha = parse_pdf_date(mod_date)
                                    
        except Exception as e:
            print(f"Erro PyMuPDF no arquivo {filename}: {e}")

    # Fallback final se tudo falhar: Nome do arquivo limpo
    if not descricao:
        name_without_ext = clean_filename
        if name_without_ext.startswith(numero_folha + "-"):
            name_without_ext = name_without_ext[len(numero_folha)+1:]
        descricao = name_without_ext

    return {
        "arquivo": arquivo,
        "numero_folha": numero_folha,
        "descricao": descricao,
        "data_folha": data_folha
    }

