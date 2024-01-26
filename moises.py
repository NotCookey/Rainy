import requests
import json
import time
import os
import wget


class Moises:

    def __init__(self, api_key):
        self.api_key = api_key

    def get_file_urls(self):  # obter um link que possa subir a musica e baixar
        headers = {
            'Authorization': self.api_key,
        }
        response = requests.get(
            "https://api.music.ai/api/upload", headers=headers)
        json_data = response.json()

        upload_url = json_data['uploadUrl']
        download_url = json_data['downloadUrl']
        return upload_url, download_url

    def upload(self, arquivo):  # subir a musica para o link obtido na funçao get_file_urls

        upload_url, download_url = self.get_file_urls()

        headers = {
            'Content-Type': 'audio/mpeg',
        }

        response = requests.put(
            upload_url, headers=headers, data=open(arquivo, 'rb'))

        print("FUNCAO UPLOAD")
        print(response.status_code)

        return download_url

    # baixar o arquivo de audio separado
    def download_arquivo(self, url, pasta, nome_arq):
        if not (os.path.exists(pasta)):
            os.mkdir(pasta)

        download = pasta + "\\" + nome_arq

        response = wget.download(url, download)

        print("FUNCAO DOWNLOAD")
        print(response)

        return response

    def separa_vocal(self, arquivo):

        download_url = self.upload(arquivo)
        print("parametro arquivo (separa): ", arquivo)
        nome_arq = os.path.basename(arquivo)

        headers = {
            'Authorization': self.api_key,
            'Content-Type': 'application/json'
        }
        data = {
            "name": "job_test_from_python",
            "workflow": "separa_vocal",
            "params": {
                "inputUrl": download_url
            }
        }

        response = requests.post(
            "https://api.music.ai/api/job", headers=headers, json=data)

        print("FUNCAO SEPARA VOCAL")
        print(response.status_code)
        print(response.json())

        while (1):

            job_url = "https://api.music.ai/api/job/" + response.json()['id']
            headers = {
                'Authorization': self.api_key,
            }
            response = requests.get(job_url, headers=headers)
            if response.json()['status'] == 'SUCCEEDED':
                # baixa o arquivo
                print(response.json())

                vocais = response.json()['result']['vocal']
                resto = response.json()['result']['resto']

                # path = "C:\\Code-1\\Hacka\\RhythmPlayer-\\teste\\" + nome_arq

                path = os.getcwd() + "\\out\\" + nome_arq

                voc_path = self.download_arquivo(vocais, path, "vocal.wav")
                instr_path = self.download_arquivo(resto, path, "instr.wav")

                if (os.path.exists(voc_path) and os.path.exists(instr_path)):
                    print("Arquivos baixados com sucesso")
                    paths = [voc_path, instr_path]
                    print("paths: ", paths)
                    return paths
                else:
                    print("Erro ao baixar arquivos")
                    return None

            elif response.json()['status'] == 'FAILED':

                print("JOB FAILED")
                break

            time.sleep(5)

    def ler_pasta(self, pasta):
        arquivos = os.listdir(pasta)

        arquivos_mp3 = [os.path.join(
            pasta, arquivo) for arquivo in arquivos if arquivo.lower().endswith('.mp3')]

        paths = {}

        for arquivo in arquivos_mp3:
            path = self.separa_vocal(arquivo)
            if path is None:
                print(
                    f"Erro ao separar vocal do arquivo {os.path.basename(arquivo)}")
            else:
                paths[os.path.basename(arquivo)] = path

        print("paths: ", paths)

        return paths

# moises = Moises('api-key-aqui')

# #para testar coloque o path em que estao suas musicas nessa funçao e rode moises.py
# paths = moises.ler_pasta("seu/path/aqui")

# with open("./data/paths.json", "w") as arquivo_json:
#     json.dump(paths, arquivo_json)

# path = os.getcwd()
# print(path)


