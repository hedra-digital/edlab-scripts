from PyPDF2 import PdfReader
import re

def check_pdf_color(pdf_path):
    reader = PdfReader(pdf_path)
    has_color = False
    
    for page in reader.pages:
        content = page.extract_text()
        if '/DeviceRGB' in str(page) or '/DeviceCMYK' in str(page):
            has_color = True
            break
    
    return "Color" if has_color else "Grayscale"

# Usage
pdf_file = "ficha-pb_modified.pdf"
result = check_pdf_color(pdf_file)
print(f"PDF is in {result}")
