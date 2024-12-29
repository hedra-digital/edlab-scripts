import asyncio
import edge_tts
import argparse
from gtts import gTTS
import os
from tqdm import tqdm
import re
import azure.cognitiveservices.speech as speechsdk
from .pattern_manager import process_text_with_patterns

# Configurações do Azure Speech Service
AZURE_SPEECH_KEY = "25lM4tmGc07aXoUcE99p99DcJzGAAj8HKZAKyUUG2c1jXk0tgVMKJQQJ99ALACZoyfiXJ3w3AAAYACOGm24o"
AZURE_SPEECH_REGION = "brazilsouth"

# Presets para diferentes estilos de voz
# Cada preset define configurações específicas para diferentes casos de uso
PRESETS = {
    'default': {
        'voice': 'pt-BR-FranciscaNeural',
        'pitch': '0',
        'rate': '0',
        'style': 'general'  # Estilo padrão para o Azure
    },
    'audiobook': {
        'voice': 'pt-BR-AntonioNeural',
        'pitch': '-10',
        'rate': '-15',
        'style': 'narration-professional'  # Estilo específico para audiobooks
    },
    'news': {
        'voice': 'pt-BR-FranciscaNeural',
        'pitch': '0',
        'rate': '10',
        'style': 'newscast-formal'  # Estilo de apresentação de notícias
    },
    'story': {
        'voice': 'pt-BR-BrendaNeural',
        'pitch': '0',
        'rate': '-10',
        'style': 'narration-relaxed'  # Estilo para narrativas
    },
    'formal': {
        'voice': 'pt-BR-AntonioNeural',
        'pitch': '-20',
        'rate': '-5',
        'style': 'business'  # Estilo formal para apresentações
    }
}

def validate_tts_params(pitch, rate):
    """
    Valida os parâmetros de síntese de voz.
    Garante que pitch e rate estejam dentro dos limites aceitáveis (-100 a +100).
    """
    try:
        pitch_val = int(pitch)
        rate_val = int(rate)
        if not (-100 <= pitch_val <= 100) or not (-100 <= rate_val <= 100):
            raise ValueError("Pitch e rate devem estar entre -100 e +100")
        return pitch_val, rate_val
    except ValueError as e:
        raise ValueError(f"Parâmetros inválidos: {str(e)}")

