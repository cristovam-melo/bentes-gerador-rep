import fitz

def main():
    filename = "F1425-TIR-PL151F-R0.pdf"
    doc = fitz.open(filename)
    print("=== PDF METADATA ===")
    for key, value in doc.metadata.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()
