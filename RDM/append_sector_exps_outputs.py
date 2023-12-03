1# -*- coding: utf-8 -*-
"""
Created on Sat Jun  3 10:08:10 2023

@author: luisf
"""

import os, sys
import pandas as pd
import time
import pickle

# Disaggregate sectors from AFOLU:
techs_2_subsectors_afolu = {
    'Bosque':'USCUSS',
    'Tierra_agropecuaria':'USCUSS',
    'Pastizales':'USCUSS',
    'Humedal':'USCUSS',
    'Zona_atropica':'USCUSS',
    'Otras_tierras':'USCUSS',
    'Bosque_nativo':'USCUSS',
    'Bosque_nativo_protegido':'USCUSS_remociones',
    'Bosque_nativo_sinproteger':'USCUSS_remociones',
    'area_restaurada':'USCUSS_remociones',
    'Plantacion_forestal':'USCUSS',
    'Cultivos':'USCUSS',
    'Conservacion_sociobosqueII':'USCUSS',
    'Banano':'Agricultura',
    'Arroz':'Agricultura',
    'Cacao':'Agricultura',
    'Cafe':'Agricultura',
    'Cana':'Agricultura',
    'Maiz':'Agricultura',
    'Palma':'Agricultura',
    'Soya':'Agricultura',
    'Palmito':'Agricultura',
    'Legumbres':'Agricultura',
    'Cereales':'Agricultura',
    'Tuberculos':'Agricultura',
    'Fruta':'Agricultura',
    'Verduras':'Agricultura',
    'Floricolas':'Agricultura',
    'Otros_cultivos':'Agricultura',
    'Exp_Banano':'Agricultura',
    'Exp_Arroz':'Agricultura',
    'Exp_Cacao':'Agricultura',
    'Exp_Cafe':'Agricultura',
    'Exp_Cana':'Agricultura',
    'Exp_Maiz':'Agricultura',
    'Exp_Palma':'Agricultura',
    'Exp_Palmito':'Agricultura',
    'Exp_Legumbres':'Agricultura',
    'Exp_Cereales':'Agricultura',
    'Exp_Tuberculos':'Agricultura',
    'Exp_Fruta':'Agricultura',
    'Exp_Verduras':'Agricultura',
    'Exp_Floricolas':'Agricultura',
    'Pasturas':'USCUSS',
    'Ganaderia_criolla':'Ganadería',
    'Ganaderia_importada':'Ganadería',
    'Ganaderia_mestiza':'Ganadería',
    'Suelo':'USCUSS',
    'Imp_Arroz':'Agricultura',
    'Imp_Cafe':'Agricultura',
    'Imp_Cana':'Agricultura',
    'Imp_Maiz':'Agricultura',
    'Imp_Palma':'Agricultura',
    'Imp_Palmito':'Agricultura',
    'Imp_Legumbres':'Agricultura',
    'Imp_Cereales':'Agricultura',
    'Imp_Tuberculos':'Agricultura',
    'Imp_Fruta':'Agricultura',
    'Imp_Verduras':'Agricultura',
    'Imp_Carne':'Ganadería',
    'Gallinas_campos':'Ganadería',
    'Gallinas_planteles':'Ganadería',
    'Cambio_de_uso':'USCUSS',
    'Cambio_de_remocion':'USCUSS_remociones',
    'Vacuno_porcino':'Ganadería',
    'Vacuno_ovino':'Ganadería',
    'Vacuno_otras_especies':'Ganadería',
    'Exp_Soya':'Agricultura',
    'Exp_Carne':'Ganadería',
    'Exp_Leche':'Ganadería',
    'Imp_Leche':'Ganadería'}

