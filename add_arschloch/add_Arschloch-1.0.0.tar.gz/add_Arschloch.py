def print_auspack(liste):
    for teil_liste in liste:
        if isinstance(teil_liste, list):
            print_auspack(teil_liste)
        else:
            print(teil_liste)
            print("Arschloch")
        
