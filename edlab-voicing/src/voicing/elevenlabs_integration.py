"""
ElevenLabs Text-to-Speech Integration Module
"""
import requests
import json
from pathlib import Path

class ElevenLabsTTS:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }

    async def convert_to_speech(self, text, output_path, voice_id="MZxV5lN3cv7hi1376O0m"):
        """
        Converts text to speech using a specific ElevenLabs voice
        
        Args:
            text (str): Text to be converted to speech
            output_path (str): Path where the audio file will be saved
            voice_id (str): Voice ID (default: Ana Dias)
        
        Returns:
            bool: True if conversion successful, False otherwise
        """
        url = f"{self.base_url}/text-to-speech/{voice_id}/stream"
        
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }

        try:
            response = requests.post(url, json=data, headers=self.headers)
            
            if response.status_code == 200:
                with open(output_path, 'wb') as audio_file:
                    audio_file.write(response.content)
                return True
            else:
                error_detail = response.json() if response.headers.get('content-type') == 'application/json' else response.text
                raise Exception(f"Error in request: {response.status_code} - {error_detail}")
                
        except Exception as e:
            raise Exception(f"Error generating audio: {str(e)}")

# Available voices dictionary
ELEVENLABS_VOICES = {
    "Ana Dias": "MZxV5lN3cv7hi1376O0m",  # Default voice
    "Manuel": "NKKvpecEshlHm99K9zn9",
}