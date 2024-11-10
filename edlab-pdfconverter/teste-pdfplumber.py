#!/usr/bin/env python3

import pdfplumber
import logging
import re
from typing import List, Dict, Tuple
from dataclasses import dataclass

def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

# Funções para extração de parágrafos
def ends_sentence(text: str) -> bool:
    """Verifica se o texto termina com pontuação de fim de frase"""
    return bool(re.search(r'[.!?"]$', text.strip()))

def is_continuation(text: str) -> bool:
    """Verifica se o texto parece ser continuação de uma frase"""
    return text.strip() and text[0].islower()

def is_title(text: str) -> bool:
    """Verifica se é um título"""
    return bool(re.match(r'^\d+\.|\#|Chapter', text.strip()))

def should_start_new_paragraph(current_line: List[Dict], 
                             prev_bottom: float, 
                             prev_text: str,
                             current_text: str) -> bool:
    """Determina se deve começar um novo parágrafo"""
    if not prev_bottom:
        return True
    
    line_start = current_line[0]['x0']
    line_top = current_line[0]['top']
    vertical_gap = line_top - prev_bottom
    
    # Critérios para novo parágrafo
    return any([
        line_start > 50,  # Recuo significativo
        vertical_gap > 12,  # Espaço vertical maior
        ends_sentence(prev_text) and not is_continuation(current_text),  # Quebra lógica
        is_title(current_text),  # É título
        current_text.startswith('—')  # Diálogo
    ])

def extract_paragraphs(page) -> List[str]:
    """Extrai parágrafos mantendo a estrutura correta"""
    # Agrupa caracteres por linha
    lines = {}
    for char in sorted(page.chars, key=lambda x: (x['top'], x['x0'])):
        line_top = round(char['top'])
        if line_top not in lines:
            lines[line_top] = []
        lines[line_top].append(char)
    
    # Processa linhas em parágrafos
    paragraphs = []
    current_paragraph = []
    prev_bottom = None
    prev_text = ""
    
    for top in sorted(lines.keys()):
        line_chars = sorted(lines[top], key=lambda x: x['x0'])
        line_text = ''.join(c['text'] for c in line_chars).strip()
        
        # Ignora linhas de metadados
        if "Clementina_Prova" in line_text or re.match(r'^\d+\s*\|', line_text):
            continue
        
        # Decide se começa novo parágrafo
        if should_start_new_paragraph(line_chars, prev_bottom, prev_text, line_text):
            if current_paragraph:
                paragraphs.append(' '.join(current_paragraph))
                current_paragraph = []
        
        if line_text:
            current_paragraph.append(line_text)
            prev_bottom = max(c['bottom'] for c in line_chars)
            prev_text = line_text
    
    # Adiciona último parágrafo
    if current_paragraph:
        paragraphs.append(' '.join(current_paragraph))
    
    return paragraphs

# Funções para extração de itálicos
def is_italic_font(font: str) -> bool:
    """Verifica se uma fonte é itálica"""
    return 'MinionPro-It' in font

def extract_italics(page) -> str:
    """Extrai texto mantendo marcações de itálico"""
    result = []
    current_italic = False
    italic_text = []
    normal_text = []
    
    chars = sorted(page.chars, key=lambda x: (x['top'], x['x0']))
    
    for char in chars:
        is_italic = is_italic_font(char['fontname'])
        
        # Início de itálico
        if is_italic and not current_italic:
            if normal_text:
                result.append(''.join(normal_text))
                normal_text = []
            result.append('*')
            current_italic = True
        
        # Fim de itálico
        elif not is_italic and current_italic:
            result.append(''.join(italic_text))
            result.append('*')
            italic_text = []
            current_italic = False
        
        # Adiciona caractere ao grupo apropriado
        if current_italic:
            italic_text.append(char['text'])
        else:
            normal_text.append(char['text'])
    
    # Fecha itálico pendente
    if italic_text:
        result.append(''.join(italic_text))
        if current_italic:
            result.append('*')
    if normal_text:
        result.append(''.join(normal_text))
    
    text = ''.join(result)
    return clean_italics(text)

