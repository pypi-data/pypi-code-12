"""Este é o módulo "nester.py" que fornece uma funcao chamada print_lol()
    que imprime listas que podem ou nao incluir listas aninhadas. """
def print_lol(the_list):
    """Esta funcao requere um argumento posicional chamado the_list que é
        qualquer lista Python (de possíveis listas aninhadas). Cada item de
        dados na lista fornecida é recursivamente impresso na tela em sua
        própria linha. """
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item)
        else:
            print(each_item)
