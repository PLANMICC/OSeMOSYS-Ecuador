# -*- coding: utf-8 -*-
"""
@author: Luis Victor-Gallardo // 2021
"""
import pandas as pd
import numpy as np
from datetime import date
from copy import deepcopy
import csv
import sys
import pickle
import time


import warnings
warnings.simplefilter("ignore")

'''
May 6th, 2022
The df.append({}) wll have to be changed
'''

start1 = time.time()
# OBJECTIVE: to establish the elements of the model to set up a BAU.
'''
-------------------------------------------------------------------------------------------------------------
Structural feature 1: './A1_Inputs/A-I_Classifier_Modes_Demand.xlsx'
1.a) We use this excel file to determine what demands should be supplied
'''
classifier_demand_sectors = \
    pd.read_excel('./A1_Inputs/A-I_Classifier_Modes_Demand.xlsx',
                  sheet_name='Sectors') # YELLOW // Gives an overview of the sectors to satisfy
classifier_demand_fuel_per_sectors = pd.read_excel('./A1_Inputs/A-I_Classifier_Modes_Demand.xlsx', sheet_name='Fuel_per_Sectors') # ORANGE // Specifies Layout
classifier_demand_fuel_to_code = pd.read_excel('./A1_Inputs/A-I_Classifier_Modes_Demand.xlsx', sheet_name='Fuel_to_Code') # COLORLESS // Gives an equivalence table with names 

cd_sectors_all = classifier_demand_sectors['Sector'].tolist()
cd_sectors_name_eng = classifier_demand_sectors['Plain English'].tolist()
cd_sectors_name_spa = classifier_demand_sectors['Plain Spanish'].tolist()
cd_sectors_method = classifier_demand_sectors['Address_Method'].tolist()

cd_sectors_index = [i for i, x in enumerate( cd_sectors_method) if x != str( 'Detailed')] # Only grabs 'Simple' Demands
cd_sectors_simple = [cd_sectors_all[cd_sectors_index[i]] for i in range(len(cd_sectors_index))]

cd_fuels_in_sectors = classifier_demand_fuel_per_sectors['Fuel/Sector'].tolist()

cd_fuel_to_code_fuels = classifier_demand_fuel_to_code['Fuel'].tolist()
cd_fuel_to_code_codes = classifier_demand_fuel_to_code['Code'].tolist()
cd_fuel_to_code_names_eng = classifier_demand_fuel_to_code['Plain English'].tolist()
cd_fuel_to_code_names_spa = classifier_demand_fuel_to_code['Plain Spanish'].tolist()

demands_simple = []
demands_simple_eng = []
demands_simple_spa = []

techs_demand_simple = []
techs_demand_simple_eng = []
techs_demand_simple_spa = []

techs_demand_input_connect = {}
techs_demand_input_connect_match_later = []
techs_demand_output_connect = {}

for s in cd_sectors_simple:
    these_s_possibles = classifier_demand_fuel_per_sectors[s].tolist()
    these_s_fuels_index = [i for i, x in enumerate( these_s_possibles) if x == str( 'x')]
    these_s_fuels = [cd_fuel_to_code_fuels[these_s_fuels_index[i]] for i in range(len(these_s_fuels_index))]
    #
    this_s_index = cd_sectors_all.index(s)
    this_s_code = s
    this_s_name_eng = cd_sectors_name_eng[this_s_index]
    this_s_name_spa = cd_sectors_name_spa[this_s_index]
    #
    
    # print('check demand issues (1)')
    # sys.exit()
    
    for f in these_s_fuels:

        f_code_index = cd_fuel_to_code_fuels.index(f)
        this_f_code = cd_fuel_to_code_codes[f_code_index]
        this_f_name_eng = cd_fuel_to_code_names_eng[f_code_index]
        this_f_name_spa = cd_fuel_to_code_names_spa[f_code_index]

        #if 'Natural Gas' in f:
        #    print('check demand issues (2)')
        #    sys.exit()


        #
        demands_simple.append('E5_' + this_s_code + this_f_code)
        demands_simple_eng.append('Demand ' + this_s_name_eng + ' ' + this_f_name_eng)
        demands_simple_spa.append('Demanda ' + this_s_name_spa + ' ' + this_f_name_spa)
        #
        techs_demand_simple.append('T5' + this_f_code + '' + this_s_code)
        techs_demand_simple_eng.append('Demand ' + this_f_name_eng + ' for ' + this_s_name_eng)
        techs_demand_simple_spa.append('Demanda ' + this_f_name_spa + ' for ' + this_s_name_spa)
        #
        techs_demand_input_connect.update({techs_demand_simple[-1]:this_f_code}) # *we leave this fuel code but later replace it with the supply side*
        #
        # $*$ CREATE AN EXCEPTION HERE FOR THE ELECTRICITY EXPORTS // THESE SHOULD BE CONNECTED TO TRANSMISSION.
        if this_s_code == 'EXP' and this_f_code == 'ELE': # We specify the specific fuel we wish for the sector.
            techs_demand_input_connect_match_later.append('E2_ELE')
        else:
            techs_demand_input_connect_match_later.append(this_f_code)
        #
        techs_demand_output_connect.update({techs_demand_simple[-1]:demands_simple[-1]})

# print('check demand issues')
# sys.exit()

'''
-------------------------------------------------------------------------------------------------------------
Structural feature 2: './A1_Inputs/A-I_Classifier_Modes_Supply.xlsx'
2.a) We use this excel file to determine how energy supply occurs
'''
classifier_supply_primary_energy = \
    pd.read_excel('./A1_Inputs/A-I_Classifier_Modes_Supply.xlsx',
                  sheet_name='PrimaryEnergy') # ORANGE // Specifies Layout
classifier_supply_sec_energy = \
    pd.read_excel('./A1_Inputs/A-I_Classifier_Modes_Supply.xlsx',
                  sheet_name='SecondaryEnergy') # ORANGE // Specifies Layout

#######################################################################################

cs_p_final_in_chain_all = classifier_supply_primary_energy['Final in Chain'].tolist()
cs_p_final_in_chain_indices = [i for i, x in enumerate( cs_p_final_in_chain_all) if x != str( 'IGNORE')] # Only grabs TRUE or FALSE booleans
cs_p_final_in_chain = [cs_p_final_in_chain_all[cs_p_final_in_chain_indices[i]] for i in range(len(cs_p_final_in_chain_indices))]

cs_p_comm_primary = [classifier_supply_primary_energy['Primary_Commodity'].tolist()[cs_p_final_in_chain_indices[i]] for i in range(len(cs_p_final_in_chain_indices))]
cs_p_comm_secondary = [classifier_supply_primary_energy['Secondary_Commodity'].tolist()[cs_p_final_in_chain_indices[i]] for i in range(len(cs_p_final_in_chain_indices))]

cs_p_tech_code = [classifier_supply_primary_energy['Tech - Code'].tolist()[cs_p_final_in_chain_indices[i]] for i in range(len(cs_p_final_in_chain_indices))]
cs_p_tech_names_eng = [classifier_supply_primary_energy['Tech - Plain English'].tolist()[cs_p_final_in_chain_indices[i]] for i in range(len(cs_p_final_in_chain_indices))]
cs_p_tech_names_spa = [classifier_supply_primary_energy['Tech - Plain Spanish'].tolist()[cs_p_final_in_chain_indices[i]] for i in range(len(cs_p_final_in_chain_indices))]

cs_p_fuel_code = [classifier_supply_primary_energy['Fuel - Code (Output)'].tolist()[cs_p_final_in_chain_indices[i]] for i in range(len(cs_p_final_in_chain_indices))]
cs_p_fuel_names_eng = [classifier_supply_primary_energy['Fuel - Plain English (Output)'].tolist()[cs_p_final_in_chain_indices[i]] for i in range(len(cs_p_final_in_chain_indices))]
cs_p_fuel_names_spa = [classifier_supply_primary_energy['Fuel - Plain Spanish (Output)'].tolist()[cs_p_final_in_chain_indices[i]] for i in range(len(cs_p_final_in_chain_indices))]

#######################################################################################

cs_s_final_in_chain_all = classifier_supply_sec_energy['Final in Chain'].tolist()
cs_s_final_in_chain_indices = [i for i, x in enumerate( cs_s_final_in_chain_all) if x != str( 'IGNORE')] # Only grabs TRUE or FALSE booleans
cs_s_final_in_chain = [cs_s_final_in_chain_all[cs_s_final_in_chain_indices[i]] for i in range(len(cs_s_final_in_chain_indices))]

cs_s_comm_secondary = [classifier_supply_sec_energy['Secondary_Commodity'].tolist()[cs_s_final_in_chain_indices[i]] for i in range(len(cs_s_final_in_chain_indices))]
cs_s_comm_tertiary = [classifier_supply_sec_energy['Tertiary_Commodity'].tolist()[cs_s_final_in_chain_indices[i]] for i in range(len(cs_s_final_in_chain_indices))]

cs_s_tech_code = [classifier_supply_sec_energy['Tech - Code'].tolist()[cs_s_final_in_chain_indices[i]] for i in range(len(cs_s_final_in_chain_indices))]
cs_s_tech_names_eng = [classifier_supply_sec_energy['Tech - Plain English'].tolist()[cs_s_final_in_chain_indices[i]] for i in range(len(cs_s_final_in_chain_indices))]
cs_s_tech_names_spa = [classifier_supply_sec_energy['Tech - Plain Spanish'].tolist()[cs_s_final_in_chain_indices[i]] for i in range(len(cs_s_final_in_chain_indices))]

cs_s_fuel_i_code = [classifier_supply_sec_energy['Fuel - Code (Input)'].tolist()[cs_s_final_in_chain_indices[i]] for i in range(len(cs_s_final_in_chain_indices))]
cs_s_fuel_i_names_eng = [classifier_supply_sec_energy['Fuel - Plain English (Input)'].tolist()[cs_s_final_in_chain_indices[i]] for i in range(len(cs_s_final_in_chain_indices))]
cs_s_fuel_i_names_spa = [classifier_supply_sec_energy['Fuel - Plain Spanish (Input)'].tolist()[cs_s_final_in_chain_indices[i]] for i in range(len(cs_s_final_in_chain_indices))]

