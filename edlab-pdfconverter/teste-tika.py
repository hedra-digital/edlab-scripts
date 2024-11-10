#!/usr/bin/env python3
# Terminou mal... não identifica os itálicos

from tika import parser
import re
import logging

def configure_logging():
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(levelname)s - %(message)s')

def extract_pdf_content(pdf_path: str) -> str:
    """
    Extrai o conteúdo do PDF usando Tika
    """
    try:
        parsed_pdf = parser.from_file(pdf_path)
        if parsed_pdf["content"] is None:
            raise ValueError("Não foi possível extrair conteúdo do PDF")
        return parsed_pdf["content"]
    except Exception as e:
        logging.error(f"Erro ao extrair conteúdo do PDF: {e}")
        raise

def clean_special_chars(text: str) -> str:
    """
    Remove caracteres especiais e formatação indesejada
    """
    # Remove linhas com números de página e dados de impressão
    text = re.sub(r'Clementina_Prova04\.indd.*?\d{2}:\d{2}', '', text, flags=re.MULTILINE)
    
    # Remove números de página isolados
    text = re.sub(r'^\d+$', '', text, flags=re.MULTILINE)
    
    return text

def process_paragraphs(text: str) -> str:
    """
    Processa o texto mantendo os asteriscos originais que indicam itálico
    """
    # Divide em parágrafos
    paragraphs = text.split('\n\n')
    
    processed_paragraphs = []
    for p in paragraphs:
        # Remove espaços extras e quebras de linha dentro do parágrafo
        p = ' '.join(p.split())
        
        if p.strip():
            # Mantém os asteriscos originais mas remove duplicatas
            p = re.sub(r'\*{2,}', '*', p)
            processed_paragraphs.append(p)
    
    return '\n\n'.join(processed_paragraphs)

def main():
    configure_logging()
    input_pdf = "inputB.pdf"
    output_markdown = "output_final.md"
    
    try:
        logging.info(f"Extraindo conteúdo de {input_pdf}")
        content = extract_pdf_content(input_pdf)
        
        logging.info("Limpando caracteres especiais")
        content = clean_special_chars(content)
        
        logging.info("Processando parágrafos")
        markdown_content = process_paragraphs(content)
        
        with open(output_markdown, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        logging.info(f"Arquivo Markdown salvo como {output_markdown}")
        
        # Mostra uma amostra do resultado
        print("\nPrimeiros 500 caracteres do resultado:")
        print(markdown_content[:500])
        
    except Exception as e:
        logging.error(f"Erro durante o processamento: {e}")
        raise

if __name__ == "__main__":
    main()