import json
import requests
from os import path

diretorio_desse_arquivo = path.dirname(__file__)
diretorio_huaula = path.join(diretorio_desse_arquivo, '..')
diretorio_huaula = path.abspath(diretorio_huaula)
print(diretorio_huaula)

import sys
print('############ ANTES DE ALTERAR O PATH ###############')
print(sys.path)
sys.path.append(diretorio_huaula)
print('############ DEPOIS DE ALTERAR O PATH ###############')
print(sys.path)
from cursoaulahu import dunder_main


def buscar_avatar(nome):
    r = requests.get('https://api.github.com/users/{}'.format(nome))
    dados = json.loads(r.text)
    print(dunder_main)
    dunder_main.b
    return dados['avatar_url']

print(buscar_avatar('viollarr'))
