# -*- coding: utf-8 -*-
# ===============================================================================

import pytools4dart as ptd
from pytools4dart.add import Polygone_plot_vol_info, Poly_corners
from pytools4dart.simulation import simulation

#simu = simulation("test2plotsSimu_defautOptProps")
#simu = simulation("test2plotsSimu")
simu = simulation()
#simu = simulation("use_case_0") # run ok

sp_band_list = [[0.7, 0.02],
                [0.8, 0.02],
                [1.0, 0.02]]

simu.add.sp_bands_uf(sp_band_list) #phase and coeff_diff

corners = Poly_corners(x1 = 3.0, y1= 3.0, x2=10.0, y2=3.0, x3=10.0, y3=10.0, x4=3.0, y4=10.0)
poly_vol_info = Polygone_plot_vol_info(poly_corners = corners)

add_plot_ok = simu.add.plot(plot_type="vegetation", plot_form="polygon", volume_info = poly_vol_info, plot_opt_prop_name="veg_opt_prop_1", plot_therm_prop_name="therm_prop_1", grd_opt_prop_type=None, grd_opt_prop_name=None, grd_therm_prop_name=None, createProps=True)

add_plot_ok = simu.add.plot(plot_type="ground", plot_form="polygon", plot_opt_prop_name=None, plot_therm_prop_name=None, grd_opt_prop_type="lambertian", grd_opt_prop_name="lambertianprop1", grd_therm_prop_name="thermprop1", createProps=True)


simu.checker.module_dependencies()

simu.write(modified_simu_name="test_newSimu_Plus1PlotWithVol", overwrite=True)

simu2 = simulation("test_newSimu_Plus1PlotWithVol")

try:
    simu2.run.full()
except(Exception):
    print(Exception.message)

print("stop")