import argparse
import os
import subprocess
from pathlib import Path

def compress_pdf(input_file, resolution=150):
    """
    Comprime um arquivo PDF usando Ghostscript.
    A resolução fornecida será usada diretamente para as imagens.
    
    Args:
        input_file (str): Caminho do arquivo PDF de entrada
        resolution (int): Resolução das imagens em DPI
    """
    if not os.path.exists(input_file):
        print(f"Erro: O arquivo {input_file} não foi encontrado.")
        return

    if not input_file.lower().endswith('.pdf'):
        print("Erro: O arquivo deve ser um PDF.")
        return

    try:
        output_file = str(Path(input_file).with_suffix('')) + '_compressed.pdf'
        
        gs_command = [
            'gs',
            '-sDEVICE=pdfwrite',
            '-dCompatibilityLevel=1.4',
            '-dPDFSETTINGS=/printer',
            '-dNOPAUSE',
            '-dQUIET',
            '-dBATCH',
            '-dColorImageDownsampleType=/Bicubic',
            f'-dColorImageResolution={resolution}',
            '-dGrayImageDownsampleType=/Bicubic',
            f'-dGrayImageResolution={resolution}',
            '-dMonoImageDownsampleType=/Bicubic',
            f'-dMonoImageResolution={resolution}',
            f'-sOutputFile={output_file}',
            input_file
        ]

        # Executa o Ghostscript
        result = subprocess.run(gs_command, capture_output=True, text=True)
        
        # Se houver warnings relevantes, mostra-os
        for line in result.stderr.split('\n'):
            if line and not "Object streams" in line and not "XRef stream" in line:
                print(line)

        # Calcula e mostra a redução alcançada
        original_size = os.path.getsize(input_file)
        compressed_size = os.path.getsize(output_file)
        reduction = (1 - compressed_size/original_size) * 100

        print(f"\nArquivo comprimido salvo como: {output_file}")
        print(f"Tamanho original: {original_size/1024:.2f} KB")
        print(f"Tamanho comprimido: {compressed_size/1024:.2f} KB")
        print(f"Redução alcançada: {reduction:.1f}%")
        print(f"Resolução usada: {resolution} DPI")

    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar Ghostscript: {str(e)}")
    except Exception as e:
        print(f"Erro ao processar o PDF: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Comprime um arquivo PDF')
    parser.add_argument('-i', '--input', required=True, help='Arquivo PDF de entrada')
    parser.add_argument('--shrink', type=int, nargs='?', const=150, default=150,
                      help='Resolução das imagens em DPI (padrão: 150)')
    
    args = parser.parse_args()
    
    # Validação da resolução (mínimo de 72 DPI, máximo de 300 DPI)
    if args.shrink < 72 or args.shrink > 300:
        print("Erro: A resolução deve estar entre 72 e 300 DPI")
        return
        
    compress_pdf(args.input, args.shrink)

if __name__ == "__main__":
    main()