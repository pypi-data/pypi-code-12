"""Este é o modulo "nester.py" (capitulo 1 do livro 'Head First Python').
Fornece uma função chamada print_lol() que imprime listas que podem ou não incluir outras listas aninhadas."""
def print_lol(the_list):
    """
    Esta função requer um argumento posicional chamado "The_list", que é qualquer lista Python (de possíveis listas aninhadas).
    Cada item de Dados na lista é (recursivamente) impresso na tela, cada um em sua linha.
    """
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item)
        else:
            print(each_item)
