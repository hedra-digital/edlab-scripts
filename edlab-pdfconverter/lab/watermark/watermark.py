import argparse
from PyPDF2 import PdfReader, PdfWriter
import io
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
from reportlab.lib.pagesizes import letter

def create_watermark(text="WATERMARK"):
    """Cria uma marca d'água em um PDF temporário"""
    # Criar um buffer de memória para o PDF
    packet = io.BytesIO()
    
    # Criar um novo PDF com ReportLab
    can = canvas.Canvas(packet, pagesize=letter)
    
    # Definir a cor cinza clara (RGB: 0.8, 0.8, 0.8, alpha: 0.3)
    light_gray = Color(0.8, 0.8, 0.8, alpha=0.3)
    can.setFillColor(light_gray)
    
    # Definir fonte e tamanho
    can.setFont("Helvetica", 60)
    
    # Rotacionar e posicionar o texto
    can.saveState()
    can.translate(300, 400)
    can.rotate(45)
    can.drawCentredString(0, 0, text)
    can.restoreState()
    
    can.save()
    
    # Mover para o início do buffer
    packet.seek(0)
    return PdfReader(packet)

def add_watermark(input_path, output_path, watermark_text="WATERMARK"):
    """Adiciona marca d'água a todas as páginas do PDF"""
    # Criar a marca d'água
    watermark = create_watermark(watermark_text)
    watermark_page = watermark.pages[0]
    
    # Abrir o PDF original
    reader = PdfReader(input_path)
    writer = PdfWriter()
    
    # Adicionar marca d'água em cada página
    for page in reader.pages:
        page.merge_page(watermark_page)
        writer.add_page(page)
    
    # Salvar o PDF resultante
    with open(output_path, 'wb') as output_file:
        writer.write(output_file)

def main():
    # Configurar o parser de argumentos
    parser = argparse.ArgumentParser(description='Adiciona marca d\'água em um PDF')
    parser.add_argument('-i', '--input', required=True, help='Arquivo PDF de entrada')
    parser.add_argument('--watermark', nargs='?', const='WATERMARK', 
                       default='WATERMARK', help='Texto da marca d\'água')
    
    args = parser.parse_args()
    
    # Gerar nome do arquivo de saída
    output_path = args.input.rsplit('.', 1)[0] + '_watermark.pdf'
    
    try:
        add_watermark(args.input, output_path, args.watermark)
        print(f"Marca d'água adicionada com sucesso! Arquivo salvo como: {output_path}")
    except Exception as e:
        print(f"Erro ao processar o PDF: {str(e)}")

if __name__ == "__main__":
    main()