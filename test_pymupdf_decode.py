import re

def decode_pymupdf_garbage(text):
    # This maps chr(cid) to the actual character for the specific CAD font
    char_map = {
        chr(41): 'F',
        chr(50): 'O',
        chr(53): 'R',
        chr(48): 'M',
        chr(36): 'A',
        chr(40): 'E',
        chr(100): 'Ç',
        chr(173): 'Ã',
        chr(174): 'Õ',
        chr(11): '(',
        chr(12): ')',
        chr(91): 'x',
        chr(3): ' ',
        chr(20): '1',
        chr(21): '2',
        chr(22): '3',
        chr(23): '4',
        chr(24): '5',
        chr(25): '6',
        chr(26): '7',
        chr(27): '8',
        chr(28): '9',
        chr(19): '0'
    }
    # Only decode if it looks like the garbage string (has lots of these chars)
    # Actually, we can just translate the whole string if it contains these signature garbage chars like ')250$'
    decoded = ""
    for c in text:
        decoded += char_map.get(c, c)
    return decoded

def main():
    encoded = ")250$ ( $50$d\xad2\x0b\x14[\x0c"
    decoded = decode_pymupdf_garbage(encoded)
    print(f"Decoded PyMuPDF: {decoded}")

if __name__ == "__main__":
    main()
