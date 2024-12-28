import boto3

polly = boto3.client('polly')
response = polly.synthesize_speech(
    Text='<speak>Texto SSML</speak>',
    TextType='ssml',
    OutputFormat='mp3',
    VoiceId='Vitoria'
)