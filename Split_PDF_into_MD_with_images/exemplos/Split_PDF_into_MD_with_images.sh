
#!/bin/bash

# Verificar se o nome do arquivo PDF foi fornecido como argumento
if [ -z "$1" ]; then
    echo "Uso: $0 <arquivo.pdf>"
    exit 1
fi

# Nome do arquivo PDF passado como argumento
PDF_FILE="$1"

# Verificar se o arquivo existe
if [[ ! -f "$PDF_FILE" ]]; then
    echo "Arquivo PDF '$PDF_FILE' não encontrado!"
    exit 1
fi

# Remover a extensão .pdf para criar o nome da pasta e arquivo concatenado
DIR_NAME="${PDF_FILE%.pdf}"
AUDIO_MD_FILE="$DIR_NAME/${DIR_NAME}_audio.md"

# Criar diretório com o nome do arquivo PDF e pasta para imagens
mkdir -p "$DIR_NAME/img"

# Contador de páginas
page_number=1

# Limpar o arquivo concatenado, caso já exista
> "$AUDIO_MD_FILE"

# Loop por cada página
while pdftotext -f "$page_number" -l "$page_number" "$PDF_FILE" "$DIR_NAME/page-$page_number.txt"; do
    # Se não extrair texto, sair do loop
    if [[ ! -s "$DIR_NAME/page-$page_number.txt" ]]; then
        rm "$DIR_NAME/page-$page_number.txt"
        break
    fi

    # Remover o número da página no final de cada página extraída (eliminação do número da página no conteúdo)
    sed -i '/^[0-9]\+$/d' "$DIR_NAME/page-$page_number.txt"

    # Adicionar o número da página no início do arquivo em formato Markdown
    echo "[Página $page_number]" > "$DIR_NAME/page-$(printf "%03d" $page_number).md"
    cat "$DIR_NAME/page-$page_number.txt" >> "$DIR_NAME/page-$(printf "%03d" $page_number).md"
    
    # Remover arquivo temporário de texto
    rm "$DIR_NAME/page-$page_number.txt"
    
    # Extrair imagens da página e salvar na pasta img dentro do diretório criado
    pdftoppm -f "$page_number" -l "$page_number" -jpeg "$PDF_FILE" "$DIR_NAME/img/page_$(printf "%03d" $page_number)"

    # Verificar se há imagens extraídas e adicionar ao arquivo .md com a sintaxe correta
    if [[ -n $(ls "$DIR_NAME"/img/page_$(printf "%03d" $page_number)-*.jpg 2>/dev/null) ]]; then
        for img in "$DIR_NAME"/img/page_$(printf "%03d" $page_number)-*.jpg; do
            echo "![$page_number](./img/page_$(printf "%03d" $page_number).jpg)" >> "$DIR_NAME/page-$(printf "%03d" $page_number).md"
        done
    fi

    # Concatenar o conteúdo da página atual no arquivo _audio.md
    cat "$DIR_NAME/page-$(printf "%03d" $page_number).md" >> "$AUDIO_MD_FILE"
    echo -e "\n---\n" >> "$AUDIO_MD_FILE" # Adiciona uma linha divisória entre as páginas

    # Incrementar o número da página
    ((page_number++))
done

echo "Extração completa. Verifique a pasta '$DIR_NAME' para os arquivos .md e o arquivo concatenado '$AUDIO_MD_FILE'."
