"""Este é o módulo "nester.py", e fornece uma função chamada print_lol() 
que imprime listas que podem ou não incluir listas aninhadas."""

#Esta função requer um argumento posicional chamado "the_list", que é
#qualquer lista Python (de possíveis listas aninhadas). Cada item de dados ná
#lista fornecida é (recursivamente) impresso na tela em sua própria linha.
#Um segundo argumento chamado "level" é usado para inserir tabulações quando
#uma lista aninhada é encontrada.
def print_lol(the_list, level):
    for eachItem in the_list:
        if isinstance(eachItem, list):
            print_lol(eachItem, level+1)
            return
        for tab in range(level):
            print("\t", end='')
        print(eachItem)
