#!/usr/bin/env python3

# Bibliotecas padrão
import argparse
import logging
import os
import re
import subprocess
from datetime import datetime
from io import StringIO, BytesIO
from pdf2docx import Converter

# Bibliotecas de terceiros
import fitz
import numpy as np
import PIL.Image
from PIL import Image
from pdf2image import convert_from_path
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.colors import Color
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from tqdm import tqdm

# Configuração do logging para depuração
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_pdf_to_docx(pdf_files):
    """
    Converte PDFs para formato DOCX.
    """
    if not pdf_files:
        logging.error("Nenhum arquivo PDF válido encontrado para conversão")
        return

    with tqdm(total=len(pdf_files), desc="Arquivos processados") as file_pbar:
        for input_file in pdf_files:
            try:
                output_file = generate_output_filename(input_file, "docx", ".docx")
                file_pbar.write(f"\nProcessando: {os.path.basename(input_file)}")
                
                # Criar pasta de imagens se não existir
                img_dir = os.path.join(os.path.dirname(output_file), "img_docx")
                if not os.path.exists(img_dir):
                    os.makedirs(img_dir)
                
                # Criar o conversor e realizar a conversão
                cv = Converter(input_file)
                try:
                    cv.convert(
                        output_file,
                        start=0,
                        delete_end_line_hyphen=True
                    )
                    file_pbar.write(f"✓ Concluído: {os.path.basename(output_file)}\n")
                except Exception as e:
                    file_pbar.write(f"Erro na conversão: {str(e)}")
                finally:
                    cv.close()
                
                file_pbar.update(1)
                
            except Exception as e:
                file_pbar.write(f"Erro ao processar {input_file}: {str(e)}")

def process_pdf_to_black(pdf_files):
    """
    Converte PDFs para preto chapado.
    """
    if not pdf_files:
        logging.error("Nenhum arquivo PDF válido encontrado para conversão")
        return

    with tqdm(total=len(pdf_files), desc="Arquivos processados") as file_pbar:
        for input_file in pdf_files:
            try:
                output_file = generate_output_filename(input_file, "black")
                file_pbar.write(f"\nProcessando: {os.path.basename(input_file)}")

                # Converte o PDF em uma lista de imagens
                pages = convert_from_path(input_file)
                
                # Barra de progresso para as páginas
                with tqdm(total=len(pages), desc="Convertendo páginas", position=1, leave=False) as page_pbar:
                    solid_black_pages = []
                    for page in pages:
                        # Converte para array numpy para manipulação
                        img_array = np.array(page)
                        
                        # Identifica pixels brancos
                        white_pixels = np.all(img_array == [255, 255, 255], axis=-1)
                        
                        # Cria imagem em preto e branco
                        solid_black = np.zeros_like(img_array[..., 0], dtype=np.uint8)
                        solid_black[white_pixels] = 255
                        
                        # Converte para imagem PIL e modo binário
                        solid_black_img = Image.fromarray(solid_black)
                        solid_black_img = solid_black_img.convert('1')
                        
                        solid_black_pages.append(solid_black_img)
                        page_pbar.update(1)
                
                # Salva o PDF
                solid_black_pages[0].save(
                    output_file,
                    'PDF',
                    save_all=True,
                    append_images=solid_black_pages[1:],
                    resolution=300.0
                )
                
                file_pbar.write(f"✓ Concluído: {os.path.basename(output_file)}\n")
                file_pbar.update(1)
                
            except Exception as e:
                file_pbar.write(f"Erro ao processar {input_file}: {str(e)}")

