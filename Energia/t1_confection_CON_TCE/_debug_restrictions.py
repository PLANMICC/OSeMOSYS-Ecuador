import pickle
from copy import deepcopy
import sys

# dict_scen = pickle.load(open("check_stable_scenarios_freeze.pickle", "rb"))
dict_scen = pickle.load(open("check_stable_scenarios.pickle", "rb"))

dict_BAU = dict_scen['BAU']


# A)
# Get the dictionaries to structure the fñeet

Fleet_Groups =              pickle.load(open('./A1_Outputs/A-O_Fleet_Groups.pickle',            "rb"))
### Ind_Groups =                pickle.load(open('./A1_Outputs/A-O_Ind_Groups.pickle',            "rb"))
Fleet_Groups_Distance =     pickle.load(open('./A1_Outputs/A-O_Fleet_Groups_Distance.pickle',   "rb"))
Fleet_Groups_OR =           pickle.load(open('./A1_Outputs/A-O_Fleet_Groups_OR.pickle',         "rb"))
Fleet_Groups_techs_2_dem =  pickle.load(open('./A1_Outputs/A-O_Fleet_Groups_T2D.pickle',        "rb"))
#
Fleet_Groups_inv = {}
for k in range(len(list(Fleet_Groups.keys()))):
    this_fleet_group_key = list(Fleet_Groups.keys())[k]
    for e in range(len(Fleet_Groups[this_fleet_group_key])):
        this_fleet_group_tech = Fleet_Groups[this_fleet_group_key][e]
        Fleet_Groups_inv.update({ this_fleet_group_tech:this_fleet_group_key })

all_gt_techs = list(Fleet_Groups_techs_2_dem.keys())


# B)
# Find issues with transport:
    
all_params_list = \
    ['AnnualEmissionLimit', 'AvailabilityFactor', 'CapacityFactor',
     'CapacityToActivityUnit', 'CapitalCost', 'DepreciationMethod',
     'DiscountRate', 'EmissionActivityRatio', 'EmissionsPenalty', 'FixedCost',
     'InputActivityRatio', 'ModelPeriodEmissionLimit', 'OperationalLife',
     'OutputActivityRatio', 'REMinProductionTarget', 'ResidualCapacity',
     'RETagFuel', 'RETagTechnology', 'SpecifiedAnnualDemand',
     'SpecifiedDemandProfile', 'TotalAnnualMaxCapacity',
     'TotalAnnualMaxCapacityInvestment', 'TotalAnnualMinCapacity',
     'TotalAnnualMinCapacityInvestment',
     'TotalTechnologyAnnualActivityLowerLimit',
     'TotalTechnologyAnnualActivityUpperLimit',
     'TotalTechnologyModelPeriodActivityLowerLimit',
     'TotalTechnologyModelPeriodActivityUpperLimit', 'VariableCost',
     'YearSplit']

"""
'TotalAnnualMaxCapacity'

'SpecifiedAnnualDemand'

'TotalTechnologyAnnualActivityLowerLimit'

'OutputActivityRatio'
"""


group_techs = list(Fleet_Groups_techs_2_dem.keys())

dem_sets = []
dem_sets_max_vals = {}
dem_sets_all = {}
time_range_vector = [y for y in range(2018, 2070+1)]
zeroes = [0 for y in range(len(time_range_vector))]
for gt in group_techs:
    if Fleet_Groups_techs_2_dem[gt] not in dem_sets:
        dem_sets.append(Fleet_Groups_techs_2_dem[gt])
        dem_sets_max_vals.update({dem_sets[-1]:deepcopy(zeroes)})
        dem_sets_all.update({dem_sets[-1]:deepcopy(zeroes)})

# Define demands:
dem_sets_vals = {}
for d in dem_sets:
    i_dem = [i for i, x in
             enumerate(dict_BAU['SpecifiedAnnualDemand']['f']) if x == d]
    vals_dem = \
        deepcopy(dict_BAU['SpecifiedAnnualDemand']['value'][i_dem[0]:i_dem[-1]+1])
    dem_sets_vals.update({d: vals_dem})


tamc_dict = {}

all_min_low_diffs = {}

dict_diff_chec_maxcap = {}
dict_diff_chec_lowact = {}

dict_gt_diff = {}

