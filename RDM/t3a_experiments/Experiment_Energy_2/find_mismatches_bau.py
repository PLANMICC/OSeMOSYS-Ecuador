# -*- coding: utf-8 -*-
"""
Created on Thu Aug 24 18:54:22 2023

@author: luisf
"""

import os
import sys
from copy import deepcopy
import time
import pickle

# running_for_last_time = False
running_for_last_time = True

start1 = time.time()

technology_list = [
    "PP_GEO",
    "PP_HYDPACDAMSMA",
    "PP_HYDPACDAMMED",
    "PP_HYDPACDAMLAR",
    "PP_HYDAMADAMSMA",
    "PP_HYDAMADAMMED",
    "PP_HYDAMADAMLAR",
    "PP_HYDPACRORSMA",
    "PP_HYDPACRORMED",
    "PP_HYDPACRORLAR",
    "PP_HYDAMARORSMA",
    "PP_HYDAMARORMED",
    "PP_HYDAMARORLAR",
    "PP_SPV_US",
    "PP_WND_US",
    "PP_WND_OF",
    "PP_SPV_DG",
    "PP_SPV_US_H2",
    "PP_WND_US_H2",
    "PP_WND_OF_H2",
    "PPIHYDAMAELR",
    "PPIHYDPACELR",
    "PPISPVELR",
    "PPIWNDGAL",
    "PPISPVGAL",
    "PPIHYDAMACEM",
    "PPIHYDPACCEM",
    "PP_NGSTGS",
    "PPINGSPETTST",
    "PPINGSPETICE",
    "PPINGSPETTGS",
    "PP_DSLICE",
    "PP_DSLTGS",
    "PPIDSLGALICE",
    "PPIDSLELRICE",
    "PPIDSLELRTST",
    "PPIDSLCEMTST",
    "PPIDSLPETTGS",
    "PPIDSLPETICE",
    "PPIFOIPETICE",
    "PP_FOIICE",
    "PP_FOITST",
    "PP_CRU",
    "PPICRUPETICE",
    "PPICRUPETTST",
    "PP_WASICE",
    "PP_CHP",
    "PP_SUG",
    "PP_COA",
    "PP_BMSTST",
    "PP_BGSICE"
]

tech_dict = {}

# Initialize dictionary of dictionaries
for tech in technology_list:
    tech_dict[tech] = {
        'AvailabilityFactor': None,  # Placeholder values, can be replaced later
        'CapacityFactor': None,
        'TotalAnnualMaxCapacity': None,
        'TotalTechnologyAnnualActivityLowerLimit': None
    }

# First we gotta open the BAUs and iterate across each file, we will focus on power plant issues and assume transport does not have any issues

# Specify the directory path here
dir_bau_files = './Experimental_Platform/Futures/BAU'

# List all entries in the directory
all_entries = os.listdir(dir_bau_files)

# Filter only the directories
folders = [entry for entry in all_entries if os.path.isdir(os.path.join(dir_bau_files, entry))]

dict_store_lines = {'Original':{}, 'Updated':{}}

# print(folders)

