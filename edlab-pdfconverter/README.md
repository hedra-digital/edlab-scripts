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

# Descrição


## Remover o texto do PDF e dar um crop no pdf final

```
./Delete_Texts_From_PDF_And_Convert_To_PNG_After_Crop.py -i input.pdf -o output.pdf -d output_images -m '10 10 10 10'
```

## Remover o texto do PDF e converter todas as páginas para PNG:
```
./Delete_Texts_From_PDF_And_Convert_To_PNG_After_Crop.py -i input.pdf -o output.pdf -d img
```

Isso vai gerar o arquivo output.pdf e converter todas as páginas do PDF para imagens PNG no diretório img.

## Remover o texto e converter apenas algumas páginas (ex: 1 a 3):
```
./Delete_Texts_From_PDF_And_Convert_To_PNG_After_Crop.py -i input.pdf -o output.pdf -d img -p 1-3
```

Isso irá converter apenas as páginas 1 a 3 do PDF para PNG no diretório img.

## Remover o texto e converter apenas uma página (ex: página 1):

```
./Delete_Texts_From_PDF_And_Convert_To_PNG_After_Crop.py -i input.pdf -o output.pdf -d img -p 1
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

## GPT

https://chatgpt.com/share/6709752c-80a0-8004-be01-d1d1b5a6033f


## Install

Se você usa bash, edite o arquivo .bashrc ou .bash_profile:

```
subl ~/.bashrc
```

Adicione a seguinte linha ao final do arquivo:
```
export PATH="$HOME/bin:$PATH"
```

Salve e feche o arquivo. Depois, rode:
```
source ~/.bashrc
```

Se você usa zsh, edite o arquivo .zshrc:
```
subl ~/.zshrc
```

Adicione a mesma linha:
```
export PATH="$HOME/bin:$PATH"
```

Salve e rode:
```
source ~/.zshrc
```

