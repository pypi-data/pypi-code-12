"""Este é o módulo "nester.py", e fornece a função chamada print_lol() que imprime listas que podem ou não incluir
listas aninhadas"""
def print_lol(the_list):
    """esta função requer um argumento posicional chamado "the_list", que é qualquer lista Python. Cada item da lista
    é recursivamente impressa na tela"""
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item)
        else:
            print(each_item)

