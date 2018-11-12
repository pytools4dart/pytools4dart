# -*- coding: utf-8 -*-
# ===============================================================================

import pytools4dart as ptd
from pytools4dart.simulationXSD import simulation

#simu = simulation("test2plotsSimu_defautOptProps")
simu = simulation("test2plotsSimu")

simu.check_module_dependencies()  #includes check_sp_bands and check_properties_indexes_through_tables

simu.writeToXMLFromObj(modified_simu_name = "test2plotsSimu_readAndWrite")

simu2 = simulation("test2plotsSimu_readAndWrite")
simu2.runners.full()

print("stop")