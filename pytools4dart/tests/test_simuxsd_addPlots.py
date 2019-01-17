# -*- coding: utf-8 -*-
# ===============================================================================

import pytools4dart as ptd
from pytools4dart.simulation import simulation

#simu = simulation("test2plotsSimu_defautOptProps")
#simu = simulation("test2plotsSimu")
simu = simulation()
#simu = simulation("use_case_0") # run ok

sp_band_list = [[0.7, 0.02],
                [0.8, 0.02],
                [1.0, 0.02]]

simu.add_sp_bands(sp_band_list) #phase

simu.add.check_and_correct_sp_bands() # --> warnings and correction of coeff_diff

simu.add.sp_bands_uf(sp_band_list) #phase and coeff_diff

#simu.check_and_correct_sp_bands() #no warning

check = simu.checker.module_dependencies()  #includes check_and_correct_sp_bands and properties_indexes

simu.write(modified_simu_name ="test_newSimu_Plus3bands", overwrite=True)

simu2 = simulation("test_newSimu_Plus3bands")

#simu2.runners.full() #---> OK


add_plot_ok = simu2.add.plot(plot_type="ground", plot_form="polygon", plot_opt_prop_name=None, plot_therm_prop_name=None, grd_opt_prop_type="lambertian", grd_opt_prop_name="lambertianprop1", grd_therm_prop_name="thermprop1", createProps=True)

simu2.checker.module_dependencies()

simu2.write(modified_simu_name="test_newSimu_Plus3bands_Plus1Plot", overwrite=True)

simu3 = simulation("test_newSimu_Plus3bands_Plus1Plot")

try:
    simu3.run.full()
except(Exception):
    print(Exception.message)

print("stop")