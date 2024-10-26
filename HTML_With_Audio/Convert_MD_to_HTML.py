import os
import re
import sys

# Função para converter o conteúdo markdown em HTML básico
def markdown_para_html(linha):
    # Verificar se a linha contém uma imagem no formato markdown ![alt_text](image_path)
    imagem_match = re.match(r'!\[.*?\]\((.*?)\)', linha)
    if imagem_match:
        imagem_path = imagem_match.group(1)
        return f'''
        <figure class="img">
            <img class="fig-2" src="../resources/img/{imagem_path}" alt="">
        </figure>
        '''
    else:
        return f"<p>{linha.strip()}</p>"

def processar_arquivo_md(nome_arquivo_md, titulo):
    with open(nome_arquivo_md, 'r', encoding='utf-8') as arquivo_md:
        conteudo_md = arquivo_md.read()

    paginas = re.split(r'\[Página (\d+)\]', conteudo_md)  # Dividir por [Página X]
    paginas = [p.strip() for p in paginas if p.strip()]  # Remover espaços em branco vazios

    for i in range(1, len(paginas), 2):  # Páginas pares são números, ímpares são conteúdos
        numero_pagina = paginas[i - 1]  # Pega o número da página
        conteudo_pagina = paginas[i]  # Pega o conteúdo da página

        # Converter conteúdo markdown para HTML, incluindo imagens
        conteudo_html = '\n'.join(markdown_para_html(linha) for linha in conteudo_pagina.splitlines())

        # Determinar os valores para prev e next, com zero à esquerda para números menores que 10
        prev_page = int(numero_pagina) - 1
        next_page = int(numero_pagina) + 1

        prev_page_str = f"pag-{str(prev_page).zfill(2)}.html" if prev_page > 0 else ""
        next_page_str = f"pag-{str(next_page).zfill(2)}.html"

        # Criação do conteúdo HTML com preâmbulo
        html = f"""<!--?xml version="1.0" encoding="utf-8"?--><!DOCTYPE html>
<html lang="pt-BR" xml:lang="pt-BR" xmlns="http://www.w3.org/1999/xhtml"><head>
  <title>{titulo}</title>
  <link href="../resources/styles/global.css" type="text/css" rel="stylesheet">
  <meta charset="utf-8">
  <meta content="noindex, nofollow" name="robots">
  <meta content="IE=edge" http-equiv="X-UA-Compatible">
</head>

<body lang="pt-BR" xml:lang="pt-BR">
<div itemscope="" itemtype="https://schema.org/Book">
  <meta itemprop="accessibilityFeature" content="longDescription">
  <meta itemprop="accessibilityFeature" content="alternativeText">
  <meta itemprop="accessibilityControl" content="fullKeyboardControl">
</div>

<main>
<nav class="navbar">
  <ol>
    <li class="toc"><a href="../index.html#toc">Sumário</a></li>
    {"<li class='prev'><a href='" + prev_page_str + "'>Anterior</a></li>" if prev_page > 0 else ""}
    <li class="next"><a href="{next_page_str}">Próximo</a></li>
  </ol>
</nav>

<p class="numeracao" title="{numero_pagina}" id="p{numero_pagina}" role="doc-pagebreak">{numero_pagina}</p>

{conteudo_html}

<script src="../sync.js"></script>
</main>
</body>
</html>"""

        # Salvar o conteúdo HTML em um novo arquivo
        nome_arquivo_html = f"pag-{numero_pagina.zfill(2)}.html"
        with open(nome_arquivo_html, 'w', encoding='utf-8') as arquivo_html:
            arquivo_html.write(html)

        print(f'Página {numero_pagina} salva como {nome_arquivo_html}.')

# Captura de parâmetros da linha de comando
if len(sys.argv) != 3:
    print("Uso: python3 html.py <arquivo_md> <título>")
else:
    arquivo_md = sys.argv[1]
    titulo = sys.argv[2]
    processar_arquivo_md(arquivo_md, titulo)
