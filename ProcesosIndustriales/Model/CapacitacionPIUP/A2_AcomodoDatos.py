# -*- coding: utf-8 -*-
"""
@author: Luis Victor-Gallardo // 2021
"""
import pandas as pd
#import pickle
#import sys
import math
#import numpy as np
import time
from copy import deepcopy
#
start1 = time.time()
#
horizon_configuration = pd.read_excel( './A1_Inputs/A-I_Horizon_Configuration.xlsx' )
baseyear = horizon_configuration['Initial_Year'].tolist()[0]
endyear = horizon_configuration['Final_Year'].tolist()[0]
global time_range_vector
time_range_vector = [ n for n in range( baseyear, endyear+1 ) ]

Wide_Param_Header = [ 'PARAMETER', 'Scenario', 'REGION', 'TECHNOLOGY', 'FUEL', # For the production of the parameter files
                        'EMISSION', 'MODE_OF_OPERATION', 'YEAR', 'TIMESLICE',
                        'SEASON', 'DAYTYPE', 'DAILYTIMEBRACKET', 'STORAGE', 'Value' ]
#
other_setup_parameters = pd.read_excel( './A2_Extra_Inputs/A-Xtra_Scenarios.xlsx' )
other_setup_params_name = other_setup_parameters['Name'].tolist()
other_setup_params_param = other_setup_parameters['Param'].tolist()
other_setup_params = {}
for n in range( len( other_setup_params_name ) ):
    other_setup_params.update( { other_setup_params_name[n]:other_setup_params_param[n] } )
#
print_aid_parameter = False
#
df_Yearsplit = pd.DataFrame( columns = Wide_Param_Header )
for y in range( len( time_range_vector ) ):
    this_dict_4_wide = {}
    this_dict_4_wide.update( { 'PARAMETER':'Yearsplit', 'Scenario':other_setup_params[ 'Main_Scenario' ],
                                'TIMESLICE':other_setup_params['Timeslice'], 'YEAR':time_range_vector[y],
                                'Value':1 } )
    df_Yearsplit = df_Yearsplit.append( this_dict_4_wide, ignore_index=True )
    

#------------------------------------------------------------------------------
# BELOW WORKS WELL
#
AR_Model_Base_Year = pd.ExcelFile('./A1_Outputs/A-O_AR_Model_Base_Year.xlsx')
AR_Projections = pd.ExcelFile('./A1_Outputs/A-O_AR_Projections.xlsx')
groups_list = AR_Model_Base_Year.sheet_names # see all sheet names
# NOTE THIS IS THE SAME AS :: AR_Projections.sheet_names # see all sheet names

# This section affects the *InputActivityRatio* and the *OutputActivityRatio*
AR_Osemosys_Parameters = [ 'InputActivityRatio', 'OutputActivityRatio' ]
df_IAR = pd.DataFrame( columns = Wide_Param_Header )
df_IAR_dict = {}
df_OAR = pd.DataFrame( columns = Wide_Param_Header )
df_OAR_dict = {}

All_Tech_list_system_group = []
All_Tech_list = []
All_Tech_list_names = []
All_Fuel_list = []
All_Fuel_list_names = []
#
All_Tech_len_long = 0
All_Fuel_len_long = 0
#
AR_Base_df = {}
AR_Base_proj_df = {}
AR_Base_proj_df_new = {}
AR_Base = {}

