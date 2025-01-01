import os
import json
import re
from pathlib import Path

class PatternManager:
    """
    Gerencia padrões de substituição de texto, combinando padrões globais e locais.
    Padrões são definidos em arquivos .patterns no formato JSON.
    """
    def __init__(self, project_dir=None):
        self.project_dir = project_dir or str(Path(__file__).parent)
        self.patterns = []
        self.load_patterns()

    def load_patterns(self):
        """
        Carrega padrões de substituição dos arquivos .patterns
        Primeiro carrega o arquivo global, depois o local para permitir sobrescrita
        """
        # Carrega padrões globais
        global_patterns = self._load_pattern_file(os.path.join(self.project_dir, '.patterns'))
        
        # Carrega padrões locais
        local_patterns = self._load_pattern_file('.patterns')
        
        # Combina os padrões, permitindo que locais sobrescrevam globais
        self.patterns = []
        if global_patterns:
            self.patterns.extend(global_patterns)
        if local_patterns:
            # Remove padrões globais que têm o mesmo nome que padrões locais
            local_names = {p['name'] for p in local_patterns}
            self.patterns = [p for p in self.patterns if p['name'] not in local_names]
            self.patterns.extend(local_patterns)

    def _load_pattern_file(self, filepath):
        """
        Carrega e valida um arquivo de padrões
        Retorna uma lista de padrões ou None se o arquivo não existir
        """
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    patterns = json.load(f)
                    
                    # Valida o formato dos padrões
                    if not isinstance(patterns, list):
                        raise ValueError(f"Arquivo {filepath} deve conter uma lista de padrões")
                    
                    for pattern in patterns:
                        required_fields = ['name', 'pattern', 'replacement']
                        if not all(field in pattern for field in required_fields):
                            raise ValueError(f"Padrão em {filepath} está faltando campos obrigatórios")
                        
                        # Compila o padrão para validar a expressão regular
                        try:
                            re.compile(pattern['pattern'])
                        except re.error as e:
                            raise ValueError(f"Expressão regular inválida em {filepath}: {str(e)}")
                    
                    return patterns
        except json.JSONDecodeError as e:
            raise ValueError(f"Erro ao parsear arquivo {filepath}: {str(e)}")
        except Exception as e:
            print(f"Aviso: Erro ao carregar {filepath}: {str(e)}")
        return None
        
    def apply_patterns(self, text):
        modified_text = text
        for pattern in self.patterns:
            try:
                before = modified_text
                modified_text = re.sub(
                    pattern['pattern'],
                    pattern['replacement'],
                    modified_text,
                    flags=re.MULTILINE | re.UNICODE
                )
                if before != modified_text:
                    print(f"Padrão '{pattern['name']}' alterou o texto:")
                    print(f"Antes: {before}")
                    print(f"Depois: {modified_text}\n")
            except Exception as e:
                print(f"Erro ao aplicar padrão {pattern['name']}: {str(e)}")
        return modified_text

def process_text_with_patterns(text, project_dir=None):
    """
    Função auxiliar para processar texto com padrões de substituição
    Retorna o texto processado ou o texto original se nenhum padrão for aplicado
    
    Args:
        text (str): Texto a ser processado
        project_dir (str, optional): Diretório do projeto onde procurar o arquivo global .patterns
    
    Returns:
        str: Texto processado com os padrões aplicados
    """
    pattern_manager = PatternManager(project_dir)
    return pattern_manager.apply_patterns(text)