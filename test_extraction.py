import pdfplumber
import sys

def main():
    filename = "F1425-TIR-PL151F-R0.pdf"
    with pdfplumber.open(filename) as pdf:
        page = pdf.pages[0]
        text_normal = page.extract_text()
        text_layout = page.extract_text(layout=True)
        
    print("=== TEXT NORMAL ===")
    if text_normal:
        print(text_normal)
    else:
        print("NONE")
        
    print("\n=== TEXT LAYOUT ===")
    if text_layout:
        for i, line in enumerate(text_layout.split('\n')):
            print(f"{i:03d}: {line}")
    else:
        print("NONE")

if __name__ == "__main__":
    main()