cs_s_fuel_o_code = [classifier_supply_sec_energy['Fuel - Code (Output)'].tolist()[cs_s_final_in_chain_indices[i]] for i in range(len(cs_s_final_in_chain_indices))]
cs_s_fuel_o_names_eng = [classifier_supply_sec_energy['Fuel - Plain English (Output)'].tolist()[cs_s_final_in_chain_indices[i]] for i in range(len(cs_s_final_in_chain_indices))]
cs_s_fuel_o_names_spa = [classifier_supply_sec_energy['Fuel - Plain Spanish (Output)'].tolist()[cs_s_final_in_chain_indices[i]] for i in range(len(cs_s_final_in_chain_indices))]

#######################################################################################
# Working with the Primary Energy:
techs_primary = []
primary_techs_names_eng = []
primary_techs_names_spa = []
primary_o_fuels_names_eng = []
primary_o_fuels_names_spa = []

techs_primary_output_connect = {}

techs_demand_input_connect_match_now = deepcopy( techs_demand_input_connect_match_later)

#*****************#
# Unique supply fuels for transport // this will save us complicated callbacks:
unique_final_fuel = []
unique_final_fuel_desc_2_code = {}
#*****************#

for i in range(len(cs_p_final_in_chain)): # NOTE: for this to work, the FUEL as *Final of Value Chain* must be unique, otherwise, it is not a true *Final of Value Chain*.
    this_output_fuel = cs_p_comm_secondary[i]
    this_output_fuel_index = cd_fuel_to_code_fuels.index(this_output_fuel)
    this_output_fuel_code = cd_fuel_to_code_codes[this_output_fuel_index]

    techs_primary.append(cs_p_tech_code[i])
    primary_techs_names_eng.append(cs_p_tech_names_eng[i])
    primary_techs_names_spa.append(cs_p_tech_names_spa[i])
    primary_o_fuels_names_eng.append(cs_p_fuel_names_eng[i])
    primary_o_fuels_names_spa.append(cs_p_fuel_names_spa[i])

    techs_primary_output_connect.update({techs_primary[-1]:cs_p_fuel_code[i]})

    indices_to_match = \
        [i for i, x in enumerate(techs_demand_input_connect_match_now)
         if x == str( this_output_fuel_code)]

    if cs_p_final_in_chain[i] == True:
        for k in range( len(indices_to_match)):
            techs_demand_input_connect_match_now[indices_to_match[k]] = \
                cs_p_fuel_code[i]
        if this_output_fuel not in unique_final_fuel:
            unique_final_fuel.append(this_output_fuel)
            unique_final_fuel_desc_2_code.update({this_output_fuel:
                                                  cs_p_fuel_code[i]})

###############################################################################
techs_secondary = []
secondary_techs_names_eng = []
secondary_techs_names_spa = []
secondary_i_fuels_names_eng = {}
secondary_i_fuels_names_spa = {}
secondary_o_fuels_names_eng = {}
secondary_o_fuels_names_spa = {}

techs_secondary_input_connect = {}
techs_secondary_output_connect = {}

test_tertiary_fuels = \
    list(set(classifier_supply_sec_energy['Tertiary_Commodity'].tolist()))

# print('Review the lists of fuels matching each tech (1)')
# sys.exit()

# Working with the Secondary Energy:
for i in range(len(cs_s_final_in_chain)):
    

    if cs_s_tech_code[i] not in techs_secondary:
        techs_secondary.append(cs_s_tech_code[i])
        techs_secondary_input_connect.update({cs_s_tech_code[i]:[]})
        techs_secondary_output_connect.update({cs_s_tech_code[i]:[]})

        secondary_techs_names_eng.append(cs_s_tech_names_eng[i])
        secondary_techs_names_spa.append(cs_s_tech_names_spa[i])
        secondary_i_fuels_names_eng.update({cs_s_tech_code[i]:[]})
        secondary_i_fuels_names_spa.update({cs_s_tech_code[i]:[]})
        secondary_o_fuels_names_eng.update({cs_s_tech_code[i]:[]})
        secondary_o_fuels_names_spa.update({cs_s_tech_code[i]:[]})

    # rev_list_tsic = deepcopy(techs_secondary_input_connect[cs_s_tech_code[i]])
    # if cs_s_fuel_i_code[i] not in rev_list_tsic:
    techs_secondary_input_connect[cs_s_tech_code[i]
                                 ].append(cs_s_fuel_i_code[i])

    # rev_list_tsoc = deepcopy(techs_secondary_output_connect[cs_s_tech_code[i]])
    # if cs_s_fuel_o_code[i] not in rev_list_tsoc:
    techs_secondary_output_connect[cs_s_tech_code[i]
                                  ].append(cs_s_fuel_o_code[i])
    '''
    Note: these two lists are the same length.
    '''
    secondary_i_fuels_names_eng[cs_s_tech_code[i]
                                ].append(cs_s_fuel_i_names_eng[i])
    secondary_i_fuels_names_spa[cs_s_tech_code[i]
                                ].append(cs_s_fuel_i_names_spa[i])
    secondary_o_fuels_names_eng[cs_s_tech_code[i]
                                ].append(cs_s_fuel_o_names_eng[i])
    secondary_o_fuels_names_spa[cs_s_tech_code[i]
                                ].append(cs_s_fuel_o_names_spa[i])

    this_tertiary_comm_string = cs_s_comm_tertiary[i].split( ' ')


    for test in test_tertiary_fuels: # This loop will always finish
        if test in this_tertiary_comm_string:
            use_this_test = test
            this_output_fuel_index = \
                cd_fuel_to_code_fuels.index(use_this_test)
            this_output_fuel_code = \
                cd_fuel_to_code_codes[this_output_fuel_index]
    indices_to_match = \
        [i for i, x in enumerate(techs_demand_input_connect_match_now)
         if x == str(this_output_fuel_code)]

    #if 'Natural' in this_tertiary_comm_string:
    #    print('check the connection (-1)')
    #    sys.exit()

    if cs_s_final_in_chain[i] == True:
        for k in range( len(indices_to_match)):
            techs_demand_input_connect_match_now[indices_to_match[k]] = \
                cs_s_fuel_o_code[i]
        if use_this_test not in unique_final_fuel:
            unique_final_fuel.append(use_this_test)
            unique_final_fuel_desc_2_code.update({use_this_test:
                                                  cs_s_fuel_o_code[i]})

#-----------------------------------------------------------------------------------------------------------#
# Connecting the supply output with the inputs:
techs_demand_input_connect_keys = list( techs_demand_input_connect.keys())
for i in range(len(techs_demand_input_connect_keys)):
    techs_demand_input_connect[techs_demand_input_connect_keys[i]] = techs_demand_input_connect_match_now[i]


# print('check the connection')
# sys.exit()


#-----------------------------------------------------------------------------------------------------------#
'''
##########################################################################################################################
-------------------------------------------------------------------------------------------------------------
Structural feature 3: './A1_Inputs/A-I_Classifier_Modes_Transport.xlsx'
3.a) We use this excel file to determine how to strcuture the transport sector (the same would apply for other "Special" type of demands in 1.a)
'''
classifier_TRN_mode_broad = pd.read_excel( './A1_Inputs/A-I_Classifier_Modes_Transport.xlsx', sheet_name='Mode_Broad') # YELLOW // Gives an overview of the Transport Demands (Columns) and Group Techs (Rows)
classifier_TRN_mode_per_vehfuel = pd.read_excel( './A1_Inputs/A-I_Classifier_Modes_Transport.xlsx', sheet_name='Mode_per_VehFuel') # ORANGE // What does each Group Tech has as VEHICLE FUELS (e.g. hybrids)?
classifier_TRN_fuel_per_vehfuel = pd.read_excel( './A1_Inputs/A-I_Classifier_Modes_Transport.xlsx', sheet_name='Fuel_per_VehFuel') # ORANGE // What FUEL does each VEHICLE FUEL use?

classifier_TRN_fuel_to_code = pd.read_excel( './A1_Inputs/A-I_Classifier_Modes_Transport.xlsx', sheet_name='Fuel_to_Code') # COLORLESS // Gives an equivalence table with names - FUELS 
classifier_TRN_vehfuel_to_code = pd.read_excel( './A1_Inputs/A-I_Classifier_Modes_Transport.xlsx', sheet_name='VehFuel_to_Code') # COLORLESS // Gives an equivalence table with names - VEHICLE FUEL DESCRIPTION
classifier_TRN_tech_to_code = pd.read_excel( './A1_Inputs/A-I_Classifier_Modes_Transport.xlsx', sheet_name='Tech_to_Code') # COLORLESS // Gives an equivalence table with names - TECHNOLOGY GROUPS
classifier_TRN_dem_to_code = pd.read_excel( './A1_Inputs/A-I_Classifier_Modes_Transport.xlsx', sheet_name='Dem_to_Code') # COLORLESS // Gives an equivalence table with names - DEMAND CODES

# CALLING ALL EQUIVALENCIES: // NOTE: *sp_trn* means "special - transport"
# i)
sp_trn_fuel_to_code_Fuel = classifier_TRN_fuel_to_code['Fuel'].tolist()
sp_trn_fuel_to_code_Code = classifier_TRN_fuel_to_code['Code'].tolist()
sp_trn_fuel_to_code_names_eng = classifier_TRN_fuel_to_code['Plain_English'].tolist()
sp_trn_fuel_to_code_names_spa = classifier_TRN_fuel_to_code['Plain Spanish'].tolist()
# ii)
sp_trn_vehfuel_to_code_VehFuel = classifier_TRN_vehfuel_to_code['VehFuel'].tolist()
sp_trn_vehfuel_to_code_Code = classifier_TRN_vehfuel_to_code['Code'].tolist()
sp_trn_vehfuel_to_code_names_eng = classifier_TRN_vehfuel_to_code['Plain_English'].tolist()
sp_trn_vehfuel_to_code_names_spa = classifier_TRN_vehfuel_to_code['Plain Spanish'].tolist()
# iii)
sp_trn_tech_to_code_Tech = classifier_TRN_tech_to_code['Techs'].tolist()
sp_trn_tech_to_code_Code = classifier_TRN_tech_to_code['Code'].tolist()
sp_trn_tech_to_code_names_eng = classifier_TRN_tech_to_code['Plain_English'].tolist()
sp_trn_tech_to_code_names_spa = classifier_TRN_tech_to_code['Plain Spanish'].tolist()
# iv)
sp_trn_dem_to_code_Code = classifier_TRN_dem_to_code['Demand_Codes'].tolist()
sp_trn_dem_to_code_names_eng = classifier_TRN_dem_to_code['Plain_English'].tolist()
sp_trn_dem_to_code_names_spa = classifier_TRN_dem_to_code['Plain Spanish'].tolist()

