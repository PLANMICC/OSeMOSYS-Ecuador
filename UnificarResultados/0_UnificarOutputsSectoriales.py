# -*- coding: utf-8 -*-
import pandas as pd
import os
import numpy as np
#import math
import ast

'Funcion para leer los archivos dentro de un directorio'
def ListaArchivos( Nombre_carpeta ):
    listaArchivos = os.listdir( Nombre_carpeta )
    return listaArchivos

'Funcion para hacer una copia de una lista'
def CopiaLista(lista):
    copia=list()
    for i in lista:
        copia.append(i)
    return copia

'Funcion para hacer un idice para ordenar los Dataframes'
def IndiceOrdeneTabla(lista, nuevo_elemento, indice):
    copia=CopiaLista(lista)
    copia.insert(indice,nuevo_elemento)
    return copia

'Funcion para eliminar repetidos de una lista'
def EliminarRepetidos(lista):
    salida=list()
    for i in range(len(lista)):
        if lista[i] not in salida:
            salida.append(lista[i])
    return salida

'''Funcion para eliminar nans de una lista'''
def EliminarNoStr(lista):
    salida=list()
    for i in range(len(lista)):
        if type(lista[i])==str:
            salida.append(lista[i])
    return salida



'Lista con los anios para filtrar, esto puede cambiar para el escenario que va a 2070'
filtro_anios_Ecuador=[2018,2019,2020,2021,2022,2023,2024,2025,2026,2027,2028,2029,2030,2031,2032,2033,2034,2035,2036,2037,2038,2039,2040,2041,2042,2043,2044,2045,2046,2047,2048,2049,2050,2051,2052,2053,2054,2055,2056,2057,2058,2059,2060,2061,2062,2063,2064,2065,2066,2067,2068,2069,2070]

lista_archivos_Energy=ListaArchivos("0_OutputEnergy")
lista_archivos_AFOLU=ListaArchivos("1_OutputAFOLU")
lista_archivos_PIUP=ListaArchivos("2_OutputPIUP")
lista_archivos_Waste=ListaArchivos("3_OutputWaste")


'En teoria, solo hay 1 archivo de salida por sector en donde están todos los escenarios y estarán todos los futuros'
###########################################################################################################
### ENERGY
###########################################################################################################
df_Energy_output = pd.read_csv("0_OutputEnergy/"+lista_archivos_Energy[0], index_col=None, header=0, low_memory=False)
'Energia tiene mas comulnas que el resto de sectores por lo que vamos a completar el resto con la misma cantidad de columnas'
lista1=list(df_Energy_output.columns)
#print(lista1)
#print(df_Energy_output)
techs_energy=list(df_Energy_output['Technology'])
techs_energy=EliminarRepetidos(techs_energy)
techs_energy=EliminarNoStr(techs_energy)


file = open("Sec_Energy.txt", "r")
contents = file.read()
Sec_Energy = ast.literal_eval(contents)
file.close()


'Se procede a hacer eso para cada sector'
###########################################################################################################
### AFOLU: tiene una copia de PIUP por ahora hasta que JAM pase el csv de resultados
###########################################################################################################
df_AFOLU_output = pd.read_csv("1_OutputAFOLU/"+lista_archivos_AFOLU[0], index_col=None, header=0)
lista2=list(df_AFOLU_output.columns)
#print(lista2)
# for i in range(len(lista1)):
#     if lista1[i] not in lista2:
#         print(lista1[i])
df_AFOLU_output=df_AFOLU_output.assign(DistanceDriven=np.NaN)
df_AFOLU_output=df_AFOLU_output.assign(Fleet=np.NaN)
df_AFOLU_output=df_AFOLU_output.assign(NewFleet=np.NaN)
df_AFOLU_output=df_AFOLU_output.assign(ProducedMobility=np.NaN)
df_AFOLU_output=df_AFOLU_output.assign(FilterFuelType=np.NaN)
df_AFOLU_output=df_AFOLU_output.assign(FilterVehicleType=np.NaN)
df_AFOLU_output=df_AFOLU_output.assign(Capex_GDP=np.NaN)
df_AFOLU_output=df_AFOLU_output.assign(FixedOpex_GDP=np.NaN)
df_AFOLU_output=df_AFOLU_output.assign(VarOpex_GDP=np.NaN)
df_AFOLU_output=df_AFOLU_output.assign(Opex_GDP=np.NaN)
df_AFOLU_output=df_AFOLU_output.assign(Externalities_GDP=np.NaN)
'Se agrega la columna de sector'
df_AFOLU_output=df_AFOLU_output.assign(Sector='AFOLU')
#print(df_AFOLU_output)
techs_AFOLU=list(df_AFOLU_output['Technology'])
techs_AFOLU=EliminarRepetidos(techs_AFOLU)
techs_AFOLU=EliminarNoStr(techs_AFOLU)

