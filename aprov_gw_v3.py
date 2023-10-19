from selenium.webdriver import Chrome
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
from tkinter import ttk
from datetime import time

'''
aprov_gw_v3.py
Bruno Rodrigues Pacheco
07/01/2023

Esta versao esta fazendo o seguinte:
    - usa a API do geticweb para pegar os chamados em aprovacao (numero e titulo)
    - usa o arquivo "C:/Users/c23x/OneDrive - TRANSPETRO/Documentos - OneDrive/SERVTIC/Automatizacoes/txt_aprov.txt"
        para pegar as justificativas de aprovacoes ou reprovacoes
    - usa o tkinter para mostrar as inforamcoes acima usando labels, botoes e comboboxes
    - usa o selenium para navegar no geticweb e aprovar/reprovar os chamados listados na primeira acao
        - o selenium precisa da aplicacao chromedriver.exe colocado em alguma pasta do path
        - no nosso caso esta no C:/Users/c23x/AppData/Local/Programs/Python/Python310
        - atualmente estamos usando a versao 108 do chrome e baixamos o chromedriver 
        - em https://chromedriver.storage.googleapis.com/index.html?path=108.0.5359.71/
'''

def init_graph_int():
    root = tk.Tk()
    img = tk.PhotoImage(file = r'.\br_logo.png')
    root.call('wm', 'iconphoto', root._w, img)    
    obj_principal = AprovGW(root)    
    root.protocol('WM_DELETE_WINDOW', obj_principal.destroi_janela)
    root.mainloop()
       

