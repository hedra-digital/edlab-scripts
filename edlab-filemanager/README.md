# Histórico

Precisávamos o tempo todo corrigir padrões de arquivos dentro de diretórios. Exemplo: page-1.png para page-001.png. Ou cropar e remover sufixos. Milhares de arquivos!

# Dependências

Todas as do edlab-pdfconverter e mais:
1. `sudo pacman -S python-colorama`


# File Manager Script

Este script Python oferece funcionalidades avançadas para gerenciar e renomear arquivos em lote. Ele é especialmente útil para organizar grandes coleções de arquivos, alinhando valores numéricos ou aplicando renomeações baseadas em uma tabela predefinida.

## Principais Funcionalidades

1. **Renomeação baseada em tabela**: Renomeia arquivos de acordo com um mapeamento definido em um arquivo de tabela.
2. **Alinhamento de valores numéricos**: Ajusta os números nos nomes dos arquivos para terem a mesma quantidade de dígitos.
3. **Visualização em árvore**: Mostra a estrutura de diretórios e as mudanças planejadas.
4. **Modo de simulação (dry-run)**: Permite visualizar as mudanças sem aplicá-las.
5. **Processamento recursivo**: Opção para processar subdiretórios.
6. **Filtros de prefixo e sufixo**: Permite processar apenas arquivos com determinados prefixos ou sufixos.
7. **Prevenção de sobrescrita**: Solicita confirmação antes de sobrescrever arquivos existentes.

### Uso

```
edlab-filemanager [opções] arquivo1 arquivo2 | caminho1 [caminho2 ...]
```

### Opções

- `--tree`: Processa diretórios recursivamente.
- `--align-place-values` ou `-pva`: Alinha valores numéricos nos nomes dos arquivos.
- `--table-name` ou `-tn`: Especifica um arquivo contendo a tabela de renomeação.
- `--prefix-pattern` ou `-pp`: Processa apenas arquivos que começam com o prefixo especificado.
- `--suffix-pattern` ou `-sp`: Processa apenas arquivos que terminam com o sufixo especificado.
- `--dry-run`: Mostra as mudanças sem aplicá-las.
- `--ignore-overwrites`: Ignora potenciais sobrescritas sem pedir confirmação.

## Exemplos

1. Renomear arquivos usando uma tabela:

```
 edlab-filemanager --table-name="nomes.list" /caminho/para/diretorio
```

2. Alinhar valores numéricos em nomes de arquivos dentro de pastas (--dry-run para verificar o que será executado):

```
 edlab-filemanager --tree --dry-run --table-name renaming_table.txt /caminho/para/diretorio
```

4. Processar apenas arquivos com um determinado sufixo ou prefixo:
```
 edlab-filemanager --suffix-pattern=".jpg" --prefix-pattern="file" --align-place-values /caminho/para/diretorio
```

## Notas

- Cuidado ao rodar para não perder arquivos!
- O script usa colorama para saída colorida no terminal.
- Sempre faça um backup dos seus arquivos antes de executar operações de renomeação em massa.

