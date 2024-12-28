from google.cloud import texttospeech

client = texttospeech.TextToSpeechClient()
synthesis_input = texttospeech.SynthesisInput(
    ssml='<speak>Seu texto SSML aqui</speak>'
)