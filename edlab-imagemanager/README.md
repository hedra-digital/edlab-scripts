# edlab-designtool

edlab-designtool é um script Python versátil para processamento de imagens, projetado principalmente para trabalhar com capas de livros ou outras imagens que precisam ser padronizadas ou modificadas para o site. 

## Funcionalidades

- Adicionar uma borda fina a imagens
- Criar imagens quadradas com conteúdo centralizado
- Personalizar a cor de fundo para imagens quadradas
- Processar arquivos individuais ou em lote
- Especificar diretórios de entrada e saída personalizados
- Customizar o sufixo dos arquivos de saída

## Requisitos

- Python 3.x
- Pillow (PIL Fork)

Para instalar o Pillow, use:

```
pip install Pillow
```

## Uso

### Sintaxe Básica

```
edlab-designtool [opções] arquivo(s)
```

### Opções

- `-i`, `--input-dir`: Diretório de entrada para imagens
- `-o`, `--output-dir`: Diretório de saída para imagens processadas
- `-b`, `--border-width`: Largura da borda preta (padrão: 1)
- `-s`, `--square`: Criar uma imagem quadrada com conteúdo centralizado
- `--suffix`: Sufixo para imagens processadas (padrão: 'new')
- `--background-color`: Cor de fundo em formato hexadecimal (padrão: #E9EAEC)

### Exemplos

1. Criar uma imagem quadrada:
   ```
   edlab-designtool imagem.png --square
   ```

2. Adicionar uma borda a uma imagem:

   ```
   edlab-designtool imagem.png
   ```

3. Especificar a largura da borda:
   ```
   edlab-designtool imagem.png -b 3
   ```

4. Usar um sufixo personalizado para salvar o nome do arquivo:
   ```
   edlab-designtool imagem.png --suffix customizado
   ```

5. Definir uma cor de fundo personalizada:
   ```
   edlab-designtool imagem.png --square --background-color "#FF0000"
   ```

6. Processar múltiplos arquivos:
   ```
   edlab-designtool *.png -o pasta_saida
   ```
	ou um diretório inteiro de imagens

   ```
   edlab-designtool -i . --square
   ```
7. Combinando várias opções:
   ```
   edlab-designtool imagem.png --square -b 2 --suffix quadrado --background-color "#00FF00" -o pasta_saida
   ```

## Notas

- Por padrão, as imagens processadas são salvas no mesmo diretório que as imagens originais, a menos que um diretório de saída seja especificado.
- Quando a opção `--square` não é usada, o script apenas adiciona uma borda à imagem.
- O script suporta imagens nos formatos PNG, JPG e JPEG.

## Contribuições

Contribuições para melhorar o CoverSquare são bem-vindas. Por favor, sinta-se à vontade para forkar o repositório, fazer suas modificações e enviar um pull request.

## Licença

Este projeto é distribuído sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## Claude

https://claude.ai/chat/d2e998ce-c69e-4c99-8b04-5dabcaef6cef
