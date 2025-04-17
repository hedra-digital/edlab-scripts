# Text-to-Speech (TTS) Command Line Tool
Um utilitário de linha de comando para converter texto em fala usando diferentes engines de síntese de voz.

## Atenção

Ussar python 3.12.9

```
pyenv install 3.12
pyenv local 3.12.9
```

## 🌟 Características

- Múltiplos engines de síntese de voz:
  - Azure Speech Service
  - Edge TTS
  - Google Text-to-Speech (gTTS)
- Presets predefinidos para diferentes estilos de narração
- Suporte a SSML (Speech Synthesis Markup Language)
- Controle de pitch e velocidade
- Pausas automáticas customizáveis
- Suporte a múltiplos idiomas

## 📋 Pré-requisitos

```bash
# Instale as dependências necessárias
pip install azure-cognitiveservices-speech edge-tts gtts tqdm
```

Para usar o Azure Speech Service, você precisará de:
1. Uma conta Azure
2. Um recurso de Speech Service configurado
3. Chave de API e região definidas como variáveis de ambiente:

```bash
export AZURE_SPEECH_KEY="sua_chave_aqui"
export AZURE_SPEECH_REGION="sua_região_aqui"
```

## 🚀 Uso Básico

### Texto Simples
```bash
python voicing.py --text "Olá mundo!" --engine azure --preset default -o saida.mp3
```

### Com SSML
```bash
python voicing.py --text "<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='pt-BR'><voice name='pt-BR-AntonioNeural'><prosody rate='-15%' pitch='-10Hz'>Seu texto aqui</prosody></voice></speak>" --engine azure -o saida.mp3
```

### Com Pausas Automáticas
```bash
python voicing.py --text "Primeira frase. Segunda frase! Terceira frase?" --pause 5 --engine azure -o saida.mp3
```

### com arquivos

```bash
python voicing.py -i ./examples/noticia.txt --engine azure --preset news --pause 3 -o noticia.mp3
```





## 🎭 Presets Disponíveis

| Preset     | Descrição                                    | Voz                  | Pitch | Rate  |
|------------|----------------------------------------------|---------------------|-------|-------|
| default    | Configuração padrão balanceada               | Francisca (fem)     | 0     | 0     |
| audiobook  | Otimizado para narração de livros           | Antonio (masc)      | -10   | -15   |
| news       | Estilo de apresentação de notícias          | Francisca (fem)     | 0     | +10   |
| story      | Narração suave para histórias               | Brenda (fem)        | 0     | -10   |
| formal     | Tom profissional para documentos            | Antonio (masc)      | -20   | -5    |

## 🏷️ Exemplos de Tags SSML

### Ênfase
```xml
<emphasis level="strong">Texto enfatizado</emphasis>
```

### Datas
```xml
<say-as interpret-as="date" format="dmy">15/04/2024</say-as>
```

### Siglas/Abreviações
```xml
<sub alias="I B M">IBM</sub>
```

### Pausas
```xml
<break time="500ms"/>
```

## 🎯 Exemplos Completos

### Exemplo com Múltiplas Tags SSML
```bash
python voicing.py --text "Hoje, dia <say-as interpret-as='date' format='dmy'>15/04/2024</say-as>, iniciamos nosso teste de síntese de voz. A <emphasis level='strong'>inteligência artificial</emphasis> está transformando nossa forma de interagir com a tecnologia! Você sabia que a <sub alias='I B M'>IBM</sub> foi uma das pioneiras nesta área?" --engine azure --preset audiobook --pause 5 -o teste_simples.mp3
```

## 🛠️ Opções de Comando

```bash
  -i, --input        Arquivo de entrada (markdown ou txt)
  --text            Texto para converter em áudio
  -o, --output      Nome do arquivo de saída (padrão: output.mp3)
  --engine          Motor de síntese (gtts/edge/azure)
  --language        Código do idioma para gTTS (padrão: pt-br)
  --voice           Voz a ser usada (padrão: pt-BR-FranciscaNeural)
  --pitch           Ajuste do tom (-100 a +100)
  --rate            Ajuste da velocidade (-100 a +100)
  --pause           Tamanho das pausas (0 para desativar)
  --preset          Usar configuração predefinida
  --list-voices     Lista todas as vozes disponíveis
  --list-presets    Lista todos os presets disponíveis
```

## 📚 Links Úteis

- [Portal Azure](https://portal.azure.com)
- [Documentação do Azure Speech Service](https://docs.microsoft.com/azure/cognitive-services/speech-service/)
- [Referência SSML](https://docs.microsoft.com/azure/cognitive-services/speech-service/speech-synthesis-markup)

## 📝 Notas

1. O Azure Speech Service oferece recursos avançados como:
   - Estilos de fala (narração, notícias, etc.)
   - Controle de emoções
   - Pausas naturais
   
2. As pausas automáticas (--pause) são úteis para:
   - Melhorar a naturalidade da fala
   - Criar ritmo na narração
   - Facilitar a compreensão

3. Os presets foram otimizados para:
   - Audiobooks (narração profissional)
   - Notícias (apresentação clara)
   - Histórias (narração envolvente)
   - Documentos formais (tom profissional)

# Com o python


## Não esquecer de ativar a máquina virtual

```bash
source venv/bin/activate
```

## Se precisar reinstalar libs

```bash
pip install azure-cognitiveservices-speech edge-tts gtts tqdm
```

## Como gerar e instalar o arquivo requirements.txt

```bash
pip freeze > requirements.txt
pip install -r requirements.txt
```


