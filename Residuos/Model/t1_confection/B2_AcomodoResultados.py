# -*- coding: utf-8 -*-
"""
@author: Luis Victor-Gallardo // 2021
"""
from datetime import date
import sys
import pandas as pd
import os
from copy import deepcopy
import csv
import numpy as np

sys.path.insert(0, 'Executables')
import local_dataset_creator_0

'Define control parameters:'

lista_techs_beneficios_salud=["WWWOT","WWWT","WFIRU","SEWERWWWOT","SEWERWWWT","WWWTFIRU","TWWWOT","SEWERWW","STWW"]


run_for_first_time = True

if run_for_first_time == True:
    local_dataset_creator_0.execute_local_dataset_creator_0_outputs()
    local_dataset_creator_0.execute_local_dataset_creator_0_inputs()
############################################################################################################
df_0_output = pd.read_csv('.\Executables\output_dataset_0.csv', index_col=None, header=0)
###################################
###################################
###################################
nombres_columnas=list(df_0_output.columns)
#print(nombres_columnas)
discount_rate = 0.055
discount_year = 2023
escenario=list()
tecnologia=list()
annio=list()
row_aux=list()
row_aux2=list()
for i in range(len(df_0_output)):
    if df_0_output.iloc[i]['Technology'] in lista_techs_beneficios_salud:
        try:
            row_aux.append(-df_0_output.iloc[i]['CapitalInvestment']*7.3)
            row_aux2.append(-df_0_output.iloc[i]['CapitalInvestment']*7.3/((1+discount_rate)**(int(df_0_output.iloc[i]['Year'])-discount_year)))
            escenario.append(df_0_output.iloc[i]['Strategy'])
            tecnologia.append(df_0_output.iloc[i]['Technology'])
            annio.append(df_0_output.iloc[i]['Year'])
        except:
            a=0
for i in range(len(row_aux)):
    list_row = [escenario[i],0,np.NaN,
                tecnologia[i],'SALUD',annio[i],
                np.NaN,np.NaN,np.NaN,
                np.NaN,np.NaN,np.NaN,
                np.NaN,np.NaN,np.NaN,
                np.NaN,np.NaN,np.NaN,
                np.NaN,np.NaN,np.NaN,
                np.NaN,np.NaN,np.NaN,
                row_aux[i],np.NaN,np.NaN,
                np.NaN,np.NaN,np.NaN,
                np.NaN,np.NaN,row_aux2[i],
                np.NaN,np.NaN,np.NaN,
                np.NaN,np.NaN]
    df_0_output.loc[len(df_0_output)] = list_row

#['Strategy', 'Future.ID', 'Fuel',
#'Technology', 'Emission', 'Year',
#'Demand', 'NewCapacity', 'AccumulatedNewCapacity',
#'TotalCapacityAnnual', 'TotalTechnologyAnnualActivity', 'ProductionByTechnology',
#'UseByTechnology', 'CapitalInvestment', 'DiscountedCapitalInvestment',
#'SalvageValue', 'DiscountedSalvageValue', 'OperatingCost',
#'DiscountedOperatingCost', 'AnnualVariableOperatingCost', 'AnnualFixedOperatingCost',
#'TotalDiscountedCostByTechnology', 'TotalDiscountedCost', 'AnnualTechnologyEmission',
#'AnnualTechnologyEmissionPenaltyByEmission', 'AnnualTechnologyEmissionsPenalty', 'DiscountedTechnologyEmissionsPenalty',
#'AnnualEmissions', 'Capex2023', 'FixedOpex2023',
#'VarOpex2023', 'Opex2023', 'Externalities2023',
#'Capex_GDP', 'FixedOpex_GDP', 'VarOpex_GDP',
#'Opex_GDP', 'Externalities_GDP']

###################################
###################################
###################################
li_output = [df_0_output]
#
df_output = pd.concat(li_output, axis=0, ignore_index=True)
df_output.sort_values(by=['Future.ID','Fuel','Technology','Emission','Year'], inplace=True)
############################################################################################################
df_0_input = pd.read_csv('.\Executables\input_dataset_0.csv', index_col=None, header=0)
#
li_intput = [df_0_input]
#
df_input = pd.concat(li_intput, axis=0, ignore_index=True)
df_input.sort_values(by=['Future.ID','Strategy.ID','Strategy','Fuel','Technology','Emission','Season','Year'], inplace=True)
############################################################################################################
#
dfa_list = [ df_output, df_input ] #, df_price, df_distribution ]
#
today = date.today()
#
df_output = dfa_list[0]
df_output.to_csv ( 'f0_OSMOSYS_ECU_Output.csv', index = None, header=True)
df_output.to_csv ( 'f0_OSMOSYS_ECU_Output_' + str( today ).replace( '-', '_' ) + '.csv', index = None, header=True)
#
df_input = dfa_list[1]
df_input.to_csv ( 'f0_OSMOSYS_ECU_Input.csv', index = None, header=True)
df_input.to_csv ( 'f0_OSMOSYS_ECU_Input_' + str( today ).replace( '-', '_' ) + '.csv', index = None, header=True)
#

print("********************************")
print("********************************")
print("proceso finalizado correctamente")
print("********************************")
print("********************************")