file = open("Sec_AFOLU.txt", "r")
contents = file.read()
Sec_AFOLU = ast.literal_eval(contents)
file.close()

###########################################################################################################
### PIUP
###########################################################################################################
df_PIUP_output = pd.read_csv("2_OutputPIUP/"+lista_archivos_PIUP[0], index_col=None, header=0)
lista3=list(df_PIUP_output.columns)
#print(lista3)
# for i in range(len(lista1)):
#     if lista1[i] not in lista3:
#         print(lista1[i])
df_PIUP_output=df_PIUP_output.assign(DistanceDriven=np.NaN)
df_PIUP_output=df_PIUP_output.assign(Fleet=np.NaN)
df_PIUP_output=df_PIUP_output.assign(NewFleet=np.NaN)
df_PIUP_output=df_PIUP_output.assign(ProducedMobility=np.NaN)
df_PIUP_output=df_PIUP_output.assign(FilterFuelType=np.NaN)
df_PIUP_output=df_PIUP_output.assign(FilterVehicleType=np.NaN)
'Se agrega la columna de sector'
df_PIUP_output=df_PIUP_output.assign(Sector='PIUP')
#print(df_PIUP_output)

###########################################################################################################
### Waste
###########################################################################################################
df_Waste_output = pd.read_csv("3_OutputWaste/"+lista_archivos_Waste[0], index_col=None, header=0, low_memory=False)
lista4=list(df_Waste_output.columns)
#print(lista4)
# for i in range(len(lista1)):
#     if lista1[i] not in lista3:
#         print(lista1[i])
df_Waste_output=df_Waste_output.assign(DistanceDriven=np.NaN)
df_Waste_output=df_Waste_output.assign(Fleet=np.NaN)
df_Waste_output=df_Waste_output.assign(NewFleet=np.NaN)
df_Waste_output=df_Waste_output.assign(ProducedMobility=np.NaN)
df_Waste_output=df_Waste_output.assign(FilterFuelType=np.NaN)
df_Waste_output=df_Waste_output.assign(FilterVehicleType=np.NaN)
'Se agrega la columna de sector'
df_Waste_output=df_Waste_output.assign(Sector='Waste')
#print(df_Waste_output)

###########################################################################################################
'Se agrega la columna de sector al Dataframe de Energia'
df_Energy_output=df_Energy_output.assign(Sector='Energy')

'Se ordenan los dataframes con el orden del Datafreme de Energia'
df_Energy_output=df_Energy_output[IndiceOrdeneTabla(lista1, 'Sector', 2)]
df_AFOLU_output=df_AFOLU_output[IndiceOrdeneTabla(lista1, 'Sector', 2)]
df_PIUP_output=df_PIUP_output[IndiceOrdeneTabla(lista1, 'Sector', 2)]
df_Waste_output=df_Waste_output[IndiceOrdeneTabla(lista1, 'Sector', 2)]
# print(df_Energy_output)
# print(df_AFOLU_output)
# print(df_PIUP_output)
# print(df_Waste_output)

###########################################################################################################
'Se reunen los 4 Dataframes'
df_output = df_Energy_output._append(df_AFOLU_output)
df_output = df_output._append(df_PIUP_output)
df_output = df_output._append(df_Waste_output)
### Usamos diferentes nombres para escenarios entonces con esta linea siguiente los ponemos todos iguales
df_output['Strategy'] = df_output['Strategy'].replace(['DDP50'], 'DDP')


#####################################################################
### Usamos los diccionarios para ser más especificos con los sectores
#####################################################################
llaves=list(Sec_AFOLU.keys())
col_sector=np.array(list(df_output['Sector']))
df_output['SecCorr'] = col_sector
for i in range(len(llaves)):
    df_output.loc[df_output['Technology'] == llaves[i], 'SecCorr'] =  Sec_AFOLU[llaves[i]]


llaves=list(Sec_Energy.keys())
for i in range(len(llaves)):
    df_output.loc[df_output['Technology'] == llaves[i], 'SecCorr'] =  Sec_Energy[llaves[i]]
    
    

###########################################################################################################
### Escribir archivo unificado y filtrado por anios
###########################################################################################################
# df_output = pd.concat(Energy_output, axis=0, ignore_index=True)
df_output.sort_values(by=['Sector','Strategy','Future.ID','Fuel','Technology','Year','Emission'], inplace=True)
df_output.to_csv ( '4_OutputUnificado/f0_OSMOSYS_ECU_Output.csv', index = None, header=True)
#print(df_output)
df_filter_year = df_output[df_output['Year'].isin(filtro_anios_Ecuador)]
df_filter_year.to_csv ( '4_OutputUnificado/f0_OSMOSYS_ECU_Output_Filtrado.csv', index = None, header=True)