def process_pdf_to_gray(pdf_files):
    """
    Converte PDFs para escala de cinza.
    """
    if not pdf_files:
        logging.error("Nenhum arquivo PDF válido encontrado para conversão")
        return

    with tqdm(total=len(pdf_files), desc="Arquivos processados") as file_pbar:
        for input_file in pdf_files:
            try:
                output_file = generate_output_filename(input_file, "gray")
                file_pbar.write(f"\nProcessando: {os.path.basename(input_file)}")

                # Converte o PDF em uma lista de imagens
                pages = convert_from_path(input_file)
                
                # Barra de progresso para as páginas
                with tqdm(total=len(pages), desc="Convertendo páginas", position=1, leave=False) as page_pbar:
                    gray_pages = []
                    for page in pages:
                        # Converte para escala de cinza
                        gray_page = page.convert('L')
                        gray_pages.append(gray_page)
                        page_pbar.update(1)
                
                # Salva o PDF
                gray_pages[0].save(
                    output_file,
                    'PDF',
                    save_all=True,
                    append_images=gray_pages[1:]
                )
                
                file_pbar.write(f"✓ Concluído: {os.path.basename(output_file)}\n")
                file_pbar.update(1)
                
            except Exception as e:
                file_pbar.write(f"Erro ao processar {input_file}: {str(e)}")

def process_pdf_shrinking(pdf_files, resolution=150):
    """
    Processa a compressão de um ou mais arquivos PDF.
    
    Args:
        pdf_files (list): Lista de caminhos dos arquivos PDF
        resolution (int): Resolução das imagens em DPI
    """
    if not pdf_files:
        logging.error("Nenhum arquivo PDF válido encontrado para compressão")
        return
        
    for input_file in pdf_files:
        try:
            output_file = generate_output_filename(input_file, "compressed")
            
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

            logging.info(f"Comprimindo arquivo: {input_file}")
            result = subprocess.run(gs_command, capture_output=True, text=True)
            
            # Processa warnings relevantes
            for line in result.stderr.split('\n'):
                if line and not "Object streams" in line and not "XRef stream" in line:
                    logging.warning(line)

            # Calcula e mostra a redução alcançada
            original_size = os.path.getsize(input_file)
            compressed_size = os.path.getsize(output_file)
            reduction = (1 - compressed_size/original_size) * 100

            logging.info(f"\nCompressão concluída para: {input_file}")
            logging.info(f"Arquivo comprimido salvo como: {output_file}")
            logging.info(f"Tamanho original: {original_size/1024:.2f} KB")
            logging.info(f"Tamanho comprimido: {compressed_size/1024:.2f} KB")
            logging.info(f"Redução alcançada: {reduction:.1f}%")
            
        except subprocess.CalledProcessError as e:
            logging.error(f"Erro ao executar Ghostscript em {input_file}: {str(e)}")
        except Exception as e:
            logging.error(f"Erro ao processar o arquivo {input_file}: {str(e)}")

def analyze_pdf_colors(pdf_path: str) -> dict:
    """Analisa cores em um PDF."""
    doc = fitz.open(pdf_path)
    results = {
        'is_color': False,
        'pages_info': [],
        'color_coverage': 0
    }
    
    total_pixels = 0
    color_pixels = 0
    
    for page_num in tqdm(range(doc.page_count), desc="Analisando páginas"):
        page = doc[page_num]
        pix = page.get_pixmap()
        img_data = pix.samples
        image = PIL.Image.frombytes("RGB", [pix.width, pix.height], img_data)
        
        pixels = np.array(image)
        is_gray = np.all(pixels[:,:,0] == pixels[:,:,1]) & np.all(pixels[:,:,1] == pixels[:,:,2])
        page_color_pixels = np.sum(~is_gray)
        page_total_pixels = pixels.shape[0] * pixels.shape[1]
        
        if page_color_pixels > 0:
            coverage = (page_color_pixels / page_total_pixels) * 100
            results['pages_info'].append({
                'number': page_num + 1,
                'has_color': True,
                'coverage': coverage
            })
            results['is_color'] = True
        else:
            results['pages_info'].append({
                'number': page_num + 1,
                'has_color': False,
                'coverage': 0
            })
        
        total_pixels += page_total_pixels
        color_pixels += page_color_pixels
    
    results['color_coverage'] = (color_pixels / total_pixels) * 100 if total_pixels > 0 else 0
    return results


def create_watermark(text="WATERMARK"):
    """Cria uma marca d'água em um PDF temporário"""
    # Criar um buffer de memória para o PDF
    packet = BytesIO()
    
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
    
    logging.info(f"Marca d'água adicionada com sucesso em: {output_path}")



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

