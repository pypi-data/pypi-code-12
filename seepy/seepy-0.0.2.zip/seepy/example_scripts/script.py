#<##Dokumentacja tom I dla zadania 
#<------
#<
'''
###Pkt 1. Obliczenie xxxxxx
The backtick delimiters surrounding a code span may include spaces — one after the opening, one before the closing. This allows you to place literal backtick characters at the beginning or end of a code span

Tu mozesz pisac co checsz

Dodatkowy opis .......


'''
from strupy import units as u

#< *Dane wejsciowe*
h = 4 * u.mm #< Wysokosc
s = 1 * u.m 
s #< szerokosc



A = (h * s).asUnit(u.mm2) #< Wynik

sigma = 250*u.kN/A

sigma = sigma.asUnit(u.MPa) 

sigma #< Naprezenie

#<------
#<
''' 
Tabela Markdown

|strupy . | | | | | | |
|:-------------|:------|:-----|:-----|:-----|:-----|:-----|
| | **concrete .** *(reinforced concrete structure design)*
'''
#<------
#<###Pkt 2. Obliczenie xxxxxx

#< To jest komntarz w jednej lini pierwsza wartosc to %(h)s a druga to %(s)s

#<
''' 
>To jest komantarz wieloliniowy

Wartosci to %(h)s i %(s)s
Use the `printf()` function.

'''
#<kod funkci:

#/code
a = 11
c = 12
i = 34
text = 'text'
for i in text:
    print i
#/