for g in range( len( groups_list ) ):
    AR_Base_df.update( { groups_list[g]:AR_Model_Base_Year.parse( groups_list[g] ) } )
    this_df = AR_Base_df[ groups_list[g] ]
    #
    AR_Base_proj_df.update( { groups_list[g]:AR_Projections.parse( groups_list[g] ) } )
    this_proj_df = AR_Base_proj_df[ groups_list[g] ]
    #
    this_proj_df_new = deepcopy( this_proj_df )
    this_proj_df_new.replace( { 'Direction': 'Output'}, 'OutputActivityRatio', inplace=True )
    this_proj_df_new.replace( { 'Direction': 'Input'}, 'InputActivityRatio', inplace=True )
    this_proj_df_new.rename( columns={ "Direction": "Parameter" }, inplace=True )
    this_proj_df_new = this_proj_df_new.drop(columns=['Projection.Mode', 'Projection.Parameter'])
    #
    if groups_list[g] != 'Primary' and groups_list[g] != 'Transport':
        this_df_fuel_i = this_df['Fuel.I'].tolist()
        this_df_fuel_i_name = this_df['Fuel.I.Name'].tolist()
    if groups_list[g] == 'Primary':
        this_df_fuel_i = []
        this_df_fuel_i_name = []
    if groups_list[g] == 'Transport':
        this_df_fuel_i = this_df['Fuel.I.1'].tolist()
        this_df_fuel_i_name = this_df['Fuel.I.1.Name'].tolist()
        #
        # this_df_filtered = this_df.loc[ ( this_df['Fuel.I.2'] != 'none' ) ]
        this_df_fuel_i2 = this_df['Fuel.I.2'].tolist()
        this_df_fuel_i2_name = this_df['Fuel.I.2.Name'].tolist()
        #
    #
    this_df_techs = this_df['Tech'].tolist()
    this_df_techs_names = this_df['Tech.Name'].tolist()
    All_Tech_len_long += len( this_df_techs )
    #
    this_df_fuel_o = this_df['Fuel.O'].tolist()
    this_df_fuel_o_name = this_df['Fuel.O.Name'].tolist()
    #------------------------------------------------------#
    these_fuels = this_df_fuel_i + this_df_fuel_o
    these_fuels_names = this_df_fuel_i_name + this_df_fuel_o_name
    #------------------------------------------------------#
    for t in range( len( this_df_techs ) ):
        if this_df_techs[t] not in All_Tech_list:
            All_Tech_list.append( this_df_techs[t] )
            All_Tech_list_names.append( this_df_techs_names[t] )
    #
    for f in range( len( these_fuels ) ):
        if these_fuels[f] not in All_Fuel_list:
            All_Fuel_list.append( these_fuels[f] )
            All_Fuel_list_names.append( these_fuels_names[f] )
    #
    #------------------------------------------------------#
    tech_plus_fuel_unique_oar, tech_plus_fuel_unique_iar = [], []

    # Let us continue with a useful dictionary gathering all the data:
    for t in range( len( this_df_techs ) ):
        this_tech = this_df_techs[t]
        output_fuel = this_df_fuel_o[t]
        #
        # Query the output // Applies to all *groups_list* 
        this_df_select = this_df.loc[ ( this_df[ 'Tech' ] == this_tech ) & ( this_df[ 'Fuel.O' ] == output_fuel ) ]
        this_df_select_by_fo = this_df_select[ 'Value.Fuel.O' ].tolist()[0]
        
        this_proj_df_local = this_proj_df.loc[ ( this_proj_df[ 'Tech' ] == this_tech ) & ( this_proj_df[ 'Fuel' ] == output_fuel ) ] 
        this_proj_df_mode_o, this_proj_df_param_o = this_proj_df_local['Projection.Mode'].tolist()[0] , this_proj_df_local['Projection.Parameter'].tolist()[0]
        #
        if groups_list[g] != 'Primary' and groups_list[g] != 'Transport':
            # query 1 input and 1 output
            input_fuel = this_df_fuel_i[t]
            input_fuel_2 = 'none'
        #
        if groups_list[g] == 'Transport':
            # query 2 inputs
            input_fuel = this_df_fuel_i[t]
            input_fuel_2 = this_df_fuel_i2[t]
        #
        if groups_list[g] != 'Primary':
            if groups_list[g] != 'Transport':
                this_df_select = this_df.loc[ ( this_df[ 'Tech' ] == this_tech ) & ( this_df[ 'Fuel.I' ] == input_fuel ) ]
                this_df_select_by_fi = [ this_df_select[ 'Value.Fuel.I' ].tolist()[0] ]
                #
                this_proj_df_local = this_proj_df.loc[ ( this_proj_df[ 'Tech' ] == this_tech ) & ( this_proj_df[ 'Fuel' ] == input_fuel ) ] 
                this_proj_df_mode_i, this_proj_df_param_i = [ this_proj_df_local['Projection.Mode'].tolist()[0] ], [ this_proj_df_local['Projection.Parameter'].tolist()[0] ]  
                #
            else:
                this_df_select = this_df.loc[ ( this_df[ 'Tech' ] == this_tech ) & ( this_df[ 'Fuel.I.1' ] == input_fuel ) ]
                this_df_select_by_fi = [ this_df_select[ 'Value.Fuel.I.1' ].tolist()[0] ]
                #
                this_proj_df_local = this_proj_df.loc[ ( this_proj_df[ 'Tech' ] == this_tech ) & ( this_proj_df[ 'Fuel' ] == input_fuel ) ] 
                this_proj_df_mode_i, this_proj_df_param_i = [ this_proj_df_local['Projection.Mode'].tolist()[0] ], [ this_proj_df_local['Projection.Parameter'].tolist()[0] ]  
                #
                if input_fuel_2 != 'none':
                    this_df_select = this_df.loc[ ( this_df[ 'Tech' ] == this_tech ) & ( this_df[ 'Fuel.I.2' ] == input_fuel_2 ) ]
                    this_df_select_by_fi += [ this_df_select[ 'Value.Fuel.I.2' ].tolist()[0] ]
                    #
                    this_proj_df_local = this_proj_df.loc[ ( this_proj_df[ 'Tech' ] == this_tech ) & ( this_proj_df[ 'Fuel' ] == input_fuel_2 ) ] 
                    this_proj_df_mode_i += [ this_proj_df_local['Projection.Mode'].tolist()[0] ]
                    this_proj_df_param_i += [ this_proj_df_local['Projection.Parameter'].tolist()[0] ]
        #
        else:
            this_proj_df_mode_i = ''
        #
        if print_aid_parameter == True:
            print( groups_list[g], this_tech, this_proj_df_mode_o, this_proj_df_mode_i )    
        #
        for y in range( len( time_range_vector ) ):
            this_param = 'OutputActivityRatio'
            mask = ( this_proj_df_new[ 'Tech' ] == this_tech ) & ( this_proj_df_new[ 'Fuel' ] == output_fuel ) & ( this_proj_df_new[ 'Parameter' ] == this_param )
            if this_proj_df_mode_o == 'Flat':
                this_proj_df_new.loc[ mask , time_range_vector[y] ] = round( this_df_select_by_fo, 4 )

            # Filling the data :
            if this_tech + '+' + output_fuel not in tech_plus_fuel_unique_oar:
                this_mask_index = this_proj_df_new.loc[ mask , time_range_vector[y] ].index.tolist()[0]
                df_OAR_dict.update( { 'PARAMETER':this_param, 'Scenario':other_setup_params[ 'Main_Scenario' ],
                                    'REGION':other_setup_params['Region'] , 'TECHNOLOGY':this_tech , 'FUEL':output_fuel ,
                                    'MODE_OF_OPERATION':other_setup_params['Mode_of_Operation'] , 'YEAR':time_range_vector[y] ,
                                    'Value':deepcopy( this_proj_df_new.loc[ mask , time_range_vector[y] ][ this_mask_index ] ) } )
                df_OAR = df_OAR.append( df_OAR_dict, ignore_index=True )

            if groups_list[g] != 'Primary':
                input_fuel_list = [ input_fuel ]
                if input_fuel_2 != 'none':
                    input_fuel_list += [ input_fuel_2 ]
                #
                for inp in range( len( input_fuel_list ) ):
                    this_input_fuel = input_fuel_list[inp]
                    this_proj_df_mode_i0 = this_proj_df_mode_i[inp]
                    this_proj_df_param_i0 = this_proj_df_param_i[inp]
                    #
                    this_param = 'InputActivityRatio'
                    mask = ( this_proj_df_new[ 'Tech' ] == this_tech ) & ( this_proj_df_new[ 'Fuel' ] == this_input_fuel ) & ( this_proj_df_new[ 'Parameter' ] == this_param )
                    ###################################################################################################
                    if this_proj_df_mode_i0 == 'Flat':
                        this_proj_df_new.loc[ mask , time_range_vector[y] ] = round( this_df_select_by_fi[ inp ], 4 )
                    if this_proj_df_mode_i0 == 'Yearly percent change':
                        if y == 0:
                            this_proj_df_new.loc[ mask , time_range_vector[y] ] = round( this_df_select_by_fi[ inp ], 4 ) # round( this_df_select_by_fi[ inp ]*( 1 + this_proj_df_param_i0/100 ), 4 )
                        else:
                            this_proj_df_new.loc[ mask , time_range_vector[y] ] = round( this_proj_df_new.loc[ mask , time_range_vector[y-1] ]*( 1 + this_proj_df_param_i0/100 ), 4 )
                    #
                    if this_proj_df_mode_i0 == 'User defined':
                        this_proj_df_new.loc[ mask , time_range_vector[y] ] = round( this_proj_df.loc[ mask , time_range_vector[y] ], 4 )
                    #
                    ###################################################################################################
                    # Filling the data :
                    if this_tech + '+' + this_input_fuel not in tech_plus_fuel_unique_iar:
                        this_mask_index = this_proj_df_new.loc[ mask , time_range_vector[y] ].index.tolist()[0]
                        df_IAR_dict.update( { 'PARAMETER':this_param, 'Scenario':other_setup_params[ 'Main_Scenario' ],
                                            'REGION':other_setup_params['Region'] , 'TECHNOLOGY':this_tech , 'FUEL':this_input_fuel ,
                                            'MODE_OF_OPERATION':other_setup_params['Mode_of_Operation'] , 'YEAR':time_range_vector[y] , 
                                            'Value':deepcopy( this_proj_df_new.loc[ mask , time_range_vector[y] ][ this_mask_index ] ) } )
                        df_IAR = df_IAR.append( df_IAR_dict, ignore_index=True )

                    # Create a tech + fuel string to show uniqueness in iar values:
                    if (this_tech + '+' + this_input_fuel not in tech_plus_fuel_unique_iar) and y == len(time_range_vector)-1:
                        tech_plus_fuel_unique_iar.append(this_tech + '+' + this_input_fuel)

        # Create a tech + fuel string to show uniqueness in oar values:
        if this_tech + '+' + output_fuel not in tech_plus_fuel_unique_oar:
            tech_plus_fuel_unique_oar.append(this_tech + '+' + output_fuel)

    AR_Base_proj_df_new.update( { groups_list[g]:this_proj_df_new } )
    #