def convert_pdf_to_images(input_pdf, output_dir, format='jpeg', page_range=None):
    """Converte páginas específicas de um PDF em imagens no formato especificado e salva no diretório."""
    logging.info(f"Convertendo {input_pdf} para imagens {format} no diretório {output_dir}")

    # Converte o PDF em imagens
    try:
        if page_range:
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
            image_path = os.path.join(output_dir, f'page_{page_num_str}.{format}')
            image.save(image_path, format.upper())
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
        return True
    except OSError as e:
        logging.error(f"Erro ao renomear arquivo: {e}")
        return False

def copy_file(source, destination):
    """Copia um arquivo mantendo o original."""
    try:
        import shutil
        shutil.copy2(source, destination)
        logging.info(f"Arquivo copiado de {source} para {destination}")
    except OSError as e:
        logging.error(f"Erro ao copiar arquivo: {e}")

def generate_output_filename(input_path, suffix=""):
    """
    Gera um nome de arquivo de saída baseado no arquivo de entrada.
    Adiciona um sufixo antes da extensão se fornecido.
    
    Args:
        input_path: Caminho do arquivo de entrada
        suffix: Sufixo a ser adicionado antes da extensão
    """
    directory = os.path.dirname(os.path.abspath(input_path))
    filename = os.path.basename(input_path)
    name, ext = os.path.splitext(filename)
    
    if suffix:
        new_name = f"{name}_{suffix}{ext}"
    else:
        new_name = f"{name}_modified{ext}"
    
    return os.path.join(directory, new_name)
    
def find_pdf_files(input_paths):
    """
    Encontra arquivos PDF baseado nos caminhos de entrada.
    Suporta arquivo único, wildcards e diretórios.
    
    Args:
        input_paths: Lista de caminhos ou padrões
        
    Returns:
        Lista de caminhos de arquivos PDF encontrados
    """

    import glob
    
    pdf_files = []
    # Obtém o diretório de trabalho atual
    current_dir = os.getcwd()
    
    for input_path in input_paths:
        if isinstance(input_path, str) and input_path.upper() == "BLANK":
            pdf_files.append("BLANK")
            continue
            
        # Converte para caminho absoluto se for caminho relativo
        abs_path = os.path.abspath(os.path.join(current_dir, input_path))
            
        if os.path.isdir(abs_path):
            # Se for um diretório, procura todos os PDFs nele
            pdf_files.extend(sorted(glob.glob(os.path.join(abs_path, "*.pdf"))))
        elif '*' in input_path:
            # Para wildcards, primeiro converte o diretório base para absoluto
            base_dir = os.path.dirname(abs_path)
            pattern = os.path.basename(input_path)
            full_pattern = os.path.join(base_dir, pattern)
            pdf_files.extend(sorted(glob.glob(full_pattern)))
        elif os.path.isfile(abs_path):
            # Se for um arquivo único, adiciona se for PDF
            if abs_path.lower().endswith('.pdf'):
                pdf_files.append(abs_path)
        else:
            logging.warning(f"Caminho inválido ou arquivo não encontrado: {input_path}")
    
    # Remove duplicatas mantendo a ordem
    return list(dict.fromkeys(pdf_files))
    
    # Remove duplicatas mantendo a ordem
    return list(dict.fromkeys(pdf_files))

def merge_pdfs(input_files, output_file):
    """
    Junta múltiplos arquivos PDF em um único arquivo.
    
    Args:
        input_files: Lista de caminhos dos arquivos PDF a serem unidos
        output_file: Caminho do arquivo PDF de saída
    """
    merger = PdfWriter()
    
    try:
        # Verifica se todos os arquivos existem e são PDFs
        for pdf_file in input_files:
            if not os.path.exists(pdf_file):
                raise FileNotFoundError(f"Arquivo não encontrado: {pdf_file}")
            if not pdf_file.lower().endswith('.pdf'):
                raise ValueError(f"Arquivo não é um PDF: {pdf_file}")
        
        # Adiciona cada PDF ao merger
        for pdf_file in input_files:
            logging.info(f"Adicionando arquivo: {pdf_file}")
            reader = PdfReader(pdf_file)
            merger.append(reader)
        
        # Salva o PDF unificado
        with open(output_file, 'wb') as output:
            merger.write(output)
        
        logging.info(f"PDFs unidos com sucesso em: {output_file}")
        return True
        
    except Exception as e:
        logging.error(f"Erro ao unir PDFs: {str(e)}")
        return False


