"""Este é o módulo "nester.py", e fornece uma função chamada print_lol() 
que imprime listas que podem ou não incluir listas aninhadas."""

#Esta função requer um argumento posicional chamado "the_list", que é
#qualquer lista Python (de possíveis listas aninhadas). Cada item de dados ná
#lista fornecida é (recursivamente) impresso na tela em sua própria linha."""
def print_lol(the_list):
    for eachItem in the_list:
        if isinstance(eachItem, list):
            print_lol(eachItem)
            return
        print(eachItem)
