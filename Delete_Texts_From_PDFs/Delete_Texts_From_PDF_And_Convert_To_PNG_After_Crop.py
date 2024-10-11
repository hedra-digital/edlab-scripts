#!/usr/bin/env python3

import argparse
import subprocess
import os
import logging
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path

# Configuração do logging para depuração
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def delete_text_from_pdf(input_pdf, output_pdf):
    """Remove o texto de um PDF mantendo as imagens usando Ghostscript."""
    gs_command = [
        "gs",
        "-sDEVICE=pdfwrite",
        "-dFILTERTEXT",
        "-o", output_pdf,
        "-f", input_pdf
    ]

    logging.info(f"Executando o comando Ghostscript para remover texto: {' '.join(gs_command)}")

    # Executa o comando Ghostscript
    try:
        subprocess.run(gs_command, check=True)
        logging.info(f"PDF sem texto gerado com sucesso: {output_pdf}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Erro ao executar Ghostscript: {e}")

def crop_pdf_with_pdfcrop(input_pdf, output_pdf, margins):
    """Usa pdfcrop para cortar as margens do PDF."""
    pdfcrop_command = ['pdfcrop', '--margins', margins, input_pdf, output_pdf]

    logging.info(f"Executando pdfcrop para cortar o PDF: {' '.join(pdfcrop_command)}")

    try:
        subprocess.run(pdfcrop_command, check=True)
        logging.info(f"PDF cortado com sucesso: {output_pdf}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Erro ao executar pdfcrop: {e}")

def convert_pdf_to_images(input_pdf, output_dir, page_range=None):
    """Converte páginas específicas de um PDF em imagens PNG e salva no diretório especificado."""
    logging.info(f"Convertendo {input_pdf} para imagens PNG no diretório {output_dir}")

    # Converte o PDF em imagens PNG
    try:
        if page_range:
            # Define as páginas a serem convertidas
            images = convert_from_path(input_pdf, first_page=page_range[0], last_page=page_range[1])
        else:
            images = convert_from_path(input_pdf)

        image_paths = []
        num_pages = len(images)
        num_digits = len(str(num_pages))  # Exemplo: para 100 páginas, precisamos de 3 dígitos

        # Garante que o diretório de saída existe
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logging.info(f"Diretório criado: {output_dir}")

        for i, image in enumerate(images):
            # Formata o número da página com zeros à esquerda
            page_num_str = str(i + 1).zfill(num_digits)
            image_path = os.path.join(output_dir, f'page_{page_num_str}.png')
            image.save(image_path, 'PNG')
            image_paths.append(image_path)
            logging.info(f"Página {i+1} salva como imagem: {image_path}")

        logging.info(f"Todas as páginas foram convertidas e salvas no diretório {output_dir}")
        return image_paths
    except Exception as e:
        logging.error(f"Erro ao converter PDF para imagens: {e}")
        return []

def extract_pages(input_pdf, output_pdf, page_range):
    """Extrai páginas específicas de um PDF e salva em um novo arquivo."""
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    for page_num in range(page_range[0] - 1, page_range[1]):
        writer.add_page(reader.pages[page_num])

    with open(output_pdf, 'wb') as output_file:
        writer.write(output_file)

    logging.info(f"Páginas {page_range[0]}-{page_range[1]} extraídas com sucesso para {output_pdf}")

def parse_page_range(pages):
    """Interpreta a opção de intervalo de páginas e retorna a primeira e última página."""
    if '-' in pages:
        first_page, last_page = map(int, pages.split('-'))
        return first_page, last_page
    else:
        page = int(pages)
        return page, page

def rename_file(old_name, new_name):
    """Renomeia um arquivo."""
    try:
        os.rename(old_name, new_name)
        logging.info(f"Arquivo renomeado de {old_name} para {new_name}")
    except OSError as e:
        logging.error(f"Erro ao renomear arquivo: {e}")

def main():
    # Parser de argumentos
    parser = argparse.ArgumentParser(description="Remove o texto de um PDF, corta margens, e/ou converte páginas específicas em imagens PNG.")
    
    # Argumentos de entrada e saída
    parser.add_argument("-i", "--input", required=True, help="Caminho para o arquivo PDF de entrada.")
    parser.add_argument("-o", "--output", required=True, help="Caminho para o arquivo PDF de saída após a remoção do texto.")
    parser.add_argument("-m", "--margins", help="Margens para o corte com pdfcrop. Use um valor ou quatro valores para margens separadas (esquerda, direita, cima, baixo).")
    parser.add_argument("-d", "--dir", help="Diretório onde as imagens PNG serão salvas (uma imagem por página).")
    parser.add_argument("-p", "--pages", help="Intervalo de páginas para processar (remover texto, cortar margens e converter em imagens), por exemplo '1-3' ou '1'.")

    # Parseia os argumentos
    args = parser.parse_args()

    page_range = None
    if args.pages:
        page_range = parse_page_range(args.pages)

    # Extrai páginas específicas, se a opção -p estiver definida
    temp_pdf = "temp_extracted.pdf"
    if page_range:
        extract_pages(args.input, temp_pdf, page_range)
        input_pdf = temp_pdf
    else:
        input_pdf = args.input

    # Remove o texto do PDF e gera o PDF sem texto
    delete_text_from_pdf(input_pdf, args.output)

    # Aplica o pdfcrop para cortar as margens do PDF final, apenas se a opção -m estiver definida
    if args.margins:
        cropped_output = args.output.replace(".pdf", "_cropped.pdf")
        crop_pdf_with_pdfcrop(args.output, cropped_output, args.margins)
        # Renomeia o PDF cortado de volta para output.pdf
        rename_file(cropped_output, args.output)

    # Se o diretório de saída para as imagens for fornecido, converte o PDF (com ou sem corte) para imagens PNG
    if args.dir:
        convert_pdf_to_images(args.output, args.dir, page_range)

if __name__ == "__main__":
    main()