# Obtain max values:
for gt in group_techs:
    i_tamc = [i for i, x in
              enumerate(dict_BAU['TotalAnnualMaxCapacity']['t']) if x == gt]
    vals_tamc = \
        deepcopy(dict_BAU['TotalAnnualMaxCapacity']['value'][i_tamc[0]:i_tamc[-1]+1])
    tamc_dict.update({gt: vals_tamc})


    i_oar  = [i for i, x in
              enumerate(dict_BAU['OutputActivityRatio']['t']) if x == gt]
    vals_oar = \
        deepcopy(dict_BAU['OutputActivityRatio']['value'][i_oar[0]:i_oar[-1]+1])

    i_all  = [i for i, x in
              enumerate(dict_BAU['TotalTechnologyAnnualActivityLowerLimit']['t']) if x == gt]
    vals_all = \
        deepcopy(dict_BAU['TotalTechnologyAnnualActivityLowerLimit']['value'][i_all[0]:i_all[-1]+1])

    
    list_gt_diff = []
    for y in range(len(time_range_vector)):
        max_dem = float(vals_oar[y])*float(vals_tamc[y])
        min_dem = float(vals_oar[y])*float(vals_all[y])
        dem_sets_max_vals[Fleet_Groups_techs_2_dem[gt]][y] += max_dem
        dem_sets_all[Fleet_Groups_techs_2_dem[gt]][y] += min_dem

        list_gt_diff.append(max_dem-min_dem)
        if list_gt_diff[-1] < 0:
            print('alert! 0 - maxcap - lowlim of group techs is negative')
    
    dict_gt_diff.update({gt:list_gt_diff})
    
    fuel_techs = Fleet_Groups[gt]
    sum_lower_inner = deepcopy(zeroes)  # > Verify that the lower limit of fuel-techs is lower than the max cap of group techs:
    sum_maxcap_inner = deepcopy(zeroes)  # > Verify that the max cap is lower than the max cap:
    local_min_low_diffs = {}

    for ft in fuel_techs:

        i_tamc_ft = [i for i, x in
                    enumerate(dict_BAU['TotalAnnualMaxCapacity']['t']) if x == ft]
        if len(i_tamc_ft) > 0:
            vals_tamc_ft = deepcopy(dict_BAU['TotalAnnualMaxCapacity']['value'][i_tamc_ft[0]:i_tamc_ft[-1]+1])        
        else:
            vals_tamc_ft = deepcopy(zeroes)

        i_all_ft = [i for i, x in
                    enumerate(dict_BAU['TotalTechnologyAnnualActivityLowerLimit']['t']) if x == ft]
        if len(i_all_ft) > 0:
            vals_all_ft = deepcopy(dict_BAU['TotalTechnologyAnnualActivityLowerLimit']['value'][i_all_ft[0]:i_all_ft[-1]+1])
        else:
            vals_all_ft = deepcopy(zeroes)

        list_min_low_diff = []

        for y in range(len(time_range_vector)):
            sum_maxcap_inner[y] += float(vals_tamc_ft[y])
            sum_lower_inner[y] += float(vals_all_ft[y])
            
            list_min_low_diff.append(vals_tamc_ft[y] - vals_all_ft[y])
            
            if float(list_min_low_diff[-1]) < 0.0:
                print('alert! 1 - maxcap - lowlim of fuel techs is negative')
                sys.exit()

        local_min_low_diffs.update({ft:list_min_low_diff})

    all_min_low_diffs.update({gt: deepcopy(local_min_low_diffs)})
        

    diff_chec_maxcap = []  # must be positive for all entries
    for y in range(len(time_range_vector)):
        diff_chec_maxcap.append(sum_maxcap_inner[y] - float(vals_tamc[y]))
    dict_diff_chec_maxcap.update({gt:deepcopy(diff_chec_maxcap)})

    diff_chec_lowact = []  # must be positive for all entries
    for y in range(len(time_range_vector)):
        diff_chec_lowact.append(float(vals_tamc[y]) - sum_lower_inner[y])
    dict_diff_chec_lowact.update({gt:deepcopy(diff_chec_lowact)})

    # sys.exit()
    
# For all transport techs, verify that the max cap is greater than the lower limit:

# Obtain differences:
dem_sets_vals_diff = {}
for d in dem_sets:
    this_dem_list = dem_sets_vals[d]
    this_max_val_list = dem_sets_max_vals[d]
    diff_list = []
    for y in range(len(time_range_vector)):
        diff_list.append(this_max_val_list[y] - float(this_dem_list[y]))
        if float(diff_list[-1]) < 0.0:
            print('alert! 2 - maxcap*oar - demand of group techs is negative')
    dem_sets_vals_diff.update({d:diff_list})
    
    


# C)
# Find issues with electricity:
power_techs = [\
    'PP_GEO',
    'PP_HYDPACDAMSMA',
    'PP_HYDPACDAMMED',
    'PP_HYDPACDAMLAR',
    'PP_HYDAMADAMSMA',
    'PP_HYDAMADAMMED',
    'PP_HYDAMADAMLAR',
    'PP_HYDPACRORSMA',
    'PP_HYDPACRORMED',
    'PP_HYDPACRORLAR',
    'PP_HYDAMARORSMA',
    'PP_HYDAMARORMED',
    'PP_HYDAMARORLAR',
    'PP_SPV_US',
    'PP_WND_US',
    'PP_WND_OF',
    'PP_SPV_DG',
    'PP_SPV_US_H2',
    'PP_WND_US_H2',
    'PP_WND_OF_H2',
    'PPIHYDAMAELR',
    'PPIHYDPACELR',
    'PPISPVELR',
    'PPIWNDGAL',
    'PPISPVGAL',
    'PPIHYDAMACEM',
    'PPIHYDPACCEM',
    'PP_BGSICE',
    'PP_CHP',
    'PP_SUG',
    'PP_BMSTST',
    'PP_COA',
    'PP_FOIICE',
    'PP_FOITST',
    'PP_DSLICE',
    'PP_DSLTGS',
    'PP_NGSTGS',
    'PP_CRU',
    'PP_WASICE',
    'PPIDSLGALICE',
    'PPIDSLELRICE',
    'PPIDSLELRTST',
    'PPIDSLCEMTST',
    'PPICRUPETICE',
    'PPICRUPETTST',
    'PPIDSLPETTGS',
    'PPIDSLPETICE',
    'PPINGSPETTST',
    'PPINGSPETICE',
    'PPINGSPETTGS',
    ]