def get_pdf_sequence_info(input_sequence):
    """
    Analisa a sequência de entrada e retorna informações sobre os PDFs.
    
    Args:
        input_sequence: Lista de arquivos PDF e BLANKs
    
    Returns:
        dict: Informações sobre a sequência, incluindo tamanho padrão das páginas
    """
    pdf_info = {
        'page_size': None,
        'pdf_files': [],
        'total_pdfs': 0
    }
    
    # Primeiro, coleta todos os arquivos PDF válidos
    for item in input_sequence:
        if item.lower().endswith('.pdf'):
            if os.path.exists(item):
                pdf_info['pdf_files'].append(item)
                # Pega o tamanho do primeiro PDF encontrado
                if pdf_info['page_size'] is None:
                    try:
                        reader = PdfReader(item)
                        if len(reader.pages) > 0:
                            page = reader.pages[0]
                            pdf_info['page_size'] = (
                                float(page.mediabox.width),
                                float(page.mediabox.height)
                            )
                            logging.info(f"Tamanho padrão de página definido: {pdf_info['page_size']}")
                    except Exception as e:
                        logging.warning(f"Erro ao ler tamanho do PDF {item}: {e}")
    
    pdf_info['total_pdfs'] = len(pdf_info['pdf_files'])
    
    # Se não conseguiu determinar o tamanho, usa A4 como padrão
    if pdf_info['page_size'] is None:
        pdf_info['page_size'] = (595, 842)  # A4 em pontos
        logging.info("Usando tamanho A4 padrão para páginas em branco")
    
    return pdf_info

def merge_pdfs_with_blanks(input_sequence, output_file):
    """
    Junta PDFs inserindo páginas em branco onde especificado.
    Usa um tamanho consistente para todas as páginas em branco.
    """
    merger = PdfWriter()
    pdfs_added = 0
    
    try:
        # Obtém informações sobre a sequência de PDFs
        sequence_info = get_pdf_sequence_info(input_sequence)
        
        if sequence_info['total_pdfs'] < 2:
            raise ValueError("São necessários pelo menos 2 arquivos PDF para juntar")
        
        # Usa o mesmo tamanho para todas as páginas em branco
        blank_page_size = sequence_info['page_size']
        logging.info(f"Usando tamanho consistente para páginas em branco: {blank_page_size}")
        
        # Cria uma única página em branco que será reutilizada
        blank_page = create_blank_page(blank_page_size)
        
        for item in input_sequence:
            if item.lower() == "blank":
                logging.info(f"Adicionando página em branco (tamanho: {blank_page_size[0]}x{blank_page_size[1]} pontos)")
                merger.append(blank_page)
                
            elif item.lower().endswith('.pdf'):
                if os.path.exists(item):
                    logging.info(f"Adicionando arquivo: {item}")
                    reader = PdfReader(item)
                    merger.append(reader)
                    pdfs_added += 1
                    
                    if pdfs_added == sequence_info['total_pdfs']:
                        logging.info("Todos os PDFs foram processados")
        
        # Salva o PDF final
        with open(output_file, 'wb') as output:
            merger.write(output)
        
        logging.info(f"PDFs unidos com sucesso em: {output_file}")
        return True
        
    except Exception as e:
        logging.error(f"Erro ao unir PDFs: {str(e)}")
        return False



