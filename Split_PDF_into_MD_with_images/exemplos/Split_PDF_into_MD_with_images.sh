
#!/bin/bash

# Verificar se o nome do arquivo PDF foi fornecido como argumento
if [ -z "$1" ]; then
    echo "Uso: $0 <arquivo.pdf> [--pages-split]"
    exit 1
fi

# Nome do arquivo PDF passado como argumento
PDF_FILE="$1"
shift

# Variável para controle da opção de divisão por páginas
SPLIT_PAGES=false

# Verificar argumentos opcionais
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --pages-split) SPLIT_PAGES=true ;;
        *) echo "Opção desconhecida: $1"; exit 1 ;;
    esac
    shift
done

# Verificar se o arquivo existe
if [[ ! -f "$PDF_FILE" ]]; then
    echo "Arquivo PDF '$PDF_FILE' não encontrado!"
    exit 1
fi

# Remover a extensão .pdf para criar o nome da pasta e arquivo concatenado
DIR_NAME="${PDF_FILE%.pdf}"
AUDIO_MD_FILE="$DIR_NAME/${DIR_NAME}_text.md"

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

    # Remover qualquer caractere estranho, incluindo <0x0c>, e qualquer espaço antes do link da imagem
    sed -i 's/^\x0c//g' "$DIR_NAME/page-$page_number.txt"

    # Nome do arquivo de cada página
    PAGE_MD_FILE="$DIR_NAME/page-$(printf "%04d" $page_number).md"

    # Adicionar o número da página no início do arquivo em formato Markdown
    echo "[Página $page_number]" > "$PAGE_MD_FILE"
    cat "$DIR_NAME/page-$page_number.txt" >> "$PAGE_MD_FILE"
    
    # Remover arquivo temporário de texto
    rm "$DIR_NAME/page-$page_number.txt"
    
    # Extrair imagens da página e salvar na pasta img dentro do diretório criado
    pdftoppm -f "$page_number" -l "$page_number" -jpeg "$PDF_FILE" "$DIR_NAME/img/page_$(printf "%04d" $page_number)"

    # Renomear a imagem corretamente e remover o sufixo "-01"
    for img in "$DIR_NAME"/img/page_$(printf "%04d" $page_number)-*.jpg; do
        mv "$img" "$DIR_NAME/img/page_$(printf "%04d" $page_number).jpg"
    done

    # Verificar se há imagens extraídas e adicionar ao arquivo .md com a sintaxe correta
    if [[ -n $(ls "$DIR_NAME"/img/page_$(printf "%04d" $page_number).jpg 2>/dev/null) ]]; then
        echo "![$page_number](./img/page_$(printf "%04d" $page_number).jpg)" >> "$PAGE_MD_FILE"
    fi

    # Concatenar o conteúdo da página atual no arquivo _text.md
    cat "$PAGE_MD_FILE" >> "$AUDIO_MD_FILE"
    echo -e "\n---\n" >> "$AUDIO_MD_FILE" # Adiciona uma linha divisória entre as páginas

    # Se a opção --pages-split foi fornecida, manter o arquivo .md individual de cada página
    if [ "$SPLIT_PAGES" = false ]; then
        rm "$PAGE_MD_FILE"
    fi

    # Incrementar o número da página
    ((page_number++))
done

echo "Extração completa. Verifique a pasta '$DIR_NAME' para os arquivos .md e o arquivo concatenado '$AUDIO_MD_FILE'."
