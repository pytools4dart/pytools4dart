# -*- coding: utf-8 -*-
# ===============================================================================


import timeit
import pytools4dart as ptd
from pytools4dart.simulationXSD import simulation

plots = ptd.plots.createDartFile()
Plot = ptd.plots.create_Plot()
plots.Plots.Plot=[]
tic=timeit.default_timer()
for i in range(100):
    plots.Plots.add_Plot(Plot.copy())
toc=timeit.default_timer()
print('elapsed time 1 = {}'.format(toc - tic))

simu = simulation()
tic=timeit.default_timer()
for i in range(100):
    simu.add_plot(createProps = True)
toc = timeit.default_timer()
print('elapsed time2 = {}'.format(toc - tic))


simu.write(modified_simu_name="test_newSimu_Plus100Plots")

tic=timeit.default_timer()
simu2 = simulation("test_newSimu_Plus100Plots")
toc=timeit.default_timer()
print('elapsed time3 = {}'.format(toc - tic))

try:
    simu2.run.full()
except(Exception):
    print(Exception.message)

print("stop")