""" Melhorias pendentes:
Alguns textos nao tem o atributo string, de forma quee nao e possivel ver a justificativa
Definir classe navegador
"""

#from selenium.webdriver import Chrome
# Precisa colocar o chromedriver da versao correta dentro de alguma pasta
# que esteja no Path C:\Users\c23x\AppData\Local\Programs\Python\Python310
#from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.common.by import By
#from selenium.webdriver import ChromeOptions
#from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.support import expected_conditions as EC
from requests import request #garantir que esta lib esta atualizada
from json import loads
from bs4 import BeautifulSoup
from threading import Thread as th
import pandas as pd
import numpy as np
import sys #para lidar com os warnings

'''
class Browser(Chrome):
    def __init__(self,options):
        super().__init__(options=options)

    #def get_webpage(self, url
'''     


def get_mk_dict_json(url, headers, data, verify):
    """
    Esta funcao executa um HTTP GET recebendo os parametros enviados e
    transforma a resposta recebida em JSON em um dicionario manipulavel
    """
    return loads(request("GET", url = url, headers = headers,
                                      data = data, verify = verify).text)

def post_mk_dict_json(url, headers, data, verify):
    """
    Esta funcao executa um HTTP POST recebendo os parametros
    enviados e transforma a resposta recebida em JSON em um
    dicionario manipulavel
    """
    return loads(request("POST", url = url, headers = headers,
                                      data = data, verify = verify).text)



if __name__ == '__main__':
    ### Definindo o que fazer com os warnings

    if not sys.warnoptions:
        import warnings
        warnings.simplefilter("ignore")

    
    ### Primeiro vamos utilizar a API REST do GETICWEB para pegar os chamados em aprovacao para mim
    # VPN de acesso a RIC precisa estar conectada para encontrar o GETICWEB
    # Pegar o token para producao
    chave = 'C23X'
    senha = '1qaz@WSX3d'
    response_token_json = post_mk_dict_json("https://geticweb.transpetro.com.br"+
                                            "/api/seguranca/token",
                                            {'Content-Type': 'application/x-www-form-urlencoded'},
                                            "grant_type=password&username="+chave+
                                            "&password="+senha+"&dominio=1", False)

    token = response_token_json['access_token']

    #Pegar os chamados em aprovacao para a minha chave

    response_chmd_aprov_json = get_mk_dict_json("https://geticweb.transpetro.com.br/" +
                                                "api/chamado/EmAprovacao",
                                                {'Authorization': 'Bearer '+token}, {},
                                                False)

    #abre o chrome atraves do selenium para executar as acoes no geticweb uma vez que a
    #API nao ta deixando aprovar por la
    '''

    op = ChromeOptions()
    op.add_argument('headless')
    # = th(target=self.alimentalista)
    driver = Chrome(options=op)
    #driver = th(target=Browser(options=op))
    #driver = Chrome()
    thread_get = th(target=driver.get("https://geticweb.transpetro.com.br")) #url do geticewb

    #autenticacao do geticweb.. pegando os elemntos dos campos de usuario e senha
    elmnt_usuario = driver.find_element(By.ID,"usuario")
    elmnt_senha = driver.find_element(By.ID,"senha")
    elmnt_usuario.send_keys("c23x")
    elmnt_senha.send_keys("1qaz@WSX3d")
    #clicand no botao login
    elmnt_botao_login = driver.find_element(By.ID,'login')
    driver.execute_script("arguments[0].click();", elmnt_botao_login)
    #mostrando os chamados para aprovacao
    '''

    #df_chamados = pd.read_csv('.\chamados_infrati.csv')
    with open('.\chamados_infrati.csv') as file:
        chamados = file.read()

    chamados = chamados.split('\n')
    #print(chamados[len(chamados)-2])
    chamados_sae_gw = []
    #print(len(chamados))
    #print(chamados)
    #while True:
    #print('Estes sao os chamados para sua aprovacao:\n')
    for i in range(1, len(chamados)-1):
        print(chamados[i], i)
        response_chmd_aprov_det_json = get_mk_dict_json("https://geticweb.transpetro"+
                                                        ".com.br/api/chamado/"+chamados[i],
                                                        {'Authorization': 'Bearer '+token},
                                                        {}, False)
        #print(response_chmd_aprov_det_json)
        
        soup = BeautifulSoup(response_chmd_aprov_det_json['descricao'], features="lxml")
        content = str(soup.find_all())
        content = content.lower()
        

        teste1 = content.find('geticweb')
        teste2 = content.find('sae')
        teste3 = content.find('gw')
        teste4 = content.find('ellevo')
        teste5 = content.find('elevo')
        teste6 = content.find('gdt')

        if teste2 or teste3 or teste4 or teste5 or teste6 or teste1:
            chamados_sae_gw.append(chamados[i])
            print(content[teste1-10:teste1+30])
            print(content[teste2-10:teste2+30])
            print(content[teste3-10:teste3+30])
            print(content[teste4-10:teste4+30])
            print(content[teste5-10:teste5+30])
            print(content[teste6-10:teste6+30])
            #print("\n\n")
            #print(content[)


    print(len(chamados_sae_gw))

