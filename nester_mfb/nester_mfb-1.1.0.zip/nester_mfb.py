""" Este es el modulo "nester_mfb.py", ofrece una funcion "print_lol"
    que muestra listas que pueden contener otras listas (o no).
    Version 1.1.0
"""
def print_lol(the_list, level):
    """ El parametro posicional "the_list"
        es un lista de Phyton que puede contener otra sublistas-
        Cada elemento en la lista es (recursivamente) mostrado
        en la pantalla en su propia linea.
	El parametro "level" indica el numero de TAB que se indenta una línea
    """
    for item in the_list:
        if isinstance(item, list):
            print_lol(item, level+1)
        else:
            for num in range(level):
                print("\t", end='')
            print(item)
	    

			
