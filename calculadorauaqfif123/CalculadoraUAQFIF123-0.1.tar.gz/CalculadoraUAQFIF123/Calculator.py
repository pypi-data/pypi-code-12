class Calculator ():

    def __init__(self):
        print ("Iniciando Calculadora")

    def multiplicacion(self, x, y):##Falta el self si no, no funciona
        res = (x * y)
        print ("Tu resultado es: " + str(res))

    def division(self, x, y):
        res = (x / y)
        print ("Tu resultado es: " + str(res))

    def suma(self, x, y):
        res = (x + y)
        print ("Tu resultado es: " + str(res))

    def resta(self, x, y):
        res = (x - y)
        print ("Tu resultado es: " + str(res))