'''
-------------------------------------------------------------------------------------------------------------
3.b) The first step is defining that the columns of the first table are the FINAL TRANSPORT DEMANDS, so we should call them.
#
classifier_TRN_mode_broad :: 'Techs/Demand','E6TDPASSPUB','E6TDPASPRIV','E6TDFREHEA','E6TDFRELIG' (updated 20/7/2020)
'''
sp_trn_demands = classifier_TRN_mode_broad.columns.tolist()[1:]
sp_trn_group_techs = classifier_TRN_mode_broad['Techs/Demand'].tolist()
sp_trn_group_techs_names_eng = []

sp_trn_group_techs_o_connect = {}
sp_trn_group_techs_i_connect = {}
sp_trn_group_techs_d = {}
for t in sp_trn_group_techs:
    sp_trn_group_techs_o_connect.update( {t:''})
    sp_trn_group_techs_i_connect.update( {t:''})
    sp_trn_group_techs_d.update( {t:''})

sp_trn_techs_per_demands = {}
for d in sp_trn_demands:
    sp_trn_techs_per_demands.update({d:[]})

    this_x_marks = classifier_TRN_mode_broad[d].tolist()
    for t in range(len(this_x_marks)):
        if this_x_marks[t] == 'x':
            sp_trn_techs_per_demands[d].append(sp_trn_group_techs[t])
            sp_trn_group_techs_o_connect[sp_trn_group_techs[t]] = d

            code_tech_index = sp_trn_tech_to_code_Tech.index(sp_trn_group_techs[t])
            code_tech = sp_trn_tech_to_code_Code[code_tech_index]
            sp_trn_group_techs_i_connect[sp_trn_group_techs[t]] = 'E5_' + code_tech

            sp_trn_group_techs_d[sp_trn_group_techs[t]] = d[-3:]

'''
-------------------------------------------------------------------------------------------------------------
3.c) The second step is defining that the columns of the second table are the varieties of each GROUP TECH, so we should call them.
#
classifier_TRN_mode_per_vehfuel :: 'VehFuel/Tech','Techs_4WD','Techs_LD','Techs_Minivan','Techs_Motos','Techs_Buses','Techs_Microbuses','Techs_Taxis','Techs_Trains','Techs_He_Freight','Techs_Li_Freight' (updated 20/7/2020)
'''
# From the above columns, we note that the columns are the GROUP TECHS, so no need to call them again.
sp_trn_vehfuels = classifier_TRN_mode_per_vehfuel['VehFuel/Tech'].tolist()

sp_trn_vehfuels_per_techs = {}
for t in sp_trn_group_techs:
    sp_trn_vehfuels_per_techs.update({t:[]})
    #
    this_x_marks = classifier_TRN_mode_per_vehfuel[t].tolist()
    for vf in range(len(sp_trn_vehfuels)):
        if this_x_marks[vf] == 'x':
            sp_trn_vehfuels_per_techs[t].append(sp_trn_vehfuels[vf])
            #
        #
    #
#
'''
-------------------------------------------------------------------------------------------------------------
3.d) The third step is defining that the columns of the third table are the varieties of each GROUP TECH, so we should call them.
#
classifier_TRN_fuel_per_vehfuel :: 'VehFuel/Fuel','Diesel','Gasoline','LPG','Electricity','Hydrogren' (updated 20/7/2020)
'''
# From the above columns, we note that the columns are the FUELS, so we need to call them (for the first time).
sp_trn_fuels = classifier_TRN_fuel_per_vehfuel.columns.tolist()[1:]
# *sp_trn_vehfuels* is the same as previously defined in 3.c)

sp_trn_fuel_per_vehfuels = {}
for vf in range(len(sp_trn_vehfuels)):
    sp_trn_fuel_per_vehfuels.update({sp_trn_vehfuels[vf]:[]})

    for f in sp_trn_fuels:
        this_x_marks = classifier_TRN_fuel_per_vehfuel[f].tolist()

        if this_x_marks[vf] == 'x':
            sp_trn_fuel_per_vehfuels[sp_trn_vehfuels[vf]].append(f)

'''
-------------------------------------------------------------------------------------------------------------
3.e) The fourth step is combining the previous data.
'''
#**************************#
# These are for the vehicles-per-fuel- technology:
sp_trn_techs = []
sp_trn_techs_names_eng = []
sp_trn_techs_names_spa = []
#
sp_trn_techs_o_connect = {}
sp_trn_techs_i_connect = {}
#
#**************************#
# These are for the fuel distribution technologies:
sp_trn_fuel_dist = []
sp_trn_fuel_dist_eng = []
sp_trn_fuel_dist_spa = []
#
sp_trn_techs_dist = []
sp_trn_techs_dist_eng = []
sp_trn_techs_dist_spa = []
#
sp_trn_dist_techs_o_connect = {}
sp_trn_dist_techs_i_connect = {}
#
#**************************#

dict_dist_fam_to_name_eng = \
    {'PUB':'Public', 'PRI':'Private', 'HEA':'Heavy Freight',
     'MED':'Medium Freight', 'LIG':'Light Freight'}
dict_dist_fam_to_name_spa = \
    {'PUB':'Público', 'PRI':'Privado', 'HEA':'Carga Pesada',
     'MED':'Carga Mediana', 'LIG':'Carga Liviana' }

for gt in sp_trn_group_techs: # gt is for group tech
    #
    this_gt_index_4code = sp_trn_tech_to_code_Tech.index(gt)
    sp_trn_group_techs_names_eng.append(sp_trn_tech_to_code_names_eng[this_gt_index_4code])
    #
    these_vfs = sp_trn_vehfuels_per_techs[gt]
    #
    for vf in these_vfs:
        this_vf_index_4code = sp_trn_vehfuel_to_code_VehFuel.index(vf)
        #
        these_fs = sp_trn_fuel_per_vehfuels[vf]
        #---------------------------------------------------------------#
        # We must call the elements indexed to compose the tech code:
        the_tech_code = sp_trn_tech_to_code_Code[this_gt_index_4code]
        the_vehfuel_code = sp_trn_vehfuel_to_code_Code[this_vf_index_4code]
        sp_trn_techs.append(the_tech_code + the_vehfuel_code)
        #
        the_tech_name_eng = sp_trn_tech_to_code_names_eng[this_gt_index_4code]
        the_vehfuel_name_eng = sp_trn_vehfuel_to_code_names_eng[this_vf_index_4code]
        sp_trn_techs_names_eng.append(the_tech_name_eng + ' ' + the_vehfuel_name_eng)
        #
        the_tech_name_spa = sp_trn_tech_to_code_names_spa[this_gt_index_4code]
        the_vehfuel_name_spa = sp_trn_vehfuel_to_code_names_spa[this_vf_index_4code]
        sp_trn_techs_names_spa.append(the_tech_name_spa + ' ' + the_vehfuel_name_spa)
        #
        #---------------------------------------------------------------#
        # Calling the dictionaries to complete the input/output naming:
        sp_trn_techs_o_connect.update({sp_trn_techs[-1]:sp_trn_group_techs_i_connect[gt]})
        sp_trn_techs_i_connect.update({sp_trn_techs[-1]:[]})
        #
        fuel_dist_fam = sp_trn_group_techs_d[gt]

        for f in these_fs:
            this_f_index_4code = sp_trn_fuel_to_code_Fuel.index(f)
            the_fuel_code = sp_trn_fuel_to_code_Code[this_f_index_4code]

            this_vehicle_input_fuel = 'E4_' + the_fuel_code + fuel_dist_fam
            this_vehicle_dist_techs = 'T4_' + the_fuel_code + fuel_dist_fam

            sp_trn_techs_i_connect[sp_trn_techs[-1]].append(this_vehicle_input_fuel)

            if this_vehicle_input_fuel not in sp_trn_fuel_dist:
                sp_trn_fuel_dist.append(this_vehicle_input_fuel)
                sp_trn_techs_dist.append(this_vehicle_dist_techs)

                this_dist_fam_to_name_eng = dict_dist_fam_to_name_eng[fuel_dist_fam]
                this_dist_fam_to_name_spa = dict_dist_fam_to_name_spa[fuel_dist_fam]
                this_code_names_eng = sp_trn_fuel_to_code_names_eng[this_f_index_4code]
                this_code_names_spa = sp_trn_fuel_to_code_names_spa[this_f_index_4code]

                sp_trn_fuel_dist_eng.append('Distributed ' + this_code_names_eng + ' for ' + this_dist_fam_to_name_eng)
                sp_trn_fuel_dist_spa.append('Distributed ' + this_code_names_spa + ' for ' + this_dist_fam_to_name_spa)
                sp_trn_techs_dist_eng.append('Distribute ' + this_code_names_eng + ' for ' + this_dist_fam_to_name_eng)
                sp_trn_techs_dist_spa.append('Distribute ' + this_code_names_spa + ' for ' + this_dist_fam_to_name_spa)

                sp_trn_dist_techs_o_connect.update({this_vehicle_dist_techs:this_vehicle_input_fuel})

                supply_input = unique_final_fuel_desc_2_code[f]
                sp_trn_dist_techs_i_connect.update({this_vehicle_dist_techs:supply_input})