def read_text_file(filepath):
    """
    Lê o conteúdo de um arquivo de texto.
    Usa codificação UTF-8 para suportar caracteres especiais.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")
    except Exception as e:
        raise Exception(f"Erro ao ler arquivo: {str(e)}")

def azure_tts_convert(text, voice, output_file, pitch="0", rate="0", style="general"):
    """
    Converte texto em fala usando Azure Speech Service.
    Aceita tanto texto simples quanto SSML.
    """
    try:
        speech_config = speechsdk.SpeechConfig(
            subscription=AZURE_SPEECH_KEY,
            region=AZURE_SPEECH_REGION
        )
    except speechsdk.exceptions.SpeechException as e:
        print(f"Erro de conexão com o Azure: {str(e)}")
        return False
    
    audio_config = speechsdk.audio.AudioOutputConfig(filename=output_file)
    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, 
        audio_config=audio_config
    )
    
    # Verifica se o texto já é SSML (começa com <speak>)
    is_ssml = text.strip().startswith('<speak')
    
    if not is_ssml:
        # Se não for SSML, cria o SSML
        pitch_val, rate_val = validate_tts_params(pitch, rate)
        pitch_hz = f"{pitch_val}Hz"
        rate_pct = f"{rate_val}%"
        
        text = f'''
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="pt-BR">
            <voice name="{voice}">
                <mstts:express-as style="{style}" xmlns:mstts="http://www.w3.org/2001/mstts">
                    <prosody rate="{rate_pct}" pitch="{pitch_hz}">
                        {text}
                    </prosody>
                </mstts:express-as>
            </voice>
        </speak>
        '''
    
    # Realiza a síntese
    try:
        result = synthesizer.speak_ssml_async(text).get()
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return True
        else:
            print(f"Erro na síntese: {result.reason}")
            if result.reason == speechsdk.ResultReason.Canceled:
                details = result.cancellation_details
                print(f"Detalhes do erro: {details.reason}")
            return False
    except speechsdk.SpeechSynthesisException as e:
        print(f"Erro de síntese de fala: {str(e)}")
        return False
    except Exception as e:
        print(f"Erro durante a síntese: {str(e)}")
        return False

async def edge_tts_convert(text, voice, output_file, pitch="0", rate="0"):
    """
    Converte texto em fala usando Edge TTS.
    Usa configurações diretas em vez de SSML para maior compatibilidade.
    """
    pitch_val, rate_val = validate_tts_params(pitch, rate)
    
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=f"{rate_val:+}%",
        volume="+0%",
        pitch=f"{pitch_val:+}Hz"
    )
    
    await communicate.save(output_file)

async def convert_to_speech(text, output_file, engine, language, voice, pitch, rate, preset, pause_size):
    """Função principal de conversão"""
    if preset and preset in PRESETS:
        config = PRESETS[preset]
        voice = config['voice']
        pitch = config['pitch']
        rate = config['rate']
        style = config.get('style', 'general')
        print(f"Usando preset '{preset}' com estilo '{style}'")

    # Só processa padrões e pausas se o texto não for SSML
    is_ssml = text.strip().startswith('<speak')
    if not is_ssml:
        # Aplica os padrões de substituição
        text = process_text_with_patterns(text)
        
        # Processa pausas se necessário
        if pause_size > 0:
            pause_ms = pause_size * 100
            parts = re.split(r'([.!?:;])', text)
            processed_text = ""
            
            for i in range(0, len(parts)-1, 2):
                if parts[i].strip():
                    sentence = parts[i].strip() + parts[i+1]
                    processed_text += f"{sentence} <break time='{pause_ms}ms'/> "
            
            if len(parts) % 2 == 1 and parts[-1].strip():
                processed_text += parts[-1].strip()
            
            text = processed_text.strip()
    
    with tqdm(total=1, desc="Convertendo", unit="arquivo") as pbar:
        try:
            if engine == "gtts":
                clean_text = re.sub(r'<[^>]+>', '', text)
                tts = gTTS(text=clean_text, lang=language)
                tts.save(output_file)
            elif engine == "azure":
                style = PRESETS[preset]['style'] if preset else 'general'
                success = azure_tts_convert(text, voice, output_file, pitch, rate, style)
                if not success:
                    raise Exception("Falha na síntese de voz com Azure")
            else:  # edge
                await edge_tts_convert(text, voice, output_file, pitch, rate)
            pbar.update(1)
        except Exception as e:
            print(f"Erro durante a conversão: {str(e)}")
            raise

async def list_voices():
    """Lista todas as vozes disponíveis no Edge TTS"""
    voices = await edge_tts.list_voices()
    for voice in voices:
        print(f"Nome: {voice['Name']}")
        print(f"Idioma: {voice['Locale']}")
        print(f"Gênero: {voice['Gender']}")
        print("-" * 50)

def list_presets():
    """Lista todos os presets disponíveis com suas configurações"""
    for name, config in PRESETS.items():
        print(f"\nPreset: {name}")
        for key, value in config.items():
            print(f"  {key}: {value}")



#!/usr/bin/env python3
# Seu código atual aqui, mas com algumas modificações:


def main():
    """
    Função principal que será chamada quando o comando 'voicing' for executado.
    Esta função gerencia o fluxo principal do programa, incluindo:
    - Processamento de argumentos da linha de comando
    - Verificação de condições necessárias
    - Execução da conversão de texto para fala
    """
    parser = argparse.ArgumentParser(description='Converter texto em áudio')
    parser.add_argument('-i', '--input', help='Arquivo de entrada (markdown ou txt)')
    parser.add_argument('--text', help='Texto para converter em áudio')
    parser.add_argument('-o', '--output', default='output.mp3', help='Nome do arquivo de saída')
    parser.add_argument('--engine', choices=['gtts', 'edge', 'azure'], default='edge', 
                        help='Motor de síntese de voz')
    parser.add_argument('--language', default='pt-br', help='Código do idioma (para gtts)')
    parser.add_argument('--voice', default='pt-BR-FranciscaNeural', 
                        help='Voz a ser usada (para edge/azure)')
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
    
    # Executa os comandos de listagem se solicitados
    if args.list_voices:
        return asyncio.run(list_voices())
    elif args.list_presets:
        return list_presets()
    
    # Verifica se foi fornecido texto ou arquivo de entrada
    if not args.text and not args.input:
        parser.error("É necessário fornecer --text ou -i (arquivo de entrada)")
    
    # Obtém o texto da entrada apropriada
    text = read_text_file(args.input) if args.input else args.text
    
    # Executa a conversão de texto para fala
    try:
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
        print(f"\nAúdio gerado com sucesso: {args.output}")
    except Exception as e:
        error_message = f"Erro durante a conversão: {str(e)}"
        if "AZURE_SPEECH_KEY" in str(e):
            error_message += "\nVerifique se a chave do Azure Speech está correta."
        elif "AZURE_SPEECH_REGION" in str(e):
            error_message += "\nVerifique se a região do Azure Speech está correta."
        print(error_message)
        return 1

    return 0

if __name__ == "__main__":
    """
    Ponto de entrada do script quando executado diretamente.
    Chama a função main() e gerencia o código de saída do programa.
    """
    exit_code = main()
    exit(exit_code)