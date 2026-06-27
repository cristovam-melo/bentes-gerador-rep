import re

dates = ["01/06/2026", "02/60/10", "31/12/99", "32/01/2020", "15/13/2022", "10/10/24"]
pattern = r"\b(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/(\d{4}|\d{2})\b"

for d in dates:
    match = re.search(pattern, d)
    if match:
        print(f"Valid: {match.group(0)}")
    else:
        print(f"Invalid: {d}")

filenames = ["F1425-TIR-PL151F-R0.pdf", "F211-CEC-PVS2-V213-R0.PDF", "F217-CEC-PVS5-V106-R0.PDF"]
for f in filenames:
    parts = f.replace('.pdf', '').replace('.PDF', '').split('-')
    if len(parts) >= 2:
        # Pega a penúltima parte, que geralmente é o nome da peça (ex: PL151F, V213, V106)
        # Se a última parte não for revisão (R0, R1...), pode ser a última
        if parts[-1].startswith('R') and parts[-1][1:].isdigit():
            piece_name = parts[-2]
        else:
            piece_name = parts[-1]
        print(f"Filename {f} -> Piece name: {piece_name}")