# Disaggregate sectors from Energía:
techs_2_subsectors_energy = {
    'RSVNGS':'Energy',
    'RSVCRU':'Energy',
    'IMPPURDSL':'Energy',
    'IMPPURGSL':'Energy',
    'IMPCOA':'Energy',
    'IMPLPG':'Energy',
    'IMPFOI':'Energy',
    'IMPKJF':'Energy',
    'IMPCRU':'Energy',
    'IMPCOK':'Energy',
    'PROWAS':'Energy',
    'PROFIR':'Energy',
    'IMPNGS':'Energy',
    'PROSUG':'Energy',
    'PROACG':'Energy',
    'PROBMS':'Energy',
    'PROBGS':'Energy',
    'IMPELE':'Energy',
    'PP_GEO':'Energy',
    'PP_HYDPACDAMSMA':'Energy',
    'PP_HYDPACDAMMED':'Energy',
    'PP_HYDPACDAMLAR':'Energy',
    'PP_HYDAMADAMSMA':'Energy',
    'PP_HYDAMADAMMED':'Energy',
    'PP_HYDAMADAMLAR':'Energy',
    'PP_HYDPACRORSMA':'Energy',
    'PP_HYDPACRORMED':'Energy',
    'PP_HYDPACRORLAR':'Energy',
    'PP_HYDAMARORSMA':'Energy',
    'PP_HYDAMARORMED':'Energy',
    'PP_HYDAMARORLAR':'Energy',
    'PP_SPV_US':'Energy',
    'PP_WND_US':'Energy',
    'PP_WND_OF':'Energy',
    'PP_SPV_DG':'Energy',
    'PP_SPV_US_H2':'Energy',
    'PP_WND_US_H2':'Energy',
    'PP_WND_OF_H2':'Energy',
    'PPIHYDAMAELR':'Energy',
    'PPIHYDPACELR':'Energy',
    'PPISPVELR':'Energy',
    'PPIWNDGAL':'Energy',
    'PPISPVGAL':'Energy',
    'PPIHYDAMACEM':'Energy',
    'PPIHYDPACCEM':'Energy',
    'HYDPROELEISO':'Energy',
    'PP_NGSTGS':'Energy',
    'PPINGSPETTST':'Energy',
    'PPINGSPETICE':'Energy',
    'PPINGSPETTGS':'Energy',
    'HYDPRONGS':'Energy',
    'HYD_DISTR':'Energy',
    'ELE_DISTR':'Energy',
    'HYDPROELEGRI':'Energy',
    'BLEND_GSL':'Energy',
    'PP_DSLICE':'Energy',
    'PP_DSLTGS':'Energy',
    'PPIDSLGALICE':'Energy',
    'PPIDSLELRICE':'Energy',
    'PPIDSLELRTST':'Energy',
    'PPIDSLCEMTST':'Energy',
    'PPIDSLPETTGS':'Energy',
    'PPIDSLPETICE':'Energy',
    'BLEND_DSL':'Energy',
    'CENGASPRO':'Energy',
    'NGS_DISTR':'Energy',
    'PPIFOIPETICE':'Energy',
    'PP_FOIICE':'Energy',
    'PP_FOITST':'Energy',
    'ELE_TRANS':'Energy',
    'REFCRU':'Energy',
    'REFCRUDSL':'Energy',
    'REFCRUGSL':'Energy',
    'REFCRULPG':'Energy',
    'REFCRUFOI':'Energy',
    'REFCRUKJF':'Energy',
    'REFCRUCOK':'Energy',
    'REFNONENE':'Energy',
    'REFCRURED':'Energy',
    'PP_CRU':'Energy',
    'PPICRUPETICE':'Energy',
    'PPICRUPETTST':'Energy',
    'PP_WASICE':'Energy',
    'PP_CHP':'Energy',
    'PP_SUG':'Energy',
    'PROETA':'Energy',
    'PRONGS':'Energy',
    'PROCRU':'Energy',
    'PP_COA':'Energy',
    'PP_BMSTST':'Energy',
    'PROBIODSL':'Energy',
    'HYDPROBIO':'Energy',
    'PP_BGSICE':'Energy',
    'CENGASLPG':'Energy',
    'CENGASGSL':'Energy',
    'T5ELEAGR':'Energy',
    'T5PURGSLAGR':'Energy',
    'T5LPGAGR':'Energy',
    'T5NOEAGR':'Energy',
    'T5ELECON':'Energy',
    'T5PURDSLCON':'Energy',
    'T5PURGSLCON':'Energy',
    'T5KJFCON':'Energy',
    'T5LPGCON':'Energy',
    'T5NOECON':'Energy',
    'T5PURDSLCOM':'Energy',
    'T5ELECOM':'Energy',
    'T5FOICOM':'Energy',
    'T5PURGSLCOM':'Energy',
    'T5LPGCOM':'Energy',
    'T5PURDSLIND':'Energy',
    'T5ELEIND':'Energy',
    'T5FIRIND':'Energy',
    'T5FOIIND':'Energy',
    'T5PURGSLIND':'Energy',
    'T5HYDIND':'Energy',
    'T5COKIND':'Energy',
    'T5LPGIND':'Energy',
    'T5NGSIND':'Energy',
    'T5SUGIND':'Energy',
    'T5HECIND':'Energy',
    'T5ELERES':'Energy',
    'T5FIRRES':'Energy',
    'T5LPGRES':'Energy',
    'T5NGSRES':'Energy',
    'T5CRUEXP':'Energy',
    'T5REDCRUEXP':'Energy',
    'T5PURDSLEXP':'Energy',
    'T5ELEEXP':'Energy',
    'T5FOIEXP':'Energy',
    'T5PURGSLEXP':'Energy',
    'T5LPGEXP':'Energy',
    'T5BMSEXP':'Energy',
    'T5PURGSLAERTRN':'Transport',
    'T5KJFAERTRN':'Transport',
    'T5PURDSLSHITRN':'Transport',
    'T5FOISHITRN':'Transport',
    'T5PURGSLSHITRN':'Transport',
    'T5PROGAS':'Energy',
    'T5CRUTRN':'Transport',
    'T5PURGSLREF':'Energy',
    'T5KJFREF':'Energy',
    'T5PURDSLREF':'Energy',
    'T5FOIREF':'Energy',
    'T5LPGREF':'Energy',
    'T5BUN':'Energy',
    'T4_DSLPUB':'Transport',
    'T4_NGSPUB':'Transport',
    'T4_HYDPUB':'Transport',
    'T4_ELEPUB':'Transport',
    'T4_LPGPUB':'Transport',
    'T4_GSLPUB':'Transport',
    'T4_ELEPRI':'Transport',
    'T4_GSLPRI':'Transport',
    'T4_DSLPRI':'Transport',
    'T4_NGSPRI':'Transport',
    'T4_LPGPRI':'Transport',
    'T4_DSLHEA':'Transport',
    'T4_HYDHEA':'Transport',
    'T4_ELEHEA':'Transport',
    'T4_GSLHEA':'Transport',
    'T4_LPGHEA':'Transport',
    'T4_DSLMED':'Transport',
    'T4_NGSMED':'Transport',
    'T4_HYDMED':'Transport',
    'T4_ELEMED':'Transport',
    'T4_GSLMED':'Transport',
    'T4_LPGMED':'Transport',
    'T4_DSLLIG':'Transport',
    'T4_NGSLIG':'Transport',
    'T4_ELELIG':'Transport',
    'T4_GSLLIG':'Transport',
    'T4_LPGLIG':'Transport',
    'TRNMICHYBDSL':'Transport',
    'TRNMICGSL':'Transport',
    'TRNMICHYD':'Transport',
    'TRNMICELE':'Transport',
    'TRNMICDSL':'Transport',
    'TRNMICLPG':'Transport',
    'TRNBUSHYBDSL':'Transport',
    'TRNBUSNGV':'Transport',
    'TRNBUSHYD':'Transport',
    'TRNBUSELE':'Transport',
    'TRNBUSDSL':'Transport',
    'TRNBUSLPG':'Transport',
    'TRNTAXHYBDSL':'Transport',
    'TRNTAXELE':'Transport',
    'TRNTAXDSL':'Transport',
    'TRNTAXHYBGSL':'Transport',
    'TRNTAXGSL':'Transport',
    'TRNTAXLPG':'Transport',
    'TRNPASRAIHYD':'Transport',
    'TRNPASRAIELE':'Transport',
    'TRNPASRAIDSL':'Transport',
    'TRNMOTELE':'Transport',
    'TRNMOTGSL':'Transport',
    'TRNSEDELE':'Transport',
    'TRNSEDDSL':'Transport',
    'TRNSEDHYBGSL':'Transport',
    'TRNSEDGSL':'Transport',
    'TRNSEDLPG':'Transport',
    'TRNSUVHYBDSL':'Transport',
    'TRNSUVNGV':'Transport',
    'TRNSUVELE':'Transport',
    'TRNSUVDSL':'Transport',
    'TRNSUVHYBGSL':'Transport',
    'TRNSUVGSL':'Transport',
    'TRNSUVLPG':'Transport',
    'TRNCAMHYBDSL':'Transport',
    'TRNCAMNGV':'Transport',
    'TRNCAMELE':'Transport',
    'TRNCAMDSL':'Transport',
    'TRNCAMHYBGSL':'Transport',
    'TRNCAMGSL':'Transport',
    'TRNCAMLPG':'Transport',
    'TRNFREHEAHYBDSL':'Transport',
    'TRNFREHEAHYD':'Transport',
    'TRNFREHEAELE':'Transport',
    'TRNFREHEADSL':'Transport',
    'TRNFREHEAGSL':'Transport',
    'TRNFREHEALPG':'Transport',
    'TRNFREMEDHYBDSL':'Transport',
    'TRNFREMEDNGV':'Transport',
    'TRNFREMEDHYD':'Transport',
    'TRNFREMEDELE':'Transport',
    'TRNFREMEDDSL':'Transport',
    'TRNFREMEDGSL':'Transport',
    'TRNFREMEDLPG':'Transport',
    'TRNFRELIGHYBDSL':'Transport',
    'TRNFRELIGNGV':'Transport',
    'TRNFRELIGELE':'Transport',
    'TRNFRELIGDSL':'Transport',
    'TRNFRELIGHYBGSL':'Transport',
    'TRNFRELIGGSL':'Transport',
    'TRNFRELIGLPG':'Transport',
    'TRNCATTRUELE':'Transport',
    'TRNFRERAIHYD':'Transport',
    'TRNFRERAIELE':'Transport',
    'TRNFRERAIDSL':'Transport',
    'TRNMIC':'Transport',
    'TRNBUS':'Transport',
    'TRNTAX':'Transport',
    'TRNPASRAI':'Transport',
    'TRNMOT':'Transport',
    'TRNSED':'Transport',
    'TRNSUV':'Transport',
    'TRNCAM':'Transport',
    'TRNFREHEA':'Transport',
    'TRNFREMED':'Transport',
    'TRNFRELIG':'Transport',
    'TRNCATTRU':'Transport',
    'TRNFRERAI':'Transport',
    'EXTRATECH':'Transport',
    'TRANTE_NOMOT':'Transport'}

