# -*- coding: utf-8 -*-
# ===============================================================================

import pytools4dart as ptd
from pytools4dart.simulation import simulation

#simu = simulation("test2plotsSimu_defautOptProps")
#simu = simulation("test2plotsSimu")
simu = simulation()

simu.add_opt_property("lambertian","newlambprop")
simu.add_opt_property("vegetation","newprop")
simu.add_opt_property("lambertian","newprop")
#simu.add_opt_property("vegetation","newprop")

simu.add_th_property("newthprop")
#simu.add_th_property("newthprop")


simu.check_module_dependencies()  #includes check_and_correct_sp_bands and check_properties_indexes

simu.write(modified_simu_name ="test_newSimu_addProp", overwrite=True)

simu2 = simulation("test_newSimu_addProp")


simu2.run.full()

print("stop")