import pdfplumber
import re
import os

def extract_data_from_pdf(file_stream, filename):
    """
    Extrai informações (Folha, Data, Descrição) de um arquivo PDF de planta.
    
    file_stream: stream do arquivo (File-like object do Streamlit)
    filename: Nome original do arquivo PDF.
    """
    text_normal = ""
    text_layout = ""
    try:
        with pdfplumber.open(file_stream) as pdf:
            first_page = pdf.pages[0]
            text_normal = first_page.extract_text() or ""
            text_layout = first_page.extract_text(layout=True) or ""
    except Exception as e:
        print(f"Erro ao ler PDF {filename}: {e}")
        return None

    # 1. Arquivo
    arquivo = filename
    
    # Extração primária usando regex sobre o texto normal (muito mais robusto)
    numero_folha = ""
    descricao = ""
    data_folha = ""
    
    # Busca pela data (DD/MM/AAAA)
    match_data = re.search(r"(\d{2}/\d{2}/\d{2,4})", text_normal)
    if match_data:
        data_folha = match_data.group(1)

    # Regex para o bloco de Título, Obra e Folha
    # A estrutura esperada no texto normal é:
    # TITULO OBRA N. FOLHA N. REVISÃO
    # <numero_revisao>
    # <titulo_linha_1> <obra_n> <folha_n>
    # VERIFICAÇÃO
    # <titulo_linha_2> <rubrica>
    match_titulo = re.search(r'TITULO\s+OBRA N\.\s+FOLHA N\.\s+REVIS[ÃA]O\s*\n.*?\n(.*?)\s+([\w/]+)\s+([A-Z0-9]+)\s*\n.*?\n(.*?)\s+[A-Z]+\s*$', text_normal, re.MULTILINE | re.IGNORECASE)
    
    if match_titulo:
        titulo1 = match_titulo.group(1).strip()
        folha_n = match_titulo.group(3).strip()
        titulo2 = match_titulo.group(4).strip()
        
        numero_folha = folha_n
        descricao = f"{titulo1} - {titulo2}"

    # Fallback 1: Layout text extraction (se o regex falhar)
    if not numero_folha and text_layout:
        lines = text_layout.split('\n')
        for i, line in enumerate(lines):
            if 'FOLHA N.' in line.upper():
                idx_folha = line.upper().find('FOLHA N.')
                idx_right = len(line)
                for marker in ['REVISÃO', 'REVISAO']:
                    m_idx = line.upper().find(marker)
                    if m_idx > idx_folha and m_idx < idx_right:
                        idx_right = m_idx
                
                idx_left = max(0, idx_folha - 2)
                for j in range(1, 5):
                    if i + j < len(lines):
                        next_line = lines[i+j]
                        if len(next_line) > idx_left:
                            part = next_line[idx_left:idx_right].strip()
                            if part and any(c.isalnum() for c in part):
                                numero_folha = part.split()[-1] 
                                break
                if numero_folha:
                    break

    if not descricao and text_layout:
        lines = text_layout.split('\n')
        for i, line in enumerate(lines):
            if 'TITULO' in line.upper():
                idx_titulo = line.upper().find('TITULO')
                idx_right = len(line)
                for marker in ['OBRA N.', 'FOLHA N.', 'REVISÃO', 'REVISAO', 'ESCALA', 'DATA']:
                    m_idx = line.upper().find(marker)
                    if m_idx > idx_titulo and m_idx < idx_right:
                        idx_right = m_idx
                
                desc_parts = []
                for j in range(1, 6):
                    if i + j < len(lines):
                        next_line = lines[i+j]
                        if len(next_line) > idx_titulo:
                            part = next_line[idx_titulo:idx_right].strip()
                            if part:
                                desc_parts.append(part)
                
                if desc_parts:
                    descricao = " - ".join(desc_parts)
                break

    # Fallback 2: Nome do arquivo (se tudo falhar)
    if not numero_folha:
        parts = filename.split('-')
        numero_folha = parts[0] if parts else ""
        
    if not descricao:
        name_without_ext = os.path.splitext(filename)[0]
        if name_without_ext.startswith(numero_folha + "-"):
            name_without_ext = name_without_ext[len(numero_folha)+1:]
        descricao = name_without_ext

    return {
        "arquivo": arquivo,
        "numero_folha": numero_folha,
        "descricao": descricao,
        "data_folha": data_folha
    }
