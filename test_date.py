import fitz
import re

def main():
    filename = "F1425-TIR-PL151F-R0.pdf"
    doc = fitz.open(filename)
    page = doc[0]
    text = page.get_text("text")
    dates = re.findall(r"\d{2}/\d{2}/\d{2,4}", text)
    print(f"Found dates: {dates}")
    
if __name__ == "__main__":
    main()