# HERE WE HAVE A FUNCTIONING IAR AND OAR FOR BOTH NEEDS: WIDE AND LONG FORMATS
#
#------------------------------------------------------------------------------
# DEMAND
Demand = pd.ExcelFile('./A1_Outputs/A-O_Demand.xlsx')
Demand_df = Demand.parse( Demand.sheet_names[0] )
#
df_SpecAnnualDemand = pd.DataFrame( columns = Wide_Param_Header )
df_SpecDemandProfile = pd.DataFrame( columns = Wide_Param_Header )
demand_headers = [  'Demand/Share', 'Fuel/Tech', 'Ref.Cap.BY', 'Ref.OAR.BY', 'Ref.km.BY',
                    'Projection.Mode', 'Projection.Parameter', 'Introduced.Unit', 'Target.Unit']
#
list_demand_or_share = Demand_df[ 'Demand/Share' ].tolist()
#
list_fuel_or_tech = Demand_df[ 'Fuel/Tech' ].tolist()

list_projection_mode = Demand_df[ 'Projection.Mode' ].tolist()
list_projection_param = Demand_df[ 'Projection.Parameter' ].tolist()


for m in range( len( list_demand_or_share ) ):
    # This is the case for *Passenger* transport:
    #
    if Demand_df['Demand/Share'].tolist()[m] == 'Demand':
        this_fuel = list_fuel_or_tech[m]
        for y in range( len( time_range_vector ) ):
            this_dict_4_wide = {}
            this_dict_4_wide.update( { 'PARAMETER':'SpecifiedAnnualDemand', 'Scenario':other_setup_params[ 'Main_Scenario' ],
                                        'REGION':other_setup_params['Region'] , 'FUEL':this_fuel,
                                        'YEAR':time_range_vector[y],
                                        'Value':Demand_df.loc[ m, time_range_vector[y] ] } )
            df_SpecAnnualDemand = df_SpecAnnualDemand.append( this_dict_4_wide, ignore_index=True )
            #
            this_dict_4_wide = {}
            this_dict_4_wide.update( { 'PARAMETER':'SpecifiedDemandProfile', 'Scenario':other_setup_params[ 'Main_Scenario' ],
                                        'REGION':other_setup_params['Region'] , 'FUEL':this_fuel,
                                        'TIMESLICE':other_setup_params['Timeslice'], 'YEAR':time_range_vector[y],
                                        'Value':1 } )
            df_SpecDemandProfile = df_SpecDemandProfile.append( this_dict_4_wide, ignore_index=True )
            #
        #
    #
