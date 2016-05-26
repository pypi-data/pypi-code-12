""" Este eh o modulo nester.py, e fornece uma funcao chamada print_lol() que imprime listas que podem ou nao incluir listas aninhadas """
def print_lol(the_list, indent=False, level=0):
	"esta funcao recursivamente imprime os dados da lista"
	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol(each_item, indent, level+1)
		else:
			if indent:
				for tab_stop in range(level):
					print("\t", end='')
			print(each_item)
