""" Este eh o modulo nester.py, e fornece uma funcao chamada print_lol() que imprime listas que podem ou nao incluir listas aninhadas """
def print_lol(the_list):
	"esta funcao recursivamente imprime os dados da lista"
	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol(each_item)
		else:
			print(each_item)
