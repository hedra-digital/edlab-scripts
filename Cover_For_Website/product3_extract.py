import pandas as pd
import base64
import os

# Carregar o arquivo CSV
file_path = 'Products.csv'  # Substitua pelo caminho correto do seu arquivo CSV
df = pd.read_csv(file_path)

# Criar a pasta de destino, se ela não existir
output_folder = 'images'
invalid_folder = 'invalid_images'
os.makedirs(output_folder, exist_ok=True)
os.makedirs(invalid_folder, exist_ok=True)

# Função para salvar uma imagem a partir de uma string base64
def save_image(image_base64, file_name):
    try:
        image_data = base64.b64decode(image_base64)
        with open(file_name, 'wb') as f:
            f.write(image_data)
    except Exception as e:
        print(f"Erro ao salvar a imagem {file_name}: {e}")

# Iterar pelas linhas do DataFrame e salvar as imagens
for index, row in df.iterrows():
    image_base64 = row['Image']
    internal_reference = row['Internal Reference']
    file_name = os.path.join(output_folder, f"{internal_reference}.png")
    invalid_file_name = os.path.join(invalid_folder, f"{internal_reference}.txt")
    
    if isinstance(image_base64, str) and image_base64.startswith('/9j/'):  # Verificar se é uma string base64 válida
        save_image(image_base64, file_name)
        print(f"Imagem salva como {file_name}")
    else:
        # Salvar os dados inválidos para inspeção
        with open(invalid_file_name, 'w') as f:
            f.write(str(image_base64))
        print(f"Dados de imagem inválidos na linha {index}. Salvos como {invalid_file_name}")

print("Processo concluído.")
