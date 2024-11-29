# PDF Compression Script

Um script em Python para comprimir arquivos PDF usando Ghostscript. O script permite controlar a resolução das imagens (DPI) para ajustar o nível de compressão.

## Requisitos

### Python
- Python 3.x

### Dependências do Sistema
No Arch Linux/Manjaro:
```bash
sudo pacman -S ghostscript
```

No Ubuntu/Debian:
```bash
sudo apt-get install ghostscript
```

No CentOS/RHEL:
```bash
sudo yum install ghostscript
```

## Instalação

1. Clone o repositório ou baixe o script `shrink.py`
2. Certifique-se de que o script tem permissão de execução:
```bash
chmod +x shrink.py
```

## Uso

O script aceita dois parâmetros:
- `-i` ou `--input`: Arquivo PDF de entrada (obrigatório)
- `--shrink`: Resolução das imagens em DPI (opcional, padrão: 150)

### Exemplos de Uso

Usar resolução padrão (150 DPI):
```bash
python shrink.py -i arquivo.pdf
```

Especificar uma resolução personalizada:
```bash
python shrink.py -i arquivo.pdf --shrink 300  # Máxima qualidade
python shrink.py -i arquivo.pdf --shrink 150  # Qualidade média
python shrink.py -i arquivo.pdf --shrink 72   # Menor qualidade
```

### Referência de Valores DPI

- 300 DPI: Qualidade para impressão
- 150 DPI: Bom equilíbrio entre qualidade e tamanho
- 100 DPI: Qualidade web
- 72 DPI: Menor qualidade aceitável

**Nota**: A resolução deve estar entre 72 e 300 DPI.

## Saída

O script criará um novo arquivo com o sufixo '_compressed' mantendo o arquivo original intacto. Por exemplo:
- Entrada: documento.pdf
- Saída: documento_compressed.pdf

O script também mostrará informações sobre:
- Tamanho original do arquivo
- Tamanho do arquivo comprimido
- Porcentagem de redução alcançada
- Resolução (DPI) usada

## Limitações

- O script requer que o Ghostscript esteja instalado no sistema
- A compressão é mais efetiva em PDFs com imagens
- O resultado final pode variar dependendo do conteúdo do PDF original