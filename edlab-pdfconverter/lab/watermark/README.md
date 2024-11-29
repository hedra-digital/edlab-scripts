# PDF Watermark Script

Um script Python simples e eficiente para adicionar marcas d'água em documentos PDF. O script adiciona uma marca d'água em cinza claro, diagonal e semitransparente em todas as páginas do PDF.

## Características

- Adiciona marca d'água em todas as páginas do PDF
- Texto em cinza claro com 30% de opacidade
- Marca d'água rotacionada em 45 graus
- Preserva o conteúdo original do documento
- Gera um novo arquivo, mantendo o original intacto
- Suporta textos personalizados para a marca d'água
- Palavra "WATERMARK" como marca d'água padrão

## Requisitos

- Python 3.6 ou superior
- PyPDF2
- reportlab

## Instalação

1. Clone este repositório ou baixe o script
2. Instale as dependências necessárias:

```bash
pip install PyPDF2 reportlab
```

## Uso

O script pode ser usado de três maneiras diferentes:

1. Com marca d'água personalizada:
```bash
python script.py -i arquivo.pdf --watermark "Confidencial"
```

2. Com a marca d'água padrão "WATERMARK":
```bash
python script.py -i arquivo.pdf --watermark
```

3. Sem especificar a marca d'água (usará "WATERMARK" como padrão):
```bash
python script.py -i arquivo.pdf
```

## Argumentos

- `-i` ou `--input`: Caminho do arquivo PDF de entrada (obrigatório)
- `--watermark`: Texto da marca d'água (opcional, padrão: "WATERMARK")

## Saída

O script gera um novo arquivo PDF no mesmo diretório do arquivo de entrada, adicionando o sufixo "_watermark" ao nome original.

Exemplo:
- Arquivo de entrada: `documento.pdf`
- Arquivo de saída: `documento_watermark.pdf`

## Exemplos de Uso

1. Adicionar a marca d'água "CONFIDENCIAL":
```bash
python script.py -i contrato.pdf --watermark "CONFIDENCIAL"
```

2. Usar a marca d'água padrão:
```bash
python script.py -i relatorio.pdf
```

## Estrutura do Código

O script é composto por três funções principais:

- `create_watermark()`: Cria o PDF da marca d'água
- `add_watermark()`: Adiciona a marca d'água ao PDF original
- `main()`: Função principal que processa os argumentos e executa o script

## Tratamento de Erros

O script inclui tratamento de erros básico e fornecerá mensagens de erro claras em caso de:
- Arquivo de entrada não encontrado
- Arquivo PDF inválido
- Erro durante o processamento

## Limitações

- O tamanho e a fonte da marca d'água são fixos
- A posição da marca d'água é centralizada na página
- A rotação é fixa em 45 graus
- A cor é sempre cinza claro com 30% de opacidade

## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir melhorias
- Enviar pull requests

## Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.