def get_page_size(pdf_path):
    """
    Obtém o tamanho da primeira página de um PDF.
    
    Args:
        pdf_path: Caminho do arquivo PDF
    
    Returns:
        tuple: (width, height) em pontos ou None se não conseguir obter
    """
    try:
        reader = PdfReader(pdf_path)
        if len(reader.pages) > 0:
            page = reader.pages[0]
            return (float(page.mediabox.width), float(page.mediabox.height))
    except Exception as e:
        logging.warning(f"Erro ao obter tamanho da página de {pdf_path}: {e}")
    return None

def create_blank_page(size=(595, 842)):
    """
    Cria uma página em branco com o tamanho especificado.
    
    Args:
        size: Tupla (width, height) em pontos
    
    Returns:
        PdfReader contendo uma única página em branco
    """
    from reportlab.pdfgen import canvas
    from io import BytesIO
    
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=size)
    c.showPage()
    c.save()
    
    # Converte o buffer em um PdfReader
    buffer.seek(0)
    return PdfReader(buffer)
def find_pdf_files(input_paths):
    """
    Encontra arquivos PDF baseado nos caminhos de entrada.
    Suporta arquivo único, wildcards e diretórios.
    
    Args:
        input_paths: Lista de caminhos ou padrões
        
    Returns:
        Lista de caminhos de arquivos PDF encontrados
    """
    import glob
    
    pdf_files = []
    
    for input_path in input_paths:
        if isinstance(input_path, str) and input_path.upper() == "BLANK":
            pdf_files.append("BLANK")
            continue
            
        if os.path.isdir(input_path):
            # Se for um diretório, procura todos os PDFs nele
            pdf_files.extend(sorted(glob.glob(os.path.join(input_path, "*.pdf"))))
        elif '*' in input_path:
            # Se contiver wildcard, usa glob diretamente
            pdf_files.extend(sorted(glob.glob(input_path)))
        elif os.path.isfile(input_path):
            # Se for um arquivo único, adiciona se for PDF
            if input_path.lower().endswith('.pdf'):
                pdf_files.append(input_path)
        else:
            logging.warning(f"Caminho inválido ou arquivo não encontrado: {input_path}")
    
    # Remove duplicatas mantendo a ordem
    return list(dict.fromkeys(pdf_files))

def count_pdf_pages(pdf_files):
    """
    Conta o número de páginas em cada arquivo PDF.
    
    Args:
        pdf_files: Lista de caminhos de arquivos PDF
        
    Returns:
        dict: Dicionário com informações sobre contagem de páginas
    """
    results = {
        'files': [],
        'total_pages': 0,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'error_files': []
    }
    
    for pdf_file in pdf_files:
        try:
            reader = PdfReader(pdf_file)
            num_pages = len(reader.pages)
            results['files'].append({
                'file': pdf_file,
                'pages': num_pages,
                'size': os.path.getsize(pdf_file) / (1024 * 1024)  # Tamanho em MB
            })
            results['total_pages'] += num_pages
            logging.info(f"Contadas {num_pages} páginas em: {pdf_file}")
        except Exception as e:
            logging.error(f"Erro ao processar {pdf_file}: {str(e)}")
            results['error_files'].append({
                'file': pdf_file,
                'error': str(e)
            })
    
    return results

def save_page_count_report(results, output_file="PAGES.txt"):
    """
    Salva o relatório simplificado de contagem de páginas em um arquivo texto,
    usando tab como separador entre colunas.
    
    Args:
        results: Dicionário com resultados da contagem
        output_file: Nome do arquivo de saída
    """
    try:
        # Converte o nome do arquivo de saída para caminho absoluto
        current_dir = os.getcwd()
        output_path = os.path.abspath(os.path.join(current_dir, output_file))
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # Cabeçalho com tab
            f.write(f"Nome do arquivo\tPáginas\n")
            
            # Lista de arquivos e páginas
            for file_info in results['files']:
                filename = os.path.basename(file_info['file'])  # Pega só o nome do arquivo, sem o caminho
                f.write(f"{filename}\t{file_info['pages']}\n")
            
        logging.info(f"Relatório de contagem salvo em: {output_path}")
    except Exception as e:
        logging.error(f"Erro ao salvar relatório: {str(e)}")
        raise
        
