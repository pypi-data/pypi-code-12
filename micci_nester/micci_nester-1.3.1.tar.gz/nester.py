"""Este é o módulo "nester.py", e fornece a função chamada print_lol() que imprime listas que podem ou não incluir
listas aninhadas"""
def print_lol(the_list, ident=False, level=0):
    """esta função requer um argumento posicional chamado "the_list", que é qualquer lista Python. Cada item da lista
    é recursivamente impressa na tela"""
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, level+1)
        else:
            if ident:
                for tab_stop in range(level):
                    print("\t", end='')
            print(each_item)

