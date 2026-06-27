from pdf_extractor import extract_data_from_pdf

filename = "F217-CEC-PVS5-V106-R0.PDF"
with open(filename, "rb") as f:
    data = extract_data_from_pdf(f, filename)
    print("EXTRACTED DATA:")
    print(data)