#

Parametrization = pd.ExcelFile('./A1_Outputs/A-O_Parametrization.xlsx')
param_sheets = Parametrization.sheet_names # see all sheet names
#
params_dict = {}
params_dict_new = {}
params_dict_new_natural = {}
params_columns_dict = {}
#
# Let us quickly obtain the parameter list found in this excel file:
overall_param_list = []
for s in range( len( param_sheets ) ):
    this_df = Parametrization.parse( param_sheets[s] )
    overall_param_list_raw = this_df[ 'Parameter' ].tolist()
    for p in range( len( list( set( overall_param_list_raw ) ) ) ):
        if list( set( overall_param_list_raw ) )[p] not in overall_param_list:
            overall_param_list.append( list( set( overall_param_list_raw ) )[p] )
#
overall_param_df_dict = {}
overall_param_df_dict.update( { 'InputActivityRatio':df_IAR } )
overall_param_df_dict.update( { 'OutputActivityRatio':df_OAR } )
overall_param_df_dict.update( { 'YearSplit':df_Yearsplit } )
overall_param_df_dict.update( { 'SpecifiedAnnualDemand':df_SpecAnnualDemand } )
overall_param_df_dict.update( { 'SpecifiedDemandProfile':df_SpecDemandProfile } )
for p in range( len( overall_param_list ) ):
    if overall_param_list[p] != 'OutputActivityRatio':
        overall_param_df_dict.update( { overall_param_list[p]:pd.DataFrame( columns = Wide_Param_Header ) } )
