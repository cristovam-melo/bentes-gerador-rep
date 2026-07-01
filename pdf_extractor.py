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

def _extract_title_block_descricao(raw_text, numero_folha=""):
    lines = raw_text.split('\n')

    # Support P, V, L, F, D, M, PR, VS, BL, SC, and C (Consolo)
    PIECE_LINE_RE = re.compile(r'\b(?:P|V|L|F|D|M|PR|VS|BL|SC|C)(?:[0-9OOM]{1,4})\b', re.IGNORECASE)

    # LOCATION_RE matches the location prefix (e.g. PAVILHÃO 2)
    LOCATION_RE = re.compile(r'\bPAVILH[ÃA]O\b', re.IGNORECASE)

    # FORMA_ARMACAO_RE matches drawing types
    FORMA_ARMACAO_RE = re.compile(
        r'\b(?:FORMA\s+E?\s*ARMA[CÇ][AÃ]O|FORMA|ARMA[CÇ][AÃ]O|DETALHE|PLANTA|CORTE|ELEVA[CÇ][AÃ]O|MONTAGEM)\b(?:\s*\(\d+x\))?',
        re.IGNORECASE
    )

    # ── Early-detection: PDFs where title block has no FOLHA N. marker ──
    # Scan all lines looking for a consecutive pair: piece description + drawing type.
    # We skip lines that look like encoded garbage (too many non-printable chars).
    GARBAGE_RE = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]')
    # Pattern typical of PyMuPDF encoded title text (dollar signs + digits + special chars)
    ENCODED_TITLE_RE = re.compile(r'[\$%&@#]{1,}\d|\d[\$%&@#]')

    def is_garbage_line(text):
        """Return True if line contains too many non-printable/control characters."""
        if not text:
            return False
        garbage_count = len(GARBAGE_RE.findall(text))
        # Also detect lines that look like encoded PyMuPDF text ($ mixed with digits)
        has_encoded_pattern = bool(ENCODED_TITLE_RE.search(text))
        return (garbage_count >= 1 or has_encoded_pattern)


    # Build a clean list of (original_index, text) ignoring garbage and pure-number lines
    NUM_ONLY_RE = re.compile(r'^\d+([.,]\d+)?\s*(mm|cm|m|GPa|MPa|kg|kgf)?$')
    clean_indexed = []
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        if is_garbage_line(stripped):
            continue
        if NUM_ONLY_RE.match(stripped):
            continue
        clean_indexed.append((idx, stripped))

    # Walk clean lines to find best (piece, forma) pair
    best_piece = None
    best_forma = None
    best_location = None

    def piece_score(text):
        """Higher score = better/more descriptive piece title."""
        score = 0
        # Contains a structural keyword → likely the main title
        if re.search(r'\b(VIGA|PILAR|LAJE|COLUNA|VIGA BALDRAME|CONSOLO)\b', text, re.IGNORECASE):
            score += 10
        # Contains '=' → multiple equivalent pieces (rich title)
        if '=' in text:
            score += 5
        # Contains (Nx) multiplier
        if re.search(r'\(\d+x\)', text):
            score += 3
        # Has multiple digits/numbers
        digit_count = len(re.findall(r'\d+', text))
        score += min(digit_count, 3)
        # Longer text is generally more descriptive
        score += min(len(text) // 5, 4)
        return score

    for ci, (idx, text) in enumerate(clean_indexed):
        if PIECE_LINE_RE.search(text):
            matches = PIECE_LINE_RE.findall(text)
            valid = all(m.upper() not in ('CM', 'MM', 'M', 'KG', 'KGF') for m in matches)
            if not valid:
                continue
            # Look ahead within the next 3 clean lines for a forma line
            lookahead = clean_indexed[ci + 1: ci + 4]
            found_forma = None
            for _, next_text in lookahead:
                if FORMA_ARMACAO_RE.search(next_text):
                    found_forma = next_text
                    break
            # If no clean forma found, check raw lines directly after this line
            # (handles cases where ARMAÇÃO/FORMA is in garbage-encoded text)
            if found_forma is None:
                for raw_offset in range(1, 4):
                    raw_idx = idx + raw_offset
                    if raw_idx < len(lines):
                        raw_line = lines[raw_idx].strip()
                        if raw_line and is_garbage_line(raw_line):
                            decoded_line = decode_pymupdf_garbage(raw_line)
                            if FORMA_ARMACAO_RE.search(decoded_line):
                                # Use a canonical form label based on what was decoded
                                if re.search(r'ARMA', decoded_line, re.IGNORECASE):
                                    found_forma = 'ARMAÇÃO'
                                elif re.search(r'FORMA', decoded_line, re.IGNORECASE):
                                    found_forma = 'FORMA'
                                else:
                                    found_forma = decoded_line.strip()
                                break
                        elif raw_line and not NUM_ONLY_RE.match(raw_line):
                            # Hit a non-garbage, non-number line that's not a forma - stop
                            if not FORMA_ARMACAO_RE.search(raw_line):
                                break
            if found_forma:
                # Check location in surrounding lines
                loc = None
                lookbehind = clean_indexed[max(0, ci - 2): ci]
                for _, prev_text in lookbehind:
                    if LOCATION_RE.search(prev_text):
                        loc = prev_text
                        break
                # Keep the highest-scoring piece title
                if best_piece is None or piece_score(text) > piece_score(best_piece):
                    best_piece = text
                    best_forma = found_forma
                    best_location = loc



    if best_piece and best_forma:
        combined_parts = []
        if best_location:
            combined_parts.append(best_location)
        combined_parts.append(best_piece)
        # Only append forma if it's different from piece
        if best_forma != best_piece:
            combined_parts.append(best_forma)
        return " - ".join(combined_parts)


    folha_idx = None
    for i, line in enumerate(lines):
        if 'FOLHA N.' in line:
            folha_idx = i
            break

    # If no FOLHA N. found, process all lines (some PDFs omit this label)
    if folha_idx is None:
        folha_idx = -1

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

    if len(meaningful) < 2:
        return None

    piece_line = None
    location_line = None
    forma_line = None

    for line in meaningful:
        # Check location
        if LOCATION_RE.search(line) and not location_line:
            location_line = line
        
        # Check piece
        matches = PIECE_LINE_RE.findall(line)
        if matches and not piece_line:
            # We must filter out sheet numbers and units
            is_valid = True
            for match in matches:
                m_upper = match.upper()
                if m_upper in ['CM', 'MM', 'M', 'KG', 'KGF']:
                    is_valid = False
                    break
                if numero_folha:
                    nf_upper = numero_folha.upper()
                    if m_upper == nf_upper or m_upper == nf_upper.replace('F', ''):
                        is_valid = False
                        break
            if is_valid:
                piece_line = line
            
        # Check forma/type
        if FORMA_ARMACAO_RE.search(line) and not forma_line:
            forma_line = line

    # Now let's combine them intelligently
    if piece_line:
        has_forma_in_piece = FORMA_ARMACAO_RE.search(piece_line)
        has_location_in_piece = LOCATION_RE.search(piece_line) if location_line else True
        
        parts = []
        if location_line and not has_location_in_piece:
            parts.append(location_line)
        parts.append(piece_line)
        if forma_line and not has_forma_in_piece:
            parts.append(forma_line)
            
        return " - ".join(parts)

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

        descricao = _extract_title_block_descricao(raw_text, numero_folha)

        if not descricao:
            decoded = decode_pymupdf_garbage(raw_text)
            descricao = _extract_title_block_descricao(decoded, numero_folha)

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
