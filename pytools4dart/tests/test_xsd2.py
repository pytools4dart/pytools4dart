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
plots = ptd.plots.createDartFile()
# load phase from simulation
phase = ptd.phase.parse(os.path.join(ptd.settings.get_simu_input_path('use_case_3'),
                                     'phase.xml'))
Plot = ptd.plots.create_Plot()
Plot.Polygon2D.Point2D[1].x=20
Plot.copy()
# update_node(plots, troot)
# toc=timeit.default_timer()
print(etree.tostring(phase.to_etree(), pretty_print=True))
# creation of 2 plots
plots.Plots.add_Plot(ptd.plots.create_Plot())
plots.Plots.add_Plot(ptd.plots.create_Plot())
plots.Plots.Plot[0].form = 1
print(etree.tostring(plots.to_etree(), pretty_print=True))

# WARNING: all is done by reference
# Following example will add two plots completly connected
# that is to say modifying one will modify the other one
plots.Plots.Plot = []
Plot = ptd.plots.create_Plot()
plots.Plots.add_Plot(Plot)
plots.Plots.add_Plot(Plot)
plots.Plots.add_Plot(Plot.copy())
plots.Plots.Plot[1].form = 1
toc=timeit.default_timer()
print(toc - tic)
print(etree.tostring(plots.to_etree(), pretty_print=True))

Plot = ptd.plots.create_Plot()
plots.Plots.Plot=[]
tic=timeit.default_timer()
for i in range(100):
    plots.Plots.add_Plot(Plot.copy())
toc=timeit.default_timer()
print(toc - tic)

## modification des coordonnées d'un Plots
import numpy as np
X, Y = np.meshgrid(range(10), range(10))
I = [0, 1, 1, 0]
J = [0, 0, 1, 1]
for iplot, (x, y) in enumerate(zip(X.ravel(), Y.ravel())):
    for ipoint, (ix, iy) in enumerate(zip(I, J)):
        plots.Plots.Plot[iplot].Polygon2D.Point2D[ipoint].x = x + ix
        plots.Plots.Plot[iplot].Polygon2D.Point2D[ipoint].y = y + iy



ptd.xsdschema.utils.export_xsd_to_tree(plots).write(os.path.expanduser('~/plots1.xml'),
                                pretty_print=True,
                                encoding="UTF-8",
                                xml_declaration=True)
