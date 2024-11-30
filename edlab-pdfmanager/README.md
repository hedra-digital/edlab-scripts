# edlab-pdfmanager

Uma ferramenta de linha de comando para manipulação avançada de arquivos PDF.

## Instalação

### Dependências

#### Ubuntu/Debian
```bash
# Instalar dependências do sistema
sudo apt-get update
sudo apt-get install -y \
    ghostscript \
    pdftk \
    texlive-extra-utils \
    python3-pip \
    python3-venv \
    poppler-utils

```

#### Arch Linux
```bash
yay -S ghostscript pdftk pdfcrop python-pypdf2 python-pdf2image python-pdfminer.six python-reportlab python-tqdm python-fitz python-pillow python-pdf2docx
```

#### Instalação de uma máquina virtual

```
# Criar e ativar ambiente virtual (opcional, mas recomendado)
python3 -m venv venv
source venv/bin/activate

# Instalar dependências Python
pip install PyPDF2 pdf2image pdfminer.six reportlab tqdm PyMuPDF Pillow pdf2docx
```

### Instalação do edlab-pdfmanager

1. Clone o repositório:
```bash
git clone [URL_DO_REPOSITORIO]
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

[... resto do README anterior ...]

## Estrutura do Projeto

```
edlab-pdfmanager/
├── edlab-pdfmanager  # Script principal
├── Makefile          # Automação de instalação e testes
├── README.md         # Documentação
└── tests/            # Arquivos de teste
    ├── input.pdf
    └── ...
```

## Desenvolvimento

Para contribuir com o projeto:

1. Certifique-se de que todos os testes passam: `make test`
2. Limpe os arquivos de teste antes de commits: `make clean`
3. Adicione novos testes ao Makefile quando implementar novas funcionalidades

# edlab-pdfmanager

Uma ferramenta de linha de comando para manipulação avançada de arquivos PDF.


## Notas

- Os arquivos processados são salvos com sufixos apropriados (ex: `_compressed`, `_black`, `_gray`)
- Para junção de PDFs com páginas em branco, use "BLANK" como nome de arquivo
- A compressão usa Ghostscript com configurações otimizadas
- A conversão para preto chapado mantém áreas totalmente brancas

## Requisitos de Sistema

- Python 3.6+
- Ghostscript
- pdfcrop (para corte de margens)
- Espaço em disco suficiente para processamento de arquivos

## Licença

Este projeto é distribuído sob a licença MIT.