def remove_hyphenation(text):
    """
    Remove hifenizações do texto mantendo quebras de linha legítimas.
    
    Args:
        text: Texto extraído do PDF
        
    Returns:
        str: Texto sem hifenizações
    """
    # Padrão para encontrar palavras hifenizadas no final da linha
    pattern = r'(\w+)-\n(\w+)'
    
    # Função para processar cada match e decidir se deve juntar as palavras
    def process_hyphen(match):
        part1, part2 = match.groups()
        combined = part1 + part2
        
        # Verifica se a palavra combinada existe (implementação simplificada)
        # Você pode adicionar um dicionário mais completo ou outras regras aqui
        if len(combined) >= 4:  # Heurística simples: palavras maiores que 4 letras
            return combined + '\n'
        else:
            return f"{part1}-\n{part2}"  # Mantém a hifenização original
    
    # Aplica a remoção de hifenização
    dehyphenated = re.sub(pattern, process_hyphen, text)
    
    return dehyphenated

def extract_text_from_pdf(input_pdf, output_file=None):
    """
    Extrai texto de um PDF e remove hifenizações.
    
    Args:
        input_pdf: Caminho do arquivo PDF de entrada
        output_file: Caminho do arquivo de saída (opcional)
    
    Returns:
        str: Caminho do arquivo de saída
    """
    try:
        # Configura parâmetros de extração
        laparams = LAParams(
            line_overlap=0.5,
            char_margin=2.0,
            line_margin=0.5,
            word_margin=0.1,
            boxes_flow=0.5,
            detect_vertical=False,
            all_texts=True
        )
        
        # Extrai o texto para um buffer
        output_buffer = StringIO()
        with open(input_pdf, 'rb') as fin:
            extract_text_to_fp(fin, output_buffer, laparams=laparams)
        
        # Obtém o texto e remove hifenizações
        text = output_buffer.getvalue()
        dehyphenated_text = remove_hyphenation(text)
        
        # Gera nome do arquivo de saída se não especificado
        if output_file is None:
            output_file = generate_output_filename(input_pdf, "extracted_text", ".txt")
        
        # Salva o texto processado
        with open(output_file, 'w', encoding='utf-8') as fout:
            fout.write(dehyphenated_text)
        
        logging.info(f"Texto extraído e processado salvo em: {output_file}")
        return output_file
        
    except Exception as e:
        logging.error(f"Erro ao extrair texto do PDF: {str(e)}")
        raise

# Modifique a função generate_output_filename para aceitar extensão personalizada:

def generate_output_filename(input_path, suffix="", ext=None):
    """
    Gera um nome de arquivo de saída baseado no arquivo de entrada.
    
    Args:
        input_path: Caminho do arquivo de entrada
        suffix: Sufixo a ser adicionado antes da extensão
        ext: Extensão personalizada (opcional)
    """
    directory = os.path.dirname(os.path.abspath(input_path))
    filename = os.path.basename(input_path)
    name, original_ext = os.path.splitext(filename)
    
    # Use a extensão fornecida ou mantenha a original
    final_ext = ext if ext is not None else original_ext
    
    if suffix:
        new_name = f"{name}_{suffix}{final_ext}"
    else:
        new_name = f"{name}_modified{final_ext}"
    
    return os.path.join(directory, new_name)

def process_color_analysis(pdf_files):
    """Processa a análise de cores dos PDFs."""
    if not pdf_files:
        logging.error("Nenhum arquivo PDF válido encontrado para análise de cores")
        return
    
    for pdf_file in pdf_files:
        try:
            results = analyze_pdf_colors(pdf_file)
            print(f"\nAnálise de cores: {pdf_file}")
            print("-" * 50)
            print(f"Status: {'Colorido' if results['is_color'] else 'Preto e Branco'}")
            print("\nDetalhes por página:")
            for page in results['pages_info']:
                status = "Colorida" if page['has_color'] else "P&B"
                print(f"Página {page['number']}: {status} (Cobertura: {page['coverage']:.1f}%)")
            print(f"\nCobertura total de cor: {results['color_coverage']:.1f}%")
        except Exception as e:
            logging.error(f"Erro ao analisar cores em {pdf_file}: {str(e)}")