# Now let us iterate across the folders and read the input files; we will focus on text files
# folders = [folders[0]]
for f in folders:
    all_txt_in_folder = [afile for afile in os.listdir(dir_bau_files + '/' + f) if '.txt' in afile]
    print(all_txt_in_folder)
    # txt_file = dir_bau_files + '/' + f  + '/' + all_txt_in_folder[0]
    txt_file_temp = dir_bau_files + '/' + f  + '/' + 'temp_file.txt'

    # Initialize empty list to hold files without '_output'
    txt_files_without_output = []

    # Initialize empty list to hold '_output' files to be deleted
    txt_files_to_delete = []

    for afile in all_txt_in_folder:
        full_path = os.path.join(dir_bau_files, f, afile)
        if '_output' in afile:
            txt_files_to_delete.append(full_path)
        else:
            txt_files_without_output.append(full_path)

    # Delete '_output' files
    for filepath in txt_files_to_delete:
        os.remove(filepath)
        print(f"Deleted file: {filepath}")

    # Update all_txt_in_folder after deletion
    all_txt_in_folder = [os.path.basename(filepath) for filepath in txt_files_without_output]

    print(f"After: {all_txt_in_folder}")

    if txt_files_without_output:  # Check if there is at least one item in the list
        txt_file = txt_files_without_output[0]
        print(f"Selected file: {txt_file}")
    else:
        print("No suitable txt files found.")

    act_file = open(txt_file, 'r')
    line_list = deepcopy(act_file.readlines())
    line_list_orig = deepcopy(line_list)
    act_file.close()

    read_all_lines = False
    #read_all_lines = True
    if read_all_lines:
        # Iterate over the lines
        for idx, line in enumerate(line_list):
            # If we reach the start point, set the start flag to True    
            if "param" in line:
                print(line)
                pass
        print('Here we are checking the reading of all lines')
        sys.exit()

    # The goal is to calculate the max production and contrast to the lower limit:

    ###########################################################################
    # A) grab the Availabiitly factor
    # Flags for start and end
    start_av_fac = False
    values_av_fac = []
    
    # Iterate over the lines
    for idx, line in enumerate(line_list):
        # If we reach the start point, set the start flag to True

        if "param" in line:
            # print(line)
            pass

        if "param AvailabilityFactor" in line:
            start_av_fac = True
            start_index = idx
            continue
        # If we reach the end point, break the loop
        if line.strip() == ";" and start_av_fac:
            end_index = idx
            break
        # If the start flag is set, add the line to the values
        if start_av_fac:
            values_av_fac.append(line.strip())

    # Once you have the start and end indices, you can remove those lines from line_list
    line_list_raw1 = deepcopy(line_list)
    if start_index is not None and end_index is not None:
        del line_list[start_index:end_index+1]  # +1 because Python slicing is exclusive of the end index

    header = values_av_fac[1].strip().split()  # Extract the years
    data_dict_1 = {}
    for loc_line in values_av_fac[2:]:
        values = loc_line.strip().split()
        if not values:  # Skip empty lines
            continue
        tech, *years_data = values
        data_dict_1[tech] = dict(zip(header, map(float, years_data)))

    # print('review this 1')
    print('-------------------------------------------------------- \n')
    #sys.exit()

    # Update the tech_dict with the parsed data
    for tech, values in data_dict_1.items():
        if tech in tech_dict:
            tech_dict[tech]['AvailabilityFactor'] = values

    ###########################################################################
    # B) grab the Capactiy factor
    start_cf_fac = False
    values_cf_fac = []
    
    # Iterate over the lines
    for idx, line in enumerate(line_list):
        # If we reach the start point, set the start flag to True

        if "param" in line:
            # print(line)
            pass

        if "param CapacityFactor" in line:
            start_cf_fac = True
            start_index = idx
            continue
        # If we reach the end point, break the loop
        if line.strip() == ";" and start_cf_fac:
            end_index = idx
            break
        # If the start flag is set, add the line to the values
        if start_cf_fac:
            values_cf_fac.append(line.strip())

    # Once you have the start and end indices, you can remove those lines from line_list
    line_list_raw2 = deepcopy(line_list)
    if start_index is not None and end_index is not None:
        del line_list[start_index:end_index+1]  # +1 because Python slicing is exclusive of the end index

    i_cf = 0
    while i_cf < len(values_cf_fac):
        if values_cf_fac[i_cf].startswith("["):
            tech_name = values_cf_fac[i_cf].split(",")[1]
            tech_values = list(map(float, values_cf_fac[i_cf + 2].split()[1:]))  # Adjust the range according to how many years' data you want
            tech_dict[tech_name]['CapacityFactor'] = tech_values
        i_cf += 3  # Skip to the next technology block

    print('review this 2')
    print('-------------------------------------------------------- \n')
    #sys.exit()

    """
    header = values_cf_fac[1].strip().split()  # Extract the years
    data_dict_2 = {}
    for loc_line in values_cf_fac[2:]:
        values = loc_line.strip().split()
        if not values:  # Skip empty lines
            continue
        tech, *years_data = values
        data_dict_2[tech] = dict(zip(header, map(float, years_data)))

        print('review this 2')
        sys.exit()

    # Update the tech_dict with the parsed data
    for tech, values in data_dict_2.items():
        if tech in tech_dict:
            tech_dict[tech]['CapacityFactor'] = values
    """

    ###########################################################################
    # C) grab the Total Annual Max Capacity
    start_tamc_fac = False
    values_tamc_fac = []
    
    # Iterate over the lines
    for idx, line in enumerate(line_list):
        # If we reach the start point, set the start flag to True
        
        if "param" in line:
            # print(line)
            pass
        
        if "param TotalAnnualMaxCapacity" in line:
            start_tamc_fac = True
            start_index = idx
            continue
        # If we reach the end point, break the loop
        if line.strip() == ";" and start_tamc_fac:
            end_index = idx
            break
        # If the start flag is set, add the line to the values
        if start_tamc_fac:
            values_tamc_fac.append(line.strip())

    print('review this 3')
    print('-------------------------------------------------------- \n')
    # sys.exit()

    # Once you have the start and end indices, you can remove those lines from line_list
    line_list_raw3 = deepcopy(line_list)
    if start_index is not None and end_index is not None:
        del line_list[start_index:end_index+1]  # +1 because Python slicing is exclusive of the end index

    header = values_tamc_fac[1].strip().split()  # Extract the years
    data_dict_3 = {}
    for loc_line in values_tamc_fac[2:]:
        values = loc_line.strip().split()
        if not values:  # Skip empty lines
            continue
        tech, *years_data = values
        data_dict_3[tech] = dict(zip(header, map(float, years_data)))

    # Update the tech_dict with the parsed data
    for tech, values in data_dict_3.items():
        if tech in tech_dict:
            tech_dict[tech]['TotalAnnualMaxCapacity'] = values

    ###########################################################################
    # D) grab the TotalTechnologyActivityLowerLimity    
    start_taall_fac = False
    values_taall_fac = []
    
    # Iterate over the lines
    for idx, line in enumerate(line_list):
        # If we reach the start point, set the start flag to True
        
        if "param" in line:
            # print(line)
            pass
        
        if "param TotalTechnologyAnnualActivityLowerLimit" in line:
            start_taall_fac = True
            start_index = idx
            continue
        # If we reach the end point, break the loop
        if line.strip() == ";" and start_taall_fac:
            end_index = idx
            break
        # If the start flag is set, add the line to the values
        if start_taall_fac:
            values_taall_fac.append(line.strip())

    # print('review this 4')
    # sys.exit()

    technology_list_with_lower_limit = []
    technology_list_with_update = []

    # Once you have the start and end indices, you can remove those lines from line_list
    line_list_raw4 = deepcopy(line_list)
    if start_index is not None and end_index is not None:
        del line_list[start_index:end_index+1]  # +1 because Python slicing is exclusive of the end index

    header = values_taall_fac[1].strip().split()  # Extract the years
    data_dict_4 = {}
    for loc_line in values_taall_fac[2:]:
        values = loc_line.strip().split()
        if not values:  # Skip empty lines
            continue
        tech, *years_data = values
        data_dict_4[tech] = dict(zip(header, map(float, years_data)))

    # Update the tech_dict with the parsed data
    for tech, values in data_dict_4.items():
        if tech in tech_dict:
            tech_dict[tech]['TotalTechnologyAnnualActivityLowerLimit'] = values
            if values is not None:  # Only proceed if values is not None
                technology_list_with_lower_limit.append(tech)

    print('review this 4')
    print('-------------------------------------------------------- \n')
    # sys.exit()

    # At this stage the data is gathered. Next, we need to calculate the difference
    # between the maximum production and the lower production to avoid inconsistencies
    time_vector = [y for y in range(2018, 2070+1)]
    time_vector_str = [str(y) for y in time_vector]
    
    # Define an updated dictionary;
    tech_dict_updated = deepcopy(tech_dict)
    
    for tech in technology_list_with_lower_limit:
        this_af_list = [tech_dict[tech]['AvailabilityFactor'][y] for y in time_vector_str]
        this_cf_list = tech_dict[tech]['CapacityFactor']
        this_maxcap_list = [tech_dict[tech]['TotalAnnualMaxCapacity'][y] for y in time_vector_str]
        
        this_lowerlimit_list = [tech_dict[tech]['TotalTechnologyAnnualActivityLowerLimit'][y] for y in time_vector_str]
        
        # Assuming the lists this_af_list, this_cf_list, and this_maxcap_list are of the same length
        this_maxprod_list = [af * cf * cap * 31.536 for af, cf, cap in zip(this_af_list, this_cf_list, this_maxcap_list)]

        # Assuming the lists this_maxcap_list and this_lowerlimit_list are of the same length
        difference_list = [maxprod - lowerlimit for maxprod, lowerlimit in zip(this_maxprod_list, this_lowerlimit_list)]

        if any(x < 0 for x in difference_list):
            print(f"Warning 1: Negative value detected in difference_list for tech {tech}!")
            further_print_debugging = False
            if further_print_debugging:
                print(this_af_list)
                print(this_cf_list)
                print(this_maxcap_list)
                print(this_maxprod_list)
                print(this_lowerlimit_list)
                print(difference_list)

            # Update this_maxprod_list to make sure the difference is not negative
            this_maxprod_list_new = [max(prod, lower) for prod, lower in zip(this_maxprod_list, this_lowerlimit_list)]

            # Recalculate this_maxcap_list_new based on the new this_maxprod_list
            this_maxcap_list_new = [(1.001) * prod / (af * cf * 31.536) if af * cf != 0 else 0 for prod, af, cf in zip(this_maxprod_list_new, this_af_list, this_cf_list)]
            this_maxcap_list_new_orig = this_maxcap_list_new.copy()

            # Check for decreasing values in this_maxcap_list_new
            warning_printed = False  # Initialize flag
            for i in range(1, len(this_maxcap_list_new)):
                if this_maxcap_list_new[i] < this_maxcap_list_new[i-1]:
                    if not warning_printed:  # Only print the warning if it hasn't been printed yet
                        print(f"Warning 2: Found decreasing values in this_maxcap_list_new for tech {tech}")
                        technology_list_with_update.append(tech)
                        warning_printed = True  # Set flag to True so warning is not printed again
                        
                        # print('quick check')
                        # sys.exit()
                    
                    # Update the list so it doesn't have decreasing values
                    this_maxcap_list_new[i] = this_maxcap_list_new[i-1]
            print('\n')

            tech_dict_updated[tech]['TotalAnnualMaxCapacity'] = deepcopy(this_maxcap_list_new)

        # print('Calculating maxprod - mincap for ', tech)
        # sys.exit()

    # We need to update the line of TotalAnnualMaxCapacity for the updates:
    # Iterate over the lines
    line_list_change = deepcopy(line_list_orig)
    start_tamc_fac = False

    if running_for_last_time is False:
        for idx, line in enumerate(line_list_orig):
            # If we reach the start point, set the start flag to True

            if "param" in line:
                print(line)
                # pass

            if "param TotalAnnualMaxCapacity" in line:
                start_tamc_fac = True
                start_index_update = idx
                continue

            if start_tamc_fac:
                for tech_n in technology_list_with_update:
                    if tech_n in line:
                        # Extract the values from tech_dict_updated into a list
                        new_values_list = tech_dict_updated[tech_n]['TotalAnnualMaxCapacity']
    
                        # Convert the list elements to strings and then join them with spaces
                        new_values_str = ' '.join(map(str, new_values_list))
    
                        # Create the new updated string
                        updated_string = f"{tech_n} {new_values_str} \n"
    
                        line_list_change[idx] = deepcopy(updated_string)

                        #print('check what happens here 1')
                        # sys.exit()

            # If we reach the end point, break the loop
            if line.strip() == ";" and start_tamc_fac:
                end_index_update = idx
                break

    else:
        with open(txt_file_temp, "w") as temp_file:
            for idx, line in enumerate(line_list_orig):
                # If we reach the start point, set the start flag to True

                print_normal = True

                line_freeze = deepcopy(line)

                if "param" in line:
                    print(line)
                    # pass

                if "param TotalAnnualMaxCapacity" in line:
                    start_tamc_fac = True
                    start_index_update = idx

                if start_tamc_fac:
                    for tech_n in technology_list_with_update:
                        if tech_n in line:
                            # Extract the values from tech_dict_updated into a list
                            new_values_list = tech_dict_updated[tech_n]['TotalAnnualMaxCapacity']
        
                            # Convert the list elements to strings and then join them with spaces
                            new_values_str = ' '.join(map(str, new_values_list))
        
                            # Create the new updated string
                            updated_string = f"{tech_n} {new_values_str} \n"
        
                            line_list_change[idx] = deepcopy(updated_string)

                            temp_file.write(line_list_change[idx])
                            print_normal =  False
        
                            #print('check what happens here 2')
                            # sys.exit()

                # If we reach the end point, break the loop
                if line.strip() == ";" and start_tamc_fac:
                    start_tamc_fac = False
                    end_index_update = idx

                if print_normal:
                    temp_file.write(line_freeze)

        # Delete the original file
        os.remove(txt_file)

        # Rename the temporary file to have the name of the original file
        os.rename(txt_file_temp, txt_file)

    print('End for file ', all_txt_in_folder[0])
    dict_store_lines['Original'].update({all_txt_in_folder[0]:deepcopy(line_list_orig)})
    dict_store_lines['Updated'].update({all_txt_in_folder[0]:deepcopy(line_list_change)})
    # sys.exit()


# Now we need to store and re-print
print_store_pickle = True
# print_store_pickle = False
if print_store_pickle:
    # Open a file for writing
    with open('dict_store_lines.pkl', 'wb') as file:
        pickle.dump(dict_store_lines, file)


end_1 = time.time()   
time_elapsed_1 = -start1 + end_1

print('For all effects this has finished in ', time_elapsed_1/60)    
sys.exit()




