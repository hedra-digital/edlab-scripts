from pdf2image import convert_from_path
from PIL import Image
import os

def convert_pdf_to_bw(input_pdf, output_pdf):
    """
    Converte um arquivo PDF colorido para preto e branco (grayscale).
    
    Args:
        input_pdf (str): Caminho do arquivo PDF de entrada (colorido)
        output_pdf (str): Caminho para salvar o arquivo PDF em preto e branco
    """
    try:
        # Converte o PDF em uma lista de imagens
        pages = convert_from_path(input_pdf)
        
        # Converte cada página para preto e branco
        bw_pages = []
        for page in pages:
            # Converte para escala de cinza
            bw_page = page.convert('L')
            bw_pages.append(bw_page)
        
        # Salva a primeira página como PDF
        bw_pages[0].save(
            output_pdf,
            'PDF',
            save_all=True,
            append_images=bw_pages[1:] # Adiciona as páginas restantes
        )
        
        print(f"PDF convertido com sucesso! Salvo em: {output_pdf}")
        
    except Exception as e:
        print(f"Erro ao converter o PDF: {str(e)}")

# Exemplo de uso
if __name__ == "__main__":
    input_file = "logo2.pdf"
    output_file = "logo2-pb.pdf"
    
    convert_pdf_to_bw(input_file, output_file)