#*****************************************************************************
# Let us do the capacity limits for the group technologies
'''
Description: this section changes the units from *Demand_df* in % to Gpkm for the modes of transport
Alternatives: change the value of oar (occupancy rate) in time, here it is left constant
'''
Demand_df_new = deepcopy( Demand_df )
Demand_df_techs = Demand_df_new[ 'Fuel/Tech' ].tolist()
#
for s in range( len( param_sheets ) ):
    params_dict.update( { param_sheets[s]:Parametrization.parse( param_sheets[s] ) } )
    this_df = params_dict[ param_sheets[s] ]
    # print(this_df)
    # print(type(this_df))
    #
    this_df_new = deepcopy( this_df )
    this_df_new_2 = deepcopy( this_df )
    #
    params_columns_dict.update( { param_sheets[s]:this_df.columns.tolist() } )
    #
    df_index_list = this_df.index.tolist()
    df_index_list_with_data = []
    #
    this_df_tech_list = this_df['Tech' ].tolist()
    #
    for n in range( len( df_index_list ) ):
        this_tech = this_df.loc[ n, 'Tech' ]
        this_param = this_df.loc[ n, 'Parameter' ]
        
        if s != 0: # s == 0 does not need to change in time
            this_projection_mode = this_df.loc[ n, 'Projection.Mode' ]
            #-----------------------------------------
            if this_projection_mode == 'Flat':
                print(this_projection_mode)
                for y in range( len( time_range_vector ) ):
                    this_df_new.loc[ n, time_range_vector[y] ] = round( this_df.loc[ n, 2018 ], 4 )
                    this_df_new_2.loc[ n, time_range_vector[y] ] = this_df_new.loc[ n, time_range_vector[y] ]
            #-----------------------------------------
            if this_projection_mode == 'Percent growth of incomplete years':
                print(this_projection_mode)
                growth_param = this_df.loc[ n, 'Projection.Parameter' ]
                for y in range( len( time_range_vector ) ):
                    value_field = this_df.loc[ n, time_range_vector[y] ]
                    if math.isnan(value_field) == True:
                        this_df_new.loc[ n, time_range_vector[y] ] = round( this_df_new.loc[ n, time_range_vector[y-1] ]*( 1 + growth_param/100 ), 4 )
                        this_df_new_2.loc[ n, time_range_vector[y] ] = this_df_new.loc[ n, time_range_vector[y] ]
            #-----------------------------------------
            if this_projection_mode == 'User defined':
                print(this_projection_mode)
                for y in range( len( time_range_vector ) ):
                    this_df_new.loc[ n, time_range_vector[y] ] = round( this_df.loc[ n, time_range_vector[y] ], 4 )
                    this_df_new_2.loc[ n, time_range_vector[y] ] = this_df_new.loc[ n, time_range_vector[y] ]
            #-----------------------------------------
            if this_projection_mode == 'Zero':
                for y in range( len( time_range_vector ) ):
                    this_df_new.loc[ n, time_range_vector[y] ] = 0
                    this_df_new_2.loc[ n, time_range_vector[y] ] = this_df_new.loc[ n, time_range_vector[y] ]
            #
        #********************************************#
        if param_sheets[s] == 'Vehicle Techs':
            this_projection_mode = this_df.loc[ n, 'Projection.Mode' ]
            this_unit_introduced = this_df.loc[ n, 'Unit.Introduced' ] 
            this_unit_target = this_df.loc[ n, 'Unit' ] 
            # we must use fleet // demand // projections to calibrate the vehicle fleets
            if type( this_unit_introduced ) == str:
            
                if 'Relative' in this_unit_introduced and this_projection_mode == 'User defined trajectory relative to BY':
                    ref_tech = this_unit_introduced.split(' ')[-1]
                    ref_tech_index = this_df_tech_list.index(ref_tech)
                    ref_value = this_df.loc[ ref_tech_index, time_range_vector[0] ]
                    for y in range( len( time_range_vector ) ):
                        if y == 0:
                            this_df_new.loc[ n, time_range_vector[y] ] = ref_value*this_df.loc[ n, time_range_vector[y] ]
                        else:
                            this_df_new.loc[ n, time_range_vector[y] ] = this_df_new.loc[ n, time_range_vector[0] ]*this_df.loc[ n, time_range_vector[y] ]                    
                        this_df_new_2.loc[ n, time_range_vector[y] ] = this_df_new.loc[ n, time_range_vector[y] ]
                #
                if 'Relative' in this_unit_introduced and this_projection_mode == 'Flat':
                    ref_tech = this_unit_introduced.split(' ')[-1]
                    ref_tech_index = this_df_tech_list.index(ref_tech)
                    ref_value = this_df.loc[ ref_tech_index, time_range_vector[0] ]
                    #
                    for y in range( len( time_range_vector ) ):
                        this_df_new.loc[ n, time_range_vector[y] ] = ref_value*this_df.loc[ n, time_range_vector[0] ]
                        this_df_new_2.loc[ n, time_range_vector[y] ] = this_df_new.loc[ n, time_range_vector[y] ]
                #
                if 'Relative' not in this_unit_introduced and this_projection_mode == 'User defined trajectory relative to BY':
                    for y in range( len( time_range_vector ) ): # these units are NOT relative to another tech, so we proceeed as follows:
                        if y == 0:
                            pass # nothing is necessary to do
                        else:
                            this_df_new.loc[ n, time_range_vector[y] ] = this_df.loc[ n, time_range_vector[0] ]*this_df.loc[ n, time_range_vector[y] ]
                            this_df_new_2.loc[ n, time_range_vector[y] ] = this_df_new.loc[ n, time_range_vector[y] ]
        #
        #********************************************#
        # Remember to call: *this_tech*, *this_param*
        if s == 0: # we store the parameters without years
            this_dict_4_wide = {}
            this_dict_4_wide.update( { 'PARAMETER':this_param, 'Scenario':other_setup_params[ 'Main_Scenario' ],
                                'REGION':other_setup_params['Region'] , 'TECHNOLOGY':this_tech,
                                'Value':deepcopy( this_df_new_2.loc[ n , 'Value' ] ) } )
            overall_param_df_dict[this_param] = overall_param_df_dict[this_param].append( this_dict_4_wide, ignore_index=True )
                
                
        elif this_projection_mode != 'EMPTY' and this_projection_mode != 'Zero' and this_projection_mode != '' and type(this_projection_mode) == str and this_projection_mode != 'None' and this_projection_mode != 'According to demand':
            for y in range( len( time_range_vector ) ):
                this_dict_4_wide = {}
                #
                if s != 0 and param_sheets[s] != 'Other_Techs':
                    if this_param in [ 'CapacityFactor' ]: # must include timeslice
                        
                        
                        this_dict_4_wide.update( { 'PARAMETER':this_param, 'Scenario':other_setup_params[ 'Main_Scenario' ],
                                                'REGION':other_setup_params['Region'] , 'TECHNOLOGY':this_tech,
                                                'YEAR':time_range_vector[y], 'TIMESLICE':other_setup_params['Timeslice'],
                                                'Value':deepcopy( round( this_df_new_2.loc[ n, time_range_vector[y] ], 4 ) ) } )
                    if this_param in [ 'VariableCost' ]: # include mode of operation
                            
                        this_dict_4_wide.update( { 'PARAMETER':this_param, 'Scenario':other_setup_params[ 'Main_Scenario' ],
                                                'REGION':other_setup_params['Region'] , 'TECHNOLOGY':this_tech,
                                                'YEAR':time_range_vector[y], 'MODE_OF_OPERATION':other_setup_params['Mode_of_Operation'],
                                                'Value':deepcopy( round( this_df_new_2.loc[ n, time_range_vector[y] ], 4 ) ) } )

                    if this_param not in [ 'CapacityFactor', 'VariableCost' ] and this_projection_mode != 'According to demand':
                        this_dict_4_wide.update( { 'PARAMETER':this_param, 'Scenario':other_setup_params[ 'Main_Scenario' ],
                                                'REGION':other_setup_params['Region'] , 'TECHNOLOGY':this_tech,
                                                'YEAR':time_range_vector[y],
                                                'Value':deepcopy( round( this_df_new_2.loc[ n, time_range_vector[y] ], 4 ) ) } )
                    #
                    if this_projection_mode == 'According to demand':
                        pass
                        #
                    #
                    overall_param_df_dict[this_param] = overall_param_df_dict[this_param].append( this_dict_4_wide, ignore_index=True )
                    #
                #
            #
        #
    #    
    params_dict_new.update( { param_sheets[s]:this_df_new_2 } ) # this has the model ready for osemosys, but it may be less intuitive for the rest of the system
    params_dict_new_natural.update( { param_sheets[s]:this_df_new } ) # this has the model in natural terms
    #

