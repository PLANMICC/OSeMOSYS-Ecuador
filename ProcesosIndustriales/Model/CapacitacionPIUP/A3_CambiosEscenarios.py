import Auxiliares as AUX
import pandas as pd

libro=AUX.LeerExcel("CambiosEscenarios.xlsx")
listaHojas=AUX.ListaHojas(libro)

# Hoja del InputActivityRatio

hoja1=AUX.LeerHoja2(libro, listaHojas[0], 0)
encab=AUX.LeerHeaders(hoja1)
years=AUX.LeerCol(hoja1, encab[0])
for i in range(1,len(encab)):
     df_Energy_output = pd.read_csv("A2_Output_Params/"+encab[i].split(";")[2]+"/InputActivityRatio.csv", index_col=None, header=0, low_memory=False)
     lista1=list(df_Energy_output.columns)
     col=AUX.LeerCol(hoja1,encab[i])
     dic=dict(zip(years,col))
     for j in range(len(df_Energy_output)):
         if df_Energy_output["TECHNOLOGY"][j]==encab[i].split(";")[0] and df_Energy_output["FUEL"][j]==encab[i].split(";")[1]:
             df_Energy_output["Value"][j]=dic[df_Energy_output["YEAR"][j]]
    
     df_Energy_output.to_csv("A2_Output_Params/"+encab[i].split(";")[2]+"/InputActivityRatio.csv", index = None, header=True)
     
# Hoja del Variable Cost

hoja1=AUX.LeerHoja2(libro, listaHojas[1], 0)
encab=AUX.LeerHeaders(hoja1)
years=AUX.LeerCol(hoja1, encab[0])
for i in range(1,len(encab)):
     df_Energy_output = pd.read_csv("A2_Output_Params/"+encab[i].split(";")[1]+"/VariableCost.csv", index_col=None, header=0, low_memory=False)
     lista1=list(df_Energy_output.columns)
     #print(lista1)
     col=AUX.LeerCol(hoja1,encab[i])
     dic=dict(zip(years,col))
     for j in range(len(df_Energy_output)):
         if df_Energy_output["TECHNOLOGY"][j]==encab[i].split(";")[0]:
             df_Energy_output["Value"][j]=dic[df_Energy_output["YEAR"][j]]
    
     df_Energy_output.to_csv("A2_Output_Params/"+encab[i].split(";")[1]+"/VariableCost.csv", index = None, header=True)
     
     
# Hoja del EmissionsPenalty

hoja1=AUX.LeerHoja2(libro, listaHojas[2], 0)
encab=AUX.LeerHeaders(hoja1)
years=AUX.LeerCol(hoja1, encab[0])
for i in range(1,len(encab)):
    df_Energy_output = pd.read_csv("A2_Output_Params/"+encab[i].split(";")[1]+"/EmissionsPenalty.csv", index_col=None, header=0, low_memory=False)
    
    lista1=list(df_Energy_output.columns)
    # print(lista1)
    # print(len(df_Energy_output))
    col=AUX.LeerCol(hoja1,encab[i])
    dic=dict(zip(years,col))
    for j in range(len(years)):
        listaAux=['EmissionsPenalty',encab[i].split(";")[1],'ECU','','',encab[i].split(";")[0],'',years[j],'','','','','',dic[years[j]]]
        df_Energy_output.loc[len(df_Energy_output)] = listaAux
    
    df_Energy_output = df_Energy_output.drop_duplicates(subset = ['EMISSION','YEAR'],keep = 'last')
    df_Energy_output.to_csv("A2_Output_Params/"+encab[i].split(";")[1]+"/EmissionsPenalty.csv", index = None, header=True)
    

########################################################################
########### COPIAAMOS CARPETAS DE A2_Outputs_Params a B1_Outputs_Params
########################################################################
        
from distutils.dir_util import copy_tree


DIRECTORIO_ORIGEN = "./A2_Output_Params/"
DIRECTORIO_DESTINO = "./B1_Output_Params/"


print("Copiando...")
copy_tree(DIRECTORIO_ORIGEN, DIRECTORIO_DESTINO)
print("Copiado")

########################################################################

print("********************************")
print("********************************")
print("proceso finalizado correctamente")
print("********************************")
print("********************************")