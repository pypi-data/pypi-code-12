# -*- coding:utf-8 -*-
from apus.users.models import Users
from apus.config.db import save_in_db, query


def create_user():
    print("Criar novo usuário")

    username = input('username: ')
    email = input('email: ')
    user = Users(username=username, email=email)
    save_in_db(user)


def list_users():
    print("Listagem de usuários: ")

    usu = query(Users)
    for i, u in enumerate(usu.all()):
        print(i, u)
