# -*- coding: utf-8 -*-
"""
Created on Wed Jun  9 17:23:30 2021

@author: luisf
"""

'''
Objective: in some rare cases, the restrictions of power plant capacity are
incompatible with a specific demand, e.g., H2 production.

In these cases, increasing the "TotalAnnualMaxCapacity" is a good solution.

Here we "clean up" the existing runs to avoid re-running the entire experiment
if the only problem is the restriction management.
'''


import os, os.path
import multiprocessing as mp
import errno
import scipy
from scipy import stats
import pandas as pd
import numpy as np
import xlrd
import csv
import os, os.path
import sys
import math
from copy import deepcopy
import time
import re
import linecache
import gc
import shutil
import pickle


def set_first_list(Executed_Scenario):
    dir_of_interest = \
        './Experimental_Platform/Futures/' + str(Executed_Scenario)
    first_list_raw = os.listdir(dir_of_interest)

    first_list = [e for e in first_list_raw if ('.csv' not in e) and
                  ('Table' not in e) and ('.py' not in e) and
                  ('__pycache__' not in e)]
    return first_list, dir_of_interest


def data_processor( case, Executed_Scenario, unpackaged_useful_elements ):
    #
    Reference_driven_distance =     unpackaged_useful_elements[0]
    Reference_occupancy_rate =      unpackaged_useful_elements[1]
    Fleet_Groups_inv =              unpackaged_useful_elements[2]
    time_range_vector =             unpackaged_useful_elements[3]
    dict_gdp_ref      =             unpackaged_useful_elements[4]
    #
    # Briefly open up the system coding to use when processing for visualization:
    df_fuel_to_code = pd.read_excel( './0_From_Confection/A-I_Classifier_Modes_Transport.xlsx', sheet_name='Fuel_to_Code' )
    df_fuel_2_code_fuel_list        = df_fuel_to_code['Code'].tolist()
    df_fuel_2_code_plain_english    = df_fuel_to_code['Plain_English'].tolist()
    df_tech_to_code = pd.read_excel( './0_From_Confection/A-I_Classifier_Modes_Transport.xlsx', sheet_name='Tech_to_Code' )
    df_tech_2_code_fuel_list        = df_tech_to_code['Techs'].tolist()
    df_tech_2_code_plain_english    = df_tech_to_code['Plain_English'].tolist()
    #
    # 1 - Always call the structure for the model:
    #-------------------------------------------#
    structure_filename = "./0_From_Confection/B1_Model_Structure.xlsx"
    structure_file = pd.ExcelFile(structure_filename)
    structure_sheetnames = structure_file.sheet_names  # see all sheet names
    sheet_sets_structure = pd.read_excel(open(structure_filename, 'rb'),
                                         header=None,
                                         sheet_name=structure_sheetnames[0])
    sheet_params_structure = pd.read_excel(open(structure_filename, 'rb'),
                                           header=None,
                                           sheet_name=structure_sheetnames[1])
    sheet_vars_structure = pd.read_excel(open(structure_filename, 'rb'),
                                         header=None,
                                         sheet_name=structure_sheetnames[2])

    S_DICT_sets_structure = {'set':[],'initial':[],'number_of_elements':[],'elements_list':[]}
    for col in range(1,11+1):  # 11 columns
        S_DICT_sets_structure['set'].append( sheet_sets_structure.iat[0, col] )
        S_DICT_sets_structure['initial'].append( sheet_sets_structure.iat[1, col] )
        S_DICT_sets_structure['number_of_elements'].append( int( sheet_sets_structure.iat[2, col] ) )
        #
        element_number = int( sheet_sets_structure.iat[2, col] )
        this_elements_list = []
        if element_number > 0:
            for n in range( 1, element_number+1 ):
                this_elements_list.append( sheet_sets_structure.iat[2+n, col] )
        S_DICT_sets_structure['elements_list'].append( this_elements_list )
    #
    S_DICT_params_structure = {'category':[],'parameter':[],'number_of_elements':[],'index_list':[]}
    param_category_list = []
    for col in range(1,30+1):  # 30 columns
        if str( sheet_params_structure.iat[0, col] ) != '':
            param_category_list.append( sheet_params_structure.iat[0, col] )
        S_DICT_params_structure['category'].append( param_category_list[-1] )
        S_DICT_params_structure['parameter'].append( sheet_params_structure.iat[1, col] )
        S_DICT_params_structure['number_of_elements'].append( int( sheet_params_structure.iat[2, col] ) )
        #
        index_number = int( sheet_params_structure.iat[2, col] )
        this_index_list = []
        for n in range(1, index_number+1):
            this_index_list.append( sheet_params_structure.iat[2+n, col] )
        S_DICT_params_structure['index_list'].append( this_index_list )
    #
    S_DICT_vars_structure = {'category':[],'variable':[],'number_of_elements':[],'index_list':[]}
    var_category_list = []
    for col in range(1,43+1):  # 43 columns
        if str( sheet_vars_structure.iat[0, col] ) != '':
            var_category_list.append( sheet_vars_structure.iat[0, col] )
        S_DICT_vars_structure['category'].append( var_category_list[-1] )
        S_DICT_vars_structure['variable'].append( sheet_vars_structure.iat[1, col] )
        S_DICT_vars_structure['number_of_elements'].append( int( sheet_vars_structure.iat[2, col] ) )
        #
        index_number = int( sheet_vars_structure.iat[2, col] )
        this_index_list = []
        for n in range(1, index_number+1):
            this_index_list.append( sheet_vars_structure.iat[2+n, col] )
        S_DICT_vars_structure['index_list'].append( this_index_list )
    #-------------------------------------------#
    all_vars = ['Demand',
                'NewCapacity',
                'AccumulatedNewCapacity',
                'TotalCapacityAnnual',
                # 'TotalTechnologyAnnualActivity',
                'ProductionByTechnology',
                'UseByTechnology',
                'CapitalInvestment',
                # 'DiscountedCapitalInvestment',
                # 'SalvageValue',
                # 'DiscountedSalvageValue',
                'OperatingCost',
                # 'DiscountedOperatingCost',
                'AnnualVariableOperatingCost',
                'AnnualFixedOperatingCost',
                # 'TotalDiscountedCostByTechnology',
                # 'TotalDiscountedCost',
                'AnnualTechnologyEmission',
                # 'AnnualTechnologyEmissionPenaltyByEmission'
                # 'AnnualTechnologyEmissionsPenalty',
                # 'DiscountedTechnologyEmissionsPenalty',
                # 'AnnualEmissions'
                ]
    #
    more_vars = [   'DistanceDriven',
                    'Fleet',
                    'NewFleet',
                    'ProducedMobility']
    #
    filter_vars = [ 'FilterFuelType',
                    'FilterVehicleType',
                    # 'DiscountedTechnEmissionsPen',
                    #
                    'Capex2023', # CapitalInvestment
                    'FixedOpex2023', # AnnualFixedOperatingCost
                    'VarOpex2023', # AnnualVariableOperatingCost
                    'Opex2023', # OperatingCost
                    'Externalities2023', # AnnualTechnologyEmissionPenaltyByEmission
                    #
                    'Capex_GDP', # CapitalInvestment
                    'FixedOpex_GDP', # AnnualFixedOperatingCost
                    'VarOpex_GDP', # AnnualVariableOperatingCost
                    'Opex_GDP', # OperatingCost
                    'Externalities_GDP' # AnnualTechnologyEmissionPenaltyByEmission
                    ]
    #
    first_list, dir_of_interest = set_first_list( Executed_Scenario )
    all_vars_output_dict = [ {} for e in range( len( first_list ) ) ]
    #
    output_header = [ 'Strategy', 'Future.ID','Fuel','Technology','Emission','Year']
    #-------------------------------------------------------#
    for v in range( len( all_vars ) ):
        output_header.append( all_vars[v] )
    for v in range( len( more_vars ) ):
        output_header.append( more_vars[v] )
    for v in range( len( filter_vars ) ):
        output_header.append( filter_vars[v] )
    #-------------------------------------------------------#
    this_strategy = first_list[case].split('_')[0] 
    this_future   = first_list[case].split('_')[1]
    list_gdp_ref = dict_gdp_ref[int(this_future)]
    #-------------------------------------------------------#
    #
    vars_as_appear = []
    data_name = str( './Experimental_Platform/Futures/' + str( Executed_Scenario ) + '/' + first_list[case] ) + '/' + str(first_list[case]) + '_output.txt'
    #
    n = 0
    break_this_while = False
    while break_this_while == False:
        n += 1
        structure_line_raw = linecache.getline(data_name, n)
        if 'No. Column name  St   Activity     Lower bound   Upper bound    Marginal' in structure_line_raw:
            ini_line = deepcopy( n+2 )
        if 'Karush-Kuhn-Tucker' in structure_line_raw:
            end_line = deepcopy( n-1 )
            break_this_while = True
            break
    #
    for n in range(ini_line, end_line, 2 ):
        structure_line_raw = linecache.getline(data_name, n)
        structure_list_raw = structure_line_raw.split(' ')
        #
        structure_list_raw_2 = [ s_line for s_line in structure_list_raw if s_line != '' ]
        structure_line = structure_list_raw_2[1]
        structure_list = structure_line.split('[')
        the_variable = structure_list[0]
        #
        if the_variable in all_vars:
            set_list = structure_list[1].replace(']','').replace('\n','').split(',')
            #--%
            index = S_DICT_vars_structure['variable'].index( the_variable )
            this_variable_indices = S_DICT_vars_structure['index_list'][ index ]
            #
            #--%
            if 'y' in this_variable_indices:
                data_line = linecache.getline(data_name, n+1)
                data_line_list_raw = data_line.split(' ')
                data_line_list = [ data_cell for data_cell in data_line_list_raw if data_cell != '' ]
                useful_data_cell = data_line_list[1]
                #--%
                if useful_data_cell != '0':
                    #
                    if the_variable not in vars_as_appear:
                        vars_as_appear.append( the_variable )
                        all_vars_output_dict[case].update({ the_variable:{} })
                        all_vars_output_dict[case][the_variable].update({ the_variable:[] })
                        #
                        for n in range( len( this_variable_indices ) ):
                            all_vars_output_dict[case][the_variable].update( { this_variable_indices[n]:[] } )
                    #--%
                    this_variable = vars_as_appear[-1]
                    all_vars_output_dict[case][this_variable][this_variable].append( useful_data_cell )
                    for n in range( len( this_variable_indices ) ):
                        all_vars_output_dict[case][the_variable][ this_variable_indices[n] ].append( set_list[n] )
                #
            #
            elif 'y' not in this_variable_indices:
                data_line = linecache.getline(data_name, n+1)
                data_line_list_raw = data_line.split(' ')
                data_line_list = [ data_cell for data_cell in data_line_list_raw if data_cell != '' ]
                useful_data_cell = data_line_list[1]
                #--%
                if useful_data_cell != '0':
                    #
                    if the_variable not in vars_as_appear:
                        vars_as_appear.append( the_variable )
                        all_vars_output_dict[case].update({ the_variable:{} })
                        all_vars_output_dict[case][the_variable].update({ the_variable:[] })
                        #
                        for n in range( len( this_variable_indices ) ):
                            all_vars_output_dict[case][the_variable].update( { this_variable_indices[n]:[] } )
                    #--%
                    this_variable = vars_as_appear[-1]
                    all_vars_output_dict[case][this_variable][this_variable].append( useful_data_cell )
                    for n in range( len( this_variable_indices ) ):
                        all_vars_output_dict[case][the_variable][ this_variable_indices[n] ].append( set_list[n] )
        #--%
        else:
            pass
    #
    linecache.clearcache()
    #%%
    #-----------------------------------------------------------------------------------------------------------%
    output_adress = './Experimental_Platform/Futures/' + str( Executed_Scenario ) + '/' + str( first_list[case] )
    combination_list = [] # [fuel, technology, emission, year]
    data_row_list = []
    for var in range( len( vars_as_appear ) ):
        this_variable = vars_as_appear[var]
        this_var_dict = all_vars_output_dict[case][this_variable]
        #--%
        index = S_DICT_vars_structure['variable'].index( this_variable )
        this_variable_indices = S_DICT_vars_structure['index_list'][ index ]
        #--------------------------------------#
        for k in range( len( this_var_dict[this_variable] ) ):
            this_combination = []
            #
            if 'f' in this_variable_indices:
                this_combination.append( this_var_dict['f'][k] )
            else:
                this_combination.append( '' )
            #
            if 't' in this_variable_indices:
                this_combination.append( this_var_dict['t'][k] )
            else:
                this_combination.append( '' )
            #
            if 'e' in this_variable_indices:
                this_combination.append( this_var_dict['e'][k] )
            else:
                this_combination.append( '' )
            #
            if 'l' in this_variable_indices:
                this_combination.append( '' )
            else:
                this_combination.append( '' )
            #
            if 'y' in this_variable_indices:
                this_combination.append( this_var_dict['y'][k] )
            else:
                this_combination.append( '' )
            #
            if this_combination not in combination_list:
                combination_list.append( this_combination )
                data_row = ['' for n in range( len( output_header ) ) ]
                # print('check', len(data_row), len(run_id) )
                data_row[0] = this_strategy
                data_row[1] = this_future
                data_row[2] = this_combination[0] # Fuel
                data_row[3] = this_combination[1] # Technology
                data_row[4] = this_combination[2] # Emission
                # data_row[7] = this_combination[3]
                data_row[5] = this_combination[4] # Year
                #
                var_position_index = output_header.index( this_variable )
                data_row[ var_position_index ] = this_var_dict[ this_variable ][ k ]
                data_row_list.append( data_row )
            else:
                ref_index = combination_list.index( this_combination )
                this_data_row = deepcopy( data_row_list[ ref_index ] )
                #
                var_position_index = output_header.index( this_variable )
                #
                if 'l' in this_variable_indices: 
                    #
                    if str(this_data_row[ var_position_index ]) != '' and str(this_var_dict[ this_variable ][ k ]) != '' and ( 'Rate' not in this_variable ):
                        this_data_row[ var_position_index ] = str(  float( this_data_row[ var_position_index ] ) + float( this_var_dict[ this_variable ][ k ] ) )
                    elif str(this_data_row[ var_position_index ]) == '' and str(this_var_dict[ this_variable ][ k ]) != '':
                        this_data_row[ var_position_index ] = str( float( this_var_dict[ this_variable ][ k ] ) )
                    elif str(this_data_row[ var_position_index ]) != '' and str(this_var_dict[ this_variable ][ k ]) == '':
                        pass
                else:
                    this_data_row[ var_position_index ] = this_var_dict[ this_variable ][ k ]
                #
                data_row_list[ ref_index ]  = deepcopy( this_data_row )
                #
            #
            if this_variable == 'TotalTechnologyAnnualActivity' or this_variable == 'NewCapacity':
                ref_index = combination_list.index( this_combination )
                this_data_row = deepcopy( data_row_list[ ref_index ] ) # this must be updated in a further position of the list
                #
                this_tech = this_combination[1]
                if this_tech in list( Fleet_Groups_inv.keys() ):
                    group_tech = Fleet_Groups_inv[ this_tech ]
                    #
                    this_year = this_combination[4]
                    this_year_index = time_range_vector.index( int( this_year ) )
                    #
                    ref_var_position_index = output_header.index( this_variable )
                    #
                    if group_tech in ['TRNMIC', 'TRNBUS', 'TRNTAX', 'TRNMOT', 'TRNSED', 'TRNSUV', 'TRNCAM', 'TRNFREHEA', 'TRNFREMED', 'TRNFRELIG', 'TRNCATTRU']:
                        ''' Debug section start
                        '''
                        try:
                            driven_distance = float( Reference_driven_distance[ this_strategy ][int(this_future)][ group_tech ][ this_year_index ] )
                        except Exception:
                            print(this_strategy)
                            print(this_future)
                            print(group_tech)
                            print(this_year_index)
                            print('error here')
                        #
                        if group_tech not in ['TRNMIC', 'TRNSED', 'TRNSUV', 'TRNCAM']:
                            passenger_per_vehicle = 1
                        else:
                            try:
                                passenger_per_vehicle = float( Reference_occupancy_rate[ this_strategy ][int(this_future)][ group_tech ][ this_year_index ]  )
                            except Exception:
                                print(list(Reference_occupancy_rate[ this_strategy ][int(this_future)].keys()))
                                print('check alert')
                                sys.exit()
                        ''' Debug section end
                        '''
                        #
                        if this_variable == 'NewCapacity':
                            var_position_index = output_header.index( 'NewFleet' )
                            this_data_row[ var_position_index ] =  round( (10**9)*float( this_data_row[ ref_var_position_index ] )/driven_distance, 4)
                        #
                        if this_variable == 'TotalTechnologyAnnualActivity':
                            #
                            var_position_index = output_header.index( 'Fleet' )
                            this_data_row[ var_position_index ] =  round( (10**9)*float( this_data_row[ ref_var_position_index ] )/driven_distance, 4)
                            #
                            var_position_index = output_header.index( 'DistanceDriven' )
                            this_data_row[ var_position_index ] = round(driven_distance, 4)
                            #
                            var_position_index = output_header.index( 'ProducedMobility' )
                            this_data_row[ var_position_index ] =  round( float( this_data_row[ ref_var_position_index ] )*passenger_per_vehicle, 4)
                        #
                        data_row_list[ ref_index ] = deepcopy( this_data_row )
                        #
                    #
                    ###################################################################################################
                    #
                #
            #
            # Creating convinience filters for the analysis of model outputs:
            this_tech = this_combination[1]
            if this_tech in list( Fleet_Groups_inv.keys() ):
                ref_index = combination_list.index( this_combination )
                this_data_row = deepcopy( data_row_list[ ref_index ] ) # this must be updated in a further position of the list
                #
                var_position_index = output_header.index( 'FilterFuelType' )
                ############################################
                # By Fuel Type
                for r in range( len( df_fuel_2_code_fuel_list ) ):
                    if df_fuel_2_code_fuel_list[r] in this_tech:
                        this_data_row[ var_position_index ] = df_fuel_2_code_plain_english[ r ]
                        break
                ############################################
                var_position_index = output_header.index( 'FilterVehicleType' )
                # By vehicle type
                for r in range( len( df_tech_2_code_fuel_list ) ):
                    if df_tech_2_code_fuel_list[r] in this_tech:
                        this_data_row[ var_position_index ] = df_tech_2_code_plain_english[ r ]
                        break
                data_row_list[ ref_index ] = deepcopy( this_data_row )
            #
            output_csv_r = 0.05*100
            output_csv_year = 2023
            #
            if this_combination[2] in ['Accidents', 'Health', 'Congestion'] and this_variable == 'AnnualTechnologyEmissionPenaltyByEmission':
                ref_index = combination_list.index( this_combination )
                this_data_row = deepcopy( data_row_list[ ref_index ] ) # this must be updated in a further position of the list
                #
                ref_var_position_index = output_header.index( 'AnnualTechnologyEmissionPenaltyByEmission' )
                new_var_position_index = output_header.index( 'Externalities2023' )
                new2_var_position_index = output_header.index( 'Externalities_GDP' )
                #
                this_year = this_combination[4]
                this_year_index = time_range_vector.index( int( this_year ) )
                #
                resulting_value_raw = float(this_data_row[ ref_var_position_index ]) / ( ( 1 + output_csv_r/100 )**( float(this_year) - output_csv_year ) )
                resulting_value = round( resulting_value_raw, 4)
                #
                this_data_row[new_var_position_index] = str( resulting_value )
                this_data_row[new2_var_position_index] = str( float(this_data_row[ ref_var_position_index ])/list_gdp_ref[this_year_index] )
                #
                data_row_list[ ref_index ] = deepcopy( this_data_row )
                #
            #
            ''' $ This is new (beginning) $ '''
            #
            if this_variable == 'CapitalInvestment':
                ref_index = combination_list.index( this_combination )
                this_data_row = deepcopy( data_row_list[ ref_index ] ) # this must be updated in a further position of the list
                #
                ref_var_position_index = output_header.index( 'CapitalInvestment' )
                new_var_position_index = output_header.index( 'Capex2023' )
                new2_var_position_index = output_header.index( 'Capex_GDP' )
                #
                this_year = this_combination[4]
                this_year_index = time_range_vector.index( int( this_year ) )
                #
                # Here we must add an adjustment to the capital investment to make the fleet constant:
                this_cap_inv = float(this_data_row[ ref_var_position_index ])
                this_data_row[ref_var_position_index] = \
                    str(this_cap_inv)  # Here we re-write the new capacity to adjust the system
                #
                resulting_value_raw = this_cap_inv/((1 + output_csv_r/100)**(float(this_year) - output_csv_year))
                resulting_value = round( resulting_value_raw, 4)
                #
                this_data_row[new_var_position_index] = str( resulting_value )
                this_data_row[new2_var_position_index] = str( float(this_data_row[ ref_var_position_index ])/list_gdp_ref[this_year_index] )
                #
                data_row_list[ ref_index ] = deepcopy( this_data_row )
                #
            #
            if this_variable == 'AnnualFixedOperatingCost':
                ref_index = combination_list.index( this_combination )
                this_data_row = deepcopy( data_row_list[ ref_index ] ) # this must be updated in a further position of the list
                #
                ref_var_position_index = output_header.index( 'AnnualFixedOperatingCost' )
                new_var_position_index = output_header.index( 'FixedOpex2023' )
                new2_var_position_index = output_header.index( 'FixedOpex_GDP' )
                #
                this_year = this_combination[4]
                this_year_index = time_range_vector.index( int( this_year ) )
                #
                resulting_value_raw = float(this_data_row[ ref_var_position_index ]) / ( ( 1 + output_csv_r/100 )**( float(this_year) - output_csv_year ) )
                resulting_value = round( resulting_value_raw, 4)
                #
                this_data_row[new_var_position_index] = str( resulting_value )
                this_data_row[new2_var_position_index] = str( float(this_data_row[ ref_var_position_index ])/list_gdp_ref[this_year_index] )
                #
                data_row_list[ ref_index ] = deepcopy( this_data_row )
                #
            #
            if this_variable == 'AnnualVariableOperatingCost':
                ref_index = combination_list.index( this_combination )
                this_data_row = deepcopy( data_row_list[ ref_index ] ) # this must be updated in a further position of the list
                #
                ref_var_position_index = output_header.index( 'AnnualVariableOperatingCost' )
                new_var_position_index = output_header.index( 'VarOpex2023' )
                new2_var_position_index = output_header.index( 'VarOpex_GDP' )
                #
                this_year = this_combination[4]
                this_year_index = time_range_vector.index( int( this_year ) )
                #
                resulting_value_raw = float(this_data_row[ ref_var_position_index ]) / ( ( 1 + output_csv_r/100 )**( float(this_year) - output_csv_year ) )
                resulting_value = round( resulting_value_raw, 4)
                #
                this_data_row[new_var_position_index] = str( resulting_value )
                this_data_row[new2_var_position_index] = str( float(this_data_row[ ref_var_position_index ])/list_gdp_ref[this_year_index] )
                #
                data_row_list[ ref_index ] = deepcopy( this_data_row )
                #
            #
            if this_variable == 'OperatingCost':
                ref_index = combination_list.index( this_combination )
                this_data_row = deepcopy( data_row_list[ ref_index ] ) # this must be updated in a further position of the list
                #
                ref_var_position_index = output_header.index( 'OperatingCost' )
                new_var_position_index = output_header.index( 'Opex2023' )
                new2_var_position_index = output_header.index( 'Opex_GDP' )
                #
                this_year = this_combination[4]
                this_year_index = time_range_vector.index( int( this_year ) )
                #
                resulting_value_raw = float(this_data_row[ ref_var_position_index ]) / ( ( 1 + output_csv_r/100 )**( float(this_year) - output_csv_year ) )
                resulting_value = round( resulting_value_raw, 4)
                #
                this_data_row[new_var_position_index] = str( resulting_value )
                this_data_row[new2_var_position_index] = str( float(this_data_row[ ref_var_position_index ])/list_gdp_ref[this_year_index] )
                #
                data_row_list[ ref_index ] = deepcopy( this_data_row )
                #
            #
            ''' $ (end) $ '''
            #
        #
    #
    non_year_combination_list = []
    non_year_combination_list_years = []
    for n in range( len( combination_list ) ):
        this_combination = combination_list[ n ]
        this_non_year_combination = [ this_combination[0], this_combination[1], this_combination[2] ]
        if this_combination[4] != '' and this_non_year_combination not in non_year_combination_list:
            non_year_combination_list.append( this_non_year_combination )
            non_year_combination_list_years.append( [ this_combination[4] ] )
        elif this_combination[4] != '' and this_non_year_combination in non_year_combination_list:
            non_year_combination_list_years[ non_year_combination_list.index( this_non_year_combination ) ].append( this_combination[4] )
    #
    for n in range( len( non_year_combination_list ) ):
        if len( non_year_combination_list_years[n] ) != len(time_range_vector):
            #
            this_existing_combination = non_year_combination_list[n]
            this_existing_combination.append( '' )
            this_existing_combination.append( non_year_combination_list_years[n][0] )
            ref_index = combination_list.index( this_existing_combination )
            this_existing_data_row = deepcopy( data_row_list[ ref_index ] )
            #
            for n2 in range( len(time_range_vector) ):
                #
                if time_range_vector[n2] not in non_year_combination_list_years[n]:
                    #
                    data_row = ['' for n in range( len( output_header ) ) ]
                    data_row[0] = this_strategy
                    data_row[1] = this_future
                    data_row[2] = non_year_combination_list[n][0]
                    data_row[3] = non_year_combination_list[n][1]
                    data_row[4] = non_year_combination_list[n][2]
                    data_row[5] = time_range_vector[n2]
                    #
                    for n3 in range( len( vars_as_appear ) ):
                        this_variable = vars_as_appear[n3]
                        this_var_dict = all_vars_output_dict[case][this_variable]
                        index = S_DICT_vars_structure['variable'].index( this_variable )
                        this_variable_indices = S_DICT_vars_structure['index_list'][ index ]
                        #
                        var_position_index = output_header.index( this_variable )
                        #
                        print_true = False
                        #
                        if ( 'f' in this_variable_indices and str(non_year_combination_list[n][0]) != '' ): # or ( 'f' not in this_variable_indices and str(non_year_combination_list[n][0]) == '' ):
                            print_true = True
                        else:
                            pass
                        #
                        if ( 't' in this_variable_indices and str(non_year_combination_list[n][1]) != '' ): # or ( 't' not in this_variable_indices and str(non_year_combination_list[n][1]) == '' ):
                            print_true = True
                        else:
                            pass
                        #
                        if ( 'e' in this_variable_indices and str(non_year_combination_list[n][2]) != '' ): # or ( 'e' not in this_variable_indices and str(non_year_combination_list[n][2]) == '' ):
                            print_true = True
                        else:
                            pass
                        #
                        if 'y' in this_variable_indices and ( str( this_existing_data_row[ var_position_index ] ) != '' ) and print_true == True:
                            data_row[ var_position_index ] = '0'
                            #
                        else:
                            pass
                    #
                    data_row_list.append( data_row )
    #--------------------------------------#
    with open( output_adress + '/' + str( first_list[case] ) + '_Output' + '.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow( output_header )
        for n in range( len( data_row_list ) ):
            csvwriter.writerow( data_row_list[n] )
    #-----------------------------------------------------------------------------------------------------------%
    shutil.os.remove(data_name)
    #-----------------------------------------------------------------------------------------------------------%
    gc.collect(generation=2)
    time.sleep(0.05)
    #-----------------------------------------------------------------------------------------------------------%
    print(  'We finished with printing the outputs.', case)


############################################################################################################################################################################################################
def main_executer(n1, Executed_Scenario, packaged_useful_elements):
    print('# ' + str(n1+1) + ' of ' + Executed_Scenario )
    first_list, dir_of_interest = set_first_list( Executed_Scenario )
    file_aboslute_address = os.path.abspath("experiment_manager.py")
    file_adress = re.escape( file_aboslute_address.replace( 'experiment_manager.py', '' ) ).replace( '\:', ':' )
    #
    case_address = file_adress + r'Experimental_Platform\\Futures\\' + Executed_Scenario + '\\' + str( first_list[n1] )
    #
    this_case = [ e for e in os.listdir( case_address ) if '.txt' in e ]
    #
    str1 = "start /B start cmd.exe @cmd /k cd " + file_adress
    #
    data_file = case_address.replace('./','').replace('/','\\') + '\\' + str( this_case[0] )
    output_file = case_address.replace('./','').replace('/','\\') + '\\' + str( this_case[0] ).replace('.txt','') + '_output' + '.txt'
    #
    str2 = "glpsol -m OSeMOSYS_Model.txt -d " + str( data_file )  +  " -o " + str(output_file)
    os.system( str1 and str2 )
    time.sleep(1)
    #
    data_processor(n1,Executed_Scenario,packaged_useful_elements)


if __name__ == '__main__':
    time_list = []
    setup_table = pd.read_excel('_Experiment_Setup.xlsx' )
    scenarios_to_reproduce = str(setup_table.loc[0 ,'Scenario_to_Reproduce'])
    experiment_ID = str( setup_table.loc[0 ,'Experiment_ID'])
    gdp_dict_export = pickle.load( open( 'GDP_dict.pickle', "rb" ) )

    global Initial_Year_of_Uncertainty
    Initial_Year_of_Uncertainty = \
        int( setup_table.loc[0 ,'Initial_Year_of_Uncertainty'])

    time_range_vector = [y for y in range(2018, 2070+1)]
    start_mod_idx = time_range_vector.index(Initial_Year_of_Uncertainty)

    scenario_list = []
    if scenarios_to_reproduce == 'All':
        stable_scenario_list_raw = os.listdir('1_Baseline_Modelling')
        for n in range(len(stable_scenario_list_raw)):
            if (stable_scenario_list_raw[n] not in ['_Base_Dataset', '_BACKUP']
                    and '.txt' not in stable_scenario_list_raw[n]):
                scenario_list.append(stable_scenario_list_raw[n])
    elif scenarios_to_reproduce == 'Experiment':
        scenario_list.append('BAU')
        scenario_list.append('DDP')
    elif (scenarios_to_reproduce != 'All' and 
            scenarios_to_reproduce != 'Experiment'):
        scenario_list.append( scenarios_to_reproduce )

    # Expand the capacity of solar overall
    expand_plants = ['PP_SPV_US', 'PP_WND_US']

    ###
    # test_first = True
    test_first = False
    if test_first is True:
        scenario_list = [s for s in scenario_list if 'BAU' not in s]
    ###

    # Step 1: find all the runs without outputs
    for scen in scenario_list:
        files_2_cleanup, dirs_4_cleanup, store_names = [], [], []
        store_cases = []

        first_list, dir_of_interest = set_first_list(scen)
        for f in first_list:
            spec_dir = dir_of_interest + '/' + f
            all_files_internal = os.listdir(spec_dir)
            output_dir = spec_dir + '/' + [i for i in all_files_internal if
                                        'Output' in i and '.csv' in i][0]
            output_txt = spec_dir + '/' + [i for i in all_files_internal if
                                        '.txt' in i][0]
            name_txt = [i for i in all_files_internal if '.txt' in i][0]
            mod_case = name_txt.replace('.txt', '')
    
            file_size = os.stat(output_dir).st_size
            if file_size < 3000:
                files_2_cleanup.append(output_txt)
                dirs_4_cleanup.append(spec_dir)
                store_names.append(name_txt)
                store_cases.append(mod_case)

        # only acts if len(files_2_cleanup) > 0
        keep_files_ask, mod_files_ask = True, True
        # keep_files_ask, mod_files_ask = True, False

        with open('cleanup_' + str(scen) + '.pickle', 'wb') as outclean:
            pickle.dump(files_2_cleanup, outclean,
                        protocol=pickle.HIGHEST_PROTOCOL)
        outclean.close()

        # print('test first')
        # sys.exit()

        ###
        if test_first is True:
            files_2_cleanup = [f for f in files_2_cleanup if 'DDP' in f]
            # print('check files')
            # sys.exit()
        ###

        for f in range(len(files_2_cleanup)):
            ### if keep_files_ask is True:
            ###     keep_file = open('./_FRM_cleanup_store/' + store_names[f], 'w')
            act_file = open(files_2_cleanup[f], 'r')
            line_list = deepcopy(act_file.readlines())
            act_file.close()
            os.remove(files_2_cleanup[f])

            new_str_lines = []
            newlines_store = {}
            expand_plants_store = []

            interest_line_idx, continue_search = [], True
            for l in range(len(line_list)):
                line = line_list[l]
                if ('TotalAnnualMaxCapacity ' in line and
                        continue_search is True):
             
                    for n in range(l, l+80):
                        next_line = line_list[n]
                        set_row = next_line.split(' ')[0]

                        # Increment the capacity for hydrogen trucks
                        if 'TRNFREHEAHYD' == set_row:
                            
                            # print('happens!?')
                            
                            interest_line_idx.append(n)
                            convert_line_data_raw = next_line.split(' ')
                            convert_line_data = next_line.split(' ')[1:-1]
                            adj_line_data = []
                            for k in range(len(convert_line_data)):
                                if k > start_mod_idx:
                                    adj_line_data \
                                        .append("{:.2f}".format(float(9999)))  # double solar capacity
                                else:
                                    adj_line_data.append(convert_line_data[k])
                            adj_line_str = convert_line_data_raw[0] + ' '
                            for k in adj_line_data:
                                adj_line_str += str(k) + ' '
                            adj_line_str += convert_line_data_raw[-1]
                            newlines_store.update({n:deepcopy(adj_line_str)})

                            continue_search = False

                        # # Multiply the maximum capacity:
                        # if (('PP_SPV_US' in set_row or 'PP_WND_US' in set_row)
                        #         and 'HYD' not in set_row
                        #         and 'H2' not in set_row
                        #         and continue_search is True):
                        # 
                        #     if 'PP_SPV_US' == set_row and 'PP_SPV_US' not in expand_plants_store:
                        #         expand_plants_store.append('PP_SPV_US')
                        #         exp_mult = 1
                        #     
                        #     if 'PP_WND_US' == set_row and 'PP_WND_US' not in expand_plants_store:
                        #         expand_plants_store.append('PP_WND_US')
                        #         exp_mult = 1
                        # 
                        #     interest_line_idx.append(n)
                        #     convert_line_data_raw = next_line.split(' ')
                        #     convert_line_data = next_line.split(' ')[1:-1]
                        #     adj_line_data = []
                        #     for k in range(len(convert_line_data)):
                        #         if k > start_mod_idx:
                        #             adj_line_data \
                        #                 .append("{:.2f}".format(float(convert_line_data[k])*exp_mult))  # double solar capacity
                        #         else:
                        #             adj_line_data.append(convert_line_data[k])
                        #     adj_line_str = convert_line_data_raw[0] + ' '
                        #     for k in adj_line_data:
                        #         adj_line_str += str(k) + ' '
                        #     adj_line_str += convert_line_data_raw[-1]
                        #     newlines_store.update({n:deepcopy(adj_line_str)})
                        # 
                        #     expand_plants.sort()
                        #     expand_plants_store.sort()
                        #     if expand_plants == expand_plants_store:
                        #         continue_search = False

                        # # Increment the capacity for hydrogen
                        # if 'PP_SPV_US_H2' == set_row:
                        #     interest_line_idx.append(n)
                        #     convert_line_data_raw = next_line.split(' ')
                        #     convert_line_data = next_line.split(' ')[1:-1]
                        #     adj_line_data = []
                        #     for k in range(len(convert_line_data)):
                        #         if k > start_mod_idx:
                        #             adj_line_data \
                        #                 .append("{:.2f}".format(float(10)))  # double solar capacity
                        #         else:
                        #             adj_line_data.append(convert_line_data[k])
                        #     adj_line_str = convert_line_data_raw[0] + ' '
                        #     for k in adj_line_data:
                        #         adj_line_str += str(k) + ' '
                        #     adj_line_str += convert_line_data_raw[-1]
                        #     newlines_store.update({n:deepcopy(adj_line_str)})
                        # 
                        #     continue_search = False

                if l in interest_line_idx and interest_line_idx != 0:
                    new_str_lines.append(newlines_store[l])
                else:
                    new_str_lines.append(line)

            # Now write the updated file:
            if mod_files_ask is True:
                act_file_new = open(files_2_cleanup[f], 'w')
                for l in range(len(new_str_lines)):
                    line = new_str_lines[l]
                    act_file_new.write(line)
                act_file_new.close()

        if test_first is True:
            print('check the text file')
            sys.exit()

        # Here the files would have been re-written

        # Before continuing, we must add a few additional inputs:
        Fleet_Groups = pickle.load( open( './0_From_Confection/A-O_Fleet_Groups.pickle', "rb" ))
        Fleet_Techs_Distance = pickle.load( open( './0_From_Confection/A-O_Fleet_Groups_Distance.pickle', "rb" ))
        Fleet_Techs_OR = pickle.load( open( './0_From_Confection/A-O_Fleet_Groups_OR.pickle', "rb" ))
        Fleet_Groups_techs_2_dem = pickle.load( open( './0_From_Confection/A-O_Fleet_Groups_T2D.pickle', "rb" ))

        Fleet_Groups_inv = {}
        for k in range( len( list( Fleet_Groups.keys() ) ) ):
            this_fleet_group_key = list( Fleet_Groups.keys() )[k]
            for e in range( len( Fleet_Groups[ this_fleet_group_key ] ) ):
                this_fleet_group_tech = Fleet_Groups[ this_fleet_group_key ][ e ]
                Fleet_Groups_inv.update( { this_fleet_group_tech:this_fleet_group_key } )

        reference_driven_distance = \
            pickle.load( open( 'reference_driven_distance.pickle', "rb" ))

        reference_occupancy_rate = \
            pickle.load( open( 'reference_occupancy_rate.pickle', "rb" ))

        # Now this is a continuation of normal FRM
        packaged_useful_elements = [reference_driven_distance,
                                    reference_occupancy_rate,
                                    Fleet_Groups_inv,
                                    time_range_vector,
                                    gdp_dict_export]

        x = len(store_cases)

        max_x_per_iter = int( setup_table.loc[ 0 ,'Parallel_Use'] ) # FLAG: This is an input.

        y = x / max_x_per_iter
        y_ceil = math.ceil( y )

        #'''
        for n in range(0,y_ceil):
            print('###')
            n_ini = n*max_x_per_iter
            processes = []
            start1 = time.time()
            if n_ini + max_x_per_iter <= x:
                max_iter = n_ini + max_x_per_iter
            else:
                max_iter = x
            for n2 in range( n_ini , max_iter ):
                idx_apply = first_list.index(store_cases[n2])
                print('index: ' + str(idx_apply), ' // case: ' + first_list[idx_apply])
                p = mp.Process(target=main_executer,
                               args=(idx_apply,
                                     scen, packaged_useful_elements,))
                processes.append(p)
                p.start()
            for process in processes:
                process.join()

            end_1 = time.time()   
            time_elapsed_1 = -start1 + end_1
            print( str( time_elapsed_1 ) + ' seconds' )
            time_list.append( time_elapsed_1 )
        #'''
    print('   The total time producing outputs and storing data has been: ' + str( sum( time_list ) ) + ' seconds')
    print( 'For all effects, this has been the end. It all took: ' + str( sum( time_list ) ) + ' seconds')

