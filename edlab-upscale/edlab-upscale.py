#!/usr/bin/env python3

import argparse
import os
import shutil
from pathlib import Path
from basicsr.archs.rrdbnet_arch import RRDBNet
from basicsr.utils.download_util import load_file_from_url
from realesrgan import RealESRGANer
import cv2
import torch
import logging
import torchvision.transforms.functional as F  # Mudança aqui

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def setup_model(scale):
    # Selecionar o modelo apropriado baseado na escala
    if scale == 2:
        model_path = 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x2plus.pth'
        model_name = 'RealESRGAN_x2plus.pth'
    else:  # scale 4
        model_path = 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth'
        model_name = 'RealESRGAN_x4plus.pth'
    
    model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32)
    
    if not os.path.exists(model_name):
        load_file_from_url(model_path, model_dir='.')
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    upsampler = RealESRGANer(
        scale=scale,
        model_path=model_name,
        model=model,
        device=device
    )
    return upsampler

def process_image(input_path, upsampler, output_dir=None):
    try:
        # Ler a imagem
        img = cv2.imread(str(input_path), cv2.IMREAD_UNCHANGED)
        if img is None:
            logging.error(f"Não foi possível ler a imagem: {input_path}")
            return False

        # Processar a imagem
        output, _ = upsampler.enhance(img)

        # Definir caminho de saída
        if output_dir:
            output_path = Path(output_dir) / input_path.name
        else:
            output_path = input_path.parent / f"upscaled_{input_path.name}"

        # Salvar a imagem processada
        cv2.imwrite(str(output_path), output)
        logging.info(f"Imagem processada salva em: {output_path}")
        return True
    except Exception as e:
        logging.error(f"Erro ao processar {input_path}: {str(e)}")
        return False

def backup_images(image_paths, backup_dir):
    backup_dir = Path(backup_dir)
    backup_dir.mkdir(exist_ok=True)
    
    for img_path in image_paths:
        dest = backup_dir / img_path.name
        shutil.copy2(str(img_path), str(dest))
        logging.info(f"Backup criado: {dest}")

def main():
    setup_logging()
    parser = argparse.ArgumentParser(description='EdLab Upscale - Aumentar resolução de imagens usando Real-ESRGAN')
    parser.add_argument('-i', '--input', nargs='+', required=True, 
                        help='Caminho para imagem(ns) ou diretório')
    parser.add_argument('-s', '--scale', type=int, choices=[2, 4], default=4,
                        help='Fator de escala (2 ou 4). Padrão: 4')
    
    args = parser.parse_args()
    
    # Inicializar o modelo
    logging.info(f"Inicializando o modelo Real-ESRGAN (escala {args.scale}x)...")
    upsampler = setup_model(args.scale)
    
    # Coletar caminhos das imagens
    image_paths = []
    input_paths = [Path(p) for p in args.input]
    
    for path in input_paths:
        if path.is_file():
            image_paths.append(path)
        elif path.is_dir():
            image_paths.extend([
                p for p in path.glob('*') 
                if p.suffix.lower() in ['.png', '.jpg', '.jpeg', '.webp']
            ])
    
    if not image_paths:
        logging.error("Nenhuma imagem encontrada para processar!")
        return
    
    # Criar backup se necessário
    if len(input_paths) == 1 and input_paths[0].is_dir():
        backup_dir = Path('bkp-images')
        logging.info(f"Criando backup das imagens em: {backup_dir}")
        backup_images(image_paths, backup_dir)
    
    # Processar imagens
    total = len(image_paths)
    successful = 0
    
    for i, img_path in enumerate(image_paths, 1):
        logging.info(f"Processando imagem {i}/{total}: {img_path.name}")
        if process_image(img_path, upsampler):
            successful += 1
    
    logging.info(f"Processamento concluído! {successful}/{total} imagens processadas com sucesso.")

if __name__ == '__main__':
    main()