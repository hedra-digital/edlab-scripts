#!/usr/bin/env python3

import argparse
import os
import shutil
from pathlib import Path
import torch
import logging
from PIL import Image
import numpy as np
import urllib.request
import ssl

class RDBLayer(torch.nn.Module):
    def __init__(self, nc):
        super(RDBLayer, self).__init__()
        self.conv1 = torch.nn.Conv2d(nc, 32, 3, 1, 1)
        self.conv2 = torch.nn.Conv2d(nc + 32, 32, 3, 1, 1)
        self.conv3 = torch.nn.Conv2d(nc + 64, 32, 3, 1, 1)
        self.conv4 = torch.nn.Conv2d(nc + 96, 32, 3, 1, 1)
        self.conv5 = torch.nn.Conv2d(nc + 128, nc, 3, 1, 1)
        self.lrelu = torch.nn.LeakyReLU(negative_slope=0.2, inplace=True)
        self.beta = 0.2

    def forward(self, x):
        x1 = self.lrelu(self.conv1(x))
        x2 = self.lrelu(self.conv2(torch.cat((x, x1), 1)))
        x3 = self.lrelu(self.conv3(torch.cat((x, x1, x2), 1)))
        x4 = self.lrelu(self.conv4(torch.cat((x, x1, x2, x3), 1)))
        x5 = self.conv5(torch.cat((x, x1, x2, x3, x4), 1))
        return x5 * self.beta + x

class RRDB(torch.nn.Module):
    def __init__(self, nc):
        super(RRDB, self).__init__()
        self.rdb1 = RDBLayer(nc)
        self.rdb2 = RDBLayer(nc)
        self.rdb3 = RDBLayer(nc)
        self.beta = 0.2

    def forward(self, x):
        out = self.rdb1(x)
        out = self.rdb2(out)
        out = self.rdb3(out)
        return out * self.beta + x

class RRDBNet(torch.nn.Module):
    def __init__(self, scale):
        super(RRDBNet, self).__init__()
        self.scale = scale
        
        # First conv
        self.conv_first = torch.nn.Conv2d(3, 64, 3, 1, 1)
        
        # Body
        self.body = torch.nn.ModuleList([RRDB(64) for _ in range(23)])
        self.conv_body = torch.nn.Conv2d(64, 64, 3, 1, 1)
        
        # Upsampling
        if scale == 4:
            self.conv_up1 = torch.nn.Conv2d(64, 64, 3, 1, 1)
            self.conv_up2 = torch.nn.Conv2d(64, 64, 3, 1, 1)
        elif scale == 2:
            self.conv_up1 = torch.nn.Conv2d(64, 64, 3, 1, 1)
            
        self.conv_hr = torch.nn.Conv2d(64, 64, 3, 1, 1)
        self.conv_last = torch.nn.Conv2d(64, 3, 3, 1, 1)
        
        self.lrelu = torch.nn.LeakyReLU(negative_slope=0.2, inplace=True)

    def forward(self, x):
        feat = self.conv_first(x)
        body_feat = feat.clone()
        
        for block in self.body:
            body_feat = block(body_feat)
            
        body_feat = self.conv_body(body_feat)
        body_feat = body_feat + feat
        
        # Upsampling
        if self.scale == 4:
            feat = self.lrelu(self.conv_up1(torch.nn.functional.interpolate(body_feat, scale_factor=2, mode='nearest')))
            feat = self.lrelu(self.conv_up2(torch.nn.functional.interpolate(feat, scale_factor=2, mode='nearest')))
        elif self.scale == 2:
            feat = self.lrelu(self.conv_up1(torch.nn.functional.interpolate(body_feat, scale_factor=2, mode='nearest')))
            
        out = self.conv_last(self.lrelu(self.conv_hr(feat)))
        return out

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def download_model(url, model_path):
    if not os.path.exists(model_path):
        logging.info(f"Baixando modelo de {url}")
        # Desabilitar verificação SSL para download
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(url, context=ctx) as response:
            with open(model_path, 'wb') as f:
                f.write(response.read())
        logging.info("Download concluído")

def setup_model(scale):
    # Selecionar o modelo apropriado baseado na escala
    if scale == 2:
        model_url = 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x2plus.pth'
        model_path = 'RealESRGAN_x2plus.pth'
    else:  # scale 4
        model_url = 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth'
        model_path = 'RealESRGAN_x4plus.pth'
    
    download_model(model_url, model_path)
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = RRDBNet(scale=scale)
    
    state_dict = torch.load(model_path, map_location=torch.device('cpu'))
    if 'params_ema' in state_dict:
        model.load_state_dict(state_dict['params_ema'])
    elif 'params' in state_dict:
        model.load_state_dict(state_dict['params'])
    else:
        model.load_state_dict(state_dict)
    
    model.eval()
    model = model.to(device)
    return model, device

def backup_image(image_path):
    backup_dir = Path('./old_images')
    backup_dir.mkdir(exist_ok=True)
    
    dest = backup_dir / image_path.name
    shutil.copy2(str(image_path), str(dest))
    logging.info(f"Backup criado: {dest}")

