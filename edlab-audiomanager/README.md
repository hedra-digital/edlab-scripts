# Audio Editor Lab

Um script em Python para processamento em lote de arquivos de áudio, oferecendo funcionalidades de transcrição de áudio para texto com timestamps.

## Características

- Transcrição de áudio para texto usando Whisper
- Suporte para processamento em lote de múltiplos arquivos
- Barra de progresso para acompanhamento do processamento
- Suporte a arquivos WAV e MP3
- Processamento paralelo para maior velocidade
- Suporte a GPU para transcrição acelerada
- Opção de escolha do modelo Whisper (tiny, base, small, medium, large)

## Requisitos do Sistema

- Python 3.x
- Sistema operacional baseado em Arch Linux (Manjaro, etc.)
- GPU NVIDIA (opcional, mas recomendado para melhor performance)

## Instalação

1. Instale as dependências necessárias usando pacman/yay:

```bash
# Se você tem GPU NVIDIA, instale o pytorch com suporte CUDA
yay -S python-pytorch-cuda

# Instale as outras dependências
yay -S ffmpeg python-openai-whisper python-tqdm

# Resolva dependências do protobuf se necessário
yay -S protobuf
sudo pacman -S protobuf
```

## Uso

### Comando básico:
```bash
./edlab-audio-editor.py -i arquivo.wav --transcript
```

### Opções disponíveis:
```bash
-i, --input     : Arquivo de entrada ou diretório
-o, --output    : Arquivo de saída (opcional)
--transcript    : Realizar transcrição do áudio
--model        : Escolher modelo Whisper (tiny, base, small, medium, large)
--workers      : Número de workers para processamento paralelo
```

### Exemplos de uso:

1. Transcrever um único arquivo:
```bash
./edlab-audio-editor.py -i audio.wav --transcript
```

2. Transcrever com arquivo de saída específico:
```bash
./edlab-audio-editor.py -i audio.wav --transcript -o transcricao.txt
```

3. Processar todos os arquivos WAV em um diretório:
```bash
./edlab-audio-editor.py -i . --transcript
```

4. Processar apenas arquivos WAV específicos:
```bash
./edlab-audio-editor.py -i "*.wav" --transcript
```

5. Usar modelo mais rápido com processamento paralelo:
```bash
./edlab-audio-editor.py -i "*.wav" --model tiny --workers 4 --transcript
```

## Modelos Disponíveis

O Whisper oferece diferentes modelos, balanceando velocidade e precisão:

| Modelo  | Parâmetros | Velocidade Relativa | Uso de Memória |
|---------|------------|---------------------|----------------|
| tiny    | 39M        | Muito Rápido        | Baixo         |
| base    | 74M        | Rápido              | Baixo         |
| small   | 244M       | Médio               | Médio         |
| medium  | 769M       | Lento               | Alto          |
| large   | 1550M      | Muito Lento         | Muito Alto    |

## Saída

O script gera um arquivo de texto com o seguinte formato:
```
TRANSCRIÇÃO: nome_do_arquivo
==================================================

[00:00:00 -> 00:00:05]:
Texto transcrito para este segmento...

[00:00:05 -> 00:00:08]:
Continuação da transcrição...
```

## Desempenho

- Com GPU NVIDIA: Performance até 5x mais rápida
- Processamento paralelo: Melhora significativa ao processar múltiplos arquivos
- Tempo estimado de processamento (1 minuto de áudio):
  - tiny: ~15 segundos
  - base: ~30 segundos
  - small: ~1 minuto
  - medium: ~2 minutos
  - large: ~4 minutos

## Limitações

- O desempenho pode variar significativamente dependendo do hardware
- GPU NVIDIA é recomendada para melhor performance
- Arquivos muito longos podem consumir mais memória

## Licença

Este projeto está licenciado sob a MIT License - veja o arquivo LICENSE para detalhes.