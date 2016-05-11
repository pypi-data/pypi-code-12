# -*- coding: utf-8 -*-
from .validacao import valida_cpf, valida_cnpj, valida_cpf_cnpj

__author__ = 'rodrigo'


def test_valida_cpf():
    tests = []
    tests.append(['38449278597', True])
    tests.append(['473.523.334-28', True])
    tests.append(['319.627.714-31', True])
    tests.append(['290.744.619-30', True])
    tests.append(['84121280288', True])
    tests.append(['535.347.740-51', True])
    #Todos os cpfs abaixo são inválidos
    tests.append(['535.347.740-52', False])
    tests.append(['64110936735', False])
    tests.append(['18535865168', False])
    tests.append(['313830366839', False])
    tests.append(['4876777752', False])
    tests.append(['00000000000', False])
    tests.append(['11111111111', False])
    tests.append(['22222222222', False])
    tests.append(['33333333333', False])
    tests.append(['44444444444', False])
    tests.append(['55555555555', False])
    tests.append(['66666666666', False])
    tests.append(['77777777777', False])
    tests.append(['88888888888', False])
    tests.append(['99999999999', False])
    tests.append(['73551826849', False])
    tests.append(['26847233696 ', False])
    tests.append([' ', False])
    tests.append(['           ', False])

    for cpf in tests:
        assert valida_cpf(cpf[0]) == cpf[1]
        
def test_valida_cnpj():

    tests = []
    tests.append(['25378864000172 ', False])
    tests.append(['67.312.201/0001-03', True])
    tests.append(['11.444.777/0001-61', True])
    tests.append(['86.452.146/0001-93', True])
    tests.append(['22.347.342/0001-15', True])
    tests.append(['98011495000159', True])
    tests.append(['63258135000171', True])
    tests.append(['41088284000105', True])
    tests.append(['10276193000161', True])
    tests.append(['10.276.193/0001-61', True])
    tests.append(['15.045.096/0001-81', True])

    #Todos os cnpjs abaixo são inválidos
    tests.append(['24.237.510/0001-46', False])
    tests.append(['77.780.552/0001-10', False])
    tests.append(['44.152.617/0001-26', False])
    tests.append(['86.866.620/0001-20', False])
    tests.append(['71.662.874/0002-52', False])
    tests.append(['38370784010112', False])
    tests.append(['12980192000193', False])
    tests.append(['75550581000135', False])
    tests.append(['00000000000000', False])
    tests.append(['11111111111111', False])
    tests.append(['22222222222222', False])
    tests.append(['33333333333333', False])
    tests.append(['44444444444444', False])
    tests.append(['55555555555555', False])
    tests.append(['66666666666666', False])
    tests.append(['77777777777777', False])
    tests.append(['88888888888888', False])
    tests.append(['99999999999999', False])
    tests.append(['3837078401011', False])

    tests.append([' ', False])
    tests.append(['           ', False])

    for cnpj in tests:
        assert valida_cnpj(cnpj[0]) == cnpj[1]
