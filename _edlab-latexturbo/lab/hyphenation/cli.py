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

# Padrões problemáticos de hifenização
TIPOS_PROBLEMAS = {
    "ditongos": "Ditongos que não devem ser separados",
    "hiatos": "Hiatos que podem ser separados",
    "encontros_nasais": "Encontros nasais que requerem cuidado na separação",
    "prefixos": "Prefixos que devem ser separados da raiz da palavra",
    "sufixos": "Sufixos que podem ser separados em determinados contextos",
    "digrafos": "Dígrafos que não devem ser separados"
}

# Dígrafos inseparáveis
DIGRAFOS_INSEPARAVEIS = ["ch", "lh", "nh", "qu", "gu", "rr", "ss", "sc", "xc"]

# Regras tipográficas para palavras específicas
REGRAS_TIPOGRAFICAS = {
    # Palavras com regras específicas de hifenização
    "ideia": {"divisao": "idei-a", "tipo": "hiatos"},
    "história": {"divisao": "his-tó-ria", "tipo": "hiatos"},
    "coordenar": {"divisao": "co-or-de-nar", "tipo": "hiatos"},
    "nacional": {"divisao": "na-ci-o-nal", "tipo": "encontros_nasais"},
    "energias": {"divisao": "e-ner-gi-as", "tipo": "encontros_nasais"},
    "romance": {"divisao": "ro-man-ce", "tipo": "encontros_nasais"},
    "homenagens": {"divisao": "ho-me-na-gens", "tipo": "encontros_nasais"},
    "trejeitos": {"divisao": "tre-jei-tos", "tipo": "ditongos"},
}

# Dicionário de hifenização correta para casos específicos
HIFENIZACAO_CORRETA = {
    "nacional": "na-ci-o-nal",
    "energias": "e-ner-gi-as",
    "romance": "ro-man-ce",
    "homenagens": "ho-me-na-gens",
    "trejeitos": "tre-jei-tos",
    # Adicione mais palavras conforme necessário
}

# Prefixos comuns em português
PREFIXOS = [
    "anti", "auto", "contra", "des", "extra", "hiper", "infra", "inter", 
    "intra", "micro", "multi", "poli", "pós", "pré", "proto", "pseudo", 
    "semi", "sub", "super", "supra", "ultra", "re", "in", "im", "i", "a"
]

# Sufixos comuns em português
SUFIXOS = [
    "inho", "inha", "zinho", "zinha", "mente", "issimo", "íssimo", "íssima",
    "izar", "ção", "ismo", "idade", "mento", "vel", "bilidade", "tório", 
    "dor", "dora", "ante", "ência", "ância", "ico", "ica", "ável", "ível"
]

# Vogais e ditongos
VOGAIS = "aeiouáàâãéèêíìîóòôõúùû"
DITONGOS = ["ai", "au", "ei", "eu", "iu", "oi", "ou", "ui", "ão", "ãe", "õe"]

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

def eh_ditongo(texto, i):
    """Verifica se há um ditongo na posição i"""
    if i+1 >= len(texto):
        return False
        
    # Verificar se é um dos ditongos conhecidos
    if i+1 < len(texto) and texto[i:i+2].lower() in DITONGOS:
        return True
        
    # Regra geral para ditongos
    return (texto[i] in VOGAIS and texto[i+1] in "iu" and
            (i+2 == len(texto) or texto[i+2] not in VOGAIS) and
            # Verificar se não é hiato óbvio
            not (texto[i] in "aeo" and texto[i+1] == "i" and 
                 (i+2 == len(texto) or texto[i+2] not in VOGAIS)))

def eh_hiato(texto, i):
    """Verifica se há um hiato na posição i"""
    if i+1 >= len(texto):
        return False
        
    # Duas vogais diferentes seguidas (exceto ditongos conhecidos)
    return (texto[i] in VOGAIS and texto[i+1] in VOGAIS and 
            texto[i] != texto[i+1] and
            texto[i:i+2].lower() not in DITONGOS)

def contem_digrafo_inseparavel(texto, i):
    """Verifica se há um dígrafo inseparável na posição i"""
    if i+1 >= len(texto):
        return False
        
    return texto[i:i+2].lower() in DIGRAFOS_INSEPARAVEIS

