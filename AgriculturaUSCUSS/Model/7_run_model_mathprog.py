import os, os.path
import time
import re
import csv
import xlrd
import linecache
from copy import deepcopy
import gc

sce = 'DDP50'

def set_txt_list( model_to_run ):
    #
    txt_list_raw = os.listdir( './2_Model/' + sce + '/')
    #
    global txt_list, structural_list
    txt_list = [e for e in txt_list_raw if ( '.txt' in e ) and ( model_to_run in e ) ]
    structural_list = []
    #
    for e in range( len( txt_list ) ):
        structural_list.append( 'STRUCTURE_OSEMOSYS_GUA_LAND.xls' )

############################################################################################################################################################################################################

def data_processor( case, model_to_run_gen, sce_gen ):
    # 1 - Always call the structure fo the model:
    
    table1 = xlrd.open_workbook( "0_Ref/" + str( structural_list[ case ] ) ) # works for all strategies
    print("$$$$$$")
    print( str( structural_list[ case ] ) )
    print("$$$$$$")
    sheet_sets_structure = table1.sheet_by_index(0) # 11 columns
    sheet_params_structure = table1.sheet_by_index(1) # 30 columns
    sheet_vars_structure = table1.sheet_by_index(2) # 43 columns
    #
    S_DICT_sets_structure = {'set':[],'initial':[],'number_of_elements':[],'elements_list':[]}
    for col in range(1,11+1):
        S_DICT_sets_structure['set'].append( sheet_sets_structure.cell_value(rowx=0, colx=col) )
        S_DICT_sets_structure['initial'].append( sheet_sets_structure.cell_value(rowx=1, colx=col) )
        S_DICT_sets_structure['number_of_elements'].append( int( sheet_sets_structure.cell_value(rowx=2, colx=col) ) )
        #
        element_number = int( sheet_sets_structure.cell_value(rowx=2, colx=col) )
        this_elements_list = []
        if element_number > 0:
            for n in range( 1, element_number+1 ):
                this_elements_list.append( sheet_sets_structure.cell_value(rowx=2+n, colx=col) )
        S_DICT_sets_structure['elements_list'].append( this_elements_list )
    #
    S_DICT_params_structure = {'category':[],'parameter':[],'number_of_elements':[],'index_list':[]}
    param_category_list = []
    for col in range(1,30+1):
        if str( sheet_params_structure.cell_value(rowx=0, colx=col) ) != '':
            param_category_list.append( sheet_params_structure.cell_value(rowx=0, colx=col) )
        S_DICT_params_structure['category'].append( param_category_list[-1] )
        S_DICT_params_structure['parameter'].append( sheet_params_structure.cell_value(rowx=1, colx=col) )
        S_DICT_params_structure['number_of_elements'].append( int( sheet_params_structure.cell_value(rowx=2, colx=col) ) )
        #
        index_number = int( sheet_params_structure.cell_value(rowx=2, colx=col) )
        this_index_list = []
        for n in range(1, index_number+1):
            this_index_list.append( sheet_params_structure.cell_value(rowx=2+n, colx=col) )
        S_DICT_params_structure['index_list'].append( this_index_list )
    #
    S_DICT_vars_structure = {'category':[],'variable':[],'number_of_elements':[],'index_list':[]}
    var_category_list = []
    for col in range(1,43+1):
        if str( sheet_vars_structure.cell_value(rowx=0, colx=col) ) != '':
            var_category_list.append( sheet_vars_structure.cell_value(rowx=0, colx=col) )
        S_DICT_vars_structure['category'].append( var_category_list[-1] )
        S_DICT_vars_structure['variable'].append( sheet_vars_structure.cell_value(rowx=1, colx=col) )
        S_DICT_vars_structure['number_of_elements'].append( int( sheet_vars_structure.cell_value(rowx=2, colx=col) ) )
        #
        index_number = int( sheet_vars_structure.cell_value(rowx=2, colx=col) )
        this_index_list = []
        for n in range(1, index_number+1):
            this_index_list.append( sheet_vars_structure.cell_value(rowx=2+n, colx=col) )
        S_DICT_vars_structure['index_list'].append( this_index_list )
    #-------------------------------------------#
    #
    all_vars = S_DICT_vars_structure['variable']
    #
    all_vars_output_dict = [ {} for e in range( len( txt_list ) ) ]
    #
    output_header = ['Strategy','Fuel','Fuel.DESCRIPTION','Technology','Technology.DESCRIPTION','Emission','Emission.DESCRIPTION','Year']
    #-------------------------------------------------------#
    for v in range( len( all_vars ) ):
        output_header.append( all_vars[v] )
    #-------------------------------------------------------#
    vars_as_appear = []
    # data_name = str( './Casos/' + txt_list[case] ) + '/' + str(txt_list[case]) + '_output.txt'
    case_name = txt_list[case].replace('.txt','')
    #
    data_name = './2_Model/' + sce + '/' + str( case_name ) + '_output.txt'
    print( data_name )
    #
    
    string_ini = ' No. Column name  St   Activity     Lower bound   Upper bound    Marginal'
    string_end = 'Karush-Kuhn-Tucker'
    
    file_data_output = open( './2_Model/'+sce_gen + '/data_land_output.txt', 'r')
  
    # setting flag and index to 0
    index1 = 0
    index2 = 0
  
        # Loop through the file line by line
    for line in file_data_output:  
        index1 = index1 + 1 
        index2 = index2 + 1
      
    # checking string is present in line or not
        if string_ini in line:
            ini_line = index1 + 2

        if string_end in line:
            end_line = index2 - 1

    #
    for n in range(ini_line, end_line, 2 ):
        structure_line_raw = linecache.getline(data_name, n)
        structure_list_raw = structure_line_raw.split(' ')
        # print( structure_line_raw, data_name, n, ini_line, end_line )
        # time.sleep(20)
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
    output_adress = './2_Model'
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
                data_row[0] = sce
                data_row[1] = this_combination[0]
                data_row[3] = this_combination[1]
                data_row[5] = this_combination[2]
                # data_row[7] = this_combination[3]
                data_row[7] = this_combination[4]
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
    # complete_years = [ '2015', '2019', '2025', '2030', '2035', '2040', '2045', '2050' ]
    complete_years = [ str(a_year) for a_year in range(2018,2070+1,1) ]
    #
    for n in range( len( non_year_combination_list ) ):
        if len( non_year_combination_list_years[n] ) != len(complete_years):
            #
            this_existing_combination = non_year_combination_list[n]
            # print('flag 1', this_existing_combination )
            this_existing_combination.append( '' )
            # print('flag 2', this_existing_combination )
            this_existing_combination.append( non_year_combination_list_years[n][0] )
            # print('flag 3', this_existing_combination )
            ref_index = combination_list.index( this_existing_combination )
            this_existing_data_row = deepcopy( data_row_list[ ref_index ] )
            #
            for n2 in range( len(complete_years) ):
                #
                if complete_years[n2] not in non_year_combination_list_years[n]:
                    #
                    data_row = ['' for n in range( len( output_header ) ) ]
                    data_row[0] = sce
                    data_row[1] = non_year_combination_list[n][0]
                    data_row[3] = non_year_combination_list[n][1]
                    data_row[5] = non_year_combination_list[n][2]
                    data_row[7] = complete_years[n2]
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
    with open( output_adress + '/' + sce + '/' + case_name + '_' + sce + '_Output' + '.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow( output_header )
        for n in range( len( data_row_list ) ):
            csvwriter.writerow( data_row_list[n] )
    #-----------------------------------------------------------------------------------------------------------%
    gc.collect(generation=2)
    time.sleep(0.05)
    #-----------------------------------------------------------------------------------------------------------%

############################################################################################################################################################################################################

def main_executer( n1 ):
    #
    set_txt_list( model_to_run )
    #
    file_aboslute_address = os.path.abspath("7_run_model_mathprog.py")
    file_adress = re.escape( file_aboslute_address.replace( '7_run_model_mathprog.py', '' ) ).replace( '\:', ':' )
    #
    print('$$')
    print( txt_list )
    print('$$')
    data_file = file_adress + r'2_Model\\' + sce + '\\' + str( txt_list[n1] )
    #
    str1 = "start /B start cmd.exe @cmd /k cd " + file_adress
    #
    output_file = data_file.replace('.txt','') + '_output' + '.txt'
    #
    str2 = "glpsol -m Long_Model.txt -d " + str( data_file )  +  " -o " + str(output_file)
    os.system( str1 and str2 )
    time.sleep(1)
    #
    print('I finished this run, now I will process')
    data_processor( n1, model_to_run, sce )

global model_to_run
model_to_run = 'land'
set_txt_list( model_to_run )

for n1 in range( len(txt_list) ):
    main_executer(n1)