'''
For all effects, read all the user-defined scenarios in future 0, created by hand in Base_Runs_Generator.py ;
These data parameters serve as the basis to implement the experiment.
'''
horizon_configuration = pd.read_excel( './A1_Inputs/A-I_Horizon_Configuration.xlsx')
baseyear = horizon_configuration['Initial_Year'].tolist()[0]
endyear = horizon_configuration['Final_Year'].tolist()[0]
global time_range_vector
time_range_vector = [n for n in range( baseyear, endyear+1)]
'''
################################# PART 1 #################################
'''
# Objective: Produce a Structure OSEMOSYS-CR
#   Let us recapitulate what the key variables for this are.

# Primary supply:
codes_list_techs_primary = techs_primary # // LIST # these are techs that provide primary energy supply
codes_dict_techs_primary_output = techs_primary_output_connect # // DICT # Has the FUELS that are outputs

# Secondary technologies:
codes_list_techs_secondary = techs_secondary # // LIST # these are techs that provide secondary energy supply
codes_dict_techs_secondary_input = techs_secondary_input_connect # // DICT # Has the FUELS that are inputs
codes_dict_techs_secondary_output = techs_secondary_output_connect # // DICT # Has the FUELS that are outputs

# Demand side:
codes_list_fuels_demands = demands_simple # these are fuels
codes_list_techs_demands = techs_demand_simple # // LIST # these are techs that have demand outputs
codes_dict_techs_demands_input = techs_demand_input_connect # // DICT # Has the FUELS that are inputs
codes_dict_techs_demands_output = techs_demand_output_connect # // DICT # Has the FUELS that are outputs

# Fuel distribution for transport technologies:
codes_list_techs_DISTTRN = sp_trn_techs_dist # // LIST # these are techs that provide secondary energy supply
codes_list_techs_DISTTRN_input = sp_trn_dist_techs_i_connect # // DICT # Has the FUELS that are inputs
codes_list_techs_DISTTRN_output = sp_trn_dist_techs_o_connect # // DICT # Has the FUELS that are outputs

# Transport technologies:
codes_list_techs_TRN = sp_trn_techs # // LIST # these are techs that provide secondary energy supply
codes_list_techs_TRN_input = sp_trn_techs_i_connect # // DICT # Has the FUELS that are inputs
codes_list_techs_TRN_output = sp_trn_techs_o_connect # // DICT # Has the FUELS that are outputs

# Transport group technologies:
codes_list_techs_TRNGROUP = sp_trn_group_techs
codes_list_techs_TRNGROUP_input = sp_trn_group_techs_i_connect
codes_list_techs_TRNGROUP_output = sp_trn_group_techs_o_connect

codes_list_techs_all = codes_list_techs_primary + codes_list_techs_secondary +\
    codes_list_techs_demands + codes_list_techs_DISTTRN +\
    codes_list_techs_TRN + codes_list_techs_TRNGROUP

###############################################################
# Now let us visualize the connection of the model:
#   We will print the tecnologies horizontally;
#   We will start from the primary supply and continue through the secondary supply.
#       Primary => Secondary && DISTTRN // Secondary => Demands
#       then,
#       DISTTRN => TRN => TRNGROUP
# we will create a dataframe and create each of these sections as columns:
codes_primary_secondary_demands_df_headers = [\
    'Primary.Tech', 'Primary.Fuel.O', 'Secondary.Fuel.I', 'Secondary.Tech',
    'Secondary.Fuel.O', 'Demands.Fuel.I', 'Demands.Tech', 'Demands.Fuel.O']
codes_primary_secondary_demands_df = \
    pd.DataFrame(columns = codes_primary_secondary_demands_df_headers)

codes_transport_df_headers = [\
    'DISTTRN.Fuel.I', 'DISTTRN.Tech', 'DISTTRN.Fuel.O', 'TRN.Fuel.I',
    'TRN.Tech', 'TRN.Fuel.O', 'TRNGROUP.Fuel.I', 'TRNGROUP.Tech',
    'TRNGROUP.Fuel.O']
codes_transport_df = pd.DataFrame(columns = codes_transport_df_headers)

#---------------#
tech_param_list_all_notyearly = ['CapacityToActivityUnit', 'OperationalLife']
tech_param_list_primary = [\
    'CapitalCost', 'FixedCost', 'VariableCost', 'ResidualCapacity',
    'TotalAnnualMaxCapacity', 'TotalTechnologyAnnualActivityUpperLimit',
    'TotalTechnologyAnnualActivityLowerLimit',
    'TotalAnnualMinCapacityInvestment', 'CapacityFactor', 'AvailabilityFactor']
tech_param_list_secondary = [\
    'CapitalCost', 'FixedCost', 'VariableCost', 'ResidualCapacity',
    'TotalAnnualMaxCapacity', 'TotalTechnologyAnnualActivityUpperLimit',
    'TotalTechnologyAnnualActivityLowerLimit',
    'TotalAnnualMinCapacityInvestment', 'CapacityFactor', 'AvailabilityFactor']
tech_param_list_demands = ['CapitalCost', 'FixedCost', 'ResidualCapacity']
tech_param_list_disttrn = ['CapitalCost', 'FixedCost', 'ResidualCapacity']
tech_param_list_trn = [\
    'CapitalCost', 'FixedCost', 'ResidualCapacity', 'TotalAnnualMaxCapacity',
    'TotalTechnologyAnnualActivityLowerLimit']
tech_param_list_trngroups = [\
    'TotalAnnualMaxCapacity', 'TotalTechnologyAnnualActivityLowerLimit']

#---------------#
tech_param_list_all_notyearly_df_headers = [\
    'Tech.Type','Tech.ID', 'Tech', 'Tech.Name', 'Parameter.ID', 'Parameter',
    'Unit', 'Value']

tech_param_list_all_notyearly_df = \
    pd.DataFrame(columns = tech_param_list_all_notyearly_df_headers)

tech_param_list_all_yearly_df_headers = [\
    'Tech.ID', 'Tech', 'Tech.Name' , 'Parameter.ID', 'Parameter', 'Unit',
    'Projection.Mode', 'Projection.Parameter'] + time_range_vector

#---------------#
tech_param_list_yearly_primary_df = pd.DataFrame(columns=tech_param_list_all_yearly_df_headers)

tech_param_list_yearly_secondary_df = pd.DataFrame(columns=tech_param_list_all_yearly_df_headers)

tech_param_list_yearly_demands_df = pd.DataFrame(columns=tech_param_list_all_yearly_df_headers)

tech_param_list_yearly_disttrn_df = pd.DataFrame(columns=tech_param_list_all_yearly_df_headers)

tech_param_list_yearly_trn_df = pd.DataFrame(columns=tech_param_list_all_yearly_df_headers)

tech_param_list_yearly_trngroups_df = pd.DataFrame(columns=tech_param_list_all_yearly_df_headers)

#############################################################################################
all_lens_psd = [len(codes_list_techs_primary), len(codes_list_techs_secondary),
                len(codes_list_techs_demands)]
max_lens_psd = max( all_lens_psd)

all_lens_trn = [len(codes_list_techs_DISTTRN), len(codes_list_techs_TRN), 
                len( codes_list_techs_TRNGROUP)]
max_lens_trn = max( all_lens_trn)

#############################################################################################
for n in range(max_lens_psd):
    #-------------------------------------------------------------------------#
    if n < len( codes_list_techs_primary):
        this_primary_tech = codes_list_techs_primary[n]
        this_primary_fuel_o = codes_dict_techs_primary_output[codes_list_techs_primary[n]]
    else: # we surpassed this limit and must fill table with empty strings
        this_primary_tech = ''
        this_primary_fuel_o = ''
    #-------------------------------------------------------------------------#
    if n < len( codes_list_techs_secondary):
        this_secondary_fuel_i = codes_dict_techs_secondary_input[codes_list_techs_secondary[n]]
        this_secondary_tech = codes_list_techs_secondary[n]
        this_secondary_fuel_o = codes_dict_techs_secondary_output[codes_list_techs_secondary[n]]
    else: # we surpassed this limit and must fill table with empty strings
        this_secondary_fuel_i = ''
        this_secondary_tech = ''
        this_secondary_fuel_o = ''
    #-------------------------------------------------------------------------#
    if n < len( codes_list_techs_demands):
        this_demand_fuel_i = codes_dict_techs_demands_input[codes_list_techs_demands[n]]
        this_demand_tech = codes_list_techs_demands[n]
        this_demand_fuel_o = codes_dict_techs_demands_output[codes_list_techs_demands[n]]
    else: # we surpassed this limit and must fill table with empty strings
        this_demand_fuel_i = ''
        this_demand_tech = ''
        this_demand_fuel_o = ''
    #-------------------------------------------------------------------------#
    #
    codes_primary_secondary_demands_df = \
        codes_primary_secondary_demands_df.append({
        'Primary.Tech'      :this_primary_tech,
        'Primary.Fuel.O'    :this_primary_fuel_o,
        'Secondary.Fuel.I'  :this_secondary_fuel_i,
        'Secondary.Tech'    :this_secondary_tech,
        'Secondary.Fuel.O'  :this_secondary_fuel_o,
        'Demands.Fuel.I'    :this_demand_fuel_i,
        'Demands.Tech'      :this_demand_tech,
        'Demands.Fuel.O'    :this_demand_fuel_o
        }, ignore_index=True)

# print('Review the lists of fuels matching each tech (1.1)')
# sys.exit()

