import pyttsx3

engine = pyttsx3.init()
engine.say('<speak>Texto com <emphasis>SSML</emphasis></speak>', 'ssml')
engine.runAndWait()
