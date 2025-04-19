import re
import os
import sys
import time
import logging
from collections import defaultdict

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("hifenizacao.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("hifenizacao")

# Simplificação dos padrões problemáticos
TIPOS_PROBLEMAS = {
    "palavras_curtas": "Palavras curtas geralmente não devem ser hifenizadas",
    "ditongos": "Separação de ditongos não deve ocorrer",
    "hiatos": "Hiatos podem ser separados em determinados contextos",
    "encontros_nasais": "Encontros nasais requerem cuidado na separação",
    "prefixos": "Prefixos devem ser separados da raiz da palavra",
    "sufixos": "Sufixos podem ser separados em determinados contextos"
}

# Regras tipográficas para palavras específicas
REGRAS_TIPOGRAFICAS = {
    "sábio": {"divisao": "sábio", "tipo": "ditongos"},
    "ideia": {"divisao": "idei-a", "tipo": "hiatos"},
    "história": {"divisao": "histó-ria", "tipo": "hiatos"},
    "coordenar": {"divisao": "coor-denar", "tipo": "hiatos"},
    "contra": {"divisao": "contra", "tipo": "palavras_curtas"},
    "para": {"divisao": "para", "tipo": "palavras_curtas"},
    "como": {"divisao": "como", "tipo": "palavras_curtas"},
    "pela": {"divisao": "pela", "tipo": "palavras_curtas"},
    "pelo": {"divisao": "pelo", "tipo": "palavras_curtas"},
    "quem": {"divisao": "quem", "tipo": "palavras_curtas"},
    "tem": {"divisao": "tem", "tipo": "palavras_curtas"},
    "sem": {"divisao": "sem", "tipo": "palavras_curtas"},
    "mas": {"divisao": "mas", "tipo": "palavras_curtas"},
    "dos": {"divisao": "dos", "tipo": "palavras_curtas"},
    "das": {"divisao": "das", "tipo": "palavras_curtas"},
    "nos": {"divisao": "nos", "tipo": "palavras_curtas"},
    "nas": {"divisao": "nas", "tipo": "palavras_curtas"},
}

# Prefixos comuns em português
PREFIXOS = ["anti", "auto", "contra", "des", "extra", "hiper", "infra", "inter", 
            "intra", "micro", "multi", "poli", "pós", "pré", "proto", "pseudo", 
            "semi", "sub", "super", "supra", "ultra"]

# Sufixos comuns em português
SUFIXOS = ["inho", "inha", "zinho", "zinha", "mente", "issimo", "íssimo", "íssima",
           "izar", "ção", "ismo", "idade", "mento", "vel", "bilidade"]

# Vogais
VOGAIS = "aeiouáàâãéèêíìîóòôõúùû"

def barra_progresso(progresso, total, tamanho=50, prefixo="", sufixo=""):
    """Exibe uma barra de progresso no terminal"""
    porcentagem = min(1.0, progresso / max(1, total))
    barra = '█' * int(tamanho * porcentagem)
    espaços = ' ' * (tamanho - len(barra))
    sys.stdout.write(f"\r{prefixo}[{barra}{espaços}] {int(porcentagem * 100)}% ({progresso}/{total}) {sufixo}")
    sys.stdout.flush()

def extrair_palavras_tex(arquivo_tex):
    """Extrai palavras de um arquivo .tex e conta suas ocorrências"""
    try:
        with open(arquivo_tex, 'r', encoding='utf-8') as f:
            conteudo = f.read()
            tamanho_total = len(conteudo)
            logger.info(f"Lido arquivo {arquivo_tex} com {tamanho_total} caracteres")
    except Exception as e:
        logger.error(f"ERRO ao ler o arquivo {arquivo_tex}: {str(e)}")
        return {}
    
    logger.info("Processando texto e removendo comandos LaTeX...")
    
    # Remove comandos LaTeX e ambientes matemáticos
    conteudo_processado = re.sub(r'\\[a-zA-Z]+(\{[^}]*\})*', ' ', conteudo)
    conteudo_processado = re.sub(r'\$[^$]*\$', ' ', conteudo_processado)
    
    logger.info("Extraindo palavras...")
    
    # Extrai palavras (incluindo acentuadas)
    palavras_encontradas = re.findall(r'\b[a-záàâãéèêíìîóòôõúùûçA-ZÁÀÂÃÉÈÊÍÌÎÓÒÔÕÚÙÛÇ]+\b', conteudo_processado, re.UNICODE)
    
    # Criar contagem de palavras
    logger.info(f"Contando frequência de {len(palavras_encontradas)} palavras...")
    palavra_count = defaultdict(int)
    for palavra in palavras_encontradas:
        palavra_count[palavra] += 1
    
    logger.info(f"Encontradas {len(palavra_count)} palavras únicas em {len(palavras_encontradas)} ocorrências totais")
    return palavra_count

def identificar_palavras_problematicas(palavras):
    """Identifica palavras com potenciais problemas tipográficos usando métodos mais simples e rápidos"""
    palavras_problematicas = defaultdict(list)
    lista_palavras = list(palavras.items())
    total_palavras = len(lista_palavras)
    
    logger.info(f"Identificando palavras potencialmente problemáticas (versão simplificada)...")
    
    # Processamento mais simples e rápido
    for i, (palavra, contagem) in enumerate(lista_palavras):
        palavra_lower = palavra.lower()
        
        # Atualizar barra de progresso
        if i % 5 == 0 or i == total_palavras - 1:
            barra_progresso(i+1, total_palavras, prefixo="Analisando palavras: ")
        
        # Verificar se é palavra específica com regra predefinida
        if palavra_lower in REGRAS_TIPOGRAFICAS:
            tipo = REGRAS_TIPOGRAFICAS[palavra_lower]["tipo"]
            categoria = TIPOS_PROBLEMAS[tipo]
            divisao = REGRAS_TIPOGRAFICAS[palavra_lower]["divisao"]
            
            palavras_problematicas[categoria].append({
                "palavra": palavra,
                "contagem": contagem,
                "divisao_tipografica": divisao,
                "fonte": "regra_específica"
            })
            continue
        
        # Regras simplificadas para análise rápida
        
        # Palavras curtas (3-5 letras)
        if len(palavra_lower) <= 5:
            palavras_problematicas[TIPOS_PROBLEMAS["palavras_curtas"]].append({
                "palavra": palavra,
                "contagem": contagem,
                "divisao_tipografica": palavra_lower,  # Não separar
                "fonte": "palavras_curtas"
            })
            continue
        
        # Verificar prefixos
        prefixo_encontrado = False
        for prefixo in PREFIXOS:
            if palavra_lower.startswith(prefixo) and len(palavra_lower) > len(prefixo) + 3:
                # Verificar se a letra após o prefixo é uma vogal
                if palavra_lower[len(prefixo)] in VOGAIS:
                    palavras_problematicas[TIPOS_PROBLEMAS["prefixos"]].append({
                        "palavra": palavra,
                        "contagem": contagem,
                        "divisao_tipografica": prefixo + "-" + palavra_lower[len(prefixo):],
                        "fonte": "prefixos"
                    })
                    prefixo_encontrado = True
                    break
        
        if prefixo_encontrado:
            continue
        
        # Verificar sufixos
        sufixo_encontrado = False
        for sufixo in SUFIXOS:
            if palavra_lower.endswith(sufixo) and len(palavra_lower) > len(sufixo) + 3:
                # Para zinho/zinha, sempre separar
                if sufixo in ["zinho", "zinha"]:
                    palavras_problematicas[TIPOS_PROBLEMAS["sufixos"]].append({
                        "palavra": palavra,
                        "contagem": contagem,
                        "divisao_tipografica": palavra_lower[:-len(sufixo)] + "-" + sufixo,
                        "fonte": "sufixos"
                    })
                    sufixo_encontrado = True
                    break
                # Para outros sufixos, verificar caso a caso
                elif sufixo in ["mente", "idade", "mento"]:
                    palavras_problematicas[TIPOS_PROBLEMAS["sufixos"]].append({
                        "palavra": palavra,
                        "contagem": contagem,
                        "divisao_tipografica": palavra_lower[:-len(sufixo)] + "-" + sufixo,
                        "fonte": "sufixos"
                    })
                    sufixo_encontrado = True
                    break
        
        if sufixo_encontrado:
            continue
        
        # Verificar hiatos simples (vogal + vogal diferente)
        hiato_encontrado = False
        for i in range(len(palavra_lower) - 1):
            if (palavra_lower[i] in VOGAIS and palavra_lower[i+1] in VOGAIS and 
                palavra_lower[i] != palavra_lower[i+1]):
                # Se for hiato no final, considerar separá-lo
                if i+1 == len(palavra_lower) - 1:
                    palavras_problematicas[TIPOS_PROBLEMAS["hiatos"]].append({
                        "palavra": palavra,
                        "contagem": contagem,
                        "divisao_tipografica": palavra_lower[:i+1] + "-" + palavra_lower[i+1:],
                        "fonte": "hiatos"
                    })
                    hiato_encontrado = True
                    break
        
        if hiato_encontrado:
            continue
        
        # Verificar ditongos óbvios (vogal + i/u)
        ditongo_encontrado = False
        for i in range(len(palavra_lower) - 1):
            if (palavra_lower[i] in VOGAIS and palavra_lower[i+1] in "iu" and 
                (i+2 == len(palavra_lower) or palavra_lower[i+2] not in VOGAIS)):
                palavras_problematicas[TIPOS_PROBLEMAS["ditongos"]].append({
                    "palavra": palavra,
                    "contagem": contagem,
                    "divisao_tipografica": palavra_lower,  # Não separar ditongos
                    "fonte": "ditongos"
                })
                ditongo_encontrado = True
                break
        
        if ditongo_encontrado:
            continue
        
        # Encontros nasais (vogal + m/n + vogal)
        for i in range(len(palavra_lower) - 2):
            if (palavra_lower[i] in VOGAIS and palavra_lower[i+1] in "mn" and 
                palavra_lower[i+2] in VOGAIS):
                palavras_problematicas[TIPOS_PROBLEMAS["encontros_nasais"]].append({
                    "palavra": palavra,
                    "contagem": contagem,
                    "divisao_tipografica": palavra_lower[:i+1] + "-" + palavra_lower[i+1:],
                    "fonte": "encontros_nasais"
                })
                break
    
    print("\nProcessamento concluído com sucesso.")
    return palavras_problematicas

def gerar_hyphenation_sty(palavras_problematicas, arquivo_saida="hyphenation.sty"):
    """Gera o arquivo hyphenation.sty com sugestões de hifenização"""
    logger.info(f"Gerando arquivo {arquivo_saida}...")
    
    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        f.write("% Arquivo de hifenização tipográfica especial\n")
        f.write("% Gerado automaticamente para ajuste tipográfico\n\n")
        
        total_categorias = len(palavras_problematicas)
        i = 0
        
        for categoria, palavras in palavras_problematicas.items():
            i += 1
            barra_progresso(i, total_categorias, prefixo="Gerando arquivo: ")
            
            # Ordenar palavras por contagem
            palavras_sorted = sorted(palavras, key=lambda x: x["contagem"], reverse=True)
            
            f.write(f"% {categoria}\n")
            for p in palavras_sorted:
                palavra = p['palavra']
                divisao_tipografica = p['divisao_tipografica']
                contagem = p['contagem']
                
                f.write(f"% Palavra: {palavra}\n")
                f.write(f"% Frequência no texto: {contagem}\n")
                
                # Sempre usar o comando \hyphenation
                f.write(f"\\hyphenation{{{divisao_tipografica}}}\n")
                
                # Versão com inicial maiúscula
                if '-' in divisao_tipografica:
                    partes = divisao_tipografica.split('-')
                    partes_cap = [partes[0].capitalize()] + partes[1:]
                    divisao_cap = '-'.join(partes_cap)
                    f.write(f"\\hyphenation{{{divisao_cap}}}\n")
                else:
                    f.write(f"\\hyphenation{{{divisao_tipografica.capitalize()}}}\n")
                
                # Versão toda maiúscula
                f.write(f"\\hyphenation{{{divisao_tipografica.upper()}}}\n\n")
    
    print("\nArquivo gerado com sucesso.")

def processar_arquivo_tex(arquivo_tex, saida="hyphenation.sty", max_palavras=None):
    """Processa um arquivo .tex e gera regras de hifenização tipográfica"""
    # Verifica se o arquivo existe
    if not os.path.isfile(arquivo_tex):
        logger.error(f"ERRO: O arquivo {arquivo_tex} não existe ou não pode ser acessado.")
        return False
    
    logger.info(f"Iniciando processamento do arquivo {arquivo_tex}...")
    tempo_inicio = time.time()
    
    try:
        # Extrai palavras do arquivo
        palavras = extrair_palavras_tex(arquivo_tex)
        
        if not palavras:
            logger.warning(f"AVISO: Não foram encontradas palavras no arquivo {arquivo_tex}.")
            return False
        
        # Limitar o número de palavras para testes (opcional)
        if max_palavras and len(palavras) > max_palavras:
            logger.info(f"Limitando análise às {max_palavras} palavras mais frequentes para teste")
            palavras_ordenadas = sorted(palavras.items(), key=lambda x: x[1], reverse=True)[:max_palavras]
            palavras = dict(palavras_ordenadas)
        
        # Identificar palavras com potenciais problemas tipográficos
        palavras_problematicas = identificar_palavras_problematicas(palavras)
        
        # Gerar arquivo de saída
        gerar_hyphenation_sty(palavras_problematicas, saida)
        
        # Estatísticas
        total_problematicas = sum(len(palavras) for palavras in palavras_problematicas.values())
        logger.info(f"Total de palavras com potenciais problemas de hifenização tipográfica: {total_problematicas}")
        
        for categoria, palavras_lista in palavras_problematicas.items():
            logger.info(f"  • {categoria}: {len(palavras_lista)} palavras")
            
            # Mostrar as palavras mais frequentes
            if len(palavras_lista) > 0:
                palavras_ordenadas = sorted(palavras_lista, key=lambda x: x["contagem"], reverse=True)
                top_palavras = palavras_ordenadas[:min(5, len(palavras_ordenadas))]
                palavras_print = ", ".join([f"{p['palavra']} ({p['contagem']})" for p in top_palavras])
                logger.info(f"    → Mais frequentes: {palavras_print}")
        
        tempo_total = time.time() - tempo_inicio
        logger.info(f"Processamento concluído em {tempo_total:.2f} segundos.")
        return True
        
    except Exception as e:
        logger.exception(f"Erro durante o processamento: {str(e)}")
        return False

if __name__ == "__main__":
    # Verifica os argumentos
    if len(sys.argv) < 2:
        print("Uso: python script.py arquivo.tex [saida.sty] [max_palavras]")
        sys.exit(1)
    
    arquivo_tex = sys.argv[1]
    saida = sys.argv[2] if len(sys.argv) > 2 else "hyphenation.sty"
    
    # Parâmetro opcional para limitar número de palavras (para testes)
    max_palavras = None
    if len(sys.argv) > 3:
        try:
            max_palavras = int(sys.argv[3])
        except ValueError:
            print(f"AVISO: Valor inválido para max_palavras: {sys.argv[3]}")
    
    # Definir um timeout (opcional)
    import signal
    
    def timeout_handler(signum, frame):
        print("\nOperação excedeu o tempo limite. Interrompendo...")
        sys.exit(1)
    
    # Configurar timeout de 30 segundos
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)
    
    # Processa o arquivo
    sucesso = processar_arquivo_tex(arquivo_tex, saida, max_palavras)
    
    # Desativa o alarme
    signal.alarm(0)
    
    if sucesso:
        print(f"\nArquivo {saida} gerado com sucesso!")
    else:
        print(f"\nOcorreu um erro ao processar o arquivo {arquivo_tex}.")