def process_text_extraction(input_files, output_file):
    """Processa a extração de texto dos PDFs."""
    for input_file in [f for f in input_files if f != "BLANK"]:
        try:
            extracted_file = extract_text_from_pdf(input_file, output_file)
            logging.info(f"Texto extraído com sucesso de {input_file} para {extracted_file}")
        except Exception as e:
            logging.error(f"Erro ao processar {input_file}: {str(e)}")

def process_page_counting(pdf_files):
    """Processa a contagem de páginas dos PDFs."""
    if not pdf_files:
        logging.error("Nenhum arquivo PDF válido encontrado para contagem")
        return
    
    results = count_pdf_pages(pdf_files)
    save_page_count_report(results)

def process_pdf_joining(input_files, output_file, watermark_text=None):
    """Processa a junção de PDFs."""
    has_blank = any(item == "BLANK" for item in input_files)
    
    if has_blank:
        if not merge_pdfs_with_blanks(input_files, output_file):
            logging.error("Falha na operação de junção com páginas em branco")
            return False
    else:
        pdf_files = [f for f in input_files if f != "BLANK"]
        if len(pdf_files) < 2:
            logging.error("São necessários pelo menos 2 arquivos PDF para juntar")
            return False
        
        if not merge_pdfs(pdf_files, output_file):
            logging.error("Falha na operação de junção")
            return False
    
    if watermark_text:
        watermark_output = generate_output_filename(output_file, "watermark")
        add_watermark(output_file, watermark_output, watermark_text)
        os.remove(output_file)
        os.rename(watermark_output, output_file)
    
    return True

def process_single_pdf(input_file, args):
    """Processa operações em um único PDF."""
    if not args.output:
        suffix = []
        if args.pages:
            suffix.append(f"pages_{args.pages.replace('-', 'to')}")
        if args.remove_text:
            suffix.append("notext")
        if args.margins:
            suffix.append("cropped")
        if args.watermark:
            suffix.append("watermark")
        
        suffix_str = "_".join(suffix) if suffix else ""
        args.output = generate_output_filename(input_file, suffix_str)
        logging.info(f"Nome do arquivo de saída gerado automaticamente: {args.output}")

    page_range = parse_page_range(args.pages) if args.pages else None
    
    temp_pdf = "temp_extracted.pdf"
    input_pdf = temp_pdf if page_range else input_file
    
    if page_range:
        extract_pages(input_file, temp_pdf, page_range)

    if args.remove_text:
        delete_text_from_pdf(input_pdf, args.output)
    else:
        copy_file(input_pdf, args.output)

    if args.margins:
        cropped_output = args.output.replace(".pdf", "_cropped.pdf")
        crop_pdf_with_pdfcrop(args.output, cropped_output, args.margins)
        os.remove(args.output)
        rename_file(cropped_output, args.output)

    if args.watermark:
        watermark_output = generate_output_filename(args.output, "watermark")
        add_watermark(args.output, watermark_output, args.watermark)
        os.remove(args.output)
        rename_file(watermark_output, args.output)

    if page_range and os.path.exists(temp_pdf):
        os.remove(temp_pdf)

    if args.dir:
        convert_pdf_to_images(args.output, args.dir, args.format.lower(), page_range)

