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
import gc
import psutil
import time
import sys
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor, as_completed 

# Adicionando controle de memória mais rigoroso
class MemoryManager:
    def __init__(self, memory_limit_percent, min_free_memory_mb=1000):
        self.memory_limit_percent = memory_limit_percent
        self.min_free_memory_mb = min_free_memory_mb
        self.process = psutil.Process(os.getpid())
        
    def get_memory_info(self):
        system = psutil.virtual_memory()
        process_memory = self.process.memory_info().rss / (1024 * 1024)  # MB
        free_memory = system.available / (1024 * 1024)  # MB
        return {
            'process_memory_mb': process_memory,
            'free_memory_mb': free_memory,
            'memory_percent': system.percent
        }
    
    def check_memory(self):
        info = self.get_memory_info()
        
        if info['memory_percent'] > self.memory_limit_percent:
            raise MemoryError(f"Sistema usando {info['memory_percent']}% de memória (limite: {self.memory_limit_percent}%)")
            
        if info['free_memory_mb'] < self.min_free_memory_mb:
            raise MemoryError(f"Memória livre insuficiente: {info['free_memory_mb']:.0f}MB (mínimo: {self.min_free_memory_mb}MB)")
        
        return True
    
    @contextmanager
    def monitor(self):
        try:
            self.check_memory()
            yield
        finally:
            self.cleanup()
    
    def cleanup(self):
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

class ResourceGuard:
    def __init__(self, memory_manager, max_retries=3, retry_delay=5):
        self.memory_manager = memory_manager
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    @contextmanager
    def guard(self, operation_name="operação"):
        attempts = 0
        while attempts < self.max_retries:
            try:
                with self.memory_manager.monitor():
                    yield
                    break
            except MemoryError as e:
                attempts += 1
                if attempts >= self.max_retries:
                    logging.error(f"Falha na {operation_name} após {self.max_retries} tentativas: {str(e)}")
                    raise
                logging.warning(f"Tentativa {attempts}/{self.max_retries} falhou: {str(e)}")
                time.sleep(self.retry_delay)
            except Exception as e:
                logging.error(f"Erro na {operation_name}: {str(e)}")
                raise

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
    # Definir caminhos dos modelos
    models_dir = Path(__file__).parent / 'models'
    
    if scale == 2:
        model_url = 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x2plus.pth'
        model_path = models_dir / 'RealESRGAN_x2plus.pth'
    else:  # scale 4
        model_url = 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth'
        model_path = models_dir / 'RealESRGAN_x4plus.pth'
    
    # Baixar modelo apenas se não existir
    if not model_path.exists():
        models_dir.mkdir(parents=True, exist_ok=True)
        logging.info(f"Baixando modelo de {model_url}")
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

def get_system_info():
    """Retorna informações detalhadas do sistema"""
    process = psutil.Process(os.getpid())
    system = psutil.virtual_memory()
    return {
        'memory_used': process.memory_info().rss / 1024 / 1024,  # MB
        'memory_percent': process.memory_percent(),
        'system_memory_percent': system.percent,
        'cpu_percent': process.cpu_percent(),
        'system_cpu_percent': psutil.cpu_percent(),
        'threads': process.num_threads()
    }

def check_resources(memory_limit=70):
    """Verifica se há recursos disponíveis para continuar"""
    info = get_system_info()
    
    # Verificar CPU (limite de 60%)
    if info['system_cpu_percent'] > 60:
        logging.warning("CPU acima de 60%. Aguardando...")
        return False
        
    # Verificar memória (usando limite definido pelo usuário)
    if info['system_memory_percent'] > memory_limit:
        logging.warning(f"Memória do sistema acima de {memory_limit}%. Aguardando...")
        return False
    
    return True

def wait_for_resources(memory_limit=70, check_interval=5):
    """Aguarda até que os recursos estejam disponíveis"""
    while not check_resources(memory_limit):
        gc.collect()  # Forçar coleta de lixo
        if torch.cuda.is_available():
            torch.cuda.empty_cache()  # Limpar cache CUDA
        time.sleep(check_interval)

def log_system_status():
    """Loga status detalhado do sistema"""
    info = get_system_info()
    logging.info(
        f"Status do Sistema:\n"
        f"- RAM Processo: {info['memory_used']:.1f}MB ({info['memory_percent']:.1f}%)\n"
        f"- RAM Sistema: {info['system_memory_percent']:.1f}%\n"
        f"- CPU Processo: {info['cpu_percent']:.1f}%\n"
        f"- CPU Sistema: {info['system_cpu_percent']:.1f}%\n"
        f"- Threads: {info['threads']}"
    )