start1 = time.time()

dir_exp = './t3a_experiments'
submodel_folders = os.listdir(dir_exp)
submodel_folders = [i for i in submodel_folders if 'Integrated' not in i]

# print('Cut through the model manually')
# sys.exit()

list_inputs, list_outputs = [], []
list_inputs_sm, list_outputs_sm = [], []
list_inputs_cols, list_outputs_cols = [], []

# Iterate across folders:
for folder in submodel_folders:
    inner_dir = dir_exp + '/' + folder
    inner_folders = os.listdir(inner_dir)

    submodel_name = folder.split('_')[-1]

    output_csv_name_raw = [i for i in inner_folders if 'Output.csv' in i]
    output_csv_name = output_csv_name_raw[0]
    output_df = pd.read_csv(
        inner_dir + '/' + output_csv_name, index_col=None, header=0)
    output_df['Submodel'] = submodel_name
    list_outputs.append(output_df)
    list_outputs_cols.append(output_df.columns.tolist())
    print(list_outputs_cols[-1])
    list_outputs_sm.append(submodel_name)

    input_csv_name_raw = [i for i in inner_folders if 'Input.csv' in i]
    input_csv_name = input_csv_name_raw[0]
    input_df = pd.read_csv(
        inner_dir + '/' + input_csv_name, index_col=None, header=0)
    input_df['Submodel'] = submodel_name
    list_inputs.append(input_df)
    list_inputs_cols.append(input_df.columns.tolist())
    list_inputs_sm.append(submodel_name)

    # print('review the elements')
    # sys.exit()


