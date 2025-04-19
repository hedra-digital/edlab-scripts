import re
import os
from collections import defaultdict

# Dicionário de padrões problemáticos com suas regras de hifenização tipográfica
PADROES_PROBLEMATICOS = {
    "ditongos_crescentes": {
        "regex": r'[^aeiouáàâãéèêíìîóòôõúùû][aeiouáàâãéèêíìîóòôõúùû][aeiouáàâãéèêíìîóòôõúùû]',
        "comentario": "Separação de ditongos crescentes",
        "exemplos": ["sábio", "ódio", "série"]
    },
    "hiatos_final": {
        "regex": r'[aeiouáàâãéèêíìîóòôõúùû][aeiouáàâãéèêíìîóòôõúùû]$',
        "comentario": "Separação de hiatos em final de palavra",
        "exemplos": ["ideia", "história"]
    },
    "vogais_identicas": {
        "regex": r'[aeiouáàâãéèêíìîóòôõúùû]{2}',
        "comentario": "Separação de vogais idênticas contíguas",
        "exemplos": ["coordenar", "microonda"]
    },
    "grupos_qu_gu": {
        "regex": r'[qg]u[aeiouáàâãéèêíìîóòôõúùû]',
        "comentario": "Separação de grupos consonantais especiais (qu/gu)",
        "exemplos": ["frequente", "ambíguo"]
    },
    "encontros_nasalizados": {
        "regex": r'[aeiouáàâãéèêíìîóòôõúùû][mn][aeiouáàâãéèêíìîóòôõúùû]',
        "comentario": "Separação de encontros vocálicos nasalizados",
        "exemplos": ["criança", "lâmina"]
    },
    "nomes_proprios": {
        "regex": r'[A-ZÁÀÂÃÉÈÊÍÌÎÓÒÔÕÚÙÛ][a-záàâãéèêíìîóòôõúùû]+[aeiouáàâãéèêíìîóòôõúùû][aeiouáàâãéèêíìîóòôõúùû]',
        "comentario": "Separação de hiatos em nomes próprios",
        "exemplos": ["Luís", "Raul"]
    },
    "prefixos_vogais": {
        "regex": r'[a-záàâãéèêíìîóòôõúùû]+(a|e|i|o|u)[aeiouáàâãéèêíìîóòôõúùû]',
        "comentario": "Prefixos terminados em vogal + palavra iniciada por vogal",
        "exemplos": ["contraataque", "autoestima"]
    },
    "sufixos_diminutivos": {
        "regex": r'[aeiouáàâãéèêíìîóòôõúùû](zinho|zinha)',
        "comentario": "Separação de sufixos diminutivos",
        "exemplos": ["cafezinho", "florzinha"]
    },
    "estrangeirismos": {
        "regex": r'[^aeiouáàâãéèêíìîóòôõúùû][aeiouáàâãéèêíìîóòôõúùû]{2}',
        "comentario": "Separação de ditongos em palavras de origem estrangeira",
        "exemplos": ["museu", "basileu"]
    },
    "proparoxitonas": {
        "regex": r'[áàâãéèêíìîóòôõúùû][^aeiouáàâãéèêíìîóòôõúùû][aeiouáàâãéèêíìîóòôõúùû]$',
        "comentario": "Separação de terminações vocálicas em palavras proparoxítonas",
        "exemplos": ["história", "série"]
    }
}

# Regras de hifenização tipográfica para palavras específicas
REGRAS_ESPECIFICAS = {
    "sábio": {"divisao": "sábio", "comentario": "Separação de ditongos crescentes"},
    "ideia": {"divisao": "idei-a", "comentario": "Separação de hiatos em final de palavra"},
    "história": {"divisao": "histó-ria", "comentario": "Separação de terminações vocálicas em palavras proparoxítonas"},
    "coordenar": {"divisao": "coor-denar", "comentario": "Separação de vogais idênticas contíguas"},
    "museu": {"divisao": "museu", "comentario": "Separação de ditongos em palavras de origem estrangeira"},
    "criança": {"divisao": "crian-ça", "comentario": "Separação de encontros vocálicos nasalizados"},
    "frequente": {"divisao": "frequen-te", "comentario": "Separação de grupos consonantais especiais (qu/gu)"},
    "raul": {"divisao": "raul", "comentario": "Separação de hiatos em nomes próprios curtos"},
    "contraataque": {"divisao": "contra-ataque", "comentario": "Separação de vogais contíguas em composições"},
    "cafezinho": {"divisao": "café-zinho", "comentario": "Separação de sufixos diminutivos"},
    "série": {"divisao": "série", "comentario": "Separação de ditongos crescentes"},
    "ódio": {"divisao": "ódio", "comentario": "Separação de ditongos crescentes"},
    "microonda": {"divisao": "micro-onda", "comentario": "Separação de vogais idênticas contíguas"},
    "ambíguo": {"divisao": "ambí-guo", "comentario": "Separação de grupos consonantais especiais (qu/gu)"},
    "luís": {"divisao": "luís", "comentario": "Separação de hiatos em nomes próprios curtos"},
    "autoestima": {"divisao": "auto-estima", "comentario": "Prefixos terminados em vogal + palavra iniciada por vogal"},
    "florzinha": {"divisao": "flor-zinha", "comentario": "Separação de sufixos diminutivos"},
    "basileu": {"divisao": "basileu", "comentario": "Separação de ditongos em palavras de origem estrangeira"},
}