#############################################################################################
for n in range( max_lens_trn):
    #-------------------------------------------------------------------------#
    if n < len( codes_list_techs_DISTTRN):
        this_DISTTRN_fuel_i = codes_list_techs_DISTTRN_input[codes_list_techs_DISTTRN[n]]
        this_DISTTRN_tech   = codes_list_techs_DISTTRN[n]
        this_DISTTRN_fuel_o = codes_list_techs_DISTTRN_output[codes_list_techs_DISTTRN[n]]
    else: # we surpassed this limit and must fill table with empty strings
        this_DISTTRN_fuel_i = ''
        this_DISTTRN_tech   = ''
        this_DISTTRN_fuel_o = ''
    #-------------------------------------------------------------------------#
    if n < len( codes_list_techs_TRN):
        this_TRN_fuel_i = codes_list_techs_TRN_input[codes_list_techs_TRN[n]]
        this_TRN_tech   = codes_list_techs_TRN[n]
        this_TRN_fuel_o = codes_list_techs_TRN_output[codes_list_techs_TRN[n]]
    else: # we surpassed this limit and must fill table with empty strings
        this_TRN_fuel_i     = ''
        this_TRN_tech       = ''
        this_TRN_fuel_o     = ''
    #-------------------------------------------------------------------------#
    if n < len( codes_list_techs_TRNGROUP):
        this_TRNGROUP_fuel_i    = codes_list_techs_TRNGROUP_input[codes_list_techs_TRNGROUP[n]]
        this_TRNGROUP_tech      = codes_list_techs_TRNGROUP[n]
        this_TRNGROUP_fuel_o    = codes_list_techs_TRNGROUP_output[codes_list_techs_TRNGROUP[n]]
    else: # we surpassed this limit and must fill table with empty strings
        this_TRNGROUP_fuel_i    = ''
        this_TRNGROUP_tech      = ''
        this_TRNGROUP_fuel_o    = ''
    #-------------------------------------------------------------------------#
    #
    codes_transport_df = codes_transport_df.append({\
        'DISTTRN.Fuel.I'    :this_DISTTRN_fuel_i    ,
        'DISTTRN.Tech'      :this_DISTTRN_tech      ,
        'DISTTRN.Fuel.O'    :this_DISTTRN_fuel_o    ,
        'TRN.Fuel.I'        :this_TRN_fuel_i        ,
        'TRN.Tech'          :this_TRN_tech          ,
        'TRN.Fuel.O'        :this_TRN_fuel_o        ,
        'TRNGROUP.Fuel.I'   :this_TRNGROUP_fuel_i   ,
        'TRNGROUP.Tech'     :this_TRNGROUP_tech     ,
        'TRNGROUP.Fuel.O'   :this_TRNGROUP_fuel_o
        }, ignore_index=True)

###############################################################################
#-----------------------------------------------------------------------------#
# Primary Techs
for n in range(len(codes_list_techs_primary)):
    for p in range(len(tech_param_list_all_notyearly)):
        tech_param_list_all_notyearly_df = \
            tech_param_list_all_notyearly_df.append({
            'Tech.Type'             : 'Primary'                         ,
            'Tech.ID'               : n+1                               ,
            'Tech'                  : codes_list_techs_primary[n]       ,
            'Tech.Name'             : primary_techs_names_eng[n]        ,
            'Parameter.ID'          : p+1                               ,
            'Parameter'             : tech_param_list_all_notyearly[p]
            }, ignore_index=True)

    for p in range(len(tech_param_list_primary)):
        tech_param_list_yearly_primary_df = \
            tech_param_list_yearly_primary_df.append({
            'Tech.ID'               : n+1                               ,
            'Tech'                  : codes_list_techs_primary[n]       ,
            'Tech.Name'             : primary_techs_names_eng[n]        ,
            'Parameter.ID'          : p+1                               ,
            'Parameter'             : tech_param_list_primary[p]        ,
            'Projection.Parameter'  : 0
            }, ignore_index=True)

#-----------------------------------------------------------------------------#
# Secondary Techs
for n in range(len(codes_list_techs_secondary)):
    for p in range(len(tech_param_list_all_notyearly)):
        tech_param_list_all_notyearly_df = \
            tech_param_list_all_notyearly_df.append({
            'Tech.Type'             : 'Secondary'                       ,
            'Tech.ID'               : n+1                               ,
            'Tech'                  : codes_list_techs_secondary[n]     ,
            'Tech.Name'             : secondary_techs_names_eng[n]      ,
            'Parameter.ID'          : p+1                               ,
            'Parameter'             : tech_param_list_all_notyearly[p]
            }, ignore_index=True)

    for p in range(len(tech_param_list_secondary)):
        tech_param_list_yearly_secondary_df = \
            tech_param_list_yearly_secondary_df.append({
            'Tech.ID'               : n+1                               ,
            'Tech'                  : codes_list_techs_secondary[n]     ,
            'Tech.Name'             : secondary_techs_names_eng[n]      ,
            'Parameter.ID'          : p+1                               ,
            'Parameter'             : tech_param_list_secondary[p]      ,
            'Projection.Parameter'  : 0
            }, ignore_index=True)

#-----------------------------------------------------------------------------#
# Demand Techs (simple)
for n in range(len(codes_list_techs_demands)):
    for p in range(len(tech_param_list_all_notyearly)):
        tech_param_list_all_notyearly_df = \
            tech_param_list_all_notyearly_df.append({
            'Tech.Type'             : 'Demand Techs'                    ,
            'Tech.ID'               : n+1                               ,
            'Tech'                  : codes_list_techs_demands[n]       ,
            'Tech.Name'             : techs_demand_simple_eng[n]        ,
            'Parameter.ID'          : p+1                               ,
            'Parameter'             : tech_param_list_all_notyearly[p]
            }, ignore_index=True)

    for p in range(len(tech_param_list_demands)):
        tech_param_list_yearly_demands_df = \
            tech_param_list_yearly_demands_df.append({
            'Tech.ID'               : n+1                               ,
            'Tech'                  : codes_list_techs_demands[n]       ,
            'Tech.Name'             : techs_demand_simple_eng[n]        ,
            'Parameter.ID'          : p+1                               ,
            'Parameter'             : tech_param_list_demands[p]        ,
            'Projection.Parameter'  : 0
            }, ignore_index=True)

#-----------------------------------------------------------------------------#
# Transport fuel distribution techs:
for n in range(len(codes_list_techs_DISTTRN)):
    for p in range(len(tech_param_list_all_notyearly)):
        tech_param_list_all_notyearly_df = \
            tech_param_list_all_notyearly_df.append({
            'Tech.Type'             : 'Transport Fuel Distribution'     ,
            'Tech.ID'               : n+1                               ,
            'Tech'                  : codes_list_techs_DISTTRN[n]       ,
            'Tech.Name'             : sp_trn_techs_dist_eng[n]          ,
            'Parameter.ID'          : p+1                               ,
            'Parameter'             : tech_param_list_all_notyearly[p]
            }, ignore_index=True)

    for p in range( len(tech_param_list_disttrn)):
        tech_param_list_yearly_disttrn_df = \
            tech_param_list_yearly_disttrn_df.append({
            'Tech.ID'               : n+1                               ,
            'Tech'                  : codes_list_techs_DISTTRN[n]       ,
            'Tech.Name'             : sp_trn_techs_dist_eng[n]          ,
            'Parameter.ID'          : p+1                               ,
            'Parameter'             : tech_param_list_disttrn[p]        ,
            'Projection.Parameter'  : 0
            }, ignore_index=True)

#-----------------------------------------------------------------------------#
# Transport vehicle techs:
for n in range(len(codes_list_techs_TRN)):
    for p in range(len(tech_param_list_all_notyearly)):
        tech_param_list_all_notyearly_df = \
            tech_param_list_all_notyearly_df.append({
            'Tech.Type'             : 'Transport Vehicles'              ,
            'Tech.ID'               : n+1                               ,
            'Tech'                  : codes_list_techs_TRN[n]           ,
            'Tech.Name'             : sp_trn_techs_names_eng[n]         ,
            'Parameter.ID'          : p+1                               ,
            'Parameter'             : tech_param_list_all_notyearly[p]
            }, ignore_index=True)

    for p in range(len(tech_param_list_trn)):
        tech_param_list_yearly_trn_df = \
            tech_param_list_yearly_trn_df.append({
            'Tech.ID'               : n+1                               ,
            'Tech'                  : codes_list_techs_TRN[n]           ,
            'Tech.Name'             : sp_trn_techs_names_eng[n]         ,
            'Parameter.ID'          : p+1                               ,
            'Parameter'             : tech_param_list_trn[p]            ,
            'Projection.Parameter'  : 0
            }, ignore_index=True)

#-----------------------------------------------------------------------------#
# Transport vehicle group techs:
for n in range(len(codes_list_techs_TRNGROUP)):
    for p in range(len(tech_param_list_all_notyearly)):
        tech_param_list_all_notyearly_df = \
            tech_param_list_all_notyearly_df.append({
            'Tech.Type'             : 'Vehicle Groups'                  ,
            'Tech.ID'               : n+1                               ,
            'Tech'                  : codes_list_techs_TRNGROUP[n]      ,
            'Tech.Name'             : sp_trn_group_techs_names_eng[n]   ,
            'Parameter.ID'          : p+1                               ,
            'Parameter'             : tech_param_list_all_notyearly[p]
            }, ignore_index=True)

    for p in range(len(tech_param_list_trngroups)):
        tech_param_list_yearly_trngroups_df = \
            tech_param_list_yearly_trngroups_df.append({
            'Tech.ID'               : n+1                               ,
            'Tech'                  : codes_list_techs_TRNGROUP[n]      ,
            'Tech.Name'             : sp_trn_group_techs_names_eng[n]   ,
            'Parameter.ID'          : p+1                               ,
            'Parameter'             : tech_param_list_trngroups[p]      ,
            'Projection.Parameter'  : 0
            }, ignore_index=True)

#############################################################################################
# We must create different sheets with every section of the model, and we must create:
#   1) Base Year calibration data, 2) Projection Data
#   3) Demand data, which we will define here:
df_demands_all_header = [\
    'Demand/Share', 'Fuel/Tech', 'Name',
    'Ref.Cap.BY', 'Ref.OAR.BY', 'Ref.km.BY',
    'Projection.Mode', 'Projection.Parameter'] + time_range_vector
df_demands_all = pd.DataFrame(columns=df_demands_all_header)
df_demands_fuel_list = []
#
#---------------------------------------------------------------------------------------------------------------------------------#
# A - Let's start by looking at the primary technologies for the base year // we need the elements of codename and fields for data:
df_techs_primary_base_year_HEADER = [\
    'Tech', 'Tech.Name', 'Fuel.O', 'Fuel.O.Name', 'Value.Fuel.O', 'Unit.Fuel.O'
    ]
