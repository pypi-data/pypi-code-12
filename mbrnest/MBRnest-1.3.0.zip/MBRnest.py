
"""Este é o módulo "nester.py", e fornece uma funço chamada print_lol() que imprime lista que podem ou não incluir listas aninhadas"""

def print_lol(the_list, indent=False, level=0):

#Esta função requer um argumento posicional chamado "the_list", que é QUALQUER lista Python(de possíves aninhadas). Cada item de dados na lista fornecida é(recursivamente) impresso na tela em sua própria linha.
#Um segundo argumento chamado "level" é usado para inserir tabulações quando uma lista aninhada é encontrada.

	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol(each_item, indent, level+1)
		else:
                        if indent:
                                print("\t"*level,end='')
                        print(each_item)

			
 