def sugerir_pontos_hifenizacao(palavra):
    """Sugere pontos de hifenização para uma palavra com base em regras fonéticas"""
    palavra_lower = palavra.lower()
    
    # Verificar se a palavra está no dicionário de hifenização
    if palavra_lower in HIFENIZACAO_CORRETA:
        return HIFENIZACAO_CORRETA[palavra_lower]
        
    # Verificar se a palavra está nas regras tipográficas
    if palavra_lower in REGRAS_TIPOGRAFICAS:
        return REGRAS_TIPOGRAFICAS[palavra_lower]["divisao"]
    
    # Implementação básica de regras de separação silábica
    resultado = ''
    i = 0
    
    while i < len(palavra_lower):
        # Não separar se estamos no início da palavra ou próximo do fim
        if i <= 0 or i >= len(palavra_lower) - 1:
            resultado += palavra_lower[i]
            i += 1
            continue
            
        # Não separar dígrafos
        if contem_digrafo_inseparavel(palavra_lower, i):
            resultado += palavra_lower[i:i+2]
            i += 2
            continue
            
        # Tratar ditongos (não separar)
        if eh_ditongo(palavra_lower, i):
            resultado += palavra_lower[i:i+2]
            i += 2
            continue
            
        # Tratar hiatos (separar)
        if eh_hiato(palavra_lower, i):
            resultado += palavra_lower[i] + '-' + palavra_lower[i+1]
            i += 2
            continue
            
        # Consoante entre vogais (V-CV)
        if (i > 0 and palavra_lower[i-1] in VOGAIS and 
            palavra_lower[i] not in VOGAIS and i+1 < len(palavra_lower) and 
            palavra_lower[i+1] in VOGAIS):
            resultado += '-' + palavra_lower[i]
            i += 1
            continue
            
        # Grupo de consoantes (VCC-V)
        if (i > 0 and palavra_lower[i-1] in VOGAIS and 
            palavra_lower[i] not in VOGAIS and i+1 < len(palavra_lower) and 
            palavra_lower[i+1] not in VOGAIS and i+2 < len(palavra_lower) and 
            palavra_lower[i+2] in VOGAIS):
            # Separar entre as consoantes se não formarem um dígrafo
            if not contem_digrafo_inseparavel(palavra_lower, i):
                resultado += palavra_lower[i] + '-' + palavra_lower[i+1]
                i += 2
                continue
                
        # Caso padrão
        resultado += palavra_lower[i]
        i += 1
        
    return resultado

def identificar_palavras_problematicas(palavras):
    """Identifica palavras com potenciais problemas tipográficos e sugere pontos de hifenização"""
    palavras_problematicas = defaultdict(list)
    lista_palavras = list(palavras.items())
    total_palavras = len(lista_palavras)
    
    logger.info(f"Identificando padrões de hifenização para {total_palavras} palavras...")
    
    # Filtrar palavras muito curtas (menos de 4 letras)
    palavras_longas = [(palavra, contagem) for palavra, contagem in lista_palavras if len(palavra) >= 4]
    total_palavras_longas = len(palavras_longas)
    
    logger.info(f"Analisando {total_palavras_longas} palavras com 4 ou mais letras...")
    
    for i, (palavra, contagem) in enumerate(palavras_longas):
        palavra_lower = palavra.lower()
        
        # Atualizar barra de progresso
        if i % 5 == 0 or i == total_palavras_longas - 1:
            barra_progresso(i+1, total_palavras_longas, prefixo="Analisando palavras: ")
        
        # 1. Verificar se é uma palavra com regra predefinida
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
        
        # 2. Verificar se é uma palavra do dicionário de hifenização correta
        if palavra_lower in HIFENIZACAO_CORRETA:
            for tipo, descricao in TIPOS_PROBLEMAS.items():
                if "encontro" in descricao.lower():  # Categoria genérica
                    palavras_problematicas[descricao].append({
                        "palavra": palavra,
                        "contagem": contagem,
                        "divisao_tipografica": HIFENIZACAO_CORRETA[palavra_lower],
                        "fonte": "dicionário_hifenização"
                    })
                    break
            continue
        
        # 3. Verificar prefixos
        prefixo_encontrado = False
        for prefixo in PREFIXOS:
            if (palavra_lower.startswith(prefixo) and 
                len(palavra_lower) > len(prefixo) + 3 and
                # Verificar se há uma vogal após o prefixo
                len(palavra_lower) > len(prefixo) and palavra_lower[len(prefixo)] in VOGAIS):
                
                # Separar após o prefixo
                resto = palavra_lower[len(prefixo):]
                divisao = prefixo + '-' + resto
                
                # Refina ainda mais a hifenização no resto da palavra
                if len(resto) > 4:  # Se o resto for grande o suficiente
                    divisao_resto = sugerir_pontos_hifenizacao(resto)
                    if '-' in divisao_resto:  # Se o algoritmo sugeriu pontos
                        divisao = prefixo + '-' + divisao_resto
                
                palavras_problematicas[TIPOS_PROBLEMAS["prefixos"]].append({
                    "palavra": palavra,
                    "contagem": contagem,
                    "divisao_tipografica": divisao,
                    "fonte": "prefixos"
                })
                prefixo_encontrado = True
                break
        
        if prefixo_encontrado:
            continue
        
        # 4. Verificar sufixos
        sufixo_encontrado = False
        for sufixo in SUFIXOS:
            if (palavra_lower.endswith(sufixo) and 
                len(palavra_lower) > len(sufixo) + 3):
                
                # Separar antes do sufixo
                raiz = palavra_lower[:-len(sufixo)]
                divisao = raiz + '-' + sufixo
                
                # Refina ainda mais a hifenização na raiz da palavra
                if len(raiz) > 4:  # Se a raiz for grande o suficiente
                    divisao_raiz = sugerir_pontos_hifenizacao(raiz)
                    if '-' in divisao_raiz:  # Se o algoritmo sugeriu pontos
                        divisao = divisao_raiz + '-' + sufixo
                
                palavras_problematicas[TIPOS_PROBLEMAS["sufixos"]].append({
                    "palavra": palavra,
                    "contagem": contagem,
                    "divisao_tipografica": divisao,
                    "fonte": "sufixos"
                })
                sufixo_encontrado = True
                break
        
        if sufixo_encontrado:
            continue
        
        # 5. Verificar dígrafos inseparáveis
        digrafo_encontrado = False
        for i in range(len(palavra_lower) - 1):
            if contem_digrafo_inseparavel(palavra_lower, i):
                # Tentar uma hifenização genérica, mas preservando o dígrafo
                divisao = sugerir_pontos_hifenizacao(palavra_lower)
                
                palavras_problematicas[TIPOS_PROBLEMAS["digrafos"]].append({
                    "palavra": palavra,
                    "contagem": contagem,
                    "divisao_tipografica": divisao,
                    "fonte": "digrafos"
                })
                digrafo_encontrado = True
                break
        
        if digrafo_encontrado:
            continue
        
        # 6. Verificar ditongos
        ditongo_encontrado = False
        for i in range(len(palavra_lower) - 1):
            if eh_ditongo(palavra_lower, i):
                # Gerar uma sugestão de hifenização que preserva os ditongos
                divisao = sugerir_pontos_hifenizacao(palavra_lower)
                
                palavras_problematicas[TIPOS_PROBLEMAS["ditongos"]].append({
                    "palavra": palavra,
                    "contagem": contagem,
                    "divisao_tipografica": divisao,
                    "fonte": "ditongos"
                })
                ditongo_encontrado = True
                break
        
        if ditongo_encontrado:
            continue
        
        # 7. Verificar hiatos
        hiato_encontrado = False
        for i in range(len(palavra_lower) - 1):
            if eh_hiato(palavra_lower, i):
                # Gerar uma sugestão de hifenização com separação no hiato
                divisao = sugerir_pontos_hifenizacao(palavra_lower)
                
                palavras_problematicas[TIPOS_PROBLEMAS["hiatos"]].append({
                    "palavra": palavra,
                    "contagem": contagem,
                    "divisao_tipografica": divisao,
                    "fonte": "hiatos"
                })
                hiato_encontrado = True
                break
        
        if hiato_encontrado:
            continue
        
        # 8. Para palavras grandes sem padrões específicos identificados
        if len(palavra_lower) > 6:
            # Aplicar hifenização genérica baseada em padrões fonéticos
            divisao = sugerir_pontos_hifenizacao(palavra_lower)
            
            # Categorizar com base em características gerais
            if 'n' in palavra_lower or 'm' in palavra_lower:
                categoria = TIPOS_PROBLEMAS["encontros_nasais"]
            else:
                # Usar a primeira categoria como genérica
                categoria = list(TIPOS_PROBLEMAS.values())[0]
            
            palavras_problematicas[categoria].append({
                "palavra": palavra,
                "contagem": contagem,
                "divisao_tipografica": divisao,
                "fonte": "algoritmo_genérico"
            })
    
    print("\nProcessamento concluído com sucesso.")
    return palavras_problematicas

