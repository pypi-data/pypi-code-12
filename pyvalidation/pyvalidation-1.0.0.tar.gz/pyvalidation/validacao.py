# -*- coding: utf-8 -*-
import re

__author__ = 'Rodrigo Rodrigues'


def valida_cpf_cnpj(cpf_cnpj):
    if not valida_cpf(cpf_cnpj) and not valida_cnpj(cpf_cnpj):
        return False
    return True


def valida_cpf(cpf):
    def calcula_primeiro_digito(cpf):
        soma = int(cpf[0]) * 10 + \
               int(cpf[1]) * 9 + \
               int(cpf[2]) * 8 + \
               int(cpf[3]) * 7 + \
               int(cpf[4]) * 6 + \
               int(cpf[5]) * 5 + \
               int(cpf[6]) * 4 + \
               int(cpf[7]) * 3 + \
               int(cpf[8]) * 2

        soma_resto = soma % 11
        if (soma_resto < 2):
            return 0
        else:
            return 11 - soma_resto

    def calcula_segundo_digito(cpf, primeiro_digito):
        soma = int(cpf[0]) * 11 + \
               int(cpf[1]) * 10 + \
               int(cpf[2]) * 9 + \
               int(cpf[3]) * 8 + \
               int(cpf[4]) * 7 + \
               int(cpf[5]) * 6 + \
               int(cpf[6]) * 5 + \
               int(cpf[7]) * 4 + \
               int(cpf[8]) * 3 + \
               (primeiro_digito * 2)

        soma_resto = soma % 11
        if (soma_resto < 2):
            return 0
        else:
            return 11 - soma_resto

    # Verifique também se está no formato no CPF,caso contrário retorna falso
    # Verifique se tem 11 caracteres e se são números de 0 a 9, caso contrário retorne falso
    if re.match(r'^\d{3}.\d{3}.\d{3}-\d{2}$', cpf) == None and re.match(r'^\d{11}$', cpf) == None:
        return False

    # Extrai somente os números de uma string
    cpf = ''.join(re.findall(r'\d', cpf))

    # Verifique se possui os 11 dígitos iguais, pois esse padrão passa na validação do dígito verificador
    if re.match(r'^0{11}|1{11}|2{11}|3{11}|4{11}|5{11}|6{11}|7{11}|8{11}|9{11}$', cpf) != None:
        return False

    # calcula os dígitos verificadores
    digito1 = calcula_primeiro_digito(cpf)
    digito2 = calcula_segundo_digito(cpf, digito1)

    # verifica se os dígitos batem
    if int(cpf[-2]) != digito1:
        return False

    if int(cpf[-1]) != digito2:
        return False

    return True


def valida_cnpj(cnpj):
    def calcula_primeiro_digito(cnpj):
        soma = int(cnpj[0]) * 5 + \
               int(cnpj[1]) * 4 + \
               int(cnpj[2]) * 3 + \
               int(cnpj[3]) * 2 + \
               int(cnpj[4]) * 9 + \
               int(cnpj[5]) * 8 + \
               int(cnpj[6]) * 7 + \
               int(cnpj[7]) * 6 + \
               int(cnpj[8]) * 5 + \
               int(cnpj[9]) * 4 + \
               int(cnpj[10]) * 3 + \
               int(cnpj[11]) * 2

        soma_resto = soma % 11
        if (soma_resto < 2):
            return 0
        else:
            return 11 - soma_resto

    def calcula_segundo_digito(cnpj, primeiro_digito):
        soma = int(cnpj[0]) * 6 + \
               int(cnpj[1]) * 5 + \
               int(cnpj[2]) * 4 + \
               int(cnpj[3]) * 3 + \
               int(cnpj[4]) * 2 + \
               int(cnpj[5]) * 9 + \
               int(cnpj[6]) * 8 + \
               int(cnpj[7]) * 7 + \
               int(cnpj[8]) * 6 + \
               int(cnpj[9]) * 5 + \
               int(cnpj[10]) * 4 + \
               int(cnpj[11]) * 3 + \
               (primeiro_digito * 2)

        soma_resto = soma % 11
        if (soma_resto < 2):
            return 0
        else:
            return 11 - soma_resto

    # Verifique também se está no formato no CNPJ,caso contrário retorna falso
    # Verifique se tem 14 caracteres e se são números de 0 a 9, caso contrário retorne falso
    if re.match(r'^\d{2}.\d{3}.\d{3}/\d{4}-\d{2}$', cnpj) == None and re.match(r'^\d{14}$', cnpj) == None:
        return False


    # Extrai somente os números de uma string
    cnpj = ''.join(re.findall(r'\d', cnpj))

    # Verifique se possui os 14 dígitos iguais, pois esse padrão passa na validação do dígito verificador
    if re.match(r'^0{14}|1{14}|2{14}|3{14}|4{14}|5{14}|6{14}|7{14}|8{14}|9{14}$', cnpj) != None:
        return False


    # calcula os dígitos verificadores
    digito1 = calcula_primeiro_digito(cnpj)
    digito2 = calcula_segundo_digito(cnpj, digito1)

    # verifica se os dígitos batem
    if int(cnpj[-2]) != digito1:
        return False

    if int(cnpj[-1]) != digito2:
        return False

    return True