df_techs_primary_projection_HEADER = [\
    'Tech', 'Tech.Name', 'Fuel', 'Fuel.Name', 'Direction',
    'Projection.Mode', 'Projection.Parameter'] + time_range_vector

df_techs_primary_base_year = pd.DataFrame(columns=df_techs_primary_base_year_HEADER)
df_techs_primary_projection = pd.DataFrame(columns=df_techs_primary_projection_HEADER)

this_complete_fuel_o = []
for n in range(len(codes_list_techs_primary)):
    this_complete_fuel_o.append(codes_dict_techs_primary_output[codes_list_techs_primary[n]])

for n in range(len(codes_list_techs_primary)):
    this_tech_names = primary_techs_names_eng[n]
    this_fuel_o = codes_dict_techs_primary_output[codes_list_techs_primary[n]]
    this_fuel_o_name_index = this_complete_fuel_o.index(this_fuel_o)
    this_fuel_o_name = primary_o_fuels_names_eng[this_fuel_o_name_index]

    df_techs_primary_base_year = df_techs_primary_base_year.append({\
        'Tech'          : codes_list_techs_primary[n]   ,
        'Tech.Name'     : this_tech_names               ,
        'Fuel.O'        : this_fuel_o                   ,
        'Fuel.O.Name'   : this_fuel_o_name                ,
        'Value.Fuel.O'  : 1 # This should be filled by the user
        }, ignore_index=True)

    df_techs_primary_projection = df_techs_primary_projection.append({\
        'Tech'                  : codes_list_techs_primary[n]   ,
        'Tech.Name'             : this_tech_names               ,
        'Fuel'                  : this_fuel_o                   ,
        'Fuel.Name'             : this_fuel_o_name                ,
        'Direction'             : 'Output',
        'Projection.Mode'       : '',
        'Projection.Parameter'  : 1 # This should be filled by the user
        }, ignore_index=True)

df_techs_primary_projection = \
    df_techs_primary_projection.replace(np.nan, '', regex=True)

#-----------------------------------------------------------------------------#
# B - Let's now take the elements for the secondary energy and reproduce what we did above:
df_techs_secondary_base_year_HEADER = [\
    'Fuel.I', 'Fuel.I.Name', 'Value.Fuel.I', 'Unit.Fuel.I', 'Tech',
    'Tech.Name', 'Fuel.O', 'Fuel.O.Name', 'Value.Fuel.O', 'Unit.Fuel.O']
df_techs_secondary_projection_HEADER = [\
    'Tech', 'Tech.Name', 'Fuel', 'Fuel.Name', 'Direction', 'Projection.Mode',
    'Projection.Parameter'] + time_range_vector

df_techs_secondary_base_year = \
    pd.DataFrame(columns = df_techs_secondary_base_year_HEADER)
df_techs_secondary_projection = \
    pd.DataFrame(columns = df_techs_secondary_projection_HEADER)

this_complete_fuel_i = []
this_complete_fuel_o = []
for n in range(len(codes_list_techs_secondary)):
    this_fuel_i_list = \
        codes_dict_techs_secondary_input[codes_list_techs_secondary[n]]
    this_fuel_o_list = \
        codes_dict_techs_secondary_output[codes_list_techs_secondary[n]]
    for n2 in range(len(this_fuel_i_list)):
        this_fuel_i = this_fuel_i_list[n2]
        this_fuel_o = this_fuel_o_list[n2]
        if this_fuel_i not in this_complete_fuel_i:
            this_complete_fuel_i.append(this_fuel_i)
        if this_fuel_o not in this_complete_fuel_o:
            this_complete_fuel_o.append(this_fuel_o)

# print('Review the lists of fuels matching each tech (2)')
# sys.exit()

for n in range(len(codes_list_techs_secondary)):
    this_tech_names = secondary_techs_names_eng[n]
    this_tech = codes_list_techs_secondary[n]

    this_fuel_i_list = codes_dict_techs_secondary_input[this_tech]
    this_fuel_o_list = codes_dict_techs_secondary_output[this_tech]
    '''
    These lists are of the same lenght.
    '''
    repeat_input = []
    repeat_output = []

    for n2 in range(len(this_fuel_i_list)):
        this_fuel_i = this_fuel_i_list[n2]
        this_fuel_i_name = secondary_i_fuels_names_eng[this_tech][n2]

        this_fuel_o = this_fuel_o_list[n2]
        this_fuel_o_name = secondary_o_fuels_names_eng[this_tech][n2]

        df_techs_secondary_base_year = df_techs_secondary_base_year.append({\
            'Fuel.I'        : this_fuel_i                   ,
            'Fuel.I.Name'   : this_fuel_i_name              ,
            'Value.Fuel.I'  : 1 , # This should be filled by the user
            'Tech'          : codes_list_techs_secondary[n] ,
            'Tech.Name'     : this_tech_names               ,
            'Fuel.O'        : this_fuel_o                   ,
            'Fuel.O.Name'   : this_fuel_o_name              ,
            'Value.Fuel.O'  : 1 # This should be filled by the user
            }, ignore_index=True)

        if this_fuel_i not in repeat_input:
            repeat_input.append(this_fuel_i)
            df_techs_secondary_projection = \
                df_techs_secondary_projection.append({
                'Tech'                  : codes_list_techs_secondary[n]     ,
                'Tech.Name'             : this_tech_names                   ,
                'Fuel'                  : this_fuel_i                       ,
                'Fuel.Name'             : this_fuel_i_name                  ,
                'Direction'             : 'Input',
                'Projection.Mode'       : '',
                'Projection.Parameter'  : 0 # This should be filled by the user
                }, ignore_index=True)

        if this_fuel_o not in repeat_output:
            repeat_output.append(this_fuel_o)
            df_techs_secondary_projection = \
                df_techs_secondary_projection.append({
                'Tech'                  : codes_list_techs_secondary[n]     ,
                'Tech.Name'             : this_tech_names                   ,
                'Fuel'                  : this_fuel_o                       ,
                'Fuel.Name'             : this_fuel_o_name                  ,
                'Direction'             : 'Output',
                'Projection.Mode'       : '',
                'Projection.Parameter'  : 0 # This should be filled by the user
                }, ignore_index=True)

df_techs_secondary_projection = \
    df_techs_secondary_projection.replace(np.nan, '', regex=True)


# print('Review the lists of fuels matching each tech (3)')
# sys.exit()

#-----------------------------------------------------------------------------#
# C - Let's now take the elements for the demand of simple methods:
df_techs_demand_base_year_HEADER = [\
    'Fuel.I', 'Fuel.I.Name', 'Value.Fuel.I', 'Unit.Fuel.I', 'Tech',
    'Tech.Name', 'Fuel.O', 'Fuel.O.Name', 'Value.Fuel.O', 'Unit.Fuel.O']
df_techs_demand_projection_HEADER = [\
    'Tech', 'Tech.Name', 'Fuel', 'Fuel.Name', 'Direction', 'Projection.Mode',
    'Projection.Parameter'] + time_range_vector

df_techs_demand_base_year = \
    pd.DataFrame(columns = df_techs_demand_base_year_HEADER)
df_techs_demand_projection = \
    pd.DataFrame(columns = df_techs_demand_projection_HEADER)

for n in range(len(codes_list_techs_demands)):
    this_tech_names = techs_demand_simple_eng[n]

    this_fuel_i = codes_dict_techs_demands_input[codes_list_techs_demands[n]]
    this_fuel_i_name_index = '' # this should be completed later
    this_fuel_i_name = '' # this should be completed later

    this_fuel_o = codes_dict_techs_demands_output[codes_list_techs_demands[n]]
    this_fuel_o_name_index = demands_simple.index(this_fuel_o)
    this_fuel_o_name = demands_simple_eng[this_fuel_o_name_index]

    df_techs_demand_base_year = df_techs_demand_base_year.append({\
        'Fuel.I'        : this_fuel_i                   ,
        'Fuel.I.Name'   : this_fuel_i_name              ,
        'Value.Fuel.I'  : 1 , # This should be filled by the user
        'Tech'          : techs_demand_simple[n] ,
        'Tech.Name'     : this_tech_names               ,
        'Fuel.O'        : this_fuel_o                   ,
        'Fuel.O.Name'   : this_fuel_o_name              ,
        'Value.Fuel.O'  : 1 # This should be filled by the user
        }, ignore_index=True)

    df_techs_demand_projection = df_techs_demand_projection.append({\
        'Tech'                  : techs_demand_simple[n]     ,
        'Tech.Name'             : this_tech_names                   ,
        'Fuel'                  : this_fuel_i                       ,
        'Fuel.Name'             : this_fuel_i_name                  ,
        'Direction'             : 'Input',
        'Projection.Mode'       : '',
        'Projection.Parameter'  : 0 # This should be filled by the user
        }, ignore_index=True)

    df_techs_demand_projection = df_techs_demand_projection.append({\
        'Tech'                  : techs_demand_simple[n]     ,
        'Tech.Name'             : this_tech_names                   ,
        'Fuel'                  : this_fuel_o                       ,
        'Fuel.Name'             : this_fuel_o_name                  ,
        'Direction'             : 'Output',
        'Projection.Mode'       : '',
        'Projection.Parameter'  : 0 # This should be filled by the user
        }, ignore_index=True)

    df_demands_all = df_demands_all.append({\
        'Ref.Cap.BY'            : 'not needed'      ,
        'Ref.OAR.BY'            : 'not needed'      ,
        'Ref.km.BY'             : 'not needed'      ,
        'Demand/Share'          : 'Demand'          ,
        'Fuel/Tech'             : this_fuel_o       ,
        'Name'                  : this_fuel_o_name  ,
        'Projection.Mode'       : ''                ,
        'Projection.Parameter'  : 0
        }, ignore_index=True)

df_techs_demand_projection = \
    df_techs_demand_projection.replace(np.nan, '', regex=True)
df_demands_all = df_demands_all.replace(np.nan, '', regex=True)

#---------------------------------------------------------------------------------------------------------------------------------#
# D - Let's now take the elements of the fuel distribution elements of transport
df_techs_DISTTRN_base_year_HEADER = [\
    'Fuel.I', 'Fuel.I.Name', 'Value.Fuel.I', 'Unit.Fuel.I', 'Tech',
    'Tech.Name', 'Fuel.O', 'Fuel.O.Name', 'Value.Fuel.O', 'Unit.Fuel.O']
