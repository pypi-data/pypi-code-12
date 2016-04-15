"""Este é o modulo "nester.py" (capitulo 1 do livro 'Head First Python').
Fornece uma função chamada print_lol() que imprime listas que podem ou não incluir outras listas aninhadas."""
def print_lol(the_list, indent=False, nivel=0):
    """
    Esta função requer um argumento posicional chamado "The_list", que é qualquer lista Python (de possíveis listas aninhadas).
    Cada item de Dados na lista é (recursivamente) impresso na tela, cada um em sua linha.
    O Segundo argumento quando setado para "True", habilita a identaçao (indent)
    O terceiro argumento (nivel) insere tabs de acordo com o nivel de aninhamento da lista.
    """
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, indent, nivel+1)
        else:
            if indent:
                for tab_stop in range(nivel):
                    print("\t", end='')
                print(each_item)
            else:
                print(each_item)
