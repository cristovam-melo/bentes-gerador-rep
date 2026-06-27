import re

def test_regex():
    # Previous Regex
    PIECE_LINE_RE_OLD = re.compile(r'\b(?:P|V|L|F|D|M|PR|VS|BL|SC)(?:[0-9OOM]{2,4})\b', re.IGNORECASE)
    # New Regex
    PIECE_LINE_RE_NEW = re.compile(r'\b(?:P|V|L|F|D|M|PR|VS|BL|SC)(?:[0-9OOM]{1,4})\b', re.IGNORECASE)

    texts = [
        "PAVILHÃO 2 - P7 - FORMA E ARMAÇÃO (1x)",
        "PAVILHÃO 2 - P9 - FORMA E ARMAÇÃO (2x)",
        "PAVILHÃO 2 - P10 - FORMA E ARMAÇÃO (1x)"
    ]

    for t in texts:
        print(f"Texto: {t}")
        match_old = PIECE_LINE_RE_OLD.search(t)
        print(f"  Match Regex Antigo: {match_old.group(0) if match_old else 'None'}")
        match_new = PIECE_LINE_RE_NEW.search(t)
        print(f"  Match Regex Novo:   {match_new.group(0) if match_new else 'None'}")
        print("-" * 40)

if __name__ == "__main__":
    test_regex()
