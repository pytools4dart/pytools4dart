from pytools4dart.simulation import simulation

#simu = simulation("test_newSimuWithPlotsTxt")

simu = simulation("test2plotsSimu")

src_file_path = "plots.txt" #in this file 2 species are requested
simu.add.add_plotstxtfile_reference(src_file_path=src_file_path)

simu.core.update()

simu.write("test2plotsSimu_PlusPlotsTxt", overwrite=True)

simu2 = simulation("test2plotsSimu_PlusPlotsTxt")

simu2.run.full()


