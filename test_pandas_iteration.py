import pandas as pd

default_destinatarios = pd.DataFrame(
    [
        {"nome": "FULANO", "empresa": "EMPRESA A"},
        {"nome": "BELTRANO", "empresa": "PRODUZ NUM SEI QUE"},
        {"nome": None, "empresa": None}
    ]
)

destinatarios = []
for _, row in default_destinatarios.iterrows():
    nome_val = str(row['nome']).strip() if pd.notna(row['nome']) else ""
    emp_val = str(row['empresa']).strip() if pd.notna(row['empresa']) else ""
    if nome_val and nome_val.lower() != "nan":
        destinatarios.append({"nome": nome_val, "empresa": emp_val})
        
print("DESTINATARIOS:", destinatarios)