dict_pt_max_act = {}
dict_pt_all = {}
dict_pt_diff_act = {}
dict_pt_diff_cap = {}

error_pts_3 = []
error_pts_4 = []

for pt in power_techs:
    i_tamc = [i for i, x in
              enumerate(dict_BAU['TotalAnnualMaxCapacity']['t']) if x == pt]
    if len(i_tamc) > 0:
        vals_tamc = \
            deepcopy(dict_BAU['TotalAnnualMaxCapacity']['value'][i_tamc[0]:i_tamc[-1]+1])
        vals_tamc = [float(i) for i in vals_tamc]
    else:
        vals_tamc = deepcopy(zeroes)


    i_rescap = [i for i, x in
              enumerate(dict_BAU['ResidualCapacity']['t']) if x == pt]
    if len(i_rescap) > 0:
        vals_rescap = \
            deepcopy(dict_BAU['ResidualCapacity']['value'][i_rescap[0]:i_rescap[-1]+1])
        vals_rescap = [float(i) for i in vals_tamc]
    else:
        vals_rescap = deepcopy(zeroes)


    i_cf  = [i for i, x in
              enumerate(dict_BAU['CapacityFactor']['t']) if x == pt]
    if len(i_cf) > 0:
        vals_cf = \
            deepcopy(dict_BAU['CapacityFactor']['value'][i_cf[0]:i_cf[-1]+1])
        vals_cf = [float(i) for i in vals_cf]
    else:
        vals_cf = deepcopy(zeroes)


    i_af  = [i for i, x in
              enumerate(dict_BAU['AvailabilityFactor']['t']) if x == pt]
    if len(i_af) > 0:
        vals_af = \
            deepcopy(dict_BAU['AvailabilityFactor']['value'][i_af[0]:i_af[-1]+1])
        vals_af = [float(i) for i in vals_af]
    else:
        vals_af = deepcopy(zeroes)


    i_cau  = [i for i, x in
              enumerate(dict_BAU['CapacityToActivityUnit']['t']) if x == pt]
    if len(i_cau) > 0:
        vals_cau = \
            deepcopy(dict_BAU['CapacityToActivityUnit']['value'][i_cau[0]:i_cau[-1]+1])
        vals_cau = [float(i) for i in vals_cau]
    else:
        vals_cau = deepcopy(zeroes)


    i_all  = [i for i, x in
              enumerate(dict_BAU['TotalTechnologyAnnualActivityLowerLimit']['t']) if x == pt]
    if len(i_all) > 0:
        vals_all = \
            deepcopy(dict_BAU['TotalTechnologyAnnualActivityLowerLimit']['value'][i_all[0]:i_all[-1]+1])
        vals_all = [float(i) for i in vals_all]
    else:
        vals_all = deepcopy(zeroes)

    max_act = deepcopy(zeroes)
    diff_act = deepcopy(zeroes)
    diff_cap = deepcopy(zeroes)
    for y in range(len(i_tamc)):  # check tha maximum activty allowed
        max_act[y] = vals_cau[0]*vals_tamc[y]*vals_cf[y]*vals_af[y]
        diff_act[y] = max_act[y] - vals_all[y]
        if diff_act[y] < 0:
            print('alert! 3 - this is a mismatch between maximum generation and lower limit generation')
            if pt not in error_pts_3:
                error_pts_3.append(pt)
            # sys.exit()

        diff_cap[y] = vals_tamc[y] - vals_rescap[y]
        if diff_cap[y] < 0:
            print('alert! 4 - this is a mismatch between max capacity and residual capacity')
            if pt not in error_pts_4:
                error_pts_4.append(pt)
            # sys.exit()

    dict_pt_max_act.update({pt: deepcopy(max_act)})
    dict_pt_all.update({pt: deepcopy(vals_all)})
    dict_pt_diff_act.update({pt: deepcopy(diff_act)})
    dict_pt_diff_cap.update({pt: deepcopy(diff_cap)})

    # print(vals_tamc)
    # print(vals_cf)
    # print(vals_af)
    # print(vals_cau)
    # print(vals_all)


    # sys.exit()



print('Got till the end.')
