# Split_PDF_into_MD_with_images

## História

Quando estávamos trabalhando no PNLD2026, precisamos fazer HTMLs a partir dos PDFs. Precisamos então de um script para extrair o conteúdo legível do
PDF e as imagens para um arquivo Markdown (um por página e um unificando todo o conteúdo) e uma pasta /imgs com todas as imagens em jpg. 

## Dependências



* Ubuntu
```
sudo apt-get install poppler-utils imagemagick
```

* Manjaro
```
sudo pacman -S poppler imagemagick

```

## Como usar?

```
./Split_PDF_into_MD_with_images.sh <NOME.pdf>
```
