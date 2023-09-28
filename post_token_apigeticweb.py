import requests

url = 'https://geticwebh.transpetro.com.br/api/seguranca/token'

payload="grant_type=password&username=c23x&password=billYje1&dominio=transp"
headers = {
  'Content-Type':'application/x-www-form-urlencoded'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
print(response.json())

#nao pode ter o espaco antes do application
#curl -X POST http://geticwebh.transpetro.com.br/api/seguranca/token -H 'Content-Type:application/x-www-form-urlencoded' -d "grant_type=password&username=c23x@transp&password=billYje1"
