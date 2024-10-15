import os
import re
from pydub import AudioSegment

def inserir_audio_html(diretorio_html, diretorio_audio):
    # Listar todos os arquivos de áudio no diretório de áudio
    arquivos_audio = sorted([f for f in os.listdir(diretorio_audio) if f.endswith(".mp3")])

    # Criar um dicionário para mapear os números finais dos arquivos de áudio e suas durações
    audio_map = {}
    duracao_map = {}
    prefixo_map = {}
    for audio in arquivos_audio:
        # Extrair o número do final do nome do arquivo de áudio (exemplo: 22 em PNLD2026_001_pg_22.mp3)
        match = re.search(r'_(\d+)\.mp3$', audio)
        if match:
            numero = match.group(1)
            audio_map[numero] = audio
            
            # Obter a duração do áudio usando pydub
            caminho_audio = os.path.join(diretorio_audio, audio)
            audio_duracao = AudioSegment.from_mp3(caminho_audio).duration_seconds
            duracao_map[numero] = int(audio_duracao)  # Duração do áudio em segundos

            # Pegar o prefixo até o _pg_ para o arquivo correspondente (exemplo: PNLD2026_001_pg)
            prefixo = audio.rsplit('_pg_', 1)[0] + '_pg_'
            prefixo_map[numero] = prefixo

    # Manter controle do ID sequencial para os parágrafos
    id_counter = 1
    sync_map = {}

    # Listar todos os arquivos HTML no diretório de HTML
    arquivos_html = sorted([f for f in os.listdir(diretorio_html) if f.endswith(".html")])

    # Iterar sobre os arquivos HTML
    for html in arquivos_html:
        # Extrair o número do final do nome do arquivo HTML (exemplo: 22 em pag-22.html)
        match_html = re.search(r'pag-(\d+)\.html$', html)
        if match_html:
            numero_html = match_html.group(1)

            # Verificar se há um áudio correspondente para este HTML
            if numero_html in audio_map:
                caminho_html = os.path.join(diretorio_html, html)
                caminho_audio = os.path.join(diretorio_audio, audio_map[numero_html])

                # Ler o conteúdo do arquivo HTML
                with open(caminho_html, 'r', encoding='utf-8') as file:
                    conteudo_html = file.readlines()

                # Verificar se o comando <audio> já foi inserido
                if any('<audio id="audio"' in line for line in conteudo_html):
                    print(f"O comando de áudio já está presente em {html}.")
                    continue

                # Inserir o comando de áudio após a tag <p class="numeracao">
                audio_inserido = False
                for idx, linha in enumerate(conteudo_html):
                    if '<p class="numeracao"' in linha:
                        # Usar o prefixo correto para o nome do arquivo de áudio
                        prefixo = prefixo_map[numero_html]
                        audio_tag = f'''
    <audio id="audio" controls>
        <source src="../audio/{prefixo}{numero_html}.mp3" type="audio/mpeg">
    </audio>\n'''
                        conteudo_html.insert(idx + 1, audio_tag)
                        audio_inserido = True
                        break

                # Se o áudio foi inserido, adicionar IDs crescentes aos parágrafos COM TEXTO após o áudio
                if audio_inserido:
                    for idx in range(idx + 2, len(conteudo_html)):
                        linha = conteudo_html[idx].strip()
                        if linha.startswith("<p>") and not linha.startswith("<p></p>"):
                            # Adicionar o id incremental sem vírgula após o <p>
                            conteudo_html[idx] = conteudo_html[idx].replace('<p>', f'<p id="id{id_counter}">')
                            # Atualizar o syncMap com o tempo do áudio
                            sync_map[f"id{id_counter}"] = {
                                "start": 0,
                                "end": duracao_map[numero_html]
                            }
                            id_counter += 1

                # Escrever o conteúdo modificado de volta no arquivo HTML
                with open(caminho_html, 'w', encoding='utf-8') as file:
                    file.writelines(conteudo_html)

                print(f"Comando de áudio e IDs inseridos em {html}.")

    # Criar o arquivo sync.js com os IDs e as durações
    gerar_sync_js(sync_map)

def gerar_sync_js(sync_map):
    sync_js_content = '''const syncMap = {\n'''
    
    for id_, timing in sync_map.items():
        sync_js_content += f'    "{id_}": {{ "start": {timing["start"]}, "end": {timing["end"]} }},\n'
    
    sync_js_content += '''};

document.addEventListener("DOMContentLoaded", function() {
    const audio = document.getElementById("audio");

    if (audio) {
        audio.addEventListener("timeupdate", function() {
            const currentTime = audio.currentTime;

            for (const [id, timing] of Object.entries(syncMap)) {
                const element = document.getElementById(id);
                if (!element) continue; // Pular IDs que não estão na página atual

                const text = element.innerText;
                const totalLength = text.length;

                if (currentTime >= timing.start && currentTime <= timing.end) {
                    const elapsed = currentTime - timing.start;
                    const duration = timing.end - timing.start;
                    const progress = elapsed / duration;

                    // Calcula o número de caracteres a serem destacados
                    const charsToHighlight = Math.floor(progress * totalLength);

                    // Destaca progressivamente o texto com grifo amarelo
                    element.innerHTML = `
                        <span style="background-color: yellow;">${text.slice(0, charsToHighlight)}</span>${text.slice(charsToHighlight)}
                    `;
                } else if (currentTime > timing.end) {
                    element.innerHTML = `<span style="background-color: yellow;">${text}</span>`;
                } else {
                    element.innerHTML = text;
                }
            }
        });
    }
});
'''

    # Escrever o arquivo sync.js
    with open("sync.js", "w", encoding="utf-8") as sync_file:
        sync_file.write(sync_js_content)

    print("Arquivo sync.js criado com sucesso!")

# Exemplo de uso
if __name__ == "__main__":
    diretorio_html = os.getcwd()  # O diretório atual onde o script está sendo executado
    diretorio_audio = os.path.join(diretorio_html, "audio")  # Pasta "audio" dentro do diretório atual
    inserir_audio_html(diretorio_html, diretorio_audio)