# NOTE: while list_inputs_cols is homogenous across model, the list_outputs is not

'''
# Extract the lists at indices 1, 2, 3
sublists = [list_outputs_cols[i] for i in [1, 2, 3]]
'''

# Find the most comprehensive list among them
'''
most_comprehensive_list = max(sublists, key=len)
'''
most_comprehensive_list_in = max(list_inputs_cols, key=len)
most_comprehensive_list_out = max(list_outputs_cols, key=len)

'''
# Prune the list at index 0 based on the most comprehensive list
list_outputs_cols_0 = [x for x in list_outputs_cols[0] if x in most_comprehensive_list]
'''

# We must re-arrange so that we have all elements needed:

# Iterate across folders again:
for afolder in range(len(submodel_folders)):
    list_outputs[afolder] = \
        list_outputs[afolder].reindex(columns=most_comprehensive_list_out)
    
    xorig = list_outputs[afolder].columns.tolist()
    if list_outputs[afolder].columns.tolist() == most_comprehensive_list_out:
        print('Success')
    else:
        print('Error')
        sys.exit()

    """
    # Fill new columns with None or np.nan
    list_outputs[afolder] = list_outputs[afolder].fillna(0)
    """

    # print('check this please')
    # sys.exit()

# Store the final inputs:
# df_input_all = pd.concat(list_inputs, axis=0, ignore_index=True)
df_output_all = pd.concat(list_outputs, axis=0, ignore_index=True)