def main():
    """Função principal do programa."""
    parser = argparse.ArgumentParser(description="Manipulação de arquivos PDF: juntar, remover texto, cortar margens, extrair páginas, converter para imagens e adicionar marca d'água.")
    
    # Configuração dos argumentos
    parser.add_argument("-i", "--input", required=True, nargs='+',
                       help="Arquivo(s) PDF de entrada, diretório(s) ou padrões (*.pdf). Use 'BLANK' para inserir páginas em branco quando usando --join")
    parser.add_argument("-o", "--output", 
                       help="Arquivo de saída para operações em arquivo único ou junção, ou diretório para múltiplos arquivos.")
    parser.add_argument("-m", "--margins", 
                       help="Margens para o corte com pdfcrop. Use um valor ou quatro valores para margens separadas.")
    parser.add_argument("-d", "--dir", 
                       help="Diretório onde as imagens serão salvas.")
    parser.add_argument("-f", "--format", default="jpeg",
                       help="Para ser usado com -d. Define o formato da imagem de saída (jpeg ou png). Padrão: jpeg.")
    parser.add_argument("-p", "--pages", 
                       help="Intervalo de páginas para processar ou extrair (ex: '1-3' ou '1').")
    parser.add_argument("-rt", "--remove-text", action='store_true',
                       help="Remove o texto do PDF antes de cortar margens e converter em imagens.")
    parser.add_argument("-j", "--join", action='store_true',
                       help="Junta múltiplos PDFs em um único arquivo.")
    parser.add_argument("--page-counter", action='store_true',
                       help="Conta o número de páginas dos PDFs e gera relatório em PAGES.txt")
    parser.add_argument("-et", "--extract-text", action='store_true',
                       help="Extrai texto do PDF para um arquivo txt, removendo hifenizações.")
    parser.add_argument("--extract-to-docx", action='store_true',
                       help="Converte PDF para formato DOCX, preservando itálicos.")
    parser.add_argument("-w", "--watermark", nargs='?', const='WATERMARK', 
                       help="Adiciona marca d'água ao PDF. Use sem valor para 'WATERMARK' ou especifique o texto desejado.")
    parser.add_argument("--check-color", action='store_true',
                       help="Analisa se o PDF contém páginas coloridas")
    parser.add_argument("--shrink", type=int, nargs='?', const=150, default=None,
                      help='Comprime PDFs usando a resolução especificada em DPI (72-300, padrão: 150)')
    parser.add_argument("--convert-to-gray", action='store_true',
                       help="Converte PDF para escala de cinza. Curvas serão convertidas em imagem.")
    parser.add_argument("--convert-to-black", action='store_true',
                       help="Converte PDF para preto chapado. Curvas serão convertidas em imagem.")

    args = parser.parse_args()

    try:
        input_files = find_pdf_files(args.input)
        
        if not input_files:
            logging.error("Nenhum arquivo PDF encontrado")
            return

        # Lista de arquivos PDF válidos (excluindo BLANKs)
        valid_pdfs = [f for f in input_files if f != "BLANK"]
        
        # Adicionar nas opções de processamento (logo após as conversões de cores):
        if args.extract_to_docx:
            process_pdf_to_docx(valid_pdfs)
            return
      
        # 1. Processamentos de conversão de cores
        if args.convert_to_black:
            process_pdf_to_black(valid_pdfs)
            return
            
        if args.convert_to_gray:
            process_pdf_to_gray(valid_pdfs)
            return
        
        # 2. Processamento de compressão
        if args.shrink is not None:
            if args.shrink < 72 or args.shrink > 300:
                logging.error("Erro: A resolução deve estar entre 72 e 300 DPI")
                return
            process_pdf_shrinking(valid_pdfs, args.shrink)
            return
        
        # 3. Análises e extrações
        if args.check_color:
            process_color_analysis(valid_pdfs)
            return
            
        if args.page_counter:
            process_page_counting(valid_pdfs)
            return
        
        # 4. Processamento de múltiplos arquivos
        if args.join:
            output_file = args.output
            if not output_file:
                first_pdf = next((f for f in valid_pdfs), None)
                if not first_pdf:
                    logging.error("Nenhum arquivo PDF encontrado na sequência")
                    return
                output_file = generate_output_filename(first_pdf, "merged")
            
            output_file = output_file if output_file.lower().endswith('.pdf') else output_file + '.pdf'
            process_pdf_joining(input_files, output_file, args.watermark)
            return
        
        # 5. Processamento de arquivo único
        input_file = next((f for f in valid_pdfs), None)
        if not input_file:
            logging.error("Nenhum arquivo PDF válido encontrado para processamento")
            return
        
        process_single_pdf(input_file, args)

    except Exception as e:
        logging.error(f"Erro durante o processamento: {str(e)}")
        raise

if __name__ == "__main__":
    main()