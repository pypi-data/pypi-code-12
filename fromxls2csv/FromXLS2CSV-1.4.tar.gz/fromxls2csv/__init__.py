#-*- coding: utf8 -*-
from csv import reader, writer
from os import system
from os.path import isfile

import pandas as pd


def convert(entrada, salida=None, include=None, exclude=None, delimiter=None,
    verbose=False, es_cabecera=True):
    # Preguntamos si existe el fichero:
    if not isfile(entrada):
        return 'No existe el fichero %s' %entrada
        exit()

    xls = pd.ExcelFile(entrada)
    sheetlist = xls.sheet_names  # Obtenemos lista con nombres hojas Excel

    ruta_archivo = entrada.split('/')
    indice = len(ruta_archivo) - 1
    archivo = ruta_archivo[indice]

    name = archivo.split(".")[0]
    if not salida is None:
        name = archivo.split(".")[0]

    n = 1

    # Definimos el delimitador:
    if delimiter is None:
        delimiter = ';'

    # Generamos fichero .csv para cada hoja:
    for sheet in sheetlist:
        outfile = "%s-%s.csv" %(name, n)  # Nombre .csv final
        n = n + 1

        try:
            data = xls.parse(sheet)
        except IndexError as e:
            return "El archivo no contiene información para ser procesada"
            exit()

        if not include is None:
            for columna in data.columns:
                if not str(columna).lower() in [n.lower() for n in include]:
                    del data[columna]

        if not exclude is None:
            for columna in data.columns:
                if str(columna).lower() in [n.lower() for n in exclude]:
                    del data[columna]

        column_names = ['X%i' % n for n in range(len(data.columns))]
        fila_cero = "%s%s\n" % (delimiter, delimiter.join(column_names))

        crear_archivo = True
        if isfile(outfile):
            crear_archivo = True

        if crear_archivo:
            modo = 'w'
            if es_cabecera is False:
                with open(outfile, 'w') as archivo:
                    archivo.write(fila_cero)
                modo = 'a'

            data.to_csv(outfile, sep=delimiter, encoding='utf-8',
                header=es_cabecera, mode=modo)
            return "Archivo %s creado con exito" % outfile