def gerar_hyphenation_sty(palavras_problematicas, arquivo_saida="hyphenation.sty"):
    """Gera o arquivo hyphenation.sty com as palavras problemáticas e suas variantes maiúsculas/minúsculas"""
    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        f.write("% Arquivo de hifenização tipográfica especial\n")
        f.write("% Gerado automaticamente para ajuste tipográfico\n\n")
        
        for tipo, palavras in palavras_problematicas.items():
            f.write(f"% {tipo}\n")
            for p in palavras:
                palavra = p['palavra']
                divisao = p['divisao']
                
                f.write(f"% Palavra: {palavra}\n")
                
                if divisao != "verificar":
                    # Gerar variantes de capitalização
                    if divisao == palavra.lower():  # Sem hífens
                        f.write(f"\\hyphenation{{{divisao} {divisao.capitalize()} {divisao.upper()}}}\n\n")
                    else:  # Com hífens
                        # Para palavras com hífen, precisamos tratar cada parte
                        partes = divisao.split('-')
                        partes_cap = [p.capitalize() for p in partes]
                        partes_up = [p.upper() for p in partes]
                        
                        divisao_cap = '-'.join(partes_cap)
                        divisao_up = '-'.join(partes_up)
                        
                        f.write(f"\\hyphenation{{{divisao}}}\n")
                        f.write(f"\\hyphenation{{{divisao_cap}}}\n")
                        f.write(f"\\hyphenation{{{divisao_up}}}\n\n")
                else:
                    f.write(f"% ATENÇÃO: Verificar hifenização da palavra '{palavra}'\n")
                    f.write(f"% \\hyphenation{{{palavra}}}\n")
                    f.write(f"% \\hyphenation{{{palavra.capitalize()}}}\n")
                    f.write(f"% \\hyphenation{{{palavra.upper()}}}\n\n")

