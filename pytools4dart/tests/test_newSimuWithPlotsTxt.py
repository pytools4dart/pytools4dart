# -*- coding: utf-8 -*-
# ===============================================================================

import pytools4dart as ptd
from pytools4dart.simulation import simulation
import pandas as pd

simu = simulation()

src_file_path = "plots.txt" #in this file 2 species are requested

simu.add.opt_property(opt_prop_type="vegetation", opt_prop_name="veg1") #otherwise the add_plotstxtfile fails
simu.add.plotstxtfile_reference(src_file_path=src_file_path)

simu.write("test_newSimuWithPlotsTxt", overwrite = True)

simu2 = simulation("test_newSimuWithPlotsTxt")
simu2.run.full()

print("stop")