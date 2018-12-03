# -*- coding: utf-8 -*-
# ===============================================================================

import pytools4dart as ptd
from pytools4dart.simulation import simulation

#simu = simulation("test2plotsSimu_defautOptProps")
simu = simulation("test2plotsSimu")
import lxml.etree as etree
print(etree.tostring(ptd.plots.create_Plot().to_etree(), pretty_print=True))
simu.checker.module_dependencies()  #includes check_and_correct_sp_bands and properties_indexes

simu.write(modified_simu_name ="test2plotsSimu_readAndWrite", overwrite=True)

simu2 = simulation("test2plotsSimu_readAndWrite")
simu2.run.full()

print("stop")