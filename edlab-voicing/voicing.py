import asyncio
import edge_tts
import argparse
from gtts import gTTS
import os
from tqdm import tqdm
import re

# Presets de configuração
PRESETS = {
    'default': {
        'voice': 'pt-BR-FranciscaNeural',
        'pitch': '0',
        'rate': '0'
    },
    'audiobook': {
        'voice': 'pt-BR-AntonioNeural',
        'pitch': '-10',
        'rate': '-15'
    },
    'news': {
        'voice': 'pt-BR-FranciscaNeural',
        'pitch': '0',
        'rate': '10'
    },
    'story': {
        'voice': 'pt-BR-BrendaNeural',
        'pitch': '0',
        'rate': '-10'
    },
    'formal': {
        'voice': 'pt-BR-AntonioNeural',
        'pitch': '-20',
        'rate': '-5'
    }
}

def add_pauses(text, pause_size):
    pause_ms = pause_size * 100
    
    # Primeiro processa o texto interno
    processed = text
    for punct in ['.', '!', '?', ':', ';']:
        processed = re.sub(f'\\{punct}\\s', f'{punct}<break time="{pause_ms}ms"/>', processed)
    
    # Então envolve em tags SSML completas
    return f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis">{processed}</speak>'

async def edge_tts_convert(text, voice, output_file, pitch="0", rate="0"):
    """Converte texto em fala usando edge-tts"""
    pitch_hz = f"{int(pitch):+}Hz"
    rate_pct = f"{int(rate):+}%"
    
    # Adicionando parâmetro para indicar que o texto é SSML
    communicate = edge_tts.Communicate(
        text, 
        voice, 
        pitch=pitch_hz, 
        rate=rate_pct,
        ssml=True  # Indicando que o texto contém SSML
    )
    await communicate.save(output_file)

def read_text_file(file_path):
    """Lê um arquivo texto (markdown ou txt) e retorna seu conteúdo"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        raise Exception(f"Arquivo não encontrado: {file_path}")
    except Exception as e:
        raise Exception(f"Erro ao ler arquivo: {str(e)}")

async def convert_to_speech(text, output_file, engine, language, voice, pitch, rate, preset, pause_size):
    """Função principal de conversão"""
    # Primeiro adiciona as pausas
    processed_text = add_pauses(text, pause_size) if pause_size > 0 else text
    
    print(f"Texto processado: '{processed_text}'")  # Adicionar este print
    
    # Depois aplica as configurações do preset
    if preset and preset in PRESETS:
        config = PRESETS[preset]
        voice = config['voice']
        pitch = config['pitch']
        rate = config['rate']
        print(f"Usando preset '{preset}'")
    
    with tqdm(total=1, desc="Convertendo", unit="arquivo") as pbar:
        if engine == "gtts":
            tts = gTTS(text=processed_text, lang=language)
            tts.save(output_file)
        else:  # edge
            await edge_tts_convert(processed_text, voice, output_file, pitch, rate)
        pbar.update(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Converter texto em áudio')
    parser.add_argument('-i', '--input', help='Arquivo de entrada (markdown ou txt)')
    parser.add_argument('--text', help='Texto para converter em áudio')
    parser.add_argument('-o', '--output', default='output.mp3', help='Nome do arquivo de saída')
    parser.add_argument('--engine', choices=['gtts', 'edge'], default='edge', 
                        help='Motor de síntese de voz')
    parser.add_argument('--language', default='pt-br', help='Código do idioma (para gtts)')
    parser.add_argument('--voice', default='pt-BR-FranciscaNeural', 
                        help='Voz a ser usada (para edge)')
    parser.add_argument('--pitch', default="0",
                        help='Ajuste do tom da voz (-100 a +100)')
    parser.add_argument('--rate', default="0",
                        help='Ajuste da velocidade (-100 a +100)')
    parser.add_argument('--pause', type=int, default=0,
                        help='Tamanho das pausas (0 para desativar, > 0 para ativar)')
    parser.add_argument('--preset', choices=list(PRESETS.keys()),
                        help='Usar configuração predefinida')
    parser.add_argument('--list-voices', action='store_true', 
                        help='Lista todas as vozes disponíveis')
    parser.add_argument('--list-presets', action='store_true',
                        help='Lista todos os presets disponíveis')
    
    args = parser.parse_args()
    
    if args.list_voices:
        asyncio.run(list_voices())
    elif args.list_presets:
        list_presets()
    else:
        if not args.text and not args.input:
            parser.error("É necessário fornecer --text ou -i (arquivo de entrada)")
            
        if args.input:
            text = read_text_file(args.input)
        else:
            text = args.text
            
        asyncio.run(convert_to_speech(
            text,
            args.output,
            args.engine,
            args.language,
            args.voice,
            args.pitch,
            args.rate,
            args.preset,
            args.pause
        ))