def gerar_hyphenation_sty(palavras_problematicas, arquivo_saida="hyphenation.sty"):
    """Gera o arquivo hyphenation.sty com sugestões de hifenização"""
    logger.info(f"Gerando arquivo {arquivo_saida}...")
    
    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        f.write("% Arquivo de hifenização tipográfica especial\n")
        f.write("% Gerado automaticamente para ajuste tipográfico\n")
        f.write("% Data de geração: " + time.strftime("%Y-%m-%d %H:%M:%S") + "\n")
        f.write("% NOTA: Cada comando \\hyphenation{} especifica os pontos onde a quebra É PERMITIDA\n")
        f.write("%       Se uma palavra não contém hífens no comando, ela NUNCA será hifenizada\n\n")
        
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
                fonte = p['fonte']
                
                f.write(f"% Palavra: {palavra}\n")
                f.write(f"% Frequência no texto: {contagem}\n")
                f.write(f"% Fonte da regra: {fonte}\n")
                
                # Para declarar corretamente os pontos de hifenização
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
        logger.info(f"Total de palavras com sugestões de hifenização: {total_problematicas}")
        
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
    
    # Opcional: configurar timeout
    import signal
    
    def timeout_handler(signum, frame):
        print("\nOperação excedeu o tempo limite. Interrompendo...")
        sys.exit(1)
    
    # Configurar timeout de 60 segundos (ajustado para processar mais palavras)
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(60)
    
    # Processa o arquivo
    sucesso = processar_arquivo_tex(arquivo_tex, saida, max_palavras)
    
    # Desativa o alarme
    signal.alarm(0)
    
    if sucesso:
        print(f"\nArquivo {saida} gerado com sucesso!")
        print(f"NOTA: O arquivo contém sugestões de pontos onde a hifenização é PERMITIDA.")
        print(f"      Revise manualmente para garantir a qualidade tipográfica.")
    else:
        print(f"\nOcorreu um erro ao processar o arquivo {arquivo_tex}.")