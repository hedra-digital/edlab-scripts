# Grab_Text_From_Image.py

## História

Estávamos preparando os HTMLs para o PNLD2026 e eu precisei tirar textos diretamente das imagens. 
Geralmente tiramos os textos do PDF, mas em alguns casos específicos, o designer exportou as fontes
como imagens. Só restava transcrever na mão ou fazer um script. O resultado do texto não é uma 
maravilha, mas já ajuda bastante. 

## Dependências

```
sudo pacman -S python python-pip
sudo pacman -S python-pytesseract python-pillow
sudo pacman -S tesseract-data-eng
sudo pacman -S tesseract-data-por
```

## Modo de usar

```
python3 Grab_Text_From_Image.py exemplos/img -o teste.md
```