def should_process_image(image_path, min_size_kb, max_size_kb):
    """
    Verifica se a imagem deve ser processada baseado no seu tamanho
    """
    size_kb = os.path.getsize(image_path) / 1024  # Converter bytes para KB
    
    if min_size_kb and size_kb < min_size_kb:
        logging.info(f"Pulando {image_path.name} (tamanho: {size_kb:.1f}KB < {min_size_kb}KB)")
        return False
    
    if max_size_kb and size_kb > max_size_kb:
        logging.info(f"Pulando {image_path.name} (tamanho: {size_kb:.1f}KB > {max_size_kb}KB)")
        return False
        
    return True


def process_image(input_path, model, device, target_dpi=300, target_width_mm=None):
    try:
        # Fazer backup da imagem original
        backup_image(input_path)
        
        # Ler a imagem
        img = Image.open(input_path).convert('RGB')
        original_width, original_height = img.size
        
        # Calcular nova resolução se width foi especificado
        if target_width_mm:
            # Converter mm para polegadas (1 polegada = 25.4mm)
            target_width_inches = target_width_mm / 25.4
            # Calcular pixels necessários para o width desejado em 300dpi
            target_width_pixels = int(target_width_inches * target_dpi)
            # Manter proporção
            ratio = original_height / original_width
            target_height_pixels = int(target_width_pixels * ratio)
        else:
            target_width_pixels = original_width
            target_height_pixels = original_height
        
        # Preparar imagem para o modelo
        img_array = np.array(img)
        img_tensor = torch.from_numpy(img_array).float() / 255.0
        img_tensor = img_tensor.permute(2, 0, 1).unsqueeze(0)
        img_tensor = img_tensor.to(device)
        
        # Processar imagem
        with torch.no_grad():
            output = model(img_tensor)
        
        # Converter resultado de volta para imagem
        output = output.squeeze().float().cpu().clamp_(0, 1).numpy()
        output = (output * 255.0).round().astype(np.uint8)
        output = np.transpose(output, (1, 2, 0))
        output_img = Image.fromarray(output)
        
        # Redimensionar para o tamanho alvo se necessário
        if target_width_pixels != output_img.width:
            output_img = output_img.resize((target_width_pixels, target_height_pixels), 
                                         Image.Resampling.LANCZOS)
        
        # Definir DPI
        output_img.info['dpi'] = (target_dpi, target_dpi)
        
        # Salvar imagem processada
        output_img.save(str(input_path), dpi=(target_dpi, target_dpi))
        logging.info(f"Imagem processada salva em: {input_path}")
        logging.info(f"Resolução final: {output_img.size[0]}x{output_img.size[1]} pixels @ {target_dpi} DPI")
        if target_width_mm:
            logging.info(f"Tamanho para impressão: {target_width_mm}mm x {target_width_mm * output_img.size[1] / output_img.size[0]:.1f}mm")
        
        return True
    except Exception as e:
        logging.error(f"Erro ao processar {input_path}: {str(e)}")
        return False

def main():
    setup_logging()
    parser = argparse.ArgumentParser(description='EdLab Upscale - Aumentar resolução de imagens usando Real-ESRGAN')
    parser.add_argument('-i', '--input', nargs='+', required=True, 
                        help='Caminho para imagem(ns) ou diretório')
    parser.add_argument('-s', '--scale', type=int, choices=[2, 4], default=4,
                        help='Fator de escala (2 ou 4). Padrão: 4')
    parser.add_argument('-m', '--min-size', type=float, default=0,
                        help='Tamanho mínimo em KB para processar a imagem')
    parser.add_argument('-M', '--max-size', type=float, default=0,
                        help='Tamanho máximo em KB para processar a imagem')
    parser.add_argument('-w', '--workers', type=int, default=1,
                        help='Número de imagens processadas simultaneamente')
    parser.add_argument('--dpi', type=int, default=300,
                        help='DPI desejado para a imagem de saída. Padrão: 300')
    parser.add_argument('--width', type=float,
                        help='Largura desejada em milímetros (mantém proporção)')
    
    args = parser.parse_args()
    
    # Inicializar o modelo
    logging.info(f"Inicializando o modelo Real-ESRGAN (escala {args.scale}x)...")
    model, device = setup_model(args.scale)
    
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
    
    # Processar imagens
    total = len(image_paths)
    successful = 0
    skipped_small = 0
    skipped_large = 0
    
    for i, img_path in enumerate(image_paths, 1):
        size_kb = os.path.getsize(img_path) / 1024
        if not should_process_image(img_path, args.min_size, args.max_size):
            if args.min_size and size_kb < args.min_size:
                skipped_small += 1
            elif args.max_size and size_kb > args.max_size:
                skipped_large += 1
            continue
            
        logging.info(f"Processando imagem {i}/{total}: {img_path.name} ({size_kb:.1f}KB)")
        if process_image(img_path, model, device, args.dpi, args.width):
            successful += 1
            
    logging.info(f"\nProcessamento concluído!")
    logging.info(f"- Imagens processadas com sucesso: {successful}")
    if args.min_size > 0:
        logging.info(f"- Imagens puladas (menores que {args.min_size}KB): {skipped_small}")
    if args.max_size > 0:
        logging.info(f"- Imagens puladas (maiores que {args.max_size}KB): {skipped_large}")
    logging.info(f"- Total de imagens encontradas: {total}")

if __name__ == '__main__':
    main()