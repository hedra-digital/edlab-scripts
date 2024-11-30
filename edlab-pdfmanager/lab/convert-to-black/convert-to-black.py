from pdf2image import convert_from_path
from PIL import Image
import numpy as np
import os

def convert_pdf_to_solid_black(input_pdf, output_pdf):
    """
    Converte um arquivo PDF colorido para preto chapado, mantendo apenas áreas totalmente
    brancas como branco e convertendo todas as outras cores para preto sólido.
    
    Args:
        input_pdf (str): Caminho do arquivo PDF de entrada
        output_pdf (str): Caminho para salvar o arquivo PDF em preto chapado
    """
    try:
        # Converte o PDF em uma lista de imagens
        pages = convert_from_path(input_pdf)
        
        # Converte cada página para preto chapado
        solid_black_pages = []
        for page in pages:
            # Converte para array numpy para manipulação mais fácil
            img_array = np.array(page)
            
            # Identifica pixels totalmente brancos (255, 255, 255)
            white_pixels = np.all(img_array == [255, 255, 255], axis=-1)
            
            # Cria uma nova imagem em preto e branco
            solid_black = np.zeros_like(img_array[..., 0], dtype=np.uint8)
            
            # Define pixels brancos
            solid_black[white_pixels] = 255
            
            # Converte de volta para imagem PIL
            solid_black_img = Image.fromarray(solid_black)
            
            # Converte para modo '1' (binário) para garantir preto chapado
            solid_black_img = solid_black_img.convert('1')
            
            solid_black_pages.append(solid_black_img)
        
        # Salva a primeira página como PDF
        solid_black_pages[0].save(
            output_pdf,
            'PDF',
            save_all=True,
            append_images=solid_black_pages[1:],
            resolution=300.0  # DPI alto para qualidade
        )
        
        print(f"PDF convertido com sucesso! Salvo em: {output_pdf}")
        
    except Exception as e:
        print(f"Erro ao converter o PDF: {str(e)}")

def batch_convert_pdfs(input_folder, output_folder):
    """
    Converte todos os PDFs de uma pasta para preto chapado.
    
    Args:
        input_folder (str): Pasta com os PDFs coloridos
        output_folder (str): Pasta para salvar os PDFs convertidos
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    for filename in os.listdir(input_folder):
        if filename.lower().endswith('.pdf'):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, f"BLACK_{filename}")
            convert_pdf_to_solid_black(input_path, output_path)

# Exemplo de uso
if __name__ == "__main__":
    # Para converter um único arquivo
    input_file = "logo2.pdf"
    output_file = "logo2-pb.pdf"
    convert_pdf_to_solid_black(input_file, output_file)
    
    # Para converter vários arquivos de uma vez
    # batch_convert_pdfs("pasta_entrada", "pasta_saida")