df_techs_DISTTRN_projection_HEADER = [\
    'Tech', 'Tech.Name', 'Fuel', 'Fuel.Name', 'Direction',
    'Projection.Mode', 'Projection.Parameter'] + time_range_vector

df_techs_DISTTRN_base_year = pd.DataFrame(columns=df_techs_DISTTRN_base_year_HEADER)
df_techs_DISTTRN_projection = pd.DataFrame(columns=df_techs_DISTTRN_projection_HEADER)

for n in range(len(codes_list_techs_DISTTRN)):
    this_tech_names = sp_trn_techs_dist_eng[n]

    this_fuel_i = codes_list_techs_DISTTRN_input[codes_list_techs_DISTTRN[n]]
    this_fuel_i_name_index = '' # this should be completed later
    this_fuel_i_name = '' # this should be completed later

    this_fuel_o = codes_list_techs_DISTTRN_output[codes_list_techs_DISTTRN[n]]
    this_fuel_o_name_index = sp_trn_fuel_dist.index(this_fuel_o) # this should be completed later
    this_fuel_o_name = sp_trn_fuel_dist_eng[this_fuel_o_name_index] # this should be completed later

    df_techs_DISTTRN_base_year = df_techs_DISTTRN_base_year.append({\
        'Fuel.I'        : this_fuel_i                   ,
        'Fuel.I.Name'   : this_fuel_i_name              ,
        'Value.Fuel.I'  : 1 , # This should be filled by the user
        'Tech'          : codes_list_techs_DISTTRN[n] ,
        'Tech.Name'     : this_tech_names               ,
        'Fuel.O'        : this_fuel_o                   ,
        'Fuel.O.Name'   : this_fuel_o_name              ,
        'Value.Fuel.O'  : 1 # This should be filled by the user
        }, ignore_index=True)

    df_techs_DISTTRN_projection = df_techs_DISTTRN_projection.append({\
        'Tech'                  : codes_list_techs_DISTTRN[n]     ,
        'Tech.Name'             : this_tech_names                   ,
        'Fuel'                  : this_fuel_i                       ,
        'Fuel.Name'             : this_fuel_i_name                  ,
        'Direction'             : 'Input',
        'Projection.Mode'       : '',
        'Projection.Parameter'  : 0 # This should be filled by the user
        }, ignore_index=True)

    df_techs_DISTTRN_projection = df_techs_DISTTRN_projection.append({\
        'Tech'                  : codes_list_techs_DISTTRN[n]     ,
        'Tech.Name'             : this_tech_names                   ,
        'Fuel'                  : this_fuel_o                       ,
        'Fuel.Name'             : this_fuel_o_name                  ,
        'Direction'             : 'Output',
        'Projection.Mode'       : '',
        'Projection.Parameter'  : 0 # This should be filled by the user
        }, ignore_index=True)

df_techs_DISTTRN_projection = \
    df_techs_DISTTRN_projection.replace(np.nan, '', regex=True)

#---------------------------------------------------------------------------------------------------------------------------------#
# E - Let's now take the elements of vehicle techs
df_techs_TRN_base_year_HEADER = [\
    'Fuel.I.1', 'Fuel.I.1.Name', 'Value.Fuel.I.1', 'Unit.Fuel.I.1','Fuel.I.2',
    'Fuel.I.2.Name', 'Value.Fuel.I.2', 'Unit.Fuel.I.2', 'Tech', 'Tech.Name',
    'Fuel.O', 'Fuel.O.Name', 'Value.Fuel.O', 'Unit.Fuel.O']
df_techs_TRN_projection_HEADER = [\
    'Tech', 'Tech.Name', 'Fuel', 'Fuel.Name', 'Direction',
    'Projection.Mode', 'Projection.Parameter'] + time_range_vector

df_techs_TRN_base_year = pd.DataFrame(columns=df_techs_TRN_base_year_HEADER)
df_techs_TRN_projection = pd.DataFrame(columns=df_techs_TRN_projection_HEADER)

for n in range(len(codes_list_techs_TRN)):
    this_tech_names = sp_trn_techs_names_eng[n]

    this_fuel_i = codes_list_techs_TRN_input[codes_list_techs_TRN[n]]
    if len( this_fuel_i) >= 1:
        this_fuel_i_1 = this_fuel_i[0]
        this_fuel_i_1_name_index = '' # this should be completed later // sp_trn_fuel_dist.index(this_fuel_i)
        this_fuel_i_1_name = '' # this should be completed later // sp_trn_fuel_dist_eng[this_fuel_i_name_index]

        this_fuel_i_2 = 'none'
        this_fuel_i_2_name_index = '' # this should be completed later // sp_trn_fuel_dist.index(this_fuel_i)
        this_fuel_i_2_name = '' # this should be completed later // sp_trn_fuel_dist_eng[this_fuel_i_name_index]

    if len( this_fuel_i) == 2:
        this_fuel_i_2 = this_fuel_i[1]

    this_fuel_o = codes_list_techs_TRN_output[codes_list_techs_TRN[n]]
    this_fuel_o_name_index = '' # this should be completed later
    this_fuel_o_name = '' # this should be completed later

    df_techs_TRN_base_year = df_techs_TRN_base_year.append({\
        'Fuel.I.1'      : this_fuel_i_1                 ,
        'Fuel.I.1.Name' : this_fuel_i_1_name            ,
        'Value.Fuel.I.1': 0 , # This should be filled by the user
        'Fuel.I.2'      : this_fuel_i_2                 ,
        'Fuel.I.2.Name' : this_fuel_i_2_name            ,
        'Value.Fuel.I.2': 0 , # This should be filled by the user
        'Tech'          : codes_list_techs_TRN[n] ,
        'Tech.Name'     : this_tech_names               ,
        'Fuel.O'        : this_fuel_o                   ,
        'Fuel.O.Name'   : this_fuel_o_name              ,
        'Value.Fuel.O'  : 1 # This should be filled by the user
        }, ignore_index=True)
    #
    df_techs_TRN_projection = df_techs_TRN_projection.append({\
        'Tech'                  : codes_list_techs_TRN[n]           ,
        'Tech.Name'             : this_tech_names                   ,
        'Fuel'                  : this_fuel_i_1                     ,
        'Fuel.Name'             : this_fuel_i_1_name                ,
        'Direction'             : 'Input',
        'Projection.Mode'       : '',
        'Projection.Parameter'  : 0 # This should be filled by the user
        }, ignore_index=True)

    if len( this_fuel_i) == 2:
        df_techs_TRN_projection = df_techs_TRN_projection.append({\
            'Tech'                  : codes_list_techs_TRN[n]           ,
            'Tech.Name'             : this_tech_names                   ,
            'Fuel'                  : this_fuel_i_2                     ,
            'Fuel.Name'             : this_fuel_i_2_name                ,
            'Direction'             : 'Input',
            'Projection.Mode'       : '',
            'Projection.Parameter'  : 0 # This should be filled by the user
            }, ignore_index=True)

    df_techs_TRN_projection = df_techs_TRN_projection.append({\
        'Tech'                  : codes_list_techs_TRN[n]     ,
        'Tech.Name'             : this_tech_names                   ,
        'Fuel'                  : this_fuel_o                       ,
        'Fuel.Name'             : this_fuel_o_name                  ,
        'Direction'             : 'Output',
        'Projection.Mode'       : '',
        'Projection.Parameter'  : 0 # This should be filled by the user
        }, ignore_index=True)

df_techs_TRN_projection = \
    df_techs_TRN_projection.replace(np.nan, '', regex=True)

#---------------------------------------------------------------------------------------------------------------------------------#
# F - Let's now take the elements of group vehcile techs
df_techs_TRNGROUP_base_year_HEADER = [\
    'Fuel.I', 'Fuel.I.Name', 'Value.Fuel.I', 'Unit.Fuel.I', 'Tech',
    'Tech.Name', 'Fuel.O', 'Fuel.O.Name', 'Value.Fuel.O', 'Unit.Fuel.O']
df_techs_TRNGROUP_projection_HEADER = [\
    'Tech', 'Tech.Name', 'Fuel', 'Fuel.Name', 'Direction',
    'Projection.Mode', 'Projection.Parameter'] + time_range_vector

df_techs_TRNGROUP_base_year = pd.DataFrame(columns=df_techs_TRNGROUP_base_year_HEADER)
df_techs_TRNGROUP_projection = pd.DataFrame(columns=df_techs_TRNGROUP_projection_HEADER)

