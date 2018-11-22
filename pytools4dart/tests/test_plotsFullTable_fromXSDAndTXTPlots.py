from pytools4dart.simulationXSD import simulation

#simu = simulation("test_newSimuWithPlotsTxt")

simu = simulation("test2plotsSimu")

src_file_path = "plots.txt" #in this file 2 species are requested
simu.add_plotstxtfile_reference(src_file_path=src_file_path)

simu.update_tables_from_objs()

simu.writeToXMLFromObj("test2plotsSimu_PlusPlotsTxt")

simu2 = simulation("test2plotsSimu_PlusPlotsTxt")

simu2.runners.full()


