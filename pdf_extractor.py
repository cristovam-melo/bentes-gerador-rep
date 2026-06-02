import pdfplumber
import fitz
import re
import os

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
    except Exception as e:
        print(f"Erro ao ler PDF {filename} com pdfplumber: {e}")

    arquivo = filename
    numero_folha = ""
    descricao = ""
    data_folha = ""
    
    # Tenta descobrir o número da folha pelo nome do arquivo (ex: F1425-TIR-PL151F-R0 -> F1425)
    # Limpa a extensão primeiro
    clean_filename = re.sub(r'\.pdf$', '', filename, flags=re.IGNORECASE)
    parts = clean_filename.split('-')
    if parts:
        numero_folha = parts[0]
        
    # Busca pela data (DD/MM/AAAA ou DD/MM/AA) em ambos os textos usando um regex mais seguro
    date_pattern = r"\b(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/(\d{4}|\d{2})\b"
    match_data = re.search(date_pattern, text_normal + "\n" + text_layout)
    if match_data:
        data_folha = match_data.group(0) # group(0) pega a data completa

    # Tenta o regex padrão do Bentes para o título
    # Evitamos que o .*? pule muitas linhas e pegue lixo limitando com [^\n]{0,100}
    match_titulo = re.search(r'TITULO\s+OBRA N\.\s+FOLHA N\.\s+REVIS[ÃA]O\s*\n[^\n]{0,100}\n(.*?)\s+([\w/]+)\s+([A-Z0-9]+)\s*\n[^\n]{0,100}\n(.*?)\s+[A-Z]+\s*$', text_normal, re.MULTILINE | re.IGNORECASE)
    if match_titulo:
        titulo1 = match_titulo.group(1).strip()
        folha_n = match_titulo.group(3).strip()
        titulo2 = match_titulo.group(4).strip()
        
        # Só atualiza a folha se não tivermos pego do arquivo ou se a do arquivo for muito curta
        if not numero_folha or len(numero_folha) < 2:
            numero_folha = folha_n
            
        descricao = f"{titulo1} - {titulo2}"
        
        # Se a descrição pega pelo regex for igual ao nome do arquivo, provavelmente foi um falso positivo
        if clean_filename in descricao or len(descricao) < 5:
            descricao = "" # Anula para forçar o PyMuPDF

    # --- TENTATIVA 2: PyMuPDF (fitz) para descrições sem "TITULO" (Padrão Dexa/CAD) ---
    if not descricao or "TITULO" not in descricao:
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            page = doc[0]
            fitz_text = page.get_text("text")
            
            # Procura por outras datas seguras caso o pdfplumber tenha falhado
            if not data_folha:
                match_data_fitz = re.search(date_pattern, fitz_text)
                if match_data_fitz:
                    data_folha = match_data_fitz.group(0)
            
            # Heurística para achar o Título baseado no nome da peça no arquivo
            # A peça geralmente é a penúltima parte antes da revisão (ex: F211-CEC-PVS2-V213-R0 -> V213)
            piece_name = ""
            if len(parts) >= 2:
                if parts[-1].startswith('R') and parts[-1][1:].isdigit(): # Verifica se a última é revisão (R0, R1)
                    piece_name = parts[-2]
                else:
                    piece_name = parts[-1]
                
            if piece_name:
                lines = fitz_text.split('\n')
                best_line_idx = -1
                for i, line in enumerate(lines):
                    # Procura a linha mais longa que contém o nome da peça (geralmente é o título principal)
                    if piece_name.upper() in line.upper():
                        if best_line_idx == -1 or len(line) > len(lines[best_line_idx]):
                            best_line_idx = i
                            
                if best_line_idx != -1:
                    titulo_principal = lines[best_line_idx].strip()
                    descricao = titulo_principal
                    
                    # Tenta pegar um subtítulo legível ao redor
                    if best_line_idx > 0:
                        prev_line = lines[best_line_idx-1].strip()
                        if len(prev_line) > 3 and not prev_line.startswith("(cid:") and " (1x)" not in prev_line and " (2x)" not in prev_line:
                            if "FORMA" in prev_line.upper() or "ARMA" in prev_line.upper():
                                descricao = f"{titulo_principal} - {prev_line}"
                                
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