'''
paths =  {'song - Copia (2).mp3': ['C:\\Code-1\\Hacka\\RhythmPlayer-\\out\\song - Copia (2).mp3\\vocal.wav', 
                                  'C:\\Code-1\\Hacka\\RhythmPlayer-\\out\\song - Copia (2).mp3\\instr.wav'], 
         'song - Copia.mp3': ['C:\\Code-1\\Hacka\\RhythmPlayer-\\out\\song - Copia.mp3\\vocal.wav', 
                              'C:\\Code-1\\Hacka\\RhythmPlayer-\\out\\song - Copia.mp3\\instr.wav'], 
         'song.mp3': ['C:\\Code-1\\Hacka\\RhythmPlayer-\\out\\song.mp3\\vocal.wav', 
                      'C:\\Code-1\\Hacka\\RhythmPlayer-\\out\\song.mp3\\instr.wav']}

json = json.dumps(paths)
print(json)


{'id': 'fa4ad6a6-e426-494f-af46-e988fc42130a', 'app': 'Default Application', 'workflow': 'separa_vocal', 'status': 'SUCCEEDED', 'batchName': None, 'workflowParams': {
'inputUrl': 'https://storage.googleapis.com/moises-production--tmp/developer-portal/309b1612-4e10-42d2-bd83-1bca6aa97dcb?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=731360694588-compute%40developer.gserviceaccount.com%2F20240124%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20240124T180818Z&X-Goog-Expires=86400&X-Goog-SignedHeaders=host&X-Goog-Signature=9ebc05d07201a0fa2f2f6d00e5cb3ab658576193e31a10bbf76d4cfb42d0a2cb06781226f9a71e3cc5ac1c18f577fff6b9ebbb4a00922835b8b9a05da76dfc32acebed2bdcdd8c8fff09a2350437eec38ae49c320cd4e77c53aa4e86601d668e717bd3696cc84f26d86c39f06e22eb2068011aebb09039006dbd3cbcc84e5f2d9c4cad0ba4914c6e1c6562b10a380cb457a9a7e799a41338905f5c5ed9b39070be39a35fe8f8d37290cf6ac8d08021c3cdfa3b48ce4e6bad4f7aa48b93643476e135b3f9bb2b543f10f3c747034c037e1acf6972f8f916502fe966fe43feea922484ae11b270e75f5b3862c00f25c15ad4e6139696a74e0847f4ea10ee183b6d'}, 
'metadata': {}, 
'result': { 'resto': 'https://storage.googleapis.com/moises-production--developer/orchestrator/9b8c908c-460c-4ae2-8dca-58bde974d252/868f5401-eacb-4d3a-9c34-ac1b3015f54f/bk_vocals-vocals-other-hifi--other.wav?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=731360694588-compute%40developer.gserviceaccount.com%2F20240124%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20240124T180904Z&X-Goog-Expires=596160&X-Goog-SignedHeaders=host&X-Goog-Signature=8ee4f3350d417245e3511dddb2226ec71f4c709fb434b0a57c3fffb9bdd847f583aa84276db3d45ed8e6fa3d85141f7c57b76e61562a9c4ebc7c7dabc64320c74a1af77527e8d7cc290c1cc5ec7c9332e69a71e740d9d032c9e9e698726956e3c9581ff14c1fd7d71483e27d3568b9b6b09211bd5654e9a16b3c8a90be97bf1d4ccd6b991513f4ff56f5b354c2f9515170e631b84b0e9d212d0ae4a0e98eeb4f160eb05aa31cda8883c21aa2105b1c3c2c83a091c7772e03118ad521111371744051d37724f7791d72b92020b8930f557a32202c879557fdc77fd2623876e9478f4e0bc6a78e5cd698ba50181ac2a75076ac21eb67cda499d5211a7a307c6488', 
            'vocal': 'https://storage.googleapis.com/moises-production--developer/orchestrator/cadd1a3e-ab2b-4cd8-8ef0-f1ca046b358d/988ad8b4-5d4c-42e0-96f1-d800324f9f49/job_test_from_python--vocal.wav?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=731360694588-compute%40developer.gserviceaccount.com%2F20240124%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20240124T181025Z&X-Goog-Expires=596160&X-Goog-SignedHeaders=host&X-Goog-Signature=00ec00235086d7a2bf38ea8476979d748fc86363dd286e8581c5d6e4c6d20a1f1f4b19231e316b1375a0ef0b68d74e7dc6b9bb61e55f1296435e95d2db38581ed268634f8e0fcdbb18cd4a468f3f9c53bc69e013d6e26c627760bf3b40d446fa406b6ba7404fac78463dc19a92610ea9c530a155530b21b3e0c4e11f46e291a72366d37f0c548558d85a32a44545117b964d0709ed4381376767badd5142ffaa5ee6b3f2ea122a3a7b18cdfaf39eff060b975bc0326a28224c47f2bbcb09691ca75ca54cdfd96e8688a6afc13a3ffe2100cc86dff6547bf4433ca57224d9a4be99d90623b2ecc41f0800da2f03fe571c12373845c51eafd8a612c059c7ccab7a'}, 
'name': 'job_test_from_python', 
'createdAt': '2024-01-24T18:08:24.229Z', 
'startedAt': '2024-01-24T18:08:24.253Z', 
'completedAt': '2024-01-24T18:10:20.162Z'}

'''
