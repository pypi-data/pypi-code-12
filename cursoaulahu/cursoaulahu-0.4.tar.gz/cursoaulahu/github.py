import json
import requests
import sys
from os import path

diretorio_desse_arquivo = path.dirname(__file__)
diretorio_huaula = path.join(diretorio_desse_arquivo, '..')
diretorio_huaula = path.abspath(diretorio_huaula)
sys.path.append(diretorio_huaula)

from cursoaulahu import dunder_main


def buscar_avatar(nome):
    r = requests.get('https://api.github.com/users/{}'.format(nome))
    dados = json.loads(r.text)
    dunder_main.b
    return dados['avatar_url']

print(buscar_avatar('viollarr'))
