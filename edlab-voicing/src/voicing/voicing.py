import asyncio
import edge_tts
import argparse
from gtts import gTTS
import os
from tqdm import tqdm
import re
import azure.cognitiveservices.speech as speechsdk
from .pattern_manager import process_text_with_patterns
from .elevenlabs_integration import ElevenLabsTTS, ELEVENLABS_VOICES

# Configurações do Azure Speech Service
AZURE_SPEECH_KEY = "25lM4tmGc07aXoUcE99p99DcJzGAAj8HKZAKyUUG2c1jXk0tgVMKJQQJ99ALACZoyfiXJ3w3AAAYACOGm24o"
AZURE_SPEECH_REGION = "brazilsouth"

# Add ElevenLabs configuration
ELEVENLABS_API_KEY = "sk_2b5385cba7c47b56c598f195c618ec8296956744b32c4e88"


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


def process_line_breaks(text):
    """
    Processa quebras de linha no texto, mantendo apenas quebras entre parágrafos.
    Remove quebras de linha dentro de parágrafos e mantém a formatação entre parágrafos.
    
    Args:
        text (str): Texto a ser processado
        
    Returns:
        str: Texto processado com quebras de linha ajustadas
    """
    # Primeiro, normaliza as quebras de linha para \n
    text = text.replace('\r\n', '\n')
    
    # Remove espaços extras no final das linhas
    text = re.sub(r'\s+$', '', text, flags=re.MULTILINE)
    
    # Substitui quebras de linha simples por espaços
    text = re.sub(r'\n(?!\n)', ' ', text)
    
    # Remove múltiplos espaços
    text = re.sub(r'\s+', ' ', text)
    
    # Normaliza quebras duplas para ter exatamente uma linha em branco
    text = re.sub(r'\n\s*\n\s*', '\n\n', text)
    
    # Remove espaços no início e fim do texto
    text = text.strip()
    
    return text

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
    """Main function for text-to-speech conversion"""
    if preset and preset in PRESETS:
        config = PRESETS[preset]
        voice = config['voice']
        pitch = config['pitch']
        rate = config['rate']
        style = config.get('style', 'general')
        print(f"Using preset '{preset}' with style '{style}'")

    # Process line breaks
    if engine not in ['azure', 'elevenlabs']:
        text = process_line_breaks(text)

    # Process text with patterns if not SSML
    if not text.strip().startswith('<speak'):
        text = process_text_with_patterns(text)
        if pause_size > 0 and engine != 'elevenlabs':
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

    with tqdm(total=1, desc="Converting", unit="file") as pbar:
        try:
            if engine == "elevenlabs":
                tts = ElevenLabsTTS(ELEVENLABS_API_KEY)
                # If voice is a name from ELEVENLABS_VOICES, get its ID
                voice_id = ELEVENLABS_VOICES.get(voice, voice)
                success = await tts.convert_to_speech(text, output_file, voice_id)
                if not success:
                    raise Exception("Failed to synthesize speech with ElevenLabs")
            elif engine == "azure":
                # Existing Azure implementation...
                style = PRESETS[preset]['style'] if preset else 'general'
                success = azure_tts_convert(text, voice, output_file, pitch, rate, style)
                if not success:
                    raise Exception("Failed to synthesize speech with Azure")
            else:  # gtts or edge
                if engine == "gtts":
                    clean_text = re.sub(r'<[^>]+>', '', text)
                    tts = gTTS(text=clean_text, lang=language)
                    tts.save(output_file)
                else:  # edge
                    await edge_tts_convert(text, voice, output_file, pitch, rate)
            pbar.update(1)
        except Exception as e:
            print(f"Error during conversion: {str(e)}")
            raise


async def list_voices():
    """List all available voices for the selected engine"""
    print("\nElevenLabs Voices:")
    print("-" * 50)
    for name, voice_id in ELEVENLABS_VOICES.items():
        print(f"Name: {name}")
        print(f"ID: {voice_id}")
        print("-" * 50)
    
    print("\nEdge TTS Voices:")
    voices = await edge_tts.list_voices()
    for voice in voices:
        print(f"Name: {voice['Name']}")
        print(f"Language: {voice['Locale']}")
        print(f"Gender: {voice['Gender']}")
        print("-" * 50)

def list_presets():
    """Lista todos os presets disponíveis com suas configurações"""
    for name, config in PRESETS.items():
        print(f"\nPreset: {name}")
        for key, value in config.items():
            print(f"  {key}: {value}")



def main():
    """
    Função principal que será chamada quando o comando 'voicing' for executado.
    Esta função gerencia o fluxo principal do programa, incluindo:
    - Processamento de argumentos da linha de comando
    - Verificação de condições necessárias
    - Execução da conversão de texto para fala
    """
    parser = argparse.ArgumentParser(description='Convert text to speech')
    parser.add_argument('-i', '--input', help='Input file (markdown or txt)')
    parser.add_argument('--text', help='Text to convert to speech')
    parser.add_argument('-o', '--output', default='output.mp3', help='Output filename')
    parser.add_argument('--engine', choices=['gtts', 'edge', 'azure', 'elevenlabs'], 
                       default='edge', help='Speech synthesis engine')
    parser.add_argument('--language', default='pt-br', help='Language code (for gtts)')
    parser.add_argument('--voice', default='MZxV5lN3cv7hi1376O0m',  # Ana Dias as default
                       help='Voice to use (ID or name for elevenlabs, voice name for edge/azure)')
    parser.add_argument('--pitch', default="0",
                       help='Voice pitch adjustment (-100 to +100)')
    parser.add_argument('--rate', default="0",
                       help='Speed adjustment (-100 to +100)')
    parser.add_argument('--pause', type=int, default=0,
                       help='Pause size (0 to disable, > 0 to enable)')
    parser.add_argument('--preset', choices=list(PRESETS.keys()),
                       help='Use predefined configuration')
    parser.add_argument('--list-voices', action='store_true',
                       help='List all available voices')
    parser.add_argument('--list-presets', action='store_true',
                       help='List all available presets')

    args = parser.parse_args()
    
    if args.list_voices:
        return asyncio.run(list_voices())
    elif args.list_presets:
        return list_presets()
    
    if not args.text and not args.input:
        parser.error("You must provide --text or -i (input file)")
    
    text = read_text_file(args.input) if args.input else args.text
    
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
        print(f"\nAudio generated successfully: {args.output}")
    except Exception as e:
        error_message = f"Error during conversion: {str(e)}"
        if "AZURE_SPEECH_KEY" in str(e):
            error_message += "\nCheck if Azure Speech key is correct."
        elif "AZURE_SPEECH_REGION" in str(e):
            error_message += "\nCheck if Azure Speech region is correct."
        elif "ELEVENLABS_API_KEY" in str(e):
            error_message += "\nCheck if ElevenLabs API key is correct."
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