def extrair_palavras_tex(arquivo_tex):
    """Extrai palavras de um arquivo .tex"""
    with open(arquivo_tex, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Remove comandos LaTeX e ambientes matemáticos
    conteudo = re.sub(r'\\[a-zA-Z]+(\{[^}]*\})*', ' ', conteudo)
    conteudo = re.sub(r'\$[^$]*\$', ' ', conteudo)
    
    # Extrai palavras, incluindo acentuadas
    palavras = re.findall(r'\b[a-záàâãéèêíìîóòôõúùûçA-ZÁÀÂÃÉÈÊÍÌÎÓÒÔÕÚÙÛÇ]+\b', conteudo, re.UNICODE)
    return set(palavras)

def identificar_palavras_problematicas(palavras):
    """Identifica palavras que seguem padrões problemáticos de hifenização"""
    palavras_problematicas = defaultdict(list)
    
    # Verificar palavras já conhecidas
    for palavra in palavras:
        palavra_lower = palavra.lower()
        if palavra_lower in REGRAS_ESPECIFICAS:
            palavras_problematicas[REGRAS_ESPECIFICAS[palavra_lower]["comentario"]].append({
                "palavra": palavra,
                "divisao": REGRAS_ESPECIFICAS[palavra_lower]["divisao"]
            })
            continue
            
        # Verificar padrões problemáticos
        for tipo, info in PADROES_PROBLEMATICOS.items():
            if re.search(info["regex"], palavra_lower):
                # Adicionar apenas se ainda não foi adicionada em outra categoria
                already_added = False
                for _, palavras_lista in palavras_problematicas.items():
                    if any(p["palavra"] == palavra for p in palavras_lista):
                        already_added = True
                        break
                
                if not already_added:
                    divisao = "verificar"
                    # Tentar determinar a divisão tipográfica
                    if tipo == "hiatos_final" and palavra_lower.endswith("ia"):
                        divisao = palavra_lower[:-2] + "-ia"
                    elif tipo == "grupos_qu_gu" and ("quen" in palavra_lower or "guen" in palavra_lower):
                        divisao = palavra_lower.replace("quen", "quen-").replace("guen", "guen-")
                    elif tipo == "sufixos_diminutivos" and ("zinho" in palavra_lower or "zinha" in palavra_lower):
                        divisao = palavra_lower.replace("zinho", "-zinho").replace("zinha", "-zinha")
                    
                    palavras_problematicas[info["comentario"]].append({
                        "palavra": palavra,
                        "divisao": divisao
                    })
                
    return palavras_problematicas

def gerar_hyphenation_sty(palavras_problematicas, arquivo_saida="hyphenation.sty"):
    """Gera o arquivo hyphenation.sty com as palavras problemáticas e suas variantes maiúsculas/minúsculas"""
    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        f.write("% Arquivo de hifenização tipográfica especial\n")
        f.write("% Gerado automaticamente para ajuste tipográfico\n\n")
        
        for tipo, palavras in palavras_problematicas.items():
            f.write(f"% {tipo}\n")
            for p in palavras:
                palavra = p['palavra']
                divisao = p['divisao']
                
                # Adicionar informação sobre divisão silábica gramatical
                divisao_gramatical = obter_divisao_gramatical(palavra)
                
                f.write(f"% Palavra: {palavra}\n")
                f.write(f"% Divisão silábica gramatical: {divisao_gramatical}\n")
                
                if divisao != "verificar":
                    # Versão original (minúscula)
                    f.write(f"\\hyphenation{{{divisao}}}\n")
                    
                    # Versão com inicial maiúscula (apenas a primeira letra maiúscula)
                    if '-' in divisao:
                        partes = divisao.split('-')
                        # Apenas a primeira letra da primeira parte fica maiúscula
                        partes_cap = [partes[0].capitalize()] + partes[1:]
                        divisao_cap = '-'.join(partes_cap)
                        f.write(f"\\hyphenation{{{divisao_cap}}}\n")
                    else:
                        f.write(f"\\hyphenation{{{divisao.capitalize()}}}\n")
                    
                    # Versão toda maiúscula
                    f.write(f"\\hyphenation{{{divisao.upper()}}}\n\n")
                else:
                    f.write(f"% ATENÇÃO: Verificar hifenização da palavra '{palavra}'\n")
                    f.write(f"% \\hyphenation{{{palavra}}}\n")
                    f.write(f"% \\hyphenation{{{palavra.capitalize()}}}\n")
                    f.write(f"% \\hyphenation{{{palavra.upper()}}}\n\n")

def obter_divisao_gramatical(palavra):
    """Função auxiliar para obter divisão silábica gramatical da palavra"""
    # Aqui você pode implementar um algoritmo para divisão silábica gramatical
    # ou usar um dicionário predefinido para palavras comuns
    
    # Exemplo de implementação simplificada (dicionário predefinido)
    divisoes_gramaticais = {
        "sábio": "sá-bio",
        "ideia": "i-dei-a",
        "história": "his-tó-ria",
        "coordenar": "co-or-de-nar",
        "museu": "mu-seu",
        "criança": "cri-an-ça",
        "frequente": "fre-quen-te",
        "raul": "ra-ul",
        "contraataque": "con-tra-a-ta-que",
        "cafezinho": "ca-fe-zi-nho",
        "série": "sé-rie",
        "ódio": "ó-dio",
        "microonda": "mi-cro-on-da",
        "ambíguo": "am-bí-guo",
        "luís": "lu-ís",
        "autoestima": "au-to-es-ti-ma",
        "florzinha": "flor-zi-nha",
        "basileu": "ba-si-leu",
    }
    
    palavra_lower = palavra.lower()
    if palavra_lower in divisoes_gramaticais:
        return divisoes_gramaticais[palavra_lower]
    else:
        # Se não estiver no dicionário, retornar "não disponível"
        # Aqui você poderia implementar um algoritmo automático para divisão silábica
        return "não disponível"

def processar_arquivos_tex(diretorio=".", saida="hyphenation.sty"):
    """Processa todos os arquivos .tex em um diretório"""
    todas_palavras = set()
    
    # Encontrar todos os arquivos .tex
    for raiz, _, arquivos in os.walk(diretorio):
        for arquivo in arquivos:
            if arquivo.endswith('.tex'):
                caminho_completo = os.path.join(raiz, arquivo)
                print(f"Processando {caminho_completo}...")
                palavras = extrair_palavras_tex(caminho_completo)
                todas_palavras.update(palavras)
    
    print(f"Total de palavras únicas encontradas: {len(todas_palavras)}")
    
    # Adicionar manualmente algumas palavras que queremos verificar
    todas_palavras.update(["sábio", "ideia", "história", "coordenar", "museu", 
                          "criança", "frequente", "raul", "contraataque", "cafezinho"])
    
    # Identificar palavras problemáticas
    palavras_problematicas = identificar_palavras_problematicas(todas_palavras)
    
    # Gerar arquivo de saída
    gerar_hyphenation_sty(palavras_problematicas, saida)
    print(f"Arquivo {saida} gerado com sucesso!")
    
    # Estatísticas
    total_problematicas = sum(len(palavras) for palavras in palavras_problematicas.values())
    print(f"Total de palavras com potenciais problemas de hifenização: {total_problematicas}")
    for tipo, palavras in palavras_problematicas.items():
        print(f"  • {tipo}: {len(palavras)} palavras")

if __name__ == "__main__":
    import sys
    diretorio = sys.argv[1] if len(sys.argv) > 1 else "."
    saida = sys.argv[2] if len(sys.argv) > 2 else "hyphenation.sty"
    processar_arquivos_tex(diretorio, saida)