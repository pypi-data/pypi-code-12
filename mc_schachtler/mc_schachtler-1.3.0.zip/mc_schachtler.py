"""Mein erstes Modul! Es stellt eine Funktion namens print_lvl bereit,die eine
Liste mit beliebig vielen eingebetteten Listen ausgibt."""
def print_lvl(liste,einzug=False,ebene=0):
        """Zeigt den Inhalt einer Liste inkl. evtl. eingebetteter Listen an.
        Der zweite Parameter erzeugt Tabulatoren bei der Ausgabe."""
        for element in liste:
                if isinstance(element,list):
                        print_lvl(element, einzug, ebene+1)
                else:
                        if einzug: # wenn Einzug = True
                                for tab in range(ebene):
                                        print("\t",end='')
                        print(element)
