import pandas as pd


data_output1 = './2_Model/BAU/data_land_BAU_Output.csv'
data_output2 = './2_Model/PA/data_land_PA_Output.csv'
data_output3 = './2_Model/DDP50/data_land_DDP50_Output.csv'
data_output4 = './2_Model/DDP70/data_land_DDP70_Output.csv'

df1 = pd.read_csv(data_output1)
df2 = pd.read_csv(data_output2)
df3 = pd.read_csv(data_output3)
df4 = pd.read_csv(data_output4)

dff2 = df1.append(df2)
dff3 = dff2.append(df3)
dff4 = dff3.append(df4)

    
dff4['Capex2023'] = dff4['CapitalInvestment']
dff4['FixedOpex2023'] = dff4['AnnualFixedOperatingCost']
dff4['VarOpex2023'] = dff4['AnnualVariableOperatingCost']
dff4['Opex2023'] = dff4['OperatingCost']
dff4['Externalities2023'] = dff4['AnnualTechnologyEmissionPenaltyByEmission']


dff4.to_csv( './2_Model/f0_OSMOSYS_ECU_Output.csv', index = None, header=True)