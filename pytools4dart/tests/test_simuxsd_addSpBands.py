# -*- coding: utf-8 -*-
# ===============================================================================

import pytools4dart as ptd
from pytools4dart.simulationXSD import simulation

#simu = simulation("test2plotsSimu_defautOptProps")
simu = simulation("test2plotsSimu")
#simu = simulation("use_case_0") # run ok

sp_band_list = [[0.7, 0.02],
                [0.8, 0.02],
                [1.0, 0.02]]

simu.add_sp_bands(sp_band_list) #phase

#check = simu.check_sp_bands() # --> warnings and correction of coeff_diff

simu.add_sp_bands_uf(sp_band_list) #phase and coeff_diff

check = simu.check_module_dependencies()  #includes check_sp_bands and check_properties_indexes_through_tables

if check:
    simu.writeToXMLFromObj(modified_simu_name = "test2plotsSimu_Plus3bands") # this includes check_module_dependencies, leave or let the user to check this before writting as shown in this exemple?

    simu2 = simulation("test2plotsSimu_Plus3bands")
    simu2.runners.full()

print("stop")