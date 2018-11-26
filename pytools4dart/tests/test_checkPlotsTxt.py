# -*- coding: utf-8 -*-
# ===============================================================================

import pytools4dart as ptd
from pytools4dart.simulationXSD import simulation

#simu = simulation("test2plotsSimu_defautOptProps")
simu = simulation("test_simuWithPlotsFile")
simu.check_module_dependencies()  #includes check_and_correct_sp_bands and check_properties_indexes

simu.write(modified_simu_name ="test2plotsSimu_readAndWrite")

simu2 = simulation("test2plotsSimu_readAndWrite")
simu2.run.full()

print("stop")