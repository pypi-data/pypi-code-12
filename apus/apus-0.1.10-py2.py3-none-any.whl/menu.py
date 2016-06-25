# -*- coding:utf-8 -*-
from .users.models import Users, session


def general(command):
    """
    Hello!
    """

    if command == 'create':
        print("Criar novo usuário")
        username = input('username: ')
        email = input('email: ')
        user = Users(username=username, email=email)
        user.save()

    elif command == 'listall':
        print("Listagem de usuários: ")
        usu = session.query(Users)
        for i, u in enumerate(usu.all()):
            print(i, u)
        pass

