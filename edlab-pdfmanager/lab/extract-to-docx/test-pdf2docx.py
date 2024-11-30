# yay -S python-pdf2docx
from pdf2docx import Converter
import os


def converter_pdf_com_opcoes(pdf_file, docx_file, pasta_imagens=None):
    """
    Converte PDF para DOCX com opções avançadas
    
    Args:
        pdf_file: Caminho do arquivo PDF
        docx_file: Caminho do arquivo DOCX de saída
        pasta_imagens: Pasta para salvar as imagens extraídas (opcional)
    """
    # Criar pasta de imagens se especificada
    if pasta_imagens and not os.path.exists(pasta_imagens):
        os.makedirs(pasta_imagens)
    
    # Configurações da conversão
    config = {
        'connected_border': True,  # Conecta bordas de tabelas
        'debug': False,  # Modo debug
        'min_section_height': 20,  # Altura mínima para considerar uma seção
        'delete_end_line_hyphen': False,  # Remove hifenização no final das linhas
        'multi_processing': True,  # Usa multiprocessamento para maior velocidade
    }
    
    # Se definida pasta de imagens, configura extração
    if pasta_imagens:
        config['image_dir'] = pasta_imagens
        config['extract_image'] = True
    
    # Criar o conversor
    cv = Converter(pdf_file)

    
    try:
        # Realizar a conversão com as configurações
        # cv.convert(docx_file, start=0, end=None, pages_config=config)
        cv.convert(docx_file, start=0, delete_end_line_hyphen=True)
        print(f"Conversão concluída: {pdf_file} -> {docx_file}")
        
        if pasta_imagens:
            print(f"Imagens extraídas para: {pasta_imagens}")
            
    except Exception as e:
        print(f"Erro durante a conversão: {str(e)}")
    
    finally:
        cv.close()

# Exemplo de uso
if __name__ == "__main__":
    pdf_file = 'original.pdf'
    docx_file = 'original.docx'
    pasta_imagens = 'img'
    
    converter_pdf_com_opcoes(pdf_file, docx_file, pasta_imagens)