#------------------------------------------------------------------------------
Emissions = pd.ExcelFile('./A2_Extra_Inputs/A-Xtra_Emissions.xlsx')
# Emissions.sheet_names # see all sheet names // this only need thes wide format
Emissions_ghg_df = Emissions.parse( 'GHGs' )
Emissions_ext_df = Emissions.parse( 'Externalities' )
#
emissions_list = list( set( Emissions_ghg_df['Emission'].tolist() + Emissions_ext_df['External Cost'].tolist() ) )
#
df_Emissions = pd.DataFrame( columns = Wide_Param_Header )
these_emissions = Emissions_ghg_df['Emission'].tolist()
these_e_techs = Emissions_ghg_df['Tech'].tolist()
these_e_values = Emissions_ghg_df['EmissionActivityRatio'].tolist()
for e in range( len( these_emissions ) ):
    this_emission = these_emissions[e]
    this_tech = these_e_techs[e]
    #
    for y in range( len( time_range_vector ) ):
        this_dict_4_wide = {}
        this_dict_4_wide.update( { 'PARAMETER':'EmissionActivityRatio', 'Scenario':other_setup_params[ 'Main_Scenario' ],
                                    'REGION':other_setup_params['Region'] , 'TECHNOLOGY':this_tech, 'EMISSION':this_emission,
                                    'MODE_OF_OPERATION':other_setup_params['Mode_of_Operation'],'YEAR':time_range_vector[y],
                                    'Value':these_e_values[e] } )
        df_Emissions = df_Emissions.append( this_dict_4_wide, ignore_index=True )

