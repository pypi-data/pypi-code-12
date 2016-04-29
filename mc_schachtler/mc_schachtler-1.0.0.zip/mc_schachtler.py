"""Mein erstes Modul!"""
def print_lvl(liste):
	"""Zeigt den Inhalt einer Liste inkl. evtl. eingebetteter Listen an"""
	for element in liste:
		if isinstance(element,list):
			print_lvl(element)
		else:
			print(element)