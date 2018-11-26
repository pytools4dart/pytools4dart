# -*- coding: utf-8 -*-
# ===============================================================================

import pytools4dart as ptd
from pytools4dart.simulationXSD import simulation

#simu = simulation("test2plotsSimu_defautOptProps")
#simu = simulation("test2plotsSimu")
simu = simulation()
#simu = simulation("use_case_0") # run ok

sp_band_list = [[0.7, 0.02],
                [0.8, 0.02],
                [1.0, 0.02]]

simu.add_sp_bands(sp_band_list) #phase

#check =
simu.check_and_correct_sp_bands() # --> warnings and correction of coeff_diff

simu.write(modified_simu_name ="test_newSimu_Plus3bands")

simu2 = simulation("test_newSimu_Plus3bands")

simu2.run.full()

simu.add_sp_bands_uf(sp_band_list) #phase and coeff_diff

check = simu.check_module_dependencies()  #includes check_and_correct_sp_bands and check_properties_indexes

if check:
    simu.write(modified_simu_name ="test_newSimu_Plus3bands") # this includes check_module_dependencies, leave or let the user to check this before writting as shown in this exemple?

    simu2 = simulation("test_newSimu_Plus3bands")
    simu2.run.full()

print("stop")