# -*- coding: utf-8 -*-

import lxml.etree as etree
import cProfile
import pytools4dart as ptd
from pytools4dart.xsdschema.utils import get_gs_troot, update_node
import timeit
import os
# troot = get_gs_troot('plots', 'DartFile')
# creation d'un plots.xml par defaut
tic=timeit.default_timer()
plots = ptd.plots_gds.createDartFile()
# update_node(plots, troot)
# toc=timeit.default_timer()

# creation of 2 plots
plots.Plots.add_Plot(ptd.plots_gds.create_Plot())
plots.Plots.add_Plot(ptd.plots_gds.create_Plot())
plots.Plots.Plot[0].form = 1
print(etree.tostring(plots.to_etree(), pretty_print=True))

# WARNING: all is done by reference
# Following example will add two plots completly connected
# that is to say modifying one will modify the other one
Plot = ptd.plots_gds.create_Plot()
plots.Plots.add_Plot(Plot)
plots.Plots.add_Plot(Plot)
plots.Plots.Plot[2].form = 1

print(etree.tostring(plots.to_etree(), pretty_print=True))
toc=timeit.default_timer()
print(toc - tic)
tic=timeit.default_timer()
for i in range(100):
    plots.Plots.add_Plot(ptd.plots_gds.create_Plot())
toc=timeit.default_timer()
print(toc - tic)

ptd.xsdschema.utils.export_xsd_to_tree(plots).write(os.path.expanduser('~/plots1.xml'),
                                pretty_print=True,
                                encoding="UTF-8",
                                xml_declaration=True)
