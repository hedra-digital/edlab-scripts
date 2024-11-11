from PIL import Image
import os

def remove_all_colors_except_black(image_path):
    """
    Abre uma imagem, remove todas as cores exceto o preto, e retorna a imagem processada.
    """
    image = Image.open(image_path).convert("RGBA")
    pixels = image.load()

    # Processa cada pixel e torna transparente se não for preto
    for y in range(image.height):
        for x in range(image.width):
            r, g, b, a = pixels[x, y]
            if not (r < 50 and g < 50 and b < 50):  # Pixels que não são pretos
                pixels[x, y] = (255, 255, 255, 0)  # Tornar transparente

    return image

def process_images(input_directory, output_directory):
    """
    Processa todas as imagens em um diretório, removendo todas as cores exceto o preto,
    e salva no diretório de saída em formato PNG.
    """
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for filename in os.listdir(input_directory):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            input_path = os.path.join(input_directory, filename)
            output_path = os.path.join(output_directory, f"processed_{os.path.splitext(filename)[0]}.png")

            processed_image = remove_all_colors_except_black(input_path)
            processed_image.save(output_path, format="PNG")  # Salvar como PNG

            print(f"Imagem processada salva em: {output_path}")

# Defina os diretórios de entrada e saída
input_directory = '.'
output_directory = 'news'

# Executa o processamento das imagens
process_images(input_directory, output_directory)
