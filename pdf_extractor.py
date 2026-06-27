import re
import io
import fitz

def decode_pymupdf_garbage(text):
    if not text: return ""
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

def parse_pdf_date(date_str):
    if not date_str:
        return ""
    match = re.search(r"D:(\d{4})(\d{2})(\d{2})", date_str)
    if match:
        year, month, day = match.groups()
        return f"{day}/{month}/{year}"
    return ""

def _extract_title_block_descricao(raw_text):
    lines = raw_text.split('\n')

    folha_idx = None
    for i, line in enumerate(lines):
        if 'FOLHA N.' in line:
            folha_idx = i
            break
    if folha_idx is None:
        return None

    LABELS = {'CLIENTE', 'OBRA', 'DATA', 'TITULO', 'DESENHO',
              'REVISÃO', 'REVISAO', 'VERIFICAÇÃO', 'VERIFICACAO',
              'ESCALA', 'OBRA N.', 'FOLHA N.'}

    # Lines that are noise from the notes/observations block - should never be description
    NOISE_RE = re.compile(
        r'MEDIDAS EM|NOTAS E OBSERV|CARACTER[IÍ]STICAS DO CONCRETO|'
        r'CLASSE \(NBR|Rela[cç][aã]o a/c|'
        r'TAXA DE A[CÇ]O|COBRIMENTO SOBRE|VOLUME / PESO|'
        r'NA DESFORMA|^\s*GPa|^\s*MPa|Ec\s+GPa',
        re.IGNORECASE
    )

    meaningful = []
    for j in range(folha_idx + 1, len(lines)):
        line = lines[j].strip()
        if not line:
            continue
        if line in LABELS:
            continue
        if re.match(r'^A[0-9]$', line):
            continue
        if re.match(r'^\d+(?:[.,]\d+)?\s*(?:mm|cm|m)$', line):
            continue
        if NOISE_RE.search(line):
            continue
        meaningful.append(line)

    if len(meaningful) < 5:
        return None

    # Support P (Pilar), V (Viga), L (Laje), F (Fundação), D (Detalhe), M (Montagem), etc.
    PIECE_LINE_RE = re.compile(r'\b(?:P|V|L|F|D|M|PR|VS|BL|SC)(?:[0-9OOM]{1,4})\b', re.IGNORECASE)

    # TYPE_RE matches the structural type: FORMA, ARMAÇÃO, etc.
    # PAVILHÃO is NOT a type — it's a location prefix, handled separately
    TYPE_RE = re.compile(
        r'\b(FORMA|ARMA(?:ÇÃO|ÇAO|CAO)?|VIGA|DETALHE|PLANTA|CORTE|ELEVA(?:ÇÃO|ÇAO|CAO)?|MONTAGEM|DEXA)\b',
        re.IGNORECASE
    )

    # LOCATION_RE matches the location prefix (e.g. PAVILHÃO 2)
    LOCATION_RE = re.compile(
        r'\bPAVILH[ÃA]O\b',
        re.IGNORECASE
    )

    # FORMA_ARMACAO_RE specifically matches the "FORMA E ARMAÇÃO (Nx)" pattern
    FORMA_ARMACAO_RE = re.compile(
        r'FORMA\s+E?\s*ARMA[CÇ][AÃ]O\s*\(\d+x\)',
        re.IGNORECASE
    )

    description_line = None
    forma_line = None

    for idx, line in enumerate(meaningful):
        # Skip noise lines
        if NOISE_RE.search(line):
            continue

        has_piece = PIECE_LINE_RE.search(line)
        has_location = LOCATION_RE.search(line)
        has_forma = FORMA_ARMACAO_RE.search(line)
        has_type = TYPE_RE.search(line)

        # Best case: line has location + piece + forma all together
        # e.g. "PAVILHÃO 2 - P10 - FORMA E ARMAÇÃO (1x)"
        if has_location and has_piece and has_forma:
            return line

        # Line has location + piece (e.g. "PAVILHÃO 2 - P10")
        # Look ahead for the FORMA E ARMAÇÃO line
        if has_location and has_piece:
            description_line = line
            # Search the next few meaningful lines for FORMA E ARMAÇÃO
            for k in range(idx + 1, min(idx + 4, len(meaningful))):
                next_line = meaningful[k]
                if FORMA_ARMACAO_RE.search(next_line):
                    forma_line = next_line
                    break
            if description_line:
                break

        # Line has piece + type but NOT location (e.g. "V207=V217 - FORMA E ARMAÇÃO (2x)")
        if has_piece and has_type and not has_location:
            if not NOISE_RE.search(line):
                description_line = line
                break

    if description_line:
        if forma_line:
            return f"{description_line} - {forma_line}"
        return description_line

    # Second pass: look for piece-only line and type-only line separately
    piece_line = None
    type_line = None

    for line in meaningful:
        if NOISE_RE.search(line):
            continue
        has_piece = PIECE_LINE_RE.search(line)
        has_type = TYPE_RE.search(line)

        if has_piece and not piece_line:
            piece_line = line
        elif has_type and not has_piece:
            if not type_line:
                type_line = line

    if piece_line and type_line:
        if type_line.upper() in piece_line.upper():
            return piece_line
        return f"{piece_line} - {type_line}"

    if piece_line:
        return piece_line

    # Fallback to the original logic
    verific_idx = -1
    for idx in range(len(meaningful) - 1, -1, -1):
        val = meaningful[idx]
        if re.match(r'^[A-ZÀ-Ú]{1,5}$', val) and idx >= min(4, len(meaningful) - 2):
            verific_idx = idx
            break

    if verific_idx >= 0:
        desenho_parts = []
        if verific_idx > 0:
            line_before = meaningful[verific_idx - 1]
            if line_before and not re.match(r'^\d+$', line_before):
                if verific_idx > 1:
                    line_before2 = meaningful[verific_idx - 2]
                    if not re.search(r'\d+/\d+\s+F\d{3,4}|\d{2}/\d{2}/\d{4}', line_before2):
                        return f"{line_before2} - {line_before}"
                return line_before

        DESENHO_RE = re.compile(
            r'^(?:P\d{2,4}\s*-(?!.*PLT)|\bFORMA\b|\bARMA(?:ÇÃO|CAO)?\b|\bVIGA\b|\bDETALHE\b|\bPLANTA\b|\bCORTE\b|'
            r'\bELEVA\b|\bMONTAGEM\b|\bDEXA\b|\bPAVILH\b)',
            re.IGNORECASE
        )

        for part in meaningful[verific_idx + 1:]:
            if DESENHO_RE.search(part):
                desenho_parts.append(part)
            elif desenho_parts:
                break
            if len(desenho_parts) >= 2:
                break

        if desenho_parts:
            return ' - '.join(desenho_parts)

    # Fallback: try to extract TITULO directly via regex
    titulo_match = re.search(
        r'TITULO\s+OBRA N\.\s+FOLHA N\.\s+REVIS[ÃA]O\s*\n.*?\n(.*?)\s+([\w/]+)\s+([A-Z0-9]+)\s*\n.*?\n(.*?)\s+[A-Z]+\s*$',
        raw_text, re.MULTILINE | re.IGNORECASE
    )
    if titulo_match:
        titulo1 = titulo_match.group(1).strip()
        titulo2 = titulo_match.group(4).strip()
        if titulo2 and titulo2 != titulo1:
            return f"{titulo1} - {titulo2}"
        return titulo1

    return None

