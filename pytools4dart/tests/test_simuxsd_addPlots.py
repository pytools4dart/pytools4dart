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

simu.check_sp_bands() # --> warnings and correction of coeff_diff

simu.add_sp_bands_uf(sp_band_list) #phase and coeff_diff

#simu.check_sp_bands() #no warning

#simu.extract_plots_full_table() # included in check_properties_index_through_tables

#simu.check_properties_indexes_through_tables()


check = simu.check_module_dependencies()  #includes check_sp_bands and check_properties_indexes_through_tables


simu.writeToXMLFromObj(modified_simu_name = "test2plotsSimu_Plus3bands")

simu2 = simulation("test2plotsSimu_Plus3bands")

#simu2.runners.full() #---> OK


add_plot_ok = simu2.add_plot(plot_type="ground", plot_form="polygon", plot_opt_prop_name=None, plot_therm_prop_name=None,grd_opt_prop_type="lambertian",grd_opt_prop_name="lambertianprop1",grd_therm_prop_name="thermprop1",createProps=True)

simu2.check_module_dependencies()

simu2.writeToXMLFromObj(modified_simu_name= "test2plotsSimu_Plus3bands_Plus1plot")

simu3 = simulation("test2plotsSimu_Plus3bands_Plus1plot")

simu3.runners.full()

print("stop")