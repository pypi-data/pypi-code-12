from strupy import units as u

#!
'''
##*Obliczenie zbrojenia w przekroju zginanym prostokatnym*

>*(metoda maksymalnie uproszczona)*
'''

#! ###1.Wymiary przekroju
h = 1200 * u.mm #! - wysokosc przekoju
b = 800 * u.m #! - szerokosc przekroju

#! ###2.Obciazenie
Msd = 300 * u.kNm #! - moment obliczeniowy

#! ###3.Material
fyd = 450 * u.MPa #! - stal zbrojeniowa

#! ---

#%img PrzekZginany_fig_1.png

#! Ze wzoru:

#%code
As1 = Msd / (0.8 * h) * 1 / fyd
#%

#! otrzymujemy wynik:

As1 = As1.asUnit(u.cm2) 
As1 #! - potrzebna powierzchnia zbrojenia

#!
'''
---
###Podsumowanie
Dla przekroju o wymiarach %(b)s x %(h)s (bxh) i obciazeniniu %(Msd)s 
potrzebne zbrojenie dolem %(As1)s
'''



