import requests, json, base64, shutil, glob
from datetime import datetime
from env import arquivo_conf, headers

class Extract:

    lista_pdfs = []

    def __init__(self):
        self.lista_pdfs = []
        for first_folder in glob.iglob(r'data/*'):
            if len(glob.glob1(first_folder, "*")) == 0:
                self.write_log('\n{} -> {} está vazia\n'.format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), first_folder))
                print("{} está vazia".format(first_folder))
            for folders in glob.iglob(r'{}/*'.format(first_folder)):
                #Verifcando se há arquivos .PDF nas pastas
                if len(glob.glob1(folders,"*.pdf")) == 0:
                    self.write_log("\n{} -> Não há arquivos PDF para processar em: {}\n".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), folders))
                    print("Não há arquivos PDF para processar em: {}".format(folders))
                else:
                    for pdf in glob.iglob(r'{}/*.pdf'.format(folders)):
                        self.write_log('\n{} -> Processando arquivo: {}\n'.format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), pdf))
                        print('Processando arquivo: {}'.format(pdf))
                        if folders in arquivo_conf:
                            chave_valor = {}
                            chave_valor[arquivo_conf[folders]] = pdf
                            self.lista_pdfs.append(chave_valor)
                        else:
                            self.write_log("\n{} -> Diretório {} não cadastrado no arquivo de configuração\n".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), folders))
                            print("Diretório {} não cadastrado no arquivo de configuração".format(folders))

        return self.insert_ged(self.lista_pdfs)

    def post_request(self, data, processed):
        response = requests.post("YOUR_ENDPOINT_HERE", headers=headers, data=data)

        if response.status_code == 200 or response.status_code == 201:
            self.write_log('\n{} -> {} processado com sucesso!\n'.format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), processed))
            print('{} processado com sucesso!'.format(processed))
            shutil.move(processed, 'processados/')
        else:
            self.write_log('\n{} -> Houve um erro ao processar o arquivo\n'.format(datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
            print('Houve um erro ao processar o arquivo')

    def insert_ged(self, pdfs):

        for pdf in pdfs:
            for area, _pdf in pdf.items():
                pwd_pdf = _pdf
                #BASE64 PDF
                with open(_pdf, "rb") as pdf_file:
                    read_pdf = base64.b64encode(pdf_file.read())
                    pdf_decoded = read_pdf.decode('utf-8')
                
                _pdf = self.data_munging(_pdf)

                pdf_json = {"idArea": "{}".format(arquivo_conf['AREA_GED']),
                            "idUsuario" : 2,
                                    "listaIndice": [
                                    {
                                    "idTipoIndice": 12,
                                    "identificador": "orgao",
                                    "valor": _pdf['orgao']
                                    },
                                    {
                                    "idTipoIndice": 15,
                                    "identificador": "desc",
                                    "valor": _pdf['descricao']
                                    },
                                ],
                                "listaDocumento" : [
                                {
                                "listaIndice": [
                                    {
                                    "idTipoIndice": 12,
                                    "identificador": "tipo",
                                    "valor": _pdf['tipo']
                                    },
                                ],
                                "endereco" : "teste",
                                "idArea": "{}".format(arquivo_conf['AREA_GED']),
                                "bytes" : pdf_decoded
                                }
                            ]
                            }
                jsonData = json.dumps(pdf_json)
                self.post_request(jsonData, pwd_pdf)
            
                
    def data_munging(self, string):
        
        string = string.split('/')[-1]
        string = string.split('-')
        tipo_pdf = string[0]
        orgao_pdf = string[1]
        desc_pdf  = string[2]
        paginas_pdf = string[3]
        hora_pdf = string[4].replace('.pdf', '')

        params = {
            'tipo' : tipo_pdf,
            'orgao' : orgao_pdf,
            'paginas' : paginas_pdf,
            'hora' : hora_pdf,
            'descricao' : desc_pdf
        }
        return params



    def write_log(self, log):
        f = open('logs.txt', 'a+')
        f.write(str(log))
        f.close()


if __name__ == "__main__":
    d = Extract()    