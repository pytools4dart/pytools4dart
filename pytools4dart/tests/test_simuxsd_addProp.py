# -*- coding: utf-8 -*-
# ===============================================================================

import pytools4dart as ptd
from pytools4dart.simulation import simulation

#simu = simulation("test2plotsSimu_defautOptProps")
#simu = simulation("test2plotsSimu")
simu = simulation()

simu.add.opt_property("lambertian", "newlambprop")
simu.add.opt_property("vegetation", "newprop")
simu.add.opt_property("lambertian", "newprop")
#simu.opt_property("vegetation","newprop")

simu.add.th_property("newthprop")
#simu.th_property("newthprop")


simu.checker.module_dependencies()  #includes check_and_correct_sp_bands and properties_indexes

simu.write(modified_simu_name ="test_newSimu_addProp", overwrite=True)

simu2 = simulation("test_newSimu_addProp")


simu2.run.full()

print("stop")