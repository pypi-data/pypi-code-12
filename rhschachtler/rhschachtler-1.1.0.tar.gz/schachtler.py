"""Dies ist das Modul "schachtler.py". Es stellt eine Funktion namens print_lvl()
bereit, die eine Liste mit beliebig viel eingebetten Listen ausgibt."""

def print_lvl(liste,ebene):
    """Die Funktion erwartet ein positionelles Argument namens "liste" das eine
    beliegige Python-Liste (mit eventuell eingebetten Listen) ist. Jedes Element
    der Liste wird (rekursiv) auf dem Bildschirm jeweils in einer eigenen Zeile
    ausgegeben.
    Mit dem zweiten Argument "ebene" können bei eingebettene Listen Tabulatoren
    eingesetzt werden.
    """
    
    for element in liste:
        if (isinstance(element,list)):
            print_lvl(element,ebene+1)
        else:
            for einrücken in range(ebene):
                print("\t",end="")
            print(element)
            
