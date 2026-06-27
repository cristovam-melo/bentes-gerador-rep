import re

def parse_pdf_date(date_str):
    if not date_str:
        return ""
    # Usually D:YYYYMMDDHHMMSS
    match = re.search(r"D:(\d{4})(\d{2})(\d{2})", date_str)
    if match:
        year, month, day = match.groups()
        return f"{day}/{month}/{year}"
    return ""

print(parse_pdf_date("D:20260601183627"))