df_EmissionPenalty = pd.DataFrame( columns = Wide_Param_Header )
these_emissions = Emissions_ext_df['External Cost'].tolist()
these_e_techs = Emissions_ext_df['Tech'].tolist()
these_e_values = Emissions_ext_df['EmissionActivityRatio'].tolist()
these_e_penalty = Emissions_ext_df['EmissionsPenalty'].tolist()
this_emission_unique = []
for e in range( len( these_emissions ) ):
    this_emission = these_emissions[e]
    this_tech = these_e_techs[e]
    #
    for y in range( len( time_range_vector ) ):
        this_dict_4_wide = {}
        this_dict_4_wide_2 = {}
        this_dict_4_wide.update( { 'PARAMETER':'EmissionActivityRatio', 'Scenario':other_setup_params[ 'Main_Scenario' ],
                                    'REGION':other_setup_params['Region'] , 'TECHNOLOGY':this_tech, 'EMISSION':this_emission,
                                    'MODE_OF_OPERATION':other_setup_params['Mode_of_Operation'],'YEAR':time_range_vector[y],
                                    'Value':these_e_values[e] } )
        df_Emissions = df_Emissions.append( this_dict_4_wide, ignore_index=True )
        #
        if this_emission + ' ' + str( time_range_vector[y] ) not in this_emission_unique:
            this_dict_4_wide_2.update( { 'PARAMETER':'EmissionsPenalty', 'Scenario':other_setup_params[ 'Main_Scenario' ],
                                        'REGION':other_setup_params['Region'] , 'TECHNOLOGY':'', 'EMISSION':this_emission,
                                        'YEAR':time_range_vector[y],
                                        'Value':these_e_penalty[e] } )
            df_EmissionPenalty = df_EmissionPenalty.append( this_dict_4_wide_2, ignore_index=True )
            this_emission_unique.append( this_emission + ' ' + str( time_range_vector[y] ) )
        #
    #
#
overall_param_df_dict.update( { 'EmissionActivityRatio':df_Emissions } )
overall_param_df_dict.update( { 'EmissionsPenalty':df_EmissionPenalty } )
#
# Let us create the basis for the NDP:
overall_param_df_dict_ndp = deepcopy( overall_param_df_dict )


end_1 = time.time()   
time_elapsed_1 = -start1 + end_1
print( str( time_elapsed_1 ) + ' seconds /', str( time_elapsed_1/60 ) + ' minutes' )
print('*: For all effects, we have finished the processing tasks of this script. We must now print the results out.')
#***********************************************************************************
#---------------------------------
# Print updated demand DF (user)
writer_Demand_df_new = pd.ExcelWriter("./A1_Outputs/A-O_Demand_COMPLETED.xlsx", engine='xlsxwriter')
Demand_df_new[2018] = Demand_df_new[2018].astype(float)
Demand_df_new = Demand_df_new.round( 4 )
Demand_df_new.to_excel( writer_Demand_df_new, sheet_name = 'A-O_Demand', index=False)
writer_Demand_df_new.save()
#---------------------------------
# Print updated *parameterization* DF (user) // this is in Osemosys terms
writer_Param_df = pd.ExcelWriter("./A1_Outputs/A-O_Parametrization_COMPLETED.xlsx", engine='xlsxwriter')
param_sheets_print = list( params_dict_new.keys() )
for s in range( len( param_sheets_print ) ):
    this_df_print = params_dict_new[ param_sheets_print[s] ]
    this_df_print = this_df_print.round( 4 )
    this_df_print.to_excel( writer_Param_df, sheet_name = param_sheets_print[s], index=False)
