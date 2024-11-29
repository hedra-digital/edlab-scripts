import fitz  # PyMuPDF
import PIL.Image
import io

def check_pdf_colors(pdf_path):
    doc = fitz.open(pdf_path)
    
    for page in doc:
        pix = page.get_pixmap()
        img_data = pix.samples
        image = PIL.Image.frombytes("RGB", [pix.width, pix.height], img_data)
        
        # Verifica se há pixels não-cinza
        for pixel in image.getdata():
            r, g, b = pixel
            if not (r == g == b):
                return True
                
    return False

pdf_file = "exemplo.pdf"
is_color = check_pdf_colors(pdf_file)
print(f"O PDF é: {'Colorido' if is_color else 'Preto e Branco'}")