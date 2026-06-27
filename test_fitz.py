import fitz

def main():
    filename = "F1425-TIR-PL151F-R0.pdf"
    doc = fitz.open(filename)
    page = doc[0]
    text = page.get_text("text")
    
    print("=== PYMUPDF TEXT ===")
    print(text)

if __name__ == "__main__":
    main()
