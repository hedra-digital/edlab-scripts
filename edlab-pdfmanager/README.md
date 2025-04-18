# edlab-pdfmanager

Uma ferramenta de linha de comando para manipulação avançada de arquivos PDF.

## Instalação

## Requisitos de Sistema

- Python 3.6+
- Ghostscript
- pdfcrop (para corte de margens)
- Espaço em disco suficiente para processamento de arquivos

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install ghostscript pdftk texlive-extra-utils poppler-utils python3-pypdf2 python3-pdfminer.six python3-reportlab python3-tqdm python3-pil python3-fitz python3-pdf2docx
```

### Arch Linux/Manjaro
```bash
yay -S ghostscript pdftk pdfcrop python-pypdf2 python-pdf2image python-pdfminer.six python-reportlab python-tqdm python-fitz python-pillow python-pdf2docx
sudo pacman -S protobuf
sudo pacman -S opencv
sudo pacman -S openexr
```

### Instalação de uma máquina virtual

```
# Instalar também dependências do sistema
sudo apt-get update
sudo apt-get install -y \
    ghostscript \
    pdftk \
    texlive-extra-utils \
    python3-pip \
    poppler-utils

# Criar e ativar ambiente virtual (opcional, mas recomendado)
python3 -m venv venv
source venv/bin/activate

# Instalar dependências Python
pip install PyPDF2 pdf2image pdfminer.six reportlab tqdm PyMuPDF Pillow pdf2docx
```

### Instalação do edlab-pdfmanager

1. Clone o repositório:
```bash
git clone git@github.com:hedra-digital/edlab-scripts.git
cd edlab-pdfmanager
```

2. Instalação usando Make:
```bash
sudo make install
```

Isto instalará o script em `/usr/local/bin`, tornando-o disponível globalmente no sistema.


## Recursos

- Juntar múltiplos PDFs
- Comprimir PDFs
- Converter cores (preto chapado ou escala de cinza)
- Remover texto
- Cortar margens
- Extrair páginas específicas
- Converter para imagens
- Adicionar marca d'água
- Analisar cores
- Extrair texto
- Contagem de páginas
- Converter para DOCX

## Uso

### Exemplos básicos

```bash
# Juntar PDFs
./edlab-pdfmanager -i arquivo1.pdf arquivo2.pdf -j

# Comprimir PDF
./edlab-pdfmanager -i input.pdf --shrink 150

# Converter para preto chapado
./edlab-pdfmanager -i input.pdf --convert-to-black

# Converter para escala de cinza
./edlab-pdfmanager -i input.pdf --convert-to-gray

# Extrair páginas específicas
./edlab-pdfmanager -i input.pdf -p 1-3 -o output.pdf

# Adicionar marca d'água
./edlab-pdfmanager -i input.pdf -w "CONFIDENCIAL"

# Converter para DOCX
./edlab-pdfmanager -i input.pdf --extract-to-docx
```

### Opções avançadas

```bash
# Juntar PDFs com páginas em branco entre eles
./edlab-pdfmanager -i arquivo1.pdf BLANK arquivo2.pdf -j

# Comprimir com resolução específica
./edlab-pdfmanager -i input.pdf --shrink 200

# Extrair páginas e converter para imagens
./edlab-pdfmanager -i input.pdf -p 1-3 -d imagens/

# Remover texto e cortar margens
./edlab-pdfmanager -i input.pdf -rt -m "10 10 10 10"

# Analisar cores no PDF
./edlab-pdfmanager -i input.pdf --check-color

# Contar páginas
./edlab-pdfmanager -i *.pdf --page-counter
```

## Argumentos

| Argumento | Descrição |
|-----------|-----------|
| `-i, --input` | Arquivo(s) PDF de entrada |
| `-o, --output` | Arquivo de saída |
| `-m, --margins` | Margens para corte (ex: "10 10 10 10") |
| `-d, --dir` | Diretório para salvar imagens |
| `-p, --pages` | Intervalo de páginas (ex: "1-3") |
| `-f, --format` | Formato de imagem (jpeg/png) |
| `-rt, --remove-text` | Remove texto do PDF |
| `-j, --join` | Junta PDFs |
| `-w, --watermark` | Adiciona marca d'água |
| `--shrink` | Comprime PDF (DPI 72-300) |
| `--check-color` | Analisa cores no PDF |
| `--convert-to-black` | Converte para preto chapado |
| `--convert-to-gray` | Converte para escala de cinza |
| `--extract-to-docx` | Converte para DOCX |
| `--page-counter` | Conta páginas dos PDFs |


## Desenvolvimento e Testes

O projeto inclui um Makefile para facilitar o desenvolvimento e testes:

### Comandos do Makefile

```bash
# Instalar globalmente
make install

# Executar todos os testes
make test

# Limpar arquivos gerados
make clean
```

### Testes Disponíveis

O Makefile inclui 11 testes que verificam diferentes funcionalidades:

1. Cortar margens, extrair páginas, remover texto e converter para PNG
2. Juntar PDFs
3. Testar contador de páginas
4. Extrair texto
5. Adicionar marca d'água
6. Verificar cores
7. Contar páginas
8. Comprimir PDF
9. Converter para preto chapado
10. Converter para escala de cinza
11. Converter para DOCX

Para executar um teste específico, você pode verificar o Makefile e rodar o comando manualmente.

## Notas

- Os arquivos processados são salvos com sufixos apropriados (ex: `_compressed`, `_black`, `_gray`)
- Para junção de PDFs com páginas em branco, use "BLANK" como nome de arquivo
- A compressão usa Ghostscript com configurações otimizadas
- A conversão para preto chapado mantém áreas totalmente brancas

## Licença

Este projeto é distribuído sob a licença MIT.
