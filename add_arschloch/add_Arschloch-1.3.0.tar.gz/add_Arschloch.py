""" Dies ist das Modul "add_Arschloch". Es gibt Listen aus, welche sich in
Listen verbergen. Jeweils ein Objekt pro Zeile. Dabei wird für jedes Listen-Objekt
das Wort "Arschloch" hinzugefügt. Mit dem zweiten Argument "ebene" kann bestimmt
werden, wie weit die nächste Liste jeweils engerückt werden soll."""

tl = ["Andi","Ivi",[666,"Burger","Hamlet",[777,"Schawul","Beni"]]]
tl.append("handtuch")
tl.insert(1,"tu es")

def print_auspack(liste,einzug = False, ebene = 0):
    for teil_liste in liste:
        if isinstance(teil_liste, list):
            print_auspack(teil_liste, einzug, ebene + 2)
            
        else:
            if einzug == True:
                for anzahl in range(ebene):
                    print("\t",end='')
            print(teil_liste,"Arschloch") 
           
        