with open('list_outputs.pickle', 'wb') as handle:
    pickle.dump( list_outputs, handle, protocol=pickle.HIGHEST_PROTOCOL)
handle.close()

with open('list_outputs.pickle', 'rb') as file_list_outputs:
    list_outputs = pickle.load(file_list_outputs)

# Rewrite the elements of the subsector:
df_output_all['Submodel'] = \
    df_output_all['Technology'].map(
        techs_2_subsectors_afolu).fillna(df_output_all['Submodel'])
df_output_all['Submodel'] = \
    df_output_all['Technology'].map(
        techs_2_subsectors_energy).fillna(df_output_all['Submodel'])

# Find null and valid columns
exclude_for_simplicity = [
    'Capex_GDP', 'FixedOpex_GDP', 'VarOpex_GDP', 'Opex_GDP',
    'Externalities_GDP', 'AnnualEmissions', 'AnnualTechnologyEmissionsPenalty',
    'DiscountedTechnologyEmissionsPenalty', 'TotalDiscountedCost']
null_columns_final, valid_columns_final = [], []
for col in df_output_all.columns.tolist():
    if df_output_all[col].isnull().all():
        null_columns_final.append(col)
    elif col not in exclude_for_simplicity:
        valid_columns_final.append(col)

df_output_all = df_output_all[valid_columns_final]

# df_input_all.to_csv ( 'OSEMOSYS_ECU_Integrated_Input.csv', index = None, header=True)
df_output_all.to_csv ( 'OSEMOSYS_ECU_Integrated_Output.csv', index = None, header=True)
print('\nElements printed!')

end1 = time.time()
time_elapsed_1 = -start1 + end1
print( 'Time elapsed:', str( time_elapsed_1 ) + ' seconds' )

# df_input_all_read = pd.read_csv('OSEMOSYS_ECU_Integrated_Input.csv', index_col=None, header=0)
df_output_all_read = pd.read_csv('OSEMOSYS_ECU_Integrated_Output.csv', index_col=None, header=0)

