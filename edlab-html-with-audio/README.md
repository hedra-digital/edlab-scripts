# Histórico

Scripts pensados para converter arquivos .md para .html com navegabilidade e áudio integrados. Foram criados a partir dos padrões de acessibilidade exigidos pelo PNLD026.

# Dependências

É preciso instalar a biblioteca *pydub* do Python:
1. `pip install pydub`


# File Manager Script

Os três scripts Python correspondem a três etapas na criação de um HTML, conforme as necessidades colocadas pelo PNLD2026.

## Principais Funcionalidades

A ordem de execução dos scripts é:

1. **Convert_MD_to_HTML**: Separa e converte um arquivo .md em vários arquivos .html. A divisão do html sempre ocorre no elemento [Página X] do .md, e o arquivo .html vai ser nomeado com base no valor de X. Além de dividir e converter para o html, ele já insere o número da página no html, conforme o valor de X, e cria um preâmbulo pra cada HTML em que estão os elementos de navegabilidade: uma barra acima da página com a indicação de "Sumário", "Anterior" e "Próxima", para navegar entre as páginas do HTML.
2. **Create_Index_HTML_With_Metadata**: Cria o arquivo index.html com base nas páginas divididas do livro. Nele estarão os links (sumário) para todos os elementos do HTML exigidos pelo edital e os metadados do livro. O sumário sempre indica a primeira e a última página da obra, que são criadas com base na primeira e na última página do arquivo .html que foi dividido na etapa anterior.
3. **Synchronize_Audio_Files_With_HTML**: Insere, em cada página do HTML, o display de controle para reproduzir um áudio. O display é inserido com o áudio correspondente à página correta: para o arquivo pag_XX.html, ele cria o display com o arquivo de áudio PNLD2026_000_pg_XX.mp3. Ele também insere, em cada frase iniciada por <p> do html, um "id=" que vai servir para a sincronização do áudio. Por fim, cria um arquivo nomeado sync.js, em que estão elencados todos os "id" criados nos arquivos com o tempo de início e fim correspondente a cada áudio. Nesse arquivo sync.js estão definidos os comandos que "pintam" as frases do livro conforme o andamento do áudio.

### Uso

```
python3 Convert_MD_to_HTML.py ARQUIVO.md "TÍTULO DO LIVRO"
```

*Obs.: É preciso preencher o título do livro na linha de comando para que ele seja inserido em cada página de .hmtl criada e separada.*

```
python3 Create_Index_HTML_With_Metadata.py
```

*Obs.: Os metadados são preenchidos com base em um arquivo metadados.txt, cujo exemplo se encontra nesse diretório.*

```
python3 Synchronize_Audio_Files_With_HTML.py
```

*Obs.: Ele sempre vai procurar os arquivos de áudio dentro de uma pasta nomeada audio.*

## Notas

- Os três scripts devem ser rodados na ordem apresentada e no mesmo diretório;
- Após a criação de todos os arquivos, as páginas separadas do html devem ser alocadas na pasta *content*; o index.html e o sync.js devem ficar na raiz da pasta; as imagens devem ficar na pasta *img* dentro da pasta *resource*, na qual também estará a pasta *styles*, com o .css.