def _extract_date_from_pymupdf(doc, raw_text):
    date_pattern = r"\b(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/(\d{4}|\d{2})\b"
    match = re.search(date_pattern, raw_text)
    if match:
        return match.group(0)

    decoded = decode_pymupdf_garbage(raw_text)
    match = re.search(date_pattern, decoded)
    if match:
        return match.group(0)

    mod_date = doc.metadata.get("modDate") or doc.metadata.get("creationDate")
    if mod_date:
        return parse_pdf_date(mod_date)

    return ""

def extract_data_from_pdf(file_stream, filename):
    file_stream.seek(0)
    pdf_bytes = file_stream.read()

    arquivo = filename
    numero_folha = ""
    descricao = ""
    data_folha = ""

    clean_filename = re.sub(r'\.pdf$', '', filename, flags=re.IGNORECASE)
    parts = clean_filename.split('-')
    if parts:
        numero_folha = parts[0]

    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page = doc[0]
        raw_text = page.get_text("text")

        data_folha = _extract_date_from_pymupdf(doc, raw_text)

        descricao = _extract_title_block_descricao(raw_text)

        if not descricao:
            decoded = decode_pymupdf_garbage(raw_text)
            descricao = _extract_title_block_descricao(decoded)

    except Exception as e:
        print(f"Erro PyMuPDF no arquivo {filename}: {e}")

    if not descricao:
        piece_name = ""
        if len(parts) >= 2:
            if parts[-1].startswith('R') and parts[-1][1:].isdigit():
                piece_name = parts[-2]
            else:
                piece_name = parts[-1]
        if piece_name:
            descricao = piece_name
        else:
            name_without_ext = clean_filename
            if name_without_ext.startswith(numero_folha + "-"):
                name_without_ext = name_without_ext[len(numero_folha) + 1:]
            descricao = name_without_ext

    # Normalize multiple whitespace in description (PDF text extraction artifacts)
    if descricao:
        descricao = re.sub(r'\s{2,}', ' ', descricao).strip()

    return {
        "arquivo": arquivo,
        "numero_folha": numero_folha,
        "descricao": descricao,
        "data_folha": data_folha
    }

