# Histórico
No PNLD2026, precisamos criar imagens a partir dos PDFs para para o HTML. Essas imagens precisavam ser cropadas e sem o texto do livro. 

# Dependências
```
sudo pacman -S ghostscript poppler  # Para Ghostscript e pdf2image

sudo pacman -S yay
yay -S python-pdf2image python-pillow  # Usando yay para instalar pdf2image e Pillow do AUR
yay -S python-pypdf2

sudo pacman -S texlive-core # para o pdfcrop

```

## Instalação no Ubuntu

```
sudo apt update

pip3 install --break-system-packages pdf2image Pillow PyPDF2
```

# Descrição


## Remover o texto do PDF e dar um crop no pdf final

```
./edlab-pdfconverter -i input.pdf -o output.pdf -d output_images -m '10 10 10 10'
```

## Remover o texto do PDF e converter todas as páginas para PNG:
```
./edlab-pdfconverter -i input.pdf -o output.pdf -d img
```

Isso vai gerar o arquivo output.pdf e converter todas as páginas do PDF para imagens PNG no diretório img.

## Remover o texto e converter apenas algumas páginas (ex: 1 a 3):
```
./edlab-pdfconverter -i input.pdf -o output.pdf -d img -p 1-3
```

Isso irá converter apenas as páginas 1 a 3 do PDF para PNG no diretório img.

## Remover o texto e converter apenas uma página (ex: página 1):

```
./edlab-pdfconverter -i input.pdf -o output.pdf -d img -p 1
```

Isso converterá apenas a página 1 do PDF em PNG.

# Opções

```
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Caminho para o arquivo PDF de entrada.
  -o OUTPUT, --output OUTPUT
                        Caminho para o arquivo PDF de saída.
  -m MARGINS, --margins MARGINS
                        Margens para o corte com pdfcrop. Use um valor ou quatro valores para margens separadas (esquerda, direita, cima, baixo).
  -d DIR, --dir DIR     Diretório onde as imagens serão salvas.
  -p PAGES, --pages PAGES
                        Intervalo de páginas para processar, por exemplo '1-3' ou '1'.
  -f FORMAT, --format FORMAT
                        Formato da imagem de saída (jpeg ou png). Padrão: jpeg.
  -rt, --remove-text    Remove o texto do PDF antes de cortar margens e converter em imagens.
```



## Sobre as margens

Você pode especificar as margens que deseja passar para o pdfcrop usando a opção -m ou --margins.
As margens podem ser especificadas de duas formas:
* Um único valor (exemplo: -m 10), que aplica o mesmo valor de margem em todos os lados.
* Quatro valores separados (exemplo: -m '5 10 5 10'), aplicando valores separados para esquerda, direita, cima e baixo.



## Makefine

`make install`  : para instalar
`make test` : para testar
`make clean` : para limpar os testes
 