# -*- coding: utf-8 -*-
# ===============================================================================


import timeit
import pytools4dart as ptd
from pytools4dart.simulationXSD import simulation

# plots = ptd.plots.createDartFile()
# Plot = ptd.plots.create_Plot()
# plots.Plots.Plot=[]
# tic=timeit.default_timer()
# for i in range(100):
#     plots.Plots.add_Plot(Plot.copy())
# toc=timeit.default_timer()
# print('elapsed time 1 = {}'.format(toc - tic))

simu = simulation()
#
# sp_bands_list = []
lam0 = 0.7
#
# tic=timeit.default_timer()
#
# for i in range(100):
#     sp_bands_list.append( [lam0 + i*0.1 , 0.02] )
#
# simu.add_sp_bands(sp_bands_list)
#
# toc=timeit.default_timer()
#
# print('elapsed time1 = {} s'.format(toc - tic))


sp_bands_list = []
tic=timeit.default_timer()
for i in range(100):
    sp_bands_list.append([lam0 + i*0.1 , 0.02] )

simu.add_sp_bands_uf(sp_bands_list)

toc=timeit.default_timer()

print('elapsed time2 = {} s'.format(toc - tic))

simu.writeToXMLFromObj(modified_simu_name= "test_newSimu_Plus100SpBands")

tic=timeit.default_timer()
simu2 = simulation("test_newSimu_Plus100SpBands")
toc=timeit.default_timer()
print('reading time = {} s'.format(toc - tic))

try:
    simu2.runners.full()
except(Exception):
    print(Exception.message)

print("stop")