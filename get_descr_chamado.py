""" Melhorias pendentes:
Alguns textos nao tem o atributo string, de forma quee nao e possivel ver a justificativa
Definir classe navegador
"""

from selenium.webdriver import Chrome
# Precisa colocar o chromedriver da versao correta dentro de alguma pasta
# que esteja no Path
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from requests import request #garantir que esta lib esta atualizada
from json import loads
from bs4 import BeautifulSoup
from threading import Thread as th
import sys #para lidar com os warnings
import tkinter as tk

class Browser(Chrome):
    def __init__(self,options):
        super().__init__(options=options)

    def get_webpage(self, url):
        pass

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

def get_token(url, headers, data, verify):
    """
    Esta funcao pega o token da API para executar as operacoes
    """
    json_token = post_mk_dict_json(url, headers, data, verify)

    return json_token['access_token']

if __name__ == '__main__':

    ### Definindo o que fazer com os warnings
    if not sys.warnoptions:
        import warnings
        warnings.simplefilter("ignore")
    
    ### Primeiro vamos utilizar a API REST do GETICWEB para pegar os chamados em aprovacao para mim
    # VPN de acesso a RIC precisa estar conectada para encontrar o GETICWEB
    # Pegar o token para producao
    chave           = "C23X"
    senha           = "3edc4RFV5t"
    url_token       = "https://geticweb.transpetro.com.br/api/seguranca/token"
    headers_token   = {'Content-Type': 'application/x-www-form-urlencoded'}
    data_token      = "grant_type=password&username="+chave+"&password="+senha+"&dominio=1"
    verify_token    = False

    #executando a funcao que pega o token
    token           = get_token(url_token, headers_token, data_token, verify_token)   

    with open('.\chamados.csv') as file:
        data = file.read()

    chamados = data.split('\n')

    for i in len(chamados)

    response_chmd_aprov_det_json = get_mk_dict_json("https://geticweb.transpetro"+
                                                        ".com.br/api/chamado/"+chmd_to_aprv,
                                                        {'Authorization': 'Bearer '+token},
                                                        {}, False)

    soup = BeautifulSoup(response_chmd_aprov_det_json['descricao'], features="lxml")
    soup = soup.get_text()
    print(soup)