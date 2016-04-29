"""Dies ist das Modul "schachtler.py". Es stellt eine Funktion namens print_lvl()
bereit, die eine Liste mit beliebig viel eingebetten Listen ausgibt."""

def print_lvl(liste,einzug=False,ebene=0):
    """Die Funktion erwartet ein positionelles Argument namens "liste" das eine
    beliegige Python-Liste (mit eventuell eingebetten Listen) ist. Jedes Element
    der Liste wird (rekursiv) auf dem Bildschirm jeweils in einer eigenen Zeile
    ausgegeben.
    Wird das zweite optionale Argument "einzug" True, so werden eingebette Listen
    eingrückt dargestellt.
    Mit dem dritte optinonalen Argument "ebene" wird die Anzahl die Einrücktiefe
    der ersten Ebene eingestellt.
    """
    
    for element in liste:
        if (isinstance(element,list)):
            print_lvl(element,einzug,ebene+1)
        else:
            if einzug == True:
                for einrücken in range(ebene):
                    print("\t",end="")
            print(element)
            
