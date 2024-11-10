from pdf2docx import Converter

# Defina os arquivos de entrada e saída
pdf_file = 'original.pdf'
docx_file = 'original.docx'

# Crie o conversor e realize a conversão
cv = Converter(pdf_file)
cv.convert(docx_file, start=0, end=None)  # Define páginas de início e fim se necessário
cv.close()
