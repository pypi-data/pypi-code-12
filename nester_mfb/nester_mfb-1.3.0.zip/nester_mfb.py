""" Este es el modulo "nester_mfb.py", ofrece una funcion "print_lol"
    que muestra listas que pueden contener otras listas (o no).
    Version 1.3.0
"""
def print_lol(the_list, indent=False, level=0):
    """-El parametro posicional "the_list"
        es un lista de Phyton que puede contener otra sublistas.
        Cada elemento en la lista es (recursivamente) mostrado
        en la pantalla en su propia linea.
       -El parametro indent indica si se desea que las líneas se indenten
        por defecto la opcion es FALSE (no se indenta ninguna línea).
       -El parametro "level" (opcional) indica el numero de TABs que se indenta una línea
	"level" tiene un valor por defecto de 0.
	
    """
    for item in the_list:
        if isinstance(item, list):
            print_lol(item, indent, level+1)
        else:
            if indent:
                for num in range(level):
                    print("\t", end='')
            print(item)
	    

			