for n in range(len(codes_list_techs_TRNGROUP)):
    #
    this_tech_names = sp_trn_group_techs_names_eng[n] # this should be completed later
    #
    this_fuel_i = codes_list_techs_TRNGROUP_input[codes_list_techs_TRNGROUP[n]]
    this_fuel_i_name_index = '' # this should be completed later
    this_fuel_i_name = '' # this should be completed later
    #
    this_fuel_o = codes_list_techs_TRNGROUP_output[codes_list_techs_TRNGROUP[n]]
    this_fuel_o_name_index = sp_trn_dem_to_code_Code.index(this_fuel_o)
    this_fuel_o_name = sp_trn_dem_to_code_names_eng[this_fuel_o_name_index]
    #
    df_techs_TRNGROUP_base_year = df_techs_TRNGROUP_base_year.append({\
        'Fuel.I'        : this_fuel_i                   ,
        'Fuel.I.Name'   : this_fuel_i_name              ,
        'Value.Fuel.I'  : 1 , # This should be filled by the user
        'Tech'          : codes_list_techs_TRNGROUP[n] ,
        'Tech.Name'     : this_tech_names               ,
        'Fuel.O'        : this_fuel_o                   ,
        'Fuel.O.Name'   : this_fuel_o_name              ,
        'Value.Fuel.O'  : 1 # This should be filled by the user
        }, ignore_index=True)

    df_techs_TRNGROUP_projection = df_techs_TRNGROUP_projection.append({\
        'Tech'                  : codes_list_techs_TRNGROUP[n]     ,
        'Tech.Name'             : this_tech_names                   ,
        'Fuel'                  : this_fuel_i                       ,
        'Fuel.Name'             : this_fuel_i_name                  ,
        'Direction'             : 'Input',
        'Projection.Mode'       : '',
        'Projection.Parameter'  : 0 # This should be filled by the user
        }, ignore_index=True)

    df_techs_TRNGROUP_projection = df_techs_TRNGROUP_projection.append({\
        'Tech'                  : codes_list_techs_TRNGROUP[n]      ,
        'Tech.Name'             : this_tech_names                   ,
        'Fuel'                  : this_fuel_o                       ,
        'Fuel.Name'             : this_fuel_o_name                  ,
        'Direction'             : 'Output',
        'Projection.Mode'       : '',
        'Projection.Parameter'  : 0 # This should be filled by the user
        }, ignore_index=True)

    if this_fuel_o not in df_demands_fuel_list: # we need this because it is repeated
        df_demands_fuel_list.append(this_fuel_o)
        df_demands_all = df_demands_all.append({\
            'Demand/Share'          : 'Demand'          ,
            'Fuel/Tech'             : this_fuel_o       ,
            'Name'                  : this_fuel_o_name  ,
            'Projection.Mode'       : ''                ,
            'Projection.Parameter'  : 0
            }, ignore_index=True)
    df_demands_all = df_demands_all.append({\
        'Demand/Share'          : 'Share'                       ,
        'Fuel/Tech'             : codes_list_techs_TRNGROUP[n]  ,
        'Name'                  : this_tech_names               ,
        'Projection.Mode'       : ''                            ,
        'Projection.Parameter'  : 0
        }, ignore_index=True)

df_techs_TRNGROUP_projection = df_techs_TRNGROUP_projection.replace(np.nan, '', regex=True)
df_demands_all = df_demands_all.replace(np.nan, '', regex=True)

tech_param_list_all_notyearly_df = tech_param_list_all_notyearly_df.replace(np.nan, '', regex=True)

tech_param_list_yearly_primary_df = tech_param_list_yearly_primary_df.replace(np.nan, '', regex=True)
tech_param_list_yearly_secondary_df = tech_param_list_yearly_secondary_df.replace(np.nan, '', regex=True)
tech_param_list_yearly_demands_df = tech_param_list_yearly_demands_df.replace(np.nan, '', regex=True)
tech_param_list_yearly_disttrn_df = tech_param_list_yearly_disttrn_df.replace(np.nan, '', regex=True)
tech_param_list_yearly_trn_df = tech_param_list_yearly_trn_df.replace(np.nan, '', regex=True)
tech_param_list_yearly_trngroups_df = tech_param_list_yearly_trngroups_df.replace(np.nan, '', regex=True)

tech_param_list_dfs = [tech_param_list_all_notyearly_df, tech_param_list_yearly_primary_df ,
                        tech_param_list_yearly_secondary_df, tech_param_list_yearly_demands_df ,
                        tech_param_list_yearly_disttrn_df, tech_param_list_yearly_trn_df, tech_param_list_yearly_trngroups_df]
tech_param_list_dfs_names = [\
    'Fixed Horizon Parameters', 'Primary Techs', 'Secondary Techs', 
    'Demand Techs', 'Transport Fuel Distribution', 'Vehicle Techs',
    'Vehicle Groups']

#---------------------------------------------------------------------------------------------------------------------------------#

# sys.exit()

# We must now print, because we need an interface with the system:
#   NOTE: https://stackoverflow.com/questions/22089317/export-from-pandas-to-excel-without-row-names-index

# Print the Base Year "Activity Ratio", that puts the units.
writer_df_baseyear = pd.ExcelWriter("./A1_Outputs/A-O_AR_Model_Base_Year.xlsx", engine='xlsxwriter') # These are activity ratios // we should add the units.
df_base_year_list = [  df_techs_primary_base_year, df_techs_secondary_base_year, df_techs_demand_base_year,
                        df_techs_DISTTRN_base_year, df_techs_TRN_base_year, df_techs_TRNGROUP_base_year]
df_base_year_names = ['Primary', 'Secondary', 'Demand Techs', 'Distribution Transport', 'Transport', 'Transport Groups']
for n in range(len(df_base_year_names)):
    this_df = df_base_year_list[n]
    this_df_sheet_name = df_base_year_names[n]
    this_df.to_excel(writer_df_baseyear,sheet_name = this_df_sheet_name, index=False)
writer_df_baseyear.save()

# Print the Projection "Activity Ratio", without the units.
writer_df_projection = pd.ExcelWriter("./A1_Outputs/A-O_AR_Projections.xlsx", engine='xlsxwriter') # These are activity ratios // we should add the units.
df_projection_list = [  df_techs_primary_projection, df_techs_secondary_projection, df_techs_demand_projection,
                        df_techs_DISTTRN_projection, df_techs_TRN_projection, df_techs_TRNGROUP_projection]
df_projection_names = ['Primary', 'Secondary', 'Demand Techs', 'Distribution Transport', 'Transport', 'Transport Groups']
for n in range(len(df_projection_names)):
    this_df = df_projection_list[n]
    this_df_sheet_name = df_projection_names[n]
    this_df.to_excel(writer_df_projection,sheet_name = this_df_sheet_name, index=False)
writer_df_projection.save()

# REMEMBER to apply this: https://support.microsoft.com/en-us/office/change-the-column-width-and-row-height-72f5e3cc-994d-43e8-ae58-9774a0905f46

'''
-------------------------------------------------------------------------------------------------------------
With that done, we now need to print the final demands. This is crucial for parameterization.
'''
writer_df_demand = pd.ExcelWriter("./A1_Outputs/A-O_Demand.xlsx", engine='xlsxwriter') # These are activity ratios // we should add the units.
this_df_sheet_name = 'Demand_Projection'
df_demands_all.to_excel(writer_df_demand, sheet_name = this_df_sheet_name, index=False)
writer_df_demand.save()

'''
-------------------------------------------------------------------------------------------------------------
With that done, we must print the distribution of trips per mode for the transport sector, as well as capacities.
'''
writer_df_parameters = pd.ExcelWriter("./A1_Outputs/A-O_Parametrization.xlsx", engine='xlsxwriter') # These are activity ratios // we should add the units.
for n in range(len(tech_param_list_dfs_names)):
    this_df = tech_param_list_dfs[n]
    this_df_sheet_name = tech_param_list_dfs_names[n]
    this_df.to_excel(writer_df_parameters, sheet_name = this_df_sheet_name, index=False)
writer_df_parameters.save()

'''
-------------------------------------------------------------------------------------------------------------
Because it will be convinient later, let us group the technologies between group and vehicle.
'''
codes_list_techs_TRNGROUP_dict = {}
codes_list_techs_TRNGROUP_input_dict = {}
for n in range(len(codes_list_techs_TRNGROUP)):
    codes_list_techs_TRNGROUP_dict.update({codes_list_techs_TRNGROUP[n]:[]})
    codes_list_techs_TRNGROUP_input_dict.update({codes_list_techs_TRNGROUP_input[codes_list_techs_TRNGROUP[n]]:codes_list_techs_TRNGROUP[n]})

for n in range(len(codes_list_techs_TRN)):
    the_group_tech = codes_list_techs_TRNGROUP_input_dict[codes_list_techs_TRN_output[codes_list_techs_TRN[n]]]
    codes_list_techs_TRNGROUP_dict[the_group_tech].append(codes_list_techs_TRN[n])

df_techs_fleet_HEADER   = [    'Group.ID', 'Group/Vehicle', 'Techs', 'Description',
                                'Fleet Unit', 'Base Year', 'Base Year Value'
                               ]

df_techs_fleet = pd.DataFrame(columns=df_techs_fleet_HEADER)

for n in range(len(codes_list_techs_TRNGROUP)):
    trn_group_list = codes_list_techs_TRNGROUP_dict[codes_list_techs_TRNGROUP[n]]
    df_techs_fleet = df_techs_fleet.append({\
        'Group.ID'          : n+1                               ,
        'Group/Vehicle'     : 'Group'                           ,
        'Techs'             : codes_list_techs_TRNGROUP[n]      ,
        'Description'       : sp_trn_group_techs_names_eng[n]   ,
        'Fleet Unit'        : 'Unidades'
        }, ignore_index=True)

    for n2 in range(len(trn_group_list)):
        codes_list_techs_TRN_index = codes_list_techs_TRN.index(trn_group_list[n2])
        df_techs_fleet = df_techs_fleet.append({\
            'Group.ID'          : n+1                                                   ,
            'Group/Vehicle'     : 'Vehicle'                                             ,
            'Techs'             : trn_group_list[n2]                                    ,
            'Description'       : sp_trn_techs_names_eng[codes_list_techs_TRN_index]  ,
            'Fleet Unit'        : 'Unidades'
            }, ignore_index=True)

with open( './A1_Outputs/A-O_Fleet_Groups.pickle', 'wb') as handle0:
    pickle.dump(codes_list_techs_TRNGROUP_dict, handle0, protocol=pickle.HIGHEST_PROTOCOL)

writer_df_fleet = pd.ExcelWriter("./A1_Outputs/A-O_Fleet.xlsx", engine='xlsxwriter') # These are activity ratios // we should add the units.
this_df_sheet_name = 'Calibration_Fleet'
df_techs_fleet.to_excel(writer_df_fleet, sheet_name = this_df_sheet_name, index=False)
writer_df_fleet.save()

'''
-------------------------------------------------------------------------------------------------------------
'''
end_1 = time.time()   
time_elapsed_1 = -start1 + end_1
print(str(time_elapsed_1) + ' seconds /', str( time_elapsed_1/60) + ' minutes')
print('*: For all effects, we have finished the work of this script.')

log_file = open("./A1_Outputs/Log.txt","w")
today = date.today()
hour = time.strftime("%H")
minute = time.strftime("%M")
str1 = 'Esta versión se produjo el ' + str(today) + ' a las ' + hour + ':' + minute
log_file.write(str1)
log_file.close()

