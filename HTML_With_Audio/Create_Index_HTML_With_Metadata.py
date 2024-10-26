import re
import os

def encontrar_arquivo_html_extremos(diretorio):
    # Listar todos os arquivos HTML no diretório
    arquivos_html = [f for f in os.listdir(diretorio) if re.match(r'pag-(\d+(-\d+)?)\.html', f)]
    
    # Se não houver arquivos HTML, retorna None para menor e maior
    if not arquivos_html:
        return None, None

    # Extrair os números dos arquivos e ordená-los
    numeros_arquivos = []
    for arquivo in arquivos_html:
        match = re.match(r'pag-(\d+(-\d+)?)\.html', arquivo)
        if match:
            numero_str = match.group(1)
            numeros_arquivos.append((numero_str, arquivo))

    # Ordenar pelo valor numérico do número principal
    numeros_arquivos.sort(key=lambda x: int(x[0].split('-')[0]))

    # Retornar o arquivo de menor número e o de maior número
    return numeros_arquivos[0][1], numeros_arquivos[-1][1]

def preencher_metadados(arquivo_entrada, arquivo_saida):
    # Lê o arquivo de entrada para extrair os valores dos metadados
    metadados = {}
    with open(arquivo_entrada, 'r', encoding='utf-8') as entrada:
        for linha in entrada:
            match = re.match(r'(\w+)=(.+)', linha.strip())  # Padrão chave=valor
            if match:
                chave, valor = match.groups()
                metadados[chave] = valor.strip()

    # Encontra o arquivo de menor número e o de maior número no diretório
    menor_html, maior_html = encontrar_arquivo_html_extremos('.')

    # Estrutura completa do index.html com placeholders para os metadados
    html_base = f"""<!--?xml version="1.0" encoding="utf-8"?--><!DOCTYPE html>
<html lang="pt-BR" xml:lang="pt-BR" xmlns="http://www.w3.org/1999/xhtml"><head>
  <title>{metadados.get('title', '')}</title>
  <link href="resources/styles/global.css" type="text/css" rel="stylesheet">
  <meta content="{metadados.get('description', '')}" name="description">
  <meta content="{metadados.get('author', '')}" name="author">
  <meta charset="utf-8">
  <meta content="noindex, nofollow" name="robots">
  <meta content="IE=edge" http-equiv="X-UA-Compatible"></head>

<body lang="pt-BR" xml:lang="pt-BR">
<div itemscope="" itemtype="https://schema.org/Book">
  <meta itemprop="accessibilityFeature" content="largePrint/CSSEnabled">
  <meta itemprop="accessibilityFeature" content="highContrast/CSSEnabled">
  <meta itemprop="accessibilityFeature" content="resizeText/CSSEnabled">
  <meta itemprop="accessibilityFeature" content="displayTransformability">
  <meta itemprop="accessibilityFeature" content="longDescription">
  <meta itemprop="accessibilityFeature" content="alternativeText">
  <meta itemprop="accessibilityControl" content="fullKeyboardControl">
  <meta itemprop="name" content="{metadados.get('title', '')}">
  <meta itemprop="description" content="{metadados.get('description', '')}">
  <meta itemprop="isbn" content="{metadados.get('isbn', '')}">
  <meta itemprop="copyrightYear" content="{metadados.get('copyrightYear', '')}">
  <meta itemprop="publisher" content="{metadados.get('publisher', '')}">
</div>
  <main><!--<h1 title="Capa do livro do estudante" id="cover"></h1>-->

  <figure class="FigCenter">
    <img id="cover" src="resources/img/cover.jpg" alt="">
  </figure>

  <!--<h1 title="Folha de rosto" id="titlepage"></h1>-->

  <figure class="FigCenter">
    <img id="titlepage" alt="" src="resources/img/page_1-01.jpg">
  </figure>

  <!--<h1 title="Crédito" id="credits"></h1>-->

  <figure class="FigCenter">
    <img id="credits" src="resources/img/page_2-02.jpg" alt="">
  </figure>
  
  <nav id="toc" role="doc-toc"><p class="SumaToc">Sumário</p>
  <ol>
    <li><a href="index.html#cover">Capa do livro</a></li>
    <li><a href="index.html#titlepage">Folha de rosto</a></li>
    <li><a href="index.html#credits">Créditos</a></li>
    <li><a href="content/{menor_html}">Início do texto</a></li>
    <li><a href="content/{maior_html}">Fim do texto</a></li>
    <li><a href="content/quarta-capa.html">Quarta Capa</a></li>
  </ol></nav></main>

</body></html>
    """

    # Escreve o HTML gerado no arquivo de saída
    with open(arquivo_saida, 'w', encoding='utf-8') as saida:
        saida.write(html_base)

    print(f"Arquivo {arquivo_saida} criado com sucesso.")

# Exemplo de uso:
arquivo_entrada = 'metadados.txt'  # Arquivo de entrada contendo os valores
arquivo_saida = 'index.html'  # Nome do arquivo HTML de saída
preencher_metadados(arquivo_entrada, arquivo_saida)
