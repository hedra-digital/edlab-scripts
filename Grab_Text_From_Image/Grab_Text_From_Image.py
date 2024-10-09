import os
import sys
import argparse
from PIL import Image
import pytesseract

# Configuração do argparse para aceitar argumentos de linha de comando
parser = argparse.ArgumentParser(description="Extrai texto de arquivos .jpg em um diretório.")
parser.add_argument('image_directory', type=str, help="O diretório que contém as imagens .jpg.")
parser.add_argument('-o', '--output', type=str, default='text_output.md', 
                    help="Nome do arquivo de saída. Se não for especificado, será 'text_output.md'.")

# Parse os argumentos da linha de comando
args = parser.parse_args()

# Diretório das imagens e nome do arquivo de saída a partir dos argumentos
image_directory = args.image_directory
output_file = args.output

# Verificar se o diretório existe
if not os.path.isdir(image_directory):
    print(f"Erro: O diretório {image_directory} não existe.")
    sys.exit(1)

# Abra o arquivo para escrever o texto extraído
with open(output_file, 'w') as f:
    # Para cada arquivo no diretório que termina com .jpg
    for filename in os.listdir(image_directory):
        if filename.endswith('.jpg'):
            # Caminho completo do arquivo
            file_path = os.path.join(image_directory, filename)
            
            # Abrir a imagem
            img = Image.open(file_path)
            
            # Usar o Tesseract para extrair o texto
            text = pytesseract.image_to_string(img)
            
            # Escrever o nome do arquivo e o texto extraído no arquivo de saída
            f.write(f"## {filename}\n\n")
            f.write(f"{text}\n\n")

print(f"Texto extraído com sucesso e salvo em {output_file}")
