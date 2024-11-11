from PyPDF2 import PdfReader, PdfWriter

def remove_links_from_pdf(input_path, output_path):
    """
    Remove todos os hiperlinks de um arquivo PDF mantendo o texto original.
    
    Args:
        input_path (str): Caminho do arquivo PDF de entrada
        output_path (str): Caminho onde será salvo o PDF sem links
    """
    # Abre o PDF original
    reader = PdfReader(input_path)
    writer = PdfWriter()

    # Processa cada página
    for page in reader.pages:
        # Remove as anotações de links (mantendo o texto)
        if '/Annots' in page:
            annotations = page['/Annots']
            # Filtra apenas as anotações que não são links
            new_annotations = [ann for ann in annotations if ann.get_object()['/Subtype'] != '/Link']
            if new_annotations:
                page['/Annots'] = new_annotations
            else:
                del page['/Annots']
        
        # Adiciona a página modificada ao novo PDF
        writer.add_page(page)

    # Salva o novo PDF
    with open(output_path, 'wb') as output_file:
        writer.write(output_file)

# Exemplo de uso
if __name__ == "__main__":
    input_file = "links.pdf"
    output_file = "sem_links.pdf"
    remove_links_from_pdf(input_file, output_file)