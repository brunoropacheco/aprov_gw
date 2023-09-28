from requests import request
from json import loads
from json import dumps
from bs4 import BeautifulSoup
import sys
import pymsteams

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
    # Pegar o token para producao
    response_token_json = post_mk_dict_json("https://geticweb.transpetro.com.br/"+
                                            "api/seguranca/token",{'Content-Type': 'applic'+
                                                                   'ation/x-www-form-'+
                                                                   'urlencoded'},
                                            "grant_type=password&username=C23X&password="+
                                            "1qaz@WSX3d&dominio=1", False)

    token = response_token_json['access_token']
    chmd = str(sys.argv[1]) #Recebe o numero do chamado pelo parametro
    #colocado na chamada do codigo pelo triggercmd
    response_chmd_aprov_det_json = get_mk_dict_json("https://geticweb.transpetro"+
                                                    ".com.br/api/chamado/"+chmd,
                                                    {'Authorization': 'Bearer '+token},
                                                    {}, False)
    qtde_tramites = int(response_chmd_aprov_det_json['quantidadeTramites'])
    soup = BeautifulSoup(response_chmd_aprov_det_json['descricao'], features="lxml")
    tmp = soup.find_all('font')
    text_resposta=""
    for val in tmp:        
        if str(val.contents)!=("[' : ']"):
            text_resposta=text_resposta+str(val.contents)+"\n"

    for tramite in range(1,qtde_tramites+1):
        resp_tramite = get_mk_dict_json("https://geticweb.transpetro"+
                                        ".com.br/api/mob/tramite/chamado/"+chmd+
                                        "/tramite/"+str(tramite),
                                        {'Authorization': 'Bearer '+token},
                                        {}, False)
        text_resposta = (text_resposta+"\n\n"+resp_tramite['usuarioNome']+
                         " - "+resp_tramite['data']+" - "+resp_tramite['descricao'])
    myTeamsMessage = pymsteams.connectorcard("https://transpetro.webhook"+
                                         ".office.com/webhookb2/9ac90db3-2e"+
                                         "dc-4118-b40a-177641c56c34@46f6a78"+
                                         "0-86e1-4570-9459-bb97b7d99f9d/In"+
                                         "comingWebhook/f99ee4c2acdf4a0090"+
                                         "789bc15a72e290/a5a63968-60c2-4696"+
                                         "-a73b-d2e8c6d6f0db")
    myTeamsMessage.text(text_resposta)
    myTeamsMessage.send()
