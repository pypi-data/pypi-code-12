import requests


def buscar_avatar(nome_de_usuario):
    r = requests.get('https://api.github.com/users/{}'.format(nome_de_usuario))
    dct = r.json()
    return dct['avatar_url']


if __name__ == '__main__':
    print(buscar_avatar('renzon'))
