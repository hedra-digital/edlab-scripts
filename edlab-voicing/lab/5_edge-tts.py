import asyncio
from edge_tts import Communicate

async def main():
    ssml = """<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="pt-BR">
        <voice name="pt-BR-FranciscaNeural">
            <prosody rate="+20%" pitch="+10%">
                Olá! Isto é um texto mais rápido e com tom mais alto.
            </prosody>
            <break time="1s"/>
            <prosody rate="-20%" pitch="-10%">
                E agora mais devagar e com tom mais baixo.
            </prosody>
            <break time="500ms"/>
            <emphasis level="strong">
                Este texto está enfatizado!
            </emphasis>
        </voice>
    </speak>"""
    
    communicate = Communicate(text=ssml, voice="pt-BR-FranciscaNeural")
    await communicate.save("teste_ssml.mp3")

if __name__ == "__main__":
    asyncio.run(main())