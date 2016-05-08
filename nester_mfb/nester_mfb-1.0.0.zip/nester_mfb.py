""" Este es el modulo "nester_mfb.py", ofrece una funcion "print_lol"
    que muestra listas que pueden contener otras listas (o no)
"""
def print_lol(the_list):
	""" Esta funcion tiene un parametro posicional "the_list"
            que es un lista de Phyton que puede contener otra sublistas-
            Cada elemento en la lista es (recursivamente) mostrado
	    en la pantalla en su propia linea.
	"""
	for item in the_list:
		if isinstance(item, list):
			print_lol(item)
		else:
			print(item)