def process_image(input_path, model, device, target_dpi=300, target_width_mm=None, worker_id=None, memory_manager=None):
    worker_info = f"[Worker {worker_id}] " if worker_id is not None else ""
    guard = ResourceGuard(memory_manager)
    
    try:
        with guard.guard("carregamento da imagem"):
            img = Image.open(input_path)
            original_width, original_height = img.size
            
            # Redimensionar previamente se necessário
            max_dimension = 2000
            if original_width > max_dimension or original_height > max_dimension:
                ratio = min(max_dimension/original_width, max_dimension/original_height)
                new_width = int(original_width * ratio)
                new_height = int(original_height * ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            img = img.convert('RGB')
            
        with guard.guard("processamento do modelo"):
            # Converter para tensor com controle de memória
            img_array = np.array(img)
            img = None  # Liberar memória original
            
            img_tensor = torch.from_numpy(img_array).float() / 255.0
            img_array = None
            
            img_tensor = img_tensor.permute(2, 0, 1).unsqueeze(0).to(device)
            
            # Processar com o modelo
            with torch.no_grad():
                output = model(img_tensor)
            
            img_tensor = None
            
            # Converter resultado
            output = output.squeeze().float().cpu().clamp_(0, 1).numpy()
            output = (output * 255.0).round().astype(np.uint8)
            output = np.transpose(output, (1, 2, 0))
            
        with guard.guard("salvamento da imagem"):
            # Criar imagem final
            output_img = Image.fromarray(output)
            output = None
            
            if target_width_mm:
                target_width_inches = target_width_mm / 25.4
                target_width_pixels = int(target_width_inches * target_dpi)
                ratio = original_height / original_width
                target_height_pixels = int(target_width_pixels * ratio)
                output_img = output_img.resize((target_width_pixels, target_height_pixels), 
                                             Image.Resampling.LANCZOS)
            
            # Backup e salvamento
            backup_image(input_path)
            output_img.save(str(input_path), dpi=(target_dpi, target_dpi))
            
        return True
        
    except Exception as e:
        logging.error(f"{worker_info}Erro ao processar {input_path}: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        return False


def main():
    setup_logging()
    parser = argparse.ArgumentParser(description='EdLab Upscale - Aumentar resolução de imagens usando Real-ESRGAN')
    parser.add_argument('-i', '--input', nargs='+', required=True, 
                        help='Caminho para imagem(ns) ou diretório')
    parser.add_argument('-s', '--scale', type=int, choices=[2, 4], default=4,
                        help='Fator de escala (2 ou 4). Padrão: 4')
    parser.add_argument('-m', '--min-size', type=float, default=0,
                        help='Tamanho mínimo da KB da imagem a ser processada')
    parser.add_argument('-M', '--max-size', type=float, default=0,
                        help='Tamanho máximo da KB da imagem a ser processada')
    parser.add_argument('-w', '--workers', type=int, default=4,
                        help='Número de threads de processamento paralelo (padrão: 4). '
                             'Aumentar pode melhorar a velocidade em CPUs multi-core, '
                             'mas também aumenta o consumo de memória')
    parser.add_argument('--dpi', type=int, default=300,
                        help='DPI desejado para a imagem de saída. Padrão: 300')
    parser.add_argument('--width', type=float,
                        help='Largura desejada em milímetros (mantém proporção)')
    parser.add_argument('--memory-limit', type=float, default=60,
                    help='Limite de uso de memória em porcentagem. Padrão: 60')
    parser.add_argument('--batch-size', type=int, default=1,
                    help='Número de imagens processadas por vez na GPU. Padrão: 1')

    args = parser.parse_args()
    
    logging.info(f"Iniciando com {args.workers} worker(s)")
    log_system_status()
    
    # Limitar número de threads do PyTorch
    torch.set_num_threads(args.workers)
    logging.info(f"Threads do PyTorch limitadas a {args.workers}")
    
    # Inicializar o modelo
    logging.info(f"Inicializando o modelo Real-ESRGAN (escala {args.scale}x)...")
    model, device = setup_model(args.scale)
    logging.info(f"Modelo inicializado no dispositivo: {device}")
    
    # Inicializar gerenciador de memória
    memory_manager = MemoryManager(
        memory_limit_percent=args.memory_limit,
        min_free_memory_mb=1000  # Garante pelo menos 1GB livre
    )
    
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
    
    # Filtrar imagens com base no tamanho
    valid_images = []
    skipped_small = 0
    skipped_large = 0
    
    for img_path in image_paths:
        if not should_process_image(img_path, args.min_size, args.max_size):
            size_kb = os.path.getsize(img_path) / 1024
            if args.min_size and size_kb < args.min_size:
                skipped_small += 1
            elif args.max_size and size_kb > args.max_size:
                skipped_large += 1
        else:
            valid_images.append(img_path)
    
    total = len(valid_images)
    successful = 0
    
    try:
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = []
            
            for i, img_path in enumerate(valid_images, 1):
                try:
                    with memory_manager.monitor():
                        size_kb = os.path.getsize(img_path) / 1024
                        logging.info(f"Enfileirando imagem {i}/{total}: {img_path.name} ({size_kb:.1f}KB)")
                        future = executor.submit(
                            process_image, 
                            img_path, 
                            model, 
                            device,
                            args.dpi,
                            args.width,
                            i % args.workers,
                            memory_manager
                        )
                        futures.append(future)
                except MemoryError as e:
                    logging.error(f"Memória insuficiente para processar {img_path}: {str(e)}")
                    continue
                
            for future in as_completed(futures):
                try:
                    if future.result():
                        successful += 1
                except Exception as e:
                    logging.error(f"Erro no processamento: {str(e)}")
                    
    except KeyboardInterrupt:
        logging.info("\nInterrompendo processamento...")
        executor._threads.clear()
        concurrent.futures.thread._threads_queues.clear()
        sys.exit(1)
    
    logging.info(f"\nProcessamento concluído!")
    logging.info(f"- Imagens processadas com sucesso: {successful}")
    if args.min_size > 0:
        logging.info(f"- Imagens puladas (menores que {args.min_size}KB): {skipped_small}")
    if args.max_size > 0:
        logging.info(f"- Imagens puladas (maiores que {args.max_size}KB): {skipped_large}")
    logging.info(f"- Total de imagens encontradas: {len(image_paths)}")

if __name__ == '__main__':
    main()