class AprovGW:
    def __init__(self, top=None):    
        self.top = top
        self.top.title("Aprovacoes GETICWEB") # titulo da janela top level
        #self.mainframe      = ttk.Frame(self.top)
        #self.mainframe.place()

        ### Primeiro vamos utilizar a API REST do GETICWEB para pegar os chamados em aprovacao para mim
        # VPN de acesso a RIC precisa estar conectada para encontrar o GETICWEB
        # Pegar o token para producao
        self.chave           = "C23X"
        self.senha           = "3edc4RFV69"
        self.url_token       = "https://geticweb.transpetro.com.br/api/seguranca/token"
        self.headers_token   = {'Content-Type': 'application/x-www-form-urlencoded'}
        self.data_token      = "grant_type=password&username="+self.chave+"&password="+self.senha+"&dominio=1"
        self.verify_token    = False

        #executando a funcao que pega o token
        self.token           = self.get_token(self.url_token, self.headers_token, self.data_token, self.verify_token)   

        #Pegar os chamados em aprovacao para a minha chave
        self.url_chm_aprov   = "https://geticweb.transpetro.com.br/api/chamado/EmAprovacao"
        self.hdrs_chm_aprov  = {'Authorization': 'Bearer '+self.token}
        self.data_chm_aprov  = {}
        self.vrfy_chm_aprov  = False

        self.chmd_aprv_json  = self.get_mk_dict_json(self.url_chm_aprov, self.hdrs_chm_aprov, self.data_chm_aprov, self.vrfy_chm_aprov)
        self.tit_gw = ttk.Label(self.top, text='GETICWEB', font=('Arial', 16, 'bold'))
        self.tit_gw.grid(row=0, columnspan=5)
        #print(self.chmd_aprv_json)
        self.descr_chmd()
        self.prnt_chmd(self.chmd_aprv_json)    
        self.bol_conn_sln = self.conn_sln()   

    def descr_chmd(self):
        for i in range(len(self.chmd_aprv_json)):
            self.chmd_aprv_json[i]['descricao'] = self.get_mk_dict_json("https://geticweb.transpetro"+
                                                        ".com.br/api/chamado/"+str(self.chmd_aprv_json[i]['chamadoId']),
                                                        {'Authorization': 'Bearer '+self.token},
                                                        {}, False)['descricao']
            self.chmd_aprv_json[i]['descricao'] = BeautifulSoup(self.chmd_aprv_json[i]['descricao'], features="lxml")
            self.chmd_aprv_json[i]['descricao'] = self.chmd_aprv_json[i]['descricao'].get_text()
            #print(self.chmd_aprv_json[i]['descricao'])

    def prnt_chmd(self, chmd_aprov_json):
        self.qtde_chmd = len(chmd_aprov_json)
        self.btns_aprv = {}
        self.btns_reprv = {}
        self.curr_var = {}
        self.combobox = {}
        with open(".\\aprov.txt") as self.file:
            self.linhas = self.file.read().split('\n')
    
        for i in range(self.qtde_chmd):
            linha = 2*i+1
            self.id = tk.Label(self.top, width=10, fg='blue', font=('Arial',10,'bold'), text=chmd_aprov_json[i]['chamadoId'])                                        
            self.id.grid(row=linha, column=0)
            self.titulo = tk.Label(self.top, width=100, fg='blue', font=('Arial',10,'bold'), text=chmd_aprov_json[i]['titulo'])
            self.titulo.grid(row=linha, column=1)
            self.descr = tk.Label(self.top, text=chmd_aprov_json[i]['descricao'], wraplength=1500)
            self.descr.grid(row=linha+1, columnspan=5)
            self.curr_var[i] = tk.StringVar()
            self.combobox[i] = ttk.Combobox(self.top, textvariable=self.curr_var[i], width=70)
            self.combobox[i]['values'] = self.linhas
            self.combobox[i]['state'] = 'readonly'
            self.combobox[i].grid(row=linha, column=2)
            self.btns_aprv[i] = tk.Button(self.top, text= 'Aprovar', command= lambda i=i: self.aprovar(chmd_aprov_json[i]['chamadoId'], 
                                                                                        self.curr_var[i].get()))
            #precisa de i=i para que nao seja sempre o ultimo botao a ser referenciado            
            self.btns_aprv[i].grid(row=linha, column=3)            
            self.btns_reprv[i] = tk.Button(self.top, text= 'Reprovar', command= lambda i=i: self.reprovar(chmd_aprov_json[i]['chamadoId'], 
                                                                                        self.curr_var[i].get()))
            self.btns_reprv[i].grid(row=linha, column=4)       

    def conn_sln(self):
        #abre o chrome atraves do selenium para executar as acoes no geticweb uma vez que a
        #API nao ta deixando aprovar por la
        self.op              = ChromeOptions()
        self.op.add_argument('headless')
        # = th(target=self.alimentalista)
        self.driver          = Chrome(options=self.op)
        #driver = th(target=Browser(options=op))
        #driver = Chrome()
        self.url_gw          = "https://geticweb.transpetro.com.br"
        #self.thread_get      = th(target=self.driver.get(self.url_gw)) #url do geticewb
        self.driver.get(self.url_gw)

        #autenticacao do geticweb.. pegando os elemntos dos campos de usuario e senha
        self.elmnt_usr       = self.driver.find_element(By.ID,"usuario")
        self.elmnt_pswd      = self.driver.find_element(By.ID,"senha")
        self.elmnt_usr.send_keys(self.chave)
        self.elmnt_pswd.send_keys(self.senha)

        #clicand no botao login
        self.elmnt_btn_log   = self.driver.find_element(By.ID,'login')
        self.driver.execute_script("arguments[0].click();", self.elmnt_btn_log)

        return True

    def aprovar(self, chamado, motivo):        
        self.urlchmd = ("https://geticweb.transpetro.com.br/indexAtendente"
                   +".html#/main/paginaurl/Historico.asp/Sol=" + str(chamado))
        self.driver.get(self.urlchmd) #sempre precisa dar o get para pegar novamente a pagina
        self.frame_teste = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,'[id*=iframeTeste]')))
        self.driver.switch_to.frame(self.frame_teste)
        self.frame_sol = self.driver.find_element(By.CSS_SELECTOR,'[id*=solicitacao]')
        self.driver.switch_to.frame(self.frame_sol)
        self.elmnt_btaprov = self.driver.find_element(By.ID,'btAprovacao') #so pra lembrar..
        #precisa entrar no primeiro frame e depois ir pro segundo pra achar o elemento
        self.driver.execute_script("arguments[0].click();", self.elmnt_btaprov)
        #aqui precisa voltar ao frame anterior DICA: Sempre verificar se ta
        #no contexto (frame) correto
        self.driver.switch_to.parent_frame()
        self.elmnt_cmp_just_aprov = self.driver.find_element(By.ID,"ext-gen15")
        self.elmnt_cmp_just_aprov.send_keys(motivo)
        self.elmnt_button_confirm = self.driver.find_element(By.ID,"ext-gen35")
        self.driver.execute_script("arguments[0].click();", self.elmnt_button_confirm) #ou aprovar so usar o botao correto

    def reprovar(self, chamado, motivo):        
        self.urlchmd = ("https://geticweb.transpetro.com.br/indexAtendente"
                   +".html#/main/paginaurl/Historico.asp/Sol=" + str(chamado))
        self.driver.get(self.urlchmd) #sempre precisa dar o get para pegar novamente a pagina
        self.frame_teste = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,'[id*=iframeTeste]')))
        self.driver.switch_to.frame(self.frame_teste)
        self.frame_sol = self.driver.find_element(By.CSS_SELECTOR,'[id*=solicitacao]')
        self.driver.switch_to.frame(self.frame_sol)
        self.elmnt_btaprov = self.driver.find_element(By.ID,'btAprovacao') #so pra lembrar..
        #precisa entrar no primeiro frame e depois ir pro segundo pra achar o elemento
        self.driver.execute_script("arguments[0].click();", self.elmnt_btaprov)
        #aqui precisa voltar ao frame anterior DICA: Sempre verificar se ta
        #no contexto (frame) correto
        self.driver.switch_to.parent_frame()
        self.elmnt_cmp_just_aprov = self.driver.find_element(By.ID,"ext-gen15")
        self.elmnt_cmp_just_aprov.send_keys(motivo)
        self.elmnt_reprv = self.driver.find_element(By.ID,"ext-comp-1006")
        self.driver.execute_script("arguments[0].click();", self.elmnt_reprv)        
        self.elmnt_button_confirm = self.driver.find_element(By.ID,"ext-gen35")
        self.driver.execute_script("arguments[0].click();", self.elmnt_button_confirm) #ou aprovar so usar o botao correto

    def get_token(self, url, headers, data, verify):
        """
        Esta funcao pega o token da API para executar as operacoes
        """
        self.json_token = self.post_mk_dict_json(url, headers, data, verify)
        return self.json_token['access_token']
    
    def destroi_janela(self):
        self.top.destroy()
        self.driver.quit()

    def get_mk_dict_json(self, url, headers, data, verify):
        """
        Esta funcao executa um HTTP GET recebendo os parametros enviados e
        transforma a resposta recebida em JSON em um dicionario manipulavel
        """
        return loads(request("GET", url = url, headers = headers, data = data, verify = verify).text)

    def post_mk_dict_json(self, url, headers, data, verify):
        """
        Esta funcao executa um HTTP POST recebendo os parametros
        enviados e transforma a resposta recebida em JSON em um
        dicionario manipulavel
        """
        return loads(request("POST", url = url, headers = headers, data = data, verify = verify).text)

if __name__ == '__main__':
    ### Definindo o que fazer com os warnings
    if not sys.warnoptions:
        import warnings
        warnings.simplefilter("ignore")
        
    init_graph_int()