from datetime import date
import sys
import pandas as pd
import os
import re
import numpy as np

sys.path.insert(0, 'Executables')
import local_dataset_creator_0

sys.path.insert(0, 'Experimental_Platform\Futures')
import local_dataset_creator_f

'Define control parameters:'

file_aboslute_address = os.path.abspath("Broad_Output_Dataset_Creator_f.py")
file_adress = re.escape( file_aboslute_address.replace( 'Broad_Output_Dataset_Creator_f.py', '' ) ).replace( '\:', ':' )

run_for_first_time = True

if run_for_first_time == True:
    local_dataset_creator_0.execute_local_dataset_creator_0_outputs()
    local_dataset_creator_f.execute_local_dataset_creator_f_outputs()
    local_dataset_creator_0.execute_local_dataset_creator_0_inputs()
    local_dataset_creator_f.execute_local_dataset_creator_f_inputs()

############################################################################################################
df_0_output = pd.read_csv('.\Executables\output_dataset_0.csv', index_col=None, header=0)
df_0_output['Scen_fut'] = df_0_output['Strategy'].astype(str) + "_" + df_0_output['Future.ID'].astype(str)
#nombres_columnas=list(df_0_output.columns)
#print(nombres_columnas)

#######################################################
###### NUEVO PARA BENEFICIO EXTERNO EN SECTOR RESIDUOS
#######################################################
lista_techs_beneficios_salud=["WWWOT","WWWT","WFIRU","SEWERWWWOT","SEWERWWWT","WWWTFIRU","TWWWOT","SEWERWW","STWW"]
#nombres_columnas=list(df_0_output.columns)
#print(nombres_columnas)
discount_rate = 0.055
discount_year = 2023
escenario=list()
tecnologia=list()
annio=list()
row_aux=list()
row_aux2=list()
scen_fut=list()
for i in range(len(df_0_output)):
    if df_0_output.iloc[i]['Technology'] in lista_techs_beneficios_salud:
        try:
            #row_aux.append(-df_0_output.iloc[i]['CapitalInvestment']*7.3)
            row_aux2.append(-df_0_output.iloc[i]['CapitalInvestment']*7.3/((1+discount_rate)**(int(df_0_output.iloc[i]['Year'])-discount_year)))
            escenario.append(df_0_output.iloc[i]['Strategy'])
            tecnologia.append(df_0_output.iloc[i]['Technology'])
            annio.append(df_0_output.iloc[i]['Year'])
            scen_fut.append(df_0_output.iloc[i]['Scen_fut'])
        except:
            a=0
for i in range(len(row_aux)):
    list_row = [escenario[i],0,np.NaN, # AQUI PUEDE HABER PROBLEMAS PORQUE NO CONOZCO SI HAY MAS COLUMNAS NUEVAS EN EL DATAFRAME AL INCLUIR EL ANALISIS RDM
                tecnologia[i],'SALUD',annio[i],
                np.NaN,np.NaN,np.NaN,
                np.NaN,np.NaN,np.NaN,
                np.NaN,np.NaN,np.NaN,
                np.NaN,np.NaN,np.NaN,
                np.NaN,np.NaN,np.NaN,
                np.NaN,np.NaN,np.NaN,
                np.NaN,np.NaN,np.NaN, #row_aux[i],np.NaN,np.NaN,
                np.NaN,np.NaN,np.NaN,
                np.NaN,np.NaN,row_aux2[i],
                np.NaN,np.NaN,np.NaN,
                np.NaN,np.NaN,scen_fut[i]]
    df_0_output.loc[len(df_0_output)] = list_row
    
df_0_output=df_0_output.assign(DistanceDriven=np.NaN)
df_0_output=df_0_output.assign(Fleet=np.NaN)
df_0_output=df_0_output.assign(NewFleet=np.NaN)
df_0_output=df_0_output.assign(ProducedMobility=np.NaN)
df_0_output=df_0_output.assign(FilterFuelType=np.NaN)
df_0_output=df_0_output.assign(FilterVehicleType=np.NaN)

lista_orden_output=['Strategy', 'Future.ID', 'Fuel', 'Technology', 'Emission', 'Year', 
                    'Demand', 'NewCapacity', 'AccumulatedNewCapacity', 'TotalCapacityAnnual', 
                    'TotalTechnologyAnnualActivity', 'ProductionByTechnology', 'UseByTechnology', 
                    'CapitalInvestment', 'DiscountedCapitalInvestment', 'SalvageValue', 
                    'DiscountedSalvageValue', 'OperatingCost', 'DiscountedOperatingCost', 
                    'AnnualVariableOperatingCost', 'AnnualFixedOperatingCost', 
                    'TotalDiscountedCostByTechnology', 'TotalDiscountedCost', 'AnnualTechnologyEmission', 
                    'AnnualTechnologyEmissionPenaltyByEmission', 'AnnualTechnologyEmissionsPenalty', 
                    'DiscountedTechnologyEmissionsPenalty', 'AnnualEmissions', 
                    'DistanceDriven', 'Fleet', 'NewFleet', 'ProducedMobility', 'FilterFuelType', 'FilterVehicleType', 
                    'Capex2023', 'FixedOpex2023', 'VarOpex2023', 'Opex2023', 'Externalities2023', 'Capex_GDP', 
                    'FixedOpex_GDP', 'VarOpex_GDP', 'Opex_GDP', 'Externalities_GDP', 'Scen_fut']
