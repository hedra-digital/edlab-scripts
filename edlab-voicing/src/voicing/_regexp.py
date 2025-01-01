import re
import json
import argparse
from pathlib import Path

def load_patterns(patterns_file='.patterns'):
    """Carrega os padrões de substituição do arquivo JSON."""
    try:
        with open(patterns_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Erro: Arquivo de padrões '{patterns_file}' não encontrado.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Erro: Arquivo '{patterns_file}' contém JSON inválido.")
        exit(1)

def process_text(text, patterns):
    """Aplica todos os padrões de substituição ao texto."""
    result = text
    for pattern in patterns:
        result = re.sub(pattern['pattern'], pattern['replacement'], result)
    return result

def process_file(input_file, patterns):
    """Processa um arquivo linha por linha aplicando os padrões."""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        processed_lines = [process_text(line, patterns) for line in lines]
        
        # Gera o nome do arquivo de saída
        output_file = Path(input_file).stem + '_processed' + Path(input_file).suffix
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(processed_lines)
            
        print(f"Arquivo processado salvo como: {output_file}")
            
    except FileNotFoundError:
        print(f"Erro: Arquivo de entrada '{input_file}' não encontrado.")
        exit(1)
    except Exception as e:
        print(f"Erro ao processar arquivo: {str(e)}")
        exit(1)

def main():
    parser = argparse.ArgumentParser(description='Processa texto usando padrões de expressões regulares.')
    parser.add_argument('-i', '--input', required=True, help='Arquivo de entrada para processar')
    parser.add_argument('-p', '--patterns', default='.patterns', 
                        help='Arquivo JSON com os padrões de substituição (padrão: .patterns)')
    
    args = parser.parse_args()
    
    # Carrega os padrões
    patterns = load_patterns(args.patterns)
    
    # Processa o arquivo
    process_file(args.input, patterns)

if __name__ == "__main__":
    main()