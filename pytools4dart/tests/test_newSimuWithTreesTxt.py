# -*- coding: utf-8 -*-
# ===============================================================================

import pytools4dart as ptd
from pytools4dart.simulation import simulation
import pandas as pd

#simu = simulation("test_simuWithTreesFile_IHM")
#simu.module_dependencies()  #includes check_and_correct_sp_bands and properties_indexes



simu = simulation()

src_file_path = "trees.txt" #in this file 2 species are requested
species_list =[]
crown_props = []
crown_dfs_columns = ['crown_opt_prop_type', 'crown_opt_prop_name', 'crown_th_prop_name', 'crown_veg_opt_prop_name', 'crown_veg_th_prop_name']
#crown 1
crown_props.append(["lambertian","lamb1","th1","turbid_1","th1"])
#crown 2
crown_props.append(["hapke","hapke1","th1","turbid_2","th1"])
species_crowns_df = pd.DataFrame(crown_props, columns = crown_dfs_columns)
species_crowns_df2 = species_crowns_df.copy()

specie1_dict = {
    "opt_prop_type": "lambertian",
    "opt_prop_name": "lamb_uno",
    "th_prop_name": "th_uno",
    "crown_props": species_crowns_df
}
specie2_dict = {
"opt_prop_type": "lambertian",
    "opt_prop_name": "lamb_dos",
    "th_prop_name": "th_dos",
    "crown_props": species_crowns_df2
}
species_list.append(specie1_dict)
species_list.append(specie2_dict)

simu.add.treestxtfile_reference(src_file_path=src_file_path, species_list=species_list, createProps= True)

simu.write(modified_simu_name ="test_newSimuWithTrees", overwrite=True)

simu2 = simulation("test_newSimuWithTrees")
simu2.run.full()

print("stop")