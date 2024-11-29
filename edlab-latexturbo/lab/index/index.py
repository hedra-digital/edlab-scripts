import re
import argparse
from typing import Dict, List, Tuple

def load_names_dict(names_str: str) -> Dict[str, str]:
    """
    Carrega o dicionário de nomes a partir de uma string formatada.
    Exemplo de formato:
    "Serafim": "Adriano, Serafim",
    "Agostini": "Eugênio, Agostini",
    """
    names_dict = {}
    # Remove espaços em branco extras e divide por linhas
    lines = [line.strip() for line in names_str.split('\n') if line.strip()]
    
    for line in lines:
        # Remove aspas e vírgula final
        line = line.rstrip(',')
        key, value = line.split('": "')
        key = key.strip('"')
        value = value.strip('"')
        names_dict[key] = value
    
    return names_dict

def find_names_positions(text: str, names: List[str]) -> List[Tuple[int, int, str]]:
    """
    Encontra as posições de todos os nomes no texto, respeitando case sensitivity.
    Retorna uma lista de tuplas (início, fim, nome_encontrado).
    """
    positions = []
    
    # Ordena os nomes por tamanho (decrescente) para evitar matches parciais
    names_sorted = sorted(names, key=len, reverse=True)
    
    for name in names_sorted:
        # Usa regex para encontrar o nome com word boundaries
        pattern = r'\b' + re.escape(name) + r'\b'
        for match in re.finditer(pattern, text):
            positions.append((match.start(), match.end(), name))
    
    # Ordena as posições para processamento sequencial
    return sorted(positions)

def process_tex_file(input_text: str, names_dict: Dict[str, str]) -> str:
    """
    Processa o texto LaTeX e adiciona as entradas \index para os nomes encontrados.
    """
    # Encontra todas as posições dos nomes
    positions = find_names_positions(input_text, list(names_dict.keys()))
    
    # Lista para armazenar o texto processado em partes
    result_parts = []
    last_pos = 0
    
    # Offset para ajustar as posições conforme adicionamos \index
    offset = 0
    
    for start, end, name in positions:
        # Ajusta as posições com o offset atual
        adjusted_start = start + offset
        adjusted_end = end + offset
        
        # Adiciona o texto anterior ao nome
        result_parts.append(input_text[last_pos:start])
        
        # Adiciona o nome com a entrada \index
        name_with_index = f"{name}\\index{{{names_dict[name]}}}"
        result_parts.append(name_with_index)
        
        # Atualiza o offset e a última posição
        offset += len(name_with_index) - len(name)
        last_pos = end
    
    # Adiciona o restante do texto
    result_parts.append(input_text[last_pos:])
    
    return ''.join(result_parts)

def main():
    """
    Função principal que processa o arquivo .tex
    """
    # Configurar o parser de argumentos
    parser = argparse.ArgumentParser(description='Processa arquivo .tex adicionando entradas \\index para nomes próprios.')
    parser.add_argument('input_file', help='Arquivo .tex de entrada')
    parser.add_argument('names_file', help='Arquivo com a lista de nomes')
    parser.add_argument('output_file', help='Arquivo .tex de saída')
    
    args = parser.parse_args()
    
    # Lê o arquivo de nomes
    try:
        with open(args.names_file, 'r', encoding='utf-8') as f:
            names_data = f.read()
    except FileNotFoundError:
        print(f"Erro: O arquivo de nomes '{args.names_file}' não foi encontrado.")
        return
    
    # Carrega o dicionário de nomes
    names_dict = load_names_dict(names_data)
    
    # Lê o arquivo de entrada
    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            input_text = f.read()
    except FileNotFoundError:
        print(f"Erro: O arquivo de entrada '{args.input_file}' não foi encontrado.")
        return
    
    # Processa o texto
    output_text = process_tex_file(input_text, names_dict)
    
    # Escreve o resultado no arquivo de saída
    try:
        with open(args.output_file, 'w', encoding='utf-8') as f:
            f.write(output_text)
        print(f"Processamento concluído. Resultado salvo em '{args.output_file}'")
    except Exception as e:
        print(f"Erro ao salvar o arquivo de saída: {e}")

if __name__ == "__main__":
    main()