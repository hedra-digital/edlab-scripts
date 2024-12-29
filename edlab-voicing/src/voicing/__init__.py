# src/voicing/__init__.py

# Versão do pacote
__version__ = '0.1.1'

# Importa funções principais para facilitar o acesso
from .pattern_manager import PatternManager, process_text_with_patterns
from .voicing import (
    azure_tts_convert,
    edge_tts_convert,
    convert_to_speech,
    list_voices,
    list_presets,
    main,
)

# Define quais funções/classes estarão disponíveis quando alguém usar 'from voicing import *'
__all__ = [
    'convert_to_speech',
    'list_voices',
    'list_presets',
    'azure_tts_convert',
    'edge_tts_convert'
]