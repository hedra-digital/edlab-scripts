# src/voicing/__init__.py

# Versão do pacote
__version__ = '0.1.0'

# Importa funções principais para facilitar o acesso
from .voicing import (
    convert_to_speech,
    list_voices,
    list_presets,
    azure_tts_convert,
    edge_tts_convert
)

# Define quais funções/classes estarão disponíveis quando alguém usar 'from voicing import *'
__all__ = [
    'convert_to_speech',
    'list_voices',
    'list_presets',
    'azure_tts_convert',
    'edge_tts_convert'
]