writer_Param_df.save()
#---------------------------------
# Print updated *parameterization* DF (user) // this is in "natural" terms, i.e. the value of each one of the vehicles per unit
writer_Param_Natural_df = pd.ExcelWriter("./A1_Outputs/A-O_Parametrization_Natural_COMPLETED.xlsx", engine='xlsxwriter')
param_sheets_print = list( params_dict_new_natural.keys() )
for s in range( len( param_sheets_print ) ):
    this_df_print = params_dict_new_natural[ param_sheets_print[s] ]
    this_df_print = this_df_print.round( 4 )
    this_df_print.to_excel( writer_Param_Natural_df, sheet_name = param_sheets_print[s], index=False)
writer_Param_Natural_df.save()
#---------------------------------
# Print updated 'Activity Ratio' projections
writer_AR_Proj_df = pd.ExcelWriter("./A1_Outputs/A-O_AR_Projections_COMPLETED.xlsx", engine='xlsxwriter')
param_sheets_print = list( AR_Base_proj_df_new.keys() )
for s in range( len( param_sheets_print ) ):
    this_df_print = AR_Base_proj_df_new[ param_sheets_print[s] ]
    this_df_print = this_df_print.round( 4 )
    this_df_print.to_excel( writer_AR_Proj_df, sheet_name = param_sheets_print[s], index=False)
writer_AR_Proj_df.save()
#
#***********************************************************************************
#
list_dicts = list( overall_param_df_dict.keys() )
for d in range( len( list_dicts ) ):
    df_to_print = overall_param_df_dict[ list_dicts[d] ]    
    df_to_print.to_csv( './A2_Output_Params/BAU/' + list_dicts[d] + '.csv', index=False, header=True)
#
list_dicts = list( overall_param_df_dict_ndp.keys() )
for d in range( len( list_dicts ) ):
    df_to_print = overall_param_df_dict_ndp[ list_dicts[d] ]
    df_to_print = df_to_print.replace( { 'Scenario':{ other_setup_params[ 'Main_Scenario' ]:"DDP"} } )
    df_to_print.to_csv( './A2_Output_Params/DDP/' + list_dicts[d] + '.csv', index=False, header=True)
    df_to_print = df_to_print.replace( { 'Scenario':{"DDP":"DDP70"} } )
    df_to_print.to_csv( './A2_Output_Params/DDP70/' + list_dicts[d] + '.csv', index=False, header=True)
    df_to_print = df_to_print.replace( { 'Scenario':{ "DDP70":"PA"} } )
    df_to_print.to_csv( './A2_Output_Params/PA/' + list_dicts[d] + '.csv', index=False, header=True)
#
end_2 = time.time()   
time_elapsed_2 = -start1 + end_2
print( str( time_elapsed_1 ) + ' seconds /', str( time_elapsed_2/60 ) + ' minutes' )
print('*: We just finished the printing of the results.')
#
#***********************************************************************************

lx = [  len( time_range_vector ), len( All_Tech_list ), len( [ other_setup_params['Timeslice'] ] ), len( All_Fuel_list ),
        len( emissions_list ), len( [ other_setup_params['Mode_of_Operation'] ] ), len( [ other_setup_params['Region'] ] )  ]
mx = max( lx )
df_structure_year = time_range_vector + [ '' for n in range( mx-lx[0] ) ]
df_structure_tech = All_Tech_list + [ '' for n in range( mx-lx[1] ) ]
df_structure_timeslice = [ other_setup_params['Timeslice'] ] + [ '' for n in range( mx-lx[2] ) ]
df_structure_fuel = All_Fuel_list + [ '' for n in range( mx-lx[3] ) ]
df_structure_emission = emissions_list + [ '' for n in range( mx-lx[4] ) ]
df_structure_moo = [ other_setup_params['Mode_of_Operation'] ] + [ '' for n in range( mx-lx[5] ) ]
df_structure_region = [ other_setup_params['Region'] ] + [ '' for n in range( mx-lx[6] ) ]
#
df_structure = pd.DataFrame( columns = [ 'Year','Tech','Timeslice','Fuel','Emission','MOO','Region' ] )
df_structure['Year'] = df_structure_year
df_structure['Tech'] = df_structure_tech
df_structure['Timeslice'] = df_structure_timeslice
df_structure['Fuel'] = df_structure_fuel
df_structure['Emission'] = df_structure_emission
df_structure['MOO'] = df_structure_moo
df_structure['Region'] = df_structure_region
writer_Structure_df = pd.ExcelWriter("A2_Structure_Lists.xlsx", engine='xlsxwriter')
df_structure.to_excel( writer_Structure_df, sheet_name = 'Lists', index=False)
writer_Structure_df.save()
#
#***********************************************************************************
print("********************************")
print("********************************")
print("proceso finalizado correctamente")
print("********************************")
print("********************************")
