# -*- coding: utf-8 -*-
# ===============================================================================

import pytools4dart as ptd
from pytools4dart.simulationXSD import simulation

#simu = simulation("test2plotsSimu_defautOptProps")
simu = simulation("test2plotsSimu")

sp_band_list = [[0.7, 0.02],
                [0.8, 0.02],
                [1.0, 0.02]]

simu.add_sp_bands(sp_band_list)

simu.check_module_dependencies()

simu.writeToXMLFromObj(modified_simu_name = "testWriteModifSimu")

simu.runners.full()

# ## CORRECTING DEPENDENCIES ISSUES:
# plots_list = simu.plots_obj.Plots.Plot
# for plot in plots_list:
#     if plot.PlotVegetationProperties.VegetationOpticalPropertyLink == "Toto_Phase_Function":
#         plot.PlotVegetationProperties.VegetationOpticalPropertyLink = "Turbid_Leaf_Deciduous_Phase_Function"
#
# simu.maket_obj.Maket.Soil.OpticalPropertyLink.ident = "Lamb_ro=1"
# #######################
#
# simu.check_module_dependencies()
#
# simu.writeToXMLFromObj()
#
#

print("stop")