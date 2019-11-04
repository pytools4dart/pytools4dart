from pytools4dart.simulation import simulation

#simu = simulation("test_newSimuWithPlotsTxt")

simu = simulation("test2plotsSimu")

simu.add.optical_property(type="vegetation",ident="veg1")
simu.add.plots('plots.txt')

simu.core.update()

simu.write("test2plotsSimu_PlusPlotsTxt", overwrite=True)

simu2 = simulation("test2plotsSimu_PlusPlotsTxt")

simu2.run.full()


