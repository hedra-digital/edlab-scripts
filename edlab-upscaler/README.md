# EdLab-Upscaler

Script Python para aumentar a resolução de imagens usando o modelo Real-ESRGAN.

## Características

- Suporta escalas de 2x e 4x
- Processa arquivos individuais ou diretórios completos
- Mantém backup automático das imagens originais
- Suporta formatos: PNG, JPG, JPEG, WEBP
- Permite filtrar imagens por tamanho (KB)
- Usa GPU se disponível, caso contrário usa CPU

## Requisitos

- Python 3.12+
- PyTorch
- Pillow
- NumPy

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/edlab-upscaler.git
cd edlab-upscaler
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install torch torchvision pillow numpy
```

## Uso

### Sintaxe básica:
```bash
python edlab-upscaler.py -i ENTRADA [-s ESCALA] [-m MIN_SIZE] [-M MAX_SIZE]
```

### Opções:
- `-i, --input`: Caminho para imagem(ns) ou diretório
- `-s, --scale`: Fator de escala (2 ou 4, padrão: 4)
- `-m, --min-size`: Tamanho mínimo em KB para processar a imagem
- `-M, --max-size`: Tamanho máximo em KB para processar a imagem

### Exemplos:

1. Processar uma única imagem:
```bash
python edlab-upscaler.py -i imagem.jpg
```

2. Processar todas as imagens de um diretório:
```bash
python edlab-upscaler.py -i .
```

3. Usar escala 2x ao invés de 4x:
```bash
python edlab-upscaler.py -i imagem.jpg -s 2
```

4. Processar apenas imagens entre 30KB e 100KB:
```bash
python edlab-upscaler.py -i . -m 30 -M 100
```

5. Processar apenas imagens menores que 50KB:
```bash
python edlab-upscaler.py -i . -M 50
```

### Organização dos arquivos:

O script mantém a seguinte estrutura:
```
diretório/
├── imagem.jpg          # Imagem processada
├── old_images/         # Pasta de backup
│   └── imagem.jpg     # Imagem original
```

## Limitações

- Para processamento em GPU, é necessário ter CUDA instalado
- O tempo de processamento pode variar dependendo do tamanho da imagem e do hardware disponível

## Créditos

Este script utiliza o modelo Real-ESRGAN para super-resolução de imagens.
- [Real-ESRGAN (GitHub)](https://github.com/xinntao/Real-ESRGAN)

## Licença

MIT License