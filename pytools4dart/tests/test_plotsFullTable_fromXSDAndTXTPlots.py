from pytools4dart.simulation import simulation

#simu = simulation("test_newSimuWithPlotsTxt")

simu = simulation("test2plotsSimu")

simu.add.opt_property(opt_prop_type="vegetation",opt_prop_name="veg1")
src_file_path = "plots.txt" #in this file 2 species are requested
simu.add.plotstxtfile_reference(src_file_path=src_file_path)

simu.core.update()

simu.write("test2plotsSimu_PlusPlotsTxt", overwrite=True)

simu2 = simulation("test2plotsSimu_PlusPlotsTxt")

simu2.run.full()


