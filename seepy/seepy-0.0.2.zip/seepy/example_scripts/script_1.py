from strupy import units as u

#<## Dokumentacja projektowa dlazadania dsasas asas

#<
'''
To jest komentarz

kjljl sdsad
'''

#<------

#<
'''
###*Pkt 1. Zalozenia*
Obliczenia wykonane xxxxxxxxxxxxxxx, xxxxxxx
xxxxxxx xxx xxxxxxx
'''

#<
'''
### Rozdzial 2

Obliczeuasa 
'''


#< ###Pkt 2. Obliczenia

#< Wymiary przekroju:
h = 600 * u.mm #< wysokosc przekoju fgggfn
b = 800 * u.m #< szerokosc przekroju
f = 40 * u.Nm #< cos tam

#< Obciozenie:
Msd = 300 * u.kNm #< moment obliczeniowy

#< Material: 
fyd = 450 * u.MPa #< Stal zbrojeniowa

#< Ze wzoru:
#/code
As = Msd / (0.8 * h) * 1 / fyd
#/

#< jest

As = As.asUnit(u.cm2) 
As #< Wynik - zbrojenie

#<
''' 
###Pkt 2. Podsumowanie

Dla przekroju o wymiarach %(b)s x %(h)s (bxh) i obciozeniniu %(Msd)s 
potrzebne zbrojenie dolem %(As)s
asas asa asas
Dla przekroju o wymiarach %(b)s x %(h)s (bxh) i obciozeniniu %(Msd)s 
potrzebne zbrojenie dolem %(As)s

'''



