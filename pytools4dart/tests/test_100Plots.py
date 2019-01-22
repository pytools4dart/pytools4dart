# -*- coding: utf-8 -*-
# ===============================================================================
# PROGRAMMERS:
#
# Florian de Boissieu <florian.deboissieu@irstea.fr>
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

import timeit
import pytools4dart as ptd

# Build list of plots
plots = ptd.plots.createDartFile()
Plot = ptd.plots.create_Plot()
plots.Plots.Plot=[]

tic=timeit.default_timer()
for i in range(100):
    plots.Plots.add_Plot(Plot.copy())
toc=timeit.default_timer()
print('elapsed time 1 = {}'.format(toc - tic))

# Build simulation
simu = ptd.simulation()
simu.name = 'test_100plots'
simu.core.xsdobjs['plots']=plots
simu.core.update_simu() # updates simu.scene and simu.acquisition
simu.add.optical_property('Vegetation')
simu.scene.update_xsdobjs()
simu.write(overwrite=True)
try:
    simu.run.full()
except(Exception):
    print(Exception.message)
