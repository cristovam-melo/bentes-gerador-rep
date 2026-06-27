import traceback
from word_generator import generate_rep_word
context = {
    "numero_rep": "001",
    "data_atual": "31/05/2026",
    "remetente": "A",
    "cliente": "B",
    "obra": "C",
    "destinatarios": [{"nome": "b", "empresa": "aa"}],
    "arquivos": [
        {"arquivo": "F237.pdf", "numero_folha": "F237", "descricao": "desc", "data_folha": "30/05/2026"}
    ]
}
try:
    buf = generate_rep_word('template.docx', context)
    print("SUCCESS")
except Exception as e:
    print("FAILED:", e)
    traceback.print_exc()
