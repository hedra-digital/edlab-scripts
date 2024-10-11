#!/usr/bin/env python3

import argparse
import subprocess

def delete_text_from_pdf(input_pdf, output_pdf):
    # Comando para remover o texto usando Ghostscript
    gs_command = [
        "gs",
        "-sDEVICE=pdfwrite",
        "-dFILTERTEXT",
        "-o", output_pdf,
        "-f", input_pdf
    ]

    # Executa o comando Ghostscript
    subprocess.run(gs_command, check=True)

def main():
    # Parser de argumentos
    parser = argparse.ArgumentParser(description="Remove o texto de um PDF mantendo as imagens.")
    
    # Argumentos de entrada e saída
    parser.add_argument("-i", "--input", required=True, help="Caminho para o arquivo PDF de entrada.")
    parser.add_argument("-o", "--output", required=True, help="Caminho para o arquivo PDF de saída.")
    
    # Parseia os argumentos
    args = parser.parse_args()

    # Chama a função para remover o texto do PDF
    delete_text_from_pdf(args.input, args.output)

if __name__ == "__main__":
    main()
