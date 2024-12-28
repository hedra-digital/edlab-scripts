import azure.cognitiveservices.speech as speechsdk

speech_config = speechsdk.SpeechConfig(
    subscription="25lM4tmGc07aXoUcE99p99DcJzGAAj8HKZAKyUUG2c1jXk0tgVMKJQQJ99ALACZoyfiXJ3w3AAAYACOGm24o",  # exemplo: "1a2b3c4d5e6f7g8h9i0j"
    region="brazilsouth"  # exemplo: "eastus", "westus", "brazilsouth", etc.
)

speech_config.speech_synthesis_language = "pt-BR"
speech_config.speech_synthesis_voice_name = "pt-BR-FranciscaNeural"

speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

ssml = """
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="pt-BR">
    <!-- Começamos com uma introdução usando voz feminina -->
    <voice name="pt-BR-FranciscaNeural">
        <!-- Ajustando o estilo para narração profissional -->
        <prosody rate="medium" pitch="0Hz">
            Bem-vindos à demonstração de SSML avançado.
        </prosody>
        
        <!-- Demonstração de mudança de velocidade e tom -->
        <prosody rate="+20%" pitch="+10%">
            Esta parte está mais rápida e em um tom mais alto,
            <break time="500ms"/>
            como se estivéssemos empolgados com algo!
        </prosody>
        
        <!-- Pausa dramática -->
        <break time="1s"/>
        
        <!-- Demonstração de fala mais lenta e grave -->
        <prosody rate="-30%" pitch="-15%">
            Agora estamos falando mais devagar e em um tom mais baixo.
            <break time="300ms"/>
            Como se estivéssemos contando um segredo importante.
        </prosody>
        
        <!-- Ênfase especial em palavras -->
        <emphasis level="strong">
            Esta é uma parte muito importante da mensagem!
        </emphasis>
        
        <!-- Controle de volume -->
        <prosody volume="+50%">
            Esta parte está significativamente mais alta!
            <break time="500ms"/>
            <prosody volume="-50%">
                E agora bem mais baixa, quase um sussurro.
            </prosody>
        </prosody>
        
        <!-- Demonstração de números e datas -->
        <say-as interpret-as="date" format="dmy">15/04/2024</say-as>
        <break time="500ms"/>
        <say-as interpret-as="cardinal">12345</say-as>
        
        <!-- Substituição de pronuncia -->
        <sub alias="CSS">Cascading Style Sheets</sub>
        
        <!-- Conclusão com entonação suave -->
        <prosody rate="90%" pitch="-5%">
            Esperamos que tenham gostado desta demonstração de SSML.
            <break time="300ms"/>
            Até a próxima!
        </prosody>
    </voice>
</speak>
"""

result = speech_synthesizer.speak_ssml_async(ssml).get()

if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    print("Síntese completada com sucesso")
elif result.reason == speechsdk.ResultReason.Canceled:
    cancellation_details = result.cancellation_details
    print(f"Síntese cancelada: {cancellation_details.reason}")
    if cancellation_details.reason == speechsdk.CancellationReason.Error:
        print(f"Erro detalhado: {cancellation_details.error_details}")
