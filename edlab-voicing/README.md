# Voicing - Text-to-Speech Converter

A versatile command-line tool for converting text to speech using multiple engines including Edge TTS, Azure Speech Service, and gTTS. Supports various voices, presets, and customizable speech parameters.

## Features

- Multiple TTS engines support:
  - Microsoft Edge TTS
  - Azure Speech Service
  - Google Text-to-Speech (gTTS)
- Customizable voice presets for different use cases
- Support for SSML and plain text
- Automatic text preprocessing with pattern matching
- Configurable speech parameters (pitch, rate, pauses)
- Support for batch processing of large texts

## Prerequisites

- Python 3.8 or higher
- pipx (for global installation)

### Installing pipx

On Ubuntu/Debian:
```bash
sudo apt update
sudo apt install python3-pip
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

On macOS:
```bash
brew install pipx
pipx ensurepath
```

On Windows:
```bash
python -m pip install --user pipx
python -m pipx ensurepath
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd voicing
```

2. Install using Make:
```bash
make install
```

### Makefile Commands

The project includes a Makefile with several useful commands:

- `make deps`: Creates a virtual environment and installs all dependencies from requirements.txt
- `make install`: Runs `deps`, prepares directories, and installs the package globally using pipx
- `make uninstall`: Removes the global installation of the package
- `make clean`: Removes all temporary files, build artifacts, and the virtual environment
- `make reinstall`: Combination of uninstall, clean, and install - useful for complete reset
- `make prepare`: Creates necessary directories and sets permissions

Alternative manual installation (if you don't want to use Make):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pipx install -e . --force
```

## Usage

### Basic Usage

Convert text to speech:
```bash
voicing --text "Hello, world!" --output hello.mp3
```

Convert text from file:
```bash
voicing -i input.txt -o output.mp3
```

### Using Different Engines

Edge TTS (default):
```bash
voicing -i input.txt --engine edge --voice pt-BR-FranciscaNeural
```

Azure Speech Service:
```bash
voicing -i input.txt --engine azure --voice pt-BR-AntonioNeural
```

Google TTS:
```bash
voicing -i input.txt --engine gtts --language pt-br
```

### Using Presets

Available presets: default, audiobook, news, story, formal

```bash
voicing -i input.txt --preset audiobook
```

### Customizing Voice Parameters

```bash
voicing -i input.txt --pitch 20 --rate -10 --pause 5
```

### Listing Available Options

List available voices:
```bash
voicing --list-voices
```

List available presets:
```bash
voicing --list-presets
```

## Configuration

### Azure Speech Service

To use the Azure Speech Service, you need to set up your credentials:

1. Get your Azure Speech Service key and region
2. Set the following environment variables:
```bash
export AZURE_SPEECH_KEY="your-key-here"
export AZURE_SPEECH_REGION="your-region"
```

### Pattern Matching

Create a `.patterns` file in your project directory or globally to define text replacement patterns:

```json
[
  {
    "name": "numbers",
    "pattern": "\\b\\d+\\b",
    "replacement": "number"
  }
]
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.