df_0_output=df_0_output[lista_orden_output]
nombres_columnas=list(df_0_output.columns)
print(nombres_columnas)
##################################################
##### SE ACABA LO NUEVO
##################################################

# print(df_0_output.columns.tolist())
# print('please review the columns and check')
# sys.exit()

df_f_output = pd.read_csv( file_adress + '\Experimental_Platform\Futures\output_dataset_f.csv', index_col=None, header=0)
nombres_columnas=list(df_f_output.columns)
print(nombres_columnas)

#######################################################
###### NUEVO PARA BENEFICIO EXTERNO EN SECTOR RESIDUOS
#######################################################
escenario=list()
futuro=list()
tecnologia=list()
annio=list()
row_aux=list()
row_aux2=list()
scen_fut=list()
for i in range(len(df_f_output)):
    if df_f_output.iloc[i]['Technology'] in lista_techs_beneficios_salud:
        try:
            #row_aux.append(-df_f_output.iloc[i]['CapitalInvestment']*7.3)
            row_aux2.append(-df_f_output.iloc[i]['CapitalInvestment']*7.3/((1+discount_rate)**(int(df_f_output.iloc[i]['Year'])-discount_year)))
            escenario.append(df_f_output.iloc[i]['Strategy'])
            tecnologia.append(df_f_output.iloc[i]['Technology'])
            annio.append(df_f_output.iloc[i]['Year'])
            scen_fut.append(df_f_output.iloc[i]['Scen_fut'])
            futuro.append(df_f_output.iloc[i]['Future.ID'])
        except:
            a=0
for i in range(len(row_aux)):
    list_row = [escenario[i],futuro[i],np.NaN, # AQUI PUEDE HABER PROBLEMAS PORQUE NO CONOZCO SI HAY MAS COLUMNAS NUEVAS EN EL DATAFRAME AL INCLUIR EL ANALISIS RDM
                tecnologia[i],'SALUD',annio[i],
                np.NaN,np.NaN,np.NaN,
                np.NaN,np.NaN,np.NaN,
                np.NaN,np.NaN,np.NaN,
                np.NaN,np.NaN,np.NaN,
                np.NaN,np.NaN,np.NaN,
                np.NaN,np.NaN,np.NaN,
                np.NaN,np.NaN,np.NaN, #row_aux[i],np.NaN,np.NaN,
                np.NaN,np.NaN,np.NaN,
                np.NaN,np.NaN,np.NaN, 
                np.NaN,np.NaN,np.NaN,
                np.NaN,np.NaN,row_aux2[i],
                np.NaN,np.NaN,np.NaN,
                np.NaN,np.NaN,scen_fut[i]]
    df_f_output.loc[len(df_f_output)] = list_row
    

##################################################
##### SE ACABA LO NUEVO
##################################################

li_output = [df_0_output, df_f_output]
#
df_output = pd.concat(li_output, axis=0, ignore_index=True)
df_output.sort_values(by=['Strategy','Future.ID','Fuel','Technology','Emission','Year'], inplace=True)

############################################################################################################
df_0_input = pd.read_csv('.\Executables\input_dataset_0.csv', index_col=None, header=0)

df_f_input = pd.read_csv('.\Experimental_Platform\Futures\input_dataset_f.csv', index_col=None, header=0)
li_intput = [df_0_input, df_f_input]
#
df_input = pd.concat(li_intput, axis=0, ignore_index=True)
df_input.sort_values(by=['Future.ID','Strategy.ID','Strategy','Fuel','Technology','Emission','Season','Year'], inplace=True)

dfa_list = [ df_output, df_input ]

today = date.today()
#
df_output = dfa_list[0]
df_output.to_csv ( 'OSEMOSYS_ECU_Waste_Output.csv', index = None, header=True)
df_output.to_csv ( 'OSEMOSYS_ECU_Waste_Output_' + str( today ).replace( '-', '_' ) + '.csv', index = None, header=True)
#
df_input = dfa_list[1]
df_input.to_csv ( 'OSEMOSYS_ECU_Waste_Input.csv', index = None, header=True)
df_input.to_csv ( 'OSEMOSYS_ECU_Waste_Input_' + str( today ).replace( '-', '_' ) + '.csv', index = None, header=True)
