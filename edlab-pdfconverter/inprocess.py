https://claude.ai/chat/6e9bf605-387d-434a-99cb-be34a10d0ac9

# Remova a primeira definição de find_pdf_files() e mantenha apenas esta versão:
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

# Use esta versão atualizada da função generate_output_filename:
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

# E reorganize a função main para evitar verificações duplicadas:
def main():
    parser = argparse.ArgumentParser(description="Manipulação de arquivos PDF: juntar, remover texto, cortar margens, extrair páginas e converter para imagens.")
    
    parser.add_argument("-i", "--input", required=True, nargs='+',
                       help="Arquivo(s) PDF de entrada, diretório(s) ou padrões (*.pdf). Use 'BLANK' para inserir páginas em branco quando usando --join")
    parser.add_argument("-o", "--output", 
                       help="Arquivo de saída para operações em arquivo único ou junção, ou diretório para múltiplos arquivos.")
    parser.add_argument("-m", "--margins", 
                       help="Margens para o corte com pdfcrop. Use um valor ou quatro valores para margens separadas.")
    parser.add_argument("-d", "--dir", 
                       help="Diretório onde as imagens serão salvas.")
    parser.add_argument("-p", "--pages", 
                       help="Intervalo de páginas para processar (ex: '1-3' ou '1').")
    parser.add_argument("-f", "--format", default="jpeg",
                       help="Formato da imagem de saída (jpeg ou png). Padrão: jpeg.")
    parser.add_argument("-rt", "--remove-text", action='store_true',
                       help="Remove o texto do PDF antes de cortar margens e converter em imagens.")
    parser.add_argument("-j", "--join", action='store_true',
                       help="Junta múltiplos PDFs em um único arquivo.")
    parser.add_argument("--page-counter", action='store_true',
                       help="Conta o número de páginas dos PDFs e gera relatório em PAGES.txt")
    parser.add_argument("-et", "--extract-text", action='store_true',
                       help="Extrai texto do PDF removendo hifenizações")

    args = parser.parse_args()

    try:
        # Encontra todos os arquivos PDF com base nos argumentos de entrada
        input_files = find_pdf_files(args.input)
        
        if not input_files:
            logging.error("Nenhum arquivo PDF encontrado")
            return

        # Processamento por tipo de operação
        if args.extract_text:
            # Processa cada arquivo PDF encontrado
            for input_file in [f for f in input_files if f != "BLANK"]:
                output_file = args.output if args.output else None
                try:
                    extracted_file = extract_text_from_pdf(input_file, output_file)
                    logging.info(f"Texto extraído com sucesso de {input_file} para {extracted_file}")
                except Exception as e:
                    logging.error(f"Erro ao processar {input_file}: {str(e)}")
            return
            
        elif args.page_counter:
            # Filtra apenas os arquivos PDF (remove BLANK se houver)
            pdf_files = [f for f in input_files if f != "BLANK"]
            if not pdf_files:
                logging.error("Nenhum arquivo PDF válido encontrado para contagem")
                return
            results = count_pdf_pages(pdf_files)
            save_page_count_report(results)
            return
            
        elif args.join:
            # Resto do código para junção de PDFs...
            # [mantenha o código existente para junção]
            pass
            
        else:
            # Operações em arquivo único
            # [mantenha o código existente para operações em arquivo único]
            pass

    except Exception as e:
        logging.error(f"Erro durante o processamento: {str(e)}")
        raise

if __name__ == "__main__":
    main()