def clean_italics(text: str) -> str:
    """Limpa os itálicos, garantindo que espaços fiquem fora das marcações"""
    
    def fix_italic_segment(match):
        # Agora usamos sempre um asterisco
        content = match.group(2)  # texto entre os marcadores
        content = content.strip()  # remove espaços do início e fim
        
        # Preserva espaços externos
        prefix = ' ' if match.group(0).startswith(' ') else ''
        suffix = ' ' if match.group(0).endswith(' ') else ''
        
        return f"{prefix}*{content}*{suffix}"
    
    # Primeiro converte ** para *
    text = text.replace('**', '*')
    
    # Procura por quaisquer marcações de itálico e padroniza para *
    text = re.sub(r'(\*\*?)\s*(.*?)\s*(\*\*?)', fix_italic_segment, text)
    
    return text

def clean_text(text: str) -> str:
    """Limpa o texto removendo artefatos"""
    # Remove metadados e números de página
    text = re.sub(r'Clementina_Prova04\.indd.*?\d{2}:\d{2}', '', text)
    text = re.sub(r'^\d+\s*\|.*$', '', text, flags=re.MULTILINE)
    
    # Remove hífens de quebra de linha
    text = re.sub(r'(\w+)-\s+(\w+)', r'\1\2', text)
    
    # Remove espaços extras
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def merge_texts(paragraphs: str, italics: str) -> str:
    """Tenta mesclar texto com parágrafos e marcações de itálico"""
    # Limpa e padroniza os itálicos primeiro
    italics_cleaned = clean_italics(italics)
    result = []
    
    # Processa cada parágrafo
    for paragraph in paragraphs.split('\n\n'):
        modified_paragraph = paragraph
        
        # Procura por trechos em itálico
        for match in re.finditer(r'(\*\*?)(.*?)(\*\*?)', italics_cleaned):
            italic_text = match.group(2).strip()
            if not italic_text:  # Ignora itálicos vazios
                continue
                
            # Procura o texto em itálico no parágrafo
            text_pos = modified_paragraph.lower().find(italic_text.lower())
            if text_pos >= 0:
                before = modified_paragraph[:text_pos]
                after = modified_paragraph[text_pos + len(italic_text):]
                # Sempre usa um único asterisco
                modified_paragraph = f"{before}*{italic_text}*{after}"
        
        result.append(modified_paragraph)
    
    # Aplica limpeza final para garantir uso de um único asterisco
    final_text = '\n\n'.join(result)
    return clean_italics(final_text)

def main():
    configure_logging()
    pdf_path = "sample.pdf"
    
    # Arquivos de saída
    paragraphs_file = "output_paragraphs.md"
    italics_file = "output_italics.md"
    merged_file = "output_merged.md"
    
    try:
        logging.info(f"Processando PDF: {pdf_path}")
        paragraphs_all = []
        italics_all = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                logging.info(f"Processando página {i+1} de {len(pdf.pages)}")
                
                # Extrai parágrafos
                paragraphs = extract_paragraphs(page)
                paragraphs_all.extend(paragraphs)
                
                # Extrai itálicos
                italics = extract_italics(page)
                italics_all.append(italics)
        
        # Prepara os textos
        paragraphs_text = '\n\n'.join(clean_text(p) for p in paragraphs_all if p.strip())
        italics_text = '\n'.join(italics_all)
        
        # Salva arquivo com parágrafos
        with open(paragraphs_file, 'w', encoding='utf-8') as f:
            f.write(paragraphs_text)
        logging.info(f"Arquivo de parágrafos salvo como {paragraphs_file}")
        
        # Salva arquivo com itálicos
        with open(italics_file, 'w', encoding='utf-8') as f:
            f.write(italics_text)
        logging.info(f"Arquivo de itálicos salvo como {italics_file}")
        
        # Tenta mesclar e salva resultado
        merged_text = merge_texts(paragraphs_text, italics_text)
        with open(merged_file, 'w', encoding='utf-8') as f:
            f.write(merged_text)
        logging.info(f"Arquivo mesclado salvo como {merged_file}")
        
    except Exception as e:
        logging.error(f"Erro durante o processamento: {e}")
        raise

if __name__ == "__main__":
    main()