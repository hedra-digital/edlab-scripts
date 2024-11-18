# arquivo-thumbs

## Roteiro

1. Converter a(s) imagen(s) para `*.png`
2. Melhorar a imagem com os comandos abaixo:
```
mogrify -fuzz 15% -trim +repage *.png
mogrify -resize 200 *.png
```
3. Colocar as imagens na pasta `./input_images`
4. Rodar o comando `python3 coversquare.py` na raiz da pasta.

## História 

1. Criei um script para arrancar capas do CSV do Odoo
2. Converti e tratei imagens com `mogrify`
```
mogrify -fuzz 15% -trim +repage *.png
mogrify -resize 200 *.png
```
3. Coloquei na arte do site com o script `./python 3 coversquare.py`
4. Criar rotina para CSV de importação
5. Importar 

## Tutorial
[Thumbnail do vídeo](https://app.screencastify.com/v2/manage/videos/sPBe5a5ExOUDrYFaP0Gr)

## Falta

1. Tratar os problemas e refazer as etapas para esse lote 2 (ou fazer na mão)
2. Verificar quais livros não entraram
