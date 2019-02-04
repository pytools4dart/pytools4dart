# -*- coding: utf-8 -*-
# ===============================================================================
# PROGRAMMERS:
#
# Florian de Boissieu <fdeboiss@gmail.com>
# https://gitlab.irstea.fr/florian.deboissieu/pytools4dart
#
# This file is part of the pytools4dart package.
#
# pytools4dart is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
#
#
# ===============================================================================
"""
Test the time to add 100 plots
"""
# TODO: update code
import timeit
import pytools4dart as ptd
import numpy as np


# Build list of plots
plots = ptd.plots.createDartFile()
Plot = ptd.plots.create_Plot()
plots.Plots.Plot=[]

tic=timeit.default_timer()
for i in range(100):
    plots.Plots.add_Plot(Plot.copy())
toc=timeit.default_timer()
print('elapsed time 1 = {}'.format(toc - tic))

## Modification of Plots coordinates
X, Y = np.meshgrid(range(10), range(10))
I = [0, 1, 1, 0]
J = [0, 0, 1, 1]
for iplot, (x, y) in enumerate(zip(X.ravel(), Y.ravel())):
    for ipoint, (ix, iy) in enumerate(zip(I, J)):
        plots.Plots.Plot[iplot].Polygon2D.Point2D[ipoint].x = x + ix
        plots.Plots.Plot[iplot].Polygon2D.Point2D[ipoint].y = y + iy

# Build simulation
simu = ptd.simulation()
simu.name = 'test_100plots'
simu.core.plots = plots
simu.core.plots = plots

# simu.core.update_simu() # updates simu.scene and simu.sensor
simu.add.optical_property('Vegetation')
simu.write(overwrite=True)
try:
    simu.run.full()
except(Exception):
    print(Exception.message)
